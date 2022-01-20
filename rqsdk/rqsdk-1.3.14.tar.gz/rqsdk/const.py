# -*- coding: utf-8 -*-
#
# Copyright 2016 Ricequant, Inc
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import json
import os

RQDATAC_DEFAULT_ADDRESS = "rqdatad-pro.ricequant.com:16011"
PERMISSIONS_INFO_URL = "https://www.ricequant.com/api/rqlicense/get_permissions_readable_info"
EXTRA_INDEX_URL = "https://rquser:Ricequant8@pypi2.ricequant.com/simple/"
BASH_FILE = [".bash_profile", ".bashrc", ".bash_profile", ".zshrc"]
TAG_MAP = ["stock", "futures", "fund", "index", "option", "convertible", ]
DEFAULT_BUNDLE_PATH = os.path.join(os.path.expanduser('~'), ".rqalpha-plus")

PRODUCTS = ["rqalpha_plus", "rqdatac", "rqfactor", "rqoptimizer"]
CONCERNED_PACKAGES = [
    "rqsdk", "rqdatac", "rqdatac_fund",
    "rqfactor", "rqoptimizer", "rqrisk",
    "rqalpha_plus", "rqalpha", "rqalpha_mod_spot", "rqalpha_mod_option", "rqalpha_mod_optimizer2",
    "rqalpha_mod_convertible", "rqalpha_mod_ricequant_data", "rqalpha_mod_rqfactor", "rqalpha_mod_fund",
    "rqalpha_mod_spot",
    "pandas", "numpy", "h5py"
]

