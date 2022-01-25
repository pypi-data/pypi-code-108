# Copyright 2019 Ingmar Dasseville, Pierre Carbonnelle
#
# This file is part of Interactive_Consultant.
#
# This program is free software: you can redistribute it and/or modify
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
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
This module contains the logic for the computation of relevance.
"""

from idp_engine.Assignments import Status as S
from idp_engine.Expression import (AppliedSymbol, TRUE, Expression, AQuantification,
                                   AConjunction, Brackets, UnappliedSymbol)
from idp_engine.Problem import Theory
from idp_engine.utils import OrderedSet, GOAL_SYMBOL, RELEVANT


def split_constraints(constraints: OrderedSet) -> OrderedSet:
    """replace [.., a ∧ b, ..] by [.., a, b, ..]

    This is to avoid dependencies between a and b (see issue #95).

    Args:
        constraints (OrderedSet): set of constraints that may contain conjunctions

    Returns:
        OrderedSet: set of constraints without top-level conjunctions
    """

    def split(c: Expression, cs: OrderedSet):
        """split constraint c and adds it to cs"""
        if type(c) in [AConjunction, Brackets]:
            for e in c.sub_exprs:
                split(e, cs)
        elif type(c) == AQuantification and c.q == '∀':
            assert len(c.sub_exprs) == 1, "Internal error in split"
            conj = OrderedSet()
            if c.simpler:
                split(c.simpler, conj)
            else:
                split(c.sub_exprs[0], conj)
            for e in conj:
                out = AQuantification.make(c.q, c.quantees, e)
                # out.code = c.code
                out.annotations = c.annotations
                cs.append(out)
        else:
            cs.append(c)

    new_constraints = OrderedSet()
    for c in constraints:
        split(c, new_constraints)
    return new_constraints


def determine_relevance(self: Theory) -> Theory:
    """Determines the questions that are relevant in a model,
    or that can appear in a justification of a ``goal_symbol``.

    When an *irrelevant* value is changed in a model M of the theory,
    the resulting M' structure is still a model.
    Relevant questions are those that are not irrelevant.

    Call must be made after a propagation, on a Theory created with ``extended=True``.
    The result is found in the ``relevant`` attribute of the assignments in ``self.assignments``.

    If ``goal_symbol`` has an enumeration in the theory
    (e.g., ``goal_symbol := {`tax_amount}``),
    relevance is computed relative to those goals.

    Definitions in the theory are ignored,
    unless they influence axioms in the theory or goals in ``goal_symbol``.

    Returns:
        Theory: the Theory with relevant information in ``self.assignments``.
    """
    assert self.extended == True,\
        "The theory must be created with 'extended=True' for relevance computations."

    for a in self.assignments.values():
        a.relevant = False

    out = self.simplify()  # creates a copy

    # analyse given information
    given = OrderedSet()
    for q in out.assignments.values():
        q.relevant = False
        if q.status in [S.GIVEN, S.DEFAULT, S.EXPANDED]:
            if not q.sentence.has_decision():
                given.append(q.sentence)

    # collect (co-)constraints
    constraints = OrderedSet()
    for constraint in out.constraints:
        if constraint.code not in self.ignored_laws:
            constraints.append(constraint)
            constraint.co_constraints(constraints)
    constraints = split_constraints(constraints)

    # constraints have set of questions in out.assignments
    # set constraint.relevant, constraint.questions
    # initialize reachable with relevant, if any
    reachable = OrderedSet()
    for constraint in constraints:
        constraint.relevant = False
        constraint.questions = OrderedSet()
        constraint.collect(constraint.questions,
                           all_=True, co_constraints=False)

        if (type(constraint) == AppliedSymbol
           and constraint.decl.name == RELEVANT):
            reachable.append(constraint.sub_exprs[0])

    # nothing relevant --> make every question in a simplified constraint relevant
    if len(reachable) == 0:
        for constraint in constraints:
            if constraint.is_type_constraint_for is None:
                for q in constraint.questions:
                    reachable.append(q)

    # still nothing relevant --> make every question in def_constraints relevant
    if len(reachable) == 0:
        for def_constraints in out.def_constraints.values():
            for def_constraint in def_constraints:
                def_constraint.questions = OrderedSet()
                def_constraint.collect(def_constraint.questions,
                                    all_=True, co_constraints=True)
                for q in def_constraint.questions:
                    reachable.append(q)

    # find relevant symbols by breadth-first propagation
    # input: reachable, given, constraints
    # output: out.assignments[].relevant, constraints[].relevant, relevants[].rank
    relevants = {}  # Dict[string: int]
    to_add, rank = reachable, 1
    while to_add:
        for q in to_add:
            if q.code in self.assignments:
                self.assignments[q.code].relevant = True
            # for s in q.collect_symbols(co_constraints=False):
            #     if s not in relevants:
            #         relevants[s] = rank
            if q not in given:
                reachable.append(q)

        to_add, rank = OrderedSet(), 2  # or rank+1
        for constraint in constraints:
            # consider constraint not yet considered
            if (not constraint.relevant
                # and with a question that is reachable but not given
                and any(q in reachable and q not in given
                        for q in constraint.questions)):
                constraint.relevant = True
                to_add.extend([q for q in constraint.questions
                               if q not in reachable])

    return self
Theory.determine_relevance = determine_relevance


Done = True