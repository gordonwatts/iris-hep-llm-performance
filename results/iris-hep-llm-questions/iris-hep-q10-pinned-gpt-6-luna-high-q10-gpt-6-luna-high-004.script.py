#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.13"
# dependencies = [
#   "typer>=0.12",
#   "servicex>=3.0.0",
#   "func-adl-servicex-xaodr25",
#   "jinja2",
#   "uproot>=5",
#   "numpy>=2",
#   "matplotlib>=3.8",
# ]
# ///
"""Fetch a PHYSLITE file and plot electron transverse momentum."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import typer
import uproot
from func_adl_servicex_xaodr25 import FuncADLQueryPHYSLITE
from servicex import Sample, ServiceXSpec, dataset, deliver

app = typer.Typer(add_completion=False)

DATASET = (
    "opendata:mc20_13TeV.410471.PhPy8EG_A14_ttbar_hdamp258p75_allhad."
    "deriv.DAOD_PHYSLITE.e6337_s3681_r13167_p6026"
)
FILE_DID = "mc20_13TeV:DAOD_PHYSLITE.37861619._000001.pool.root.1"
EXPECTED_GUID = "8B18F7A0FD496E40925B81A133BCF8DD"
MAX_EVENTS = 20_000


def _find_tree(root_file: uproot.ReadOnlyDirectory) -> uproot.behaviors.TBranch.HasBranches:
    for key in root_file.keys(recursive=True):
        try:
            obj = root_file[key]
        except Exception:
            continue
        if isinstance(obj, uproot.behaviors.TBranch.HasBranches):
            return obj
    raise RuntimeError("No event tree found in ServiceX output ROOT file")


@app.command()
def main() -> None:
    """Fetch the requested OpenData file and plot electron pT above 25 GeV."""
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

    fetched = deliver(
        ServiceXSpec(
            Sample=[
                Sample(
                    Name="electron_pt",
                    Dataset=dataset.Rucio(FILE_DID),
                    NFiles=1,
                    Query=query,
                )
            ]
        )
    )
    files = [Path(str(path)) for path in fetched["electron_pt"]]
    if not files:
        raise RuntimeError("ServiceX returned no output ROOT files")

    raw_values: list[np.ndarray] = []
    n_events = 0
    for output_file in files:
        with uproot.open(output_file) as root_file:
            tree = _find_tree(root_file)
            take = min(MAX_EVENTS - n_events, tree.num_entries)
            if take <= 0:
                break
            branches = tree.arrays(
                ["electron_pt"], entry_start=0, entry_stop=take, library="np"
            )
            pts_per_event = branches["electron_pt"]
            raw_values.extend(np.asarray(values, dtype=float) for values in pts_per_event)
            n_events += take
        if n_events >= MAX_EVENTS:
            break

    values = np.concatenate(raw_values) if raw_values else np.asarray([], dtype=float)
    output = Path("plot_1.png")
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.hist(values, bins=50, histtype="step", linewidth=1.8)
    ax.set_xlabel(r"Electron transverse momentum $p_T$ [GeV]")
    ax.set_ylabel("Electrons")
    ax.set_title(r"Electrons with $p_T > 25$ GeV (first 20,000 events)")
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(output, dpi=150)
    plt.close(fig)

    mean = float(np.mean(values)) if values.size else float("nan")
    average_entries = values.size / n_events if n_events else float("nan")
    print(f"METRIC: avg_entries_per_event={average_entries} mean={mean}", flush=True)
    print(f"Saved {output} using {n_events} events from {FILE_DID} (GUID {EXPECTED_GUID})")


if __name__ == "__main__":
    app()
