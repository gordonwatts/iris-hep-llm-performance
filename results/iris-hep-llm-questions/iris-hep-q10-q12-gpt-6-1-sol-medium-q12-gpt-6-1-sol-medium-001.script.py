#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.13"
# dependencies = [
#   "typer>=0.12",
#   "servicex>=3,<4",
#   "func_adl_servicex_xaodr25",
#   "jinja2",
#   "awkward>=2,<3",
#   "uproot>=5,<6",
#   "vector>=1,<2",
#   "numpy",
#   "hist>=2,<3",
#   "matplotlib",
#   "mplhep",
# ]
# ///
"""Unweighted same-charge dimuon masses from one Open Data PHYSLITE file.

Run with: uv run --script script.py
ServiceX uses the credentials in the local servicex.yaml configuration.
"""

from pathlib import Path

import awkward as ak
from func_adl_servicex_xaodr25 import FuncADLQueryPHYSLITE
from hist import Hist
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mplhep as hep
import numpy as np
from servicex import Sample, ServiceXSpec, dataset, deliver
import typer
import uproot
import vector

app = typer.Typer(add_completion=False)

DATASET = (
    "opendata:mc20_13TeV.700325.Sh_2211_Zmumu_maxHTpTV2_CVetoBVeto."
    "deriv.DAOD_PHYSLITE.e8351_s3681_r13167_p6026"
)


def fetch_muons() -> ak.Array:
    """Retain every event with >=2 muons, irrespective of their charges."""
    query = (
        FuncADLQueryPHYSLITE()
        .Select(lambda event: {"muons": event.Muons()})
        .Where(lambda collections: collections.muons.Count() >= 2)
        .Select(lambda collections: {
            "mu_pt": collections.muons.Select(lambda mu: mu.pt() / 1000.0),
            "mu_eta": collections.muons.Select(lambda mu: mu.eta()),
            "mu_phi": collections.muons.Select(lambda mu: mu.phi()),
            "mu_mass": collections.muons.Select(lambda mu: mu.m() / 1000.0),
            "mu_charge": collections.muons.Select(lambda mu: mu.charge()),
        })
    )
    delivered = deliver(
        ServiceXSpec(Sample=[Sample(
            Name="same_charge_muons",
            Dataset=dataset.Rucio(DATASET),
            NFiles=1,
            Query=query,
        )])
    )
    arrays = []
    for path in delivered["same_charge_muons"]:
        with uproot.open(str(path)) as root_file:
            arrays.append(root_file["atlas_xaod_tree"].arrays(library="ak"))
    if not arrays:
        raise RuntimeError("ServiceX returned no files.")
    return ak.concatenate(arrays, axis=0)


@app.command()
def main(
    output_dir: Path = typer.Option(Path("."), help="Directory for plot_1.png."),
) -> None:
    """Plot all unique same-charge muon pairs from one dataset input file."""
    data = fetch_muons()
    # This denominator includes events that later yield an empty pair list.
    event_count = len(data)
    if event_count == 0:
        raise RuntimeError("No events with at least two muons were returned.")

    vector.register_awkward()
    muons = ak.zip({
        "pt": data.mu_pt,
        "eta": data.mu_eta,
        "phi": data.mu_phi,
        "mass": data.mu_mass,
        "charge": data.mu_charge,
    }, with_name="Momentum4D")
    # combinations without replacement gives each unordered pair exactly once.
    pairs = ak.combinations(muons, 2, axis=1, fields=["first", "second"])
    pairs = pairs[pairs.first.charge == pairs.second.charge]
    masses = ak.to_numpy(ak.flatten((pairs.first + pairs.second).mass, axis=1))
    if not np.all(np.isfinite(masses)):
        raise RuntimeError("Nonfinite invariant masses in the input.")

    # Compute both metrics from raw entries, without weights or histogram APIs.
    average_entries = len(masses) / event_count
    mean = float(np.mean(masses)) if len(masses) else float("nan")

    # Extend the axis to include every raw value, including the largest mass.
    upper_edge = max(200.0, float(np.max(masses)) * 1.05) if len(masses) else 200.0
    histogram = (
        Hist.new.Reg(100, 0.0, upper_edge, name="mass", label=r"$m_{\mu\mu}$ [GeV]")
        .Int64()
    )
    histogram.fill(mass=masses)
    plt.style.use(hep.style.ATLAS)
    fig, ax = plt.subplots()
    histogram.plot(ax=ax, histtype="step", color="navy")
    ax.set_ylabel("Muon pairs / bin")
    ax.set_title("Unique same-charge muon pairs", fontsize=16)
    ax.text(
        0.97, 0.95,
        f"Events with >=2 muons: {event_count:,}\nSame-charge pairs: {len(masses):,}",
        transform=ax.transAxes, ha="right", va="top", fontsize=12,
    )
    ax.set_ylim(bottom=0)
    output_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_dir / "plot_1.png", dpi=150, bbox_inches="tight")
    print(f"METRIC: avg_entries_per_event={average_entries:.12g} mean={mean:.12g}", flush=True)
    plt.close(fig)


if __name__ == "__main__":
    app()
