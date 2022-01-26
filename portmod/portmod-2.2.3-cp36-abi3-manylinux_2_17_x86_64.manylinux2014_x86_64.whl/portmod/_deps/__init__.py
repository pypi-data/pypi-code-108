# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

"""
Dependency resolution module

Converts mod dependency links and REQUIRED_USE conditions into a MAX-SAT formula in
conjunctive normal form.
This formula is then solved using pysat (python-sat on pypi) and the resulting model
converted back into a list of installed mods and their use flag configuration.

Note that the hard requirements defined in DEPEND, RDEPEND and REQUIRED_USE are
converted into a SAT formula that must be solved in its entirety.
We use a MAX-SAT solver because there are also other soft requirements which are used
to avoid installing mods unnecessarily and to avoid changing the user's use flag
configuration, if possible.

See https://en.wikipedia.org/wiki/Boolean_satisfiability_problem for details on
the SAT problem
"""

from collections import defaultdict
from logging import info, warning
from typing import AbstractSet, Dict, Iterable, List, Optional, Set, Tuple

from portmod.config.sets import get_set
from portmod.config.use import get_use
from portmod.globals import env
from portmod.loader import (
    AmbiguousAtom,
    load_all_installed,
    load_installed_pkg,
    load_pkg,
    load_pkg_fq,
)
from portmod.transactions import (
    PackageDoesNotExist,
    Transactions,
    UseDep,
    generate_transactions,
)
from portmodlib.atom import Atom, FQAtom, QualifiedAtom, atom_sat
from portmodlib.l10n import l10n

from .formula import Formula, Target, add_masked, cond_flagstr, fstr, generate_formula
from .tokens import AtomToken, FlagToken, Token, VariableToken
from .weights import weigh_clauses


class DepError(Exception):
    """Indicates an unsatisfiable transaction"""


class _HiddenToken(str):
    def __str__(self):
        return ""


def find_dependency(
    clauses: Iterable[Formula.Clause], model: Set[Token], modstr: str
) -> Optional[Formula.Clause]:
    """Finds clause that depends on the given atom"""
    # Ignore top-level dependencies
    if not isinstance(modstr, Atom):
        return None

    for clause in clauses:
        if isinstance(clause, Formula.DepClause):
            if atom_sat(Atom(modstr), clause.dependency) and all(
                var in model for var in clause.requirements
            ):
                return clause
    return None


def find_conflict(
    clauses: Iterable[Formula.Clause], display_conflict: bool = False
) -> Tuple[List[Formula.Clause], Optional[List[Formula.Clause]]]:
    """
    Produces traces for the provided conflicting clauses

    Find clause that caused the solver to fail

    Then backtrack the package that added that clause until we reach @selected by
    looking for clauses containing the (enabled) mod as a token.
    Returns this trace.

    If display_conflict is True, also return trace for a package that requires/blocks
    the clause that caused the failure

    args:
        clauses: The clauses to be solved. These are assumed to contain a conflict
        display_conflict: If true, return a second list describing the package which
                          requires/blocks the package which caused the failure
                          Otherwise, the second list will always be None
    raises:
        DepError: if no conflict was found in the clauses

    returns:
        The conflicting clause and its parent clauses.
    """
    from pysat.solvers import Solver

    # Note: we use mc by itself rather than with RC2 (as used in the main resolve function)
    # since we don't need to take into account weighted "soft" clauses.
    with Solver("mc") as solver:
        solveableformula = []
        # Add atmost clauses first, as they won't by themselves cause conflicts,
        # and are not very useful for explaining a failed transaction
        for clause in clauses:
            if isinstance(clause, Formula.MetaClause) and clause.atmost is not None:
                solver.add_atmost(clause.intclause, clause.atmost)

        lastmodel = set()
        # FIXME: It's more efficient to do a binary rather than linear search
        for clause in clauses:
            # Ignore atmost clauses we already added, and weighted clauses
            # which will never cause a conflict
            if isinstance(clause, Formula.MetaClause) and (
                clause.atmost is not None or clause.weight is not None
            ):
                continue

            solver.add_clause(clause.intclause)

            if solver.solve():
                lastmodel = solver.get_model()
                solveableformula.append(clause)
            else:
                conflict = None
                model = set(map(Formula.getstring, lastmodel))

                for solveableclause in solveableformula:
                    # Find clause that contradicts failed clause
                    # Note that metaclauses don't have a blocks function,
                    if solveableclause.blocks(model, clause):
                        conflict = solveableclause
                        break

                source_trace = [clause]
                conflict_trace = None
                parent = find_dependency(solveableformula, model, clause.source)
                i = 1
                # Note: Any descriptor which is empty (when stringified) will be ignored
                #       This is for clauses added for constructed traces such as the use
                #       flag dependency traces
                while parent is not None and str(parent.source):
                    source_trace.append(parent)
                    parent = find_dependency(solveableformula, model, parent.source)
                    i += 1

                if conflict and display_conflict:
                    conflict_trace = [conflict]
                    parent = find_dependency(solveableformula, model, conflict.source)
                    i = 1
                    while parent is not None and str(parent.source):
                        conflict_trace.append(parent)
                        parent = find_dependency(solveableformula, model, parent.source)
                        i += 1

                return source_trace, conflict_trace
    raise DepError("Internal error: Unable to find conflict!")


def resolve(
    enabled: Iterable[Atom],
    disabled: Iterable[Atom],
    explicit: AbstractSet[Atom],
    selected: AbstractSet[Atom],
    selected_sets: AbstractSet[str],
    *,
    deep: bool = False,
    update: bool = False,
    depclean: bool = False,
    emptytree: bool = False,
) -> Transactions:
    """
    Calculates new mod configuration to match system after the given mods are installed

    Note: We have two modes of operation:

    Shallow
        We assume that all installed mods are fixed and will not
        change version. Any version of a newly selected mods may be installed.
        Note that use flags may change on installed mods.
    Deep
        We treat every mod as newly selected, and choose from among its versions

    args:
        enabled: Packages which are to be enabled/installed
        disabled: Packages which are to be disabled/removed
        selected: Enabled packages which were explicitly selected
        selected_sets: Sets which were explicitly selected (the contents of which
                would be in enabled)
        deep: Whether or not we are running in deep mode
        update: If true, packages will be updated, if possible.
        depclean: If true, packages which were neither explicitly selected, nor
                  required as dependencies, will be removed.
        emptytree: If true, all packages in the dependency tree will be rebuilt, as
                   if nothing was installed.
    returns:
        Transactions object representing the package changes required
    """
    # Slow imports
    from pysat.examples.rc2 import RC2

    info(l10n("calculating-dependencies"))
    formula = Formula()

    # List of sets of mod objects, with each being a specific version of that mod
    oldselected: List[Target] = []
    newenabled: Dict[str, Target] = dict()

    CMD_ATOM = "packages passed on command line"
    WORLD_ATOM = "world favourites file"

    for atom in list(enabled) + list(disabled):
        if not load_pkg(atom):
            raise PackageDoesNotExist(atom)

    newenabledset = {
        atom: CMD_ATOM
        for atom in set(enabled)
        | {atom for set_name in selected_sets for atom in get_set(set_name)}
    }
    for atom in disabled:
        name = load_pkg(atom)[0].CPN
        if name in newenabledset:
            del newenabledset[name]

    for atom in disabled:
        for mod in load_pkg(atom):
            formula.append_dep([AtomToken(mod.ATOM, polarity=False)], CMD_ATOM, atom)

    def create_modlist(atom):
        modlist = load_pkg(atom)

        # Raise exception if mod name is ambiguous (exists in multiple categories)
        if not all(mod.ATOM.C == modlist[0].ATOM.C for mod in modlist):
            raise AmbiguousAtom(atom, [mod.ATOM for mod in modlist])

        if not modlist:
            if atom in set(selected):
                raise PackageDoesNotExist(atom)

            raise PackageDoesNotExist(
                msg=l10n("package-does-not-exist-in-world", atom=atom)
            )
        return modlist

    for atom, source in newenabledset.items():
        modlist = create_modlist(atom)
        name = modlist[0].CPN
        if name in newenabled:
            newenabled[modlist[0].CPN].pkgs.extend(modlist)
            if newenabled[modlist[0].CPN].source is CMD_ATOM or source is CMD_ATOM:
                # Use generic atom if included multiple times on command line.
                # Not all versions in modlist will correspond to a specific version
                # passed on the command line.
                newenabled[modlist[0].CPN].atom = name
            # Prefer command line as source rather than world file
            if newenabled[modlist[0].CPN].source is WORLD_ATOM and source is CMD_ATOM:
                newenabled[modlist[0].CPN].source = CMD_ATOM
        else:
            newenabled[modlist[0].CPN] = Target(modlist, atom, source)

    for atom in get_set("world") - {load_pkg(atom)[0].CPN for atom in disabled}:
        if atom not in selected:
            modlist = create_modlist(atom)
            oldselected.append(Target(modlist, atom, "world favourites file"))

    # Any remaining installed mods don't need to remain installed if there aren't
    # any dependencies, so source is None
    installed = [Target([mod], mod.ATOM, None) for mod in load_all_installed()]

    selected_cpn = set()
    explicit_cpn = set()

    for atom in explicit:
        pkg = load_pkg(atom)[0]
        explicit_cpn.add(pkg.CPN)

    for atom in selected:
        pkg = load_pkg(atom)[0]
        selected_cpn.add(pkg.CPN)

    selected_from_sets: Set[QualifiedAtom] = set()
    for set_name in selected_sets:
        selected_from_sets |= {QualifiedAtom(atom) for atom in get_set(set_name)}

    # Hard clauses

    # The explicitly passed packages are aleays handled in deep mode
    formula.merge(generate_formula(list(newenabled.values()), set(), deep=True))

    # Existing packages are assumed not to need to change if not in deep mode,
    # so we ignore their dependency tree (unless run in deep mode).
    formula.merge(generate_formula(installed, set(), deep=deep))
    for target in oldselected:
        if load_installed_pkg(target.atom):
            formula.merge(generate_formula([target], set(), deep=deep))
        else:
            # world packages which are not installed should be merged in deep mode,
            # as they may need extra dependencies
            formula.merge(generate_formula([target], set(), deep=True))

    # Soft clauses
    formula.merge(
        weigh_clauses(
            formula.atoms,
            formula.flags,
            explicit=explicit_cpn,
            deep=deep,
            depclean=depclean,
            update=update,
            emptytree=emptytree,
        )
    )

    formula.merge(add_masked(formula.atoms, formula.flags))

    if depclean:
        for pkg in load_all_installed():
            # When depcleaning, installed packages should be frozen at their current
            # version, or else removed
            versions = load_pkg(Atom(pkg.ATOM.CPN))
            var = formula.genvariable(
                [f"No non-installed versions of {pkg.CPN} are allowed"]
            )
            # Clause requires that either the installed version should be removed,
            # or all other versions should be removed.
            # This means it is not possible for a version other than the installed version
            # to be kept
            formula.append_dep(
                [AtomToken(pkg.ATOM, polarity=False), var],
                "Selected packages must not be changed when depcleaning",
                pkg.ATOM,
            )
            # Var can only be true if all versions are not installed
            # as each clause requires that either a particular version is not installed,
            # or var is false.
            # Hence if var is true, every one of these clauses is satisfied by the left term
            for other in versions:
                if not other.INSTALLED:
                    formula.append(
                        [AtomToken(other.ATOM, polarity=False), var.neg()],
                        other.ATOM,
                        "Selected packages must not be changed when depcleaning",
                    )

            for flag in pkg.IUSE_EFFECTIVE:
                if flag in get_use(pkg)[0]:
                    flagdep = fstr(pkg.ATOM, flag)
                else:
                    flagdep = fstr(pkg.ATOM, flag).neg()
                formula.append_usedep(
                    [flagdep, AtomToken(pkg.ATOM, polarity=False)],
                    "Selected packages must not be changed when depcleaning",
                    pkg.ATOM,
                    flagdep,
                )

    if not formula.clauses:
        return Transactions()

    formula.make_numeric()
    wcnf = formula.get_wcnfplus()
    solver = RC2(wcnf, solver="mc")
    solver.compute()
    if solver.compute():
        info(l10n("done"))
        # Turn numbers in result back into strings
        result = set(
            filter(
                # Filter out custom variables that are only meaningful
                # for the computation
                lambda x: not isinstance(x, VariableToken),
                [Formula.getstring(num) for num in solver.model],
            )
        )
        flags = [token for token in result if isinstance(token, FlagToken)]
        enabled_final = [
            token.value
            for token in result
            if token.polarity and isinstance(token, AtomToken)
        ]
        enablednames = [atom.CPN for atom in enabled_final]
        disabled_final = [
            FQAtom(token.value)
            for token in result
            if not token.polarity and isinstance(token, AtomToken)
            # If mod is enabled and installed version is disabled,
            # ignore disabled version, and vice versa
            and token.value.CPN not in enablednames
        ]

        flag_dict: Dict[FQAtom, Set[str]] = defaultdict(set)
        for token in flags:
            if token.value.strip_use() in enabled_final:
                flag_dict[token.value.strip_use()].add(str(token))

        def is_installed(atom: Atom) -> bool:
            for fqatom in enabled_final:
                if atom_sat(fqatom, atom) and atom.USE <= flag_dict[fqatom]:
                    return True
            return False

        usedeps = []

        for token in flags:
            atom = token.value.strip_use()
            flag = list(token.value.USE)[0]
            if token.polarity:
                prefix = ""
            else:
                prefix = "-"

            # For all changes to the flag configuration, determine what caused the
            # change by re-running the solver with the requirement that the inverse of
            # the flag is set, and finding the conflicting clause
            if atom in enabled_final:
                pkg = load_pkg_fq(atom)
                # Note: this matches the condition in _deps.weights and is necessary since we
                # deliberately freeze flags on packages not explicitly specified
                if (
                    pkg.INSTALLED
                    and (deep and update or pkg.CPN in explicit_cpn)
                    or not pkg.INSTALLED
                ):
                    enabled_use, _ = get_use(pkg, is_installed=is_installed)
                else:
                    enabled_use = pkg.get_use()
                if (
                    not token.polarity
                    and flag in enabled_use
                    or token.polarity
                    and flag not in enabled_use
                ):
                    # To prevent solver from enabling a different version of the package,
                    # also require that the package is enabled
                    flag_config = [
                        Formula.UseDepClause(
                            _HiddenToken(), [token.neg()], atom, token.neg()
                        ).str2num(),
                        Formula.DepClause(
                            _HiddenToken(), [AtomToken(atom, True)], atom
                        ).str2num(),
                    ]

                    # If this is a result of a required use when a different flag is set,
                    # e.g. foo? ( bar ), then we need to force the rest of the configuration
                    for otherflag in pkg.IUSE_EFFECTIVE:
                        if flag != otherflag:
                            newtoken = cond_flagstr(atom, otherflag)
                            if otherflag not in enabled_use:
                                newtoken = newtoken.neg()
                            flag_config.append(
                                Formula.UseDepClause(
                                    _HiddenToken(), [newtoken], atom, newtoken
                                ).str2num(),
                            )

                    comment = []
                    try:
                        source_trace, _ = find_conflict(flag_config + formula.clauses)
                        for index, clause in enumerate(source_trace):
                            comment.append("# " + index * "  " + clause.colourless())
                    except DepError as error:
                        message = f"Internal Error: Unable to trace flag {flag} for package {pkg}"
                        if env.TESTING:
                            raise Exception(message) from error
                        warning(message)

                    usedeps.append(UseDep(atom, prefix + flag, None, comment))

        transactions = generate_transactions(
            enabled_final,
            disabled_final,
            selected_cpn,
            usedeps,
            flag_dict,
            emptytree=emptytree,
            update=update,
        )
        return transactions

    source_trace, conflict_trace = find_conflict(formula.clauses, display_conflict=True)
    exceptionstring = ""
    for index, clause in enumerate(source_trace):
        exceptionstring += index * "  " + f"{clause}\n"

    # conflict_trace may be empty if the clause contradicts itself
    if conflict_trace:
        exceptionstring += l10n("contradicts") + "\n"

        for index, clause in enumerate(conflict_trace):
            exceptionstring += index * "  " + f"{clause}\n"

    raise DepError(l10n("unable-to-satisfy-dependencies") + f"\n{exceptionstring}")
