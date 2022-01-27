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

"""Tests for release.py."""

from unittest import mock

import wikitcms.release
import wikitcms.wiki


class TestRelease:
    """Tests for Release instances."""

    # the "fjajah" is just to make sure we're running offline; if I
    # screw up and add a test that hits the network it"ll cause the
    # tests to hang/fail instead of succeeding a bit slower
    site = wikitcms.wiki.Wiki("fjajah", do_init=False, force_login=False)

    def test_release_init(self):
        """Tests for Release.__init__."""
        rl = wikitcms.release.Release("32", self.site)
        # __init__ stuff
        assert rl.release == "32"
        assert rl.dist == "Fedora"
        assert rl.category_name == "Category:Fedora 32 Test Results"
        # modular
        rl = wikitcms.release.Release("27", self.site, dist="Fedora-Modular")
        assert rl.release == "27"
        assert rl.dist == "Fedora-Modular"
        assert rl.category_name == "Category:Fedora-Modular 27 Test Results"

    def test_testday_pages(self, fakemwp):
        """Test for Release.testday_pages. There is actually quite a
        lot going on in this small method, but most of the hard work
        is tested in mwclient upstream and in the listing tests; here
        we can just assume the generator magic works right.
        """
        rl = wikitcms.release.Release("32", self.site)
        tdp = self.site.pages["Test Day:2016-10-24 Cloud"]
        tdp2 = self.site.pages["Test Day:2013-11-05 Printing"]
        other = self.site.pages["Somepage"]
        with mock.patch.object(
            self.site, "pages", {"Category:Fedora 32 Test Days": [tdp, tdp2, other]}
        ):
            assert rl.testday_pages == [tdp, tdp2]

    def test_milestone_pages(self, fakemwp):
        """Test for Release.milestone_pages. Similar to testday_pages,
        we just trust the generator magic here and test it elsewhere.
        """
        rl = wikitcms.release.Release("32", self.site)
        vp1 = self.site.pages["Test Results:Fedora 32 Branched 20200212.n.1 Desktop"]
        vp2 = self.site.pages["Test Results:Fedora 32 Beta 1.2 Base"]
        other = self.site.pages["Somepage"]
        with mock.patch("wikitcms.wiki.Wiki.walk_category", return_value=[vp1, vp2, other]):
            assert list(rl.milestone_pages()) == [vp1, vp2]
