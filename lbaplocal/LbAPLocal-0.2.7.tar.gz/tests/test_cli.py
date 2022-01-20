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
import pytest
from click.testing import CliRunner

from LbAPLocal.cli import main

args_list = ["list"]
args_render = ["render", "cbtesting"]
args_test = ["test", "cbtesting", "MC_2011_MagUp_Lb2Lee_strip"]
args_debug = ["debug", "cbtesting", "MC_2011_MagUp_Lb2Lee_strip"]
args_reproduce = ["reproduce"]
args_parse_log = ["parse-log"]


@pytest.mark.parametrize(
    "subcommand",
    [args_list, args_render, args_test, args_debug, args_reproduce, args_parse_log],
)
def test_main_help(subcommand):
    runner = CliRunner()
    result = runner.invoke(main, subcommand + ["--help"])
    assert result.exit_code == 0, result.stdout


def test_main_version():
    runner = CliRunner()
    result = runner.invoke(main, ["--version"])
    assert result.exit_code == 0, result.stdout
    assert "LbAPLocal" in result.stdout
    assert "LbAPCommon" in result.stdout
    assert "LbEnv" in result.stdout
    assert "LbDiracWrappers" in result.stdout


@pytest.mark.parametrize("subcommand", [args_test, args_debug])
def test_not_in_datapkg(subcommand, empty_data_pkg_repo, with_proxy):
    runner = CliRunner()
    result = runner.invoke(main, subcommand)
    assert result.exit_code == 1
    assert "Running command in wrong directory" in result.stdout


@pytest.mark.parametrize(
    "subcommand",
    [
        args_test,
        args_debug,
    ],
)
def test_no_proxy(subcommand, data_pkg_repo, without_proxy):
    runner = CliRunner()
    result = runner.invoke(main, subcommand)
    assert result.exit_code == 1
    assert "No grid proxy found" in result.stdout
    assert "lhcb-proxy-init" in result.stdout
