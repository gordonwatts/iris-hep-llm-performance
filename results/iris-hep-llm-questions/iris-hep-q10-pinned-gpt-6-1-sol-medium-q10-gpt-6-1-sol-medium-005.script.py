#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.13"
# dependencies = [
#   "typer>=0.12",
#   "servicex>=3.0,<4",
#   "func-adl-servicex-xaodr25",
#   "jinja2",
#   "uproot>=5",
#   "awkward>=2",
#   "numpy>=2",
#   "matplotlib>=3.9",
# ]
# ///
"""Unweighted electron pT in the first 20,000 events of one Open Data file.

Run: uv run --script script.py
ServiceX authentication/configuration is read from servicex.yaml as usual.
The public CERN replica below is the specified Rucio file in dataset
opendata:mc20_13TeV.410471.PhPy8EG_A14_ttbar_hdamp258p75_allhad.deriv.
DAOD_PHYSLITE.e6337_s3681_r13167_p6026.
File DID: mc20_13TeV:DAOD_PHYSLITE.37861619._000001.pool.root.1
GUID: 8B18F7A0FD496E40925B81A133BCF8DD
"""

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

app = typer.Typer(add_completion=False)
INPUT_URL = (
    "root://eospublic.cern.ch//eos/opendata/atlas/rucio/mc20_13TeV/"
    "DAOD_PHYSLITE.37861619._000001.pool.root.1"
)
N_EVENTS = 20_000


@app.command()
def main() -> None:
    """Save plot_1.png for electrons with pT > 25 GeV in 20,000 events."""
    query = (
        FuncADLQueryPHYSLITE()
        .Select(lambda event: {
            "electrons": event.Electrons().Where(
                lambda electron: electron.pt() / 1000.0 > 25.0
            )
        })
        .Select(lambda objects: {
            "electron_pt": objects.electrons.Select(
                lambda electron: electron.pt() / 1000.0
            )
        })
    )
    # A single explicit replica selects exactly the requested file. No event
    # filter is applied: empty electron lists must remain in the denominator.
    result = deliver(
        ServiceXSpec(Sample=[Sample(
            Name="electron_pt",
            Dataset=dataset.FileList([INPUT_URL]),
            NFiles=1,
            Query=query,
        )]),
        return_exceptions=False,
    )
    files = list(result["electron_pt"])
    if len(files) != 1:
        raise RuntimeError(f"Expected one transformed input file, got {len(files)}")
    with uproot.open(files[0]) as root_file:
        tree = root_file["atlas_xaod_tree"]
        if tree.num_entries < N_EVENTS:
            raise RuntimeError(f"Expected at least {N_EVENTS} events, got {tree.num_entries}")
        # ServiceX keeps event order. Slice before flattening, retaining events
        # with zero selected electrons among these first 20,000 rows.
        electron_pt = tree["electron_pt"].array(entry_stop=N_EVENTS, library="ak")

    values = ak.to_numpy(ak.flatten(electron_pt, axis=1)).astype(np.float64)
    if values.size == 0 or not np.all(np.isfinite(values)):
        raise RuntimeError("Expected nonempty, finite electron pT values")
    if not np.all(values > 25.0):
        raise RuntimeError("Electron pT selection failed")
    # Metrics come directly from the raw fill values, never from bin contents.
    mean = float(np.mean(values))
    avg_entries_per_event = values.size / len(electron_pt)

    fig, ax = plt.subplots(figsize=(8, 6))
    # Include the complete selected range so no fill values are hidden in flow.
    upper_edge = max(100.0, float(np.ceil(values.max() / 25.0) * 25.0))
    bins = np.linspace(25.0, upper_edge, 61)
    ax.hist(values, bins=bins, histtype="step", linewidth=1.8, color="navy")
    ax.set_xlabel(r"Electron $p_T$ [GeV]")
    ax.set_ylabel("Electrons / bin")
    ax.set_title(r"Electrons with $p_T > 25$ GeV")
    ax.text(0.96, 0.95, "ATLAS Open Data\n" + f"First {N_EVENTS:,} events\nUnweighted",
            transform=ax.transAxes, ha="right", va="top")
    ax.set_xlim(25.0, upper_edge)
    ax.set_ylim(bottom=0)
    fig.tight_layout()
    fig.savefig(Path("plot_1.png"), dpi=160)
    print(f"METRIC: avg_entries_per_event={avg_entries_per_event:.10g} mean={mean:.10g}", flush=True)
    plt.close(fig)


if __name__ == "__main__":
    app()
