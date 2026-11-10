#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.13"
# dependencies = [
#   "typer>=0.12",
#   "servicex",
#   "func_adl_servicex_xaodr25",
#   "jinja2",
#   "awkward>=2",
#   "vector",
#   "numpy",
#   "uproot",
#   "hist",
#   "matplotlib",
#   "mplhep",
# ]
# ///
"""Plot every unique same-charge muon pair in one Open Data input file.

Run with: uv run --script script.py
ServiceX uses the servicex.yaml configuration in the current directory.
No object cuts or event weights are applied. The event denominator includes
every event with at least two muons, even when it has no same-charge pair.
"""

from pathlib import Path
from typing import Annotated

import awkward as ak
import hist
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mplhep as hep
import numpy as np
import typer
import uproot
import vector
from func_adl_servicex_xaodr25 import FuncADLQueryPHYSLITE
from servicex import Sample, ServiceXSpec, dataset, deliver

app = typer.Typer(add_completion=False)
DATASET = (
    "opendata:mc20_13TeV.700325.Sh_2211_Zmumu_maxHTpTV2_CVetoBVeto."
    "deriv.DAOD_PHYSLITE.e8351_s3681_r13167_p6026"
)


def muon_query():
    """Return GeV four-vector coordinates and charge for selected events."""
    return (
        FuncADLQueryPHYSLITE()
        .Select(lambda event: {"muons": event.Muons()})
        .Where(lambda event: event.muons.Count() >= 2)
        .Select(
            lambda event: {
                "mu_pt": event.muons.Select(lambda mu: mu.pt() / 1000.0),
                "mu_eta": event.muons.Select(lambda mu: mu.eta()),
                "mu_phi": event.muons.Select(lambda mu: mu.phi()),
                "mu_mass": event.muons.Select(lambda mu: mu.m() / 1000.0),
                "mu_charge": event.muons.Select(lambda mu: mu.charge()),
            }
        )
    )


@app.command()
def main(
    output_dir: Annotated[Path, typer.Option(help="Directory for plot_1.png.")] = Path("."),
) -> None:
    """Fetch one dataset file and plot unweighted same-charge dimuon masses."""
    delivered = deliver(
        ServiceXSpec(
            Sample=[
                Sample(
                    Name="same_charge_muons",
                    Dataset=dataset.Rucio(DATASET),
                    NFiles=1,
                    Query=muon_query(),
                )
            ]
        )
    )
    paths = list(delivered["same_charge_muons"])
    if len(paths) != 1:
        raise RuntimeError(f"Expected one transformed input file, received {len(paths)}")
    with uproot.open(str(paths[0])) as root_file:
        events = root_file["atlas_xaod_tree"].arrays(library="ak")

    vector.register_awkward()
    muons = ak.zip(
        {
            "pt": events.mu_pt,
            "eta": events.mu_eta,
            "phi": events.mu_phi,
            "mass": events.mu_mass,
            "charge": events.mu_charge,
        },
        with_name="Momentum4D",
    )
    # Count BEFORE selecting pairs: opposite-charge-only events remain here.
    n_events = len(muons)
    if n_events == 0:
        raise RuntimeError("The input file contains no events with at least two muons")
    # combinations produces i < j: neither self-pairs nor reversed duplicates.
    pairs = ak.combinations(muons, 2, fields=["first", "second"])
    same_charge = pairs[pairs.first.charge == pairs.second.charge]
    masses = ak.to_numpy(ak.flatten((same_charge.first + same_charge.second).mass, axis=1))
    if not np.all(np.isfinite(masses)):
        raise RuntimeError("Non-finite invariant masses found in the selected pairs")

    # Metrics use only raw, unweighted fill values and the selected event count.
    average_entries = len(masses) / n_events
    mean_mass = float(np.mean(masses)) if len(masses) else float("nan")
    # Include every mass in the visible range, including the maximum value.
    upper_edge = max(10.0, float(np.max(masses)) * 1.05) if len(masses) else 200.0
    mass_hist = hist.Hist.new.Reg(
        100, 0.0, upper_edge, name="mass", label=r"$m_{\mu\mu}$ [GeV]"
    ).Int64()
    mass_hist.fill(mass=masses)
    print(f"METRIC: avg_entries_per_event={average_entries:.12g} mean={mean_mass:.12g}", flush=True)

    plt.style.use(hep.style.ATLAS)
    fig, ax = plt.subplots()
    mass_hist.plot(ax=ax, histtype="step", color="navy", label="Same-charge pairs")
    ax.set_ylabel("Muon pairs / bin")
    ax.set_title("Same-charge dimuon invariant mass")
    ax.legend()
    ax.text(0.97, 0.79, "ATLAS Open Data simulation\n1 input file; unweighted", transform=ax.transAxes,
            ha="right", va="top", fontsize=12)
    output_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_dir / "plot_1.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    app()
