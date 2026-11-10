#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.13"
# dependencies = [
#   "awkward>=2.6",
#   "func_adl_servicex_xaodr25",
#   "matplotlib>=3.8",
#   "servicex>=3.0",
#   "servicex-analysis-utils",
#   "typer>=0.12",
#   "jinja2",
# ]
# ///
"""Plot electron transverse momentum from the requested OpenData PHYSLITE file."""

import math
from pathlib import Path

import awkward as ak
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import typer
from func_adl_servicex_xaodr25 import FuncADLQueryPHYSLITE
from servicex import Sample, ServiceXSpec, dataset, deliver
from servicex_analysis_utils import to_awk


app = typer.Typer(add_completion=False)

# Requested dataset: opendata:mc20_13TeV.410471.PhPy8EG_A14_ttbar_hdamp258p75_allhad.deriv.DAOD_PHYSLITE.e6337_s3681_r13167_p6026
# Requested file GUID: 8B18F7A0FD496E40925B81A133BCF8DD
FILE_DID = "mc20_13TeV:DAOD_PHYSLITE.37861619._000001.pool.root.1"
SAMPLE_NAME = "electron_pt"


def make_query():
    """Return electron pT values; event slicing is applied locally to preserve order."""
    base_query = FuncADLQueryPHYSLITE()
    return (
        base_query
        .Select(
            lambda event: {
                "electron_pt": event.Electrons()
                .Select(lambda electron: electron.pt() / 1000.0)
            }
        )
    )


@app.command()
def main(
    max_events: int = typer.Option(20_000, "--max-events", min=1),
    output_dir: Path = typer.Option(Path("."), "--output-dir"),
) -> None:
    """Fetch one PHYSLITE file and plot electron pT above 25 GeV."""
    if max_events < 1:
        raise typer.BadParameter("must be at least 1", param_hint="--max-events")

    query = make_query()
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

    event_data = to_awk(delivered)[SAMPLE_NAME][:max_events]
    electron_pts = event_data["electron_pt"]
    selected_pt = electron_pts[electron_pts > 25.0]
    selected_event_count = int(ak.sum(ak.num(selected_pt, axis=1) > 0))
    raw_pts = ak.to_list(ak.flatten(selected_pt, axis=None))
    raw_pts = [float(value) for value in raw_pts]
    if selected_event_count == 0 or not raw_pts:
        raise RuntimeError(
            f"No selected electrons found in the first {max_events} events of {FILE_DID}"
        )

    output_dir.mkdir(parents=True, exist_ok=True)
    plot_path = output_dir / "plot_1.png"
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.hist(raw_pts, bins=50, range=(25, max(100, math.ceil(max(raw_pts)))),
            histtype="stepfilled", color="steelblue", alpha=0.8)
    ax.set_xlabel(r"Electron transverse momentum $p_T$ [GeV]")
    ax.set_ylabel("Electrons")
    ax.set_title("Electrons with $p_T > 25$ GeV")
    fig.tight_layout()
    fig.savefig(plot_path, dpi=150)
    plt.close(fig)

    mean_pt = math.fsum(raw_pts) / len(raw_pts)
    avg_entries_per_event = len(raw_pts) / selected_event_count
    print(
        f"METRIC: avg_entries_per_event={avg_entries_per_event:.12g} "
        f"mean={mean_pt:.12g}",
        flush=True,
    )


if __name__ == "__main__":
    app()
