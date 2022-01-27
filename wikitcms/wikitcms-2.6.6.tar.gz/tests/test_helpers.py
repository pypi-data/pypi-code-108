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

"""Tests for helpers.py."""

from unittest import mock

import pytest

import wikitcms.helpers as hl

# Only triplet_sort can handle these
HARD_SORTS = [
    ("9", "Beta", "RC1"),
    ("10", "Alpha", "TC1"),
    ("10", "Alpha", "TC2"),
    ("10", "Alpha", "TC10"),
    ("10", "Alpha", "RC1"),
]

# Weird old ones
OLD_SORTS = [
    ("12", "Alpha", "TCRegression"),
    ("12", "Beta", "PreBeta"),
    ("12", "Beta", "TC"),
    ("12", "Final", "Pre-RC"),
    ("12", "Final", "RC1"),
    ("21", "Rawhide", "2014 06"),
    ("21", "Nightly", "2014 08"),
    ("21", "Alpha", "TC1"),
]

# Standard stuff
STANDARD_SORTS = [
    ("22", "Final", "RC1"),
    ("22", "Postrelease", "20151015"),
    ("23", "Rawhide", "20150607"),
    ("23", "Branched", "20150717"),
    ("23", "Alpha", "TC1"),
    ("23", "Alpha", "TC2"),
    ("23", "Alpha", "RC1"),
    ("23", "Beta", "TC1"),
    ("23", "Beta", "TC2"),
    ("23", "Final", "RC1"),
    ("23", "Final", "RC1.1"),
    ("24", "Rawhide", "20160314.n.0"),
    ("24", "Rawhide", "20160314.n.1"),
    ("24", "Branched", "20160314.n.0"),
    ("24", "Branched", "20160318.n.0"),
    ("24", "Alpha", "1.1"),
    ("24", "Alpha", "1.2"),
    ("24", "Alpha", "2.1"),
    ("24", "Beta", "1.1"),
]


class TestHelpers:
    """Tests for the functions in helpers.py."""

    def test_fedora_release_sort(self):
        """Test for fedora_release_sort."""
        rels = OLD_SORTS + STANDARD_SORTS
        for (num, rel) in enumerate(rels[1:], 1):
            prevrel = rels[num - 1]
            assert hl.fedora_release_sort(" ".join(rel)) > hl.fedora_release_sort(" ".join(prevrel))

    def test_triplet_sort(self):
        """Test for triplet_sort and triplet_unsort."""
        rels = HARD_SORTS + OLD_SORTS + STANDARD_SORTS
        for (num, rel) in enumerate(rels[1:], 1):
            prevrel = rels[num - 1]
            sorttup = hl.triplet_sort(*rel)
            assert sorttup > hl.triplet_sort(*prevrel)
            assert hl.triplet_unsort(*sorttup) == (rel)

    def test_rreplace(self):
        """Tests for rreplace."""
        foos = "foofoofoo"
        bars = "barbarbar"
        assert hl.rreplace(bars, "bar", "foo", 1) == "barbarfoo"
        assert hl.rreplace(bars, "bar", "foo", 2) == "barfoofoo"
        assert hl.rreplace(bars, "bar", "foo", 3) == "foofoofoo"
        assert hl.rreplace(bars, "bar", "foo", 4) == "foofoofoo"
        assert hl.rreplace(foos, "bar", "foo", 1) == "foofoofoo"
        assert hl.rreplace(foos, "bar", "foo", 3) == "foofoofoo"

    def test_normalize(self):
        """Tests for normalize."""
        wikitext = "Foo_Bar Moo"
        oktext = "foo_bar_moo"
        assert hl.normalize(wikitext) == oktext
        assert hl.normalize(oktext) == oktext

    def test_find_bugs(self):
        """Test for find_bugs."""
        # text taken from a real Test Day page -
        # 2011-03-24_Power_Management - with a [[rhbug link
        # added as I couldn't find a page with all three. Some non-bug
        # text to make sure it's not erroneously processed, and an
        # example-type bug to make sure it's filtered
        text = """
| {{result|warn}} [https://bugzilla.redhat.com/show_bug.cgi?id=690177 switching of profile waiting forever] 
| [http://www.smolts.org/client/show/pub_1c75a13c-b42f-47b8-b886-a4ebf2c41305 HW]
| {{result|pass}} [https://fedoraproject.org/wiki/File:Pm-test-day-20110324-pub_54d92a30-b0cc-46ed-991c-00b3117ddb3a.txt bugreport]
| {{result|warn}} <ref> {{bz|690194}} - Probably what Albertpool is seeing</ref>
| {{result|warn}} <ref> [[rhbug:1239865|some rhbug link]]
{{bz|123456}} example bug
"""
        assert hl.find_bugs(text) == set(("690177", "690194", "1239865"))

    # this avoids needing network access and the value changing
    @mock.patch("fedfind.helpers.get_current_release", return_value=23, autospec=True)
    # this avoids needing network access
    @mock.patch("fedfind.release.Production.cid", "Fedora-24-20160314.1")
    @mock.patch("fedfind.release.Production.label", "Alpha-1.2")
    def test_cid_to_event(self, fakecurr):
        """Tests for cid_to_event."""
        bran = hl.cid_to_event("Fedora-24-20160314.n.2")
        assert bran == ("Fedora", "24", "Branched", "20160314.n.2")
        rawh = hl.cid_to_event("Fedora-Rawhide-20160314.n.1")
        assert rawh == ("Fedora", "24", "Rawhide", "20160314.n.1")
        prod = hl.cid_to_event("Fedora-24-20160314.1")
        assert prod == ("Fedora", "24", "Alpha", "1.2")
        # check that we fail intentionally on non-'Fedora' composes
        with pytest.raises(ValueError):
            hl.cid_to_event("Fedora-Cloud-28-20180711.0")
        # check that we fail intentionally on updates-ut composes
        with pytest.raises(ValueError):
            hl.cid_to_event("Fedora-27-updates-testing-20180711.0")
        with pytest.raises(ValueError):
            hl.cid_to_event("Fedora-27-updates-20180711.0")

    @mock.patch("fedfind.helpers.get_current_release", return_value=23, autospec=True)
    @mock.patch("fedfind.release.Production.cid", "Fedora-24-20160314.1")
    @mock.patch("fedfind.release.Production.label", "")
    def test_cid_to_event_fail(self, fakecurr):
        """Test to check cid_to_event fails if we cannot determine
        label for production compose.
        """
        with pytest.raises(ValueError):
            hl.cid_to_event("Fedora-24-20160314.1")


# vim: set textwidth=100 ts=8 et sw=4:
