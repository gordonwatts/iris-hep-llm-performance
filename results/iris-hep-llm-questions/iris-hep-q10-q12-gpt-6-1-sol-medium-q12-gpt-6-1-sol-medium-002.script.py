#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.13"
# dependencies = [
#   "typer>=0.12",
#   "servicex>=3",
#   "func_adl_servicex_xaodr25",
#   "jinja2",
#   "awkward>=2",
#   "vector",
#   "uproot>=5",
#   "numpy",
#   "hist",
#   "matplotlib",
#   "mplhep",
# ]
# ///
"""Plot all unique same-charge muon pairs, using one dataset file by default.

Run: uv run --script script.py
ServiceX uses the local servicex.yaml (or the user's ServiceX configuration).
All masses and transverse momenta are in GeV; no weights are used.
"""

from pathlib import Path

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


def fetch_muons(n_files: int) -> ak.Array:
    """Keep every event with >=2 muons, even if no same-charge pair exists."""
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
        Name="same_charge_muons",
        Dataset=dataset.Rucio(DATASET),
        NFiles=n_files,
        Query=query,
    )]))
    chunks = []
    for filename in delivered["same_charge_muons"]:
        with uproot.open(str(filename)) as root_file:
            trees = [obj for obj in root_file.values() if hasattr(obj, "arrays")]
            if len(trees) != 1:
                raise RuntimeError(f"Expected one output tree in {filename}.")
            chunks.append(trees[0].arrays(library="ak"))
    if not chunks:
        raise RuntimeError("ServiceX returned no files.")
    return ak.concatenate(chunks, axis=0)


def pair_masses(events: ak.Array) -> tuple[np.ndarray, int]:
    """Return raw pair masses and the denominator before pair selection."""
    vector.register_awkward()
    muons = ak.zip({
        "pt": events.mu_pt,
        "eta": events.mu_eta,
        "phi": events.mu_phi,
        "mass": events.mu_mass,
        "charge": events.mu_charge,
    }, with_name="Momentum4D")
    muons = muons[ak.num(muons, axis=1) >= 2]
    n_events = len(muons)
    # combinations gives i < j: no self-pairs or duplicate reversed pairs.
    pairs = ak.combinations(muons, 2, fields=["first", "second"])
    pairs = pairs[pairs.first.charge == pairs.second.charge]
    masses = ak.to_numpy(ak.flatten((pairs.first + pairs.second).mass, axis=1))
    if not np.all(np.isfinite(masses)):
        raise RuntimeError("Nonfinite invariant masses found in the input.")
    return masses, n_events


@app.command()
def main(
    n_files: int = typer.Option(1, min=1, help="Number of input dataset files."),
    output_dir: Path = typer.Option(Path("."), help="Directory for plot_1.png."),
) -> None:
    """Plot unweighted invariant masses of every unique same-charge muon pair."""
    masses, n_events = pair_masses(fetch_muons(n_files))
    if n_events == 0 or masses.size == 0:
        raise RuntimeError("No selected events or same-charge muon pairs to plot.")
    # Compute metrics directly from every raw fill value, never from bins.
    avg_entries_per_event = masses.size / n_events
    mean = float(np.mean(masses))
    # Cover all entries, including the largest mass, with no overflow losses.
    upper = float(np.nextafter(max(1.0, float(np.max(masses))), np.inf))
    histogram = hist.Hist(
        hist.axis.Regular(100, 0, upper, name="mass", label=r"$m_{\mu\mu}$ [GeV]"),
        storage=hist.storage.Int64(),
    )
    histogram.fill(mass=masses)
    plt.style.use(hep.style.ATLAS)
    fig, ax = plt.subplots()
    histogram.plot(ax=ax, histtype="step", color="navy")
    ax.set_ylabel("Muon pairs")
    ax.set_title("Same-charge muon pairs, events with at least two muons", fontsize=12)
    ax.text(0.97, 0.95, f"{n_events:,} events\n{masses.size:,} pairs", 
            ha="right", va="top", transform=ax.transAxes, fontsize=11)
    output_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_dir / "plot_1.png", dpi=160, bbox_inches="tight")
    print(f"METRIC: avg_entries_per_event={avg_entries_per_event:.12g} mean={mean:.12g}", flush=True)
    plt.close(fig)


if __name__ == "__main__":
    app()
