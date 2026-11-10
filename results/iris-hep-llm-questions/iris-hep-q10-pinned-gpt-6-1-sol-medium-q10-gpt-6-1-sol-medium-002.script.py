#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.13"
# dependencies = [
#   "typer>=0.12",
#   "servicex>=3,<4",
#   "func-adl-servicex-xaodr25",
#   "jinja2",
#   "uproot>=5",
#   "awkward>=2",
#   "numpy>=2",
#   "hist>=2",
#   "matplotlib>=3",
#   "mplhep>=0.3",
# ]
# ///
"""Plot unweighted electron pT in the first 20,000 events of one exact file.

Run with: uv run --script script.py
ServiceX credentials are read from the usual servicex.yaml configuration.
Events with no electrons passing the object cut remain in the denominator.
"""

from pathlib import Path

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
    # Keep every event, including empty electron lists. Reading the first
    # 20,000 output rows therefore selects the first 20,000 input events.
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
        )]),
    )
    paths = list(delivered["electron_pt"])
    if len(paths) != 1:
        raise RuntimeError(f"Expected exactly one transformed file; got {len(paths)}")
    with uproot.open(str(paths[0])) as root_file:
        tree = root_file["atlas_xaod_tree"]
        if tree.num_entries < N_EVENTS:
            raise RuntimeError(f"Input contains only {tree.num_entries} events")
        events = tree.arrays(["electron_pt"], entry_stop=N_EVENTS, library="ak")

    values = ak.to_numpy(ak.flatten(events.electron_pt, axis=1))
    event_count = len(events)
    if not len(values):
        raise RuntimeError("No electrons passed pT > 25 GeV")
    if not np.all(np.isfinite(values) & (values > 25.0)):
        raise RuntimeError("Unexpected electron transverse momentum values")
    # Compute metrics directly from the raw, unweighted histogram inputs.
    avg_entries_per_event = len(values) / event_count
    mean = float(np.mean(values))

    # Include all selected electrons in the visible histogram, even the tail.
    upper_edge = max(100.0, 25.0 * np.ceil((float(np.max(values)) + 1.0) / 25.0))
    h = hist.Hist.new.Reg(
        60, 25.0, upper_edge, name="pt", label=r"Electron $p_T$ [GeV]"
    ).Int64()
    h.fill(pt=values)
    plt.style.use(hep.style.ATLAS)
    fig, ax = plt.subplots()
    h.plot1d(ax=ax, histtype="step", color="tab:blue")
    ax.set_ylabel("Electrons / bin")
    ax.set_title(r"Electrons with $p_T > 25$ GeV")
    ax.text(0.97, 0.95, "ATLAS Open Data\n" + r"$t\bar{t}$ all-hadronic"
            + f"\nFirst {event_count:,} events", transform=ax.transAxes,
            ha="right", va="top", fontsize=12)
    ax.set_ylim(bottom=0)
    fig.tight_layout()
    fig.savefig(Path("plot_1.png"), dpi=160)
    print(f"METRIC: avg_entries_per_event={avg_entries_per_event:.10g} mean={mean:.10g}",
          flush=True)
    plt.close(fig)


if __name__ == "__main__":
    app()
