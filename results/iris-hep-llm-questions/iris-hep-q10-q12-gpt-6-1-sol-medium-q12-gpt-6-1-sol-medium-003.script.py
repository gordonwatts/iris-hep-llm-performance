#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.13"
# dependencies = [
#   "typer>=0.12",
#   "servicex",
#   "func_adl_servicex_xaodr25",
#   "jinja2",
#   "uproot>=5",
#   "awkward>=2",
#   "vector",
#   "numpy",
#   "hist",
#   "matplotlib",
#   "mplhep",
# ]
# ///
"""Unweighted same-charge dimuon masses from ATLAS Open Data PHYSLITE."""

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

DATASET = (
    "opendata:mc20_13TeV.700325.Sh_2211_Zmumu_maxHTpTV2_CVetoBVeto."
    "deriv.DAOD_PHYSLITE.e8351_s3681_r13167_p6026"
)
app = typer.Typer(add_completion=False)


def fetch_muons(n_files: int) -> ak.Array:
    """Keep every event with >=2 muons, regardless of its charge content."""
    query = (
        FuncADLQueryPHYSLITE()
        .Select(lambda event: {"muons": event.Muons()})
        .Where(lambda event: event.muons.Count() >= 2)
        .Select(lambda event: {
            "mu_pt": event.muons.Select(lambda mu: mu.pt() / 1000.0),
            "mu_eta": event.muons.Select(lambda mu: mu.eta()),
            "mu_phi": event.muons.Select(lambda mu: mu.phi()),
            "mu_mass": event.muons.Select(lambda mu: mu.m() / 1000.0),
            "mu_charge": event.muons.Select(lambda mu: mu.charge()),
        })
    )
    delivered = deliver(ServiceXSpec(Sample=[Sample(
        Name="same_charge_dimuons",
        Dataset=dataset.Rucio(DATASET),
        NFiles=n_files,
        Query=query,
    )]))
    arrays = []
    for path in delivered["same_charge_dimuons"]:
        with uproot.open(str(path)) as root_file:
            arrays.append(root_file["atlas_xaod_tree"].arrays(library="ak"))
    if not arrays:
        raise RuntimeError("ServiceX returned no input files.")
    return ak.concatenate(arrays, axis=0)


def pair_masses(events: ak.Array) -> tuple[np.ndarray, int]:
    """Return every unordered same-charge pair and the event denominator."""
    vector.register_awkward()
    muons = ak.zip({
        "pt": events.mu_pt,
        "eta": events.mu_eta,
        "phi": events.mu_phi,
        "mass": events.mu_mass,
        "charge": events.mu_charge,
    }, with_name="Momentum4D")
    muons = muons[ak.num(muons, axis=1) >= 2]
    # Count before pairing: opposite-charge-only events remain in this count.
    n_events = len(muons)
    pairs = ak.combinations(muons, 2, fields=["first", "second"])
    pairs = pairs[pairs.first.charge * pairs.second.charge > 0]
    masses = ak.to_numpy(ak.flatten((pairs.first + pairs.second).mass, axis=1))
    return masses, n_events


@app.command()
def main(
    n_files: Annotated[int, typer.Option(min=1, help="Number of dataset files.")] = 1,
    output_dir: Annotated[Path, typer.Option(help="Directory for plot_1.png.")] = Path("."),
) -> None:
    """Plot all unique same-charge muon pairs in events with at least two muons."""
    masses, n_events = pair_masses(fetch_muons(n_files))
    if n_events == 0 or len(masses) == 0:
        raise RuntimeError("No selected events or same-charge pairs in these files.")
    if not np.all(np.isfinite(masses)):
        raise RuntimeError("Nonfinite pair masses encountered.")

    # Compute both metrics from the raw, unweighted fill values, never bins.
    avg_entries = len(masses) / n_events
    mean_mass = float(np.mean(masses))
    # Include every raw mass in the plotted range, including the largest value.
    upper = max(10.0, float(np.ceil(float(np.max(masses)) / 10.0) * 10.0))
    upper = float(np.nextafter(upper, np.inf))
    histogram = hist.Hist.new.Reg(
        100, 0.0, upper, name="mass", label=r"$m_{\mu\mu}$ [GeV]"
    ).Int64()
    histogram.fill(mass=masses)
    print(f"METRIC: avg_entries_per_event={avg_entries:.12g} mean={mean_mass:.12g}", flush=True)

    plt.style.use(hep.style.ATLAS)
    fig, ax = plt.subplots()
    histogram.plot1d(ax=ax, histtype="step", color="navy")
    ax.set_ylabel("Muon pairs / bin")
    ax.set_title("Same-charge muon pairs ($N_\\mu \\geq 2$)", fontsize=16)
    ax.text(0.97, 0.95, f"ATLAS Open Data simulation\n{n_events:,} selected events\n"
            f"{len(masses):,} same-charge pairs", transform=ax.transAxes,
            ha="right", va="top", fontsize=11)
    ax.set_ylim(bottom=0)
    fig.tight_layout()
    output_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_dir / "plot_1.png", dpi=160)
    plt.close(fig)


if __name__ == "__main__":
    app()
