#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.13"
# dependencies = [
#   "typer>=0.12",
#   "servicex>=3.0,<4",
#   "func_adl_servicex_xaodr25",
#   "jinja2",
#   "uproot>=5",
#   "awkward>=2",
#   "numpy",
#   "hist>=2",
#   "matplotlib",
#   "mplhep",
# ]
# ///
"""Plot electrons above 25 GeV from the first 20,000 events of one PHYSLITE file.

Run with: uv run --script script.py
Requires a valid ServiceX configuration (e.g. servicex.yaml in this directory).
ServiceX extracts the electron column from the exact file; the event limit is
applied locally in original entry order, before flattening the electron lists.
"""

from pathlib import Path

import awkward as ak
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mplhep as hep
import numpy as np
import typer
import uproot
from func_adl_servicex_xaodr25 import FuncADLQueryPHYSLITE
from hist import Hist
from servicex import Sample, ServiceXSpec, dataset, deliver

app = typer.Typer(add_completion=False)

DATASET_DID = (
    "opendata:mc20_13TeV.410471.PhPy8EG_A14_ttbar_hdamp258p75_allhad."
    "deriv.DAOD_PHYSLITE.e6337_s3681_r13167_p6026"
)
FILE_DID = "mc20_13TeV:DAOD_PHYSLITE.37861619._000001.pool.root.1"
FILE_GUID = "8B18F7A0FD496E40925B81A133BCF8DD"
N_EVENTS = 20_000


@app.command()
def main() -> None:
    """Fetch the specified PHYSLITE file and save plot_1.png with raw metrics."""
    query = (
        FuncADLQueryPHYSLITE()
        .Select(lambda event: {
            "electrons": event.Electrons().Where(lambda el: el.pt() / 1000.0 > 25.0)
        })
        .Select(lambda collections: {
            "electron_pt": collections.electrons.Select(lambda el: el.pt() / 1000.0)
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
        raise RuntimeError(f"Expected exactly one transformed file, got {len(files)}")
    with uproot.open(str(files[0])) as root_file:
        trees = [obj for _, obj in root_file.items()
                 if isinstance(obj, uproot.behaviors.TTree.TTree)]
        if len(trees) != 1:
            raise RuntimeError(f"Expected one output tree, got {len(trees)}")
        tree = trees[0]
        if tree.num_entries < N_EVENTS:
            raise RuntimeError(f"Input has only {tree.num_entries} events")
        electron_pt = tree["electron_pt"].array(entry_stop=N_EVENTS, library="ak")

    # No event-level selection: empty electron lists remain in the denominator.
    n_events = len(electron_pt)
    values = ak.to_numpy(ak.flatten(electron_pt, axis=1)).astype(np.float64)
    if values.size == 0 or not np.all(np.isfinite(values)):
        raise RuntimeError("Expected nonempty, finite electron transverse momenta")
    if not np.all(values > 25.0):
        raise RuntimeError("Electron pT selection was not applied correctly")
    avg_entries = values.size / n_events
    mean = float(np.mean(values))

    # Include every selected value in the visible histogram, without weights.
    upper_edge = max(100.0, 10.0 * np.ceil((float(values.max()) + 1.0) / 10.0))
    histogram = Hist.new.Reg(
        60, 25.0, upper_edge, name="pt", label=r"Electron $p_T$ [GeV]"
    ).Int64()
    histogram.fill(pt=values)
    plt.style.use(hep.style.ATLAS)
    fig, ax = plt.subplots()
    histogram.plot1d(ax=ax, histtype="step", color="tab:blue")
    ax.set_ylabel("Electrons / bin")
    ax.set_title(r"Electron $p_T > 25$ GeV")
    ax.text(0.97, 0.95, r"$t\bar{t}$ all-hadronic" + "\nFirst 20,000 events",
            transform=ax.transAxes, ha="right", va="top", fontsize=13)
    ax.set_xlim(25.0, upper_edge)
    fig.tight_layout()
    fig.savefig(Path("plot_1.png"), dpi=160)
    print(f"METRIC: avg_entries_per_event={avg_entries:.12g} mean={mean:.12g}", flush=True)
    plt.close(fig)


if __name__ == "__main__":
    app()
