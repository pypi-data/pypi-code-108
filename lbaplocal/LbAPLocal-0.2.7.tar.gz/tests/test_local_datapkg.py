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


def test_list(data_pkg_repo):
    runner = CliRunner()
    result = runner.invoke(main, ["list"])
    assert result.exit_code == 0, result.stdout
    assert "cbtesting" in result.stdout
    assert "BsToJpsiPhi" in result.stdout
    assert "RDs" in result.stdout


@pytest.mark.parametrize(
    "prod_name,example,num_expected",
    [
        ("cbtesting", "MC_2016_MagDown_Lb2PsiL_mm_tuple", 168),
        ("BsToJpsiPhi", "MC_2018_MagUp_InclJpsi_sim09g_s34_dst", 16),
    ],
)
def test_list_with_production(data_pkg_repo, prod_name, example, num_expected):
    runner = CliRunner()
    result = runner.invoke(main, ["list", prod_name])
    assert result.exit_code == 0, result.stdout
    assert example in result.stdout
    assert result.stdout.count("\n*") == num_expected


@pytest.mark.parametrize("prod_name", ["cbtesting", "BsToJpsiPhi"])
def test_render(data_pkg_repo, prod_name):
    runner = CliRunner()
    result = runner.invoke(main, ["render", prod_name])
    assert result.exit_code == 0, result.stdout


@pytest.mark.parametrize("prod_name", ["RDs"])
def test_render_bad(data_pkg_repo, prod_name):
    runner = CliRunner()
    result = runner.invoke(main, ["render", prod_name])
    assert result.exit_code == 1
    assert "Rendered YAML has errors!" in result.stdout


@pytest.mark.parametrize("prod_name", ["cbtesting", "BsToJpsiPhi"])
def test_validate(data_pkg_repo, prod_name):
    runner = CliRunner()
    result = runner.invoke(main, ["validate", prod_name])
    assert result.exit_code == 0, result.stdout


@pytest.mark.parametrize("prod_name,expected_message", [("RDs", "output:")])
def test_validate_bad(data_pkg_repo, prod_name, expected_message):
    runner = CliRunner()
    result = runner.invoke(main, ["validate", prod_name])
    assert result.exit_code == 1
    assert "Error parsing YAML!" in result.stdout
