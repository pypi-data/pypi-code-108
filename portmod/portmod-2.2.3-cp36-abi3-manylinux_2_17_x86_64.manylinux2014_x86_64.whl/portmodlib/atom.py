# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

import re
from collections import namedtuple
from typing import AbstractSet, Any, Dict, Optional, Set, TypeVar

"""
Module for handling package atoms

All atom classes defined in this module should be considered read-only.
Modification of an Atom object may have unexpected side-effects
"""

flag_re = r"[A-Za-z0-9][A-Za-z0-9+_-]*"
useflag_re = re.compile(r"^" + flag_re + r"$")
usedep_re = (
    r"(?P<prefix>[!-]?)(?P<flag>"
    + flag_re
    + r")(?P<default>(\(\+\)|\(\-\))?)(?P<suffix>[?=]?)"
)
_usedep_re = re.compile("^" + usedep_re + "$")

op_re = r"(?P<B>(!!))?(?P<OP>([<>]=?|[<>=~]))?"
cat_re = r"((?P<C>[A-Za-z0-9][A-Za-z0-9\-]*)/)?"
ver_re = r"(\d+)((\.\d+)*)([a-z]?)((_(pre|p|beta|alpha|rc)\d*)*)"
rev_re = r"(-(?P<PR>r[0-9]+))?"
repo_re = r"(::(?P<R>[A-Za-z0-9_][A-Za-z0-9_-]*(::installed)?))?"
_atom_re = re.compile(
    op_re
    + cat_re
    + r"(?P<P>(?P<PN>[A-Za-z0-9+_-]+?)(-(?P<PV>"
    + ver_re
    + r"))?)"
    + rev_re
    + repo_re
    + r"(\[(?P<USE>.*)\])?$"
)


class InvalidAtom(Exception):
    "Exception indicating an atom has invalid syntax"


class UnqualifiedAtom(Exception):
    """
    Exception indicating an atom, which was expected to be
    qualified with a category, has no category
    """

    def __init__(self, atom):
        self.atom = atom

    def __str__(self):
        return f"Atom {self.atom} was expected to have a category!"


T = TypeVar("T", bound="Atom")


class Atom(str):
    CP: Optional[str]
    """
    The category, package name and version, excluding revision

    E.g. ``base/example-suite-1.0``
    """
    CPN: Optional[str]
    """
    The category and package name

    E.g. ``base/example-suite``
    """
    USE: Set[str] = set()
    """
    Use flags set on the atom.

    E.g. ``{minimal}`` in ``base/example-suite[minimal]``
    """
    P: str
    """
    The package name and version, excluding revision

    E.g. ``example-suite-1.0``
    """
    PN: str
    """
    The package name

    E.g. ``example-suite``
    """
    PF: str
    """
    The package name and version, including revision

    E.g. ``example-suite-1.0-r1``
    """
    PV: Optional[str]
    """
    The package version, not including revision

    E.g. ``1.0``
    """
    PR: Optional[str]
    """
    The package revision

    E.g. ``r1``
    """
    C: Optional[str]
    """
    The package category

    E.g. ``base``
    """
    R: Optional[str]
    """
    The package repository

    E.g. ``openmw`` in base/example-suite-1.0-r1::openmw
    """
    OP: Optional[str]
    """
    An operator.

    See PMS section `8.2.6.1 <https://projects.gentoo.org/pms/7/pms.html#x1-760008.2.6.1>`_,
    noting that Weak blocks are not currently supported by Portmod, and blocks don't show up
    in OP (they instead set the BLOCK field).

    E.g. ``openmw`` in base/example-suite-1.0-r1::openmw
    """
    BLOCK: bool
    """
    If true, this atom is a blocker, referring to a package which must not be installed.

    E.g. ``!!base/example-suite``
    """
    PVR: Optional[str]
    """
    The version and revision

    E.g. 1.0-r1
    """
    CPF: str
    """
    The category, package name and version, including revision

    E.g. ``base/example-suite-1.0-r1``
    """

    _CACHE: Dict[str, Any] = {}

    def __init__(self, atom: str):
        if atom in self._CACHE:
            self.__dict__ = self._CACHE[atom]
            return

        match = _atom_re.match(atom)
        if not match:
            raise InvalidAtom("Invalid atom %s. Cannot parse" % (atom))

        if match.group("P") and match.group("C"):
            self.CP = match.group("C") + "/" + match.group("P")
            self.CPN = match.group("C") + "/" + match.group("PN")
        else:
            self.CP = None
            self.CPN = None

        if match.group("USE"):
            self.USE = set(match.group("USE").split(","))
            for x in self.USE:
                m = _usedep_re.match(x)
                if not m:
                    raise InvalidAtom(
                        "Invalid use dependency {} in atom {}".format(atom, x)
                    )

        if match.group("PR"):
            self.PF = match.group("P") + "-" + match.group("PR")
        else:
            self.PF = match.group("P")

        self.P = match.group("P")
        self.PN = match.group("PN")
        self.PV = match.group("PV")
        self.PR = match.group("PR")
        self.C = match.group("C")
        self.R = match.group("R")
        self.OP = match.group("OP")
        self.BLOCK = match.group("B") is not None
        self.PVR = self.PV
        if self.PR:
            self.PVR += "-" + self.PR

        if self.C:
            self.CPF = self.C + "/" + self.PF
        else:
            self.CPF = self.PF

        if self.OP is not None and self.PV is None:
            raise InvalidAtom(
                "Atom %s has a comparison operator but no version!" % (atom)
            )

        self._CACHE[atom] = self.__dict__

    def evaluate_conditionals(self, use: AbstractSet[str]) -> "Atom":
        """
        Create an atom instance with any USE conditionals evaluated.
        @param use: The set of enabled USE flags
        @return: an atom instance with any USE conditionals evaluated
        """
        tokens = set()

        for x in self.USE:
            m = _usedep_re.match(x)

            if m is not None:
                operator = m.group("prefix") + m.group("suffix")
                flag = m.group("flag")
                default = m.group("default")
                if default is None:
                    default = ""

                if operator == "?":
                    if flag in use:
                        tokens.add(flag + default)
                elif operator == "=":
                    if flag in use:
                        tokens.add(flag + default)
                    else:
                        tokens.add("-" + flag + default)
                elif operator == "!=":
                    if flag in use:
                        tokens.add("-" + flag + default)
                    else:
                        tokens.add(flag + default)
                elif operator == "!?":
                    if flag not in use:
                        tokens.add("-" + flag + default)
                else:
                    tokens.add(x)
            else:
                raise Exception("Internal Error when processing atom conditionals")

        atom = Atom(self)
        atom.USE = tokens
        return atom

    def strip_use(self: T) -> T:
        """Returns the equivalent of this atom with the USE dependencies removed"""
        return self.__class__(re.sub(r"\[.*\]", "", str(self)))

    def use(self, *flags: str):
        """returns atom with use flag dependency"""
        return self.__class__(f'{self}[{",".join(flags)}]')

    def with_category(self, category: str) -> "QualifiedAtom":
        return QualifiedAtom(
            (self.BLOCK and "!!" or "")
            + (self.OP or "")
            + category
            + "/"
            + self.PF
            + (self.R or "")
        )


class QualifiedAtom(Atom):
    """Atoms that include categories"""

    CP: str
    CPN: str
    CPF: str
    C: str

    def __init__(self, atom: str):
        super().__init__(atom)

        if not self.C:
            raise UnqualifiedAtom(atom)


class VAtom(QualifiedAtom):
    """Atoms that include version information"""

    PV: str
    PVR: str

    def __init__(self, atom: str):
        super().__init__(atom)
        assert self.PV


class FQAtom(VAtom):
    """Atoms that include all possible non-optional fields"""

    R: str

    def __init__(self, atom: str):
        super().__init__(atom)
        assert self.R


VersionMatch = namedtuple(
    "VersionMatch", ["version", "numeric", "letter", "suffix", "revision"]
)


def suffix_gt(a_suffix: str, b_suffix: str) -> bool:
    """Returns true iff a_suffix > b_suffix"""
    suffixes = ["alpha", "beta", "pre", "rc", "p"]
    return suffixes.index(a_suffix) > suffixes.index(b_suffix)


def version_gt(version1: str, version2: str) -> bool:
    """
    Version comparision function

    args:
        version1: A version string
        version2: Another version string

    returns:
        True if and only if version1 is greater than version2
    """
    vre = re.compile(
        r"(?P<NUMERIC>[\d\.]+)"
        r"(?P<LETTER>[a-z])?"
        r"(?P<SUFFIX>(_[a-z]+\d*)*)"
        r"(-r(?P<REV>\d+))?"
    )
    match1 = vre.match(version1)
    match2 = vre.match(version2)

    assert match1 is not None
    assert match2 is not None
    v_match1 = VersionMatch(
        version=version1,
        numeric=match1.group("NUMERIC").split("."),
        letter=match1.group("LETTER") or "",
        suffix=match1.group("SUFFIX") or "",
        revision=int(match1.group("REV") or "0"),
    )
    v_match2 = VersionMatch(
        version=version2,
        numeric=match2.group("NUMERIC").split("."),
        letter=match2.group("LETTER") or "",
        suffix=match2.group("SUFFIX") or "",
        revision=int(match2.group("REV") or "0"),
    )

    # Compare numeric components
    for index, val in enumerate(v_match1.numeric):
        if index >= len(v_match2.numeric):
            return True
        if int(val) > int(v_match2.numeric[index]):
            return True
        if int(val) < int(v_match2.numeric[index]):
            return False
    if len(v_match2.numeric) > len(v_match1.numeric):
        return False

    # Compare letter components
    if v_match1.letter > v_match2.letter:
        return True
    if v_match1.letter < v_match2.letter:
        return False

    # Compare suffixes
    if v_match1.suffix:
        a_suffixes = v_match1.suffix.lstrip("_").split("_")
    else:
        a_suffixes = []
    if v_match2.suffix:
        b_suffixes = v_match2.suffix.lstrip("_").split("_")
    else:
        b_suffixes = []
    for a_s, b_s in zip(a_suffixes, b_suffixes):
        asm = re.match(r"(?P<S>[a-z]+)(?P<N>\d+)?", a_s)
        bsm = re.match(r"(?P<S>[a-z]+)(?P<N>\d+)?", b_s)
        assert asm
        assert bsm
        a_suffix = asm.group("S")
        b_suffix = bsm.group("S")
        a_suffix_num = int(asm.group("N") or "0")
        b_suffix_num = int(bsm.group("N") or "0")
        if a_suffix == b_suffix:
            if b_suffix_num > a_suffix_num:
                return False
            if a_suffix_num > b_suffix_num:
                return True
        elif suffix_gt(a_suffix, b_suffix):
            return True
        else:
            return False
    # More suffixes implies an earlier version,
    # except when the suffix is _p
    if len(a_suffixes) > len(b_suffixes):
        if a_suffixes[len(b_suffixes)].startswith("p"):
            return True
        return False
    if len(a_suffixes) < len(b_suffixes):
        if b_suffixes[len(a_suffixes)].startswith("p"):
            return False
        return True

    # Compare revisions
    if v_match1.revision > v_match2.revision:
        return True
    if v_match1.revision < v_match2.revision:
        return False

    # Equal
    return False


def atom_sat(specific: Atom, generic: Atom, *, ignore_name: bool = False) -> bool:
    """
    Determines if a fully qualified atom (can only refer to a single package)
    satisfies a generic atom
    """

    if not ignore_name:
        if specific.PN != generic.PN:
            # Mods must have the same name
            return False

        if generic.C and (generic.C != specific.C):
            # If para defines category, it must match
            return False

    if generic.R and (generic.R != specific.R):
        # If para defines repo, it must match
        return False

    if not generic.OP:
        # Simple atom, either one version or all versions will satisfy

        # Check if version is correct
        if generic.PV and (specific.PV != generic.PV):
            return False

        # Check if revision is correct
        if generic.PR and (specific.PR != generic.PR):
            return False
    elif generic.PV and specific.PV:
        assert generic.PVR and specific.PVR
        equal = specific.PVR == generic.PVR
        verequal = specific.PV == generic.PV
        lessthan = version_gt(generic.PVR, specific.PVR)
        greaterthan = version_gt(specific.PVR, generic.PVR)

        if generic.OP == "=":
            return equal
        if generic.OP == "~":
            return verequal
        if generic.OP == "<":
            return lessthan
        if generic.OP == "<=":
            return equal or lessthan
        if generic.OP == ">":
            return greaterthan
        if generic.OP == ">=":
            return equal or greaterthan

    return True
