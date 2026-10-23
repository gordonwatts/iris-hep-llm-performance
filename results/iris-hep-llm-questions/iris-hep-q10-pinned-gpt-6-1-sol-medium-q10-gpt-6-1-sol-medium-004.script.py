#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.13"
# dependencies = [
#   "typer>=0.12",
#   "servicex>=3.0",
#   "func_adl_servicex_xaodr25",
#   "jinja2",
#   "uproot>=5",
#   "numpy>=2",
#   "matplotlib>=3.9",
# ]
# ///
"""Plot unweighted electron pT from the first 20,000 events of one xAOD file.

Run with: uv run --script script.py
ServiceX uses the credentials in servicex.yaml (or your usual client config).
The file DID below selects the requested file, rather than an arbitrary file
from the parent dataset. ServiceX extracts one row per original event, including
events with no passing electrons; the client reads only the first 20,000 rows.
"""

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
FILE_GUID = "8B18F7A0FD496E40925B81A133BCF8DD"
N_EVENTS = 20_000


@app.command()
def main() -> None:
    """Fetch the specified PHYSLITE file and save plot_1.png."""
    query = (
        FuncADLQueryPHYSLITE()
        .Select(lambda event: {
            "electrons": event.Electrons().Where(
                lambda electron: electron.pt() / 1000.0 > 25.0
            )
        })
        .Select(lambda collections: {
            "electron_pt": collections.electrons.Select(
                lambda electron: electron.pt() / 1000.0
            )
        })
    )
    delivered = deliver(
        ServiceXSpec(Sample=[Sample(
            Name="electron_pt",
            Dataset=dataset.Rucio(FILE_DID),
            NFiles=1,
            Query=query,
        )])
    )
    files = list(delivered["electron_pt"])
    if len(files) != 1:
        raise RuntimeError(f"Expected exactly one transformed input, got {len(files)}")

    with uproot.open(str(files[0])) as root_file:
        trees = [obj for _, obj in root_file.items() if isinstance(obj, uproot.behaviors.TTree.TTree)]
        if len(trees) != 1:
            raise RuntimeError(f"Expected one output tree, got {len(trees)}")
        tree = trees[0]
        if tree.num_entries < N_EVENTS:
            raise RuntimeError(f"Input has only {tree.num_entries} events; need {N_EVENTS}")
        per_event = tree["electron_pt"].array(entry_stop=N_EVENTS, library="np")

    # No event selection: empty-electron events remain in this denominator.
    n_events = len(per_event)
    values = np.concatenate(per_event).astype(np.float64, copy=False)
    if values.size == 0:
        raise RuntimeError("No electrons passed pT > 25 GeV")
    if not np.all(np.isfinite(values) & (values > 25.0)):
        raise RuntimeError("Unexpected nonfinite or below-threshold pT")
    # Compute both metrics directly from the unweighted raw electron values.
    mean = float(np.mean(values))
    avg_entries_per_event = values.size / n_events

    fig, ax = plt.subplots(figsize=(8, 6))
    # Include every selected value in the displayed range and in the metrics.
    upper_edge = max(100.0, float(np.ceil(values.max() / 25.0) * 25.0))
    ax.hist(values, bins=np.linspace(25.0, upper_edge, 61), histtype="step", linewidth=1.6)
    ax.set_xlabel(r"Electron $p_T$ [GeV]")
    ax.set_ylabel("Electrons / bin")
    ax.set_title(r"Electron $p_T > 25$ GeV; first 20,000 events")
    ax.text(0.97, 0.95, "ATLAS Open Data\n" + r"$t\bar{t}$ all-hadronic, $\sqrt{s}=13$ TeV",
            transform=ax.transAxes, ha="right", va="top")
    ax.set_xlim(25.0, upper_edge)
    ax.set_ylim(bottom=0)
    fig.tight_layout()
    fig.savefig(Path("plot_1.png"), dpi=160)
    print(f"METRIC: avg_entries_per_event={avg_entries_per_event:.10g} mean={mean:.10g}", flush=True)
    plt.close(fig)


if __name__ == "__main__":
    app()
