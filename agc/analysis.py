# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.1
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # ATLAS Open Data $H\rightarrow ZZ^\star$ with `ServiceX`, `coffea`, `cabinetry` & `pyhf`

# %%
import re
import time

import awkward as ak
import cabinetry
import hist
import mplhep
import numpy as np
import pyhf
import uproot

from coffea import processor
from coffea.nanoevents.schemas.base import BaseSchema
import utils
from utils import infofile  # contains cross-section information

import servicex

import vector

vector.register_awkward()

utils.clean_up()  # delete output from previous runs of notebook (optional)
utils.set_logging()  # configure logging output

# %%
# set some global settings

# chunk size to use
CHUNKSIZE = 500_000

# scaling for local setups with FuturesExecutor
NUM_CORES = 4

# ServiceX behavior: ignore cache with repeated queries
IGNORE_CACHE = False

# ServiceX behavior: choose query language
USE_SERVICEX_UPROOT_RAW = True

# %% [markdown]
# ## Introduction
#
# We are going to use the ATLAS Open Data for this demonstration, in particular a $H\rightarrow ZZ^\star$ analysis. Find more information on the [ATLAS Open Data documentation](http://opendata.atlas.cern/release/2020/documentation/physics/FL2.html) and in [ATL-OREACH-PUB-2020-001](https://cds.cern.ch/record/2707171). The datasets used are [10.7483/OPENDATA.ATLAS.2Y1T.TLGL](http://doi.org/10.7483/OPENDATA.ATLAS.2Y1T.TLGL). The material in this notebook is based on the [ATLAS Open Data notebooks](https://github.com/atlas-outreach-data-tools/notebooks-collection-opendata), a [PyHEP 2021 ServiceX demo](https://github.com/gordonwatts/pyhep-2021-SX-OpenDataDemo), and [Storm Lin's adoption](https://github.com/stormsomething/CoffeaHZZAnalysis) of this analysis.
#
# This notebook is meant as a **technical demonstration**. In particular, the systematic uncertainties defined are purely to demonstrate technical aspects of realistic workflows, and are not meant to be meaningful physically. The fit performed to data consequently also only demonstrate technical aspects. If you are interested about the physics of $H\rightarrow ZZ^\star$, check out for example the actual ATLAS cross-section measurement: [Eur. Phys. J. C 80 (2020) 942](https://atlas.web.cern.ch/Atlas/GROUPS/PHYSICS/PAPERS/HIGG-2018-29/).
#
# This notebook implements most of the analysis pipeline shown in the following picture, using the tools also mentioned there:
# ![ecosystem visualization](utils/ecosystem.png)

# %% [markdown]
# ### Tools and packages used in this example
#
# The notebook showcases:
# - data delivery with `ServiceX`
# - event / column selection with `func_adl`
# - data handling with `awkward-array`
# - histogram production with `coffea`
# - histogram handling with `hist`
# - visualization with `mplhep`, `hist` & `matplotlib`
# - ROOT file handling with `uproot`
# - statistical model construction with `cabinetry`
# - statistical inference with `pyhf`

# %% [markdown]
# ### High-level strategy
#
# We will define which files to process, set up a query with `func_adl` to extract data provided by `ServiceX`, and use `coffea` to construct histograms.
# Those histograms will be saved with `uproot`, and then assembled into a statistical model with `cabinetry`.
# Following that, we perform statistical inference with `pyhf`.

# %% [markdown]
# ### Required setup for this notebook
#
# If you are running on the coffea-casa Open Data instance, ServiceX credentials are automatically available to you.
# Otherwise you will need to set those up.
# Create a file `servicex.yaml` in your home directory, or the place this notebook is located in.
#
# See this [talk by KyungEon](https://indico.cern.ch/event/1076231/contributions/4560404/) and the [ServiceX doc](https://servicex.readthedocs.io/en/latest/user/getting-started/) for more information.

# %% [markdown]
# ## Files to process
#
# To get started, we define which files are going to be processed in this notebook.
# We also set some information for histogramming that will be used subsequently.

# %%
prefix = "http://xrootd-local.unl.edu:1094//store/user/AGC/ATLAS_HZZ/"

# labels for combinations of datasets
z_ttbar = r"Background $Z,t\bar{t}$"
zzstar = r"Background $ZZ^{\star}$"
signal = r"Signal ($m_H$ = 125 GeV)"

input_files = {
    "Data": [
        prefix + "data_A.4lep.root",
        prefix + "data_B.4lep.root",
        prefix + "data_C.4lep.root",
        prefix + "data_D.4lep.root",
    ],
    z_ttbar: [
        prefix + "mc_361106.Zee.4lep.root",
        prefix + "mc_361107.Zmumu.4lep.root",
        prefix + "mc_410000.ttbar_lep.4lep.root",
    ],
    zzstar: [prefix + "mc_363490.llll.4lep.root"],
    signal: [
        prefix + "mc_345060.ggH125_ZZ4lep.4lep.root",
        prefix + "mc_344235.VBFH125_ZZ4lep.4lep.root",
        prefix + "mc_341964.WH125_ZZ4lep.4lep.root",
        prefix + "mc_341947.ZH125_ZZ4lep.4lep.root",
    ],
}

# information for histograms
bin_edge_low = 80  # 80 GeV
bin_edge_high = 250  # 250 GeV
num_bins = 34
