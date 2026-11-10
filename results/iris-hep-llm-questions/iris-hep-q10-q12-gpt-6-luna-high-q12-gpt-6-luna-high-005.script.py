#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.13"
# dependencies = [
#   "typer>=0.12",
#   "servicex>=3.0.0",
#   "func-adl-servicex-xaodr25",
#   "jinja2",
#   "uproot>=5.3",
#   "awkward>=2.6",
#   "numpy>=2.0",
#   "matplotlib>=3.9",
# ]
# ///
"""Plot invariant masses of unique same-charge muon pairs from ATLAS OpenData."""

from __future__ import annotations

import logging
import math
from pathlib import Path

import awkward as ak
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import typer
import uproot
from func_adl_servicex_xaodr25 import FuncADLQueryPHYSLITE
from servicex import Sample, ServiceXSpec, dataset, deliver


DATASET = (
    "opendata:mc20_13TeV.700325.Sh_2211_Zmumu_maxHTpTV2_CVetoBVeto."
    "deriv.DAOD_PHYSLITE.e8351_s3681_r13167_p6026"
)
MUON_MASS_GEV = 0.1056583755
app = typer.Typer(add_completion=False)


def make_query():
    """Keep events with at least two muons and return their four-vector inputs."""
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


def read_events(root_paths: list[str]) -> tuple[list[dict[str, ak.Array]], int]:
    """Read the ServiceX output tree and return its events in chunks."""
    chunks: list[dict[str, ak.Array]] = []
    event_count = 0
    required = {"mu_pt", "mu_eta", "mu_phi", "mu_charge"}
    for path in root_paths:
        with uproot.open(path) as root_file:
            tree = None
            for key, classname in root_file.classnames().items():
                if classname.startswith("TTree"):
                    candidate = root_file[key]
                    if required.issubset(set(candidate.keys())):
                        tree = candidate
                        break
            if tree is None:
                raise RuntimeError(f"No ServiceX tree with branches {sorted(required)} in {path}")
            arrays = tree.arrays(sorted(required), library="ak")
            chunks.append({name: arrays[name] for name in required})
            event_count += len(arrays)
    return chunks, event_count


def invariant_mass_values(chunks: list[dict[str, ak.Array]]) -> np.ndarray:
    """Build raw invariant masses for every unique same-charge muon pair."""
    masses: list[float] = []
    for chunk in chunks:
        pts = ak.to_list(chunk["mu_pt"])
        etas = ak.to_list(chunk["mu_eta"])
        phis = ak.to_list(chunk["mu_phi"])
        charges = ak.to_list(chunk["mu_charge"])
        for event_pt, event_eta, event_phi, event_charge in zip(pts, etas, phis, charges):
            count = len(event_pt)
            for i in range(count):
                for j in range(i + 1, count):
                    if event_charge[i] != event_charge[j]:
                        continue
                    px1 = event_pt[i] * math.cos(event_phi[i])
                    py1 = event_pt[i] * math.sin(event_phi[i])
                    pz1 = event_pt[i] * math.sinh(event_eta[i])
                    e1 = math.sqrt(
                        (event_pt[i] * math.cosh(event_eta[i])) ** 2 + MUON_MASS_GEV**2
                    )
                    px2 = event_pt[j] * math.cos(event_phi[j])
                    py2 = event_pt[j] * math.sin(event_phi[j])
                    pz2 = event_pt[j] * math.sinh(event_eta[j])
                    e2 = math.sqrt(
                        (event_pt[j] * math.cosh(event_eta[j])) ** 2 + MUON_MASS_GEV**2
                    )
                    mass2 = (e1 + e2) ** 2 - (px1 + px2) ** 2 - (py1 + py2) ** 2 - (pz1 + pz2) ** 2
                    masses.append(math.sqrt(max(mass2, 0.0)))
    return np.asarray(masses, dtype=np.float64)


@app.command()
def main(
    n_files: int = typer.Option(1, "--n-files", min=1, help="Number of dataset files to process."),
    output_dir: Path = typer.Option(Path("."), "--output-dir", help="Directory for plot_<n>.png."),
) -> None:
    """Fetch one or more files and plot every unique same-charge muon-pair mass."""
    logging.getLogger().setLevel(logging.ERROR)
    query = make_query()
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

    paths = [str(path) for path in delivered["same_charge_muons"]]
    if not paths:
        raise RuntimeError("ServiceX returned no files.")
    chunks, selected_event_count = read_events(paths)
    if selected_event_count == 0:
        raise RuntimeError("No events with at least two muons were returned.")

    masses = invariant_mass_values(chunks)
    mean = float(np.mean(masses)) if len(masses) else float("nan")
    average_entries = len(masses) / selected_event_count

    output_dir.mkdir(parents=True, exist_ok=True)
    plot_path = output_dir / "plot_1.png"
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.hist(masses, bins=60, range=(0.0, 300.0), histtype="step", linewidth=1.5)
    ax.set_xlabel("Same-charge dimuon invariant mass [GeV]")
    ax.set_ylabel("Muon pairs")
    ax.set_title("Same-charge muon pairs")
    fig.tight_layout()
    fig.savefig(plot_path, dpi=150)
    plt.close(fig)

    print(f"METRIC: avg_entries_per_event={average_entries:.12g} mean={mean:.12g}", flush=True)


if __name__ == "__main__":
    app()
