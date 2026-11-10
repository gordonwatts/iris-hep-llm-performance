#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.13"
# dependencies = [
#   "typer>=0.12",
#   "servicex>=3,<4",
#   "func_adl_servicex_xaodr25",
#   "jinja2",
#   "awkward>=2",
#   "vector>=1",
#   "uproot>=5",
#   "numpy>=2",
#   "hist>=2",
#   "matplotlib>=3",
#   "mplhep>=0.3",
# ]
# ///
"""Plot all unique same-charge muon-pair masses from one OpenData file.

Run with: uv run --script script.py
ServiceX uses the servicex.yaml configuration in the working directory.
No muon kinematic cuts, event weights, or pair-based event cuts are applied.
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


@app.command()
def main(
    n_files: int = typer.Option(1, "--n-files", "-n", min=1),
    output_dir: Path = typer.Option(Path("."), "--output-dir"),
) -> None:
    """Fetch muons from OpenData and plot unweighted same-charge pair masses."""
    query = (
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
    delivered = deliver(
        ServiceXSpec(
            Sample=[
                Sample(
                    Name="same_charge_muons",
                    Dataset=dataset.Rucio(DATASET),
                    NFiles=n_files,
                    Query=query,
                )
            ]
        )
    )
    chunks = []
    paths = list(delivered["same_charge_muons"])
    if len(paths) != n_files:
        raise RuntimeError(f"Requested {n_files} files, received {len(paths)}")
    for path in paths:
        with uproot.open(str(path)) as root_file:
            chunks.append(root_file["atlas_xaod_tree"].arrays(library="ak"))
    events = ak.concatenate(chunks, axis=0)
    # Count before the pair selection: opposite-charge-only events stay here.
    event_count = len(events)
    if event_count == 0:
        raise RuntimeError("No events with at least two muons in the input")

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
    # combinations makes each unordered pair exactly once, without self-pairs.
    pairs = ak.combinations(muons, 2, fields=["first", "second"], axis=1)
    same_charge = pairs[pairs.first.charge * pairs.second.charge > 0]
    masses = ak.to_numpy(
        ak.flatten((same_charge.first + same_charge.second).mass, axis=1)
    )
    if not np.all(np.isfinite(masses)):
        raise RuntimeError("Encountered a nonfinite pair mass")
    # These statistics use raw, unweighted entries, never histogram contents.
    avg_entries = masses.size / event_count
    mean = float(np.mean(masses)) if masses.size else float("nan")

    # Include every raw value within the displayed range, including the maximum.
    upper = max(100.0, float(np.max(masses)) * 1.01) if masses.size else 100.0
    histogram = hist.Hist.new.Reg(
        100, 0.0, upper, name="mass", label=r"$m_{\mu\mu}$ [GeV]"
    ).Int64()
    histogram.fill(mass=masses)
    plt.style.use(hep.style.ATLAS)
    fig, ax = plt.subplots()
    histogram.plot1d(ax=ax, histtype="step", color="tab:blue")
    ax.set_ylabel("Muon pairs / bin")
    ax.set_title("Same-charge muon pairs, events with at least two muons", fontsize=13)
    ax.text(
        0.97, 0.96,
        f"OpenData simulation\n{event_count:,} events\n{masses.size:,} pairs",
        ha="right", va="top", transform=ax.transAxes, fontsize=12,
    )
    ax.set_ylim(bottom=0)
    output_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_dir / "plot_1.png", dpi=160, bbox_inches="tight")
    print(f"METRIC: avg_entries_per_event={avg_entries:.12g} mean={mean:.12g}", flush=True)
    plt.close(fig)


if __name__ == "__main__":
    app()
