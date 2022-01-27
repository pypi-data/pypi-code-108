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
# pylint: disable=too-few-public-methods

"""Tests for wiki.py."""

from unittest import mock

import openidc_client
import openidc_client.requestsauth
import pytest

import wikitcms.wiki as wk
import wikitcms.event
import wikitcms.result

FAKE_CURRENT_COMPOSE = """{{tempdoc}}
<onlyinclude>{{#switch: {{{1|full}}}
| full = 24 Alpha 1.1
| release = 24
| milestone = Alpha
| compose = 1.1
| date =
}}</onlyinclude>
[[Category: Fedora Templates]]
"""


class FakeRow:
    """This is a very bare fake ResultRow class; we need it to fully
    test report_validation_results, can't really do it with Mocks. We
    use mock to replace the 'real' page.find_resultrow method with the
    fake_findrow method below, which returns instances of this class.
    """

    def __init__(self, name):
        self.name = name

    def matches(self, other):
        """Simple matches replacement."""
        return self.name == other.name


def fake_findrow(self, testcase="", section="", testname="", env=""):
    """This is a fake find_resultrow function which just returns
    FakeRows based on the values it's given. We use mock to replace
    Page instances' find_resultrow methods with this, further down.
    Note we're simulating a case where the found row covers both
    reported envs here; find_resultrow can also cover a case where
    there are two rows with equal case, section and name but each
    covering different envs, but we'll test that in its own test.
    """
    name = ".".join((testcase, section, testname))
    return FakeRow(name)


def fake_pginit1(self, site, release, testtype, milestone, compose, info=None, dist="Fedora"):
    """Fake page.__init__ for testing get_validation_page guessing.
    This one gives us pages that 'exist' if they're Rawhide and don't
    otherwise.
    """
    self.milestone = milestone
    if milestone == "Rawhide":
        self.exists = True
    else:
        self.exists = False


def fake_pginit2(self, site, release, testtype, milestone, compose, info=None, dist="Fedora"):
    """Fake page.__init__ for testing get_validation_page guessing.
    This one gives us pages that 'exist' if they're Branched and don't
    otherwise.
    """
    self.milestone = milestone
    if milestone == "Branched":
        self.exists = True
    else:
        self.exists = False


def fake_pginit3(self, site, release, testtype, milestone, compose, info=None, dist="Fedora"):
    """Fake page.__init__ for testing get_validation_page guessing.
    This one just never exists.
    """
    self.exists = False


class TestWiki:
    """Tests for the functions in wiki.py."""

    # the 'fjajah' is just to make sure we're running offline; if I
    # screw up and add a test that hits the network it'll cause the
    # tests to hang/fail instead of succeeding a bit slower
    site = wk.Wiki("fjajah", do_init=False, force_login=False)

    @mock.patch("mwclient.page.Page.__init__", return_value=None)
    @mock.patch("mwclient.page.Page.text", return_value=FAKE_CURRENT_COMPOSE)
    def test_current_compose(self, faketext, fakeinit):
        """Tests for current_compose and current_modular_compose."""
        assert self.site.current_compose == {
            "full": "24 Alpha 1.1",
            "release": "24",
            "milestone": "Alpha",
            "compose": "1.1",
            "date": "",
        }
        assert self.site.current_modular_compose == {
            "full": "24 Alpha 1.1",
            "release": "24",
            "milestone": "Alpha",
            "compose": "1.1",
            "date": "",
        }

    @mock.patch("mwclient.page.Page.__init__", return_value=None)
    @mock.patch("mwclient.page.Page.text", return_value=FAKE_CURRENT_COMPOSE)
    @mock.patch("wikitcms.wiki.Wiki.get_validation_event", autospec=True)
    def test_current_event(self, fakeget, faketext, fakeinit):
        """Tests for current_event and current_modular_event."""
        _ = self.site.current_event
        fakeget.assert_called_with(
            mock.ANY, compose="1.1", milestone="Alpha", release="24", dist="Fedora"
        )
        fakeget.reset_mock()
        _ = self.site.current_modular_event
        fakeget.assert_called_with(
            mock.ANY, compose="1.1", milestone="Alpha", release="24", dist="Fedora-Modular"
        )

    @mock.patch("mwclient.page.Page.__init__", return_value=None)
    @mock.patch("mwclient.page.Page.text", return_value="foobar")
    @mock.patch("mwclient.page.Page.save")
    def test_add_to_category(self, fakesave, faketext, fakeinit):
        """Test for add_to_category."""
        self.site.add_to_category("Foobar", "Category:Some category", "summary")
        fakesave.assert_called_with(
            "foobar\n[[Category:Some category]]", "summary", createonly=False
        )
        # now check case where page is already in the category
        faketext.return_value = "foobar\n[[Category:Some category]]"
        fakesave.reset_mock()
        self.site.add_to_category("Foobar", "Category:Some category", "summary")
        # we should return without calling save
        assert fakesave.call_count == 0

    def test_walk_category(self, fakemwp):
        """Test for walk_category."""
        # we have to mock up a whole nested category structure here
        # we're gonna walk 'fakecat1', which contains two regular
        # pages and 'fakecat2', which contains another regular page
        fakecat1 = self.site.pages["Category:Somecat"]
        fakecat1.namespace = 14
        fakecat2 = self.site.pages["Category:Someothercat"]
        fakecat1.namespace = fakecat2.namespace = 14
        fakepg1 = self.site.pages["Somepage1"]
        fakepg2 = self.site.pages["Somepage2"]
        fakepg3 = self.site.pages["Somepage3"]
        fakepg1.namespace = fakepg2.namespace = fakepg3.namespace = 1
        # this isn't really a perfect test, but it's the best I can
        # come up with for now
        with mock.patch("mwclient.listing.GeneratorList.__next__") as fakenext:
            fakenext.side_effect = [fakepg1, fakepg2, fakecat2, fakepg3]
            assert list(self.site.walk_category(fakecat1)) == [fakepg1, fakepg2, fakepg3]

    @mock.patch("fedfind.release.Compose.exists", return_value=True)
    @mock.patch("fedfind.release.IoTNightly.label", "RC-20200513.0")
    @mock.patch("fedfind.release.IoTNightly.cid", "Fedora-IoT-33-20200513.0")
    @mock.patch("fedfind.release.Production.label", "RC-1.6")
    @mock.patch("fedfind.release.Production.cid", "Fedora-27-20171105.0")
    @mock.patch("fedfind.helpers.get_current_release", autospec=True, return_value=27)
    @mock.patch("mwclient.page.Page.__init__", return_value=None)
    @mock.patch("mwclient.page.Page.text", return_value=FAKE_CURRENT_COMPOSE)
    @mock.patch("wikitcms.event.NightlyEvent", autospec=True)
    @mock.patch("wikitcms.event.ComposeEvent", autospec=True)
    def test_get_validation_event(
        self, fakecompose, fakenightly, faketext, fakeinit, fakegetcurr, fakecompexists
    ):
        """Various tests for get_validation_event."""
        # current event
        self.site.get_validation_event()
        fakecompose.assert_called_with(self.site, "24", "Alpha", "1.1", dist="Fedora", cid="")
        self.site.get_validation_event(dist="Fedora-Modular")
        fakecompose.assert_called_with(
            self.site, "24", "Alpha", "1.1", dist="Fedora-Modular", cid=""
        )
        # old-school TC/RC
        self.site.get_validation_event(23, "Final", "TC9")
        fakecompose.assert_called_with(self.site, 23, "Final", "TC9", dist="Fedora", cid="")
        self.site.get_validation_event(23, "Beta", "RC1")
        fakecompose.assert_called_with(self.site, 23, "Beta", "RC1", dist="Fedora", cid="")
        # old-school nightly
        self.site.get_validation_event(23, "Rawhide", "20151112")
        fakenightly.assert_called_with(
            self.site, release=23, milestone="Rawhide", compose="20151112", dist="Fedora"
        )
        self.site.get_validation_event(23, "Branched", "20151211", dist="Fedora")
        fakenightly.assert_called_with(
            self.site, release=23, milestone="Branched", compose="20151211", dist="Fedora"
        )
        # Pungi 4 production/candidate
        self.site.get_validation_event(24, "Alpha", "1.1")
        fakecompose.assert_called_with(self.site, 24, "Alpha", "1.1", dist="Fedora", cid="")
        self.site.get_validation_event(27, "Beta", "1.5", dist="Fedora-Modular")
        fakecompose.assert_called_with(self.site, 27, "Beta", "1.5", dist="Fedora-Modular", cid="")
        # Past 23, 'Final' milestone should be converted to 'RC'
        self.site.get_validation_event(25, "Final", "1.1")
        fakecompose.assert_called_with(self.site, 25, "RC", "1.1", dist="Fedora", cid="")
        # Pungi 4 nightly
        self.site.get_validation_event(24, "Rawhide", "20160222.n.0")
        fakenightly.assert_called_with(
            self.site, release=24, milestone="Rawhide", compose="20160222.n.0", dist="Fedora"
        )
        self.site.get_validation_event(24, "Branched", "20160315.n.1")
        fakenightly.assert_called_with(
            self.site, release=24, milestone="Branched", compose="20160315.n.1", dist="Fedora"
        )
        self.site.get_validation_event(27, "Branched", "20171110.n.1", dist="Fedora-Modular")
        fakenightly.assert_called_with(
            self.site,
            release=27,
            milestone="Branched",
            compose="20171110.n.1",
            dist="Fedora-Modular",
        )
        # Rawhide nightly compose ID
        self.site.get_validation_event(cid="Fedora-Rawhide-20180220.n.0", dist="Fedora")
        fakenightly.assert_called_with(
            self.site, release="28", milestone="Rawhide", compose="20180220.n.0", dist="Fedora"
        )
        # Branched nightly compose ID
        self.site.get_validation_event(cid="Fedora-27-20171120.n.0", dist="Fedora")
        fakenightly.assert_called_with(
            self.site, release="27", milestone="Branched", compose="20171120.n.0", dist="Fedora"
        )
        # Candidate compose ID (note compose ID passthrough)
        self.site.get_validation_event(cid="Fedora-27-20171105.0", dist="Fedora")
        fakecompose.assert_called_with(
            self.site, "27", "RC", "1.6", dist="Fedora", cid="Fedora-27-20171105.0"
        )
        # IoT compose: these are technically productions but quack and
        # walk like nightlies, with dates in the labels; we intend to
        # treat them as nightlies and create nightly events
        fakegetcurr.return_value = 32
        self.site.get_validation_event(cid="Fedora-IoT-33-20200513.0", dist="Fedora-IoT")
        fakenightly.assert_called_with(self.site, "33", "RC", "20200513.0", dist="Fedora-IoT")

        with pytest.raises(ValueError):
            # Non-nightly compose but no milestone
            self.site.get_validation_event(24, "", "1.1")
        # Invalid composes
        with pytest.raises(ValueError):
            self.site.get_validation_event(24, "Branched", "foobar")
        with pytest.raises(ValueError):
            self.site.get_validation_event(24, "Branched", "TC1a")
        with pytest.raises(ValueError):
            self.site.get_validation_event(24, "Branched", "1.1a")
        # looks kinda like a date but is not one
        with pytest.raises(ValueError):
            self.site.get_validation_event(24, "Branched", "20161356")
        with pytest.raises(ValueError):
            self.site.get_validation_event(24, "Branched", "20161356.n.0")
        with pytest.raises(ValueError):
            # invalid type
            self.site.get_validation_event(24, "Branched", "20160314.x.0")

    @mock.patch("wikitcms.wiki.Wiki.allresults")
    @mock.patch("mwclient.page.Page.text", return_value="foobar")
    def test_get_validation_event_guess_nightly(self, faketext, fakeresults, fakemwp):
        """Test get_validation_event guessing milestone for nightly
        events.
        """
        fakepage = self.site.pages["Test Results:Fedora 24 Rawhide 20160314.n.0 Base"]
        otherpage = self.site.pages["Somepage"]
        # this will test the Rawhide path, as the *first* fakepages
        # call will hit
        fakeresults.side_effect = ([fakepage],)
        ret = self.site.get_validation_event(24, "", "20160314.n.0")
        assert isinstance(ret, wikitcms.event.NightlyEvent)
        assert ret.milestone == "Rawhide"
        # this will test the Branched path, as the *second* fakepages
        # call will hit
        fakeresults.side_effect = ([otherpage], [fakepage])
        ret = self.site.get_validation_event(24, "", "20160314.n.0")
        assert isinstance(ret, wikitcms.event.NightlyEvent)
        assert ret.milestone == "Branched"
        # ...and this won't hit anywhere and should raise
        fakeresults.side_effect = ([otherpage], [otherpage])
        with pytest.raises(ValueError) as err:
            self.site.get_validation_event(24, "", "20160314.n.0")
            assert "Could not find any event" in err

    @mock.patch("wikitcms.event.ComposeEvent.__init__", return_value=None, autospec=True)
    @mock.patch("wikitcms.wiki.Wiki.get_current_event")
    def test_get_validation_event_guess_nomatch(self, fakecurr, fakeevent, fakemwp):
        """Check that when we guess but specify a release or milestone
        and the guessed release doesn't match the requested release or
        milestone, we fail.
        """
        event = wikitcms.event.ComposeEvent(self.site, 24, "Beta", "1.1")
        fakeevent.return_value = event
        with pytest.raises(ValueError) as err:
            self.site.get_validation_event(release=23)
            assert "does not match requested" in err
        with pytest.raises(ValueError) as err:
            self.site.get_validation_event(milestone="Final")
            assert "does not match requested" in err

    @mock.patch("fedfind.release.Compose.exists", return_value=True)
    @mock.patch("fedfind.release.Production.label", "RC-1.6")
    @mock.patch("fedfind.release.Production.cid", "Fedora-27-20171105.0")
    @mock.patch("fedfind.helpers.get_current_release", autospec=True, return_value=27)
    @mock.patch("mwclient.page.Page.__init__", return_value=None, autospec=True)
    @mock.patch("mwclient.page.Page.text", return_value=FAKE_CURRENT_COMPOSE)
    @mock.patch("wikitcms.page.NightlyPage", autospec=True)
    @mock.patch("wikitcms.page.ComposePage", autospec=True)
    def test_get_validation_page(
        self, fakecompose, fakenightly, faketext, fakeinit, fakegetcurr, fakecompexists
    ):
        """Various tests for get_validation_page."""
        # current event
        self.site.get_validation_page("Installation")
        fakecompose.assert_called_with(
            self.site, "24", "Installation", "Alpha", "1.1", dist="Fedora"
        )
        # old-school TC/RC
        self.site.get_validation_page("Installation", 23, "Final", "TC9")
        fakecompose.assert_called_with(self.site, 23, "Installation", "Final", "TC9", dist="Fedora")
        self.site.get_validation_page("Installation", 23, "Beta", "RC1")
        fakecompose.assert_called_with(self.site, 23, "Installation", "Beta", "RC1", dist="Fedora")
        # old-school nightly
        self.site.get_validation_page("Installation", 23, "Rawhide", "20151112")
        fakenightly.assert_called_with(
            self.site, 23, "Installation", "Rawhide", "20151112", dist="Fedora"
        )
        self.site.get_validation_page("Installation", 23, "Branched", "20151211")
        fakenightly.assert_called_with(
            self.site, 23, "Installation", "Branched", "20151211", dist="Fedora"
        )
        # Pungi 4 production/candidate
        self.site.get_validation_page("Installation", 24, "Alpha", "1.1")
        fakecompose.assert_called_with(self.site, 24, "Installation", "Alpha", "1.1", dist="Fedora")
        self.site.get_validation_page("Installation", 27, "Beta", "1.5", dist="Fedora-Modular")
        fakecompose.assert_called_with(
            self.site, 27, "Installation", "Beta", "1.5", dist="Fedora-Modular"
        )
        # Past 23, 'Final' milestone should be converted to 'RC'
        self.site.get_validation_page("Installation", 25, "Final", "1.1")
        fakecompose.assert_called_with(self.site, 25, "Installation", "RC", "1.1", dist="Fedora")
        # Pungi 4 nightly
        self.site.get_validation_page("Installation", 24, "Rawhide", "20160222.n.0")
        fakenightly.assert_called_with(
            self.site, 24, "Installation", "Rawhide", "20160222.n.0", dist="Fedora"
        )
        self.site.get_validation_page("Installation", 24, "Branched", "20160315.n.1")
        fakenightly.assert_called_with(
            self.site, 24, "Installation", "Branched", "20160315.n.1", dist="Fedora"
        )
        self.site.get_validation_page(
            "Installation", 27, "Branched", "20171110.n.1", dist="Fedora-Modular"
        )
        fakenightly.assert_called_with(
            self.site, 27, "Installation", "Branched", "20171110.n.1", dist="Fedora-Modular"
        )
        # Rawhide nightly compose ID
        self.site.get_validation_page("Installation", cid="Fedora-Rawhide-20180220.n.0")
        fakenightly.assert_called_with(
            self.site, "28", "Installation", "Rawhide", "20180220.n.0", dist="Fedora"
        )
        # Branched nightly compose ID
        self.site.get_validation_page("Installation", cid="Fedora-27-20171120.n.0")
        fakenightly.assert_called_with(
            self.site, "27", "Installation", "Branched", "20171120.n.0", dist="Fedora"
        )
        # Candidate compose ID
        self.site.get_validation_page("Installation", cid="Fedora-27-20171105.0")
        fakecompose.assert_called_with(self.site, "27", "Installation", "RC", "1.6", dist="Fedora")

        with pytest.raises(ValueError):
            # Non-nightly compose but no milestone
            self.site.get_validation_page("Installation", 24, "", "1.1")
        # Invalid composes
        with pytest.raises(ValueError):
            self.site.get_validation_page("Installation", 24, "Branched", "foobar")
        with pytest.raises(ValueError):
            self.site.get_validation_page("Installation", 24, "Branched", "TC1a")
        with pytest.raises(ValueError):
            self.site.get_validation_page("Installation", 24, "Branched", "1.1a")
        # looks kinda like a date but is not one
        with pytest.raises(ValueError):
            self.site.get_validation_page("Installation", 24, "Branched", "20161356")
        with pytest.raises(ValueError):
            self.site.get_validation_page("Installation", 24, "Branched", "20161356.n.0")
        with pytest.raises(ValueError):
            # invalid type
            self.site.get_validation_page("Installation", 24, "Branched", "20160314.x.0")

    def test_get_validation_page_guess_nightly(self):
        """Test get_validation_page guessing milestone for nightly
        events.
        """
        # fake_pginit1 will test the Rawhide path
        with mock.patch("wikitcms.page.NightlyPage.__init__", fake_pginit1):
            ret = self.site.get_validation_page("Installation", 24, "", "20160314.n.0")
        assert isinstance(ret, wikitcms.page.NightlyPage)
        assert ret.milestone == "Rawhide"
        # fake_pginit2 will test the Rawhide path
        with mock.patch("wikitcms.page.NightlyPage.__init__", fake_pginit2):
            ret = self.site.get_validation_page("Installation", 24, "", "20160314.n.0")
        assert isinstance(ret, wikitcms.page.NightlyPage)
        assert ret.milestone == "Branched"
        # ...and fake_pginit3 won't hit anywhere and should raise
        with mock.patch("wikitcms.page.NightlyPage.__init__", fake_pginit3):
            with pytest.raises(ValueError) as err:
                ret = self.site.get_validation_page("Installation", 24, "", "20160314.n.0")
                assert "Could not find any event" in err

    def test_get_validation_page_guess_nomatch(self, fakemwp):
        """Check that when we guess but specify a release or milestone
        and the guessed release doesn't match the requested release or
        milestone, we fail.
        """
        fakecurr = {
            "full": "32 Branched 20200407.n.0",
            "release": "32",
            "milestone": "Branched",
            "compose": "",
            "date": "20200407.n.0",
        }
        with mock.patch("wikitcms.wiki.Wiki.get_current_compose", return_value=fakecurr):
            with pytest.raises(ValueError) as err:
                self.site.get_validation_page("Installation", release=23)
                assert "does not match requested" in err
            with pytest.raises(ValueError) as err:
                self.site.get_validation_page("Installation", milestone="Final")
                assert "does not match requested" in err

    # we use the find_resultrow and ResultRow dummies from the top of
    # the file here
    @mock.patch("wikitcms.page.NightlyPage.__init__", return_value=None, autospec=True)
    @mock.patch("wikitcms.page.ComposePage.__init__", return_value=None, autospec=True)
    @mock.patch("wikitcms.page.NightlyPage.find_resultrow", fake_findrow)
    @mock.patch("wikitcms.page.ComposePage.find_resultrow", fake_findrow)
    @mock.patch("wikitcms.page.NightlyPage.add_results", autospec=True)
    @mock.patch("wikitcms.page.ComposePage.add_results", autospec=True)
    def test_report_validation_results(self, fakecompose, fakenightly, fakecompinit, fakenightinit):
        """Tests for report_validation_results."""
        restups = [
            wk.ResTuple(
                "Installation",
                "24",
                "Alpha",
                "1.1",
                "QA:Testcase_foo",
                status="pass",
                user="adamwill",
            ),
            wk.ResTuple(
                "Installation",
                "24",
                "Alpha",
                "1.1",
                "QA:Testcase_bar",
                status="pass",
                user="adamwill",
                section="testsec",
                env="testenv1",
            ),
            wk.ResTuple(
                "Installation",
                "24",
                "Alpha",
                "1.1",
                "QA:Testcase_bar",
                status="pass",
                user="adamwill",
                section="testsec",
                env="testenv2",
            ),
            wk.ResTuple(
                "Installation",
                "24",
                "Branched",
                "20160314.n.1",
                "QA:Testcase_foo",
                status="pass",
                user="adamwill",
            ),
            wk.ResTuple(
                "Installation",
                "24",
                "Branched",
                "20160314.n.1",
                "QA:Testcase_bar",
                status="pass",
                user="adamwill",
                section="testsec",
                env="testenv1",
            ),
            wk.ResTuple(
                "Installation",
                "24",
                "Branched",
                "20160314.n.1",
                "QA:Testcase_bar",
                status="pass",
                user="adamwill",
                section="testsec",
                env="testenv2",
            ),
        ]
        self.site.report_validation_results(restups)
        # this ought to call add_results once for each page.
        for fake in (fakecompose, fakenightly):
            assert len(fake.call_args_list) == 1
            compargs = fake.call_args
            # compargs[0] is all args as a list, add_results takes a
            # single arg which is the resdict first item is self (when
            # autospec is used)
            resdict = compargs[0][1]
            # resdict should have exactly two entries, one per test
            # instance
            assert len(resdict) == 2
            # we're going to sort the dict items for ease of testing.
            items = sorted(list(resdict.items()), key=lambda x: x[0].name, reverse=True)
            # first resdict entry: should be for the 'foo' test case...
            (key, value) = items[0]
            assert key.name == "QA:Testcase_foo.."
            # ...and value should be a 1-item list of a single 2-tuple,
            # env '', result a Result instance
            assert len(value) == 1
            (env, res) = value[0]
            assert env == ""
            assert isinstance(res, wikitcms.result.Result)
            (key, value) = items[1]
            # second resdict entry: should be for the 'bar' test case
            # with section name...
            assert key.name == "QA:Testcase_bar.testsec."
            # ... and value should be a 2-item list of 2-tuples,
            # differing in the environment
            assert len(value) == 2
            (env1, res) = value[0]
            assert env1 == "testenv1"
            assert isinstance(res, wikitcms.result.Result)
            (env1, res) = value[1]
            assert env1 == "testenv2"
            assert isinstance(res, wikitcms.result.Result)

    @mock.patch("mwclient.listing.Category.members")
    def test_testtypes(self, fakemembers, fakemwp):
        """Tests for testtypes and, incidentally, matrices."""
        # this is more or less what the return of
        # category.members(generator=False) looks like - it's an
        # mwclient 'List' instance
        instmx = {"title": "Template:Installation test matrix", "pageid": 54437, "ns": 10}
        basemx = {"title": "Template:Base test matrix", "pageid": 54433, "ns": 10}
        fakemembers.return_value = [instmx, basemx]
        assert self.site.testtypes == ["Installation", "Base"]

    @mock.patch("mwclient.listing.Category.members")
    def test_modular_testtypes(self, fakemembers, fakemwp):
        """Tests for modular testtypes and, incidentally, matrices."""
        # this is more or less what the return of
        # category.members(generator=False) looks like - it's an
        # mwclient 'List' instance
        instmx = {"title": "Template:Installation Modular test matrix", "pageid": 77036, "ns": 10}
        servmx = {"title": "Template:Server Modular test matrix", "pageid": 77040, "ns": 10}
        fakemembers.return_value = [instmx, servmx]
        assert self.site.modular_testtypes == ["Installation", "Server"]

    @mock.patch("mwclient.Site.login", autospec=True)
    @mock.patch("mwclient.Site.site_init", autospec=True)
    def test_login(self, fakeinit, fakelogin):
        """Tests for login(), including all the OpenID stuff."""
        # self.site should just wrap mwclient as it's not fp.o
        self.site.login(username="foo", password="bar")
        assert fakelogin.call_count == 1
        assert fakelogin.call_args[1]["username"] == "foo"
        assert fakelogin.call_args[1]["password"] == "bar"
        # check host splitting
        fakelogin.reset_mock()
        site = wk.Wiki(["https", "fjajah"], do_init=False, force_login=False)
        site.login(username="foo", password="bar")
        assert fakelogin.call_count == 1

        # now, activate the openid bits
        fakelogin.reset_mock()
        site = wk.Wiki("fedoraproject.org", do_init=False, force_login=False)
        # have to fake this up
        site.version = (1, 30)
        site.login()
        assert isinstance(site.connection.auth, openidc_client.requestsauth.OpenIDCClientAuther)
        assert site.connection.auth.scopes == ["openid", "https://fedoraproject.org/wiki/api"]
        assert isinstance(site.connection.auth.client, openidc_client.OpenIDCClient)
        assert site.connection.auth.client.app_id == "wikitcms"
        assert site.connection.auth.client.idp == "https://id.fedoraproject.org/openidc/"
        assert site.connection.auth.client.idp_mapping == {
            "Token": "Token",
            "Authorization": "Authorization",
        }
        assert site.connection.auth.client.client_id == "wikitcms"
        # <hacker voice>I'M IN</hacker voice>
        assert site.connection.auth.client.client_secret == "notsecret"
        assert site.connection.auth.client.useragent == "wikitcms"
        # this is when we can't import the OpenID bits - the idea is
        # we still work for non-OpenID paths in that case and only die
        # here
        with mock.patch("wikitcms.wiki.OpenIDCClient", None):
            with pytest.raises(ImportError):
                site.login()
        with mock.patch("wikitcms.wiki.OpenIDCClientAuther", None):
            with pytest.raises(ImportError):
                site.login()


# vim: set textwidth=100 ts=8 et sw=4:
