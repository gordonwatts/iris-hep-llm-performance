#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.13"
# dependencies = [
#   "typer>=0.12",
#   "servicex>=3.0",
#   "func-adl-servicex-xaodr25",
#   "jinja2",
#   "uproot>=5",
#   "awkward>=2",
#   "numpy>=2",
#   "matplotlib>=3.8",
# ]
# ///
"""Plot electron transverse momenta from one OpenData PHYSLITE Rucio file."""

from pathlib import Path

import awkward as ak
import matplotlib.pyplot as plt
import numpy as np
import typer
import uproot
from func_adl_servicex_xaodr25 import FuncADLQueryPHYSLITE
from servicex import Sample, ServiceXSpec, dataset, deliver

app = typer.Typer(add_completion=False)

FILE_DID = "mc20_13TeV:DAOD_PHYSLITE.37861619._000001.pool.root.1"
DATASET_DID = (
    "opendata:mc20_13TeV.410471.PhPy8EG_A14_ttbar_hdamp258p75_allhad."
    "deriv.DAOD_PHYSLITE.e6337_s3681_r13167_p6026"
)
SAMPLE_NAME = "electron_pt"
MAX_EVENTS = 20_000


def make_query():
    return (
        FuncADLQueryPHYSLITE()
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


@app.command()
def main(
    output_dir: Path = typer.Option(Path("."), "--output-dir", help="Directory for plot_1.png."),
) -> None:
    """Fetch the first 20,000 events and plot electron pT above 25 GeV."""
    output_dir.mkdir(parents=True, exist_ok=True)
    results = deliver(
        ServiceXSpec(
            Sample=[
                Sample(
                    Name=SAMPLE_NAME,
                    Dataset=dataset.Rucio(FILE_DID),
                    NFiles=1,
                    Query=make_query(),
                )
            ]
        )
    )

    files = [str(path) for path in results[SAMPLE_NAME]]
    if not files:
        raise RuntimeError(f"ServiceX returned no files for {FILE_DID} (dataset {DATASET_DID}).")

    event_arrays = [
        uproot.open(f"{root_file}:atlas_xaod_tree")["electron_pt"].array(library="ak")
        for root_file in files
    ]
    event_pts = ak.concatenate(event_arrays, axis=0)[:MAX_EVENTS]
    n_events = len(event_pts)
    if n_events == 0:
        raise RuntimeError("The returned file contains no events.")

    # These are the unweighted raw values passed directly to the histogram.
    values = np.asarray(ak.to_numpy(ak.flatten(event_pts, axis=1)), dtype=float)
    if values.size == 0:
        raise RuntimeError("No electrons passed the pT > 25 GeV selection.")

    figure, axis = plt.subplots(figsize=(8, 6))
    axis.hist(values, bins=50, histtype="step", linewidth=1.8)
    axis.set_xlabel(r"Electron $p_T$ [GeV]")
    axis.set_ylabel("Entries")
    axis.set_title(r"Electrons with $p_T > 25$ GeV")
    axis.grid(alpha=0.25)
    figure.tight_layout()
    figure.savefig(output_dir / "plot_1.png", dpi=150)
    plt.close(figure)

    mean = float(np.mean(values))
    average_entries = values.size / n_events
    print(f"METRIC: avg_entries_per_event={average_entries:.12g} mean={mean:.12g}", flush=True)


if __name__ == "__main__":
    app()
