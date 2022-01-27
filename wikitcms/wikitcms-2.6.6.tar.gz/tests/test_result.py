# -*- coding: utf-8 -*-

# Copyright Red Hat
#
# This file is part of python-wikitcms.
#
# python-wikitcms is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Author: Adam Williamson <awilliam@redhat.com>

# these are all kinda inappropriate for pytest patterns
# pylint: disable=no-init, protected-access, no-self-use, unused-argument, too-many-arguments

"""Tests for result.py."""

import wikitcms.result as rs


class TestResults:
    """Tests for find_results()."""

    def _check_result(
        self,
        res,
        status=None,
        user=None,
        bugs=None,
        comment="",
        bot=False,
        transferred=False,
        comment_bugs=None,
    ):
        if bugs is None:
            bugs = []
        if comment_bugs is None:
            comment_bugs = set()
        assert res.status == status
        assert res.user == user
        assert res.bugs == bugs
        assert res.comment == comment
        assert res.bot == bot
        assert res.transferred == transferred
        assert res.comment_bugs == comment_bugs

    def test_find_results_current_template(self):
        """Various common forms of the current template."""

        restext = """
{{result|none}}
{{result|pass}}
{{result|fail|adamwill}}
{{result|warn|adamwill|345234}}
{{result|pass|kparal|6789032}} <ref>Some comment.</ref>
{{result|fail||3456780}}
{{result|pass|previous RC3 run}}
{{result|pass|coconut|bot=true}}
{{result |fail |  rené|372312 |9345671}}
"""
        results = rs.find_results(restext)
        assert len(results) == 9
        self._check_result(results[0])
        self._check_result(results[1], status="pass")
        self._check_result(results[2], status="fail", user="adamwill")
        self._check_result(results[3], status="warn", user="adamwill", bugs=["345234"])
        self._check_result(
            results[4],
            status="pass",
            user="kparal",
            bugs=["6789032"],
            comment="<ref>Some comment.</ref>",
        )
        self._check_result(results[5], status="fail", bugs=["3456780"])
        self._check_result(results[6], status="pass", user="previous RC3 run", transferred=True)
        self._check_result(results[7], status="pass", user="coconut", bot=True)
        self._check_result(results[8], status="fail", user="rené", bugs=["372312", "9345671"])

    def test_find_results_old_template(self):
        """Various common forms of the old testresult template."""
        restext = """
{{testresult/none}}
{{testresult/pass|jlaska}}
{{testresult/fail|jkeating}} <ref>{{bz|517926}}</ref>
{{testresult/fail|jlaska}}  <ref>{{bz|533420}}- broken dep: gnome-python2-gdl-2.25.3-12.fc12.i686 requires libgdl-1.so.2</ref>
{{testresult/warn|jlaska}}  <ref>NEEDS REVIEW - https://fedorahosted.org/pipermail/autoqa-results/2009-November/001966.html</ref>
"""
        results = rs.find_results(restext)
        assert len(results) == 5
        self._check_result(results[0])
        self._check_result(results[1], status="pass", user="jlaska")
        self._check_result(results[2], status="fail", user="jkeating", bugs=["517926"])
        res3comm = (
            "<ref>- broken dep: gnome-python2-gdl-2.25.3-12.fc12.i686 requires "
            "libgdl-1.so.2</ref>"
        )
        self._check_result(
            results[3], status="fail", user="jlaska", bugs=["533420"], comment=res3comm
        )
        res4comm = (
            "<ref>NEEDS REVIEW - https://fedorahosted.org/pipermail/autoqa-results/"
            "2009-November/001966.html</ref>"
        )
        self._check_result(results[4], status="warn", user="jlaska", comment=res4comm)

    def test_find_results_exclusions(self):
        """Test excluding example, 'transferred' and 'bot' results."""
        restext = """
{{result|pass|adamwill}}
{{result|fail|SampleUser}}
{{result|fail|FASName}}
{{result|pass|previous RC2 run}}
{{result|pass|coconut|bot=true}}
"""
        assert len(rs.find_results(restext)) == 3
        assert len(rs.find_results(restext, transferred=False)) == 2
        assert len(rs.find_results(restext, bot=False)) == 2
        assert len(rs.find_results(restext, transferred=False, bot=False)) == 1

    def test_find_results_statuses(self):
        """Test filtering results by status."""
        restext = """
{{result|none}}
{{result|pass}}
{{result|fail|adamwill}}
{{result|pass|coconut|bot=true}}
{{result|warn|kparal}}
{{result|warn|jlaska}}
"""

        assert len(rs.find_results(restext)) == 6
        assert len(rs.find_results(restext, statuses=["pass", "fail"])) == 3
        assert len(rs.find_results(restext, statuses=["pass", "warn"], bot=False)) == 3

    def test_find_results_page_extracts(self):
        """Various tests culled from real test pages, with messy text."""
        # From Fedora_12_Final_RC1_Install. Includes sample results
        # which should be filtered (but the 'nones' cannot be).
        f12text = """
== Key ==

Please use the following format when posting results to this page


{| class="wikitable sortable" border="1"
! Priority !! Test Case !! i386 !! ppc !! x86_64 !! References
|- 
| Tier1
| A sample test case
| {{testresult/none}} <ref>Indicates untested</ref>
| {{testresult/pass|FASName}} <ref>Indicates a test that has passed </ref>
| {{testresult/fail|FASName}} <ref>Indicates a failed test ... see ''Notes/Bug(s)'' for details </ref>
| <references/> 
|-
| Tier2
| Another sample test case
| {{testresult/warn|FASName}} <ref>Indicates an inprogress or test that needs further review </ref>
| {{testresult/none}}
| style="background:lightgrey;"| {{testresult/none}} <ref> Indicates unsupported configuration </ref>
| <references/> 
|-
|}

== Priority ==

The explanation of test case priority is available at [[QA:Fedora_12_Install_Test_Plan#Test_Priority]].

= '''Test Matrix''' =

{| class="wikitable sortable" border="1"
! Priority !! Test Area !! Test Case !! i386 !! ppc !! x86_64 !! References
|-
| Tier1
| Image Sanity
| [[QA:Testcase_Mediakit_ISO_Size]]
| {{testresult/pass|kparal}} 
| {{testresult/pass|kparal}} 
| {{testresult/pass|kparal}} 
| <references/> 
|-
| Tier1
| Image Sanity
| [[QA:Testcase_Mediakit_ISO_Checksums]]
| {{testresult/none}}
| {{testresult/none}} 
| {{testresult/none}} 
| <references/> 
|- 
| Tier3
"""
        results = rs.find_results(f12text)
        assert len(results) == 9
        for res in results[3:6]:
            self._check_result(res, status="pass", user="kparal")
        for res in results[6:8]:
            self._check_result(res)

        # extracts from Fedora_16_Final_RC1_Install. Result split
        # across lines, multiple results on one line.
        f16text = """
|-
| Alpha
| Install Repository
| [[QA:Testcase_install_repository_Mirrorlist_default]]
| {{result|pass|rmarko}} <ref>{{bz|744463}} Final blocker?
</ref>
| {{result|pass|rmarko}}
|-
| Alpha
| Install Repository
| [[QA:Testcase_install_repository_DVD_default]]
| {{result|pass|rmarko}}{{result|pass|robatino}}
| {{result|pass|rmarko}}{{result|pass|robatino}}
|-
"""
        results = rs.find_results(f16text)
        assert len(results) == 6
        self._check_result(
            results[0],
            status="pass",
            user="rmarko",
            comment="<ref>{{bz|744463}} Final blocker?\n</ref>",
            comment_bugs=set(["744463"]),
        )
        for res in (results[1], results[2], results[4]):
            self._check_result(res, status="pass", user="rmarko")
        for res in (results[3], results[5]):
            self._check_result(res, status="pass", user="robatino")

        # from Test_Results:Fedora_23_Final_RC3_Installation
        # bot text mixed with regular results
        f23text = """
|-
| Alpha
| [[QA:Testcase_partitioning_guided_empty]]
| {{result|pass|coconut|bot=true}}{{result|pass|juliuxpigface}}
| {{result|pass|coconut|bot=true}}
| {{result|none}}
|-
| Alpha
| [[QA:Testcase_partitioning_guided_delete_all]]
| {{result|pass|roshi}}{{result|pass|coconut|bot=true}}{{result|pass|juliuxpigface}}
| {{result|pass|coconut|bot=true}}
| {{result|none}}
|-
| Alpha
| [[QA:Testcase_partitioning_guided_multi_select]]
| {{result|pass|coconut|bot=true}}
| {{result|pass|coconut|bot=true}}
| style="background:lightgrey;"|
|-
"""
        results = rs.find_results(f23text)
        resexc = rs.find_results(f23text, bot=False)
        assert len(results) == 11
        assert len(resexc) == 5
        for res in (results[0], results[2], results[5], results[7], results[9], results[10]):
            self._check_result(res, status="pass", user="coconut", bot=True)
        for res in (results[3], results[8]):
            self._check_result(res)
        for res in (results[1], results[6]):
            self._check_result(res, status="pass", user="juliuxpigface")
        self._check_result(results[4], status="pass", user="roshi")

    def test_find_results_by_row(self):
        """Tests for find_results_by_row."""
        # extracts from Test_Day:2011-02-23_Radeon
        # example results (should be filtered), various username styles
        # one result with a username included added to make coverage
        # happy
        restext = """
=== Main tests ===

{|
! User
! Smolt Profile
! [[QA:Testcase_radeon_basic|Basic test]]
! [[QA:Testcase_radeon_gnome3|GNOME 3 start]]
! [[QA:Testcase_radeon_dpms|DPMS]]
! [[QA:Testcase_radeon_xv|XVideo]]
! [[QA:Testcase_radeon_rotate|Rotation]]
! [[QA:Testcase_radeon_restartx|X restart]]
! [[QA:Testcase_radeon_rendercheck|Rendercheck]]
! [[QA:Testcase_radeon_glx|GLX]]
! [[QA:Testcase_radeon_fastuserswitch|User switch]]
! [[QA:Testcase_radeon_vt|VT switch]]
! [[QA:Testcase_radeon_suspend|Suspend]]
! [[QA:Testcase_radeon_multihead|Multihead]]
! Comments
|-
| [[User:Example | Example user]] 
| [http://www.smolts.org/client/show/pub_84465125-1350-4f83-87b9-5f16f7430eb8 HW]
| {{result|pass}}
| {{result|pass}}
| {{result|pass}}
| {{result|pass}}
| {{result|pass}}
| {{result|pass}}
| {{result|pass}}
| {{result|pass}}
| {{result|pass}}
| N/A
| {{result|fail||123456}}
| {{result|warn||234567}}
| <references/>
|-
| [[Denis Kurochkin]] 
| [http://www.smolts.org/client/show/pub_76e7df41-e4bb-406b-a9d2-c70564d479b7 HW]
| {{result|warn}} <ref group="long">Resolution detected as 800x600. System - system settings - display - mirror display is setted on by default. While it setted on I can not change resolution</ref>
| {{result|warn}} <ref>UI bugs like this [http://i52.tinypic.com/2qixm4y.png screenshot] </ref>
| {{result|pass}}
| {{result|pass}}
| {{result|inprogress}}
| {{result|inprogress}}
| {{result|inprogress}}
| {{result|inprogress}}
| {{result|inprogress}}
| {{result|inprogress}}
| {{result|inprogress}}
| {{result|inprogress}}
| <references/>
|-
| MadRouter
| [http://www.smolts.org/client/show/pub_7a5f902f-a866-4810-9a14-e5b3a9702cd6 HW]
| {{result|pass}}
| {{result|warn}}<ref>gnome shell does not start after first boot, start successfully after next boots</ref>
| {{result|pass}}
| {{result|pass}}
| {{result|pass}}
| {{result|pass}}
| {{result|pass}}<ref>[[File:Radeon_renderchecklog_madrouter.gz]]</ref>
| {{result|pass}}
| {{result|pass}}<ref>work fine from gnome 3 shell, N/A from gnome desktop</ref>
| {{result|pass}}
| {{result|warn}}<ref>shut down instead of suspend from gnome 3 shell, but work fine from gnome desktop</ref>
| {{result|pass}}
| <references/>
|-
| [[User:Mira | Mira]] 
| [http://www.smolts.org/client/show/pub_94b448bc-4277-4c30-89cc-0c2b7047f9ca HW]
| {{result|pass}}
| {{result|warn}} <ref>Always after 1st log-in Gnome in fallback mode, after log-out log-in Gnome shell started</ref>
| {{result|pass}}
| {{result|pass}}
| {{result|pass}}
| {{result|pass}}
| {{result|pass}}
| {{result|pass}}
| {{result|pass}}
| {{result|pass}}
| {{result|fail}} <ref>System didn't suspend successfully, it just simply switched off</ref>
| {{result|warn|foobar}}
| N/A
| <references/>
|-
"""
        results = rs.find_results_by_row(restext)
        assert len(results) == 36
        for res in results[0:12]:
            assert res.user == "[[denis kurochkin]]"
        for res in results[12:24]:
            assert res.user == "madrouter"
        for res in results[24:34]:
            assert res.user == "mira"
        assert results[35].user == "foobar"

    def _check_resultrow(
        self, row, testcase, milestone, columns, results, section="", secid=0, name=None
    ):
        assert row.testcase == testcase
        assert row.milestone == milestone
        assert row.columns == columns
        assert row.section == section
        assert row.secid == secid
        for key in row.results.keys():
            row.results[key] = len(row.results[key])
        assert row.results == results
        if not name:
            name = testcase
        assert row.name == name

    def test_find_resultrows_simple(self):
        """find_resultrows: simple table."""
        text = """
==== Virtualization ====
</div>
{| class="wikitable sortable collapsible" width=100%
|- 
!style="width:10em"|Milestone !! Test Case !! x86<ref>'x86' means 'x86_64 or i386'</ref> BIOS !! x86 UEFI !! ARM
|-
| Beta
| [[QA:Testcase_Install_to_Previous_KVM]]
| {{result|pass|previous RC6 run}}{{result|pass|pschindl}}
| {{result|warn|previous RC6 run}}<ref>openQA's UEFI stuff has issues</ref>
| {{result|none}}
|-
| Beta
| [[QA:Testcase_Install_to_Current_KVM]]
| {{result|pass|previous RC6 run}}
| {{result|pass|previous RC3 run}}
| {{result|none}}
|-
| Final
| [[QA:Testcase_Boot_Methods_Xen_Para_Virt]]
| {{result|pass|previous RC3 run}}
| {{result|none}}
| {{result|none}}
|-
|}
"""
        rows = rs.find_resultrows(text)
        assert len(rows) == 3
        cols = ["Milestone", "Test Case", "x86 BIOS", "x86 UEFI", "ARM"]
        self._check_resultrow(
            rows[0],
            "QA:Testcase_Install_to_Previous_KVM",
            "Beta",
            cols,
            {"x86 BIOS": 2, "x86 UEFI": 1, "ARM": 1},
        )
        self._check_resultrow(
            rows[1],
            "QA:Testcase_Install_to_Current_KVM",
            "Beta",
            cols,
            {"x86 BIOS": 1, "x86 UEFI": 1, "ARM": 1},
        )
        self._check_resultrow(
            rows[2],
            "QA:Testcase_Boot_Methods_Xen_Para_Virt",
            "Final",
            cols,
            {"x86 BIOS": 1, "x86 UEFI": 1, "ARM": 1},
        )

    def test_find_resultrows_names(self):
        """find_resultrows: test instances by name."""
        text = """
{| class="wikitable sortable collapsible" width=100%
|-
!style="width:10em"|Milestone !! Image !! i386 !! x86_64 !! UEFI
|-
| Alpha
| [[QA:Testcase_Boot_default_install|Workstation live]]
| {{result|pass|coconut|bot=true}}
| {{result|pass|adamwill}}{{result|pass|coconut|bot=true}}
| {{result|pass|adamwill}}{{result|pass|pschindl}}<ref>burned on dvd</ref>{{result|pass|coconut|bot=true}}
|-
| Alpha
| [[QA:Testcase_Boot_default_install|Workstation netinst]]
| {{result|pass|kparal}}
| {{result|pass|pschindl}}
| {{result|pass|pschindl}}
|-
| Alpha
| [[QA:Testcase_Boot_default_install|Server netinst]]
| {{result|pass|coconut|bot=true}}
| {{result|pass|pschindl}}{{result|pass|coconut|bot=true}}
| {{result|pass|pschindl}}{{result|pass|coconut|bot=true}}
|-
"""
        rows = rs.find_resultrows(text)
        assert len(rows) == 3
        cols = ["Milestone", "Image", "i386", "x86_64", "UEFI"]
        self._check_resultrow(
            rows[0],
            "QA:Testcase_Boot_default_install",
            "Alpha",
            cols,
            {"i386": 1, "x86_64": 2, "UEFI": 3},
            name="Workstation live",
        )
        self._check_resultrow(
            rows[1],
            "QA:Testcase_Boot_default_install",
            "Alpha",
            cols,
            {"i386": 1, "x86_64": 1, "UEFI": 1},
            name="Workstation netinst",
        )
        self._check_resultrow(
            rows[2],
            "QA:Testcase_Boot_default_install",
            "Alpha",
            cols,
            {"i386": 1, "x86_64": 2, "UEFI": 2},
            name="Server netinst",
        )

    def test_find_resultrows_multiline(self):
        """find_resultrows: results split across lines."""
        text = """
{| class="wikitable sortable collapsible" border="1" width=100%
! Milestone !! Test Case  !! Local !! EC2 !! Openstack
|-
| Alpha
| [[QA:Testcase_base_startup]]
| {{result|pass|previous RC3 run}}{{result|pass|roshi}}
| {{result|pass|dustymabe}}ami-f43b489e
| {{result|pass|kevin}}
  {{result|pass|dustymabe}}
|-
|}
"""
        rows = rs.find_resultrows(text)
        assert len(rows) == 1
        self._check_resultrow(
            rows[0],
            "QA:Testcase_base_startup",
            "Alpha",
            ["Milestone", "Test Case", "Local", "EC2", "Openstack"],
            {"Local": 2, "EC2": 1, "Openstack": 2},
        )

    def test_find_resultrows_text_between_tables(self):
        """find_resultrows: check text containing test case names between
        tables is not parsed into a garbage row.
        """
        text = """
{| class="wikitable sortable collapsible" width=100%
|-
!style="width:10em"|Milestone !! Test Case !! Server !! Workstation !! Spins !! ARM disks !! Cloud
|-
| Alpha / Final
| [[QA:Testcase_Mediakit_Checksums]]
| {{result|pass|kparal}}{{result|pass|robatino}}
| {{result|pass|kparal}}{{result|pass|robatino}}
| {{result|pass|robatino}}
| {{result|pass|robatino}}
| {{result|pass|robatino}}
|-
|}
<references/>
<div style="background-color: lightgreen; text-align: center; border-style: solid; border-width: thin">

==== Default boot and install ====
</div>
{{admon/important|Bare metal testing required|Running these tests in a virtualized environment is valuable, but the test must pass on bare metal using a physical install medium for each release-blocking image in each test environment at least for the final release candidate image (i.e. the released image) for each milestone.}}

{{admon/note|Single test table|In all of these tests, the test case used is [[QA:Testcase_Boot_default_install]]. That is where the links point. The same test needs to be run for multiple images and target platforms. Note that the non-installer-based ARM disk images are covered by the later [[#ARM disk images]] section.}}
{| class="wikitable sortable collapsible" width=100%
|-
!style="width:10em"|Milestone !! Image !! i386 !! x86_64 !! UEFI
|-
| Alpha
| [[QA:Testcase_Boot_default_install|Workstation live]]
| {{result|pass|coconut|bot=true}}
| {{result|pass|adamwill}}{{result|pass|coconut|bot=true}}
| {{result|pass|adamwill}}{{result|pass|pschindl}}<ref>burned on dvd</ref>{{result|pass|coconut|bot=true}}
|-
|}
"""
        rows = rs.find_resultrows(text)
        assert len(rows) == 2

    def test_find_resultrows_column_titles_no_separator(self):
        """Test find_resultrows works OK when there is no separator
        before the column titles.
        """
        text = """
{| class="wikitable sortable" border="1"
! Priority !! Test Area !! Test Case !! i386 !! ppc !! x86_64 !! References
|- 
| Tier1
| Image Sanity
| [[QA:Testcase_Mediakit_ISO_Size]]
| {{testresult/none}}
| {{testresult/none}}
| {{testresult/none}}
| <references/> 
|-
"""
        rows = rs.find_resultrows(text)
        assert rows[0].columns == [
            "Priority",
            "Test Area",
            "Test Case",
            "i386",
            "ppc",
            "x86_64",
            "References",
        ]

    def test_find_resultrows_column_titles_sanitize(self):
        """Test the cleanups find_resultrows does on column names."""
        text = """
{| class="wikitable sortable" border="1"
|-
! Priority !! Test Area !! Test Case !! ''i386'' !! [[Somewhere|ppc]] !! x86_64 <ref>some comment</ref> !! References
|- 
| Tier1
| Image Sanity
| [[QA:Testcase_Mediakit_ISO_Size]]
| {{testresult/none}}
| {{testresult/none}}
| {{testresult/none}}
| <references/> 
|-
"""
        rows = rs.find_resultrows(text)
        assert rows[0].columns == [
            "Priority",
            "Test Area",
            "Test Case",
            "i386",
            "ppc",
            "x86_64",
            "References",
        ]

    def test_find_resultrows_iot(self):
        """Test that find_resultrows works on the IoT test case names
        that don't follow the same pattern as all the others.
        """
        text = """
{| class="wikitable sortable mw-collapsible" border="1" width=100%
! Milestone !! Test Case  !! x86_64 !! aarch64
|-
| Basic
| [[User:Pwhalen/QA/IoT_Tests/Zezere_Ignition|Zezere Ignition]]
| {{result|none}}
| {{result|none}}
|-
| Basic
| [[User:Pwhalen/QA/IoT_Tests/rpm-ostree_upgrade|rpm-ostree upgrade]]
| {{result|none}}
| {{result|none}}
|-
| Basic
| [[User:Pwhalen/QA/IoT/RpmOstree_Package_Layering|Layered Package Installation]]
| {{result|none}}
| {{result|none}}
|-
| Basic
| [[User:Pwhalen/QA/IoT_Tests/Rebase|rpm-ostree rebase]]
| {{result|none}}
| {{result|none}}
|-
| Basic
| [[User:Pwhalen/QA/IoT_Tests/Podman_Basic|Podman]]
| {{result|none}}
| {{result|none}}
|-
| Basic
| [[QA:Testcase_base_selinux]]
| {{result|none}}
| {{result|none}}
|-
| Basic
| [[QA:Testcase_base_service_manipulation]]
| {{result|none}}
| {{result|none}}
|-
|}
"""
        rows = rs.find_resultrows(text)
        assert len(rows) == 7
        cols = ["Milestone", "Test Case", "x86_64", "aarch64"]
        self._check_resultrow(
            rows[0],
            "User:Pwhalen/QA/IoT_Tests/Zezere_Ignition",
            "Basic",
            cols,
            {"x86_64": 1, "aarch64": 1},
            name="Zezere Ignition",
        )
        self._check_resultrow(
            rows[1],
            "User:Pwhalen/QA/IoT_Tests/rpm-ostree_upgrade",
            "Basic",
            cols,
            {"x86_64": 1, "aarch64": 1},
            name="rpm-ostree upgrade",
        )
        self._check_resultrow(
            rows[2],
            "User:Pwhalen/QA/IoT/RpmOstree_Package_Layering",
            "Basic",
            cols,
            {"x86_64": 1, "aarch64": 1},
            name="Layered Package Installation",
        )
        self._check_resultrow(
            rows[3],
            "User:Pwhalen/QA/IoT_Tests/Rebase",
            "Basic",
            cols,
            {"x86_64": 1, "aarch64": 1},
            name="rpm-ostree rebase",
        )
        self._check_resultrow(
            rows[4],
            "User:Pwhalen/QA/IoT_Tests/Podman_Basic",
            "Basic",
            cols,
            {"x86_64": 1, "aarch64": 1},
            name="Podman",
        )
        self._check_resultrow(
            rows[5],
            "QA:Testcase_base_selinux",
            "Basic",
            cols,
            {"x86_64": 1, "aarch64": 1},
        )
        self._check_resultrow(
            rows[6],
            "QA:Testcase_base_service_manipulation",
            "Basic",
            cols,
            {"x86_64": 1, "aarch64": 1},
        )

    def test_result_string_template(self):
        """Test string representation and result_template of Result
        instances."""
        res = rs.Result()
        assert str(res) == "Result placeholder - {{result|none}}"
        assert res.result_template == "{{result|none}}"

        res = rs.Result(status="pass")
        assert str(res) == "Result: Pass"
        assert res.result_template == "{{result|pass}}"

        res = rs.Result(status="fail", user="adamwill")
        assert str(res) == "Result: Fail from adamwill"
        assert res.result_template == "{{result|fail|adamwill}}"

        res = rs.Result(status="warn", user="rené", bugs=["435678", "1340987"])
        assert str(res) == "Result: Warn from rené, bugs: 435678, 1340987"
        assert res.result_template == "{{result|warn|rené|435678|1340987}}"

        res = rs.Result(
            status="pass", user="kparal", comment="some comment <ref>some reference</ref>"
        )
        assert str(res) == "Result: Pass from kparal, comment: some comment some reference"
        assert res.result_template == "{{result|pass|kparal}}some comment <ref>some reference</ref>"

        res = rs.Result.from_result_template("{{result|pass|previous RC3 run}}")
        assert str(res) == "Result: Pass transferred: previous RC3 run"
        assert res.result_template == "{{result|pass|previous RC3 run}}"

        res = rs.Result(status="pass", user="coconut", bot=True)
        assert str(res) == "BOT Result: Pass from coconut"
        assert res.result_template == "{{result|pass|coconut|bot=true}}"

    def test_from_result_template_bug_comment(self):
        """Test from_result_template handling of bug numbers with
        comment refs.
        """
        res = rs.Result.from_result_template("{{result|fail|bob|1034592#c8}}")
        assert res.status == "fail"
        assert res.user == "bob"
        assert res.bugs == ["1034592"]

    def test_resultrow_matches(self):
        """Test the 'matches' method of ResultRows."""
        text = """
{| class="wikitable sortable" border="1"
|-
! Priority !! Test Area !! Test Case !! ''i386'' !! [[Somewhere|ppc]] !! x86_64 <ref>some comment</ref> !! References
|- 
| Tier1
| Image Sanity
| [[QA:Testcase_Mediakit_ISO_Size]]
| {{testresult/none}}
| {{testresult/none}}
| {{testresult/none}}
| <references/> 
|-
"""
        row1 = rs.find_resultrows(text)[0]
        row2 = rs.find_resultrows(text)[0]
        row1.secid = row2.secid = 1
        assert row1.matches(row2)
        row2.name = "foo"
        assert not row1.matches(row2)
        row2.name = row1.name
        row2.secid = 2
        assert not row1.matches(row2)
        row2.secid = row1.secid
        row2.origtext = "foo"
        assert not row1.matches(row2)
        row2.origtext = row1.origtext
        row2.testcase = "foo"
        assert not row1.matches(row2)
        # test with a different type of object
        notarow = "foo"
        assert not row1.matches(notarow)


# vim: set textwidth=100 ts=8 et sw=4:
