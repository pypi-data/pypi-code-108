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

"""This file defines various classes and helper functions for working
with results."""

from collections import OrderedDict
import re

import wikitcms.helpers

# These are used by multiple functions, so let's share them.
# Wiki table row separator
SEP_PATT = re.compile(r"\|[-\}].*?\n")
# Identifies an instance of the result template. Will break if the
# result contains another template, but don't do that. the lookahead
# is used to capture the 'comments' for the result: we keep matching
# until we hit the next instance of the template, or a cell or row
# separator (newline starting with a |). The re.S is vital.
RES_PATT = re.compile(r"{{result.+?}}.*?(?=\n*{{result|$|\n\|)", re.S)


def _filter_results(results, statuses=None, transferred=True, bot=True):
    """Filter results. Shared between next two functions."""
    # Drop example / sample results
    results = [
        r
        for r in results
        if not r.user
        or r.user.lower() not in ("sampleuser", "exampleuser", "example", "username", "fasname")
    ]
    if statuses:
        results = [r for r in results for s in statuses if r.status and s in r.status]
    if not transferred:
        results = [r for r in results if not r.transferred]
    if not bot:
        results = [r for r in results if not r.bot]
    return results


def find_results(text, statuses=None, transferred=True, bot=True):
    """Find test results in a given chunk of wiki text. Returns a list
    of Result objects. If statuses is not None, it should be an
    iterable of strings, and only result objects whose status matches
    one of the given statuses will be returned. If transferred is
    False, results like {{result|something|previous TC5 run}} will not
    be included. If bot is False, results from automated test bots
    (results with 'bot=true') will not be included.
    """
    results = list()
    # Identifies an instance of the old {{testresult template, in the
    # same way as RES_PATT (above).
    oldres_patt = re.compile(r"{{testresult.+?}}.*?(?={{testresult|$)", re.M)
    for res in RES_PATT.findall(text):
        results.append(Result.from_result_template(res))
    for oldres in oldres_patt.findall(text):
        results.append(Result.from_testresult_template(oldres))

    results = _filter_results(results, statuses, transferred, bot)
    return results


def find_results_by_row(text, statuses=None):
    """Find test results using a row-by-row scan, guessing the user
    for results which do not have one. Used for Test Day pages. Note:
    doesn't bother handling {{testresult because AFAICT no Test Day
    pages use that template.
    """
    # Slightly slapdash way to identify the contents of a wiki table
    # cell. Good enough to find the contents of the first cell in the
    # row, which we do because it'll usually be the user name in a
    # Test Day results table.
    cell_patt = re.compile(r"\| *(.*?) *\n\|")
    # Captures the user name from a wikilink to a user page (typically
    # used to indicate the user who reports a result).
    user_patt = re.compile(r"\[\[User: *(.*?) *[|\]]")
    results = list()

    for row in SEP_PATT.split(text):
        for match in RES_PATT.findall(row):
            res = Result.from_result_template(match)
            if res.status and not res.user:
                # We'll try and find a [[User: wikilink; if we can't,
                # we'll guess that the reporter's name is the contents
                # of the first cell in the row.
                pattuser = user_patt.search(row)
                if pattuser:
                    res.user = pattuser.group(1).lower()
                else:
                    celluser = cell_patt.search(row)
                    if celluser:
                        res.user = celluser.group(1).lower()
            results.append(res)

    results = _filter_results(results, statuses)
    return results


def find_resultrows(text, section="", secid=0, statuses=None, transferred=True):
    """Find result rows in a given chunk of wiki text. Returns a list
    of ResultRow objects. 'statuses' and 'transferred' are passed all
    the way through ResultRow to find_results() and behave as
    described there, for the Result objects in each ResultRow.
    """
    # oh shut up pylint what do you have against variables
    # pylint: disable=too-many-locals

    # identify all test case names, including old ones. modern ones
    # match QA:Testcase.*, but older ones sometimes have QA/TestCase.
    # some IoT tests are in pwhalen's namespace with names following
    # another pattern, see https://pagure.io/fedora-qa/issue/631
    testcase_pattern = re.compile(r"(QA[:/]Test.+?|User:Pwhalen/QA/IoT.+?)[\|\]\n]")
    # row separator is |-, end of table is |}
    columns = list()
    resultrows = list()
    rows = SEP_PATT.split(text)
    for row in rows:
        rowlines = row.split("\n")
        for line in rowlines:
            # check if this is a column header row, and update column
            # names. Sometimes the header row doesn't have an explicit
            # row separator so the 'row' might be polluted with
            # preceding lines, so we split the row into lines and
            # check each line in the row.
            line = line.strip()
            if line.find("!") == 0 and line.find("!!") > 0:
                # column titles. note: mw syntax in fact allows for
                # '! title\n! title\n! title' as well as '! title !!
                # title !! title'. But we don't use that syntax.
                columns = line.lstrip("!").split("!!")
                for column in columns:
                    # sanitize names a bit
                    newcol = column.strip()
                    newcol = newcol.strip("'[]")
                    newcol = newcol.strip()
                    try:
                        # drop out any <ref> block
                        posa = newcol.index("<ref>")
                        posb = newcol.index("</ref>") + 6  # length
                        newcol = newcol[:posa] + newcol[posb:]
                        newcol = newcol.strip()
                    except ValueError:
                        pass
                    try:
                        newcol = newcol.split("|")[1]
                    except IndexError:
                        pass
                    if newcol != column:
                        columns.insert(columns.index(column), newcol)
                        columns.remove(column)
        tcmatch = testcase_pattern.search(row)
        if tcmatch:
            # *may* be a result row - may also be a garbage 'row'
            # between tables which happens to contain a test case
            # name. So we get a ResultRow object but discard it if it
            # doesn't contain any result cells. This test works even
            # if the actual results are filtered by statuses= or
            # Transferred=, because the resrow.results dict will
            # always have a key for each result column, though its
            # value may be an empty list.
            resrow = ResultRow.from_wiki_row(
                tcmatch.group(1), columns, row, section, secid, statuses, transferred
            )
            if resrow.results:
                resultrows.append(resrow)
    return resultrows


class Result:
    """A class that represents a single test result. Note that a
    'none' result, as you get if you just instantiate this class
    without arguments, is a thing, at least for wikitcms; when text
    with {{result|none}} templates in it is parsed, such objects may
    be created/returned, and you can produce the {{result|none}} text
    as the result_template property of such an instance.

    You would usually instantiate this class directly to report a new
    result.

    Methods that parse existing results will use one of the class
    methods that returns a Result() with the appropriate attributes.
    When one of those parsers produces an instance it will pass
    origtext to record the exact string parsed to produce the instance;
    otherwise origtext should be left blank.

    transferred, if True, indicates the result is of the "previous
    (compose) run" type that is used to indicate where we think a
    result from a previous compose is valid for a later one.
    """

    # pylint: disable=too-many-instance-attributes
    def __init__(self, status=None, user=None, bugs=None, comment="", bot=False, origtext=""):
        # pylint: disable=too-many-arguments
        self.status = status
        self.user = user
        self.bugs = bugs
        if self.bugs:
            self.bugs = [str(bug) for bug in self.bugs]
        self.comment = comment
        self.bot = bot
        self.transferred = False
        self.comment_bugs = wikitcms.helpers.find_bugs(self.comment)
        self.origtext = origtext

    def __str__(self):
        if not self.status:
            return "Result placeholder - {{result|none}}"
        if self.bot:
            bot = "BOT "
        else:
            bot = ""
        status = "Result: " + self.status.capitalize()
        if self.transferred:
            user = " transferred: " + self.user
        elif self.user:
            user = " from " + self.user
        else:
            user = ""
        if self.bugs:
            bugs = ", bugs: " + ", ".join(self.bugs)
        else:
            bugs = ""
        if self.comment:
            comment = ", comment: " + self.comment
            # Don't display ref tags
            refpatt = re.compile(r"</?ref.*?>")
            comment = refpatt.sub("", comment)
        else:
            comment = ""
        return bot + status + user + bugs + comment

    @property
    def result_template(self):
        """The {{result}} template string that would represent the
        properties of this result in a wiki page.
        """
        bugtext = ""
        commtext = self.comment
        usertext = ""
        bottext = ""
        if self.status is None:
            status = "none"
        else:
            status = self.status
        if self.bugs:
            bugtext = "|" + "|".join(self.bugs)
        if self.user:
            usertext = "|" + self.user
        if self.bot:
            bottext = "|bot=true"
        return f"{{{{result|{status}{usertext}{bugtext}{bottext}}}}}{commtext}"

    @classmethod
    def from_result_template(cls, string):
        """Returns a Result object based on the {{result}} template.
        The most complex result template you see might be:
        {{ result | fail| bot =true| adamwill | 123456|654321|615243}} comment
        We want the 'fail' and 'adamwill' bits separately and stripped,
        and all the bug numbers in one chunk to be parsed later to
        construct a list of bugs, and none of the pipes, brackets, or
        whitespace. Mediawiki named parameters can occur anywhere in
        the template and aren't counted in the numbered parameters, so
        we need to find them and extract them first. We record the
        comment exactly as is.
        """
        # pylint: disable=too-many-locals
        template, comment = string.strip().split("}}", 1)
        comment = comment.strip()
        template = template.lstrip("{")
        params = template.split("|")
        namedpars = dict()
        bot = False

        for param in params:
            if "=" in param:
                (par, val) = param.split("=", 1)
                namedpars[par.strip()] = val.strip()
                params.remove(param)
        if "bot" in namedpars and namedpars["bot"]:
            # This maybe doesn't do what you expect for 'bot=false',
            # but we don't handle that in Mediawiki either and we want
            # to stay consistent.
            bot = True

        # 'params' now contains only numbered params
        # Pad the non-existent parameters to make things cleaner later
        while len(params) < 3:
            params.append("")

        for i, param in enumerate(params):
            params[i] = param.strip()
            if params[i] == "":
                params[i] = None
        status, user = params[1:3]
        bugs = params[3:]
        if status and status.lower() == "none":
            status = None

        if bugs:
            bugs = [b.strip() for b in bugs if b and b.strip()]
            for i, bug in enumerate(bugs):
                # sometimes people write 123456#c7, remove the suffix
                if "#" in bug:
                    newbug = bug.split("#")[0]
                    if newbug.isdigit():
                        bugs[i] = newbug

        res = cls(status, user, bugs, comment, bot, origtext=string)
        if user and "previous " in user:
            res.transferred = True
        return res

    @classmethod
    def from_testresult_template(cls, string):
        """Returns a Result object based on the {{testresult}} template.
        This was used in Fedora 12. It looks like this:
        {{testresult/pass|FASName}} <ref>comment or bug</ref>
        The bug handling here is very special-case - it relies on the
        fact that bug IDs were always six-digit strings, at the time,
        and on the template folks used to link to bug reports - but
        should be good enough.
        """
        bug_patt = re.compile(r"({{bz.*?(\d{6,6}).*?}})")
        emptyref_patt = re.compile(r"<ref> *?</ref>")
        template, comment = string.strip().split("}}", 1)
        template = template.lstrip("{")
        template = template.split("/")[1]
        params = template.split("|")
        try:
            status = params[0].strip().lower()
            if status == "none":
                status = None
        except IndexError:
            status = None
        try:
            user = params[1].strip().lower()
        except IndexError:
            user = None
        bugs = [b[1] for b in bug_patt.findall(comment)]
        if comment:
            comment = bug_patt.sub("", comment)
            comment = emptyref_patt.sub("", comment)
            if comment.replace(" ", "") == "":
                comment = ""
            comment = comment.strip()
        else:
            pass
        res = cls(status, user, bugs, comment, origtext=string)
        if user and "previous " in user:
            res.transferred = True
        return res


class ResultRow:
    """Represents the 'test instance' concept for Wikitcms, where it
    is a result row from the tables used to contain results. We think
    of a "test instance" as the 'basic unit' of a single test for
    which some results are expected to be reported.

    The 'testcase' is the basic identifier of a ResultRow. It will
    not necessarily be unique, though - it is not uncommon for a set
    of ResultRows to have the same 'testcase' but a different 'name',
    which is the link text: there will a column which for each row
    contains [[testcase|name]], the testcase being the same but the
    name being different. Commonly the 'testcase' and 'name' will be
    the same, when each instance within a set has a different
    'testcase' the name should be identical to the testcase.

    milestone is, roughly, the priority of the test: it will usually
    be Basic, Beta or Final.

    results is required to be a dict of lists; the dict keys represent
    the test's environments. The values must be lists of instances of
    wikitcms.Result or a subclass of it.

    columns is the list of columns in the table in which the result
    was found (this is needed to figure out the environments for the
    results, as the envs are represented by table columns, and to know
    which cell to edit when modifying results).

    origtext is the text which was parsed to produce the instance, if
    it was produced by the from_wiki_row() class method which parses
    wiki text to produce instances.

    section and secid are the wiki page section in which the table
    from which the row came is located; though these are in a way
    attributes of the page, this is really another case where an MW
    attribute is just a way of encoding information about a *test*.
    The splitting of result pages into sections is a way of sub-
    grouping tests in each page. So it's appropriate to store those
    attributes here.

    At present you typically get ResultRow instances by calling a
    ComposePage's get_resultrows() method, which runs its text through
    result.find_resultrows(), which isolates the result rows in the
    wiki text and runs through through this class' from_wiki_row()
    method. This will always provide instances with a full set of
    the above-described attributes.
    """

    # pylint: disable=too-many-instance-attributes
    def __init__(
        self, testcase, columns, section="", secid=None, milestone="", origtext="", results=None
    ):
        # pylint: disable=too-many-arguments
        self.testcase = testcase
        self.name = testcase
        self.milestone = milestone
        if not results:
            self.results = dict()
        else:
            self.results = results
        self.columns = columns
        self.origtext = origtext
        self.section = section
        self.secid = secid

    def matches(self, other):
        """This is roughly an 'equals' check for ResultRows; if all
        identifying characteristics and the origtext match, this is
        True, otherwise False. __dict__ match is too strong as the
        'results' attribute is a list of Result instances; each time
        you instantiate the same ResultRow you get different Result
        objects. We don't override __eq__ and use == because that has
        icky implications for hashing, and we just want to stay away
        from that mess:
        https://docs.python.org/3/reference/datamodel.html#object.__hash__
        """
        if isinstance(other, self.__class__):
            ours = (self.testcase, self.name, self.secid, self.origtext)
            theirs = (other.testcase, other.name, other.secid, other.origtext)
            return ours == theirs
        return False

    @classmethod
    def from_wiki_row(
        cls, testcase, columns, text, section, secid, statuses=None, transferred=True
    ):
        """Instantiate a ResultRow from some wikitext and some info
        that is worked out from elsewhere in the page.
        """
        # pylint: disable=too-many-locals, too-many-arguments
        results = OrderedDict()
        # this is presumptuous, but holds up for every result page
        # tested so far; there may be some with whitespace, and
        # '| cell || cell || cell' is permitted as an alternative to
        # '| cell\n| cell\n| cell' but we do not seem to use it.
        cells = text.split("\n|")
        milestone = ""
        for mile in ("Alpha", "Basic", "Beta", "Final", "Optional", "Tier1", "Tier2", "Tier3"):
            if mile in cells[0]:
                milestone = mile
                # we take the *first* milestone we find, so we treat
                # e.g. "Basic / Final" as Basic
                break
        for i, cell in enumerate(cells):
            if testcase in cell:
                try:
                    # see if we can find some link text for the test
                    # case, and assume it's the test's "name" if so
                    altname = cell.strip().strip("[]").split("|")[1]
                    continue
                except IndexError:
                    try:
                        altname = cell.strip().strip("[]").split(maxsplit=1)[1]
                    except IndexError:
                        altname = None
            if "{{result" in cell or "{{testresult" in cell:
                # any cell containing a result string is a 'result
                # cell', and the index of the cell in columns will be
                # the title of the column it is in. find_results()
                # returns an empty list if all results are filtered
                # out, so the results dict's keys will always
                # represent the full set of environments for this test
                try:
                    results[columns[i]] = find_results(cell, statuses, transferred)
                except IndexError:
                    # FIXME: log (messy table, see e.g. F15 'Multi
                    # Image')
                    pass
        row = cls(testcase, columns, section, secid, milestone, text, results)
        if altname:
            row.name = altname
        return row


# vim: set textwidth=100 ts=8 et sw=4:
