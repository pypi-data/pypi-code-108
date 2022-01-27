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
# pylint: disable=invalid-name

"""Tests for event.py."""

from unittest import mock

import fedfind.release
import mwclient.errors
import mwclient.page
import pytest

import wikitcms.event
import wikitcms.listing
import wikitcms.wiki as wk
from wikitcms.exceptions import FedfindNotFoundError


class TestEventFedfind:
    """Tests related to fedfind release discovery from validation
    events.
    """

    # the 'fjajah' is just to make sure we're running offline; if I
    # screw up and add a test that hits the network it'll cause the
    # tests to hang/fail instead of succeeding a bit slower
    site = wk.Wiki("fjajah", do_init=False, force_login=False)

    @mock.patch("fedfind.release.Compose.exists", True)
    @mock.patch("fedfind.release.Compose.all_images", ["foo"])
    def test_candidate_ff_release_compose(self):
        """Straightforward ff_release test case for a candidate
        compose which is properly synced to stage. Should work the
        same whether or not we pass the cid hint, both properties
        should exist and be the Compose instance.
        """
        event = wikitcms.event.ComposeEvent(
            self.site, "27", "RC", "1.6", cid="Fedora-27-20171105.0"
        )
        assert isinstance(event.ff_release, fedfind.release.Compose)
        assert isinstance(event.ff_release_images, fedfind.release.Compose)
        event = wikitcms.event.ComposeEvent(self.site, "27", "RC", "1.6")
        assert isinstance(event.ff_release, fedfind.release.Compose)
        assert isinstance(event.ff_release_images, fedfind.release.Compose)

    @mock.patch("fedfind.helpers.cid_from_label", return_value="")
    @mock.patch("fedfind.release.Compose.exists", False)
    @mock.patch("fedfind.release.Production.all_images", ["foo"])
    @mock.patch("fedfind.release.Production.cid", "Fedora-27-20171105.0")
    def test_candidate_ff_release_compose_gap(self, fakecidfromlabel):
        """Test the 'compose gap' case: this occurs when a candidate
        compose has just been created, but not yet synced to stage,
        and also has not yet appeared in PDC. In this case, without
        the 'cid' hint, we will not be able to find the fedfind
        release associated with the event. With the hint, we should
        find it in the non-synced location (as a fedfind Production).
        """
        event = wikitcms.event.ComposeEvent(
            self.site, "27", "RC", "1.6", cid="Fedora-27-20171105.0"
        )
        assert isinstance(event.ff_release, fedfind.release.Production)
        assert isinstance(event.ff_release_images, fedfind.release.Production)
        event = wikitcms.event.ComposeEvent(self.site, "27", "RC", "1.6")
        with pytest.raises(FedfindNotFoundError):
            print(event.ff_release)
        with pytest.raises(FedfindNotFoundError):
            print(event.ff_release_images)

    @mock.patch("fedfind.helpers.cid_from_label", return_value="Fedora-27-20171105.0")
    @mock.patch("fedfind.release.Compose.exists", False)
    @mock.patch("fedfind.release.Production.all_images", ["foo"])
    @mock.patch("fedfind.release.Production.cid", "Fedora-27-20171105.0")
    def test_candidate_ff_release_compose_gap_pdc(self, fakecidfromlabel):
        """Test the case where the candidate compose has not yet
        synced to stage, but has appeared in PDC. In this case, we
        should find the ff_release in the non-synced location (as a
        fedfind Production) with or without the cid hint.
        """
        event = wikitcms.event.ComposeEvent(
            self.site, "27", "RC", "1.6", cid="Fedora-27-20171105.0"
        )
        assert isinstance(event.ff_release, fedfind.release.Production)
        assert isinstance(event.ff_release_images, fedfind.release.Production)
        event = wikitcms.event.ComposeEvent(self.site, "27", "RC", "1.6")
        assert isinstance(event.ff_release, fedfind.release.Production)
        assert isinstance(event.ff_release_images, fedfind.release.Production)

    @mock.patch("fedfind.release.Compose.exists", True)
    @mock.patch("fedfind.release.Compose.all_images", [])
    @mock.patch("fedfind.release.Production.all_images", ["foo"])
    @mock.patch("fedfind.release.Production.cid", "Fedora-27-20171105.0")
    def test_candidate_ff_release_compose_exists_no_images(self):
        """Test a potential tricky case where a candidate compose
        tree exists on stage but the images haven't shown up in it
        yet. With the cid hint, the event's ff_release should be the
        Compose instance, but its ff_release_images should be the
        Production instance. Without the hint, we won't get images.
        """
        event = wikitcms.event.ComposeEvent(
            self.site, "27", "RC", "1.6", cid="Fedora-27-20171105.0"
        )
        assert isinstance(event.ff_release, fedfind.release.Compose)
        assert isinstance(event.ff_release_images, fedfind.release.Production)
        event = wikitcms.event.ComposeEvent(self.site, "27", "RC", "1.6")
        assert isinstance(event.ff_release, fedfind.release.Compose)
        with pytest.raises(FedfindNotFoundError):
            assert event.ff_release_images

    @mock.patch("fedfind.release.BranchedNightly.exists", True)
    @mock.patch("fedfind.release.BranchedNightly.all_images", ["foo"])
    def test_candidate_ff_release_nightly(self):
        """Straightforward ff_release test case for a nightly
        compose which exists and has images.
        """
        event = wikitcms.event.NightlyEvent(self.site, "27", "Branched", "20171104.n.0")
        assert isinstance(event.ff_release, fedfind.release.BranchedNightly)
        assert isinstance(event.ff_release_images, fedfind.release.BranchedNightly)

    @mock.patch("fedfind.release.BranchedNightly.exists", False)
    @mock.patch("fedfind.release.BranchedNightly.all_images", [])
    def test_candidate_ff_release_nightly_no_images(self):
        """ff_release test case for a nightly compose which doesn't
        exist and has no images. We get ff_release (as fedfind doesn't
        do an existence check in this case), but not images.
        """
        event = wikitcms.event.NightlyEvent(self.site, "27", "Branched", "20171104.n.0")
        assert isinstance(event.ff_release, fedfind.release.BranchedNightly)
        with pytest.raises(FedfindNotFoundError):
            assert event.ff_release_images

    @mock.patch("fedfind.release.IoTNightly.exists", True)
    @mock.patch("fedfind.release.IoTNightly.all_images", ["foo"])
    def test_candidate_ff_release_iot(self):
        """Straightforward ff_release test case for an IoT 'nightly'
        compose.
        """
        event = wikitcms.event.NightlyEvent(self.site, "33", "RC", "20200513.0", dist="Fedora-IoT")
        assert isinstance(event.ff_release, fedfind.release.IoTNightly)
        assert isinstance(event.ff_release_images, fedfind.release.IoTNightly)


@pytest.mark.usefixtures("fakemwp")
@mock.patch("wikitcms.page.Page.save", autospec=True)
@mock.patch("wikitcms.page.SummaryPage.update_current", autospec=True)
@mock.patch("wikitcms.page.ValidationPage.update_current", autospec=True)
@mock.patch("wikitcms.event.ValidationEvent.update_current", autospec=True)
@mock.patch(
    "test_event.wk.Wiki.get_testtypes",
    return_value=["Installation", "Base", "Server", "Cloud", "Desktop"],
)
@mock.patch("fedfind.release.BranchedNightly.cid", "Fedora-27-20171104.n.0")
@mock.patch(
    "fedfind.helpers.download_json",
    return_value={
        "arguments": {},
        "count": 1,
        "pages": 1,
        "total": 1,
        "raw_messages": [
            {
                "msg": {
                    "architecture": "x86_64",
                    "compose": "Fedora-27-20171104.n.0",
                    "destination": "eu-west-2",
                    "extra": {
                        "id": "ami-085e29c4cd80e326d",
                        "virt_type": "hvm",
                        "vol_type": "gp2",
                    },
                }
            }
        ],
    },
)
class TestEventCreate:
    """Tests related to event creation."""

    site = wk.Wiki("fjajah", do_init=False, force_login=False)

    @mock.patch("fedfind.release.BranchedNightly.exists", True)
    @mock.patch(
        "fedfind.release.BranchedNightly.all_images",
        [
            {
                "arch": "x86_64",
                "format": "iso",
                "path": (
                    "Workstation/x86_64/iso/" "Fedora-Workstation-Live-x86_64-27-2011104.n.0.iso"
                ),
                "subvariant": "Workstation",
                "type": "live",
                "url": (
                    "https://kojipkgs.fedoraproject.org/compose/branched/"
                    "Fedora-27-20171104.n.0/Workstation/x86_64/iso/"
                    "Fedora-Workstation-Live-x86_64-27-2011104.n.0.iso"
                ),
            }
        ],
    )
    def test_event_create(self, fakejson, faketypes, fakeevup, fakepageup, fakesumup, fakepagesave):
        """Test normal event creation."""
        event = wikitcms.event.NightlyEvent(self.site, "27", "Branched", "20171104.n.0")
        event.create()
        # we should save 5 test pages, plus the summary page,
        # download page, AMI page and two category pages
        assert fakepagesave.call_count == 10
        # we should call update_current for all 5 test pages
        assert fakepageup.call_count == 5
        # and also for the Summary page
        assert fakesumup.call_count == 1
        # we should call update_current for the event itself
        assert fakeevup.call_count == 1
        # verify we set createonly to True by default
        for call in fakepagesave.call_args_list:
            assert call[1]["createonly"] is True

    @mock.patch("fedfind.release.BranchedNightly.exists", False)
    @mock.patch("fedfind.release.BranchedNightly.all_images", [])
    def test_event_create_no_images(
        self, fakejson, faketypes, fakeevup, fakepageup, fakesumup, fakepagesave
    ):
        """Test event creation where no images are available. This
        should succeed, but not create a download page.
        """
        event = wikitcms.event.NightlyEvent(self.site, "27", "Branched", "20171104.n.0")
        event.create()
        # we should save 5 test pages, plus the summary page and
        # two category pages and AMI page - but no download page
        assert fakepagesave.call_count == 9
        # we should call update_current for all 5 test pages
        assert fakepageup.call_count == 5
        # we should call update_current for the event itself
        assert fakeevup.call_count == 1

    @mock.patch("fedfind.release.BranchedNightly.exists", False)
    @mock.patch("fedfind.release.BranchedNightly.all_images", [])
    def test_event_create_check(
        self, fakejson, faketypes, fakeevup, fakepageup, fakesumup, fakepagesave
    ):
        """Test event creation with check=True."""
        event = wikitcms.event.NightlyEvent(self.site, "27", "Branched", "20171104.n.0")
        # first, let's say the pages had no content, so creation
        # should go ahead...
        with mock.patch("mwclient.page.Page.text", return_value=""):
            event.create(check=True)
        # we should save 5 test pages, plus the summary page and
        # two category pages and AMI page - but no download page
        assert fakepagesave.call_count == 9
        # now, let's say the pages *do* have content, we should get
        # an exception now...
        fakepagesave.reset_mock()
        with mock.patch("mwclient.page.Page.text", return_value="foobar"):
            with pytest.raises(ValueError):
                event.create(check=True)
        assert fakepagesave.call_count == 0

    @mock.patch("fedfind.release.BranchedNightly.exists", False)
    @mock.patch("fedfind.release.BranchedNightly.all_images", [])
    def test_event_create_testtypes(
        self, fakejson, faketypes, fakeevup, fakepageup, fakesumup, fakepagesave
    ):
        """Test event creation for a specified set of test types."""
        event = wikitcms.event.NightlyEvent(self.site, "27", "Branched", "20171104.n.0")
        event.create(testtypes=["Installation", "Server"])
        # we should save 2 test pages, plus the summary page and
        # two category pages and AMI page - but no download page
        assert fakepagesave.call_count == 6
        # we should call update_current for both test pages
        assert fakepageup.call_count == 2
        # we should call update_current for the event itself
        assert fakeevup.call_count == 1
        # check correct handling of garbage list of testtypes
        with pytest.raises(ValueError):
            event.create(testtypes=["foo", "bar"])

    @mock.patch("fedfind.release.BranchedNightly.exists", False)
    @mock.patch("fedfind.release.BranchedNightly.all_images", [])
    def test_event_create_force(
        self, fakejson, faketypes, fakeevup, fakepageup, fakesumup, fakepagesave
    ):
        """Test event creation with force=True."""
        # we only need to test that we properly set createonly=None
        # here, we don't need to confirm or mock its effects
        event = wikitcms.event.NightlyEvent(self.site, "27", "Branched", "20171104.n.0")
        event.create(force=True)
        for call in fakepagesave.call_args_list:
            assert call[1]["createonly"] is None

    @mock.patch("fedfind.release.BranchedNightly.exists", False)
    @mock.patch("fedfind.release.BranchedNightly.all_images", [])
    def test_event_create_existing(
        self, fakejson, faketypes, fakeevup, fakepageup, fakesumup, fakepagesave
    ):
        """Test the handling when a page we try to create during
        event creation already exists. The expected behaviour is that
        we just log the issue and continue.
        """
        event = wikitcms.event.NightlyEvent(self.site, "27", "Branched", "20171104.n.0")
        fakepagesave.side_effect = mwclient.errors.APIError("articleexists", "Article exists", {})
        event.create()
        # but if the error is something *else*, we should raise it
        fakepagesave.side_effect = mwclient.errors.APIError("frobbled", "Article is frobbled", {})
        with pytest.raises(mwclient.errors.APIError):
            event.create()
        fakepagesave.reset_mock()

    @mock.patch("fedfind.release.BranchedNightly.exists", False)
    @mock.patch("fedfind.release.BranchedNightly.all_images", [])
    def test_event_create_nocurrent(
        self, fakejson, faketypes, fakeevup, fakepageup, fakesumup, fakepagesave
    ):
        """Test that setting current=False correctly skips current
        redirect updates.
        """
        event = wikitcms.event.NightlyEvent(self.site, "27", "Branched", "20171104.n.0")
        event.create(current=False)
        # we should save 5 test pages, plus the summary page and
        # two category pages and AMI page - but no download page
        assert fakepagesave.call_count == 9
        # we should not call update_current for test pages
        assert fakepageup.call_count == 0
        # we should not call update_current for the event itself
        assert fakeevup.call_count == 0


class TestEventOther:
    """Tests for properties of Event instances and other methods."""

    site = wk.Wiki("fjajah", do_init=False, force_login=False)

    @mock.patch("mwclient.listing.GeneratorList.__next__")
    def test_event_result_pages(self, fakenext, fakemwp):
        """Test for result_pages property."""
        event = wikitcms.event.NightlyEvent(self.site, "27", "Branched", "20171104.n.0")
        # we need to mock the output of the generator the method uses
        # it's an 'allresults' generator (so it uses the Test Results
        # namespace) and the prefix should be "Fedora 27 Branched
        # 20171104.n.0 ", so what we're expecting to get back is all
        # the actual result pages plus the summary page, and we have
        # to test the method correctly filters out the summary
        evp1 = mwclient.page.Page(self.site, "Test Results:Fedora 27 Branched 20171104.n.0 Base")
        evp2 = mwclient.page.Page(self.site, "Test Results:Fedora 27 Branched 20171104.n.0 Cloud")
        evs = mwclient.page.Page(self.site, "Test Results:Fedora 27 Branched 20171104.n.0 Summary")
        fakenext.side_effect = [evp1, evp2, evs, StopIteration]
        rps = event.result_pages
        assert len(rps) == 2
        (rp1, rp2) = rps
        assert isinstance(rp1, wikitcms.page.NightlyPage)
        assert isinstance(rp2, wikitcms.page.NightlyPage)
        assert rp1.testtype == "Base"
        assert rp2.testtype == "Cloud"
        assert rp1.dist == rp2.dist == "Fedora"
        # modular
        event = wikitcms.event.NightlyEvent(
            self.site, "27", "Branched", "20171123.n.1", dist="Fedora-Modular"
        )
        evp1 = mwclient.page.Page(
            self.site, "Test Results:Fedora-Modular 27 Branched 20171123.n.1 Base"
        )
        evp2 = mwclient.page.Page(
            self.site, "Test Results:Fedora-Modular 27 Branched 20171123.n.1 Server"
        )
        evs = mwclient.page.Page(
            self.site, "Test Results:Fedora-Modular 27 Branched 20171123.n.1 Summary"
        )
        fakenext.side_effect = [evp1, evp2, evs, StopIteration]
        rps = event.result_pages
        assert len(rps) == 2
        (rp1, rp2) = rps
        assert isinstance(rp1, wikitcms.page.NightlyPage)
        assert isinstance(rp2, wikitcms.page.NightlyPage)
        assert rp1.testtype == "Base"
        assert rp2.testtype == "Server"
        assert rp1.dist == rp2.dist == "Fedora-Modular"

    @mock.patch("mwclient.page.Page.save", autospec=True)
    def test_event_update_current(self, fakesave, fakemwp):
        """Test for update_current() method."""
        event = wikitcms.event.NightlyEvent(self.site, "27", "Branched", "20171104.n.0")
        event.update_current()
        assert fakesave.call_args[0][1] == (
            "{{tempdoc}}\n<onlyinclude>{{#switch: {{{1|full}}}\n| full = 27 Branched 20171104.n.0"
            "\n| release = 27\n| milestone = Branched\n| compose =\n| date = 20171104.n.0\n"
            "}}</onlyinclude>\n[[Category: Fedora Templates]]"
        )
        assert fakesave.call_args[0][2] == "relval: update to current event"
        assert fakesave.call_args[1]["createonly"] is None
        assert fakesave.call_args[0][0].name == "Template:CurrentFedoraCompose"
        # modular, non-nightly
        event = wikitcms.event.ComposeEvent(self.site, "27", "Beta", "1.5", dist="Fedora-Modular")
        event.update_current()
        assert fakesave.call_args[0][1] == (
            "{{tempdoc}}\n<onlyinclude>{{#switch: {{{1|full}}}\n| full = 27 Beta 1.5"
            "\n| release = 27\n| milestone = Beta\n| compose = 1.5\n| date =\n"
            "}}</onlyinclude>\n[[Category: Fedora Templates]]"
        )
        assert fakesave.call_args[0][2] == "relval: update to current event"
        assert fakesave.call_args[1]["createonly"] is None
        assert fakesave.call_args[0][0].name == "Template:CurrentFedora-ModularCompose"
        # IoT 'nightly'
        event = wikitcms.event.NightlyEvent(self.site, "33", "RC", "20200513.0", dist="Fedora-IoT")
        event.update_current()
        assert fakesave.call_args[0][1] == (
            "{{tempdoc}}\n<onlyinclude>{{#switch: {{{1|full}}}\n| full = 33 RC 20200513.0"
            "\n| release = 33\n| milestone = RC\n| compose =\n| date = 20200513.0\n"
            "}}</onlyinclude>\n[[Category: Fedora Templates]]"
        )
        assert fakesave.call_args[0][2] == "relval: update to current event"
        assert fakesave.call_args[1]["createonly"] is None
        assert fakesave.call_args[0][0].name == "Template:CurrentFedora-IoTCompose"

    def test_event_from_page(self, fakemwp):
        """Test for from_page classmethod."""
        pg = self.site.pages["Test Results:Fedora 27 Branched 20171104.n.0 Base"]
        ev = wikitcms.event.NightlyEvent.from_page(pg)
        assert ev.version == "27 Branched 20171104.n.0"
        assert ev.dist == "Fedora"
        # modular
        pg = self.site.pages["Test Results:Fedora-Modular 27 Branched 20171123.n.1 Base"]
        ev = wikitcms.event.NightlyEvent.from_page(pg)
        assert ev.version == "27 Branched 20171123.n.1"
        assert ev.dist == "Fedora-Modular"
        # IoT
        pg = self.site.pages["Test Results:Fedora-IoT 33 RC 20200513.0 General"]
        ev = wikitcms.event.NightlyEvent.from_page(pg)
        assert ev.version == "33 RC 20200513.0"
        assert ev.dist == "Fedora-IoT"

    def test_event_category_page(self, fakemwp):
        """Test for category_page property."""
        # compose
        event = wikitcms.event.ComposeEvent(self.site, "27", "Beta", "1.2")
        cat = event.category_page
        assert isinstance(cat, wikitcms.listing.ValidationCategory)
        # this is a sufficient proxy that we got the right thing
        assert cat.checkname == "Category:Fedora 27 Beta Test Results"
        # modular compose
        event = wikitcms.event.ComposeEvent(self.site, "27", "Beta", "1.5", dist="Fedora-Modular")
        cat = event.category_page
        assert cat.checkname == "Category:Fedora-Modular 27 Beta Test Results"
        # nightly
        event = wikitcms.event.NightlyEvent(self.site, "27", "Branched", "20171104.n.0")
        cat = event.category_page
        assert cat.checkname == "Category:Fedora 27 Nightly Test Results"
        # modular nightly
        event = wikitcms.event.NightlyEvent(
            self.site, "27", "Branched", "20171123.n.1", dist="Fedora-Modular"
        )
        cat = event.category_page
        assert cat.checkname == "Category:Fedora-Modular 27 Nightly Test Results"
        # IoT
        event = wikitcms.event.NightlyEvent(self.site, "33", "RC", "20200513.0", dist="Fedora-IoT")
        cat = event.category_page
        assert cat.checkname == "Category:Fedora-IoT 33 Nightly Test Results"

    # yes, I looked up the correct date. don't make fun of me!
    @mock.patch("wikitcms.page.ComposePage.creation_date", "20170922")
    def test_event_creation_date(self, fakemwp):
        """Test for creation_date property/attribute."""
        # compose
        evp = self.site.pages["Test Results:Fedora 27 Beta 1.2 Base"]
        with mock.patch("wikitcms.event.ComposeEvent.result_pages", [evp]):
            event = wikitcms.event.ComposeEvent(self.site, "27", "Beta", "1.2")
            assert event.creation_date == "20170922"
        with mock.patch("wikitcms.event.ComposeEvent.result_pages", []):
            # this is when the event doesn't exist
            event = wikitcms.event.ComposeEvent(self.site, "27", "Beta", "1.2")
            assert event.creation_date == ""
        # nightly - it's just an attribute here
        event = wikitcms.event.NightlyEvent(self.site, "27", "Branched", "20171104.n.0")
        assert event.creation_date == "20171104"
