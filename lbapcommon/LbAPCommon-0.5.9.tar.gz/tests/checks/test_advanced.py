###############################################################################
# (c) Copyright 2021 CERN for the benefit of the LHCb Collaboration           #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
from textwrap import dedent

import pytest

import LbAPCommon
from LbAPCommon import checks
from LbAPCommon.checks_utils import checks_to_JSON

pytest.importorskip("XRootD")


def test_num_entries_parsing_to_JSON():
    rendered_yaml = dedent(
        """\
    checks:
        check_num_entries:
            type: num_entries
            count: 1000
            tree_pattern: DecayTree

    job_1:
        application: DaVinci/v45r8
        input:
            bk_query: /bookkeeping/path/ALLSTREAMS.DST
        output: FILETYPE.ROOT
        options:
            - options.py
            - $VAR/a.py
        wg: Charm
        inform: a.b@c.d
        checks:
            - check_num_entries
    """
    )
    jobs_data, checks_data = LbAPCommon.parse_yaml(rendered_yaml)

    job_name = list(jobs_data.keys())[0]
    check_name = list(checks_data.keys())[0]

    result = checks.run_job_checks(
        [check_name],
        checks_data,
        [
            "root://eospublic.cern.ch//eos/opendata/lhcb/AntimatterMatters2017/data/B2HHH_MagnetDown.root"
        ],
    )[check_name]

    check_results_with_job = {
        job_name: {
            check_name: result,
        }
    }

    checks_json = checks_to_JSON(checks_data, check_results_with_job)

    json_expected = dedent(
        """\
    {
      "job_1": {
        "check_num_entries": {
          "passed": true,
          "messages": [
            "Found 5135823 in DecayTree (1000 required)"
          ],
          "input": {
            "type": "num_entries",
            "count": 1000,
            "tree_pattern": "DecayTree"
          },
          "output": {
            "DecayTree": {
              "num_entries": 5135823
            }
          }
        }
      }
    }"""
    )

    assert checks_json == json_expected


def test_range_parsing_to_JSON():
    rendered_yaml = dedent(
        """\
    checks:
        check_range:
            type: range
            expression: H1_PZ
            limits:
                min: 0
                max: 500000
            blind_ranges:
                -
                    min: 80000
                    max: 100000
                -
                    min: 180000
                    max: 200000
            tree_pattern: DecayTree

    job_1:
        application: DaVinci/v45r8
        input:
            bk_query: /bookkeeping/path/ALLSTREAMS.DST
        output: FILETYPE.ROOT
        options:
            - options.py
            - $VAR/a.py
        wg: Charm
        inform: a.b@c.d
        checks:
            - check_range
    """
    )
    jobs_data, checks_data = LbAPCommon.parse_yaml(rendered_yaml)

    job_name = list(jobs_data.keys())[0]
    check_name = list(checks_data.keys())[0]

    result = checks.run_job_checks(
        [check_name],
        checks_data,
        [
            "root://eospublic.cern.ch//eos/opendata/lhcb/AntimatterMatters2017/data/B2HHH_MagnetDown.root"
        ],
    )[check_name]

    check_results_with_job = {
        job_name: {
            check_name: result,
        }
    }

    checks_json = checks_to_JSON(checks_data, check_results_with_job)

    json_expected = dedent(
        """\
    {
      "job_1": {
        "check_range": {
          "passed": true,
          "messages": [
            "Histogram of H1_PZ successfully filled from TTree DecayTree (contains 4776546.0 events)"
          ],
          "input": {
            "type": "range",
            "expression": "H1_PZ",
            "limits": {
              "min": 0.0,
              "max": 500000.0
            },
            "blind_ranges": [
              {
                "min": 80000.0,
                "max": 100000.0
              },
              {
                "min": 180000.0,
                "max": 200000.0
              }
            ],
            "tree_pattern": "DecayTree"
          },
          "output": {
            "DecayTree": {
              "histograms": [
                {
                  "_typename": "TH1D",
                  "fUniqueID": 0,
                  "fBits": 0,
                  "fName": null,
                  "fTitle": "",
                  "fLineColor": 602,
                  "fLineStyle": 1,
                  "fLineWidth": 1,
                  "fFillColor": 0,
                  "fFillStyle": 1001,
                  "fMarkerColor": 1,
                  "fMarkerStyle": 1,
                  "fMarkerSize": 1.0,
                  "fNcells": 52,
                  "fXaxis": {
                    "_typename": "TAxis",
                    "fUniqueID": 0,
                    "fBits": 0,
                    "fName": "H1_PZ",
                    "fTitle": "H1_PZ",
                    "fNdivisions": 510,
                    "fAxisColor": 1,
                    "fLabelColor": 1,
                    "fLabelFont": 42,
                    "fLabelOffset": 0.005,
                    "fLabelSize": 0.035,
                    "fTickLength": 0.03,
                    "fTitleOffset": 1.0,
                    "fTitleSize": 0.035,
                    "fTitleColor": 1,
                    "fTitleFont": 42,
                    "fNbins": 50,
                    "fXmin": 0.0,
                    "fXmax": 500000.0,
                    "fXbins": [],
                    "fFirst": 0,
                    "fLast": 0,
                    "fBits2": 0,
                    "fTimeDisplay": false,
                    "fTimeFormat": "",
                    "fLabels": null,
                    "fModLabs": null
                  },
                  "fYaxis": {
                    "_typename": "TAxis",
                    "fUniqueID": 0,
                    "fBits": 0,
                    "fName": "yaxis",
                    "fTitle": "",
                    "fNdivisions": 510,
                    "fAxisColor": 1,
                    "fLabelColor": 1,
                    "fLabelFont": 42,
                    "fLabelOffset": 0.005,
                    "fLabelSize": 0.035,
                    "fTickLength": 0.03,
                    "fTitleOffset": 1.0,
                    "fTitleSize": 0.035,
                    "fTitleColor": 1,
                    "fTitleFont": 42,
                    "fNbins": 1,
                    "fXmin": 0.0,
                    "fXmax": 1.0,
                    "fXbins": [],
                    "fFirst": 0,
                    "fLast": 0,
                    "fBits2": 0,
                    "fTimeDisplay": false,
                    "fTimeFormat": "",
                    "fLabels": null,
                    "fModLabs": null
                  },
                  "fZaxis": {
                    "_typename": "TAxis",
                    "fUniqueID": 0,
                    "fBits": 0,
                    "fName": "zaxis",
                    "fTitle": "",
                    "fNdivisions": 510,
                    "fAxisColor": 1,
                    "fLabelColor": 1,
                    "fLabelFont": 42,
                    "fLabelOffset": 0.005,
                    "fLabelSize": 0.035,
                    "fTickLength": 0.03,
                    "fTitleOffset": 1.0,
                    "fTitleSize": 0.035,
                    "fTitleColor": 1,
                    "fTitleFont": 42,
                    "fNbins": 1,
                    "fXmin": 0.0,
                    "fXmax": 1.0,
                    "fXbins": [],
                    "fFirst": 0,
                    "fLast": 0,
                    "fBits2": 0,
                    "fTimeDisplay": false,
                    "fTimeFormat": "",
                    "fLabels": null,
                    "fModLabs": null
                  },
                  "fBarOffset": 0,
                  "fBarWidth": 1000,
                  "fEntries": 4776546.0,
                  "fTsumw": 4776546.0,
                  "fTsumw2": 4776546.0,
                  "fTsumwx": 214617100000.0,
                  "fTsumwx2": 2.245448605e+16,
                  "fMaximum": -1111.0,
                  "fMinimum": -1111.0,
                  "fNormFactor": 0.0,
                  "fContour": [],
                  "fSumw2": [
                    0.0,
                    1068515.0,
                    911171.0,
                    630749.0,
                    449908.0,
                    336446.0,
                    265471.0,
                    219142.0,
                    186119.0,
                    0.0,
                    0.0,
                    122888.0,
                    107285.0,
                    92548.0,
                    78798.0,
                    65261.0,
                    53400.0,
                    44413.0,
                    36398.0,
                    0.0,
                    0.0,
                    19816.0,
                    16119.0,
                    12874.0,
                    10512.0,
                    8506.0,
                    6869.0,
                    5591.0,
                    4593.0,
                    3772.0,
                    3049.0,
                    2522.0,
                    2166.0,
                    1754.0,
                    1520.0,
                    1286.0,
                    1033.0,
                    932.0,
                    822.0,
                    720.0,
                    610.0,
                    474.0,
                    443.0,
                    391.0,
                    347.0,
                    310.0,
                    262.0,
                    210.0,
                    186.0,
                    171.0,
                    174.0,
                    0.0
                  ],
                  "fOption": "",
                  "fFunctions": {
                    "_typename": "TList",
                    "name": "TList",
                    "arr": [],
                    "opt": []
                  },
                  "fBufferSize": 0,
                  "fBuffer": [],
                  "fBinStatErrOpt": 0,
                  "fStatOverflows": 2
                }
              ],
              "num_entries": 4776546,
              "mean": 44931.44209225662,
              "variance": 2682154203.3712554,
              "stddev": 51789.51827707278,
              "num_entries_in_mean_window": 0
            }
          }
        }
      }
    }"""
    )

    assert checks_json == json_expected
