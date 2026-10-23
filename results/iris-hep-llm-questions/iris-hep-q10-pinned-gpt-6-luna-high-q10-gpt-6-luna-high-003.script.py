#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.13"
# dependencies = [
#   "awkward>=2.6",
#   "func_adl_servicex_xaodr25",
#   "jinja2",
#   "matplotlib>=3.8",
#   "numpy>=1.26",
#   "servicex>=3.0",
#   "typer>=0.12",
#   "uproot>=5.3",
# ]
# ///
"""Plot selected electron transverse momenta from the requested OpenData file."""

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
EVENT_LIMIT = 20_000
SAMPLE_NAME = "electron_pt"


def fetch_file() -> list[Path]:
    """Fetch the exact Rucio file with only electron pT values above 25 GeV."""
    query = (
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
    return [Path(path) for path in delivered[SAMPLE_NAME]]


def read_first_events(root_path: Path) -> tuple[np.ndarray, int]:
    """Read the first 20,000 event rows and flatten their selected electron pT."""
    with uproot.open(root_path) as root_file:
        trees = [
            root_file[key]
            for key in root_file.keys(cycle=False)
            if hasattr(root_file[key], "num_entries")
            and hasattr(root_file[key], "arrays")
        ]
        if not trees:
            raise RuntimeError(f"No event tree found in {root_path}")
        tree = trees[0]
        event_count = min(EVENT_LIMIT, int(tree.num_entries))
        branch_names = [str(name).split(";")[0] for name in tree.keys()]
        matches = [name for name in branch_names if name.rsplit(".", 1)[-1] == "electron_pt"]
        if not matches:
            raise RuntimeError(
                f"Could not find the electron_pt branch; branches are {branch_names}"
            )
        values = tree[matches[0]].array(entry_stop=event_count, library="ak")
        flat_values = ak.to_numpy(ak.flatten(values, axis=None)).astype(float)
    return flat_values, event_count


def make_plot(values: np.ndarray, plot_number: int, event_count: int) -> Path:
    if values.size == 0:
        raise RuntimeError("No electrons with pT > 25 GeV were found in the selected events")

    mean = float(np.mean(values))
    average_entries = float(values.size / event_count)
    print(
        f"METRIC: avg_entries_per_event={average_entries:.6f} mean={mean:.6f}",
        flush=True,
    )

    output = Path(f"plot_{plot_number}.png")
    fig, ax = plt.subplots(figsize=(8, 5.5), constrained_layout=True)
    ax.hist(values, bins=50, color="#4477aa", edgecolor="white", linewidth=0.5)
    ax.set_xlabel(r"Electron $p_T$ [GeV]")
    ax.set_ylabel("Electrons")
    ax.set_title(r"Electrons with $p_T > 25$ GeV")
    ax.grid(axis="y", alpha=0.25)
    fig.savefig(output, dpi=150)
    plt.close(fig)
    return output


@app.command()
def main() -> None:
    """Fetch the requested PHYSLITE file and plot electron pT for its first 20,000 events."""
    files = fetch_file()
    if not files:
        raise RuntimeError("ServiceX returned no files")
    values, event_count = read_first_events(files[0])
    if event_count == 0:
        raise RuntimeError("The input file contains no events")
    output = make_plot(values, plot_number=1, event_count=event_count)
    typer.echo(f"Saved {output}")


if __name__ == "__main__":
    app()
