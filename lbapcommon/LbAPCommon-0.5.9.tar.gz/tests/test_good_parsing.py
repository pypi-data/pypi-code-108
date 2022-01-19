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
from copy import deepcopy
from textwrap import dedent

import pytest
import strictyaml
import yaml

import LbAPCommon

OPTIONAL_KEYS = [
    "root_in_tes",
    "simulation",
    "luminosity",
    "data_type",
    "input_type",
    "dddb_tag",
    "conddb_tag",
    "comment",
]


def test_good_no_defaults():
    rendered_yaml = dedent(
        """\
    job_1:
        application: DaVinci/v45r3
        input:
            bk_query: /MC/2018/Beam6500GeV-2018-MagDown/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST
        output: FILETYPE.ROOT
        options:
            - options.py
            - $VAR/a.py
        wg: Charm
        inform: a.b@c.d
        priority: 1a
        completion_percentage: 99.5
    """
    )
    jobs_data, checks_data = LbAPCommon.parse_yaml(rendered_yaml)
    assert len(jobs_data) == 1
    assert jobs_data["job_1"]["application"] == "DaVinci/v45r3"
    assert jobs_data["job_1"]["input"] == {
        "bk_query": "/MC/2018/Beam6500GeV-2018-MagDown/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST"
    }
    assert jobs_data["job_1"]["output"] == "FILETYPE.ROOT"
    assert jobs_data["job_1"]["options"] == ["options.py", "$VAR/a.py"]
    assert jobs_data["job_1"]["wg"] == "Charm"
    assert jobs_data["job_1"]["automatically_configure"] is False
    assert jobs_data["job_1"]["turbo"] is False
    assert jobs_data["job_1"]["inform"] == "a.b@c.d"
    assert jobs_data["job_1"]["priority"] == "1a"
    assert jobs_data["job_1"]["completion_percentage"] == 99.5
    assert checks_data == {}


@pytest.mark.parametrize(
    "value,expected",
    [
        ("FILETYPE.ROOT", ["FILETYPE.ROOT"]),
        ("filetype.root", ["FILETYPE.ROOT"]),
        ("filetype.ROOT", ["FILETYPE.ROOT"]),
        ("\n        - filetype.ROOT", ["FILETYPE.ROOT"]),
        (
            "\n        - filetype.ROOT\n        - filetype.dst",
            ["FILETYPE.ROOT", "FILETYPE.DST"],
        ),
    ],
)
def test_good_output_filetype_scalar(value, expected):
    rendered_yaml = dedent(
        """\
    job_1:
        application: DaVinci/v45r3
        input:
            bk_query: /MC/2018/Beam6500GeV-2018-MagDown/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST
        output: {value}
        options:
            - $VAR/a.py
        wg: Charm
        inform: a.b@c.d
    """.format(
            value=value
        )
    )
    jobs_data, checks_data = LbAPCommon.parse_yaml(rendered_yaml)
    LbAPCommon.validate_yaml(jobs_data, checks_data, "a", "b")
    assert len(jobs_data) == 1

    assert jobs_data["job_1"]["output"] == expected

    assert jobs_data["job_1"]["application"] == "DaVinci/v45r3"
    assert jobs_data["job_1"]["input"] == {
        "bk_query": "/MC/2018/Beam6500GeV-2018-MagDown/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST"
    }
    assert jobs_data["job_1"]["options"] == ["$VAR/a.py"]
    assert jobs_data["job_1"]["wg"] == "Charm"
    assert jobs_data["job_1"]["automatically_configure"] is False
    assert jobs_data["job_1"]["turbo"] is False
    assert jobs_data["job_1"]["inform"] == ["a.b@c.d"]
    assert checks_data == {}


def test_good_with_defaults():
    rendered_yaml = dedent(
        """\
    defaults:
        wg: Charm
        automatically_configure: yes
        inform:
            - name@example.com
        priority: 1a
        completion_percentage: 95.6
        comment: This production will produce tuples of a, b, c decays for the x analysis in the y working group

    job_1:
        application: DaVinci/v45r3
        input:
            bk_query: "/MC/2018/Beam6500GeV-2018-MagDown/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST"
        output: FILETYPE.ROOT
        options:
            - options.py

    job_2:
        application: DaVinci/v44r0
        input:
            bk_query: "/MC/2018/Beam6500GeV-2018-MagUp/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST"
        output: FILETYPE.ROOT
        options:
            - other_options.py
        wg: B2OC
        automatically_configure: false
        inform:
            - other@example.com
        priority: 2a
        completion_percentage: 87.35
    """
    )
    jobs_data, checks_data = LbAPCommon.parse_yaml(rendered_yaml)
    assert len(jobs_data) == 2

    assert jobs_data["job_1"]["application"] == "DaVinci/v45r3"
    assert jobs_data["job_1"]["input"] == {
        "bk_query": "/MC/2018/Beam6500GeV-2018-MagDown/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST"
    }
    assert jobs_data["job_1"]["output"] == "FILETYPE.ROOT"
    assert jobs_data["job_1"]["options"] == ["options.py"]
    assert jobs_data["job_1"]["wg"] == "Charm"
    assert jobs_data["job_1"]["automatically_configure"] is True
    assert jobs_data["job_1"]["turbo"] is False
    assert jobs_data["job_1"]["inform"] == ["name@example.com"]
    assert jobs_data["job_1"]["priority"] == "1a"
    assert jobs_data["job_1"]["completion_percentage"] == 95.6
    assert (
        jobs_data["job_1"]["comment"]
        == "This production will produce tuples of a, b, c decays for the x analysis in the y working group"
    )

    assert jobs_data["job_2"]["application"] == "DaVinci/v44r0"
    assert jobs_data["job_2"]["input"] == {
        "bk_query": "/MC/2018/Beam6500GeV-2018-MagUp/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST"
    }
    assert jobs_data["job_2"]["output"] == "FILETYPE.ROOT"
    assert jobs_data["job_2"]["options"] == ["other_options.py"]
    assert jobs_data["job_2"]["wg"] == "B2OC"
    assert jobs_data["job_2"]["automatically_configure"] is False
    assert jobs_data["job_2"]["turbo"] is False
    assert jobs_data["job_2"]["inform"] == ["other@example.com"]
    assert jobs_data["job_2"]["priority"] == "2a"
    assert jobs_data["job_2"]["completion_percentage"] == 87.35
    assert (
        jobs_data["job_2"]["comment"]
        == "This production will produce tuples of a, b, c decays for the x analysis in the y working group"
    )

    assert checks_data == {}


def test_good_all_turbo():
    rendered_yaml = dedent(
        """\
    defaults:
        wg: Charm
        automatically_configure: yes
        turbo: yes
        inform:
            - name@example.com

    job_1:
        application: DaVinci/v45r3
        input:
            bk_query: "/MC/2018/Beam6500GeV-2018-MagDown/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST"
        output: FILETYPE.ROOT
        options:
            - options.py

    job_2:
        application: DaVinci/v44r0
        input:
            bk_query: "/MC/2018/Beam6500GeV-2018-MagUp/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST"
        output: FILETYPE.ROOT
        options:
            - other_options.py
        wg: B2OC
        automatically_configure: false
        inform:
            - other@example.com

    job_3:
        application: DaVinci/v45r3
        input:
            bk_query: "/MC/2018/Beam6500GeV-2018-MagDown/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST"
        output: FILETYPE.ROOT
        turbo: no
        options:
            - options.py
    """
    )
    jobs_data, checks_data = LbAPCommon.parse_yaml(rendered_yaml)
    assert len(jobs_data) == 3

    assert jobs_data["job_1"]["application"] == "DaVinci/v45r3"
    assert jobs_data["job_1"]["input"] == {
        "bk_query": "/MC/2018/Beam6500GeV-2018-MagDown/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST"
    }
    assert jobs_data["job_1"]["output"] == "FILETYPE.ROOT"
    assert jobs_data["job_1"]["options"] == ["options.py"]
    assert jobs_data["job_1"]["wg"] == "Charm"
    assert jobs_data["job_1"]["automatically_configure"] is True
    assert jobs_data["job_1"]["turbo"] is True
    assert jobs_data["job_1"]["inform"] == ["name@example.com"]

    assert jobs_data["job_2"]["application"] == "DaVinci/v44r0"
    assert jobs_data["job_2"]["input"] == {
        "bk_query": "/MC/2018/Beam6500GeV-2018-MagUp/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST"
    }
    assert jobs_data["job_2"]["output"] == "FILETYPE.ROOT"
    assert jobs_data["job_2"]["options"] == ["other_options.py"]
    assert jobs_data["job_2"]["wg"] == "B2OC"
    assert jobs_data["job_2"]["automatically_configure"] is False
    assert jobs_data["job_2"]["turbo"] is True
    assert jobs_data["job_2"]["inform"] == ["other@example.com"]

    assert jobs_data["job_3"]["application"] == "DaVinci/v45r3"
    assert jobs_data["job_3"]["input"] == {
        "bk_query": "/MC/2018/Beam6500GeV-2018-MagDown/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST"
    }
    assert jobs_data["job_3"]["output"] == "FILETYPE.ROOT"
    assert jobs_data["job_3"]["options"] == ["options.py"]
    assert jobs_data["job_3"]["wg"] == "Charm"
    assert jobs_data["job_3"]["automatically_configure"] is True
    assert jobs_data["job_3"]["turbo"] is False
    assert jobs_data["job_3"]["inform"] == ["name@example.com"]

    for key in OPTIONAL_KEYS:
        for job in ["job_1", "job_2", "job_3"]:
            assert key not in jobs_data[job]

    assert checks_data == {}


def test_good_some_turbo():
    rendered_yaml = dedent(
        """\
    defaults:
        wg: Charm
        automatically_configure: yes
        turbo: no
        inform:
            - name@example.com

    job_1:
        application: DaVinci/v45r3
        input:
            bk_query: "/MC/2018/Beam6500GeV-2018-MagDown/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST"
        output: FILETYPE.ROOT
        options:
            - options.py

    job_2:
        application: DaVinci/v44r0
        input:
            bk_query: "/MC/2018/Beam6500GeV-2018-MagUp/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST"
        output: FILETYPE.ROOT
        options:
            - other_options.py
        wg: B2OC
        automatically_configure: false
        inform:
            - other@example.com

    job_3:
        application: DaVinci/v45r3
        input:
            bk_query: "/MC/2018/Beam6500GeV-2018-MagDown/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST"
        output: FILETYPE.ROOT
        turbo: yes
        options:
            - options.py
    """
    )
    jobs_data, checks_data = LbAPCommon.parse_yaml(rendered_yaml)
    assert len(jobs_data) == 3

    assert jobs_data["job_1"]["application"] == "DaVinci/v45r3"
    assert jobs_data["job_1"]["input"] == {
        "bk_query": "/MC/2018/Beam6500GeV-2018-MagDown/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST"
    }
    assert jobs_data["job_1"]["output"] == "FILETYPE.ROOT"
    assert jobs_data["job_1"]["options"] == ["options.py"]
    assert jobs_data["job_1"]["wg"] == "Charm"
    assert jobs_data["job_1"]["automatically_configure"] is True
    assert jobs_data["job_1"]["turbo"] is False
    assert jobs_data["job_1"]["inform"] == ["name@example.com"]

    assert jobs_data["job_2"]["application"] == "DaVinci/v44r0"
    assert jobs_data["job_2"]["input"] == {
        "bk_query": "/MC/2018/Beam6500GeV-2018-MagUp/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST"
    }
    assert jobs_data["job_2"]["output"] == "FILETYPE.ROOT"
    assert jobs_data["job_2"]["options"] == ["other_options.py"]
    assert jobs_data["job_2"]["wg"] == "B2OC"
    assert jobs_data["job_2"]["automatically_configure"] is False
    assert jobs_data["job_2"]["turbo"] is False
    assert jobs_data["job_2"]["inform"] == ["other@example.com"]

    assert jobs_data["job_3"]["application"] == "DaVinci/v45r3"
    assert jobs_data["job_3"]["input"] == {
        "bk_query": "/MC/2018/Beam6500GeV-2018-MagDown/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST"
    }
    assert jobs_data["job_3"]["output"] == "FILETYPE.ROOT"
    assert jobs_data["job_3"]["options"] == ["options.py"]
    assert jobs_data["job_3"]["wg"] == "Charm"
    assert jobs_data["job_3"]["automatically_configure"] is True
    assert jobs_data["job_3"]["turbo"] is True
    assert jobs_data["job_3"]["inform"] == ["name@example.com"]

    for key in OPTIONAL_KEYS:
        for job in ["job_1", "job_2", "job_3"]:
            assert key not in jobs_data[job]

    assert checks_data == {}


def test_good_automatically_configure_overrides():
    rendered_yaml = dedent(
        """\
    defaults:
        wg: Charm
        automatically_configure: yes
        turbo: no
        inform:
            - name@example.com

    job_1:
        application: DaVinci/v45r3
        input:
            bk_query: "/MC/2018/Beam6500GeV-2018-MagDown/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST"
        output: FILETYPE.ROOT
        options:
            - options.py

    job_2:
        application: DaVinci/v44r0
        input:
            bk_query: "/MC/2018/Beam6500GeV-2018-MagUp/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST"
        output: FILETYPE.ROOT
        options:
            - other_options.py
        wg: B2OC
        automatically_configure: false
        inform:
            - other@example.com

    job_3:
        application: DaVinci/v45r3
        input:
            bk_query: "/MC/2018/Beam6500GeV-2018-MagDown/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST"
        output: FILETYPE.ROOT
        turbo: yes
        options:
            - options.py
        root_in_tes: "/Event/Charm"
        simulation: yes
        luminosity: no
        data_type: "2018"
        input_type: "DST"
        dddb_tag: "xyz-234"
        conddb_tag: "abc-def-20u"
    """
    )
    jobs_data, checks_data = LbAPCommon.parse_yaml(rendered_yaml)
    assert len(jobs_data) == 3

    assert jobs_data["job_1"]["application"] == "DaVinci/v45r3"
    assert jobs_data["job_1"]["input"] == {
        "bk_query": "/MC/2018/Beam6500GeV-2018-MagDown/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST"
    }
    assert jobs_data["job_1"]["output"] == "FILETYPE.ROOT"
    assert jobs_data["job_1"]["options"] == ["options.py"]
    assert jobs_data["job_1"]["wg"] == "Charm"
    assert jobs_data["job_1"]["automatically_configure"] is True
    assert jobs_data["job_1"]["turbo"] is False
    assert jobs_data["job_1"]["inform"] == ["name@example.com"]
    for key in OPTIONAL_KEYS:
        assert key not in jobs_data["job_1"]

    assert jobs_data["job_2"]["application"] == "DaVinci/v44r0"
    assert jobs_data["job_2"]["input"] == {
        "bk_query": "/MC/2018/Beam6500GeV-2018-MagUp/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST"
    }
    assert jobs_data["job_2"]["output"] == "FILETYPE.ROOT"
    assert jobs_data["job_2"]["options"] == ["other_options.py"]
    assert jobs_data["job_2"]["wg"] == "B2OC"
    assert jobs_data["job_2"]["automatically_configure"] is False
    assert jobs_data["job_2"]["turbo"] is False
    assert jobs_data["job_2"]["inform"] == ["other@example.com"]

    assert jobs_data["job_3"]["application"] == "DaVinci/v45r3"
    assert jobs_data["job_3"]["input"] == {
        "bk_query": "/MC/2018/Beam6500GeV-2018-MagDown/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST"
    }
    assert jobs_data["job_3"]["output"] == "FILETYPE.ROOT"
    assert jobs_data["job_3"]["options"] == ["options.py"]
    assert jobs_data["job_3"]["wg"] == "Charm"
    assert jobs_data["job_3"]["automatically_configure"] is True
    assert jobs_data["job_3"]["turbo"] is True
    assert jobs_data["job_3"]["inform"] == ["name@example.com"]

    assert jobs_data["job_3"]["root_in_tes"] == "/Event/Charm"
    assert jobs_data["job_3"]["simulation"] is True
    assert jobs_data["job_3"]["luminosity"] is False
    assert jobs_data["job_3"]["data_type"] == "2018"
    assert jobs_data["job_3"]["input_type"] == "DST"
    assert jobs_data["job_3"]["dddb_tag"] == "xyz-234"
    assert jobs_data["job_3"]["conddb_tag"] == "abc-def-20u"

    assert checks_data == {}


def test_good_automatically_configure_defaults_overrides():
    rendered_yaml = dedent(
        """\
    defaults:
        wg: Charm
        automatically_configure: yes
        turbo: no
        inform:
            - name@example.com
        root_in_tes: "/Event/Charm"
        simulation: yes
        luminosity: no
        data_type: "2018"
        input_type: "DST"
        dddb_tag: "xyz-234"
        conddb_tag: "abc-def-20u"

    job_1:
        application: DaVinci/v45r3
        input:
            bk_query: "/MC/2018/Beam6500GeV-2018-MagDown/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST"
        output: FILETYPE.ROOT
        options:
            - options.py

    job_2:
        application: DaVinci/v44r0
        input:
            bk_query: "/MC/2018/Beam6500GeV-2018-MagUp/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST"
        output: FILETYPE.ROOT
        options:
            - other_options.py
        wg: B2OC
        automatically_configure: false
        inform:
            - other@example.com

    job_3:
        application: DaVinci/v45r3
        input:
            bk_query: "/MC/2018/Beam6500GeV-2018-MagDown/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST"
        output: FILETYPE.ROOT
        turbo: yes
        options:
            - options.py
        root_in_tes: "/Event/Other"
        simulation: no
        luminosity: yes
        data_type: "2017"
        input_type: "MDST"
        dddb_tag: "tuv-345"
        conddb_tag: "ghj-20z"
    """
    )
    jobs_data, checks_data = LbAPCommon.parse_yaml(rendered_yaml)
    assert len(jobs_data) == 3

    assert jobs_data["job_1"]["application"] == "DaVinci/v45r3"
    assert jobs_data["job_1"]["input"] == {
        "bk_query": "/MC/2018/Beam6500GeV-2018-MagDown/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST"
    }
    assert jobs_data["job_1"]["output"] == "FILETYPE.ROOT"
    assert jobs_data["job_1"]["options"] == ["options.py"]
    assert jobs_data["job_1"]["wg"] == "Charm"
    assert jobs_data["job_1"]["automatically_configure"] is True
    assert jobs_data["job_1"]["turbo"] is False
    assert jobs_data["job_1"]["inform"] == ["name@example.com"]

    assert jobs_data["job_2"]["application"] == "DaVinci/v44r0"
    assert jobs_data["job_2"]["input"] == {
        "bk_query": "/MC/2018/Beam6500GeV-2018-MagUp/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST"
    }
    assert jobs_data["job_2"]["output"] == "FILETYPE.ROOT"
    assert jobs_data["job_2"]["options"] == ["other_options.py"]
    assert jobs_data["job_2"]["wg"] == "B2OC"
    assert jobs_data["job_2"]["automatically_configure"] is False
    assert jobs_data["job_2"]["turbo"] is False
    assert jobs_data["job_2"]["inform"] == ["other@example.com"]

    for job in ["job_1", "job_2"]:
        assert jobs_data[job]["root_in_tes"] == "/Event/Charm"
        assert jobs_data[job]["simulation"] is True
        assert jobs_data[job]["luminosity"] is False
        assert jobs_data[job]["data_type"] == "2018"
        assert jobs_data[job]["input_type"] == "DST"
        assert jobs_data[job]["dddb_tag"] == "xyz-234"
        assert jobs_data[job]["conddb_tag"] == "abc-def-20u"

    assert jobs_data["job_3"]["application"] == "DaVinci/v45r3"
    assert jobs_data["job_3"]["input"] == {
        "bk_query": "/MC/2018/Beam6500GeV-2018-MagDown/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST"
    }
    assert jobs_data["job_3"]["output"] == "FILETYPE.ROOT"
    assert jobs_data["job_3"]["options"] == ["options.py"]
    assert jobs_data["job_3"]["wg"] == "Charm"
    assert jobs_data["job_3"]["automatically_configure"] is True
    assert jobs_data["job_3"]["turbo"] is True
    assert jobs_data["job_3"]["inform"] == ["name@example.com"]

    assert jobs_data["job_3"]["root_in_tes"] == "/Event/Other"
    assert jobs_data["job_3"]["simulation"] is False
    assert jobs_data["job_3"]["luminosity"] is True
    assert jobs_data["job_3"]["data_type"] == "2017"
    assert jobs_data["job_3"]["input_type"] == "MDST"
    assert jobs_data["job_3"]["dddb_tag"] == "tuv-345"
    assert jobs_data["job_3"]["conddb_tag"] == "ghj-20z"

    assert checks_data == {}


def test_good_with_checks_no_defaults():
    rendered_yaml = dedent(
        """\
    checks:
        check_range:
            type: range
            expression: Tuple D0_M
            limits:
                min: 1750
                max: 2000
            blind_ranges:
                -
                    min: 1850
                    max: 1880
                -
                    min: 1900
                    max: 1910
        check_range_nd:
            type: range_nd
            expressions:
                x: Tuple D0_M
                y: Tuple Dst_M-D0_M
                z: Tuple D0_Eta
            limits:
                x:
                    min: 1750
                    max: 2000
                y:
                    min: 139
                    max: 150
                z:
                    min: 3
                    max: 7
            blind_ranges:
                -
                    x:
                        min: 1850
                        max: 1880
                    y:
                        min: 144
                        max: 146
                    z:
                        min: 4
                        max: 6
        check_num_entries:
            type: num_entries
            count: 100
        check_num_entries_per_invpb:
            type: num_entries_per_invpb
            count_per_invpb: 12.5
            lumi_pattern: LumiTuple
        check_branches_exist:
            type: branches_exist
            branches:
                - Dst_M
                - D0_M
                - D0_Eta

    job_1:
        application: DaVinci/v45r3
        input:
            bk_query: /MC/2018/Beam6500GeV-2018-MagDown/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST
        output: FILETYPE.ROOT
        options:
            - options.py
            - $VAR/a.py
        wg: Charm
        inform: a.b@c.d
        checks:
            - check_range
            - check_range_nd
            - check_num_entries
            - check_num_entries_per_invpb
            - check_branches_exist
    """
    )
    jobs_data, checks_data = LbAPCommon.parse_yaml(rendered_yaml)
    assert len(jobs_data) == 1
    assert jobs_data["job_1"]["application"] == "DaVinci/v45r3"
    assert jobs_data["job_1"]["input"] == {
        "bk_query": "/MC/2018/Beam6500GeV-2018-MagDown/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST"
    }
    assert jobs_data["job_1"]["output"] == "FILETYPE.ROOT"
    assert jobs_data["job_1"]["options"] == ["options.py", "$VAR/a.py"]
    assert jobs_data["job_1"]["wg"] == "Charm"
    assert jobs_data["job_1"]["automatically_configure"] is False
    assert jobs_data["job_1"]["turbo"] is False
    assert jobs_data["job_1"]["inform"] == "a.b@c.d"
    assert jobs_data["job_1"]["checks"] == [
        "check_range",
        "check_range_nd",
        "check_num_entries",
        "check_num_entries_per_invpb",
        "check_branches_exist",
    ]

    assert checks_data["check_range"]["type"] == "range"
    assert checks_data["check_range"]["expression"] == "Tuple D0_M"
    assert checks_data["check_range"]["limits"]["min"] == 1750.0
    assert checks_data["check_range"]["limits"]["max"] == 2000.0
    assert checks_data["check_range"]["blind_ranges"] == [
        {"min": 1850.0, "max": 1880.0},
        {"min": 1900.0, "max": 1910.0},
    ]

    assert checks_data["check_range_nd"]["type"] == "range_nd"
    assert checks_data["check_range_nd"]["expressions"] == {
        "x": "Tuple D0_M",
        "y": "Tuple Dst_M-D0_M",
        "z": "Tuple D0_Eta",
    }
    assert checks_data["check_range_nd"]["limits"]["x"] == {
        "min": 1750.0,
        "max": 2000.0,
    }
    assert checks_data["check_range_nd"]["limits"]["y"] == {"min": 139.0, "max": 150.0}
    assert checks_data["check_range_nd"]["limits"]["z"] == {"min": 3.0, "max": 7.0}
    assert checks_data["check_range_nd"]["blind_ranges"] == [
        {
            "x": {"min": 1850.0, "max": 1880.0},
            "y": {"min": 144.0, "max": 146.0},
            "z": {"min": 4.0, "max": 6.0},
        }
    ]

    assert checks_data["check_num_entries"]["type"] == "num_entries"
    assert checks_data["check_num_entries"]["count"] == 100

    assert checks_data["check_num_entries_per_invpb"]["type"] == "num_entries_per_invpb"
    assert checks_data["check_num_entries_per_invpb"]["count_per_invpb"] == 12.5
    assert checks_data["check_num_entries_per_invpb"]["lumi_pattern"] == "LumiTuple"

    assert checks_data["check_branches_exist"]["type"] == "branches_exist"
    assert checks_data["check_branches_exist"]["branches"] == [
        "Dst_M",
        "D0_M",
        "D0_Eta",
    ]


def test_good_with_checks_defaults_extra_checks():
    rendered_yaml = dedent(
        """\
    defaults:
        application: DaVinci/v45r3
        wg: Charm
        inform: a.b@c.d
        checks:
            - check_range

    checks:
        check_range:
            type: range
            expression: Tuple D0_M
            limits:
                min: 1750
                max: 2000
            blind_ranges:
                -
                    min: 1850
                    max: 1880
                -
                    min: 1900
                    max: 1910
        check_num_entries:
            type: num_entries
            count: 100

    job_1:
        input:
            bk_query: /MC/2018/Beam6500GeV-2018-MagDown/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST
        output: FILETYPE.ROOT
        options:
            - options.py
            - $VAR/a.py

    job_2:
        input:
            bk_query: "/MC/2018/Beam6500GeV-2018-MagUp/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST"
        output: FILETYPE.ROOT
        options:
            - other_options.py
        extra_checks:
            - check_num_entries
        inform:
            - other@example.com
    """
    )
    jobs_data, checks_data = LbAPCommon.parse_yaml(rendered_yaml)
    assert len(jobs_data) == 2
    assert jobs_data["job_1"]["application"] == "DaVinci/v45r3"
    assert jobs_data["job_1"]["input"] == {
        "bk_query": "/MC/2018/Beam6500GeV-2018-MagDown/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST"
    }
    assert jobs_data["job_1"]["output"] == "FILETYPE.ROOT"
    assert jobs_data["job_1"]["options"] == ["options.py", "$VAR/a.py"]
    assert jobs_data["job_1"]["wg"] == "Charm"
    assert jobs_data["job_1"]["automatically_configure"] is False
    assert jobs_data["job_1"]["turbo"] is False
    assert jobs_data["job_1"]["inform"] == "a.b@c.d"
    assert jobs_data["job_1"]["checks"] == ["check_range"]

    assert jobs_data["job_2"]["application"] == "DaVinci/v45r3"
    assert jobs_data["job_2"]["input"] == {
        "bk_query": "/MC/2018/Beam6500GeV-2018-MagUp/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST"
    }
    assert jobs_data["job_2"]["output"] == "FILETYPE.ROOT"
    assert jobs_data["job_2"]["options"] == ["other_options.py"]
    assert jobs_data["job_2"]["wg"] == "Charm"
    assert jobs_data["job_2"]["automatically_configure"] is False
    assert jobs_data["job_2"]["turbo"] is False
    assert jobs_data["job_2"]["inform"] == ["other@example.com"]
    assert jobs_data["job_2"]["checks"] == ["check_range", "check_num_entries"]
    assert "extra_checks" not in jobs_data["job_2"]

    assert checks_data["check_range"]["type"] == "range"
    assert checks_data["check_range"]["expression"] == "Tuple D0_M"
    assert checks_data["check_range"]["limits"]["min"] == 1750.0
    assert checks_data["check_range"]["limits"]["max"] == 2000.0
    assert checks_data["check_range"]["blind_ranges"] == [
        {"min": 1850.0, "max": 1880.0},
        {"min": 1900.0, "max": 1910.0},
    ]

    assert checks_data["check_num_entries"]["type"] == "num_entries"
    assert checks_data["check_num_entries"]["count"] == 100


@pytest.mark.parametrize(
    "missing_key", ["application", "input", "output", "wg", "inform"]
)
def test_bad_missing_key(missing_key):
    data = {
        "job_1": {
            "application": "DaVinci/v45r3",
            "input": {
                "bk_query": "/MC/2018/Beam6500GeV-2018-MagDown/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST"
            },
            "output": "FILETYPE.ROOT",
            "options": ["options.py"],
            "wg": "Charm",
            "inform": "a.b@c.d",
        }
    }
    del data["job_1"][missing_key]
    rendered_yaml = yaml.safe_dump(data)
    try:
        LbAPCommon.parse_yaml(rendered_yaml)
    except strictyaml.YAMLValidationError as e:
        assert "required key(s) '" + missing_key + "' not found" in str(e)


@pytest.mark.parametrize(
    "key,value",
    [
        ("application", "DaVinci"),
        ("input", "hello"),
        ("output", ""),
        ("wg", ""),
        ("inform", ""),
        ("automatically_configure", "null"),
        ("turbo", "absolutely"),
        ("root_in_tes", "DST"),
        ("simulation", "absolutely"),
        ("luminosity", "nope"),
        ("data_type", "MSDT"),
        ("input_type", "2016"),
        ("dddb_tag", ""),
        ("conddb_tag", ""),
        ("priority", "3a"),
    ],
)
def test_bad_invalid_value(key, value):
    data = {
        "job_1": {
            "application": "DaVinci/v45r3",
            "input": {
                "bk_query": "/MC/2018/Beam6500GeV-2018-MagDown/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST"
            },
            "output": "FILETYPE.ROOT",
            "options": ["options.py"],
            "wg": "Charm",
            "inform": "a.b@c.d",
        }
    }
    data["job_1"][key] = value
    rendered_yaml = yaml.safe_dump(data)
    with pytest.raises(strictyaml.YAMLValidationError, match=key + ":"):
        LbAPCommon.parse_yaml(rendered_yaml)


@pytest.mark.parametrize(
    "key,value",
    [
        ("completion_percentage", "ninety-nine"),
        ("completion_percentage", 100.1),
        ("completion_percentage", -24.33),
        ("completion_percentage", 9.9),
    ],
)
def test_bad_invalid_completion_percentage(key, value):
    data = {
        "job_1": {
            "application": "DaVinci/v45r3",
            "input": {
                "bk_query": "/MC/2018/Beam6500GeV-2018-MagDown/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST"
            },
            "output": "FILETYPE.ROOT",
            "options": ["options.py"],
            "wg": "Charm",
            "inform": "a.b@c.d",
        }
    }
    data["job_1"][key] = value
    rendered_yaml = yaml.safe_dump(data)
    with pytest.raises((ValueError, strictyaml.StrictYAMLError)):
        jobs_data, checks_data = LbAPCommon.parse_yaml(rendered_yaml)
        LbAPCommon.validate_yaml(jobs_data, checks_data, "a", "b")


def test_completion_percentage_not_in_defaults():
    job_template = {
        "application": "DaVinci/v45r3",
        "input": {
            "bk_query": "/MC/2018/Beam6500GeV-2018-MagDown/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST"
        },
        "output": "FILETYPE.ROOT",
        "options": ["options.py"],
        "wg": "Charm",
        "inform": "a.b@c.d",
    }
    data = {
        "job_1": deepcopy({**job_template, "completion_percentage": 100}),
        "job_2": deepcopy({**job_template}),
        "job_3": deepcopy({**job_template, "completion_percentage": 20}),
    }
    rendered_yaml = yaml.safe_dump(data)
    jobs_data, checks_data = LbAPCommon.parse_yaml(rendered_yaml)
    assert jobs_data["job_1"]["completion_percentage"] == 100
    assert jobs_data["job_2"]["completion_percentage"] == 100
    assert jobs_data["job_3"]["completion_percentage"] == 20


def test_completion_percentage_in_defaults():
    job_template = {
        "application": "DaVinci/v45r3",
        "input": {
            "bk_query": "/MC/2018/Beam6500GeV-2018-MagDown/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST"
        },
        "output": "FILETYPE.ROOT",
        "options": ["options.py"],
        "wg": "Charm",
        "inform": "a.b@c.d",
    }
    data = {
        "defaults": {
            "completion_percentage": 50,
        },
        "job_1": deepcopy({**job_template, "completion_percentage": 100}),
        "job_2": deepcopy({**job_template}),
        "job_3": deepcopy({**job_template, "completion_percentage": 20}),
    }
    rendered_yaml = yaml.safe_dump(data)
    jobs_data, checks_data = LbAPCommon.parse_yaml(rendered_yaml)
    assert jobs_data["job_1"]["completion_percentage"] == 100
    assert jobs_data["job_2"]["completion_percentage"] == 50
    assert jobs_data["job_3"]["completion_percentage"] == 20


def test_filetype_validation():
    from LbAPCommon.parsing import _normalise_filetype

    with pytest.raises(ValueError) as excinfo:
        _normalise_filetype("PROD", "JOB", "XICPS_MC_26265072_2016_MAGUP.ROOT")
    assert "is excessively long" not in str(excinfo.value)
    assert "event type" in str(excinfo.value)
    assert "magnet polarity" in str(excinfo.value)
    assert "data taking year" in str(excinfo.value)

    with pytest.raises(ValueError) as excinfo:
        _normalise_filetype("PROD", "JOB", "XICPS_MC_26265072.ROOT")
    assert "is excessively long" not in str(excinfo.value)
    assert "event type" in str(excinfo.value)
    assert "magnet polarity" not in str(excinfo.value)
    assert "data taking year" not in str(excinfo.value)

    with pytest.raises(ValueError) as excinfo:
        _normalise_filetype("PROD", "JOB", "XICPS_MC_MagDown.ROOT")
    assert "is excessively long" not in str(excinfo.value)
    assert "event type" not in str(excinfo.value)
    assert "magnet polarity" in str(excinfo.value)
    assert "data taking year" not in str(excinfo.value)

    with pytest.raises(ValueError) as excinfo:
        _normalise_filetype("PROD", "JOB", "A" * 100)
    assert "is excessively long" in str(excinfo.value)
    assert "event type" not in str(excinfo.value)
    assert "magnet polarity" not in str(excinfo.value)
    assert "data taking year" not in str(excinfo.value)

    assert _normalise_filetype("PROD", "JOB", "XICPS_MC.ROOT") == "XICPS_MC.ROOT"
    assert _normalise_filetype("PROD", "JOB", "xicps_mc.root") == "XICPS_MC.ROOT"


def test_wrong_polarity():
    rendered_yaml = dedent(
        """\
    job_MagDown:
        application: DaVinci/v45r3
        input:
            bk_query: /MC/2018/Beam6500GeV-2018-MagDown/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST
        output: FILETYPE.ROOT
        options:
            - $VAR/a.py
        wg: Charm
        inform: a.b@c.d

    job_MagUp:
        application: DaVinci/v45r3
        input:
            bk_query: /MC/2017/Beam6500GeV-2018-MagDown/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST
        output: FILETYPE.ROOT
        options:
            - $VAR/a.py
        wg: Charm
        inform: a.b@c.d
    """
    )
    jobs_data, checks_data = LbAPCommon.parse_yaml(rendered_yaml)
    with pytest.raises(ValueError):
        LbAPCommon.validate_yaml(jobs_data, checks_data, "a", "b")


def test_wrong_polarity_acronym():
    rendered_yaml = dedent(
        """\
    job_MD:
        application: DaVinci/v45r3
        input:
            bk_query: /MC/2018/Beam6500GeV-2018-MagDown/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST
        output: FILETYPE.ROOT
        options:
            - $VAR/a.py
        wg: Charm
        inform: a.b@c.d

    job_MU:
        application: DaVinci/v45r3
        input:
            bk_query: /MC/2017/Beam6500GeV-2018-MagDown/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST
        output: FILETYPE.ROOT
        options:
            - $VAR/a.py
        wg: Charm
        inform: a.b@c.d
    """
    )
    jobs_data, checks_data = LbAPCommon.parse_yaml(rendered_yaml)
    with pytest.raises(ValueError):
        LbAPCommon.validate_yaml(jobs_data, checks_data, "a", "b")


def test_tuple_in_job_name():
    rendered_yaml = dedent(
        """\
    job_MagDown_tuple:
        application: DaVinci/v45r3
        input:
            bk_query: /MC/2018/Beam6500GeV-2018-MagDown/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST
        output: FILETYPE.ROOT
        options:
            - $VAR/a.py
        wg: Charm
        inform: a.b@c.d

    job_MagUp_tuple:
        application: DaVinci/v45r3
        input:
            bk_query: /MC/2018/Beam6500GeV-2018-MagUp/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST
        output: FILETYPE.ROOT
        options:
            - $VAR/a.py
        wg: Charm
        inform: a.b@c.d
    """
    )
    jobs_data, checks_data = LbAPCommon.parse_yaml(rendered_yaml)
    warnings = LbAPCommon.validate_yaml(jobs_data, checks_data, "a", "b")
    assert warnings == []


def test_polarity_acronym():
    rendered_yaml = dedent(
        """\
    job_MagDown_2018:
        application: DaVinci/v45r3
        input:
            bk_query: /MC/2018/Beam6500GeV-2018-MagDown/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST
        output: FILETYPE.ROOT
        options:
            - $VAR/a.py
        wg: Charm
        inform: a.b@c.d

    job_MagUp_2018:
        application: DaVinci/v45r3
        input:
            bk_query: /MC/2018/Beam6500GeV-2018-MagUp/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST
        output: FILETYPE.ROOT
        options:
            - $VAR/a.py
        wg: Charm
        inform: a.b@c.d

    job_MD_2017:
        application: DaVinci/v45r3
        input:
            bk_query: /MC/2017/Beam6500GeV-2017-MagDown/Sim09g/Trig0x62661709/Reco17/24142001/ALLSTREAMS.DST
        output: FILETYPE.ROOT
        options:
            - $VAR/a.py
        wg: Charm
        inform: a.b@c.d

    job_MU_2017:
        application: DaVinci/v45r3
        input:
            bk_query: /MC/2017/Beam6500GeV-2017-MagUp/Sim09g/Trig0x62661709/Reco17/24142001/ALLSTREAMS.DST
        output: FILETYPE.ROOT
        options:
            - $VAR/a.py
        wg: Charm
        inform: a.b@c.d
    """
    )
    jobs_data, checks_data = LbAPCommon.parse_yaml(rendered_yaml)
    warnings = LbAPCommon.validate_yaml(jobs_data, checks_data, "a", "b")
    assert warnings == []


def test_missing_polarity():
    rendered_yaml = dedent(
        """\
    job_MagDown:
        application: DaVinci/v45r3
        input:
            bk_query: /MC/2018/Beam6500GeV-2018-MagDown/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST
        output: FILETYPE.ROOT
        options:
            - $VAR/a.py
        wg: Charm
        inform: a.b@c.d
    """
    )
    jobs_data, checks_data = LbAPCommon.parse_yaml(rendered_yaml)
    warnings = LbAPCommon.validate_yaml(jobs_data, checks_data, "a", "b")
    assert (
        "/mc/2018/beam6500gev-2018-magdown/sim09g/trig0x617d18a4/reco18/24142001/allstreams.dst"
        " has been requested as input for 1 job(s)"
        " but its opposite polarity counterpart has not been requested for any jobs."
        " Are you sure you do not want the other polarity?" in warnings
    )


def test_duplicate_bk_query():
    rendered_yaml = dedent(
        """\
    job_1:
        application: DaVinci/v45r3
        input:
            bk_query: /MC/2018/Beam6500GeV-2018-MagDown/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST
        output: FILETYPE.ROOT
        options:
            - $VAR/a.py
        wg: Charm
        inform: a.b@c.d

    job_2:
        application: DaVinci/v45r3
        input:
            bk_query: /MC/2018/Beam6500GeV-2018-MagDown/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST
        output: FILETYPE.ROOT
        options:
            - $VAR/b.py
        wg: Charm
        inform: a.b@c.d
    """
    )
    jobs_data, checks_data = LbAPCommon.parse_yaml(rendered_yaml)
    warnings = LbAPCommon.validate_yaml(jobs_data, checks_data, "a", "b")
    assert (
        "Duplicate bk_query found (this is a case insensitive check): "
        "/mc/2018/beam6500gev-2018-magdown/sim09g/trig0x617d18a4/reco18/24142001/allstreams.dst"
        in warnings
    )
