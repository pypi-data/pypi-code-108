# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.13.1
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %%
# %load_ext autoreload
# %autoreload 2

# %% [markdown]
# # Make a new data release of the current version of the NENA data
#
# The NENA data should reside locally on your system.
#
# By default, we assume it is under `~/github` and then under *org/repo/folder/version*
# where
#
# * *org* = `CambridgeSemiticsLab`
# * *repo* = `nena_tf`
# * *folder* = `tf`
# * *version* = `alpha`
#
# You pass *org*, *repo*, *folder*, *version* as parameters.
# You can replace the `~/github` by passing a `source` parameter.
#
# The data will be zipped into a file that will be attached to a new release on GitHub.
# This zipfile is created by default in `~/Downloads`, but you can override this by passing a `dest` parameter.
#
# We assume the tf data resides under `~/local/data` and we use `~/local/zips` as landing directory for the zip file. 

# %% [markdown]
# Note the parameter `3` after `VERSION` in the call of `releaseData()` below.
# This indicates which part of the version number should be increased by one.
# The parts behind it will be deleted.
#
# Examples:
#
# old version | method | new version
# --- | --- | ---
# v2.4.6 | 3 | v2.4.7
# v2.4.6 | 2 | v2.5
# v2.4.6 | 1 | v3
# v2.4 | 3 | v2.4.1
# v2 | 3 | v2.0.1
# v2 | 2 | v2.1

# %%
from tf.advanced.repo import releaseData

ORG = "CambridgeSemiticsLab"
REPO = "nena_tf"
FOLDER = "tf"
VERSION = "alpha"
DATA_IN = "~/local/data"
DATA_ZIP = "~/local/zips"

releaseData(ORG, REPO, FOLDER, VERSION, 3, source=DATA_IN, dest=DATA_ZIP)

# %% [markdown]
# # Make all search clients for the CambridgeSemiticsLab/nena dataset
#
# Suppose a new release has been made of the NENA corpus data.
# Now we want to regenerate its client search apps.
#
# We assume the config data for the apps is in a local directory on the system.
#
# CONFIG_DIR should have the same structure as
# [layeredsearch](https://github.com/annotation/app-nena/tree/master/layeredsearch).
# You can tweak it, but it should play nice with the client generation process.
#
# We generate the client search data in a local directory on the system.

# %%
import os
from tf.client.make.build import makeSearchClients

APP_DIR = os.path.expanduser("~/local/app-nena")
OUTPUT_DIR = os.path.expanduser("~/local/lsOut")
DATASET = "nena"

# %%
makeSearchClients(DATASET, OUTPUT_DIR, APP_DIR, dataDir="~/local/tfNew")

# %% [markdown]
# # Ship all apps for all corpora
#
# From now on we work in a setting where we ship client apps to GitHub pages of the `app-`*dataset* repo.

# %%
import collections
import os

from tf.client.make.build import Make

# %%
APPS = (
    ("bhsa", "structure"),
    ("missieven", "text"),
    ("nena", "phono"),
    ("nena", "fuzzy"),
)

# %%
APPS_BY_DATASET = (
    ("nena", ("fuzzy", "phono")),
    ("bhsa", ("structure",)),
    ("missieven", ("text",)),
)

# %%
for (dataset, apps) in APPS_BY_DATASET:
    nApps = len(apps)
    for app in apps:
        Mk = Make(dataset, app, debugState="off")
        Mk.ship(publish=nApps == 1)
    if nApps > 1:
        Mk = Make(dataset, None, debugState="off")
        Mk.publish()

# %% [markdown]
# # Individual apps in debug mode

# %%
Mk = Make(*APPS[1], debugState="on")

# %% [markdown]
# # Load data
#
# The Text-Fabric dataset is loaded.

# %%
Mk.loadTf()

# %%
A = Mk.A
api = A.api
Fs = api.Fs
F = api.F
L = api.L
T = api.T

# %%
T.sectionTypes

# %% [markdown]
# # Configure
#
# If you changed critical files in the layered search app (`mkdata.py` or `config.yaml`),
# run this command to update the configuration inside the maker.

# %% tags=[]
# do this if you have changed mkdata.py or config.yaml

Mk.config()

# %% [markdown]
# # Settings
#
# Generate the settings for the client app, but do not dump them yet to file.
# Also the legends are generated here, which might use the loaded data.

# %%
Mk.makeClientSettings()

# %% [markdown]
# # Links
#
# Generate links from section nodes to online locations of those sections.
#
# This is done by simply calling the Text-Fabric API.

# %%
Mk.makeLinks()

# %% [markdown]
# # Record
#
# Here we call the app-dependent function `record()`, 
# which records the corpus data in `recorders` and `accumulators`.
#
# Some layers can use the position data of other layers, and these layers are stored in accumulators.
#
# Layers with their own position data are stored in recorders, they remember the node positions within
# the stored material. This is a Text-Fabric device, see [Recorder](https://annotation.github.io/text-fabric/tf/convert/recorder.html).

# %%
Mk.config()
Mk.record()

# %% [markdown]
# # Dump data
#
# The corpus texts and positions are derived from the recorders and accumulators, and written to file.

# %%
Mk.config()
Mk.dumpCorpus()

# %% [markdown]
# # Dump config
#
# The client settings, generated in an earlier step, are dumped to file, next to the corpus data.

# %%
Mk.dumpConfig()

# %% [markdown]
# # Make
#
# The client app is composed as an HTML page with CSS styles and a Javascript program,
# and it is moved to the `site` directory of the repo.
#
# We also set the debug flag reflecting how we initialized the maker: debug is on.

# %%
Mk.makeClient()
Mk.adjustDebug()

# %%
