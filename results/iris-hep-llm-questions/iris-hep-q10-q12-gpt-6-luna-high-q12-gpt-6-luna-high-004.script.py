#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.13"
# dependencies = [
#   "awkward>=2.6",
#   "func_adl_servicex_xaodr25",
#   "jinja2",
#   "matplotlib>=3.8",
#   "numpy>=2.0",
#   "servicex>=3.0",
#   "typer>=0.12",
#   "uproot>=5.3",
# ]
# ///
"""Plot same-charge dimuon invariant masses from an OpenData PHYSLITE sample."""

from pathlib import Path

import awkward as ak
import matplotlib.pyplot as plt
import numpy as np
import typer
import uproot
from func_adl_servicex_xaodr25 import FuncADLQueryPHYSLITE
from servicex import Sample, ServiceXSpec, dataset, deliver

app = typer.Typer(add_completion=False)

DATASET = (
    "opendata:mc20_13TeV.700325.Sh_2211_Zmumu_maxHTpTV2_CVetoBVeto."
    "deriv.DAOD_PHYSLITE.e8351_s3681_r13167_p6026"
)
MUON_MASS_GEV = 0.1056583755


def make_query():
    """Return muon kinematics for events containing at least two muons."""
    return (
        FuncADLQueryPHYSLITE()
        .Select(lambda event: {"muons": event.Muons()})
        .Where(lambda collections: collections.muons.Count() >= 2)
        .Select(
            lambda collections: {
                "mu_pt": collections.muons.Select(lambda muon: muon.pt() / 1000.0),
                "mu_eta": collections.muons.Select(lambda muon: muon.eta()),
                "mu_phi": collections.muons.Select(lambda muon: muon.phi()),
                "mu_charge": collections.muons.Select(lambda muon: muon.charge()),
            }
        )
    )


def pair_masses(pt_values, eta_values, phi_values, charges) -> list[float]:
    """Build masses for every unique pair with equal nonzero charge."""
    masses: list[float] = []
    for pts, etas, phis, event_charges in zip(
        ak.to_list(pt_values),
        ak.to_list(eta_values),
        ak.to_list(phi_values),
        ak.to_list(charges),
    ):
        count = len(pts)
        for i in range(count):
            for j in range(i + 1, count):
                if event_charges[i] != event_charges[j]:
                    continue
                px1 = pts[i] * np.cos(phis[i])
                py1 = pts[i] * np.sin(phis[i])
                pz1 = pts[i] * np.sinh(etas[i])
                px2 = pts[j] * np.cos(phis[j])
                py2 = pts[j] * np.sin(phis[j])
                pz2 = pts[j] * np.sinh(etas[j])
                e1 = np.sqrt((pts[i] * np.cosh(etas[i])) ** 2 + MUON_MASS_GEV**2)
                e2 = np.sqrt((pts[j] * np.cosh(etas[j])) ** 2 + MUON_MASS_GEV**2)
                mass_squared = (e1 + e2) ** 2 - (px1 + px2) ** 2
                mass_squared -= (py1 + py2) ** 2 + (pz1 + pz2) ** 2
                masses.append(float(np.sqrt(max(mass_squared, 0.0))))
    return masses


@app.command()
def main(
    n_files: int = typer.Option(1, "--n-files", min=1, help="Number of dataset files to process."),
    output_dir: Path = typer.Option(Path("."), "--output-dir", help="Directory for plot_<n>.png."),
) -> None:
    """Fetch one or more dataset files and plot same-charge dimuon masses."""
    query = make_query()
    fetched = deliver(
        ServiceXSpec(
            Sample=[
                Sample(
                    Name="same_charge_dimuons",
                    Dataset=dataset.Rucio(DATASET),
                    NFiles=n_files,
                    Query=query,
                )
            ]
        )
    )

    files = [Path(path) for path in fetched["same_charge_dimuons"]]
    if not files:
        raise RuntimeError("ServiceX returned no ROOT files.")

    all_masses: list[float] = []
    event_count = 0
    for root_path in files:
        with uproot.open(root_path) as root_file:
            arrays = root_file["atlas_xaod_tree"].arrays(
                ["mu_pt", "mu_eta", "mu_phi", "mu_charge"], library="ak"
            )
        event_count += len(arrays)
        all_masses.extend(
            pair_masses(arrays.mu_pt, arrays.mu_eta, arrays.mu_phi, arrays.mu_charge)
        )

    if event_count == 0:
        raise RuntimeError("No events with at least two muons were returned.")

    output_dir.mkdir(parents=True, exist_ok=True)
    plot_path = output_dir / "plot_1.png"
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(all_masses, bins=60, color="steelblue", edgecolor="white")
    ax.set_xlabel("Same-charge dimuon invariant mass [GeV]")
    ax.set_ylabel("Pairs")
    ax.set_title("Same-charge muon pairs")
    fig.tight_layout()
    fig.savefig(plot_path, dpi=150)
    plt.close(fig)

    mean = float(np.mean(all_masses)) if all_masses else float("nan")
    average_entries = len(all_masses) / event_count
    print(f"METRIC: avg_entries_per_event={average_entries} mean={mean}", flush=True)


if __name__ == "__main__":
    app()
