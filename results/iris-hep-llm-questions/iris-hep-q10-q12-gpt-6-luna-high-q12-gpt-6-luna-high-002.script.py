#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.13"
# dependencies = [
#   "awkward>=2.6",
#   "func_adl_servicex_xaodr25",
#   "hist>=2.7",
#   "jinja2",
#   "matplotlib>=3.8",
#   "mplhep>=0.3",
#   "numpy>=1.26",
#   "servicex>=3.0",
#   "servicex-analysis-utils",
#   "typer>=0.12",
#   "vector>=1.4",
# ]
# ///
"""Plot same-charge muon-pair invariant masses from one OpenData file."""

from pathlib import Path

import awkward as ak
import hist
import matplotlib.pyplot as plt
import mplhep as hep
import numpy as np
import typer
import vector
from func_adl_servicex_xaodr25 import FuncADLQueryPHYSLITE
from servicex import Sample, ServiceXSpec, dataset, deliver
from servicex_analysis_utils import to_awk

app = typer.Typer(add_completion=False)

DATASET = (
    "opendata:mc20_13TeV.700325.Sh_2211_Zmumu_maxHTpTV2_CVetoBVeto."
    "deriv.DAOD_PHYSLITE.e8351_s3681_r13167_p6026"
)


def build_query():
    """Fetch four-momenta and charges for events with at least two muons."""
    return (
        FuncADLQueryPHYSLITE()
        .Where(lambda event: event.Muons().Count() >= 2)
        .Select(
            lambda event: {
                "mu_pt": event.Muons().Select(lambda muon: muon.pt() / 1000.0),
                "mu_eta": event.Muons().Select(lambda muon: muon.eta()),
                "mu_phi": event.Muons().Select(lambda muon: muon.phi()),
                "mu_charge": event.Muons().Select(lambda muon: muon.charge()),
            }
        )
    )


@app.command()
def main(output_dir: Path = typer.Option(Path("."), help="Directory for plot_0.png.")) -> None:
    """Fetch one dataset file and plot every unique same-charge muon pair."""
    vector.register_awkward()
    query = build_query()
    delivered = deliver(
        ServiceXSpec(
            Sample=[
                Sample(
                    Name="same_charge_muons",
                    Dataset=dataset.Rucio(DATASET),
                    NFiles=1,
                    Query=query,
                )
            ]
        )
    )
    events = to_awk(delivered)["same_charge_muons"]
    muons = ak.zip(
        {
            "pt": events["mu_pt"],
            "eta": events["mu_eta"],
            "phi": events["mu_phi"],
            "mass": ak.ones_like(events["mu_pt"]) * 0.105658,
            "charge": events["mu_charge"],
        },
        with_name="Momentum4D",
    )

    # The ServiceX event filter defines the denominator: all events with >=2 muons,
    # including events that have no same-charge pair.
    n_events = len(muons)
    first, second = ak.unzip(ak.combinations(muons, 2, fields=["first", "second"]))
    same_charge = first.charge == second.charge
    pair_mass = (first[same_charge] + second[same_charge]).mass
    raw_masses = ak.to_numpy(ak.flatten(pair_mass, axis=None))

    output_dir.mkdir(parents=True, exist_ok=True)
    plot_path = output_dir / "plot_0.png"
    mass_hist = hist.Hist.new.Reg(100, 0, 200, name="mass", label="Invariant mass [GeV]").Int64()
    mass_hist.fill(mass=raw_masses)

    with plt.style.context(hep.style.ATLAS):
        fig, ax = plt.subplots()
        mass_hist.plot(ax=ax, histtype="step", linewidth=1.5)
        ax.set_title("Same-charge muon pairs")
        ax.set_ylabel("Pairs")
        fig.savefig(plot_path, dpi=150, bbox_inches="tight")
        plt.close(fig)

    mean = float(np.mean(raw_masses)) if raw_masses.size else float("nan")
    avg_entries = raw_masses.size / n_events if n_events else float("nan")
    print(f"METRIC: avg_entries_per_event={avg_entries} mean={mean}")


if __name__ == "__main__":
    app()
