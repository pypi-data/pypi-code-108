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
#
"""This file kind of shadows mwclient's listing.py, creating modified
versions of several of its classes. The point is to provide generators
similar to mwclient's own, but which return wikitcms page/category
instances when appropriate, falling through to mwclient instances
otherwise.
"""

import re

import mwclient.listing

import wikitcms.page

# exceptions: the wikitcms getter raises these when it fails rather than
# just returning None, so the generators can use try/except blocks to
# handle both this case and the case (which shouldn't ever happen, but
# just in case) where they're being used on something other than a list
# of pages.


class NoPageWarning(Exception):
    """Exception raised when the tcmswiki getter can't find a matching
    page. Not really an error, should always be handled.
    """

    def __init__(self, page):
        super(NoPageWarning, self).__init__()
        self.page = page

    def __str__(self):
        return f"Could not produce a wikitcms page for: {self.page}"


class PageCheckWarning(Exception):
    """Exception raised when the wikitcms getter finds a matching page,
    but the page name the class generators from the page's various
    attributes doesn't match the page name the getter was given. Should
    usually be handled (and an mwclient Page instance returned instead).
    """

    def __init__(self, frompage, topage):
        super(PageCheckWarning, self).__init__()
        self.frompage = frompage
        self.topage = topage

    def __str__(self):
        return f"Expected page name {self.frompage} does not match source page name {self.topage}"


def _check_page(name, page):
    """A convenience function for _get_tcms sanity check."""
    if page.checkname == name:
        return page
    raise PageCheckWarning(page.checkname, name)


class TcmsGeneratorList(mwclient.listing.GeneratorList):
    """A GeneratorList which returns wikitcms page (and category etc.)
    instances when appropriate. _get_tcms is implemented as a separate
    function so TcmsPageList can use the discovery logic.
    """

    def __next__(self):
        # We can't get the next entry from mwl.List ourselves, try and
        # handle it, then pass it up to our parent if we can't, because
        # parent's next() gets the next entry from mwl.List itself, so
        # in that scenario, one list item gets skipped. Either we
        # entirely clone next() with our own additions, or we let it
        # fire and then override the result if we can. Using nxt._info
        # is bad, but super.next() doesn't return that, and the page
        # instance doesn't expose it any other way. We could just use
        # the name, but if you don't pass info when instantiating a
        # Page, it has to hit the API during init to reconstruct info,
        # and that causes a massive performance hit.
        nxt = super(TcmsGeneratorList, self).__next__()
        try:
            # pylint: disable=protected-access
            return self._get_tcms(nxt.name, nxt._info)
        except (NoPageWarning, PageCheckWarning):
            return nxt

    def _get_tcms_testresults(self, name, info):
        """The main match logic for Test Results pages. Called by
        _get_tcms when it finds a Test Results page.
        """
        nightly_patt = re.compile(
            r"Test Results:Fedora(-\w+)? (\d{1,3}) "
            r"(Rawhide|Nightly|Branched) "
            r"(\d{8,8}(\.n\.\d+)?|\d{4,4} \d{2,2}) "
            r"(.+)$"
        )
        # IoT pages are slightly weird, as IoT composes are production
        # but we treat them as nightlies
        iot_nightly_patt = re.compile(r"Test Results:Fedora-IoT (\d{1,3}) RC (\d{8,8}\.\d+) (.+)$")
        accept_patt = re.compile(
            r"Test Results:Fedora (\d{1,3}) ([^ ]+?) (Rawhide |)Acceptance Test " r"(\d{1,2})$"
        )
        ms_patt = re.compile(r"Test Results:Fedora(-\w+)? (\d{1,3}) ([^ ]+?) ([^ ]+?) (.+)$")

        # Modern standard nightly compose event pages, and F21-era
        # monthly Rawhide/Branched test pages
        match = nightly_patt.match(name)
        if match:
            if match.group(6) == "Summary":
                # we don't really ever need to do anything to existing
                # summary pages, and instantiating one from here is kinda
                # gross, so just fall through
                raise NoPageWarning(name)
            dist = "Fedora"
            if match.group(1):
                dist += match.group(1)
            page = wikitcms.page.NightlyPage(
                self.site,
                release=match.group(2),
                testtype=match.group(6),
                milestone=match.group(3),
                compose=match.group(4),
                info=info,
                dist=dist,
            )
            return _check_page(name, page)

        match = iot_nightly_patt.match(name)
        if match:
            if match.group(3) == "Summary":
                # we don't really ever need to do anything to existing
                # summary pages, and instantiating one from here is kinda
                # gross, so just fall through
                raise NoPageWarning(name)
            page = wikitcms.page.NightlyPage(
                self.site,
                release=match.group(1),
                testtype=match.group(3),
                milestone="RC",
                compose=match.group(2),
                info=info,
                dist="Fedora-IoT",
            )
            return _check_page(name, page)

        match = accept_patt.match(name)
        if match:
            # we don't handle these, yet.
            raise NoPageWarning(name)

        # milestone compose event pages
        match = ms_patt.match(name)
        if match:
            if match.group(5) == "Summary":
                raise NoPageWarning(name)
            dist = "Fedora"
            if match.group(1):
                dist += match.group(1)
            page = wikitcms.page.ComposePage(
                self.site,
                release=match.group(2),
                testtype=match.group(5),
                milestone=match.group(3),
                compose=match.group(4),
                info=info,
                dist=dist,
            )
            return _check_page(name, page)

        # in case we matched nothing...
        raise NoPageWarning(name)

    def _get_tcms_category(self, name, info):
        """The main match logic for Category pages. Call by _get_tcms
        when it finds a Category page.
        """
        cat_patt = re.compile(r"Category:Fedora(-\w+)? (\d{1,3}) " r"(.*?) *?Test Results$")
        tdcat_patt = re.compile(r"Category:Fedora (\d{1,3}) Test Days$")

        # test result categories
        match = cat_patt.match(name)
        if match:
            dist = "Fedora"
            if match.group(1):
                dist += match.group(1)
            if not match.group(3):
                page = ValidationCategory(self.site, match.group(2), info=info, dist=dist)
                return _check_page(name, page)

            if match.group(3) == "Nightly":
                page = ValidationCategory(
                    self.site, match.group(2), nightly=True, info=info, dist=dist
                )
                return _check_page(name, page)

            # otherwise...
            page = ValidationCategory(
                self.site, match.group(2), match.group(3), info=info, dist=dist
            )
            return _check_page(name, page)

        # Test Day categories
        match = tdcat_patt.match(name)
        if match:
            page = TestDayCategory(self.site, match.group(1), info=info)
            return _check_page(name, page)

        # in case we matched nothing...
        raise NoPageWarning(name)

    def _get_tcms_testday(self, name, info):
        """The main match logic for Test Day pages. Called by
        _get_tcms when it finds a Test Day page.
        """
        testday_patt = re.compile(r"Test Day:(\d{4}-\d{2}-\d{2}) *(.*)$")
        # FIXME: There's a few like this, handle 'em sometime
        # testday2_patt = re.compile(u'Test Day:(.+) (\d{4}-\d{2}-\d{2})$')

        match = testday_patt.match(name)
        if match:
            page = wikitcms.page.TestDayPage(self.site, match.group(1), match.group(2), info=info)
            return _check_page(name, page)

        # in case we matched nothing...
        raise NoPageWarning(name)

    def _get_tcms(self, name, info=()):
        """This is where the meat starts: we are going to parse the
        page name and see if it looks like a page we have a class for,
        if so, we will instantiate the class appropriately, check the
        name we get matches the page we're actually running on, and
        return the instance if so. This method quickly sorts pages we
        *might* match into various categories then calls one of the
        specialized methods above to do the rest of the work. At all
        points, if we decide we can't match the page, we raise
        NoPageWarning, which will cause whatever is using us to fall
        through to mwclient.
        """
        if isinstance(name, int):
            # we'll have to do a wiki roundtrip, as we need the text
            # name.
            page = wikitcms.page.Page(self.site, name)
            name = page.name
        name = name.replace("_", " ")
        # quick non-RE checks to see if we'll ever match (and filter
        # out some 'known bad' pages)
        if name.startswith("Test Results:"):
            return self._get_tcms_testresults(name, info)
        if name.startswith("Category:"):
            return self._get_tcms_category(name, info)
        if name.startswith("Test Day:") and not name.endswith("/ru"):
            if not "metadata" in name.lower() and not "rendercheck" in name.lower():
                return self._get_tcms_testday(name, info)

        # otherwise, we'll just bail out here
        raise NoPageWarning(name)


class TcmsPageList(mwclient.listing.PageList, TcmsGeneratorList):
    """A version of PageList which returns wikitcms page (and category
    etc.) objects when appropriate.
    """

    def get(self, name, info=()):
        modname = name
        if self.namespace:
            modname = f"{self.site.namespaces[self.namespace]}:{name}"
        try:
            return self._get_tcms(modname, info)
        except (NoPageWarning, PageCheckWarning):
            return super(TcmsPageList, self).get(name, info)


class TcmsCategory(wikitcms.page.Page, TcmsGeneratorList):
    """A modified category class - just as mwclient's Category class
    inherits from both its Page class and its GeneratorList class,
    acting as both a page and a generator returning the members of
    the category, so this inherits from wikitcms' Page and
    TcmsGeneratorList. You can produce the page contents with pg.Page
    write() method, and you can use it as a generator which returns
    the category's members, as wikitcms class instances if appropriate
    or mwclient class instances otherwise. It works recursively - if
    a member of a ValidationCategory is itself a test category, you'll
    get another ValidationCategory instance. There are sub-classes for
    various particular types of category (Test Days, validation, etc.)
    """

    def __init__(self, site, wikiname, info=None):
        super(TcmsCategory, self).__init__(site, wikiname, info=info)
        TcmsGeneratorList.__init__(self, site, "categorymembers", "cm", gcmtitle=self.name)


class ValidationCategory(TcmsCategory):
    """A category class (inheriting from TcmsCategory) for validation
    test result category pages. If nightly is True, this will be a
    category for test results from Rawhide or Branched nightly builds
    for the given release. Otherwhise, if milestone is passed, this
    will be a category for the given milestone, and if it isn't, it
    will be the top-level category for the given release.
    """

    # no, pylint, this is just the right number of arguments
    # pylint: disable=too-many-arguments
    def __init__(self, site, release, milestone=None, nightly=False, info=None, dist="Fedora"):
        shortdist = dist[7:]
        if nightly is True:
            wikiname = f"Category:{dist} {release} Nightly Test Results"
            self.seedtext = (
                "{{Validation results milestone category"
                f"|release={release}|nightly=true|dist={shortdist}}}}}"
            )

            self.summary = (
                "Relval bot-created validation result category "
                f"page for {dist} {release} nightly results"
            )
        elif milestone:
            wikiname = f"Category:{dist} {release} {milestone} Test Results"
            self.seedtext = (
                f"{{{{Validation results milestone category|release={release}"
                f"|milestone={milestone}|dist={shortdist}}}}}"
            )
            self.summary = (
                f"Relval bot-created validation result category page for {dist} "
                f"{release} {milestone}"
            )
        else:
            wikiname = f"Category:{dist} {release} Test Results"
            self.seedtext = (
                "{{Validation results milestone category" f"|release={release}|dist={shortdist}}}}}"
            )
            self.summary = (
                "Relval bot-created validation result category page for " f"{dist} {release}"
            )

        super(ValidationCategory, self).__init__(site, wikiname, info=info)


class TestDayCategory(TcmsCategory):
    """A category class (inheriting from TcmsCategory) for Test Day
    category pages.
    """

    def __init__(self, site, release, info=None):
        wikiname = f"Category:Fedora {str(release)} Test Days"
        self.seedtext = (
            f"This category contains all the Fedora {str(release)} [[QA/Test_Days|Test "
            "Day]] pages. A calendar of the Test Days can be found ["
            "https://apps.fedoraproject.org/calendar/list/QA/?subject=Test+Day"
            " here].\n\n[[Category:Test Days]]"
        )
        self.summary = "Created page (via wikitcms)"
        super(TestDayCategory, self).__init__(site, wikiname, info=info)


# vim: set textwidth=100 ts=8 et sw=4:
