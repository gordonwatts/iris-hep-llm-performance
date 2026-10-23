#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.13"
# dependencies = [
#   "typer>=0.12",
#   "servicex>=3.0,<4",
#   "func_adl_servicex_xaodr25",
#   "jinja2",
#   "uproot>=5,<6",
#   "awkward>=2,<3",
#   "numpy>=2",
#   "hist>=2,<3",
#   "matplotlib>=3.9",
#   "mplhep>=0.3",
# ]
# ///
"""Plot unweighted electron pT from the first 20000 events of one PHYSLITE file.

Run with: uv run --script script.py
Requires access to a configured ServiceX endpoint (e.g. servicex.yaml).
The file is selected explicitly, rather than taking an arbitrary dataset file.
"""

import os
from pathlib import Path
import tempfile

os.environ.setdefault("MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "mplconfig"))

import awkward as ak
from func_adl_servicex_xaodr25 import FuncADLQueryPHYSLITE
import hist
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mplhep as hep
import numpy as np
from servicex import Sample, ServiceXSpec, dataset, deliver
import typer
import uproot

DATASET_DID = (
    "opendata:mc20_13TeV.410471.PhPy8EG_A14_ttbar_hdamp258p75_allhad."
    "deriv.DAOD_PHYSLITE.e6337_s3681_r13167_p6026"
)
FILE_DID = "mc20_13TeV:DAOD_PHYSLITE.37861619._000001.pool.root.1"
FILE_GUID = "8B18F7A0FD496E40925B81A133BCF8DD"
EVENT_LIMIT = 20_000

app = typer.Typer(add_completion=False)


@app.command()
def main() -> None:
    """Fetch the specified PHYSLITE file and save plot_1.png with raw-value metrics."""
    # No event selection: empty electron collections must remain in the output.
    query = (
        FuncADLQueryPHYSLITE()
        .Select(lambda event: {
            "electrons": event.Electrons().Where(lambda e: e.pt() / 1000.0 > 25.0)
        })
        .Select(lambda collections: {
            "electron_pt": collections.electrons.Select(lambda e: e.pt() / 1000.0)
        })
    )
    results = deliver(
        ServiceXSpec(Sample=[Sample(
            Name="electron_pt",
            Dataset=dataset.Rucio(FILE_DID),
            NFiles=1,
            Query=query,
        )]),
        return_exceptions=False,
    )
    paths = list(results["electron_pt"])
    if len(paths) != 1:
        raise RuntimeError(f"Expected one transformed input file, got {len(paths)}")
    with uproot.open(paths[0]) as root_file:
        tree = root_file["atlas_xaod_tree"]
        if tree.num_entries < EVENT_LIMIT:
            raise RuntimeError(f"Input has only {tree.num_entries} events; need {EVENT_LIMIT}")
        # ServiceX preserves event order and produces one row even for empty lists.
        events = tree.arrays(["electron_pt"], entry_stop=EVENT_LIMIT, library="ak")

    n_events = len(events)
    values = ak.to_numpy(ak.flatten(events.electron_pt, axis=1))
    if not len(values) or not np.all(np.isfinite(values)) or not np.all(values > 25):
        raise RuntimeError("Expected finite electron pT values strictly above 25 GeV")
    # Compute from the actual fill values, independently of the histogram API.
    mean = float(np.mean(values, dtype=np.float64))
    avg_entries = len(values) / n_events

    # Include the entire tail so every raw value is visible in the histogram.
    upper = max(250.0, float(np.ceil(values.max() / 25.0) * 25.0))
    h = hist.Hist.new.Reg(60, 25.0, upper, name="pt", label=r"Electron $p_T$ [GeV]").Int64()
    h.fill(pt=values)
    plt.style.use(hep.style.ATLAS)
    fig, ax = plt.subplots()
    h.plot1d(ax=ax, histtype="step", color="tab:blue")
    ax.set_ylabel("Electrons / bin")
    ax.set_title(r"Electrons with $p_T > 25$ GeV")
    ax.text(0.97, 0.95, "ATLAS Open Data simulation\nFirst 20,000 events; unweighted",
            transform=ax.transAxes, ha="right", va="top", fontsize=11)
    ax.set_yscale("log")
    ax.set_ylim(bottom=0.5)
    fig.tight_layout()
    fig.savefig("plot_1.png", dpi=150)
    print(f"METRIC: avg_entries_per_event={avg_entries:.10g} mean={mean:.10g}", flush=True)
    plt.close(fig)


if __name__ == "__main__":
    app()
