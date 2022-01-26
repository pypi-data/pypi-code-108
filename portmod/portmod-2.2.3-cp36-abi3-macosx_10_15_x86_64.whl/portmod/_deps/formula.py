# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

from collections import defaultdict
from logging import warning
from types import SimpleNamespace
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set, Tuple, Union

from pysat.formula import WCNFPlus

from portmod.config.mask import get_masked, get_unmasked
from portmod.config.use import get_forced_use
from portmod.loader import load_pkg, load_pkg_fq
from portmod.pybuild import Pybuild
from portmodlib.atom import Atom, FQAtom, QualifiedAtom, atom_sat
from portmodlib.colour import blue, green
from portmodlib.usestr import human_readable_required_use, parse_usestr

from .tokens import (
    AtomToken,
    FlagToken,
    Token,
    VariableToken,
    expand_use_conditionals,
    token_conflicts,
)


class Target(SimpleNamespace):
    def __init__(self, pkgs: List[Pybuild], atom: Atom, source: Optional[str]):
        self.pkgs = pkgs
        self.atom = atom
        self.source = source


class Formula:
    """
    Intermediate representation of the integer WCNFPlus SAT formula accepted by pysat

    All flags are disabled by prepending a "-"

    Atom requirements are represented by the fully qualified atom,
    as produced by mod.ATOM

    Use flag requirements are represented by the fully qualified atom
    of the mod they apply to, followed by [flag]

    Custom variables are prefixed by an underscore and are
    used only for the calculation and ignored in the output
    """

    __i = 1  # Integer counter, for the numerical equivalent of tokens
    __j = 1  # Variable name counter.
    __numcache: Dict[Token, int] = {}  # Strings are
    __stringcache: Dict[int, Token] = {}
    __variabledesc: Dict[Token, str] = {}

    class Clause:
        """Generic clause type"""

        def __init__(self, clause: Iterable[Token], source):
            self.requirements: Set[Token] = set()
            self.clause = clause
            self.intclause: Optional[Iterable[int]] = None
            self.source = source

        def str2num(self):
            """
            Converts the tokens in the clause to integers for use with pysat
            """
            self.intclause = list(map(Formula.getnum, self.clause))
            return self

        def sourceatom(self) -> Optional[Atom]:
            return None

        def colourless(self) -> str:
            ...

        def blocks(self, model: Set[Token], clause: "Formula.Clause") -> bool:
            return False

    class MetaClause(Clause):
        def __init__(
            self,
            source: Optional[str],
            desc: Optional[str],
            clause: Iterable[Token],
            weight: Optional[int],
            atmost: Optional[int],
        ):
            self.source = source
            self.desc = desc
            self.clause = clause
            self.weight = weight
            self.atmost = atmost
            self.requirements: Set[Token] = set()

        def __str__(self):
            return f"{self.source} - {self.desc}"

        def sourceatom(self) -> Optional[Atom]:
            if isinstance(self.source, Atom):
                return self.source
            return None

    class DepClause(Clause):
        def __init__(self, source: str, clause: Iterable[Token], dependency: Atom):
            super().__init__(clause, source)
            self.dependency = dependency

        def __str__(self):
            return f"{green(self.dependency)}: required by {green(self.source)}"

        def colourless(self):
            return f"{self.dependency}: required by {self.source}"

        def blocks(self, model: Set[Token], clause: "Formula.Clause") -> bool:
            if isinstance(clause, Formula.BlockerClause):
                if atom_sat(self.dependency, clause.blocked) and all(
                    req in model for req in self.requirements
                ):
                    return True

            return False

        def sourceatom(self) -> Optional[Atom]:
            if isinstance(self.source, Atom):
                return self.source
            return None

    class BlockerClause(Clause):
        def __init__(self, source: str, clause: Iterable[Token], blocked: Atom):
            super().__init__(clause, source)
            self.blocked = blocked

        def __str__(self):
            return f"{green(self.blocked)}: blocked by {green(self.source)}"

        def colourless(self):
            return f"{self.blocked}: blocked by {self.source}"

        def blocks(self, model: Set[Token], clause: "Formula.Clause") -> bool:
            if isinstance(clause, Formula.DepClause):
                if atom_sat(self.blocked, clause.dependency) and all(
                    req in model for req in self.requirements
                ):
                    return True

            return False

        def sourceatom(self) -> Optional[Atom]:
            if isinstance(self.source, Atom):
                return self.source
            return None

    class UseDepClause(Clause):
        def __init__(
            self, source: str, clause: Iterable[Token], depatom: Atom, flag: FlagToken
        ):
            super().__init__(clause, source)
            self.depatom = depatom
            self.flag = flag

        def __str__(self):
            return (
                f"{green(self.depatom)}[{self.flag}]: required by {green(self.source)}"
            )

        def colourless(self):
            return f"{self.depatom}[{self.flag}]: required by {self.source}"

        def blocks(self, model: Set[Token], clause: "Formula.Clause") -> bool:
            if isinstance(clause, Formula.UseDepClause):
                if (
                    atom_sat(self.depatom, clause.depatom)
                    and token_conflicts(self.flag, clause.flag)
                    and all(req in model for req in self.requirements)
                ):
                    return True
            elif isinstance(clause, Formula.RequiredUseClause):
                if (
                    atom_sat(clause.atom, self.depatom)
                    and token_conflicts(self.flag, clause.flag)
                    and all(req in model for req in self.requirements)
                ):
                    return True

            return False

    class RequiredUseClause(Clause):
        def __init__(
            self,
            atom: Atom,
            clause: Iterable[Token],
            flag: Token,
            tokens: List[Union[str, List]],
        ):
            super().__init__(clause, atom)
            self.atom = atom
            self.flag = flag
            self.tokens = tokens

        def _get_required_use_str(self) -> Tuple[str, str]:
            if isinstance(self.flag, VariableToken):  # If flag is a generated variable
                string = Formula.get_variable_desc(self.flag)
            elif isinstance(self.flag, FlagToken):
                if self.flag.polarity:
                    string = list(self.flag.value.USE)[0]
                else:
                    string = "-" + list(self.flag.value.USE)[0]
            else:
                raise Exception(
                    f"AtomToken {self.flag} passed as the flag to RequiredUseClause!"
                )
            parent = human_readable_required_use(self.tokens)
            return string, parent

        def __str__(self):
            string, parent = self._get_required_use_str()
            # FIXME: Localize
            if string == parent:
                return f"{green(self.atom)} could not satisfy {blue(string)}"
            else:
                return (
                    f"{green(self.atom)} could not satisfy {blue(string)}, which is part of "
                    f"the larger clause {blue(parent)}"
                )

        def colourless(self):
            string, parent = self._get_required_use_str()
            if string == parent:
                return f"{self.atom} could not satisfy {string}"
            else:
                return (
                    f"{self.atom} could not satisfy {string}, which is part of "
                    f"the larger clause {parent}"
                )

        def blocks(self, model: Set[Token], clause: "Formula.Clause") -> bool:
            if isinstance(clause, Formula.UseDepClause):
                if (
                    atom_sat(self.atom, clause.depatom)
                    and token_conflicts(self.flag, clause.flag)
                    and all(req in model for req in self.requirements)
                ):
                    return True
            elif isinstance(clause, Formula.RequiredUseClause):
                if (
                    atom_sat(self.atom, clause.atom)
                    and token_conflicts(self.flag, clause.flag)
                    and all(req in model for req in self.requirements)
                ):
                    return True

            return False

        def sourceatom(self) -> Optional[Atom]:
            return self.atom

    def __init__(self):
        self.clauses = []
        self.atoms: Dict[QualifiedAtom, Set[FQAtom]] = defaultdict(set)
        self.flags: Set[FQAtom] = set()

    @classmethod
    def getnum(cls, token: Token) -> int:
        if token in cls.__numcache:
            return cls.__numcache[token]

        if token.polarity:
            cls.__numcache[token] = cls.__i
            cls.__numcache[token.neg()] = -cls.__i
            cls.__stringcache[cls.__i] = token
            cls.__stringcache[-cls.__i] = token.neg()
        else:
            cls.__numcache[token] = -cls.__i
            cls.__numcache[token.neg()] = cls.__i
            cls.__stringcache[-cls.__i] = token
            cls.__stringcache[cls.__i] = token.neg()

        cls.__i += 1
        return cls.__numcache[token]

    @classmethod
    def getstring(cls, num: int) -> Token:
        return cls.__stringcache[num]

    @classmethod
    def genvariable(cls, desc: List[Any]) -> Token:
        var = VariableToken("__" + str(cls.__j))
        cls.__j += 1
        cls.__variabledesc[var] = human_readable_required_use(desc)
        return var

    @classmethod
    def get_variable_desc(cls, var: Token) -> str:
        return cls.__variabledesc[var]

    def merge(self, other: "Formula"):
        self.clauses.extend(other.clauses)
        self.flags |= other.flags
        for atom, values in other.atoms.items():
            self.atoms[atom] |= values
        return self

    def get_wcnfplus(self) -> WCNFPlus:
        formula = WCNFPlus()
        for clause in self.clauses:
            if isinstance(clause, Formula.MetaClause) and clause.weight is not None:
                formula.append(clause.intclause, weight=clause.weight)
            elif isinstance(clause, Formula.MetaClause) and clause.atmost is not None:
                formula.append([clause.intclause, clause.atmost], is_atmost=True)
            else:
                formula.append(clause.intclause)
        return formula

    def append(
        self,
        clause: Iterable[Token],
        from_atom: Optional[str] = None,
        desc: Optional[str] = None,
        weight=None,
        atmost=None,
    ):
        self.clauses.append(Formula.MetaClause(from_atom, desc, clause, weight, atmost))
        self.__update_for_clause__(clause)

    def append_dep(self, clause: Iterable[Token], from_atom: str, dependency: Atom):
        self.clauses.append(Formula.DepClause(from_atom, clause, dependency))
        self.__update_for_clause__(clause)

    def append_blocker(self, clause: Iterable[Token], from_atom: str, blocked: Atom):
        self.clauses.append(Formula.BlockerClause(from_atom, clause, blocked))
        self.__update_for_clause__(clause)

    def append_required_use(
        self,
        clause: Iterable[Token],
        from_atom: Atom,
        flag: Token,
        tokens: List[Union[str, List]],
    ):
        self.clauses.append(Formula.RequiredUseClause(from_atom, clause, flag, tokens))
        self.__update_for_clause__(clause)

    def append_usedep(
        self, clause: Iterable[Token], from_atom: str, dep_atom: Atom, flag: FlagToken
    ):
        self.clauses.append(Formula.UseDepClause(from_atom, clause, dep_atom, flag))
        self.__update_for_clause__(clause)

    def __update_for_clause__(self, clause: Iterable[Token]):
        for token in clause:
            if not isinstance(token, VariableToken):
                if isinstance(token, FlagToken):
                    self.flags.add(token.value)
                elif isinstance(token, AtomToken):
                    self.atoms[QualifiedAtom(token.value.CPN)].add(token.value)

    def extend(
        self,
        from_atom: Atom,
        clauses: List[List[Token]],
        desc: Optional[str] = None,
        weight=None,
        atmost=None,
    ):
        for clause in clauses:
            self.append(clause, from_atom, desc, weight, atmost)

    def add_constraints(self, constraints: List[Token]):
        self.__update_for_clause__(constraints)
        for clause in self.clauses:
            if not (
                isinstance(clause, Formula.MetaClause) and clause.atmost is not None
            ):
                clause.clause = list(clause.clause) + constraints
                clause.requirements |= {token.neg() for token in constraints}

    def make_numeric(self):
        for clause in self.clauses:
            clause.str2num()


def get_atmost_one_formulae(tokens: Sequence[Token]) -> List[List[Token]]:
    """
    Returns a list of clauses that enforce that at most one of the tokens may be true

    Note that this can also be achieved by using Formula.append with atmost set to 1,
    however  this does not provide a mechanism for handling additional conditions.
    Instead, you can use this function, and add the condition to each clause it produces
    """
    if len(tokens) <= 1:
        return []

    result = []
    # Enforce that for any two tokens in the list, one must be false
    for token in tokens[1:]:
        # Invert value of firsttoken
        firsttoken = tokens[0].neg()

        # Invert value of the other token
        othertoken = token.neg()
        result.append([firsttoken, othertoken])

    return result + get_atmost_one_formulae(tokens[1:])


def toggle_clause(tokens: List[Token]) -> List[Token]:
    newtokens = []
    for token in tokens:
        newtokens.append(token.neg())
    return newtokens


def get_required_use_formula(
    mod: Pybuild, tokens: List[Union[str, List]], use_expand: Optional[str] = None
) -> Formula:
    """
    Adds clauses to the given formula for the given mod's REQUIRED_USE

    :param tokens: List of tokens corresponding to the REQUIRED_USE string, parsed
            beforehand by parse_usestr to be a list of tokens, with sublists
            corresponding to brackets in the original string
    """

    def get_required_use_formula_inner(
        tokens: List[Union[str, List]]
    ) -> Tuple[Formula, List[Token]]:
        formula = Formula()
        clausevars = []

        for token in tokens:
            if isinstance(token, list):
                if token[0] != "??" and token[0].endswith("?"):
                    newvar = Formula.genvariable([token])
                    subformulae, subvars = get_required_use_formula_inner(token[1:])
                    usedep = cond_flagstr(mod.ATOM, token[0].rstrip("?")).neg()
                    subformulae.add_constraints([usedep, newvar.neg()])
                    # for clause in get_atmost_one_formulae(subvars):
                    #    formula.append_required_use(
                    #        ["-" + newvar] + clause, mod.ATOM, token
                    #    )
                    formula.merge(subformulae)
                    # Generated variable is added to clausevars, and is free if
                    # condition is unsatisfied, and matches subformulae if condition
                    # is satisfied
                    clausevars.append(newvar)
                else:
                    subformulae, subvars = get_required_use_formula_inner(token[1:])
                    newvar = Formula.genvariable([token])
                    # Note: newvar will only have the value False if the formula
                    # is satisfied
                    if token[0] in ("??", "^^"):
                        for clause in get_atmost_one_formulae(subvars):
                            formula.append(
                                [newvar.neg()] + clause,
                                mod.ATOM,
                                human_readable_required_use(tokens),
                            )
                    if token[0] in ("||", "^^"):
                        formula.append(
                            [newvar.neg()] + subvars,
                            mod.ATOM,
                            human_readable_required_use(tokens),
                        )
                    if token[0] in ("||", "^^", "??"):
                        # If clause is satisfied, and the operator is not AND,
                        # then the subclauses don't need to be all satisfied
                        subformulae.add_constraints([newvar])
                    formula.merge(subformulae)
                    clausevars.append(newvar)

            else:
                flag = token.lstrip("!")
                if use_expand:
                    flag = use_expand + "_" + flag
                var = fstr(mod.ATOM, flag)
                if token.startswith("!"):
                    var = var.neg()

                formula.append_required_use([var], mod.ATOM, var, tokens)
                clausevars.append(var)
        return formula, clausevars

    formula, clausevars = get_required_use_formula_inner(tokens)
    # Top level is an and, so require that all returned variables are satisfied
    for var in clausevars:
        formula.append_required_use([var], mod.ATOM, var, tokens)
    return formula


def fstr(atom: FQAtom, flag: str) -> FlagToken:
    """
    Produces a flag token for the formula given an atom and a flag

    This function does not produce disabled tokens. If a disabled token is
    desired, the result should be negated.
    """
    assert flag[0] not in ("-", "!") and flag[-1] not in ("?", "=")
    return FlagToken(atom.use(flag))


def cond_flagstr(atom: FQAtom, flag: str, negtoken: str = "!") -> FlagToken:
    """
    Given an atom and a flag from a use conditional,
    produces a token for use in the dependency formula
    """
    disabled = flag.startswith(negtoken)
    flag = flag.lstrip(negtoken)
    if disabled:
        return fstr(atom, flag).neg()
    return fstr(atom, flag)


def get_dep_formula(mod: Pybuild, tokens) -> Tuple[Formula, Set[FQAtom]]:
    """
    Adds clauses to the given formula for the dependency strings of the given mod

    :param tokens: List of tokens corresponding to the dependency string, parsed
            beforehand by parse_usestr to be a list of tokens, with sublists
            corresponding to brackets in the original string
    """

    formula = Formula()
    deps: Set[FQAtom] = set()

    for token in expand_use_conditionals(tokens):
        if isinstance(token, list):
            if token[0] == "||":
                # If token is an or, next token is a list, at least one of the elements of
                # which must be satisfied
                orvars = []

                # Create clause for each part of the || expression.
                for subclause in token[1:]:
                    # Create new variable to represent clause
                    var = Formula.genvariable([token])
                    orvars.append(var)
                    # Either one part of the or must be true, or the variable for
                    # the clause should be false
                    new_formula, new_deps = get_dep_formula(mod, [subclause])
                    new_formula.add_constraints([var.neg()])
                    formula.merge(new_formula)
                    deps |= new_deps

                # We should be able to set at least one of the new variables we
                # introduced to be true, meaning that some other part of their clause
                # must be satisfied
                formula.append(orvars, mod.ATOM, human_readable_required_use([token]))
            elif token[0].endswith("?"):
                new_formula, new_deps = get_dep_formula(mod, token[1:])

                # Note: If flag was disabled, we want the flag enabled in the clause, as it
                # should either be enabled,
                # or some other part of the clause must be true if disabled
                # If flag was enabled, we produce the clause (flag => dep),
                # which is equivalent to (-flag | dep)
                new_formula.add_constraints(
                    [cond_flagstr(mod.ATOM, token[0].rstrip("?")).neg()]
                )
                formula.merge(new_formula)
                deps |= new_deps
            else:
                raise Exception(
                    f"Internal Error: dependency structure {tokens} is invalid"
                )
        # Handle regular dependencies
        else:
            blocker = token.startswith("!!")
            atom = Atom(token.lstrip("!"))

            # Note that load_pkg will only return mods that completely match atom
            # I.e. it will handle any versioned atoms itself
            specificpkgs = load_pkg(atom)
            specificatoms = [m.ATOM for m in load_pkg(atom)]

            if not blocker:
                deps |= set(specificatoms)

            # !!foo[A,B] is equivalent to
            # || ( !!foo foo[-A] foo[-B] )
            # What about !!foo[A?,B]
            # A? ( || ( !!foo foo[-A] foo[-B] ) || ( !!foo foo[-B] ) )

            # At least one specific version of this mod must be enabled
            if blocker and not atom.USE:
                for specatom in specificatoms:
                    formula.append_blocker(
                        [AtomToken(specatom, polarity=False)],
                        mod.ATOM,
                        Atom(token.lstrip("!")),
                    )
            elif not blocker:
                formula.append_dep(
                    [AtomToken(atom) for atom in specificatoms], mod.ATOM, atom
                )

            # For each use flag dependency, add a requirement that the flag must be set
            # This depends on the operators used on the flag. See PMS 8.2.6.4
            for flag in atom.USE:
                for spec in specificpkgs:
                    # Either specific version should not be installed,
                    # or flag must be set (depending on flag operators)

                    # Use requirement is unnecessary unless this specific version
                    # of the mod is enabled
                    new_formula = Formula()
                    if flag.lstrip("-") not in spec.IUSE_EFFECTIVE:
                        continue

                    # 2-style
                    if blocker:
                        flagdep = cond_flagstr(spec.ATOM, flag, negtoken="-").neg()
                        new_formula.append_usedep(
                            [flagdep],
                            mod.ATOM,
                            atom.strip_use(),
                            flagdep,
                        )
                    else:
                        flagdep = cond_flagstr(spec.ATOM, flag, negtoken="-")
                        new_formula.append_usedep(
                            [flagdep],
                            mod.ATOM,
                            atom.strip_use(),
                            flagdep,
                        )

                    new_formula.add_constraints([AtomToken(spec.ATOM, polarity=False)])
                    formula.merge(new_formula)
    return formula, deps


def generate_formula(
    mods: Iterable[Target], depsadded: Set[FQAtom], deep: bool
) -> Formula:
    """
    Generates a hard dependency formula for the given mods

    :param mods: Each entry should contain a list of mods with the same base
                 category and name, the atom that pulled those mods in, and a
                 string describing where the mods were pulled from.
    :param depsadded: Mods that have already been included in the formula and
                      should not be added again
    :returns: The resulting formula
    """
    formula = Formula()
    # Queue of mods to add to the formula
    new: List[Pybuild] = []
    # Ensure newselected and oldselected mods are satisfied
    for target in mods:
        if target.source:
            # If a source is specified, at least one version of the mod must be
            # installed
            # Otherwise, we only include it for the purpose of dependency resolution
            formula.append_dep(
                [AtomToken(mod.ATOM) for mod in target.pkgs], target.source, target.atom
            )
            if target.atom.USE:
                for flag in target.atom.USE:
                    for mod in target.pkgs:
                        flagdep = cond_flagstr(mod.ATOM, flag, negtoken="-")
                        formula.append_usedep(
                            [
                                AtomToken(mod.ATOM, polarity=False),
                                flagdep,
                            ],
                            target.source,
                            target.atom.strip_use(),
                            flagdep,
                        )

        new += target.pkgs

    while new:
        # Mods to parse in next iteration, mapped to the mod that depends on them
        nextmods: Set[FQAtom] = set()
        for mod in new:
            # Either mod must not be installed, or mods dependencies must be satisfied
            new_formula, deps = get_dep_formula(
                mod, parse_usestr(mod.DEPEND + " " + mod.RDEPEND, token_class=Atom)
            )
            new_formula.merge(
                get_required_use_formula(mod, parse_usestr(mod.REQUIRED_USE))
            )
            # Exactly one texture_size flag must be enabled
            if mod.TEXTURE_SIZES.strip():
                new_formula.merge(
                    get_required_use_formula(
                        mod,
                        [["^^"] + parse_usestr(mod.TEXTURE_SIZES)],
                        use_expand="texture_size",
                    )
                )
            new_formula.add_constraints([AtomToken(mod.ATOM, polarity=False)])
            formula.merge(new_formula)
            for flag in get_forced_use(mod.ATOM):
                if flag.lstrip("-") not in mod.IUSE_EFFECTIVE:
                    continue

                formula.append(
                    [cond_flagstr(mod.ATOM, flag, negtoken="-")],
                    "profile use.force or mod.use.force",
                    f"Flag {flag} is forced on mod {mod.ATOM}",
                )

            depsadded.add(mod.ATOM)
            if deep:
                # Add this mod's dependencies to the next set of mods to parse
                nextmods |= deps

        new = []
        for atom in nextmods:
            if atom not in depsadded:
                new.append(load_pkg_fq(atom))

    return formula


def is_unmasked(atom: FQAtom) -> bool:
    for unmasked_atom in get_unmasked().get(atom.CPN, []):
        if atom_sat(atom, unmasked_atom):
            return True
    return False


def add_masked(atoms: Dict[QualifiedAtom, Set[FQAtom]], flags: Iterable[FQAtom]):
    formula = Formula()
    masked = get_masked()
    for cpn in atoms:
        if cpn in masked:
            for atom in atoms[cpn]:
                for masked_atom, comment in masked[cpn].items():
                    if atom_sat(atom, masked_atom) and not is_unmasked(atom):
                        if comment:
                            description = (
                                "package.mask with the following comment:\n  "
                                + blue("\n  ".join(comment))
                            )
                        else:
                            description = "package.mask"
                        # Masks don't apply to installed packages
                        # (i.e. the user should remove them manually)
                        if atom.R.endswith("::installed"):
                            warning(
                                f"Installed package {atom.CPF} is masked by {description}"
                            )
                        else:
                            formula.append_blocker(
                                [AtomToken(atom, polarity=False)],
                                description,
                                masked_atom,
                            )

    return formula
