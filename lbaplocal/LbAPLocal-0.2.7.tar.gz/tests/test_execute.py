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
import subprocess
from io import BytesIO
from os.path import isfile, join

import pytest
from click.testing import CliRunner

from LbAPLocal.cli import main


@pytest.fixture
def with_mock_run_local(mocker):
    mocker.patch("LbAPLocal.cli.do_options_parsing", side_effect=lambda *a: [])

    mocker.patch(
        "LbAPCommon.cern_sso.get_with_cookies",
        side_effect=lambda x: {
            "dynamic_options": {
                "local_autoconf.py": (
                    "from Configurables import DaVinci\n"
                    "DaVinci().Turbo = False\n"
                    "\n"
                    "DaVinci().InputType = 'DST'\n"
                    "DaVinci().DataType = '2018'\n"
                    "DaVinci().Simulation = True\n"
                    "DaVinci().Lumi = False\n"
                    "DaVinci().DDDBtag = 'dddb-20170721-3'\n"
                    "DaVinci().CondDBtag = 'sim-20190430-vc-md100'"
                )
            },
            "env-command": [
                "lb-run",
                "--unset=LD_LIBRARY_PATH",
                "--unset=PYTHONPATH",
                "--unset=XrdSecPROTOCOL",
                "--siteroot=/cvmfs/lhcb.cern.ch/lib/",
                "--allow-containers",
                "--platform=best",
                "--use=AnalysisProductions.v999999999999",
                "--use=ProdConf",
                "Castelao/v3r1",
            ],
            "lfns": [
                "/lhcb/MC/2018/ALLSTREAMS.DST/00092443/0000/00092443_00007924_7.AllStreams.dst"
            ],
        },
    )

    yield


@pytest.mark.slow
def test_run_test_stripping(with_proxy, data_pkg_repo, with_data, with_mock_run_local):
    runner = CliRunner()
    result = runner.invoke(main, ["test", "cbtesting", "MC_2011_MagUp_Lb2Lee_strip"])
    assert result.exit_code == 0, result.stdout

    assert "Application Manager Finalized successfully" in result.stdout
    assert "Application Manager Terminated successfully" in result.stdout
    assert "208 events processed" in result.stdout
    assert "Summary of log messages" in result.stdout
    assert "General explanations" in result.stdout
    assert "Histograms are not being saved" in result.stdout

    assert "Output can be found in" in result.stdout
    output_dir = result.stdout.split("Output can be found in")[-1].strip()

    output_fn = join(output_dir, "00012345_00006789_1.AllStreams.RD_LBTOL0LL.DST")
    assert isfile(output_fn)
    assert 1024 ** 2 <= os.stat(output_fn).st_size <= 2 * 1024 ** 2

    stdout_fn = join(output_dir, "stdout.log")
    assert isfile(stdout_fn)
    with open(stdout_fn, "rt") as fp:
        stdout = fp.read()
    assert "Application Manager Finalized successfully" in stdout
    assert "Application Manager Terminated successfully" in stdout
    assert "208 events processed" in stdout

    stderr_fn = join(output_dir, "stderr.log")
    assert isfile(stderr_fn)


@pytest.fixture
def with_mock_reproduce(mocker, with_data):
    mocker.patch(
        "LbAPCommon.cern_sso.get_with_cookies",
        side_effect=lambda x: {
            "command": [
                "gaudirun.py",
                "-T",
                "$ANALYSIS_PRODUCTIONS_DYNAMIC/Lb2Lll/MC_2011_MagUp_Lb2Lee_strip_autoconf.py",
                "$ANALYSIS_PRODUCTIONS_BASE/Lb2Lll/stripping_seq.py",
                "$ANALYSIS_PRODUCTIONS_DYNAMIC/use-jsroot-compression.py",
                "prodConf_DaVinci_00012345_00006789_1.py",
            ],
            "download_files": {
                "pool_xml_catalog.xml": "https://s3.cern.ch/pool_xml_catalog.xml",
                "prodConf_DaVinci_00012345_00006789_1.py": "https://s3.cern.ch/prodConf_DaVinci_00012345_00006789_1.py",
            },
            "dynamic_options": {
                "Lb2Lll/MC_2011_MagUp_Lb2Lee_strip_autoconf.py": (
                    "from Configurables import DaVinci\n"
                    "\n"
                    "DaVinci().InputType = 'DST'\n"
                    "DaVinci().DataType = '2011'\n"
                    "DaVinci().Simulation = True\n"
                    "DaVinci().Lumi = False\n"
                    "DaVinci().DDDBtag = 'dddb-20170721-1'\n"
                    "DaVinci().CondDBtag = 'sim-20160614-1-vc-mu100'"
                )
            },
            "env-command": [
                "lb-run",
                "--unset",
                "LD_LIBRARY_PATH",
                "--unset",
                "PYTHONPATH",
                "--unset",
                "XrdSecPROTOCOL",
                "--siteroot=/cvmfs/lhcb.cern.ch/lib/",
                "--allow-containers",
                "-c",
                "best",
                "--use=AnalysisProductions v999999999999",
                "--use=ProdConf",
                "DaVinci/v39r1p6",
            ],
            "git_repo": "https://gitlab.cern.ch/lhcb-datapkg/AnalysisProductions",
            "revision": "8c5629839ea1fc3a3688939a70e873b4f1f2a1ad",
        },
    )

    from requests import Response
    from requests import get as original_get

    prod_conf_data = (
        "from ProdConf import ProdConf\n"
        "\n"
        "ProdConf(\n"
        "    NOfEvents=-1,\n"
        "    AppVersion='v39r1p6',\n"
        "    OptionFormat='WGProd',\n"
        "    XMLSummaryFile='summaryDaVinci_00012345_00006789_1.xml',\n"
        "    Application='DaVinci',\n"
        "    OutputFilePrefix='00012345_00006789_1',\n"
        "    XMLFileCatalog='pool_xml_catalog.xml',\n"
        "    InputFiles=['LFN:/lhcb/MC/2011/ALLSTREAMS.DST/00102891/0000/00102891_00000027_5.AllStreams.dst'],\n"
        "    OutputFileTypes=['allstreams.rd_lbtol0ll.dst'],\n"
        ")\n"
    )

    def my_requests_get(url, *args, **kwargs):
        response = Response()
        response.status_code = 200
        if url == "https://s3.cern.ch/pool_xml_catalog.xml":
            response.raw = BytesIO(with_data.encode())
            response._content = with_data.encode()
        elif url == "https://s3.cern.ch/prodConf_DaVinci_00012345_00006789_1.py":
            response.raw = BytesIO(prod_conf_data.encode())
        else:
            response = original_get(url, *args, **kwargs)
        return response

    mocker.patch("requests.get", side_effect=my_requests_get)

    # responses.add(
    #     responses.GET, "https://s3.cern.ch/pool_xml_catalog.xml", body=with_data
    # )

    # responses.add(
    #     responses.GET,
    #     "https://s3.cern.ch/prodConf_DaVinci_00012345_00006789_1.py",
    #     body=(
    #         "from ProdConf import ProdConf\n"
    #         "\n"
    #         "ProdConf(\n"
    #         "    NOfEvents=-1,\n"
    #         "    AppVersion='v39r1p6',\n"
    #         "    OptionFormat='WGProd',\n"
    #         "    XMLSummaryFile='summaryDaVinci_00012345_00006789_1.xml',\n"
    #         "    Application='DaVinci',\n"
    #         "    OutputFilePrefix='00012345_00006789_1',\n"
    #         "    XMLFileCatalog='pool_xml_catalog.xml',\n"
    #         "    InputFiles=['LFN:/lhcb/MC/2011/ALLSTREAMS.DST/00102891/0000/00102891_00000027_5.AllStreams.dst'],\n"
    #         "    OutputFileTypes=['allstreams.rd_lbtol0ll.dst'],\n"
    #         ")\n"
    #     ),
    # )

    yield


@pytest.mark.slow
def test_reproduce(with_proxy, with_data, mocker, with_mock_reproduce):
    from LbAPLocal.testing import prepare_reproduce

    prepare_reproduce("1920001", "Lb2Lll", "MC_2011_MagUp_Lb2Lee_strip", "0")

    execlp_mock = mocker.patch("os.execlp", side_effect=None)

    runner = CliRunner()
    result = runner.invoke(
        main, ["reproduce", "1920001", "Lb2Lll", "MC_2011_MagUp_Lb2Lee_strip", "0"]
    )
    assert result.exit_code == 0, result.stdout
    assert "Cloning " in result.stdout
    assert "Downloading pool_xml_catalog.xml" in result.stdout
    assert "Downloading prodConf_DaVinci_00012345_00006789_1.py" in result.stdout
    assert "Starting lb-run with: lb-run" in result.stdout

    assert execlp_mock.call_count == 1
    cmd, *execlp_args = execlp_mock.call_args[0]
    assert cmd == execlp_args[0]
    assert "--use=ProdConf" in execlp_args
    assert "DaVinci/v39r1p6" in execlp_args

    assert isfile(execlp_args[execlp_args.index("--rcfile") + 1])
    with subprocess.Popen(
        execlp_args + ["-i"],
        stdout=subprocess.PIPE,
        stdin=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ) as p:
        stdout_data, stderr_data = p.communicate(input=b"which gaudirun.py")
    stdout_data = list(filter(None, stdout_data.decode().strip().split("\n")))
    assert "Welcome to analysis productions debug mode:" in stdout_data
    assert (
        stdout_data[-1]
        == "/cvmfs/lhcb.cern.ch/lib/lhcb/GAUDI/GAUDI_v27r0/InstallArea/x86_64-slc6-gcc49-opt/scripts/gaudirun.py"
    )
    assert not isfile(execlp_args[execlp_args.index("--rcfile") + 1])

    gaudirun_cmd = stdout_data[-2]
    assert gaudirun_cmd.startswith("gaudirun.py ")
