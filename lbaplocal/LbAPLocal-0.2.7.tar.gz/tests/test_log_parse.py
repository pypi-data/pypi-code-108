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
from glob import glob
from os.path import basename, dirname, join

import pytest
from click.testing import CliRunner

from LbAPLocal.cli import main

log_paths = glob(join(dirname(__file__), "data", "example-logs", "*.log"))
assert len(log_paths) > 5


@pytest.mark.parametrize("log_path", log_paths)
def test_parse_logs(log_path):
    runner = CliRunner()
    result = runner.invoke(main, ["parse-log", log_path])

    if basename(log_path).startswith("good-"):
        assert result.exit_code == 0, result.stdout
    elif basename(log_path).startswith("error-"):
        assert result.exit_code == 1, result.stdout
    else:
        raise NotImplementedError(log_path)
