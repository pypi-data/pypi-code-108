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

"""Classes that describe different types of pages we are interested
in, and attributes of pages like test results and test cases, are
defined in this file.
"""

from collections import OrderedDict
import datetime
import logging
import re
import time

from cached_property import cached_property
import fedfind.helpers
import fedfind.release
from mwclient import errors as mwe
from mwclient import page as mwp
import pytz

from wikitcms.exceptions import NoPageError, NotFoundError, TooManyError
import wikitcms.helpers
import wikitcms.result

logger = logging.getLogger(__name__)


class Page(mwp.Page):
    """Parent class for all page classes. Can be instantiated directly
    if you just want to take advantage of the convenience methods like
    sections() and save(). Available attributes: seedtext, summary.
    Note 'name' is defined by mwp.Page's __init__.
    """

    def __init__(self, site, wikiname, info=None, extra_properties=None):
        super(Page, self).__init__(site, wikiname, info, extra_properties)
        # Used for sanity check by the page generator
        self.checkname = wikiname
        self._sections = None
        self.results_separators = list()

    @property
    def sections(self):
        """A list of the page's sections. Each section is represented
        by a dict whose values provide various attributes of the
        section. Returns an empty list for non-existent page (or any
        other API error). Cached, cache cleared on each page save.
        """
        # None == not yet retrieved or cache expired. [] == retrieved,
        # but page is empty or something.
        if self._sections is None:
            try:
                apiout = self.site.api("parse", page=self.name, prop="sections")
                self._sections = apiout["parse"]["sections"]
            except mwe.APIError:
                self._sections = []
        return self._sections

    @property
    def results_wikitext(self):
        """Returns a string containing the wikitext for the page's
        results section. Will be empty if no results are found. Relies
        on the layout for result pages remaining consistent. Class
        must override definition of self.results_separators or else
        this will always return an empty string.
        """
        pagetext = self.text()
        comment = re.compile("<!--.*?-->", re.S)
        pos = -1
        for sep in self.results_separators:
            pos = pagetext.find(sep)
            if pos > -1:
                break

        if pos == -1:
            return ""
        text = pagetext[pos:]
        text = comment.sub("", text)
        return text

    @cached_property
    def creation_date(self):
        """Date the page was created. Used for sorting and seeing how
        long it's been since the last event, when creating new events.
        """
        revs = self.revisions(limit=1, dir="newer", prop="timestamp")
        try:
            origrev = next(revs)
        except StopIteration:
            # page doesn't exist
            return ""
        return time.strftime("%Y%m%d", origrev["timestamp"])

    def write(self, createonly=True):
        """Create a page with its default content and summary. mwclient
        exception will be raised on any page write failure.
        """
        seedtext = getattr(self, "seedtext", None)
        summary = getattr(self, "summary", None)
        if seedtext is None or summary is None:
            raise ValueError("wikitcms.Page.write(): both seedtext and summary needed!")
        self.save(seedtext, summary, createonly=createonly)

    # we're using *args, **kwargs. cool your jets, pylint.
    # pylint: disable=signature-differs
    def save(self, *args, **kwargs):
        """Same as the original, but will retry once on fail. If you
        already retrieved the current text, you can pass it in as
        oldtext, and we will check to see if oldtext and text are the
        same. If they are, we return a dict with the key nochange set
        to an empty string - this saves a needless extra remote round
        trip. Of course you could do this in the caller instead, it's
        just a convenience. Also clears the page sections cache.
        """
        if "oldtext" in kwargs and args[0] == kwargs["oldtext"]:
            return dict(nochange="")

        if "oldtext" in kwargs:
            # avoid mwclient save() warning about unknown kwarg
            del kwargs["oldtext"]

        try:
            ret = super(Page, self).save(*args, **kwargs)
        except mwe.EditError as err:
            logger.warning("Page %s edit failed! Trying again in 15 seconds", self.name)
            logger.debug("Error was: %s", err)
            time.sleep(15)
            ret = super(Page, self).save(*args, **kwargs)
        # clear the caches
        self._sections = None
        return ret


class ValidationPage(Page):
    """A parent class for different types of release validation event
    pages, containing common properties and methods. Required
    attributes: version, shortver, seedtext. "dist" lets us create
    multiple event streams for different compose streams: it defaults
    to "Fedora", which gives us page names for the main stream of
    composes and Fedora releases, but can be set to e.g. "Fedora IoT"
    for a validation page for an IoT compose. The provided string is
    simply included in page names, category names and so on.
    """

    # I like this number, pylint
    # pylint: disable=too-many-instance-attributes, too-many-arguments
    def __init__(self, site, release, testtype, milestone="", compose="", info=None, dist="Fedora"):
        self.release = release
        self.milestone = str(milestone)
        try:
            self.compose = fedfind.helpers.date_check(compose, fail_raise=True, out="str")
        except ValueError:
            self.compose = str(compose)
        self.version = f"{self.release} {self.milestone} {self.compose}"
        self.testtype = testtype
        self.dist = dist
        # dist without "Fedora-", used in various wiki templates;
        # for the main "Fedora" composes, this will be ""
        self.shortdist = dist[7:]

        # Wiki name the page should have, according to the naming
        # convention.
        wikiname = f"Test Results:{dist} {self.version} {self.testtype}"
        super(ValidationPage, self).__init__(site, wikiname, info)

        # Edit summary to be used for clean page creation.
        self.summary = (
            f"Relval bot-created {testtype} validation results page for {dist} " f"{self.version}"
        )
        self.results_separators = (
            "Test Matri",
            "Test Areas",
            "An unsupported test or configuration.  No testing is required.",
        )
        # Sorting helpers. sortname is a string, sorttuple is a
        # 4-tuple. sorttuple is more reliable. See the function docs.
        self.sortname = wikitcms.helpers.fedora_release_sort(
            " ".join((self.version, self.testtype))
        )
        self.sorttuple = wikitcms.helpers.triplet_sort(
            self.release, self.milestone, self.compose
        ) + (self.testtype,)

    @property
    def results_sections(self):
        """A list of the sections in the page which (most likely)
        contain test results. Takes all the sections in the page,
        finds the one one which looks like the first "test results"
        section and returns that section and those that follow it - or
        returns all sections after the Key section, if it can't find
        one which looks like the first results section.
        """
        secs = self.sections
        if not secs:
            # empty page or some other malarkey
            return secs
        first = None
        for i, sec in enumerate(secs):
            if "Test Matri" in sec["line"] or "Test Areas" in sec["line"]:
                first = i
                break
            if "Key" in sec["line"]:
                first = i + 1
        return secs[first:]

    def get_resultrows(self, statuses=None, transferred=True):
        """Returns the result.ResultRow objects representing all the
        page's table rows containing test results.
        """
        sections = self.results_sections
        if not sections:
            return list()
        rows = list()
        pagetext = self.text()
        comment = re.compile("<!--.*?-->", re.S)
        for i, sec in enumerate(sections):
            try:
                nextsec = sections[i + 1]
            except IndexError:
                nextsec = None
            section = sec["line"]
            secid = sec["index"]
            if nextsec:
                sectext = pagetext[sec["byteoffset"] : nextsec["byteoffset"]]
            else:
                sectext = pagetext[sec["byteoffset"] :]
            # strip comments
            sectext = comment.sub("", sectext)
            newrows = wikitcms.result.find_resultrows(
                sectext, section, secid, statuses, transferred
            )
            rows.extend(newrows)
        return rows

    def find_resultrow(self, testcase="", section="", testname="", env=""):
        """Return exactly one result row with the desired attributes,
        or raise an exception (if more or less than one row is found).
        The Installation page contains some rows in the same section
        with the same testcase and testname, but each row provides
        a different set of envs, so these can be uniquely identified
        by specifying the desired env.
        """
        rows = self.get_resultrows()
        if not rows:
            raise NoPageError("Page does not exist or has no result rows.")

        # Find the right row
        nrml = wikitcms.helpers.normalize
        rows = [
            r for r in rows if nrml(testcase) in nrml(r.testcase) or nrml(testcase) in nrml(r.name)
        ]
        if len(rows) > 1 and section:
            rows = [r for r in rows if nrml(section) in nrml(r.section)]
        if len(rows) > 1 and testname:
            rows = [r for r in rows if nrml(testname) in nrml(r.name)]
        if len(rows) > 1 and env:
            # the way this match is done must be kept in line with the
            # corresponding match in add_results, below
            rows = [r for r in rows if nrml(env) in [nrml(renv) for renv in r.results.keys()]]
        # try a more precise name match - e.g. "upgrade_dnf" vs.
        # "upgrade_dnf_encrypted"
        if len(rows) > 1:
            newrows = [
                r
                for r in rows
                if nrml(testcase) == nrml(r.testcase)
                or nrml(testcase) == nrml(r.name)
                or nrml(testname) == nrml(r.name)
            ]
            if len(newrows) == 1:
                rows = newrows
        # also try a more precise section name match - e.g.
        # "Release-blocking desktops" vs.
        # "Non release-blocking desktops":
        # https://pagure.io/fedora-qa/python-wikitcms/issue/4
        if len(rows) > 1:
            newrows = [r for r in rows if nrml(section) == nrml(r.section)]
            if len(newrows) == 1:
                rows = newrows
        # let's also see if non-normalized section matching helps
        if len(rows) > 1:
            newrows = [r for r in rows if section in r.section]
            if len(newrows) == 1:
                rows = newrows
        if not rows:
            raise NotFoundError("Specified row cannot be found.")
        if len(rows) > 1:
            raise TooManyError("More than one matching row found.")
        return rows[0]

    def update_current(self):
        """Make the Current convenience redirect page on the wiki for
        the given test type point to this page.
        """
        short = self.shortdist
        if short:
            short = f" {short}"
        curr = self.site.pages[f"Test Results:Current{short} {self.testtype} Test"]
        curr.save(f"#REDIRECT [[{self.name}]]", "relval: update to current event", createonly=None)

    def add_results(self, resultsdict, allowdupe=False):
        """Adds multiple results to the page. Passed a dict whose
        keys are ResultRow() instances and whose values are iterables
        of (env, Result()) 2-tuples. Returns a list, which will be
        empty unless allowdupe is False and any of the results is a
        'dupe' - i.e. the given test and environment already have a
        result from the user. The return list contains a 3-tuple of
        (row, env, result) for each dupe.
        """
        # look, pylint, this is complicated stuff. calm yoself.
        # pylint: disable=too-many-locals, too-many-branches, too-many-statements

        # We need to sort the dict in a particular way: by the section
        # ID of each row, in reverse order. This is so when we edit
        # the page, we effectively do so backwards, and the byte
        # offsets we use to find each section don't get thrown off
        # along the way (we don't edit section 1 before section 3 and
        # thus not quite slice the text correctly when we look for
        # section 3).
        resultsdict = OrderedDict(
            sorted(resultsdict.items(), key=lambda x: int(x[0].secid), reverse=True)
        )
        nonetext = wikitcms.result.Result().result_template
        dupes = list()
        # this tracks rows that we don't wind up touching, so they
        # can be left out of the summary text
        notrows = list()
        newtext = oldtext = self.text()
        for (row, results) in resultsdict.items():
            # It's possible that we have rows with identical text in
            # different page sections; this is why 'secid' is an attr
            # of ResultRows. To make sure we edit the correct row,
            # we'll slice the text at the byteoffset of the row's
            # section. We only do one replacement, so we don't need
            # to bother finding the *end* of the section.
            # We could just edit the page section-by-section, but that
            # involves doing one remote roundtrip per section.
            secoff = [sec["byteoffset"] for sec in self.sections if sec["index"] == row.secid][0]
            if secoff:
                sectext = newtext[secoff:]
            else:
                sectext = newtext
            oldrow = row.origtext
            cells = oldrow.split("\n|")

            for (env, result) in results:
                if not env in row.results:
                    # the env passed wasn't precisely one of the row's
                    # envs. let's see if we can make a safe guess. If
                    # there's only one env, it's easy...
                    if len(row.results) == 1:
                        env = list(row.results.keys())[0]
                    else:
                        # ...if not, we'll see if the passed env is
                        # a substring of only one of the envs, case-
                        # insensitively.
                        cands = [cand for cand in row.results.keys() if env.lower() in cand.lower()]
                        if len(cands) == 1:
                            env = cands[0]
                        else:
                            # LOG: bad env
                            continue
                if not allowdupe:
                    dupe = [r for r in row.results[env] if r.user == result.user]
                    if dupe:
                        dupes.append((row, env, result))
                        continue
                restext = result.result_template
                rescell = cells[row.columns.index(env)]
                if nonetext in rescell:
                    rescell = rescell.replace(nonetext, restext)
                elif "\n" in rescell:
                    rescell = rescell.replace("\n", restext + "\n")
                else:
                    rescell = rescell + restext
                cells[row.columns.index(env)] = rescell

            newrow = "\n|".join(cells)
            if newrow == oldrow:
                # All dupes, or something.
                notrows.append(row)
                continue
            sectext = sectext.replace(oldrow, newrow, 1)
            if secoff:
                newtext = newtext[:secoff] + sectext
            else:
                newtext = sectext

        touchedrows = [row for row in resultsdict.keys() if row not in notrows]
        if len(touchedrows) > 3:
            testtext = ", ".join(row.name for row in touchedrows[:3])
            testtext = f"{testtext}..."
        else:
            testtext = ", ".join(row.name for row in touchedrows)
        summary = f"Result(s) for test(s): {testtext} filed via relval"
        self.save(newtext, summary, oldtext=oldtext, createonly=None)
        return dupes

    def add_result(self, result, row, env, allowdupe=False):
        """Adds a result to the page. Must be passed a Result(), the
        result.ResultRow() object representing the row into which a
        result will be added, and the name of the environment for
        which the result is to be reported. Works by replacing the
        first instance of the row's text encountered in the page or
        page section. Expected to be used together with get_resultrows
        which provides the ResultRow() objects.
        """
        resdict = dict()
        resdict[row] = ((env, result),)
        return self.add_results(resdict, allowdupe=allowdupe)


class ComposePage(ValidationPage):
    """A Page class that describes a single result page from a test
    compose or release candidate validation test event.
    """

    # I like this number, pylint
    # pylint: disable=too-many-arguments
    def __init__(self, site, release, testtype, milestone, compose, info=None, dist="Fedora"):
        super(ComposePage, self).__init__(
            site,
            release=release,
            milestone=milestone,
            compose=compose,
            testtype=testtype,
            info=info,
            dist=dist,
        )
        self.shortver = f"{self.milestone} {self.compose}"

        # String that will generate a clean copy of the page using the
        # test page generation template system.
        if self.shortdist:
            tmpl = f"{self.shortdist} validation results"
        else:
            tmpl = "Validation results"
        self.seedtext = (
            f"{{{{subst:{tmpl}|testtype={testtype}|release={self.release}|"
            f"milestone={self.milestone}|compose={self.compose}}}}}"
        )


class NightlyPage(ValidationPage):
    """A Page class that describes a single result page from a nightly
    validation test event.
    """

    # I like this number, pylint
    # pylint: disable=too-many-arguments
    def __init__(self, site, release, testtype, milestone, compose, info=None, dist="Fedora"):
        super(NightlyPage, self).__init__(
            site,
            release=release,
            milestone=milestone,
            compose=compose,
            testtype=testtype,
            info=info,
            dist=dist,
        )
        self.shortver = self.compose
        # overridden for nightlies to avoid expensive roundtrips
        if "." in compose:
            self.creation_date = compose.split(".")[0]
        else:
            self.creation_date = compose

        # String that will generate a clean copy of the page using the
        # test page generation template system.
        if self.shortdist:
            tmpl = f"{self.shortdist} validation results"
        else:
            tmpl = "Validation results"
        self.seedtext = (
            f"{{{{subst:{tmpl}|testtype={testtype}|release={self.release}|"
            f"milestone={self.milestone}|date={self.compose}}}}}"
        )


class SummaryPage(Page):
    """A Page class that describes the result summary page for a given
    event. event is the parent Event() for the page; summary pages are
    always considered to be a part of an Event.
    """

    def __init__(self, site, event, info=None, dist="Fedora"):
        self.dist = dist
        wikiname = f"Test Results:{dist} {event.version} Summary"
        self.shortdist = self.dist[7:]
        super(SummaryPage, self).__init__(site, wikiname, info)
        self.summary = f"Relval bot-created validation results summary for {dist} {event.version}"
        self.seedtext = (
            f"{dist} {event.version} [[QA:Release validation test plan|release "
            "validation]] summary. This page shows the results from all the "
            "individual result pages for this compose together. You can file "
            "results directly from this page and they will be saved into the "
            "correct individual result page. To see test instructions, visit "
            "any of the individual pages (the section titles are links). You "
            "can find download links below.\n\n"
        )
        self.seedtext += "__TOC__\n\n"
        self.seedtext += "== Downloads ==\n{{" + dist + " " + event.version + " Download}}"
        for testpage in event.valid_pages:
            self.seedtext += "\n\n== [[" + testpage.name + "|"
            self.seedtext += testpage.testtype + "]] ==\n{{"
            self.seedtext += testpage.name + "}}"
        self.seedtext += f"\n\n[[{event.category_page.name}|Summary]]"

    def update_current(self):
        """Make the Current convenience redirect page on the wiki for the
        event point to this page.
        """
        if self.shortdist:
            curr = self.site.pages[f"Test Results:Current {self.shortdist} Summary"]
        else:
            curr = self.site.pages["Test Results:Current Summary"]
        curr.save(f"#REDIRECT [[{self.name}]]", "relval: update to current event", createonly=None)


class DownloadPage(Page):
    """The page containing image download links for a ValidationEvent.
    As with SummaryPage, is always associated with a specific event.
    """

    def __init__(self, site, event, info=None, dist="Fedora"):
        wikiname = f"Template:{dist} {event.version} Download"
        self.summary = f"Relval bot-created download page for {dist} {event.version}"
        super(DownloadPage, self).__init__(site, wikiname, info)
        self.event = event

    @property
    def seedtext(self):
        """A nicely formatted download table for the images for this
        compose. Here be dragons (and wiki table syntax). What you get
        from this is a table with one row for each unique 'image
        identifier' - the subvariant plus the image type - and columns
        for all arches in the entire image set; if there's an image
        for the given image type and arch then there'll be a download
        link in the appropriate column.
        """
        # pylint: disable=too-many-branches

        # sorting score values (see below)
        archscores = ((("x86_64", "i386"), 2000),)
        loadscores = (
            (("everything",), 300),
            (("workstation",), 220),
            (("server",), 210),
            (("cloud", "desktop", "cloud_base", "docker_base", "atomic"), 200),
            (("kde",), 190),
            (("minimal",), 90),
            (("xfce",), 80),
            (("soas",), 73),
            (("mate",), 72),
            (("cinnamon",), 71),
            (("lxde",), 70),
            (("source",), -10),
        )
        # Start by iterating over all images and grouping them by load
        # (that's imagedict) and keeping a record of each arch we
        # encounter (that's arches).
        arches = set()
        imagedict = OrderedDict()
        for img in self.event.ff_release_images.all_images:
            # we don't want entries for source DVDs
            if img.get("arch") == "src":
                continue
            if img["arch"]:
                arches.add(img["arch"])
            # simple human-readable identifier for the image
            desc = " ".join((img["subvariant"], img["type"]))
            # assign a 'score' to the image; this will be used for
            # ordering the download table's rows.
            img["score"] = 0
            for (values, score) in archscores:
                if img["arch"] in values:
                    img["score"] = score
            for (values, score) in loadscores:
                if img["subvariant"].lower() in values:
                    img["score"] += score
            # The dict values are lists of images. We could use a
            # DefaultDict here, but faking it is easy too.
            if desc in imagedict:
                imagedict[desc].append(img)
            else:
                imagedict[desc] = [img]
        # Now we have our data, sort the dict using the weight we
        # calculated earlier. We use the max score of all arches in
        # each group of images.
        imagedict = OrderedDict(
            sorted(imagedict.items(), key=lambda x: max(img["score"] for img in x[1]), reverse=True)
        )
        # ...and sort the arches (just so they don't move around in
        # each new page and confuse people).
        arches = sorted(arches)

        # Now generate the table.
        table = '{| class="wikitable sortable mw-collapsible" width=100%\n|-\n'
        # Start of the header row...
        table += "! Image"
        for arch in arches:
            # Add a column for each arch
            table += f" !! {arch}"
        table += "\n"
        for (subvariant, imgs) in imagedict.items():
            # Add a row for each subvariant
            table += "|-\n"
            table += f"| {subvariant}\n"
            for arch in arches:
                # Add a cell for each arch (whether we have an image
                # or not)
                table += "| "
                for img in imgs:
                    if img["arch"] == arch:
                        # Add a link to the image if we have one
                        table += f"[{img['url']} Download]"
                table += "\n"
        # Close out the table when we're done
        table += "|-\n|}"
        return table

    def update_current(self):
        """Kind of a hack - relval needs this to exist as things
        stand. I'll probably refactor it later.
        """


class AMIPage(Page):
    """A page containing EC2 AMI links for a given event. Is included
    in the Cloud validation page to make it easy for people to find
    the correct AMIs.
    """

    def __init__(self, site, event, info=None, dist="Fedora"):
        wikiname = f"Template:{dist} {event.version} AMI"
        self.summary = f"Relval bot-created AMI page for {dist} {event.version}"
        super(AMIPage, self).__init__(site, wikiname, info)
        self.event = event

    @property
    def seedtext(self):
        """A table of all the AMIs for the compose for this event. We
        have to query this information out of datagrepper, that's the
        only place where it's available.
        """
        # pylint: disable=too-many-locals
        text = ""
        # first, let's get the information out of datagrepper. We'll
        # ask for messages up to 2 days after the event date.
        date = fedfind.helpers.parse_cid(self.event.ff_release.cid, dic=True)["date"]
        start = datetime.datetime.strptime(date, "%Y%m%d").replace(tzinfo=pytz.utc)
        end = start + datetime.timedelta(days=2)
        url = "https://apps.fedoraproject.org/datagrepper/raw"
        url += "?topic=org.fedoraproject.prod.fedimg.image.publish"
        # convert to epoch (this is what datagrepper wants)
        url += f"&start={start.timestamp()}&end={end.timestamp()}"
        json = fedfind.helpers.download_json(url)
        msgs = json["raw_messages"]
        # handle pagination
        for page in range(2, json["pages"] + 1):
            newurl = f"{url}&page={page}"
            newjson = fedfind.helpers.download_json(newurl)
            msgs.extend(newjson["raw_messages"])

        # now let's find the messages for our event compose
        ours = [msg["msg"] for msg in msgs if msg["msg"]["compose"] == self.event.ff_release.cid]

        def _table_line(msg):
            """Convenience function for generating a table line."""
            destination = msg["destination"]
            ami = msg["extra"]["id"]
            url = "https://redirect.fedoraproject.org/console.aws.amazon.com/ec2/v2/home?"
            url += f"region={destination}#LaunchInstanceWizard:ami={ami}"
            return f"| {destination}\n| {ami}\n| [{url} Launch in EC2]\n|-\n"

        def _table(arch, virttype, voltype):
            """Convenience function for adding a table."""
            ret = f"== {arch} {virttype} {voltype} AMIs ==\n\n"
            ret += '{| class="wikitable sortable mw-collapsible'
            if arch != "x86_64" or virttype != "hvm" or voltype != "standard":
                # we expand the x86_64 hvm standard table by default
                ret += " mw-collapsed"
            ret += '" width=100%\n|-\n'
            ret += "! Region !! AMI ID !! Direct launch link\n|-\n"
            # find the right messages for this arch and types
            relevants = [
                msg
                for msg in ours
                if msg["architecture"] == arch
                and msg["extra"]["virt_type"] == virttype
                and msg["extra"]["vol_type"] == voltype
            ]
            # sort the messages by region so the table is easier to scan
            relevants.sort(key=lambda x: x["destination"])
            for msg in relevants:
                ret += _table_line(msg)
            ret += "|}\n\n"
            return ret

        # now let's create and populate the tables
        for arch in ("x86_64", "arm64"):
            for virttype in ("hvm",):
                for voltype in ("standard", "gp2"):
                    text += _table(arch, virttype, voltype)

        return text


class TestDayPage(Page):
    """A Test Day results page. Usually contains table(s) with test
    cases as the column headers and users as the rows - each row is
    one user's results for all of the test cases in the table. Note
    this class is somewhat incomplete and really can only be used
    for its own methods, do *not* try writing one of these to the
    wiki.
    """

    def __init__(self, site, date, subject, info=None):
        # Handle names with no subject, e.g. Test_Day:2012-03-14
        wikiname = f"Test Day:{date}"
        if subject:
            wikiname = f"{wikiname} {subject}"
        super(TestDayPage, self).__init__(site, wikiname, info)
        self.date = date
        self.subject = subject
        self.results_separators = ("Test Results", "Results")

    def write(self, createonly=True):
        print("Creating Test Day pages is not yet supported.")

    @cached_property
    def bugs(self):
        """Returns a list of bug IDs referenced in the results section
        (as strings). Will find bugs in {{result}} and {{bz}}
        templates."""
        bugs = wikitcms.helpers.find_bugs(self.results_wikitext)
        for res in wikitcms.result.find_results_by_row(self.results_wikitext):
            bugs.update(res.bugs)
        return sorted(bugs)

    def fix_app_results(self):
        """The test day app does its own bug references outside the
        result template, instead of including them as the final
        parameters to the template like it should. This fixes that, in
        a fairly rough and ready way.
        """
        badres = re.compile(
            r"({{result.*?)}} {0,2}"
            r"(<ref>{{bz\|\d{6,7}}}</ref>) ?"
            r"(<ref>{{bz\|\d{6,7}}}</ref>)? ?"
            r"(<ref>{{bz\|\d{6,7}}}</ref>)? ?"
            r"(<ref>{{bz\|\d{6,7}}}</ref>)? ?"
            r"(<ref>{{bz\|\d{6,7}}}</ref>)? ?"
            r"(<ref>{{bz\|\d{6,7}}}</ref>)?"
        )
        text = oldtext = self.text()
        oldtext = text
        matches = badres.finditer(text)
        for match in matches:
            bugs = list()
            groups = match.groups()
            for group in groups[1:]:
                if group:
                    bugs.append(group[10:-8])
            text = text.replace(match.group(0), match.group(1) + "||" + "|".join(bugs) + "}}")
        return self.save(
            text,
            summary="Fix testday app-generated results to "
            "use {{result}} template for bug references",
            oldtext=oldtext,
        )

    def long_refs(self):
        """People tend to include giant essays as <ref> notes on test
        day results, which really makes table rendering ugly when
        they're dumped in the last column of the table. This finds all
        <ref> notes over 150 characters long, moves them to the "long"
        group, and adds a section at the end of the page with all the
        "long" notes in it. The 'end of page discovery' is a bit
        hacky, it just finds the last empty line in the page except
        for trailing lines and sticks the section there, but that's
        usually what we want - basically we want to make sure it
        appears just above the category memberships at the bottom of
        the page. It does go wrong *sometimes*, so good idea to check
        the page after it's edited.
        """
        text = oldtext = self.text()
        if '<ref group="long">' in text:
            # Don't run if we've already been run on this page
            return dict(nochange="")
        refpatt = re.compile("<ref>(.+?</ref>)", re.S)
        matches = refpatt.finditer(text)
        found = False
        for match in matches:
            if len(match.group(0)) > 150:
                found = True
                text = text.replace(match.group(0), '<ref group="long">' + match.group(1))
        if found:
            text = wikitcms.helpers.rreplace(
                text.strip(), "\n\n", '\n\n== Long comments ==\n<references group="long" />\n\n', 1
            )
            return self.save(
                text,
                summary="Move long comments to a separate " "section at end of page",
                oldtext=oldtext,
            )

        # If we didn't find any long refs, don't do anything
        return dict(nochange="")


# vim: set textwidth=100 ts=8 et sw=4:
