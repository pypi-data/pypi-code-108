# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

from functools import cmp_to_key
from types import SimpleNamespace
from typing import AbstractSet, Iterable, List, Mapping

from portmod.config.sets import is_selected
from portmod.config.use import get_use, get_user_global_use, get_user_use
from portmod.loader import load_all_installed, load_installed_pkg, load_pkg, load_pkg_fq
from portmod.repo import get_repo
from portmod.repo.metadata import get_use_flag_atom_aliases
from portmod.util import get_keyword_dep
from portmodlib.atom import Atom, FQAtom, QualifiedAtom, version_gt

from .formula import Formula, cond_flagstr, toggle_clause
from .tokens import AtomToken, FlagToken, Token

WEIGHTS = SimpleNamespace()

###################################################################################
WEIGHTS.base_update = 1  # Base weight for the lowest
WEIGHTS.update_diff = 10  # Difference between each update, in order
# Weight to keep mods that are installed, but not selected
# The negative of this is set if depclean is enabled (plus total_up_weight)
WEIGHTS.keep_installed = 2
# Weight to keep a mod that is not selected and not installed disabled
WEIGHTS.not_needed = 2
# FIXME: Flag settings should always override the cost of installing new packages
WEIGHTS.user_flag = 50  # Weight to keep a user-set flag the same
WEIGHTS.default_flag = 40  # Weight to keep a flag at its default value
###################################################################################


def weigh_clauses(
    atoms: Mapping[QualifiedAtom, Iterable[FQAtom]],
    flags: Iterable[FQAtom],
    explicit: AbstractSet[Atom],
    *,
    deep: bool,
    depclean: bool,
    update: bool,
    emptytree: bool,
) -> Formula:
    """Creates soft clauses for the given atoms"""
    formula = Formula()
    # Soft clauses to minimize unwanted changes to user's configuration

    # Track total weights so that we can make sure that higher-priority clauses
    # always have a greater weight
    total_up_weight = 0
    total_not_needed = 0

    # Clause for each mod not installed, with a small weight penalty for installing them
    for group in atoms:
        for atom in atoms[group]:
            if (
                not load_installed_pkg(Atom(atom.CPN))
                and not is_selected(atom)
                and Atom(atom.CPN) not in explicit
            ):
                formula.append(
                    [AtomToken(atom, polarity=False)], weight=WEIGHTS.not_needed
                )
                total_not_needed += WEIGHTS.not_needed

    # When deep depcleaning, keep flags as they are,
    # so the only change should be packages being removed.
    flag_formula, total_flag_weight = weigh_flags(
        flags,
        atoms,
        explicit,
        update=update,
        deep=deep,
        freeze=depclean and deep and not update,
    )
    formula.merge(flag_formula)

    # Ensure that the update weight is at least greater than the total number of packages to
    # overcome the basic resistance against moving from an installed package to the repository's
    # version of that installed package (i.e. rebuilding)
    total_atoms = sum(len(group) for group in atoms)

    # Penalize out of date versions.
    for group in atoms:
        # Divide mods into stable, testing and unstable
        # If user accepts testing keywords, they will be considered stable
        stable = set()
        testing = set()
        unstable = set()
        for atom in atoms[group]:
            mod = load_pkg_fq(atom)
            keyword = get_keyword_dep(mod)
            if not keyword:
                stable.add(atom)
            elif keyword.keyword.startswith("~"):
                testing.add(atom)
            elif keyword.keyword == "**":
                unstable.add(atom)

        i = WEIGHTS.base_update
        inc = WEIGHTS.update_diff + total_flag_weight

        def cmp(x, y):
            (vx, rx, ax) = x
            (vy, ry, ay) = y
            # Atoms are sorted first by version, then repo priority.
            # The installed Repo (here represented by None) has the
            # lowest priority
            if version_gt(vx, vy):
                return -1
            elif not version_gt(vy, vx):
                # If nether is greater than the other, they are equal
                # The installed version comes first, unless the package was selected
                if (atom.CPN in explicit and not update) or emptytree:
                    if rx is None:
                        return 1
                    if ry is None:
                        return -1
                else:
                    if rx is None:
                        return -1
                    if ry is None:
                        return 1
                if rx.priority > ry.priority:
                    return -1
            return 1

        def weigh(li):
            nonlocal i, total_up_weight
            tosort = []
            for atom in li:
                if atom.R.endswith("::installed") or atom.R == "installed":
                    repo = None
                else:
                    repo = get_repo(atom.R)
                tosort.append((atom.PVR, repo, atom))

            inorder = sorted(tosort, key=cmp_to_key(cmp))
            for index, (version, repo, atom) in enumerate(inorder):
                formula.append([AtomToken(atom, polarity=False)], weight=i)
                if (
                    index < len(inorder) - 1
                    and inorder[index + 1][0] == version
                    and repo is None
                ):
                    # This version is installed
                    # The weight difference between installed and non-installed should be exactly one
                    i += 1
                else:
                    i += inc + total_not_needed + total_atoms
                    total_up_weight += i

        weigh(stable)
        weigh(testing)
        weigh(unstable)

        # At most one version of the mod must be installed
        formula.append(
            [AtomToken(atom) for atom in atoms[group]],
            "inviolable-rule",
            "At most one version may be installed",
            atmost=1,
        )

    total_depclean_weight = total_up_weight

    # Clause for each mod installed, but not selected, penalizing their removal
    # If depclean is set, we instead weigh them to remove if possible
    for mod in load_all_installed():
        if (
            not is_selected(mod.ATOM)
            and Atom(mod.CPN) not in explicit
            and not emptytree
        ):
            # If update and deep are passed, penalize removal, but updates override
            if update and deep:
                formula.append([AtomToken(mod.ATOM)], weight=WEIGHTS.keep_installed)
            elif depclean and deep:
                for pkg in load_pkg(Atom(mod.CPN)):
                    formula.append(
                        [AtomToken(pkg.ATOM, polarity=False)],
                        weight=WEIGHTS.keep_installed + total_up_weight,
                    )
                    total_depclean_weight += total_up_weight
            else:  # if update is not passed, stay installed regardless of updates
                formula.append(
                    [AtomToken(mod.ATOM)],
                    weight=WEIGHTS.keep_installed + total_up_weight,
                )
    # Packages which are already installed should, if not explicitly depcleaned,
    # be kep in their current state. This must override the weight of packages to be removed,
    # otherwise a package may be downgraded to avoid new dependencies.
    for pkg in load_all_installed():
        if (
            is_selected(pkg.ATOM)
            and Atom(pkg.CPN) not in explicit
            and not (update and deep)
            and not emptytree
        ):
            formula.append(
                [AtomToken(pkg.ATOM)],
                weight=WEIGHTS.keep_installed + total_depclean_weight,
            )

    # When depcleaning, make sure the weight of installing not installed mods is higher
    # than the weight of removing unneeded mods. This prevents depcleaning from swapping out
    # mods in or expressions for each other.
    if depclean:
        for group in atoms:
            for atom in atoms[group]:
                if (
                    not load_installed_pkg(Atom(atom.CPN))
                    and not is_selected(atom)
                    and Atom(atom.CPN) not in explicit
                ):
                    formula.append(
                        [AtomToken(atom, polarity=False)],
                        weight=WEIGHTS.not_needed
                        + total_up_weight
                        + WEIGHTS.keep_installed,
                    )
    return formula


def weigh_flags(
    flags: Iterable[FQAtom],
    atoms: Mapping[QualifiedAtom, Iterable[FQAtom]],
    explicit: AbstractSet[Atom],
    *,
    update: bool,
    freeze: bool,
    deep: bool,
):
    formula = Formula()

    def iterate_flags():
        for flagatom in flags:
            flag = list(flagatom.USE)[0]  # Note: each only has one flag
            assert not flag.startswith("-")
            assert not flagatom.startswith("-")
            enabledatom = FlagToken(flagatom)
            atom_nouse = flagatom.strip_use()
            pkg = load_pkg_fq(atom_nouse)
            yield flag, AtomToken(atom_nouse), enabledatom, pkg

        # We also need to consider flags which don't show up in DEPEND-style strings
        # since flags in IUSE may have an alias
        for group in atoms:
            for atom in atoms[group]:
                pkg = load_pkg_fq(atom)
                for flag in pkg.IUSE_EFFECTIVE:
                    flagatom = FQAtom(f"{pkg.ATOM}[{flag}]")
                    if flagatom not in flags:
                        yield flag, AtomToken(pkg.ATOM), FlagToken(flagatom), pkg

    default_weight = WEIGHTS.default_flag
    total_flag_weight = 0
    total_user_weight = 0

    # Clauses for default use flag values, with a small penalty for changes from
    #    the default setting,
    repo_aliases = {}
    for flag, atom, flagatom, pkg in iterate_flags():
        if freeze:
            # All flags are required to keep their current state
            # Note: mod.get_use() will return installed use, not configured use,
            # for an installed package.
            enabled = pkg.get_use()

            if flag in enabled:
                formula.append([atom.neg(), flagatom])
            else:
                formula.append([atom.neg(), flagatom.neg()])

        elif (
            (deep and update)
            or atom.value.CPN in explicit
            or not load_installed_pkg(pkg.CPN)
        ):
            if pkg.REPO not in repo_aliases:
                repo_aliases[pkg.REPO] = get_use_flag_atom_aliases(
                    get_repo(pkg.REPO).location
                )
            aliases = repo_aliases[pkg.REPO]
            user_flags = get_user_use(pkg.ATOM)
            global_user_flags = get_user_global_use()
            if flag in user_flags:
                pass
            elif "-" + flag in user_flags:
                pass
            elif flag in global_user_flags:
                pass
            elif "-" + flag in global_user_flags:
                pass
            elif flag in aliases and aliases[flag].CPN != atom.value.CPN:
                alias = aliases[flag]

                if alias.CPN not in atoms:
                    # Package isn't installed, or even in the dependency tree,
                    # so default to disabled
                    formula.append([flagatom.neg()], weight=default_weight)
                    continue

                desc = [
                    "variable for linking alias to packages",
                    "Should never cause a conflict",
                ]

                aliasdeps: List[List[Token]] = []
                for aliased_pkg in load_pkg(alias):
                    tokens: List[Token] = []
                    if alias.USE:
                        # List of tokens relevant to the use flag, plus a variable which will be
                        # used later to reference it
                        # Var at beginning of clause represents the entire flag.
                        # I.e. if any of the parts are not present, it's false.
                        # If all the parts are present, it's true
                        tokens.append(formula.genvariable(desc))
                        for alias_flag in alias.USE:
                            tokens.append(
                                cond_flagstr(aliased_pkg.ATOM, alias_flag, negtoken="-")
                            )

                    tokens.append(AtomToken(aliased_pkg.ATOM))
                    aliasdeps.append(tokens)

                # If no package matching the alias is installed,
                # this will give weight to the flag being disabled.
                formula.append(
                    [flagatom.neg()] + [clause[0] for clause in aliasdeps],
                    weight=default_weight,
                )
                for clause in aliasdeps:
                    if len(clause) > 1:
                        # This makes the variable at the beginning true if all the parts are true
                        formula.append([clause[0]] + toggle_clause(clause[1:]))

                        # This makes the variable at the beginning false if any of the parts are false
                        for term in clause[1:]:
                            formula.append([clause[0].neg(), term])

                # var is true iff no packages matching the alias are installed
                var = formula.genvariable(desc)
                # This will give weight to the flag being enabled, unless no package
                # matching the alias is installed.
                formula.append([flagatom, var], weight=default_weight)

                # If all packages are not installed, var must be true
                formula.append(
                    [var] + [clause[0] for clause in aliasdeps],
                )

                for clause in aliasdeps:
                    # If package is installed, var must be false
                    formula.append([var.neg(), clause[0].neg()])

            elif flag in get_use(pkg)[0]:  # default value
                formula.append([atom.neg(), flagatom], weight=default_weight)
                total_flag_weight += default_weight
            else:
                formula.append([atom.neg(), flagatom.neg()], weight=default_weight)
                total_flag_weight += default_weight
        else:
            # If not running in deep mode, keep flags the same for
            # non-selected but previously installed packages, if possible
            enabled = pkg.get_use()

            if flag in enabled:
                formula.append([atom.neg(), flagatom], weight=default_weight)
            else:
                formula.append([atom.neg(), flagatom.neg()], weight=default_weight)

    user_weight = WEIGHTS.user_flag + total_flag_weight
    # Clauses for user flags. These will always override changes from the default value.
    for flag, atom, flagatom, mod in iterate_flags():
        if (
            (deep and update)
            or atom.value.CPN in explicit
            or not load_installed_pkg(mod.CPN)
        ):
            user_flags = get_user_use(mod.ATOM)
            global_user_flags = get_user_global_use()
            if flag in user_flags:
                formula.append([atom.neg(), flagatom], weight=user_weight)
                total_user_weight += user_weight
            elif "-" + flag in user_flags:
                formula.append([atom.neg(), flagatom.neg()], weight=user_weight)
                total_user_weight += user_weight
            elif flag in global_user_flags:
                formula.append([atom.neg(), flagatom], weight=user_weight)
                total_user_weight += user_weight
            elif "-" + flag in global_user_flags:
                formula.append([atom.neg(), flagatom.neg()], weight=user_weight)
                total_user_weight += user_weight

    return formula, total_user_weight
