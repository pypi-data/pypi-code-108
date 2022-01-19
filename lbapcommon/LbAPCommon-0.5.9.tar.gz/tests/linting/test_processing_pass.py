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
import pytest

from LbAPCommon.parsing import create_proc_pass_map


@pytest.mark.parametrize(
    "jobs, expected",
    [
        [
            ["MC_2017_MagUp_Bu2JpsiKplus_no_str_g_Sim09g_tuple"],
            {
                "MC_2017_MagUp_Bu2JpsiKplus_no_str_g_Sim09g_tuple": "AnaProd-v0r0p00000000-MC_Bu2JpsiKplus_no_str_g_Sim09g_tuple"
            },
        ],
        [["______my-job"], {"______my-job": "AnaProd-v0r0p00000000-my-job"}],
        [["my---job"], {"my---job": "AnaProd-v0r0p00000000-my-job"}],
        [
            [
                "MC_2017_MagUp_Bu2JpsiKplus_no_str_g_Sim09g_strip",
                "MC_2017_MagUp_Bu2JpsiKplus_no_str_g_Sim09g_tuple",
            ],
            {
                "MC_2017_MagUp_Bu2JpsiKplus_no_str_g_Sim09g_strip": "AnaProd-v0r0p00000000-MC_Bu2JpsiKplus_no_str_g_Sim09g_strip",
                "MC_2017_MagUp_Bu2JpsiKplus_no_str_g_Sim09g_tuple": "tuple",
            },
        ],
        [
            [
                "MC_2017_MagUp_Bu2JpsiKplus_no_str_g_Sim09g",
                "MC_2017_MagUp_Bu2JpsiKplus_no_str_g_Sim09g_tuple",
            ],
            {
                "MC_2017_MagUp_Bu2JpsiKplus_no_str_g_Sim09g": "AnaProd-v0r0p00000000-MC_Bu2JpsiKplus_no_str_g_Sim09g",
                "MC_2017_MagUp_Bu2JpsiKplus_no_str_g_Sim09g_tuple": "tuple",
            },
        ],
        [
            [
                "MC_2017_MagUp_Bu2JpsiKplus_no_str_g_Sim09g_strip",
                "MC_2017_MagUp_Bu2JpsiKplus_no_str_g_Sim09g",
            ],
            {
                "MC_2017_MagUp_Bu2JpsiKplus_no_str_g_Sim09g_strip": "AnaProd-v0r0p00000000-MC_Bu2JpsiKplus_no_str_g_Sim09g_strip",
                "MC_2017_MagUp_Bu2JpsiKplus_no_str_g_Sim09g": "default",
            },
        ],
        [
            [
                "MC_2017_MagUp_Bu2JpsiKplus_no_str_g_Sim09g_hlt",
                "MC_2017_MagUp_Bu2JpsiKplus_no_str_g_Sim09g_strip",
                "MC_2017_MagUp_Bu2JpsiKplus_no_str_g_Sim09g_tuple",
            ],
            {
                "MC_2017_MagUp_Bu2JpsiKplus_no_str_g_Sim09g_hlt": "AnaProd-v0r0p00000000-MC_Bu2JpsiKplus_no_str_g_Sim09g_hlt",
                "MC_2017_MagUp_Bu2JpsiKplus_no_str_g_Sim09g_strip": "strip",
                "MC_2017_MagUp_Bu2JpsiKplus_no_str_g_Sim09g_tuple": "tuple",
            },
        ],
        [
            [
                "MC_2017_MagUp_Bu2JpsiKplus_Sim09g_strip_hlt",
                "MC_2017_MagUp_Bu2JpsiKplus_Sim09g_strip",
                "MC_2017_MagUp_Bu2JpsiKplus_Sim09g",
            ],
            {
                "MC_2017_MagUp_Bu2JpsiKplus_Sim09g_strip_hlt": "AnaProd-v0r0p00000000-MC_Bu2JpsiKplus_Sim09g_strip_hlt",
                "MC_2017_MagUp_Bu2JpsiKplus_Sim09g_strip": "default",
                "MC_2017_MagUp_Bu2JpsiKplus_Sim09g": "default",
            },
        ],
        [
            [
                "MC_2017_MagUp_Bu2JpsiKplus_no_str_g_Sim09g_hlt",
                "MC_2017_MagUp_Bu2JpsiKplus_no_str_g_Sim09g_hlt+strip",
                "MC_2017_MagUp_Bu2JpsiKplus_no_str_g_Sim09g_hlt+strip+tuple",
            ],
            {
                "MC_2017_MagUp_Bu2JpsiKplus_no_str_g_Sim09g_hlt": "AnaProd-v0r0p00000000-MC_Bu2JpsiKplus_no_str_g_Sim09g_hlt",
                "MC_2017_MagUp_Bu2JpsiKplus_no_str_g_Sim09g_hlt+strip": "strip",
                "MC_2017_MagUp_Bu2JpsiKplus_no_str_g_Sim09g_hlt+strip+tuple": "tuple",
            },
        ],
    ],
)
def test_create_proc_pass_map_good(jobs, expected):
    proc_pass_map = create_proc_pass_map(jobs, "v0r0p00000000")
    assert proc_pass_map == expected


@pytest.mark.parametrize(
    "jobs",
    [
        ["A" * 1000],
        [
            "hlt_MC_2017_MagUp_Bu2JpsiKplus_no_str_g_Sim09g",
            "strip_MC_2017_MagUp_Bu2JpsiKplus_no_str_g_Sim09g",
            "tuple_MC_2017_MagUp_Bu2JpsiKplus_no_str_g_Sim09g",
        ],
    ],
)
def test_create_proc_pass_map_bad(jobs):
    with pytest.raises(ValueError, match=r".*is too long.*"):
        create_proc_pass_map(jobs, "v0r0p00000000")
