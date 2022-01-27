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

# I disagree, pylint! Shut up!
# pylint: disable=too-many-arguments, too-many-instance-attributes

"""Classes that describe test events."""

import abc
import logging

from cached_property import cached_property
import fedfind.helpers
import fedfind.release
import mwclient.errors

from wikitcms.exceptions import FedfindNotFoundError
import wikitcms.helpers
import wikitcms.listing
import wikitcms.page

logger = logging.getLogger(__name__)


class ValidationEvent:
    """A parent class for different types of release validation event.
    site must be an instance of wikitcms.Wiki, already with
    appropriate access rights for any actions to be performed (i.e.
    things instantiating an Event are expected to do site.login
    themselves if needed). Required attributes: shortver,
    category_page. "dist" lets us create multiple event streams for
    different compose streams: it defaults to "Fedora", which gives
    us event and page names for the main stream of composes and Fedora
    releases, but can be set to e.g. "Fedora IoT" for a validation
    event for an IoT compose. The provided string is simply included
    in page names, category names and so on.
    """

    __metaclass__ = abc.ABCMeta

    def __init__(self, site, release, milestone="", compose="", dist="Fedora"):
        self.site = site
        self.release = release
        self.milestone = str(milestone)
        try:
            self.compose = fedfind.helpers.date_check(compose, fail_raise=True, out="str")
        except ValueError:
            self.compose = str(compose)
        self.dist = wikitcms.helpers.validate_dist(dist)
        self.version = f"{self.release} {self.milestone} {self.compose}"
        # Sorting helpers. sortname is a string, sorttuple is a
        # 4-tuple. sorttuple is more reliable. See the function docs.
        self.sortname = wikitcms.helpers.fedora_release_sort(self.version)
        self.sorttuple = wikitcms.helpers.triplet_sort(self.release, self.milestone, self.compose)

    @abc.abstractproperty
    def _current_content(self):
        """The content for the CurrentFedoraCompose template for
        this test event.
        """

    @abc.abstractproperty
    def _pagetype(self):
        """The ValidationPage class to be used for this event's pages
        (for use by valid_pages).
        """

    @abc.abstractproperty
    def category_page(self):
        """The category page for this event. Is a property because
        page instantiation requires a remote trip.
        """

    @property
    def result_pages(self):
        """A list of wikitcms page objects for currently-existing
        pages that are a part of this test event, according to the
        naming convention.
        """
        pages = self.site.allresults(prefix=f"{self.dist} {self.version} ")
        return [p for p in pages if isinstance(p, wikitcms.page.ValidationPage)]

    @property
    def download_page(self):
        """The DownloadPage for this event. Is a property because page
        instantiation requires a remote trip.
        """
        return wikitcms.page.DownloadPage(self.site, self, dist=self.dist)

    @property
    def ami_page(self):
        """The AMIPage for this event. Is a property because page
        instantiation requires a remote trip.
        """
        return wikitcms.page.AMIPage(self.site, self, dist=self.dist)

    @property
    def parent_category_page(self):
        """The parent category page for this event. Is a property for
        the same reason as download_page.
        """
        return wikitcms.listing.ValidationCategory(self.site, self.release, dist=self.dist)

    @property
    def valid_pages(self):
        """A list of the expected possible result pages (as
        page.ValidationPage objects) for this test event, derived from
        the available test types and the naming convention.
        """
        types = self.site.get_testtypes(dist=self.dist)
        return [
            self._pagetype(
                self.site,
                self.release,
                typ,
                milestone=self.milestone,
                compose=self.compose,
                dist=self.dist,
            )
            for typ in types
        ]

    @property
    def summary_page(self):
        """The page.SummaryPage object for the event's result summary
        page. Very simple property, but not set in __init__ as the
        summary page object does (slow) wiki roundtrips in  __init__.
        """
        return wikitcms.page.SummaryPage(self.site, self, dist=self.dist)

    @cached_property
    def ff_release(self):
        """A fedfind release object matching this event."""
        # note: fedfind has a hack that parses date and respin out
        # of a dot-separated compose, since wikitcms smooshes them
        # into the compose value.
        try:
            return fedfind.release.get_release(
                release=self.release, milestone=self.milestone, compose=self.compose, dist=self.dist
            )
        except ValueError as err:
            try:
                if self._cid:
                    return fedfind.release.get_release(cid=self._cid)
            except AttributeError:
                raise FedfindNotFoundError(err)
            raise FedfindNotFoundError(err)

    @property
    def ff_release_images(self):
        """A fedfind release object matching this event, that has
        images. If we can't find one, raise an exception. For the
        base class this just acts as a check on ff_release; it does
        something more clever in ComposeEvent.
        """
        rel = self.ff_release
        if rel.all_images:
            return rel
        err = f"Could not find fedfind release with images for event {self.version}"
        raise FedfindNotFoundError(err)

    def update_current(self):
        """Make the CurrentFedoraCompose template on the wiki point to
        this event. The template is used for the Current (testtype)
        Test redirect pages which let testers find the current results
        pages, and for other features of wikitcms/relval. Children
        must define _current_content.
        """
        content = "{{tempdoc}}\n<onlyinclude>{{#switch: {{{1|full}}}\n"
        content += self._current_content
        content += "}}</onlyinclude>\n[[Category: Fedora Templates]]"
        curr = self.site.pages[f"Template:Current{self.dist}Compose"]
        curr.save(content, "relval: update to current event", createonly=None)

    def create(self, testtypes=None, force=False, current=True, check=False):
        """Create the event, by creating its validation pages,
        summary page, download page, category pages, and updating the
        current redirects. 'testtypes' can be an iterable that limits
        creation to the specified testtypes. If 'force' is True, pages
        that already exist will be recreated (destroying any results
        on them). If 'current' is False, the current redirect pages
        will not be updated. If 'check' is true, we check if any
        result page already exists first, and bail immediately if so
        (so we don't start creating pages then hit one that exists and
        fail half-way through, for things that don't want that.) 'cid'
        can be set to a compose ID, this is for forcing the compose
        location at event creation time when we know we're not going
        to be able to find it any way and is a short-term hack that
        will be removed.
        """
        logger.info("Creating validation event %s", self.version)
        createonly = True
        if force:
            createonly = None
        pages = self.valid_pages
        if testtypes:
            logger.debug("Restricting to testtypes %s", " ".join(testtypes))
            pages = [pag for pag in pages if pag.testtype in testtypes]
        if not pages:
            raise ValueError("No result pages to create! Wrong test type?")
        if check:
            if any(pag.text() for pag in pages):
                raise ValueError("A result page already exists!")

        # NOTE: download page creation for ComposeEvents will only
        # work if:
        # * the compose has being synced to stage, OR
        # * the compose has been imported to PDC, OR
        # * you used get_validation_event and passed it a cid
        # Otherwise, the event will be created, but the download page
        # will not.
        pages.extend(
            (
                self.summary_page,
                self.download_page,
                self.ami_page,
                self.category_page,
                self.parent_category_page,
            )
        )

        def _handle_existing(err):
            """We need this in two places, so."""
            if err.args[0] == "articleexists":
                # no problem, just move on.
                logger.info(
                    "Page already exists, and forced write was not " "requested! Not writing."
                )
            else:
                raise err

        for pag in pages:
            try:
                # stage 1 - create page
                logger.info("Creating page %s", pag.name)
                pag.write(createonly=createonly)
            except mwclient.errors.APIError as err:
                _handle_existing(err)
            except FedfindNotFoundError:
                # this happens if download page couldn't be created
                # because fedfind release couldn't be found
                logger.warning(
                    "Could not create download page for event %s as fedfind release "
                    "was not found!"
                )

            # stage 2 - update current. this is split so if we hit
            # 'page already exists', we don't skip update_current
            if current and hasattr(pag, "update_current"):
                logger.info("Pointing Current redirect to above page")
                pag.update_current()

        if current:
            try:
                # update CurrentFedoraCompose
                logger.info("Updating CurrentFedoraCompose")
                self.update_current()
            except mwclient.errors.APIError as err:
                _handle_existing(err)

    @classmethod
    def from_page(cls, pageobj):
        """Return the ValidationEvent object for a given ValidationPage
        object.
        """
        return cls(
            pageobj.site,
            pageobj.release,
            pageobj.milestone,
            pageobj.compose,
            dist=pageobj.dist,
        )


class ComposeEvent(ValidationEvent):
    """An Event that describes a release validation event - that is,
    the testing for a particular nightly, test compose or release
    candidate build.
    """

    def __init__(self, site, release, milestone, compose, dist="Fedora", cid=""):
        super(ComposeEvent, self).__init__(
            site, release, milestone=milestone, compose=compose, dist=dist
        )
        # this is a little hint that gets set via get_validation_event
        # when getting a page or event by cid; it helps us find the
        # fedfind release for the event if the compose is not yet in
        # PDC or synced to stage
        self._cid = cid
        self.shortver = f"{self.milestone} {self.compose}"

    @property
    def category_page(self):
        """The category page for this event. Is a property because
        page instantiation requires a remote trip.
        """
        return wikitcms.listing.ValidationCategory(
            self.site, self.release, self.milestone, dist=self.dist
        )

    @property
    def _current_content(self):
        """The content for the CurrentFedoraCompose template for
        this test event.
        """
        return (
            f"| full = {self.version}\n| release = {self.release}\n"
            f"| milestone = {self.milestone}\n| compose = {self.compose}\n| date =\n"
        )

    @property
    def _pagetype(self):
        """For a ComposeEvent, obviously, ComposePage."""
        return wikitcms.page.ComposePage

    @cached_property
    def creation_date(self):
        """We need this for ordering and determining delta between
        this event and a potential new nightly event, if this is the
        current event. Return creation date of the first result page
        for the event, or "" if it doesn't exist.
        """
        try:
            return self.result_pages[0].creation_date
        except IndexError:
            # event doesn't exist
            return ""

    @property
    def ff_release_images(self):
        """A fedfind release object matching this event, that has
        images. If we can't find one, raise an exception. Here, we
        try getting the release by (release, milestone, compose), but
        if that release has no images - which happens in the specific
        case that we've just created an event for a candidate compose
        which has not yet been synced to stage - and we have the cid
        hint, we try getting a release by cid instead, which should
        find the compose in kojipkgs (a fedfind Production rather than
        Compose).
        """
        rel = self.ff_release
        if rel.all_images:
            return rel

        if self._cid:
            rel = fedfind.release.get_release(cid=self._cid)
        if rel.all_images:
            return rel
        err = f"Could not find fedfind release with images for event {self.version}"
        raise FedfindNotFoundError(err)


class NightlyEvent(ValidationEvent):
    """An Event that describes a release validation event - that is,
    the testing for a particular nightly, test compose or release
    candidate build. Milestone should be 'Rawhide' or 'Branched'.
    Note that a Fedora release number attached to a Rawhide nightly
    compose is an artificial concept that can be considered a Wikitcms
    artifact. Rawhide is a rolling distribution; its nightly composes
    do not really have a release number. What we do when we attach
    a release number to a Rawhide nightly validation test event is
    *declare* that, with our knowledge of Fedora's development cycle,
    we believe the testing of that Rawhide nightly constitutes a part
    of the release validation testing for that future release.
    """

    def __init__(self, site, release, milestone, compose, dist="Fedora"):
        super(NightlyEvent, self).__init__(
            site, release, milestone=milestone, compose=compose, dist=dist
        )
        self.shortver = self.compose
        self.creation_date = compose.split(".")[0]

    @property
    def category_page(self):
        """The category page for this event. Is a property because
        page instantiation requires a remote trip.
        """
        return wikitcms.listing.ValidationCategory(
            self.site, self.release, nightly=True, dist=self.dist
        )

    @property
    def _current_content(self):
        """The content for the CurrentFedoraCompose template for
        this test event.
        """
        return (
            f"| full = {self.version}\n| release = {self.release}\n"
            f"| milestone = {self.milestone}\n| compose =\n| date = {self.compose}\n"
        )

    @property
    def _pagetype(self):
        """For a NightlyEvent, obviously, NightlyPage."""
        return wikitcms.page.NightlyPage


# vim: set textwidth=100 ts=8 et sw=4:
