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
import shutil
import subprocess
from os.path import dirname, join

import pytest
import requests

EXAMPLE_REPO_ROOT = join(dirname(__file__), "data", "data-pkg-repo")


def pytest_addoption(parser):
    parser.addoption(
        "--runslow", action="store_true", default=False, help="run slow tests"
    )


def pytest_configure(config):
    config.addinivalue_line("markers", "slow: mark test as slow to run")


def pytest_collection_modifyitems(config, items):
    if config.getoption("--runslow"):
        # --runslow given in cli: do not skip slow tests
        return
    skip_slow = pytest.mark.skip(reason="need --runslow option to run")
    for item in items:
        if "slow" in item.keywords:
            item.add_marker(skip_slow)


@pytest.fixture
def empty_data_pkg_repo(tmpdir):
    cwd = os.getcwd()
    os.chdir(tmpdir)
    yield tmpdir
    os.chdir(cwd)


@pytest.fixture
def data_pkg_repo(empty_data_pkg_repo):
    shutil.copytree(EXAMPLE_REPO_ROOT, empty_data_pkg_repo, dirs_exist_ok=True)
    yield empty_data_pkg_repo


@pytest.fixture
def with_proxy(mocker):
    from subprocess import check_call as original_check_call

    def my_check_call(args, *more_args, **kwargs):
        if args == ["lb-dirac", "dirac-proxy-info", "--checkvalid"]:
            return
        else:
            return original_check_call(args, *more_args, **kwargs)

    mocker.patch("subprocess.check_call", new=my_check_call)


@pytest.fixture
def without_proxy(mocker):
    mocker.patch(
        "subprocess.check_call", side_effect=subprocess.CalledProcessError(1, "mocked")
    )


@pytest.fixture
def with_data(mocker):
    from subprocess import run as original_run

    data_url = "http://s3.cern.ch/lhcb-analysis-productions-dev/test-data/00092443_00007924_7.AllStreams.dst"
    data_fn = join(dirname(__file__), "data", "00092443_00007924_7.AllStreams.dst")
    if not os.path.isfile(data_fn):
        with requests.get(data_url, stream=True) as r:
            with open(data_fn, "wb") as f:
                shutil.copyfileobj(r.raw, f)

    pool_catalog_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="no" ?>\n'
        "<!-- Edited By PoolXMLCatalog.py -->\n"
        '<!DOCTYPE POOLFILECATALOG SYSTEM "InMemory">\n'
        "<POOLFILECATALOG>\n"
        '<File ID="6C5459F5-00AF-E911-9E41-0CC47A202CB8">\n'
        "<physical>\n"
        f'    <pfn filetype="ROOT_All" name="{data_fn}" se="CI-DST"/>\n'
        "</physical>\n"
        "<logical>\n"
        '    <lfn name="/lhcb/MC/2018/ALLSTREAMS.DST/00092443/0000/00092443_00007924_7.AllStreams.dst"/>\n'
        "</logical>\n"
        "</File>\n"
        "</POOLFILECATALOG>\n"
    )

    def my_run(args, *more_args, **kwargs):
        if args[:2] == ["lb-dirac", "dirac-bookkeeping-genXMLCatalog"]:
            with open(join(kwargs["cwd"], "pool_xml_catalog.xml"), "wt") as fp:
                fp.write(pool_catalog_xml)
            return subprocess.CompletedProcess([], 0, "")
        else:
            return original_run(args, *more_args, **kwargs)

    mocker.patch("subprocess.run", new=my_run)

    yield pool_catalog_xml
