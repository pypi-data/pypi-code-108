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

"""The Wiki class here extends mwclient's Site class with additional
Wikitcms-specific functionality, and convenience features like stored
user credentials.
"""

from collections import namedtuple
import datetime
import re

import fedfind.helpers
import mwclient
from productmd.composeinfo import get_date_type_respin

import wikitcms.event
from wikitcms.exceptions import NoPageError, NotFoundError, TooManyError
import wikitcms.helpers
import wikitcms.listing
import wikitcms.page
import wikitcms.result

try:
    from openidc_client import OpenIDCClient
except ImportError:
    OpenIDCClient = None
try:
    from openidc_client.requestsauth import OpenIDCClientAuther
except ImportError:
    OpenIDCClientAuther = None


def _check_compose(compose):
    """Trivial checker shared between get_validation_event and
    get_validation_compose.
    """
    date = fedfind.helpers.date_check(compose, out="obj", fail_raise=False)
    # all nightlies after F24 branch are Pungi 4-style; plain date
    # is never a valid 'compose' value after that date, 2016-02-23
    if date and date < datetime.datetime(2016, 2, 23):
        return "date"

    # check if we have a valid Pungi4-style identifier
    try:
        (date, typ, respin) = get_date_type_respin(compose)
        if date and typ and respin is not None:
            if fedfind.helpers.date_check(date, fail_raise=False):
                return "date"
    except ValueError:
        pass

    # regex to match TC/RC names: TC1, RC10, RC23.6
    patt = re.compile(r"^[TR]C\d+\.?\d*$")
    if patt.match(compose.upper()):
        return "compose"

    # regex for Pungi 4 milestone composes: 1.1, 1.2 ... 10.10 ...
    patt = re.compile(r"^\d+\.\d+$")
    if patt.match(compose):
        return "compose"

    # if nothing matched, value is invalid
    raise ValueError(
        "Compose must be a TC/RC identifier (TC1, RC3...) for pre-"
        "Fedora 24 milestone composes, a Pungi 4 milestone compose"
        " identifier (1.1, 10.10...) for post-Fedora 23 milestone "
        "composes, a date in YYYYMMDD format (for pre-Fedora 24 "
        "nightlies) or a Pungi 4 nightly identifier (20160308.n.0"
        ", 20160310.n.2) for post-Fedora 23 nightlies."
    )


# I'd really like to use namedlist.namedtuple, but it isn't widely
# available.
class ResTuple(
    namedtuple(
        "ResTuple",
        "testtype release milestone compose "
        "testcase section testname env status user bugs "
        "comment bot cid dist",
    )
):
    """namedtuple (with default values) used for report_validation_
    results(). See that method's docstring for details.
    """

    # pylint: disable=too-many-arguments, too-many-locals
    def __new__(
        cls,
        testtype,
        release="",
        milestone="",
        compose="",
        testcase="",
        section="",
        testname="",
        env="",
        status="",
        user="",
        bugs="",
        comment="",
        bot=False,
        cid="",
        dist="Fedora",
    ):
        return super(ResTuple, cls).__new__(
            cls,
            testtype,
            release,
            milestone,
            compose,
            testcase,
            section,
            testname,
            env,
            status,
            user,
            bugs,
            comment,
            bot,
            cid,
            dist,
        )


class Wiki(mwclient.Site):
    """Extends the mwclient.Site class with some extra capabilities."""

    # parent class has a whole bunch of args, so just pass whatever
    # through. always init this the same as a regular mwclient.Site
    # instance. we have to disable this warning as the args must be
    # in this exact order to maintain compatibility
    # pylint: disable=keyword-arg-before-vararg
    def __init__(self, host="fedoraproject.org", *args, **kwargs):
        super(Wiki, self).__init__(host, *args, **kwargs)
        # override the 'pages' property so it returns wikitcms Pages when
        # appropriate
        self.pages = wikitcms.listing.TcmsPageList(self)

    @property
    def current_compose(self):
        """A dict of the key / value pairs from the CurrentFedora
        Compose page which is the canonical definition of the 'current'
        primary arch validation testing compose. You can usually expect
        keys full, release, date, milestone, and compose. The page is
        normally written by ValidationEvent.update_current().
        """
        return self.get_current_compose(dist="Fedora")

    @property
    def current_event(self):
        """The current event, as a ValidationEvent instance. Will be a
        ComposeEvent or a NightlyEvent."""
        return self.get_current_event(dist="Fedora")

    @property
    def current_modular_compose(self):
        """A dict of the key / value pairs from the CurrentFedora
        ModularCompose page which is the canonical definition of the
        'current' modular primary arch validation testing compose. You
        can usually expect keys full, release, date, milestone, and
        compose. The page is normally written by
        ValidationEvent.update_current().
        """
        return self.get_current_compose(dist="Fedora-Modular")

    @property
    def current_modular_event(self):
        """The current modular event, as a ValidationEvent instance.
        Will be a ComposeEvent or a NightlyEvent."""
        return self.get_current_event(dist="Fedora-Modular")

    @property
    def matrices(self):
        """A list of dicts representing pages in the test matrix
        template category. These are the canonical definition of
        'existing' test types. Done this way - rather than using the
        category object's ability to act as an iterator over its member
        page objects - because this method respects the sort order of
        the member pages, whereas the other does not. The sort order is
        used in creating the overview summary page.
        """
        return self.get_matrices(dist="Fedora")

    @property
    def testtypes(self):
        """Test types, derived from the matrix page names according to
        a naming convention. A list of strings.
        """
        return self.get_testtypes(dist="Fedora")

    @property
    def modular_matrices(self):
        """A list of dicts representing pages in the modular test
        matrix template category. These are the canonical definition of
        'existing' test types. Done this way - rather than using the
        category object's ability to act as an iterator over its member
        page objects - because this method respects the sort order of
        the member pages, whereas the other does not. The sort order is
        used in creating the overview summary page.
        """
        return self.get_matrices(dist="Fedora-Modular")

    @property
    def modular_testtypes(self):
        """Test types, derived from the matrix page names according to
        a naming convention. A list of strings.
        """
        return self.get_testtypes(dist="Fedora-Modular")

    def get_current_compose(self, dist="Fedora"):
        """A dict of the key / value pairs from the Current{dist}
        Compose page which is the canonical definition of the 'current'
        primary arch validation testing compose. You can usually expect
        keys full, release, date, milestone, and compose. The page is
        normally written by ValidationEvent.update_current().
        """
        wikitcms.helpers.validate_dist(dist)
        currdict = dict()
        valpatt = re.compile(r"^\| *?(\w+?) *?= *([\w .]*?) *$", re.M)
        page = self.pages[f"Template:Current{dist}Compose"]
        for match in valpatt.finditer(page.text()):
            currdict[match.group(1)] = match.group(2)
        return currdict

    def get_current_event(self, dist="Fedora"):
        """Returns the current event for the given dist as a
        ValidationEvent instance. May return None if there is no
        current event for the given dist (e.g. none has yet been
        created for that dist).
        """
        wikitcms.helpers.validate_dist(dist)
        curr = self.get_current_compose(dist=dist)
        if not curr:
            return None
        # Use of 'max' plus get_validation_event handles getting us
        # the right kind of event.
        return self.get_validation_event(
            release=curr["release"],
            milestone=curr["milestone"],
            compose=max(curr["date"], curr["compose"]),
            dist=dist,
        )

    def get_matrices(self, dist="Fedora"):
        """A list of dicts representing pages in the test matrix
        template category for the specified dist. These are the
        canonical definition of 'existing' test types. Done this way -
        rather than using the category object's ability to act as an
        iterator over its member page objects - because this method
        respects the sort order of the member pages, whereas the other
        does not. The sort order is used in creating the overview
        summary page.
        """
        wikitcms.helpers.validate_dist(dist)
        # dist names have a specific form, we expect a category derived
        # from the name to exist. If dist is "Fedora", we know the name
        if dist == "Fedora":
            catname = "Category:QA test matrix templates"
        else:
            # drop "Fedora-"
            dstring = dist[7:]
            catname = f"Category:QA {dstring} test matrix templates"
        category = self.pages[catname]
        return category.members(generator=False)

    def get_testtypes(self, dist="Fedora"):
        """Returns test types (as a list of strings) for a given dist,
        derived from the matrix page names for that dist.
        """
        wikitcms.helpers.validate_dist(dist)
        # drop "Fedora-"
        dstring = dist[7:]
        if dstring:
            dstring = f"{dstring} "
        return [
            m["title"].replace("Template:", "").replace(f" {dstring}test matrix", "")
            for m in self.get_matrices(dist=dist)
        ]

    def login(self, *args, **kwargs):  # pylint: disable=signature-differs
        """Login method, overridden to use openidc auth when necessary.
        This will open a browser window and run through FAS auth on
        the first use, then a token will be saved that will allow auth
        for a while, when the token expires, the web auth process will
        pop up again.
        """
        use_openidc = False
        # This probably breaks on private wikis, but wikitcms isn't
        # ever used with any of those, AFAIK.
        host = self.host
        if isinstance(host, (list, tuple)):
            host = host[1]
        if host.endswith("fedoraproject.org") and self.version[:2] >= (1, 29):
            use_openidc = True
        if not use_openidc:
            # just work like mwclient
            super(Wiki, self).login(*args, **kwargs)

        # Fedora wiki since upgrade to 1.29 doesn't allow native
        # mediawiki auth with FAS creds any more, it only allows
        # auth via OpenID Connect. For this case we set up an
        # openidc auther, call site_init() to trigger auth and
        # update the site properties, and return.
        if OpenIDCClient is None:
            raise ImportError("python-openidc-client is needed for OIDC")
        if OpenIDCClientAuther is None:
            raise ImportError("python-openidc-client 0.4.0 or higher is " "required for OIDC")
        client = OpenIDCClient(
            app_identifier="wikitcms",
            id_provider=f"https://id.{host}/openidc/",
            id_provider_mapping={"Token": "Token", "Authorization": "Authorization"},
            client_id="wikitcms",
            client_secret="notsecret",
            useragent="wikitcms",
        )

        auther = OpenIDCClientAuther(client, ["openid", "https://fedoraproject.org/wiki/api"])

        self.connection.auth = auther
        self.site_init()

    def add_to_category(self, page_name, category_name, summary=""):
        """Add a given page to a given category if it is not already a
        member. Takes strings for the names of the page and the
        category, not mwclient objects.
        """
        page = self.pages[page_name]
        text = page.text()
        if category_name not in text:
            text += f"\n[[{category_name}]]"
            page.save(text, summary, createonly=False)

    def walk_category(self, category):
        """Simple recursive category walk. Returns a list of page
        objects that are members of the parent category or its
        sub-categories, to any level of recursion. 14 is the Category:
        namespace.
        """
        pages = dict()
        for page in category:
            if page.namespace == 14:
                sub_pages = self.walk_category(page)
                for sub_page in sub_pages:
                    pages[sub_page.name] = sub_page
            else:
                pages[page.name] = page
        pages = pages.values()
        return pages

    def allresults(self, prefix=None, start=None, redirects="all", end=None):
        """A generator for pages in the Test Results: namespace,
        similar to mwclient's allpages, allcategories etc. generators.
        This is a TcmsPageList, so it returns wikitcms objects when
        appropriate. Note, if passing prefix, start or end, leave out
        the "Test Results:" part of the name.
        """
        gen = wikitcms.listing.TcmsPageList(
            self, prefix=prefix, start=start, namespace=116, redirects=redirects, end=end
        )
        return gen

    def alltestdays(self, prefix=None, start=None, redirects="all", end=None):
        """A generator for pages in the Test Day: namespace,
        similar to mwclient's allpages, allcategories etc. generators.
        This is a TcmsPageList, so it returns wikitcms objects when
        appropriate. Note, if passing prefix, start or end, leave out
        the "Test Day:" part of the name.
        """
        gen = wikitcms.listing.TcmsPageList(
            self, prefix=prefix, start=start, namespace=114, redirects=redirects, end=end
        )
        return gen

    def get_validation_event(self, release="", milestone="", compose="", cid="", dist="Fedora"):
        # we could factor this out but I think it's fine
        # pylint: disable=too-many-arguments, too-many-branches
        """Get an appropriate ValidationEvent object for the values
        given. As with get_validation_page(), this method is for
        sloppy instantiation of pages that follow the rules. This
        method has no required arguments and tries to figure out
        what you want from what you give it. It will raise errors
        if what you give it is impossible to interpret or if it
        tries and comes up with an inconsistent-seeming result.

        dist specifies a 'dist' (compose shortname) other than the
        default "Fedora" to find an event for. If you pass a compose
        ID as cid, any value you pass for dist will be ignored; we'll
        instead parse the dist value out of the compose ID.

        If you pass a numeric release, a milestone, and a valid
        compose (TC/RC or date), it will give you the appropriate
        event, whether it exists or not. All it really does in this
        case is pick NightlyEvent or ComposeEvent for you. If you
        don't fulfill any of those conditions, it'll need to do
        some guessing/assumptions, and in some of those cases it
        will only return an Event *that actually exists*, and may
        raise exceptions if you passed a particularly pathological
        set of values.

        If you don't pass a compose argument it will get the current
        event; if you passed either of the other arguments and they
        don't match the current event, it will raise an error. It
        follows that calling this with no arguments just gives you
        current_event.

        If you pass a date as compose with no milestone, it will see
        if there's a Rawhide nightly and return it if so, otherwise it
        will see if there's a Branched nightly and return that if so,
        otherwise raise an error. It follows that you can't get the
        page for an event that *doesn't exist yet* this way: you must
        instantiate it directly or call this method with a milestone.

        It will not attempt to guess a milestone for TC/RC composes;
        it will raise an exception in this case.

        The guessing bits require wiki roundtrips, so they will be
        slower than instantiating a class directly or using this
        method with sufficient information to avoid guessing.
        """
        if cid:
            (dist, release, milestone, compose) = wikitcms.helpers.cid_to_event(cid)
        if not compose or not release:
            # Can't really make an educated guess without a compose
            # and release, so just get the current event and return it
            # if it matches any other values passed.
            event = self.get_current_event(dist=dist)
            if release and event.release != release:
                raise ValueError(
                    f"get_validation_event(): Guessed event release {event.release} does "
                    f"not match requested release {release}"
                )
            if milestone and event.milestone != milestone:
                raise ValueError(
                    f"get_validation_event(): Guessed event milestone {event.milestone} "
                    "does not match specified milestone {milestone}"
                )
            # all checks OK
            return event

        if _check_compose(compose) == "date":
            if milestone:
                return wikitcms.event.NightlyEvent(
                    self, release=release, milestone=milestone, compose=compose, dist=dist
                )

            # we have a date and no milestone. Try both and return
            # whichever exists. We check whether the first result
            # page has any contents so that if someone mistakenly
            # creates the wrong event, we can clean up by blanking
            # the pages, rather than by getting an admin to
            # actually *delete* them.
            rawev = wikitcms.event.NightlyEvent(self, release, "Rawhide", compose, dist=dist)
            pgs = rawev.result_pages
            if pgs and pgs[0].text():
                return rawev
            brev = wikitcms.event.NightlyEvent(self, release, "Branched", compose, dist=dist)
            pgs = brev.result_pages
            if pgs and pgs[0].text():
                return brev
            # Here, we failed to guess. Boohoo.
            raise ValueError(
                "get_validation_event(): Could not find any event for "
                f"release {release} and date {compose}."
            )

        if _check_compose(compose) == "compose":
            compose = str(compose).upper()
            if not milestone:
                raise ValueError(
                    "get_validation_event(): For a TC/RC compose, a milestone "
                    "- Alpha, Beta, or Final - must be specified."
                )
            # With Pungi 4, the 'Final' milestone became 'RC', let's
            # be nice and convert it
            if int(release) > 23 and milestone.lower() == "final":
                milestone = "RC"
            return wikitcms.event.ComposeEvent(
                self, release, milestone, compose, dist=dist, cid=cid
            )

        # We should never get here, but just in case.
        raise ValueError("get_validation_event(): Something very strange happened.")

    def get_validation_page(
        self, testtype, release="", milestone="", compose="", cid="", dist="Fedora"
    ):
        # we could factor this out but I think it's fine
        # pylint: disable=too-many-arguments
        """Get an appropriate ValidationPage object for the values
        given. As with get_validation_event(), this method is for
        sloppy instantiation of pages that follow the rules. This
        method has no required arguments except the testtype and tries
        to figure out what you want from what you give it. It will
        raise errors if what you give it is impossible to interpret or
        if it tries and comes up with an inconsistent-seeming result.

        dist specifies a 'dist' (compose shortname) other than the
        default "Fedora" to find a page for. If you pass a compose ID
        as cid, any value you pass for dist will be ignored; we'll
        instead parse the dist value out of the compose ID.

        If you pass a numeric release, a milestone, and a valid
        compose (TC/RC or date), it will give you the appropriate
        event, whether it exists or not. All it really does in this
        case is pick NightlyEvent or ComposeEvent for you. If you
        don't fulfill any of those conditions, it'll need to do
        some guessing/assumptions, and in some of those cases it
        will only return an Event *that actually exists*, and may
        raise exceptions if you passed a particularly pathological
        set of values.

        If you don't pass a compose argument it will get the page for
        the current event; if you passed either of the other
        arguments and they don't match the current event, it will
        raise an error. It follows that calling this with no arguments
        just gives you the page of the specified test type for the
        current event.

        If you pass a date as compose with no milestone, it will see
        if there's a Rawhide nightly and return it if so, otherwise it
        will see if there's a Branched nightly and return that if so,
        otherwise raise an error. It follows that you can't get the
        page for an event that *doesn't exist yet* this way: you must
        instantiate it directly or call this method with a milestone.

        It will not attempt to guess a milestone for TC/RC composes;
        it will raise an exception in this case.

        The guessing bits require wiki roundtrips, so they will be
        slower than instantiating a class directly or using this
        method with sufficient information to avoid guessing.
        """
        if cid:
            (dist, release, milestone, compose) = wikitcms.helpers.cid_to_event(cid)
        if not compose or not release:
            # Can't really make an educated guess without a compose
            # and release, so just get the current event and return it
            # if it matches any other values passed.
            curr = self.get_current_compose(dist=dist)
            page = self.get_validation_page(
                testtype,
                release=curr["release"],
                milestone=curr["milestone"],
                compose=max(curr["compose"], curr["date"]),
                dist=dist,
            )
            if release and page.release != release:
                raise ValueError(
                    f"get_validation_page(): Guessed page release {page.release} does "
                    f"not match requested release {release}"
                )
            if milestone and page.milestone != milestone:
                raise ValueError(
                    f"get_validation_page(): Guessed page milestone {page.milestone} "
                    f"does not match specified milestone {milestone}"
                )
            return page

        if _check_compose(compose) == "date":
            if milestone:
                return wikitcms.page.NightlyPage(
                    self, release, testtype, milestone, compose, dist=dist
                )

            # date, but no milestone
            rawpg = wikitcms.page.NightlyPage(
                self, release, testtype, "Rawhide", compose, dist=dist
            )
            if rawpg.exists:
                return rawpg
            brpg = wikitcms.page.NightlyPage(
                self, release, testtype, "Branched", compose, dist=dist
            )
            if brpg.exists:
                return brpg
            # Here, we failed to guess. Boohoo.
            raise ValueError(
                "get_validation_page(): Could not find any event for "
                f"release {release} and date {compose}."
            )

        if _check_compose(compose) == "compose":
            if not milestone:
                raise ValueError(
                    "get_validation_page(): For a milestone compose, a "
                    " milestone - Alpha, Beta, or Final - must be specified."
                )
            # With Pungi 4, the 'Final' milestone became 'RC', let's
            # be nice and convert it
            if int(release) > 23 and milestone.lower() == "final":
                milestone = "RC"
            return wikitcms.page.ComposePage(self, release, testtype, milestone, compose, dist=dist)

        # We should never get here, but just in case.
        raise ValueError("get_validation_page(): Something very strange happened.")

    def report_validation_results(self, reslist, allowdupe=False):
        # pylint: disable=too-many-locals,too-many-branches
        """High-level result reporting function. Pass it an iterable
        of objects identifying results. It's pretty forgiving about
        what these can be. They can be any kind of sequence or
        iterable containing up to 15 values in the following order:
        (testtype, release, milestone, compose, testcase, section,
        testname, env, status, user, bugs, comment, bot, cid, dist).
        They can also be any mapping type (e.g. a dict) with enough of
        the 15 keys set (see below for requirements).

        You may find it convenient to import the ResTuple class from
        this module and pass your results as instances of it: it is
        a namedtuple with default values which uses the names given
        above, so you can avoid having to pad values you don't need to
        set and conveniently read back items from the tuple after
        you've created it, if you like.

        Any value of the result item can be absent, or set to
        something empty or falsey. However, to be successfully
        reported, each item must meet these conditions:

        * 'testtype', 'release', 'milestone', 'compose', 'dist' and
        'cid' must identify a single validation page
        using get_validation_page() (at least 'testtype' must always
        be set).
        * 'testcase', 'section' and 'testname' must identify a single
        test instance using ValidationPage.find_resultrow()
        * 'env' must uniquely identify one of the test instance's
        'environments' (the columns into which results can be entered;
        it can be empty if there is only one for this test instance)
        *'status' must indicate the result status.

        'user', 'bugs', and 'comment' can always be left empty if
        desired; if 'user' is not specified, the mediawiki username
        (lower-cased) will be used.

        All values should be strings, except 'bugs', which should be
        an iterable of digit strings (though iterable of ints will be
        tolerated), and 'bot' which should be True if the result is
        from some sort of automated testing system (not a human).

        Returns a 2-tuple of lists of objects indicating any failures.
        The first list is of submissions that failed because there was
        insufficient identifying data. The second list is of
        submissions that failed because they were 'dupes' - the given
        user has already reported a result for the given test and env.
        If allowdupe is True, duplicate reports will be allowed and
        this list will always be empty.

        The items in each list have the same basic layout as the input
        results items. The 'insufficients' list will contain the exact
        same objects that were provided as input. The 'duplicates'
        list is reconstructed and will often contain more or corrected
        data compared to the input tuples. Its members are *always*
        instances of the ResTuple namedtuple class, which provides
        access to the fields by the names given above.

        Uses get_validation_page() to guess the desired page and then
        constructs a result dict to pass to the ValidationPage
        add_results() method.
        """
        pagedict = dict()  # KEY: (testtype, release, milestone, compose, cid, dist)
        insufficients = list()
        dupes = list()

        for resitem in reslist:
            # Convert the item into a ResTuple.
            try:
                restup = ResTuple(**resitem)
            except TypeError:
                restup = ResTuple(*resitem)
            if not restup.status:
                # It doesn't make sense to allow {{result|none}}
                # from this high-level function.
                insufficients.append(resitem)
                continue
            user = restup.user
            if not user:
                # If no username was given, guess at the wiki account
                # name, lower-cased.
                user = self.username.lower()
            key = (
                restup.testtype,
                restup.release,
                restup.milestone,
                restup.compose,
                restup.cid,
                restup.dist,
            )
            # We construct a dict to sort the results by page. The
            # value for each page is a 2-tuple containing the actual
            # ValidationPage object and the 'results dictionary' we
            # will pass to page.add_results() once we have iterated
            # through the full result list (unless the page cannot be
            # found, in which case the value is None.)
            if key not in pagedict:
                # We haven't yet encountered this page, so we'll try
                # and find it and add it to the dict.
                pagedict[key] = dict()
                try:
                    pagedict[key] = (self.get_validation_page(*key), dict())
                except ValueError:
                    # This means we couldn't find a page from the info
                    # provided; set the pagedict entry for this key to
                    # (None, None) to cache that information, add this
                    # result to the 'insufficients' list, and move on
                    # to the next.
                    pagedict[key] = (None, None)
                    insufficients.append(resitem)
                    continue
            elif pagedict[key] == (None, None):
                # This is when we've already tried to find a page from
                # the same (testtype, release, milestone, compose) and
                # come up empty, so append the restup to the insuffs
                # list and move on.
                insufficients.append(resitem)
                continue

            # The code from here on gets hit whenever we can find the
            # correct page for a restup. We need to find the correct
            # ResultRow from the testcase, section, testname and
            # env, and produce a Result from status, username, bugs,
            # and comment. The keys in resdict are ResultRow
            # instances, so we check if there's already one that's
            # 'equal' to the ResultRow for this restup. If so, we
            # append the (env, Result) tuple to the list that is the
            # value for that key. If not, we add a new entry to the
            # resdict. It's vital that the resdict contain only *one*
            # entry for any given ResultRow, or else the edit will go
            # squiffy.
            (page, resdict) = pagedict[key]
            try:
                myrow = page.find_resultrow(
                    restup.testcase, restup.section, restup.testname, restup.env
                )
                myres = wikitcms.result.Result(
                    restup.status, user, restup.bugs, restup.comment, restup.bot
                )
            except (NoPageError, NotFoundError, TooManyError):
                # We couldn't find precisely one result row from the
                # provided information.
                insufficients.append(resitem)
                continue

            done = False
            for row in resdict.keys():
                if myrow.matches(row):
                    resdict[row].append((restup.env, myres))
                    done = True
                    break
            if not done:
                resdict[myrow] = [(restup.env, myres)]

        # Finally, we've sorted our restups into the right shape. Now
        # all we do is throw each page's resdict at its add_results()
        # method and grab the return value, which is a list of tuples
        # representing results that were 'dupes'. We then reconstruct
        # a ResTuple for each dupe, and return the lists of insuffs
        # and dupes.
        for (page, resdict) in pagedict.values():
            if page:
                _dupes = page.add_results(resdict, allowdupe)
                for (row, env, result) in _dupes:
                    dupes.append(
                        ResTuple(
                            page.testtype,
                            page.release,
                            page.milestone,
                            page.compose,
                            row.testcase,
                            row.section,
                            row.name,
                            env,
                            result.status,
                            result.user,
                            result.bugs,
                            result.comment,
                            result.bot,
                            "",
                            page.dist,
                        )
                    )

        return (insufficients, dupes)


# vim: set textwidth=100 ts=8 et sw=4:
