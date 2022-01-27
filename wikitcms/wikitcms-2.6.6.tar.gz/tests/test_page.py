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
# pylint: disable=no-init, protected-access, no-self-use, unused-argument
# pylint: disable=invalid-name, too-few-public-methods

"""Tests for page.py."""

import datetime
import difflib
from decimal import Decimal
import json
import os
from unittest import mock

import mwclient.errors
import pytest

import wikitcms.event
import wikitcms.exceptions
import wikitcms.page
import wikitcms.result
import wikitcms.wiki

DATAPATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data")


def _diff(old, new):
    """Convenience function for diffing in add_results tests."""
    diff = list(difflib.ndiff(old.splitlines(), new.splitlines()))
    # we enumerate so we can check the changes are in the
    # correct place; obviously this relies on the known
    # content of the sample data
    return [item for item in enumerate(diff) if item[1].startswith(("+", "-", "?"))]


@pytest.mark.usefixtures("fakemwp")
class TestPage:
    """Tests for Page instances."""

    # the "fjajah" is just to make sure we're running offline; if I
    # screw up and add a test that hits the network it"ll cause the
    # tests to hang/fail instead of succeeding a bit slower
    site = wikitcms.wiki.Wiki("fjajah", do_init=False, force_login=False)

    def test_page_init(self):
        """Tests for Page.__init__."""
        pg = wikitcms.page.Page(self.site, "QA:Somepage")
        # __init__ stuff
        assert pg.checkname == "QA:Somepage"
        assert pg._sections is None
        assert pg.results_separators == []

    def test_page_sections(self, fakeapisections):
        """Tests for Page.sections."""
        pg = wikitcms.page.Page(self.site, "QA:Somepage")
        assert len(pg.sections) == 13
        assert pg.sections[0]["line"] == "Which tests to run"
        assert pg.sections[12]["line"] == "Upgrade tests"
        assert fakeapisections.call_count == 1
        # test caching
        assert len(pg.sections) == 13
        assert fakeapisections.call_count == 1
        # test error case
        pg._sections = None
        fakeapisections.side_effect = mwclient.errors.APIError(1, "foo", {})
        assert pg.sections == []
        assert fakeapisections.call_count == 2
        fakeapisections.side_effect = None
        # test cache clear, using simple return value for convenience
        fakeapisections.return_value = {"parse": {"sections": ["moo", "meep"]}}
        # until we save, changed API return value shouldn"t affect us
        assert pg.sections == []
        assert fakeapisections.call_count == 2
        with mock.patch("mwclient.page.Page.save", autospec=True):
            pg.save("foo", summary="bar")
        # now we saved, call count should increase and we should get
        # new values
        assert pg.sections == ["moo", "meep"]
        assert fakeapisections.call_count == 3

    @mock.patch("mwclient.page.Page.revisions")
    def test_page_creation_date(self, fakerev):
        """Tests for Page.creation_date."""
        pg = wikitcms.page.Page(self.site, "QA:Somepage")
        # the API gives us a timetuple, here
        date = datetime.datetime(2020, 3, 4).timetuple()
        fakerev.return_value = iter([{"timestamp": date}])
        assert pg.creation_date == "20200304"
        # this is a cached property, so we need to recreate the Page
        # instance now
        pg = wikitcms.page.Page(self.site, "QA:Somepage")
        fakerev.return_value = iter([])
        assert pg.creation_date == ""

    @mock.patch("mwclient.page.Page.save", autospec=True)
    def test_page_write(self, fakesave):
        """Tests for Page.write."""
        pg = wikitcms.page.Page(self.site, "QA:Somepage")
        # need seedtext and summary or else it should raise
        with pytest.raises(ValueError):
            pg.write()
        pg.seedtext = "something"
        with pytest.raises(ValueError):
            pg.write()
        pg.seedtext = None
        pg.summary = "summary"
        with pytest.raises(ValueError):
            pg.write()
        pg.seedtext = "seedtext"
        pg.write()
        assert fakesave.call_count == 1
        # [0][0] is self
        assert fakesave.call_args[0][1] == "seedtext"
        assert fakesave.call_args[0][2] == "summary"
        assert fakesave.call_args[1]["createonly"] is True
        pg.write(createonly=False)
        assert fakesave.call_count == 2
        assert fakesave.call_args[1]["createonly"] is False
        pg.write(createonly=None)
        assert fakesave.call_count == 3
        assert fakesave.call_args[1]["createonly"] is None

    @mock.patch("time.sleep", autospec=True)
    @mock.patch("mwclient.page.Page.save", autospec=True)
    def test_page_save(self, fakesave, faketime):
        """Tests for Page.save."""
        pg = wikitcms.page.Page(self.site, "QA:Somepage")
        assert pg.save("foo", "summary", oldtext="foo") == {"nochange": ""}
        assert fakesave.call_count == 0
        pg.save("foo", "summary", oldtext="bar")
        assert fakesave.call_count == 1
        assert "oldtext" not in fakesave.call_args[1]
        # test the retry-once-on-fail behaviour by having parent save
        # raise EditError once, then go back to normal
        fakesave.side_effect = [mwclient.errors.EditError(), None]
        pg.save("foo", "summary")
        assert faketime.call_count == 1
        assert fakesave.call_count == 3


@pytest.mark.usefixtures("fakemwp")
class TestValidationPages:
    """Tests for ValidationPage instances (all the child classes)."""

    site = wikitcms.wiki.Wiki("fjajah", do_init=False, force_login=False)

    def test_init(self):
        """Check all the various attributes of a ValidationPage set up
        during __init__ are correct for the common page types.
        """
        # a typical nightly page (should *not* be modular)
        nightly = wikitcms.page.NightlyPage(
            self.site, "32", "Installation", "Rawhide", "20200122.n.0"
        )
        # modular nightly page (based on the only nightly modular event
        # that ever existed...)
        modnightly = wikitcms.page.NightlyPage(
            self.site, "27", "Base", "Branched", "20171123.n.1", dist="Fedora-Modular"
        )
        # typical candidate page (should *not* be modular)
        candidate = wikitcms.page.ComposePage(self.site, "32", "Desktop", "RC", "1.2")
        # modular candidate page (based on the only modular compose we
        # ever did...)
        modcandidate = wikitcms.page.ComposePage(
            self.site, "27", "Server", "Beta", "1.5", dist="Fedora-Modular"
        )

        # IoT 'nightly'
        iotnightly = wikitcms.page.NightlyPage(
            self.site, "33", "General", "RC", "20200513.0", dist="Fedora-IoT"
        )
        assert nightly.release == "32"
        assert nightly.milestone == "Rawhide"
        assert nightly.compose == "20200122.n.0"
        assert nightly.version == "32 Rawhide 20200122.n.0"
        assert nightly.testtype == "Installation"
        assert nightly.dist == "Fedora"
        assert nightly.checkname == "Test Results:Fedora 32 Rawhide 20200122.n.0 Installation"
        assert nightly.summary == (
            "Relval bot-created Installation validation results page for "
            "Fedora 32 Rawhide 20200122.n.0"
        )
        assert nightly.results_separators == (
            "Test Matri",
            "Test Areas",
            "An unsupported test or configuration.  No testing is required.",
        )
        assert nightly.sortname == "32 100 20200122.n.0 Installation"
        assert nightly.sorttuple == (32, 100, Decimal("20200122.0"), "Installation")
        assert nightly.seedtext == (
            "{{subst:Validation results|testtype=Installation|release=32|milestone=Rawhide"
            "|date=20200122.n.0}}"
        )

        assert modnightly.release == "27"
        assert modnightly.milestone == "Branched"
        assert modnightly.compose == "20171123.n.1"
        assert modnightly.version == "27 Branched 20171123.n.1"
        assert modnightly.testtype == "Base"
        assert modnightly.dist == "Fedora-Modular"
        assert modnightly.checkname == "Test Results:Fedora-Modular 27 Branched 20171123.n.1 Base"
        assert modnightly.summary == (
            "Relval bot-created Base validation results page for "
            "Fedora-Modular 27 Branched 20171123.n.1"
        )
        assert modnightly.results_separators == (
            "Test Matri",
            "Test Areas",
            "An unsupported test or configuration.  No testing is required.",
        )
        assert modnightly.sortname == "27 150 20171123.n.1 Base"
        assert modnightly.sorttuple == (27, 150, Decimal("20171123.1"), "Base")
        assert modnightly.seedtext == (
            "{{subst:Modular validation results|testtype=Base|release=27|milestone=Branched"
            "|date=20171123.n.1}}"
        )

        assert candidate.release == "32"
        assert candidate.milestone == "RC"
        assert candidate.compose == "1.2"
        assert candidate.version == "32 RC 1.2"
        assert candidate.testtype == "Desktop"
        assert candidate.dist == "Fedora"
        assert candidate.checkname == "Test Results:Fedora 32 RC 1.2 Desktop"
        assert candidate.summary == (
            "Relval bot-created Desktop validation results page for " "Fedora 32 RC 1.2"
        )
        assert candidate.results_separators == (
            "Test Matri",
            "Test Areas",
            "An unsupported test or configuration.  No testing is required.",
        )
        # 6000 here is actually the value intended for "RC" as part of
        # a *compose* value, not "RC" as a *milestone* (with Pungi 4,
        # the GA milestone name changed from "Final" to "RC"). But it
        # doesn't seem to break anything, so I'm leaving it alone
        assert candidate.sortname == "32 6000 1.2 Desktop"
        assert candidate.sorttuple == (32, 800, Decimal("1.2"), "Desktop")
        assert candidate.seedtext == (
            "{{subst:Validation results|testtype=Desktop|release=32|milestone=RC|compose=1.2}}"
        )

        assert modcandidate.release == "27"
        assert modcandidate.milestone == "Beta"
        assert modcandidate.compose == "1.5"
        assert modcandidate.version == "27 Beta 1.5"
        assert modcandidate.testtype == "Server"
        assert modcandidate.dist == "Fedora-Modular"
        assert modcandidate.checkname == "Test Results:Fedora-Modular 27 Beta 1.5 Server"
        assert modcandidate.summary == (
            "Relval bot-created Server validation results page for " "Fedora-Modular 27 Beta 1.5"
        )
        assert modcandidate.results_separators == (
            "Test Matri",
            "Test Areas",
            "An unsupported test or configuration.  No testing is required.",
        )
        assert modcandidate.sortname == "27 400 1.5 Server"
        assert modcandidate.sorttuple == (27, 400, Decimal("1.5"), "Server")
        assert modcandidate.seedtext == (
            "{{subst:Modular validation results|testtype=Server|release=27|milestone=Beta"
            "|compose=1.5}}"
        )

        assert iotnightly.release == "33"
        assert iotnightly.milestone == "RC"
        assert iotnightly.compose == "20200513.0"
        assert iotnightly.version == "33 RC 20200513.0"
        assert iotnightly.testtype == "General"
        assert iotnightly.dist == "Fedora-IoT"
        assert iotnightly.checkname == "Test Results:Fedora-IoT 33 RC 20200513.0 General"
        assert iotnightly.summary == (
            "Relval bot-created General validation results page for Fedora-IoT 33 RC 20200513.0"
        )
        assert iotnightly.results_separators == (
            "Test Matri",
            "Test Areas",
            "An unsupported test or configuration.  No testing is required.",
        )
        assert iotnightly.sortname == "33 6000 20200513.0 General"
        assert iotnightly.sorttuple == (33, 800, Decimal("20200513.0"), "General")
        assert iotnightly.seedtext == (
            "{{subst:IoT validation results|testtype=General|release=33|milestone=RC"
            "|date=20200513.0}}"
        )

    def test_results_sections(self, fakeapisections):
        """Test the results_sections property."""
        # we aren"t using fakepages here so this doesn"t really matter
        # but let's stay consistent. we use fakeapisections not
        # fakepages as it's easier to adjust the return value
        page = wikitcms.page.NightlyPage(self.site, "32", "Server", "Branched", "20200322.n.0")
        assert [sec["line"] for sec in page.results_sections] == [
            "<b>Test Matrix</b>",
            "General tests",
            "FreeIPA server installation and functionality tests",
            "Domain joining tests: <b>FreeIPA</b>",
            "Domain joining tests: <b>Active Directory</b>",
            "Domain client tests",
            "PostgreSQL server installation and functionality tests",
            "Upgrade tests",
        ]
        # the code has a special case for handling a case where we
        # don"t positively find a first result section but do find a
        # section named "Key", but I don"t remember what that's for
        # and can"t find a real example (the oldest page we handle,
        # Test_Results:Fedora_12_Alpha_RC1_Install , has a
        # "Test Matrix" section), so let's make one up by dropping
        # the "Test Matrix" section from our test data
        del fakeapisections.return_value["parse"]["sections"][5]
        assert [sec["line"] for sec in page.results_sections] == [
            "General tests",
            "FreeIPA server installation and functionality tests",
            "Domain joining tests: <b>FreeIPA</b>",
            "Domain joining tests: <b>Active Directory</b>",
            "Domain client tests",
            "PostgreSQL server installation and functionality tests",
            "Upgrade tests",
        ]

    def test_get_resultrows(self, fakepages):
        """Test the get_resultrows() method."""
        # use one of the pages supported by "fakepages"
        page = wikitcms.page.NightlyPage(self.site, "32", "Server", "Branched", "20200322.n.0")
        rrows = page.get_resultrows()
        assert len(rrows) == 26
        # just sample a couple of rows
        assert rrows[0].testcase == "QA:Testcase_kickstart_firewall_disabled"
        assert rrows[13].name == "QA:Testcase_realmd_join_kickstart"
        assert rrows[25].secid == "8"

    def test_find_resultrow(self, fakepages):
        """Test find_resultrow() method, including various awkward
        cases.
        """
        page = wikitcms.page.NightlyPage(self.site, "32", "Server", "Branched", "20200322.n.0")
        # simple case: one row found by test case
        row = page.find_resultrow(testcase="QA:Testcase_kickstart_firewall_disabled")
        assert row.testcase == "QA:Testcase_kickstart_firewall_disabled"
        assert row.secid == "2"
        # should raise TooManyError for test case found more than once
        # with different names
        with pytest.raises(wikitcms.exceptions.TooManyError):
            row = page.find_resultrow(testcase="QA:Testcase_domain_client_authenticate")
        # ...but if we give a name, should be fine
        row = page.find_resultrow(
            testcase="QA:Testcase_domain_client_authenticate", testname="FreeIPA"
        )
        # and in fact just searching on the name should also work, if
        # we give the *exact* name
        rowagain = page.find_resultrow(testname="(FreeIPA)")
        assert rowagain.matches(row)
        # should raise TooManyError for test case found more than once
        # with different sections
        with pytest.raises(wikitcms.exceptions.TooManyError):
            row = page.find_resultrow(testcase="QA:Testcase_realmd_join_kickstart")
        # ...but if we give section, should be fine
        row = page.find_resultrow(testcase="QA:Testcase_realmd_join_kickstart", section="FreeIPA")
        # should raise NotFoundError if we find nothing
        with pytest.raises(wikitcms.exceptions.NotFoundError):
            row = page.find_resultrow(testcase="QA:Testcase_non_existent")
        # test case where 2+ test cases have the search string in them
        # but one matches it exactly; we should find that row and not
        # raise TooManyError or anything
        row = page.find_resultrow(testcase="QA:Testcase_freeipa_replication")
        assert row.testcase == "QA:Testcase_freeipa_replication"
        # similar case for section names, see
        # https://pagure.io/fedora-qa/python-wikitcms/issue/4
        page = wikitcms.page.NightlyPage(self.site, "32", "Desktop", "Branched", "20200322.n.0")
        row = page.find_resultrow(
            testcase="QA:Testcase_audio_basic",
            section="Release-blocking desktops: <b>x86 / x86_64</b>",
        )
        assert row.testcase == "QA:Testcase_audio_basic"
        assert row.secid == "2"
        assert row.section == "Release-blocking desktops: <b>x86 / x86_64</b>"
        # similar, but relying on non-normalized rather than exact
        # name matching: as we use a lower-case "r" we expect to find
        # the row in the "Non release-blocking" section
        row = page.find_resultrow(
            testcase="QA:Testcase_audio_basic", section="release-blocking desktops: <b>x86"
        )
        assert row.testcase == "QA:Testcase_audio_basic"
        assert row.secid == "4"
        assert row.section == "Non release-blocking desktops: <b>x86 / x86_64</b>"

    @mock.patch("mwclient.page.Page.save", autospec=True)
    def test_update_current(self, fakesave):
        """Test for update_current() method."""
        page = wikitcms.page.NightlyPage(self.site, "32", "Server", "Branched", "20200322.n.0")
        page.update_current()
        assert fakesave.call_count == 1
        args = fakesave.call_args[0]
        # this is the Page instance itself
        assert args[0].name == "Test Results:Current Server Test"
        assert args[1] == "#REDIRECT [[Test Results:Fedora 32 Branched 20200322.n.0 Server]]"
        assert args[2] == "relval: update to current event"

        # now check modular case
        page = wikitcms.page.ComposePage(
            self.site, "32", "Server", "Beta", "1.1", dist="Fedora-Modular"
        )
        page.update_current()
        assert fakesave.call_count == 2
        args = fakesave.call_args[0]
        # this is the Page instance itself
        assert args[0].name == "Test Results:Current Modular Server Test"
        assert args[1] == "#REDIRECT [[Test Results:Fedora-Modular 32 Beta 1.1 Server]]"
        assert args[2] == "relval: update to current event"

        # IoT case
        page = wikitcms.page.NightlyPage(
            self.site, "33", "General", "RC", "20200513.0", dist="Fedora-IoT"
        )
        page.update_current()
        assert fakesave.call_count == 3
        args = fakesave.call_args[0]
        # this is the Page instance itself
        assert args[0].name == "Test Results:Current IoT General Test"
        assert args[1] == "#REDIRECT [[Test Results:Fedora-IoT 33 RC 20200513.0 General]]"
        assert args[2] == "relval: update to current event"


@pytest.mark.usefixtures("fakemwp", "fakepages")
class TestAddResults:
    """Tests for ValidationPage.add_results() method. Is its own class
    so these tests can share some stuff.
    """

    @pytest.fixture(autouse=True)
    def common_setup(self, request, fakemwp, fakepages):
        """This seems like a kinda baroque way to do things, but the
        problem is we need to use the fakemwp and fakepages fixtures
        *in this code*, and I can"t figure a way to do that while just
        setting these things up as class attributes as we ordinarily
        would. This autouse fixture which sets attributes on the
        request class seems to work instead...
        """
        us = request.cls
        us.site = wikitcms.wiki.Wiki("fjajah", do_init=False, force_login=False)
        us.page = wikitcms.page.NightlyPage(us.site, "32", "Server", "Branched", "20200322.n.0")
        us.text = us.page.text()
        us.row = us.page.find_resultrow(testcase="QA:Testcase_kickstart_firewall_disabled")
        us.row2 = us.page.find_resultrow(testcase="QA:Testcase_FreeIPA_realmd_login")
        us.passed = wikitcms.result.Result("pass", "wikitcms")
        us.failed = wikitcms.result.Result("fail", "wikitcms")

    @mock.patch("mwclient.page.Page.save", autospec=True)
    def test_add_results_simple(self, fakesave, fakepages):
        """Simple one result test."""
        # pylint: disable=no-member
        ret = self.page.add_results({self.row: [("x86_64", self.passed)]})
        # should be no dupes
        assert ret == []
        assert fakesave.call_count == 1
        # summary
        expsumm = "Result(s) for test(s): QA:Testcase_kickstart_firewall_disabled filed via relval"
        assert fakesave.call_args[0][2] == expsumm
        expdiff = [
            (13, "- | {{result|pass|coconut|bot=true}}"),
            (14, "+ | {{result|pass|coconut|bot=true}}{{result|pass|wikitcms}}"),
        ]
        assert _diff(self.text, fakesave.call_args[0][1]) == expdiff

    @mock.patch("mwclient.page.Page.save", autospec=True)
    def test_add_results_multiple(self, fakesave, fakepages):
        """Multiple result test. Also tests overwriting
        {{result|none}}.
        """
        # pylint: disable=no-member
        ret = self.page.add_results({self.row: [("x86_64", self.passed), ("aarch64", self.failed)]})
        assert ret == []
        assert fakesave.call_count == 1
        expsumm = "Result(s) for test(s): QA:Testcase_kickstart_firewall_disabled filed via relval"
        assert fakesave.call_args[0][2] == expsumm
        expdiff = [
            (13, "- | {{result|pass|coconut|bot=true}}"),
            (14, "- | {{result|none}}"),
            (15, "+ | {{result|pass|coconut|bot=true}}{{result|pass|wikitcms}}"),
            (16, "+ | {{result|fail|wikitcms}}"),
        ]
        assert _diff(self.text, fakesave.call_args[0][1]) == expdiff

    @mock.patch("mwclient.page.Page.save", autospec=True)
    def test_add_results_multiple_row(self, fakesave, fakepages):
        """Multiple row, different sections test."""
        # pylint: disable=no-member
        ret = self.page.add_results(
            {self.row: [("x86_64", self.passed)], self.row2: [("Result", self.failed)]}
        )
        assert ret == []
        assert fakesave.call_count == 1
        # the ordering of test cases in the summary is reversed as we
        # reverse the dict to ensure editing accuracy...
        expsumm = (
            "Result(s) for test(s): QA:Testcase_FreeIPA_realmd_login, "
            "QA:Testcase_kickstart_firewall_disabled filed via relval"
        )
        assert fakesave.call_args[0][2] == expsumm
        expdiff = [
            (13, "- | {{result|pass|coconut|bot=true}}"),
            (14, "+ | {{result|pass|coconut|bot=true}}{{result|pass|wikitcms}}"),
            (139, "- | {{result|pass|coconut|bot=true}}"),
            (140, "+ | {{result|pass|coconut|bot=true}}{{result|fail|wikitcms}}"),
        ]
        assert _diff(self.text, fakesave.call_args[0][1]) == expdiff

    @mock.patch("mwclient.page.Page.save", autospec=True)
    def test_add_results_single_env(self, fakesave, fakepages):
        """If there's only one env, we use it even if the passed env
        doesn"t match at all (this is an arguable choice but it's what
        we"ve done for years...)
        """
        # pylint: disable=no-member
        self.page.add_results({self.row2: [("bananas", self.passed)]})
        assert fakesave.call_count == 1
        expsumm = "Result(s) for test(s): QA:Testcase_FreeIPA_realmd_login filed via relval"
        assert fakesave.call_args[0][2] == expsumm
        expdiff = [
            (138, "- | {{result|pass|coconut|bot=true}}"),
            (139, "+ | {{result|pass|coconut|bot=true}}{{result|pass|wikitcms}}"),
        ]
        assert _diff(self.text, fakesave.call_args[0][1]) == expdiff

    @mock.patch("mwclient.page.Page.save", autospec=True)
    def test_add_results_incomplete_env(self, fakesave, fakepages):
        """An incomplete env string match is expected to work if it is
        unique.
        """
        # pylint: disable=no-member
        ret = self.page.add_results({self.row: [("x86", self.passed)]})
        assert ret == []
        assert fakesave.call_count == 1
        # summary
        expsumm = "Result(s) for test(s): QA:Testcase_kickstart_firewall_disabled filed via relval"
        assert fakesave.call_args[0][2] == expsumm
        expdiff = [
            (13, "- | {{result|pass|coconut|bot=true}}"),
            (14, "+ | {{result|pass|coconut|bot=true}}{{result|pass|wikitcms}}"),
        ]
        assert _diff(self.text, fakesave.call_args[0][1]) == expdiff

    @mock.patch("mwclient.page.Page.save", autospec=True)
    def test_add_results_incomplete_dupes(self, fakesave, fakepages):
        """Duplicate submissions (when we have a result in same cell
        from same reporter) should be returned, as a list of tuples
        (row, env, Result) where the Result is the *submitted* result
        not the existing one.
        """
        # pylint: disable=no-member
        cocores = wikitcms.result.Result("fail", "coconut", bot=True)
        ret = self.page.add_results(
            {
                self.row: [("x86_64", cocores), ("x86_64", self.passed)],
                self.row2: [("Result", cocores)],
            }
        )
        # reversed, as results dict is reversed by add_results...
        assert ret == [(self.row2, "Result", cocores), (self.row, "x86_64", cocores)]
        # the row we didn't touch as we only had dupe results should be
        # left out of the summary text
        expsumm = "Result(s) for test(s): QA:Testcase_kickstart_firewall_disabled filed via relval"
        assert fakesave.call_args[0][2] == expsumm
        # the dupe results should *not* be posted
        expdiff = [
            (13, "- | {{result|pass|coconut|bot=true}}"),
            (14, "+ | {{result|pass|coconut|bot=true}}{{result|pass|wikitcms}}"),
        ]
        assert _diff(self.text, fakesave.call_args[0][1]) == expdiff

        # now check with allowdupe=True
        ret = self.page.add_results(
            {
                self.row: [("x86_64", cocores), ("x86_64", self.passed)],
                self.row2: [("Result", cocores)],
            },
            allowdupe=True,
        )
        assert ret == []
        expsumm = (
            "Result(s) for test(s): QA:Testcase_FreeIPA_realmd_login, "
            "QA:Testcase_kickstart_firewall_disabled filed via relval"
        )
        assert fakesave.call_args[0][2] == expsumm
        expdiff = [
            (13, "- | {{result|pass|coconut|bot=true}}"),
            (
                14,
                "+ | {{result|pass|coconut|bot=true}}"
                "{{result|fail|coconut|bot=true}}{{result|pass|wikitcms}}",
            ),
            (139, "- | {{result|pass|coconut|bot=true}}"),
            (140, "+ | {{result|pass|coconut|bot=true}}{{result|fail|coconut|bot=true}}"),
        ]
        assert _diff(self.text, fakesave.call_args[0][1]) == expdiff

    @mock.patch("mwclient.page.Page.save", autospec=True)
    def test_add_results_ellipsization(self, fakesave, fakepages):
        """Test the summary ellipsization when more than three test
        cases have results.
        """
        # pylint: disable=no-member
        row3 = self.page.find_resultrow(testcase="QA:Testcase_postgresql_server_installation")
        row4 = self.page.find_resultrow(
            testcase="QA:Testcase_upgrade_dnf_current_server_domain_controller"
        )
        ret = self.page.add_results(
            {
                self.row: [("x86_64", self.passed)],
                self.row2: [("Result", self.passed)],
                row3: [("x86_64", self.passed)],
                row4: [("x86_64", self.passed)],
            }
        )
        assert ret == []
        # Reverse order again...
        expsumm = (
            "Result(s) for test(s): QA:Testcase_upgrade_dnf_current_server_domain_"
            "controller, QA:Testcase_postgresql_server_installation, "
            "QA:Testcase_FreeIPA_realmd_login... filed via relval"
        )
        assert fakesave.call_args[0][2] == expsumm

    @mock.patch("mwclient.page.Page.save", autospec=True)
    def test_add_result(self, fakesave, fakepages):
        """As add_result is just a thin wrapper for add_results (to
        retain backward compatibility from before we added multiple
        simultaneous result submission), let's test it here.
        """
        # pylint: disable=no-member
        # this does the same as test_add_results_simple
        ret = self.page.add_result(self.passed, self.row, "x86_64")
        # should be no dupes
        assert ret == []
        assert fakesave.call_count == 1
        # summary
        expsumm = "Result(s) for test(s): QA:Testcase_kickstart_firewall_disabled filed via relval"
        assert fakesave.call_args[0][2] == expsumm
        expdiff = [
            (13, "- | {{result|pass|coconut|bot=true}}"),
            (14, "+ | {{result|pass|coconut|bot=true}}{{result|pass|wikitcms}}"),
        ]
        assert _diff(self.text, fakesave.call_args[0][1]) == expdiff


@pytest.mark.usefixtures("fakemwp")
class TestSummaryPage:
    """Test for the SummaryPage class."""

    @mock.patch("fedfind.release.Compose.exists", True)
    @mock.patch("fedfind.release.Compose.all_images", ["foo"])
    @mock.patch("wikitcms.wiki.Wiki.get_testtypes", return_value=["Installation", "Base"])
    @mock.patch("mwclient.page.Page.save", autospec=True)
    def test_summary_page(self, fakesave, fakeget):
        """General tests for SummaryPage. It's a simple class."""
        site = wikitcms.wiki.Wiki("fjajah", do_init=False, force_login=False)
        event = wikitcms.event.ComposeEvent(site, "32", "Beta", "1.2", cid="Fedora-32-20200312.0")
        summ = event.summary_page
        assert isinstance(summ, wikitcms.page.SummaryPage)
        assert summ.checkname == "Test Results:Fedora 32 Beta 1.2 Summary"
        # checking the summary summary, like whoah, dude
        assert summ.summary == (
            "Relval bot-created validation results summary for " "Fedora 32 Beta 1.2"
        )
        assert summ.seedtext == (
            "Fedora 32 Beta 1.2 [[QA:Release validation test plan|release "
            "validation]] summary. This page shows the results from all the "
            "individual result pages for this compose together. You can file "
            "results directly from this page and they will be saved into the "
            "correct individual result page. To see test instructions, visit "
            "any of the individual pages (the section titles are links). You "
            "can find download links below.\n\n__TOC__\n\n== Downloads ==\n{{"
            "Fedora 32 Beta 1.2 Download}}\n\n== [[Test Results:Fedora 32 Beta 1.2 Installation|"
            "Installation]] ==\n{{Test Results:Fedora 32 Beta 1.2 Installation}}\n\n== "
            "[[Test Results:Fedora 32 Beta 1.2 Base|Base]] ==\n{{Test Results:Fedora 32 Beta 1.2 "
            "Base}}\n\n[[Category:Fedora 32 Beta Test Results|Summary]]"
        )
        summ.update_current()
        assert fakesave.call_count == 1
        args = fakesave.call_args[0]
        # this is the Page instance itself
        assert args[0].name == "Test Results:Current Summary"
        assert args[1] == "#REDIRECT [[Test Results:Fedora 32 Beta 1.2 Summary]]"
        assert args[2] == "relval: update to current event"
        fakesave.reset_mock()

        # modular checks
        modevent = wikitcms.event.ComposeEvent(
            site, "27", "Beta", "1.5", cid="Fedora-Modular-27-20171108.2", dist="Fedora-Modular"
        )
        summ = modevent.summary_page
        assert isinstance(summ, wikitcms.page.SummaryPage)
        assert summ.checkname == "Test Results:Fedora-Modular 27 Beta 1.5 Summary"
        assert summ.summary == (
            "Relval bot-created validation results summary for Fedora-Modular 27 Beta 1.5"
        )
        # let's not test the whole goddamned thing again
        assert summ.seedtext.startswith("Fedora-Modular 27 Beta 1.5 [[")
        summ.update_current()
        assert fakesave.call_count == 1
        args = fakesave.call_args[0]
        # this is the Page instance itself
        assert args[0].name == "Test Results:Current Modular Summary"
        assert args[1] == "#REDIRECT [[Test Results:Fedora-Modular 27 Beta 1.5 Summary]]"
        assert args[2] == "relval: update to current event"
        fakesave.reset_mock()

        # IoT checks
        iotevent = wikitcms.event.NightlyEvent(site, "33", "RC", "20200513.0", dist="Fedora-IoT")
        summ = iotevent.summary_page
        assert isinstance(summ, wikitcms.page.SummaryPage)
        assert summ.checkname == "Test Results:Fedora-IoT 33 RC 20200513.0 Summary"
        assert summ.summary == (
            "Relval bot-created validation results summary for Fedora-IoT 33 RC 20200513.0"
        )
        # let's not test the whole goddamned thing again
        assert summ.seedtext.startswith("Fedora-IoT 33 RC 20200513.0 [[")
        summ.update_current()
        assert fakesave.call_count == 1
        args = fakesave.call_args[0]
        # this is the Page instance itself
        assert args[0].name == "Test Results:Current IoT Summary"
        assert args[1] == "#REDIRECT [[Test Results:Fedora-IoT 33 RC 20200513.0 Summary]]"
        assert args[2] == "relval: update to current event"
        fakesave.reset_mock()


@pytest.mark.usefixtures("fakemwp", "fakepages", "fakeimages")
class TestDownloadPage:
    """Tests for the DownloadPage class."""

    # we have to patch these to avoid network round trips in fedfind
    @mock.patch("fedfind.release.Compose.cid", "Fedora-32-20200312.0")
    @mock.patch("fedfind.release.Compose.exists", True)
    def test_download_page(self):
        """Test for DownloadPage. It's pretty hard to break this down
        into unit tests, given how it works, so we just test it all at
        once: we run it on the real data from a real compose, and
        check the output matches what we expect.
        """
        site = wikitcms.wiki.Wiki("fjajah", do_init=False, force_login=False)
        event = wikitcms.event.ComposeEvent(site, "32", "Beta", "1.2", cid="Fedora-32-20200312.0")
        page = event.download_page
        assert page.checkname == "Template:Fedora 32 Beta 1.2 Download"
        assert page.summary == "Relval bot-created download page for Fedora 32 Beta 1.2"
        assert page.event is event
        # seedtext is very long so we stash the expected value in a
        # file and read it here
        exptextpath = os.path.join(DATAPATH, "Template:Fedora 32 Beta 1.2 Download.seedtext")
        with open(exptextpath, "r") as exptextfh:
            exptext = exptextfh.read()
        assert page.seedtext == exptext

        # modular checks
        modevent = wikitcms.event.ComposeEvent(
            site, "27", "Beta", "1.5", cid="Fedora-Modular-27-20171108.2", dist="Fedora-Modular"
        )
        page = modevent.download_page
        assert page.checkname == "Template:Fedora-Modular 27 Beta 1.5 Download"
        assert page.summary == "Relval bot-created download page for Fedora-Modular 27 Beta 1.5"
        # that's all we need to check for modular

        # IoT checks
        iotevent = wikitcms.event.NightlyEvent(site, "33", "RC", "20200513.0", dist="Fedora-IoT")
        page = iotevent.download_page
        assert page.checkname == "Template:Fedora-IoT 33 RC 20200513.0 Download"
        assert page.summary == "Relval bot-created download page for Fedora-IoT 33 RC 20200513.0"
        # that's all we need to check for IoT


@pytest.mark.usefixtures("fakemwp", "fakepages", "fakeimages")
class TestAMIPage:
    """Tests for the AMIPage class."""

    # we have to patch these to avoid network round trips in fedfind
    @mock.patch("fedfind.release.Compose.cid", "Fedora-32-20200312.0")
    @mock.patch("fedfind.release.Compose.exists", True)
    def test_ami_page(self):
        """Test for AMIPage. As with DownloadPage, it's hard to split
        this into unit tests, so we feed in real world data (more or
        less) and check the output is as expected.
        """
        site = wikitcms.wiki.Wiki("fjajah", do_init=False, force_login=False)
        event = wikitcms.event.ComposeEvent(site, "32", "Beta", "1.2", cid="Fedora-32-20200312.0")
        page = event.ami_page
        assert page.checkname == "Template:Fedora 32 Beta 1.2 AMI"
        assert page.summary == "Relval bot-created AMI page for Fedora 32 Beta 1.2"
        assert page.event is event

        def fakedownloadjson(url):
            """Mock for fedfind.helpers.download_json to fake up a
            datagrepper query response used to find the AMIs. The data
            that backs this is close to but not quite 'real' data -
            it's the real message dicts only of the messages that were
            actually for this compose, plus *one* message that wasn't
            (to test that filtering those out works), with the headers
            and most of the additional data in the query response
            dropped. The *real* real data for the relevant two days
            is like 25 pages long, so we had to filter it. We hack up
            splitting it across two 'pages' to test the pagination
            handling.
            """
            page = 1
            if "page=2" in url:
                # dumb but enough
                page = 2
            path = os.path.join(DATAPATH, "Fedora-32-20200312.0.ami.dgdata.{0}.json".format(page))
            with open(path, "r") as amifh:
                amidata = json.load(amifh)
            return amidata

        # again, read expected seedtext from a file
        exptextpath = os.path.join(DATAPATH, "Template:Fedora 32 Beta 1.2 AMI.seedtext")
        with open(exptextpath, "r") as exptextfh:
            exptext = exptextfh.read()
        with mock.patch("fedfind.helpers.download_json", fakedownloadjson):
            assert page.seedtext == exptext


@pytest.mark.usefixtures("fakemwp")
class TestTestDayPage:
    """Tests for the TestDayPage class."""

    def test_init(self):
        """Tests for basic __init__ stuff."""
        site = wikitcms.wiki.Wiki("fjajah", do_init=False, force_login=False)
        page = wikitcms.page.TestDayPage(site, "2020-03-20", "Cloud Testday")
        assert page.checkname == "Test Day:2020-03-20 Cloud Testday"
        assert page.date == "2020-03-20"
        assert page.subject == "Cloud Testday"
        assert page.results_separators == ("Test Results", "Results")

    def test_bugs(self, fakepages):
        """Tests for the bugs() property."""
        # this page uses the bugs-in-results-template style
        site = wikitcms.wiki.Wiki("fjajah", do_init=False, force_login=False)
        page = wikitcms.page.TestDayPage(site, "2013-11-05", "Printing")
        assert page.bugs == ["1026909", "1026914", "1026928", "1026940", "1026949", "1027425"]
        # this one uses the app-generated bugs-as-references style
        # and has some direct Bugzilla URLs also, also has lots of
        # duplication between entries
        page = wikitcms.page.TestDayPage(site, "2016-10-24", "Cloud")
        assert page.bugs == ["1384150", "1387934", "1388000"]

    @mock.patch("mwclient.page.Page.save", autospec=True)
    def test_fix_app_results(self, fakesave, fakepages):
        """Test for fix_app_results."""
        site = wikitcms.wiki.Wiki("fjajah", do_init=False, force_login=False)
        page = wikitcms.page.TestDayPage(site, "2016-10-24", "Cloud")
        page.fix_app_results()
        assert fakesave.call_count == 1
        args = fakesave.call_args[0]
        kwargs = fakesave.call_args[1]
        assert kwargs["summary"] == (
            "Fix testday app-generated results to use " "{{result}} template for bug references"
        )
        # FIXME: we actually miss several conversions here as we do not
        # handle {{bz}} and comment text mixed up in a single ref tag
        # FIXME 2: I even had to cheat and edit the text of the page
        # slightly as there's a stray space between the end of the
        # template and the closing </ref>
        assert args[1] == page.text().replace(
            "{{result|fail}}<ref>{{bz|1388000}}</ref>", "{{result|fail||1388000}}"
        )

    @mock.patch("mwclient.page.Page.save", autospec=True)
    def test_long_refs(self, fakesave, fakepages):
        """Test for long_refs."""
        site = wikitcms.wiki.Wiki("fjajah", do_init=False, force_login=False)
        page = wikitcms.page.TestDayPage(site, "2016-10-24", "Cloud")
        page.long_refs()
        # read expected  modified text from a file, it's too long to
        # inline
        exptextpath = os.path.join(DATAPATH, "Test_Day:2016-10-24_Cloud.longrefs.txt")
        with open(exptextpath, "r") as exptextfh:
            exptext = exptextfh.read()
        assert fakesave.call_args[0][1] == exptext
        # summary
        assert fakesave.call_args[1]["summary"] == (
            "Move long comments to a separate " "section at end of page"
        )
