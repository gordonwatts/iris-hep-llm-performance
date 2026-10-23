#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.13"
# dependencies = [
#   "awkward>=2.6",
#   "func_adl_servicex_xaodr25",
#   "jinja2",
#   "matplotlib",
#   "servicex",
#   "servicex-analysis-utils",
#   "typer",
# ]
# ///
"""Plot electron transverse momentum from the requested OpenData PHYSLITE file."""

from __future__ import annotations

import math
from pathlib import Path

import awkward as ak
import matplotlib.pyplot as plt
import typer
from func_adl_servicex_xaodr25 import FuncADLQueryPHYSLITE
from servicex import Sample, ServiceXSpec, dataset, deliver
from servicex_analysis_utils import to_awk


app = typer.Typer(add_completion=False, help="Plot selected electron pT from the requested Rucio file.")

DATASET_DID = (
    "opendata:mc20_13TeV.410471.PhPy8EG_A14_ttbar_hdamp258p75_allhad."
    "deriv.DAOD_PHYSLITE.e6337_s3681_r13167_p6026"
)
FILE_DID = "mc20_13TeV:DAOD_PHYSLITE.37861619._000001.pool.root.1"
FILE_GUID = "8B18F7A0FD496E40925B81A133BCF8DD"
MAX_EVENTS = 20_000
SAMPLE_NAME = "electron_pt"


def fetch_electron_pt() -> ak.Array:
    """Fetch electron pT values (GeV) from the explicitly named Rucio file."""
    base_query = FuncADLQueryPHYSLITE()
    query = (
        base_query
        .Select(
            lambda event: {
                "electrons": event.Electrons().Where(
                    lambda electron: electron.pt() / 1000.0 > 25.0
                )
            }
        )
        .Select(
            lambda collections: {
                "electron_pt": collections.electrons.Select(
                    lambda electron: electron.pt() / 1000.0
                )
            }
        )
    )

    delivered = deliver(
        ServiceXSpec(
            Sample=[
                Sample(
                    Name=SAMPLE_NAME,
                    Dataset=dataset.Rucio(FILE_DID),
                    NFiles=1,
                    Query=query,
                )
            ]
        )
    )
    arrays = to_awk(delivered)
    return arrays[SAMPLE_NAME]["electron_pt"]


@app.command()
def main(
    output_dir: Path = typer.Option(Path("."), help="Directory for plot_1.png."),
) -> None:
    """Fetch the file, plot electron pT for the first 20,000 events, and print metrics."""
    # Keep the requested dataset and GUID visible alongside the file DID for provenance.
    _ = DATASET_DID, FILE_GUID
    event_values = fetch_electron_pt()[:MAX_EVENTS]
    number_of_events = len(event_values)
    raw_pt_values = [float(value) for value in ak.to_list(ak.flatten(event_values, axis=None))]

    output_dir.mkdir(parents=True, exist_ok=True)
    plot_path = output_dir / "plot_1.png"
    figure, axis = plt.subplots(figsize=(8, 6))
    axis.hist(raw_pt_values, bins=50, histtype="step", linewidth=1.8)
    axis.set_xlabel(r"Electron $p_T$ [GeV]")
    axis.set_ylabel("Electrons")
    axis.set_title("Electron transverse momentum, pT > 25 GeV")
    axis.grid(alpha=0.25)
    figure.tight_layout()
    figure.savefig(plot_path, dpi=150)
    plt.close(figure)

    mean = math.fsum(raw_pt_values) / len(raw_pt_values) if raw_pt_values else float("nan")
    average_entries = len(raw_pt_values) / number_of_events if number_of_events else float("nan")
    print(f"METRIC: avg_entries_per_event={average_entries:.6f} mean={mean:.6f}", flush=True)


if __name__ == "__main__":
    app()
