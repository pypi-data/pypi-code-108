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
"""This file contains helper functions that don't strictly belong in
any particular class or even in another file but outside of a class."""

import re
from decimal import Decimal

import fedfind.helpers
import fedfind.release

MILESTONE_PAIRS = (
    ("Rawhide", "100"),
    # We called Branched nightly pages 'Nightly' in F21 cycle.
    ("Nightly", "149"),
    ("Branched", "150"),
    ("Pre-Alpha", "175"),
    ("Alpha", "200"),
    ("Pre-Beta", "375"),
    ("Beta", "400"),
    ("Preview", "600"),
    ("Pre-Final", "775"),
    ("Final", "800"),
    ("RC", "800"),
    ("Postrelease", "900"),
)

COMPOSE_PAIRS = (
    # Some F12 crap
    ("PreBeta", "100"),
    ("TC", "200"),
    # and this.
    ("Pre-RC", "300"),
    # The extra digit here is a dumb way to make sure RC1 sorts
    # later than TC10 - otherwise you get 20010 vs. 6001, and 20010
    # wins. It might be better to treat the 'TC' / 'RC' as a separate
    # element in triplet_sort, but that's a bit harder and makes its
    # name a lie...
    ("RC", "6000"),
)


def fedora_release_sort(string):
    """Fed a string that looks something like a Fedora pre-release /
    compose version, this will output a modified version of the string
    which should sort correctly against others like it. Handles stuff
    like 'Preview' coming before 'Final', and 'TC' coming before 'RC'.
    'Alpha', 'Beta' and 'Final' sort correctly by pure chance, but we
    handle them here anyway to make sure. wikitcms ValidationEvent and
    ValidationPage objects have a 'sortname' property you can use
    instead of calling this directly. Milestones have a letter so they
    sort after nightlies (nightlies are usually going to be earlier).
    NOTE: can only sort compose event versions, really. With this
    function, '22 Alpha TC1' > '22 Alpha'.
    """
    # Some MILESTONES are substrings of COMPOSES so we do Cs first
    for (orig, repl) in COMPOSE_PAIRS + MILESTONE_PAIRS:
        string = string.replace(orig, repl)
    return string


def triplet_sort(release, milestone, compose):
    """Just like fedora_release_sort, but requires you to pass the
    now-'standard' release, milestone, compose triplet of inputs.
    This is a better way in most cases as you're going to have more
    certainty about instantiating wikitcms/fedfind objects from it,
    plus we can handle things like '23' being higher than '23 Beta'
    or '23 Final TC1'. Expects the inputs to be strings. The elements
    in the output tuple will be ints if possible as this gives a
    better sort, but may be strings if we missed something; you're not
    meant to *do* anything with the tuple but compare it to another
    similar tuple.
    """
    for (orig, repl) in MILESTONE_PAIRS:
        milestone = milestone.replace(orig, repl)
        if not milestone:
            # ('23', 'Final', '') == ('23', '', '')
            milestone = "800"
    for (orig, repl) in COMPOSE_PAIRS:
        compose = compose.replace(orig, repl)
        if not compose:
            compose = "999"
    # We want to get numerical sorts if we possibly can, so e.g.
    # TC10 (becomes 20010) > TC9 (becomes 2009). But just in case
    # we get passed a character we don't substitute to a digit,
    # check first.
    release = str(release)
    if release.isdigit():
        release = int(release)
    if milestone.isdigit():
        milestone = int(milestone)
    if compose.isdigit():
        compose = int(compose)
    else:
        # this is a bit magic but handles "TC1.1" (old-school),
        # "1.1" (new-school candidates), and "20160314.n.0" (new-
        # school nightlies)
        (comp, respin) = (compose.split(".")[0], compose.split(".")[-1])
        if comp.isdigit() and respin.isdigit():
            compose = Decimal(".".join((comp, respin)))
    return (release, milestone, compose)


def triplet_unsort(release, milestone, compose):
    """Reverse of triplet_sort."""
    (release, milestone, compose) = (str(release), str(milestone), str(compose))
    for (repl, orig) in MILESTONE_PAIRS:
        milestone = milestone.replace(orig, repl)
        if milestone == "800":
            milestone = "Final"
    # We don't want to do the replace here if the compose is a date,
    # because any of the values might happen to be in the date. This
    # is a horrible hack that should be OK (until 2100, at least).
    if fedfind.helpers.date_check(compose, fail_raise=False):
        pass
    elif fedfind.helpers.date_check(compose.split(".")[0], fail_raise=False):
        # this is slightly magic but should do for now
        (comp, respin) = compose.split(".")
        compose = f"{comp}.n.{respin}"
    else:
        for (repl, orig) in COMPOSE_PAIRS:
            compose = compose.replace(orig, repl)
            if compose == "999":
                compose = ""
    return (release, milestone, compose)


def rreplace(string, old, new, occurrence):
    """A version of the str.replace() method which works from the right.
    Taken from https://stackoverflow.com/questions/2556108/
    """
    elems = string.rsplit(old, occurrence)
    return new.join(elems)


def normalize(text):
    """Lower case and replace ' ' with '_' so I don't have to
    keep retyping it.
    """
    return text.lower().replace(" ", "_")


def find_bugs(text):
    """Find RH bug references in a given chunk of text. More than one
    method does this, so we'll put the logic here and they can share
    it. Copes with [[rhbug:(ID)]] links, {{bz|(ID)}} templates and
    URLs that look like Bugzilla. Doesn't handle aliases (only matches
    numeric IDs 6 or 7 digits long). Returns a set (so bugs that occur
    multiple times in the text will only appear once in the output).
    """
    bugs = set()
    bzpatt = re.compile(
        r"({{bz *\| *|" r"\[\[rhbug *: *|" r"bugzilla\.redhat\.com/show_bug\.cgi\?id=)" r"(\d{6,7})"
    )
    matches = bzpatt.finditer(text)
    for match in matches:
        bugs.add(match.group(2))
    # Filter out bug IDs usually used as examples
    for bug in ("12345", "123456", "54321", "654321", "234567", "1234567", "7654321"):
        bugs.discard(bug)
    return bugs


def cid_to_event(cid):
    """Given a Pungi 4 compose ID, figure out the appropriate wikitcms
    (release, milestone, compose) triplet. Guesses the appropriate
    release number to assign to the event for Rawhide composes. To
    do the opposite, you can use the ff_release property of Validation
    Event instances.
    """
    parsed = fedfind.helpers.parse_cid(cid, dic=True)
    dist = parsed["short"]
    release = parsed["version"].lower()
    vertype = parsed["version_type"]
    date = parsed["date"]
    typ = parsed["compose_type"]
    respin = parsed["respin"]
    if dist not in ("Fedora", "Fedora-Modular", "Fedora-IoT"):
        # we only have validation events for these composes ATM -
        # not e.g. FedoraRespin or Fedora-Atomic ones
        raise ValueError(f"No validation events for {dist} composes!")
    if vertype != "ga":
        # this ensures we don't create events for updates/u-t composes
        raise ValueError("No validation events for updates composes!")
    if typ == "production":
        # we need to get the label and parse that
        ffrel = fedfind.release.get_release(cid=cid)
        if not ffrel.label:
            raise ValueError(
                f"{cid} looks like a production compose, but found "
                "no label! Cannot determine event."
            )
        (milestone, compose) = ffrel.label.rsplit("-", 1)
        return (dist, release, milestone, compose)

    if not typ == "nightly":
        # we don't have validation events for any compose types other
        # than 'production' and 'nightly'
        raise ValueError("cid_to_event(): cannot guess event for 'test' compose")

    # nightlies
    if release == "rawhide":
        # the release number for new Rawhide events should always be
        # 1 above the highest current 'real' release (branched or
        # stable). FIXME: this will not do the right thing for *old*
        # composes, not sure if we can fix that sensibly.
        release = str(fedfind.helpers.get_current_release(branched=True) + 1)
        milestone = "Rawhide"
    else:
        milestone = "Branched"
    compose = f"{date}.n.{respin}"
    return (dist, release, milestone, compose)


def validate_dist(dist):
    """Just a quick check that dist names match the expected form."""
    distpatt = re.compile(r"^Fedora(-\w+)?$")
    if distpatt.match(dist):
        return dist
    raise ValueError("%s is not a valid dist!" % dist)


# vim: set textwidth=100 ts=8 et sw=4:
