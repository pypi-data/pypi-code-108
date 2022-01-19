###############################################################################
# (c) Copyright 2020 CERN for the benefit of the LHCb Collaboration           #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################

import os
import re
from os.path import dirname, join


def project_uses_cmt(app_name, app_version):
    """Determine if a application needs the CMT fallback to be applied

    This does not aim to be comprehensive.
    """
    if app_name.lower() != "davinci":
        return False
    match = re.match(r"^v(\d+)(?:r(\d+))?(?:p(\d+))?$", app_version)
    if not match:
        print("WARNING: Failed to parse version string", app_version)
        return False
    parsed = tuple(map(lambda x: int(x) if x else 0, match.groups()))
    return parsed < (36, 4, 1)


def setup_lbrun_environment(siteroot, repository_dir, setup_cmt):
    """Set up the fake siteroot for lb-run to use when testing"""
    os.environ["CMAKE_PREFIX_PATH"] = siteroot
    fake_dbase = join(siteroot, "DBASE")
    fake_install_dir = join(fake_dbase, "AnalysisProductions", "v999999999999")
    os.makedirs(dirname(fake_install_dir))
    os.symlink(repository_dir, fake_install_dir)
    if setup_cmt:
        print("Applying fallback hacks for CMT style projects")
        os.environ["User_release_area"] = siteroot
        LHCB_DBASE_ROOT = "/cvmfs/lhcb.cern.ch/lib/lhcb/DBASE"
        for dname in os.listdir(LHCB_DBASE_ROOT):
            if dname == "AnalysisProductions":
                continue
            os.symlink(join(LHCB_DBASE_ROOT, dname), join(fake_dbase, dname))
