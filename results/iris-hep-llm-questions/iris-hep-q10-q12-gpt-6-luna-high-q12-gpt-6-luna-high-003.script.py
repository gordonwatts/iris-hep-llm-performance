#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.13"
# dependencies = [
#   "awkward>=2.6",
#   "func_adl_servicex_xaodr25",
#   "hep-llm-helpers>=1.0.0b1",
#   "jinja2",
#   "matplotlib",
#   "numpy",
#   "servicex",
#   "servicex-analysis-utils",
#   "typer>=0.12",
# ]
# ///
"""Plot same-charge dimuon invariant masses from one or more OpenData files."""

from __future__ import annotations

import math
from pathlib import Path

import awkward as ak
import matplotlib.pyplot as plt
import numpy as np
import typer
from func_adl_servicex_xaodr25 import FuncADLQueryPHYSLITE
from servicex import Sample, ServiceXSpec, dataset, deliver
from servicex_analysis_utils import to_awk

app = typer.Typer(add_completion=False)

DATASET = (
    "opendata:mc20_13TeV.700325.Sh_2211_Zmumu_maxHTpTV2_CVetoBVeto."
    "deriv.DAOD_PHYSLITE.e8351_s3681_r13167_p6026"
)
MUON_MASS_GEV = 0.1056583755


def make_query():
    base_query = FuncADLQueryPHYSLITE()
    return (
        base_query
        .Where(lambda event: event.Muons().Count() >= 2)
        .Select(lambda event: {"muons": event.Muons()})
        .Select(
            lambda collections: {
                "mu_pt": collections.muons.Select(lambda mu: mu.pt() / 1000.0),
                "mu_eta": collections.muons.Select(lambda mu: mu.eta()),
                "mu_phi": collections.muons.Select(lambda mu: mu.phi()),
                "mu_charge": collections.muons.Select(lambda mu: mu.charge()),
            }
        )
    )


def invariant_mass(pt1: float, eta1: float, phi1: float,
                   pt2: float, eta2: float, phi2: float) -> float:
    """Return the dimuon invariant mass in GeV, using the muon rest mass."""
    px1, py1 = pt1 * math.cos(phi1), pt1 * math.sin(phi1)
    px2, py2 = pt2 * math.cos(phi2), pt2 * math.sin(phi2)
    pz1, pz2 = pt1 * math.sinh(eta1), pt2 * math.sinh(eta2)
    e1 = math.sqrt(px1 * px1 + py1 * py1 + pz1 * pz1 + MUON_MASS_GEV**2)
    e2 = math.sqrt(px2 * px2 + py2 * py2 + pz2 * pz2 + MUON_MASS_GEV**2)
    mass2 = (e1 + e2) ** 2 - (px1 + px2) ** 2 - (py1 + py2) ** 2 - (pz1 + pz2) ** 2
    return math.sqrt(max(mass2, 0.0))


@app.command()
def main(
    n_files: int = typer.Option(1, "--n-files", min=1, help="Number of dataset files to process."),
    output_dir: Path = typer.Option(Path("."), "--output-dir", help="Directory for plot_<n>.png files."),
) -> None:
    """Plot same-charge muon-pair masses and print raw-value metrics."""
    query = make_query()
    delivered = deliver(
        ServiceXSpec(
            Sample=[
                Sample(
                    Name="same_charge_dimuon",
                    Dataset=dataset.Rucio(DATASET),
                    NFiles=n_files,
                    Query=query,
                )
            ]
        )
    )

    event_records = to_awk(delivered)["same_charge_dimuon"]
    masses: list[float] = []
    selected_events = 0
    for event in ak.to_list(event_records):
        # The query already requires at least two muons. Keep the count here so
        # events without any same-charge pair remain in the metric denominator.
        selected_events += 1
        pts = event["mu_pt"]
        etas = event["mu_eta"]
        phis = event["mu_phi"]
        charges = event["mu_charge"]
        for i in range(len(pts)):
            for j in range(i + 1, len(pts)):
                if charges[i] == charges[j]:
                    masses.append(
                        invariant_mass(pts[i], etas[i], phis[i], pts[j], etas[j], phis[j])
                    )

    output_dir.mkdir(parents=True, exist_ok=True)
    plot_path = output_dir / "plot_1.png"
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.hist(masses, bins=50, range=(0, 200), histtype="step", linewidth=1.8)
    ax.set_xlabel("Same-charge dimuon invariant mass [GeV]")
    ax.set_ylabel("Muon pairs")
    ax.set_title("OpenData MC20 same-charge dimuon pairs")
    ax.grid(alpha=0.2)
    fig.tight_layout()
    fig.savefig(plot_path, dpi=150)
    plt.close(fig)

    mean = float(np.mean(masses)) if masses else float("nan")
    avg_entries_per_event = len(masses) / selected_events if selected_events else float("nan")
    print(f"METRIC: avg_entries_per_event={avg_entries_per_event} mean={mean}", flush=True)
    typer.echo(f"Saved {plot_path} from {selected_events} events and {len(masses)} pairs.")


if __name__ == "__main__":
    app()
