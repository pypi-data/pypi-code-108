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

"""Classes that describe distribution releases are defined here."""

import wikitcms.page
import wikitcms.listing


class Release:
    """Class for a Fedora release. wiki is a wikitcms site object.
    Release is a string containing a Fedora release version (e.g. 21).
    """

    def __init__(self, release, wiki, dist="Fedora"):
        self.release = release
        self.dist = dist
        self.category_name = f"Category:{self.dist} {self.release} Test Results"
        self.site = wiki

    @property
    def testday_pages(self):
        """All Test Day pages for this release (as a list)."""
        cat = self.site.pages[f"Category:Fedora {self.release} Test Days"]
        return [page for page in cat if isinstance(page, wikitcms.page.TestDayPage)]

    def milestone_pages(self, milestone=None):
        """If no milestone, will give all release validation pages for
        this release (as a generator). If a milestone is given, will
        give validation pages only for that milestone. Note that this
        works by category; you may get somewhat different results by
        using page name prefixes.
        """
        cat = wikitcms.listing.ValidationCategory(
            self.site, self.release, milestone, dist=self.dist
        )
        pgs = self.site.walk_category(cat)
        return (p for p in pgs if isinstance(p, wikitcms.page.ValidationPage))


# vim: set textwidth=100 ts=8 et sw=4:
