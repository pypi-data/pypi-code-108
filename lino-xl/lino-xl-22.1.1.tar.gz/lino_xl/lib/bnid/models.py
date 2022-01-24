# Copyright 2010-2019 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)


# This module is here e.g. for `lino.projects.docs` which installs the
# app but no BnIdCardHolder model.

from .choicelists import BnIdCardTypes, ResidenceTypes
from .mixins import BnIdCardHolder
