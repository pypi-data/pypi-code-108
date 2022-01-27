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
# pylint: disable=invalid-name

"""Tests for listing.py."""

from unittest import mock

import mwclient.image
import mwclient.page
import pytest

import wikitcms.listing
import wikitcms.page
import wikitcms.release
import wikitcms.wiki


@pytest.mark.usefixtures("fakemwp")
class TestListing:
    """Tests for the generator magic in listing.py. This stuff is all
    a bit odd, and because of that, the testing is a bit indirect. A
    lot of the tests don't go directly through anything defined in
    listing.py but through Wiki.pages, because ultimately backing that
    is the most important thing listing.py does: Wiki.pages is an
    instance of listing's TcmsPageList, which is a subclass of
    TcmsGeneratorList, where most of the magic lives. Aside from that
    we test the category stuff via the 'real' category classes that
    use it.
    """

    # the "fjajah" is just to make sure we're running offline; if I
    # screw up and add a test that hits the network it"ll cause the
    # tests to hang/fail instead of succeeding a bit slower
    site = wikitcms.wiki.Wiki("fjajah", do_init=False, force_login=False)

    @mock.patch("mwclient.image.Image.__init__", return_value=None)
    def test_pages_nomatch(self, fakeimage):
        """If we don't hit any of the special Wikitcms classes, we
        should return whatever mwclient would return - a Page, Image,
        or Category. We also should not hit re.compile for Page or
        Image, we should catch them with early checks.
        """
        with mock.patch("re.compile"):
            assert isinstance(self.site.pages["Somepage"], mwclient.page.Page)
            assert isinstance(self.site.pages["Image:Someimage"], mwclient.image.Image)
        # we do handle some categories, so we can't mock re.compile
        assert isinstance(self.site.pages["Category:Something"], mwclient.listing.Category)

    @mock.patch("re.compile")
    def test_pages_knownbad_early(self, fakecompile):
        """Some more cases where we should just fall through, and do
        it before hitting re.compile. Mocking it out effectively tests
        that: if we hit it, things will blow up because it's not doing
        its job because it's a MagicMock.
        """
        # we don't handle the translated pages, for test days where
        # translation happened
        assert isinstance(self.site.pages["Test_Day:2010-09-29_Radeon/ru"], mwclient.page.Page)
        # the metadata pages are special stuff for the testdays webapp
        pg = self.site.pages["Test Day:2019-09-23 F31 Upgrade Test Day TestdayApp Metadata"]
        assert isinstance(pg, mwclient.page.Page)
        # these were subpages of the Test Day page proper where we
        # put output from a specific test
        pg = self.site.pages["Test Day:2011-02-22 Nouveau/rendercheck/red"]
        assert isinstance(pg, mwclient.page.Page)

    def test_pages_knownbad_late(self):
        """Some more cases where we should just fall through, but
        later in the process, because these pages look kinda like we
        should handle them but we don't.
        """
        # a very early validation page style we don't handle yet
        pg = self.site.pages["Test Results:Fedora 13 Pre-RC Acceptance Test 1"]
        assert isinstance(pg, mwclient.page.Page)

    def test_pages_nightly(self):
        """Nightly validation pages."""
        pg = self.site.pages["Test_Results:Fedora_32_Branched_20200322.n.0_Installation"]
        assert isinstance(pg, wikitcms.page.NightlyPage)
        assert pg.release == "32"
        assert pg.testtype == "Installation"
        assert pg.milestone == "Branched"
        assert pg.compose == "20200322.n.0"
        assert pg.dist == "Fedora"
        # yeah, the _ vs. space thing is intentional, we ought to
        # handle both, may as well check it as we go
        pg = self.site.pages["Test Results:Fedora 32 Rawhide 20191030.n.1 Base"]
        assert isinstance(pg, wikitcms.page.NightlyPage)
        assert pg.testtype == "Base"
        assert pg.milestone == "Rawhide"
        # modular
        pg = self.site.pages["Test Results:Fedora-Modular 27 Branched 20171123.n.1 Server"]
        assert isinstance(pg, wikitcms.page.NightlyPage)
        assert pg.dist == "Fedora-Modular"
        # IoT
        pg = self.site.pages["Test Results:Fedora-IoT 33 RC 20200513.0 General"]
        assert isinstance(pg, wikitcms.page.NightlyPage)
        assert pg.dist == "Fedora-IoT"
        # summary should fall through to an mwclient Page
        pg = self.site.pages["Test_Results:Fedora_32_Branched_20200322.n.0_Summary"]
        assert not isinstance(pg, wikitcms.page.Page)
        assert isinstance(pg, mwclient.page.Page)

    def test_pages_f21_monthly(self):
        """The old monthly pages we had around F21."""
        pg = self.site.pages["Test Results:Fedora 21 Nightly 2014 08 Base"]
        assert isinstance(pg, wikitcms.page.NightlyPage)
        assert pg.release == "21"
        assert pg.milestone == "Nightly"
        assert pg.compose == "2014 08"
        assert pg.testtype == "Base"
        pg = self.site.pages["Test Results:Fedora 21 Rawhide 2014 04 Installation"]
        assert isinstance(pg, wikitcms.page.NightlyPage)
        assert pg.milestone == "Rawhide"
        assert pg.testtype == "Installation"

    def test_pages_milestone_f12(self):
        """Milestone validation pages, weird cases from F12."""
        pg = self.site.pages["Test Results:Fedora 12 Final Pre-RC Install"]
        assert isinstance(pg, wikitcms.page.ComposePage)
        assert pg.release == "12"
        assert pg.milestone == "Final"
        assert pg.compose == "Pre-RC"
        pg = self.site.pages["Test Results:Fedora 12 Alpha TC Install"]
        assert isinstance(pg, wikitcms.page.ComposePage)
        assert pg.milestone == "Alpha"
        assert pg.compose == "TC"
        pg = self.site.pages["Test Results:Fedora 12 Alpha TCRegression Install"]
        assert isinstance(pg, wikitcms.page.ComposePage)
        assert pg.milestone == "Alpha"
        assert pg.compose == "TCRegression"
        pg = self.site.pages["Test Results:Fedora 12 Beta PreBeta Install"]
        assert isinstance(pg, wikitcms.page.ComposePage)
        assert pg.milestone == "Beta"
        assert pg.compose == "PreBeta"

    def test_pages_milestone_tcrc(self):
        """Milestone validation pages, the pre-Pungi 4 "TCx / RCx"
        style.
        """
        # also testing the old "Install" (not "Installation") testtype
        pg = self.site.pages["Test Results:Fedora 20 Alpha RC1 Install"]
        assert isinstance(pg, wikitcms.page.ComposePage)
        assert pg.release == "20"
        assert pg.milestone == "Alpha"
        assert pg.compose == "RC1"
        assert pg.testtype == "Install"
        assert pg.dist == "Fedora"
        pg = self.site.pages["Test Results:Fedora 22 Beta TC1 Installation"]
        assert isinstance(pg, wikitcms.page.ComposePage)
        assert pg.release == "22"
        assert pg.milestone == "Beta"
        assert pg.compose == "TC1"
        assert pg.testtype == "Installation"

    def test_pages_milestone_pungi4(self):
        """Milestone validation pages, current (2020-04) Pungi 4
        style.
        """
        pg = self.site.pages["Test Results:Fedora 24 Alpha 1.1 Cloud"]
        assert isinstance(pg, wikitcms.page.ComposePage)
        assert pg.release == "24"
        assert pg.milestone == "Alpha"
        assert pg.compose == "1.1"
        assert pg.testtype == "Cloud"
        assert pg.dist == "Fedora"
        pg = self.site.pages["Test Results:Fedora 26 Beta 1.3 Security Lab"]
        assert isinstance(pg, wikitcms.page.ComposePage)
        assert pg.release == "26"
        assert pg.milestone == "Beta"
        assert pg.compose == "1.3"
        assert pg.testtype == "Security Lab"
        pg = self.site.pages["Test Results:Fedora 31 RC 1.9 Cloud"]
        assert isinstance(pg, wikitcms.page.ComposePage)
        assert pg.release == "31"
        assert pg.milestone == "RC"
        assert pg.compose == "1.9"
        assert pg.testtype == "Cloud"
        # modular
        pg = self.site.pages["Test Results:Fedora-Modular 27 Beta 1.5 Installation"]
        assert isinstance(pg, wikitcms.page.ComposePage)
        assert pg.release == "27"
        assert pg.milestone == "Beta"
        assert pg.compose == "1.5"
        assert pg.testtype == "Installation"
        assert pg.dist == "Fedora-Modular"
        # again, summary should fall through to an mwclient Page
        pg = self.site.pages["Test Results:Fedora 31 RC 1.9 Summary"]
        assert not isinstance(pg, wikitcms.page.Page)
        assert isinstance(pg, mwclient.page.Page)

    def test_pages_testday(self):
        """Test Day pages."""
        pg = self.site.pages["Test Day:2020-04-08 Fedora 32 IoT Edition"]
        assert isinstance(pg, wikitcms.page.TestDayPage)
        assert pg.date == "2020-04-08"
        assert pg.subject == "Fedora 32 IoT Edition"
        # why this exists I don't know, but it does
        pg = self.site.pages["Test Day:2012-03-14"]
        assert isinstance(pg, wikitcms.page.TestDayPage)
        assert pg.date == "2012-03-14"
        assert pg.subject == ""

    # we're just mocking this so we can count the calls
    @mock.patch("wikitcms.listing.PageCheckWarning.__init__", autospec=True, return_value=None)
    def test_pages_checkname(self, fakepagecheck):
        """There's a mechanism where we refuse to return a Wikitcms-y
        instance if its expected name (which all Wikitcms Page classes
        are required to define, as 'checkname') does not match the
        actual page name we got the instance from. This checks that
        still works.
        """
        # this should match the testday_patt regex, but the extra
        # spaces should mean the checkname won't match
        pg = self.site.pages["Test Day:2020-04-08  Foobar"]
        assert isinstance(pg, mwclient.page.Page)
        # just the above isn't sufficient, as our classes are subs of
        # mwclient Page
        assert not isinstance(pg, wikitcms.page.TestDayPage)
        # to be super sure this worked as intended, check we hit the
        # exception's __init__
        assert fakepagecheck.call_count == 1

    def test_pages_validation_category(self):
        """Validation category pages."""
        # top level
        pg = self.site.pages["Category:Fedora 32 Test Results"]
        assert isinstance(pg, wikitcms.listing.ValidationCategory)
        assert pg.seedtext == "{{Validation results milestone category|release=32|dist=}}"
        assert pg.summary == "Relval bot-created validation result category page for Fedora 32"
        # top level, modular
        pg = self.site.pages["Category:Fedora-Modular 27 Test Results"]
        assert isinstance(pg, wikitcms.listing.ValidationCategory)
        assert pg.seedtext == "{{Validation results milestone category|release=27|dist=Modular}}"
        assert pg.summary == (
            "Relval bot-created validation result category page for Fedora-Modular 27"
        )
        # top level, IoT
        pg = self.site.pages["Category:Fedora-IoT 33 Test Results"]
        assert isinstance(pg, wikitcms.listing.ValidationCategory)
        assert pg.seedtext == "{{Validation results milestone category|release=33|dist=IoT}}"
        assert pg.summary == (
            "Relval bot-created validation result category page for Fedora-IoT 33"
        )
        # milestone level
        pg = self.site.pages["Category:Fedora 32 Beta Test Results"]
        assert isinstance(pg, wikitcms.listing.ValidationCategory)
        assert pg.seedtext == (
            "{{Validation results milestone category|release=32|milestone=Beta|dist=}}"
        )
        assert pg.summary == (
            "Relval bot-created validation result category page for Fedora 32 Beta"
        )
        # milestone level, modular
        pg = self.site.pages["Category:Fedora-Modular 27 Beta Test Results"]
        assert isinstance(pg, wikitcms.listing.ValidationCategory)
        assert pg.seedtext == (
            "{{Validation results milestone category|release=27|milestone=Beta|dist=Modular}}"
        )
        assert pg.summary == (
            "Relval bot-created validation result category page for Fedora-Modular 27 Beta"
        )
        # nightly level
        pg = self.site.pages["Category:Fedora 32 Nightly Test Results"]
        assert isinstance(pg, wikitcms.listing.ValidationCategory)
        assert pg.seedtext == (
            "{{Validation results milestone category|release=32|nightly=true|dist=}}"
        )
        assert pg.summary == (
            "Relval bot-created validation result category page for Fedora 32 nightly results"
        )
        # nightly level, modular
        pg = self.site.pages["Category:Fedora-Modular 27 Nightly Test Results"]
        assert isinstance(pg, wikitcms.listing.ValidationCategory)
        assert pg.seedtext == (
            "{{Validation results milestone category|release=27|nightly=true|dist=Modular}}"
        )
        assert pg.summary == (
            "Relval bot-created validation result category page for Fedora-"
            "Modular 27 nightly results"
        )
        # nightly level, IoT
        pg = self.site.pages["Category:Fedora-IoT 33 Nightly Test Results"]
        assert isinstance(pg, wikitcms.listing.ValidationCategory)
        assert pg.seedtext == (
            "{{Validation results milestone category|release=33|nightly=true|dist=IoT}}"
        )
        assert pg.summary == (
            "Relval bot-created validation result category page for Fedora-"
            "IoT 33 nightly results"
        )

    @mock.patch("mwclient.listing.GeneratorList.__next__")
    def test_pages_testday_category(self, fakenext):
        """Test Day category pages."""
        pg = self.site.pages["Category:Fedora 32 Test Days"]
        assert isinstance(pg, wikitcms.listing.TestDayCategory)
        assert pg.seedtext == (
            "This category contains all the Fedora 32 [[QA/Test_Days|Test "
            "Day]] pages. A calendar of the Test Days can be found ["
            "https://apps.fedoraproject.org/calendar/list/QA/?subject=Test+Day"
            " here].\n\n[[Category:Test Days]]"
        )
        assert pg.summary == "Created page (via wikitcms)"
        # test the iterator capability
        tdp = mwclient.page.Page(self.site, "Test Day:2019-12-09 Kernel 5.4 Test Week")
        fakenext.return_value = tdp
        assert isinstance(next(pg), wikitcms.page.TestDayPage)
        # iterator when page isn't one of ours
        fakenext.return_value = mwclient.page.Page(self.site, "Somepage")
        nextpg = next(pg)
        assert not isinstance(nextpg, wikitcms.page.Page)
        assert isinstance(nextpg, mwclient.page.Page)

    def test_pages_int_name(self):
        """We handle getting an integer as the page 'name' - which
        IIRC retrieves a page by some sort of unique ID - by doing a
        wiki roundtrip to get the real string name.
        """
        pg = self.site.pages[80736]
        assert isinstance(pg, wikitcms.page.TestDayPage)

    def test_allresults(self):
        """This is a test using the allresults generator, because that
        exercises the namespace handling in TcmsPageList.
        """
        # this would usually be set up by a remote trip in
        # site.__init__ but obviously not with do_init=False, so we
        # have to just set it up manually
        self.site.namespaces[116] = "Test Results"
        pg = self.site.allresults()["Fedora_32_Branched_20200322.n.0_Installation"]
        assert isinstance(pg, wikitcms.page.NightlyPage)

    def test_alltestdays(self):
        """This is a test using the alltestdays generator. We may as
        well test it here too as it's just the same as allresults.
        """
        # this would usually be set up by a remote trip in
        # site.__init__ but obviously not with do_init=False, so we
        # have to just set it up manually
        self.site.namespaces[114] = "Test Day"
        pg = self.site.alltestdays()["2019-12-09 Kernel 5.4 Test Week"]
        assert isinstance(pg, wikitcms.page.TestDayPage)

    def test_nopagewarning(self):
        """Test for the NoPageWarning exception."""
        exc = wikitcms.listing.NoPageWarning("QA:Somepage")
        assert str(exc) == "Could not produce a wikitcms page for: QA:Somepage"

    def test_pagecheckwarning(self):
        """Test for the PageCheckWarning exception."""
        exc = wikitcms.listing.PageCheckWarning("QA:Somepage", "QA:Someotherpage")
        assert str(exc) == (
            "Expected page name QA:Somepage does not match source " "page name QA:Someotherpage"
        )
