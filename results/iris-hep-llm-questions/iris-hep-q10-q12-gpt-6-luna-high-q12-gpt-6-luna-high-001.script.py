#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.13"
# dependencies = [
#   "typer>=0.12",
#   "servicex>=3.0",
#   "func_adl_servicex_xaodr25",
#   "jinja2",
#   "servicex_analysis_utils",
#   "awkward>=2",
#   "vector>=1",
#   "numpy",
#   "matplotlib",
# ]
# ///
"""Plot same-charge muon-pair invariant masses from an ATLAS OpenData sample."""

from pathlib import Path

import awkward as ak
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
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


def make_query():
    """Return muon kinematics for all events containing at least two muons."""
    return (
        FuncADLQueryPHYSLITE()
        .Select(lambda event: {"muons": event.Muons()})
        .Where(lambda collections: collections.muons.Count() >= 2)
        .Select(
            lambda collections: {
                "mu_pt": collections.muons.Select(lambda muon: muon.pt() / 1000.0),
                "mu_eta": collections.muons.Select(lambda muon: muon.eta()),
                "mu_phi": collections.muons.Select(lambda muon: muon.phi()),
                "mu_mass": collections.muons.Select(lambda muon: muon.m() / 1000.0),
                "mu_charge": collections.muons.Select(lambda muon: muon.charge()),
            }
        )
    )


def pair_masses(muons: ak.Array) -> ak.Array:
    """Build every unique pair, retaining pairs whose muons have equal charge."""
    vector.register_awkward()
    p4 = ak.zip(
        {
            "pt": muons.mu_pt,
            "eta": muons.mu_eta,
            "phi": muons.mu_phi,
            "mass": muons.mu_mass,
            "charge": muons.mu_charge,
        },
        with_name="Momentum4D",
    )
    first, second = ak.unzip(ak.combinations(p4, 2, fields=("first", "second")))
    same_charge = first.charge * second.charge > 0
    return (first[same_charge] + second[same_charge]).mass


@app.command()
def main(
    n_files: int = typer.Option(1, "--n-files", min=1, help="Number of input files to process."),
) -> None:
    """Fetch one or more dataset files and plot same-charge dimuon masses."""
    query = make_query()
    delivered = deliver(
        ServiceXSpec(
            Sample=[
                Sample(
                    Name="same_charge_muons",
                    Dataset=dataset.Rucio(DATASET),
                    NFiles=n_files,
                    Query=query,
                )
            ]
        )
    )
    events = to_awk(delivered)["same_charge_muons"]
    eligible_event_count = len(events)
    masses_per_event = pair_masses(events)
    raw_masses = np.asarray(ak.to_numpy(ak.flatten(masses_per_event, axis=None)), dtype=float)

    mean = float(np.mean(raw_masses)) if raw_masses.size else float("nan")
    avg_entries_per_event = (
        float(raw_masses.size / eligible_event_count) if eligible_event_count else float("nan")
    )

    fig, ax = plt.subplots()
    ax.hist(raw_masses, bins=60, histtype="step", linewidth=1.5)
    ax.set_xlabel(r"Same-charge dimuon invariant mass [GeV]")
    ax.set_ylabel("Unweighted pairs")
    ax.set_title("ATLAS OpenData MC20: same-charge muon pairs")
    fig.tight_layout()
    fig.savefig(Path("plot_0.png"))
    plt.close(fig)

    print(f"METRIC: avg_entries_per_event={avg_entries_per_event} mean={mean}", flush=True)


if __name__ == "__main__":
    app()
