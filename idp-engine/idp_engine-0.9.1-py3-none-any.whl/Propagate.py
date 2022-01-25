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

Computes the consequences of an expression,
i.e., the sub-expressions that are necessarily true (or false)
if the expression is true (or false)

It has 2 parts:
* symbolic propagation
* Z3 propagation

This module monkey-patches the Expression and Theory classes and sub-classes.
"""

import time
from copy import copy
from typing import List, Tuple, Optional
from z3 import (Solver, sat, unsat, unknown, Not, Or, is_false, is_true, is_not, is_eq)

from .Assignments import Status as S, Assignments
from .Expression import (Expression, AQuantification,
                    ADisjunction, AConjunction, AppliedSymbol,
                    AComparison, AUnary, Brackets, TRUE, FALSE)
from .Parse import str_to_IDP
from .Problem import Theory
from .utils import OrderedSet, IDPZ3Error, NOT_SATISFIABLE

start = time.process_time()

###############################################################################
#
#  Symbolic propagation
#
###############################################################################


def _not(truth):
    return FALSE if truth.same_as(TRUE) else TRUE


# class Expression ############################################################

def simplify_with(self: Expression, assignments: "Assignments") -> Expression:
    """ simplify the expression using the assignments """
    if self.value is not None:
        return self
    value, simpler, new_e, co_constraint = None, None, None, None
    if self.simpler is not None:
        simpler = self.simpler.simplify_with(assignments)
    if self.co_constraint is not None:
        co_constraint = self.co_constraint.simplify_with(assignments)
    new_e = [e.simplify_with(assignments) for e in self.sub_exprs]
    self._change(sub_exprs=new_e, simpler=simpler, co_constraint=co_constraint)
    # calculate ass.value on the changed expression, as simplified sub
    # expressions may lead to stronger simplifications
    # E.g., P(C()) where P := {0} and C := 0.
    ass = assignments.get(self.str, None)
    if ass and ass.value is not None:
        value = ass.value
        self._change(value=value)
    return self.simplify1()
Expression.simplify_with = simplify_with


def symbolic_propagate(self,
                       assignments: "Assignments",
                       tag: "Status",
                       truth: Optional[Expression] = TRUE
                       ):
    """updates assignments with the consequences of `self=truth`.

    The consequences are obtained by symbolic processing (no calls to Z3).

    Args:
        assignments (Assignments):
            The set of assignments to update.

        truth (Expression, optional):
            The truth value of the expression `self`. Defaults to TRUE.
    """
    if self.value is None:
        if self.code in assignments:
            assignments.assert__(self, truth, tag)
        if self.simpler is not None:
            self.simpler.symbolic_propagate(assignments, tag, truth)
        else:
            self.propagate1(assignments, tag, truth)
Expression.symbolic_propagate = symbolic_propagate


def propagate1(self, assignments, tag, truth):
    " returns the list of symbolic_propagate of self, ignoring value and simpler "
    return
Expression.propagate1 = propagate1


# class AQuantification  ######################################################

def symbolic_propagate(self, assignments, tag, truth=TRUE):
    if self.code in assignments:
        assignments.assert__(self, truth, tag)
    if not self.quantees:  # expanded
        assert len(self.sub_exprs) == 1,  \
               f"Internal error in symbolic_propagate: {self}"  # a conjunction or disjunction
        self.sub_exprs[0].symbolic_propagate(assignments, tag, truth)
AQuantification.symbolic_propagate = symbolic_propagate


# class ADisjunction  #########################################################

def propagate1(self, assignments, tag, truth=TRUE):
    if truth.same_as(FALSE):
        for e in self.sub_exprs:
            e.symbolic_propagate(assignments, tag, truth)
ADisjunction.propagate1 = propagate1


# class AConjunction  #########################################################

def propagate1(self, assignments, tag, truth=TRUE):
    if truth.same_as(TRUE):
        for e in self.sub_exprs:
            e.symbolic_propagate(assignments, tag, truth)
AConjunction.propagate1 = propagate1


# class AUnary  ############################################################

def propagate1(self, assignments, tag, truth=TRUE):
    if self.operator == '¬':
        self.sub_exprs[0].symbolic_propagate(assignments, tag, _not(truth))
AUnary.propagate1 = propagate1


# class AComparison  ##########################################################

def propagate1(self, assignments, tag, truth=TRUE):
    if truth.same_as(TRUE) and len(self.sub_exprs) == 2 and self.operator == ['=']:
        # generates both (x->0) and (x=0->True)
        # generating only one from universals would make the second one
        # a consequence, not a universal
        operands1 = [e.value for e in self.sub_exprs]
        if (type(self.sub_exprs[0]) == AppliedSymbol
        and operands1[1] is not None):
            assignments.assert__(self.sub_exprs[0], operands1[1], tag)
        elif (type(self.sub_exprs[1]) == AppliedSymbol
        and operands1[0] is not None):
            assignments.assert__(self.sub_exprs[1], operands1[0], tag)
AComparison.propagate1 = propagate1


# class Brackets  ############################################################

def symbolic_propagate(self, assignments, tag, truth=TRUE):
    self.sub_exprs[0].symbolic_propagate(assignments, tag, truth)
Brackets.symbolic_propagate = symbolic_propagate



###############################################################################
#
#  Z3 propagation
#
###############################################################################

def _set_consequences_get_changed_choices(self):
    # clear consequences, as these might not be cleared by add_given when
    # running via CLI
    for a in self.assignments.values():
        if a.status in [S.CONSEQUENCE, S.ENV_CONSQ]:
            self.assignments.assert__(a.sentence, None, S.UNKNOWN)

    removed_choices = {a.sentence.code: a for a in self.previous_assignments.values()
                       if a.status in [S.GIVEN, S.DEFAULT, S.EXPANDED]}
    added_choices = []

    for a in self.assignments.values():
        if a.status in [S.GIVEN, S.DEFAULT, S.EXPANDED]:
            if (a.sentence.code in removed_choices
                    and removed_choices[a.sentence.code].value.same_as(a.value)):
                removed_choices.pop(a.sentence.code)
            else:
                added_choices.append(a)

    if not removed_choices:
        for a in self.previous_assignments.values():
            if (a.status in [S.CONSEQUENCE, S.ENV_CONSQ] and
                    self.assignments[a.sentence.code].status
                    not in [S.GIVEN, S.EXPANDED, S.DEFAULT]):
                self.assignments.assert__(a.sentence, a.value, a.status)

    # TODO: why is it not ok to use get_core_atoms in this method?

    return removed_choices, added_choices
Theory._set_consequences_get_changed_choices = _set_consequences_get_changed_choices


def _directional_todo(self, removed_choices={}, added_choices=[]):
    """ computes the list of candidate atoms for a new propagation
    * if choices are removed, all previous consequences and removed choices
      should be checked for propagation
    * if choices are added, all unknown atoms should be checked
    """

    todo = {}
    if removed_choices:
        for a in removed_choices.values():
            todo[a.sentence.code] = a.sentence
        for a in self.previous_assignments.values():
            if a.status in [S.CONSEQUENCE, S.ENV_CONSQ]:
                todo[a.sentence.code] = a.sentence

    if added_choices:
        for a in self.get_core_atoms([S.UNKNOWN]):
            todo[a.sentence.code] = a.sentence

    return todo
Theory._directional_todo = _directional_todo


def _batch_propagate(self, tag=S.CONSEQUENCE):
    """ generator of new propagated assignments.  Update self.assignments too.

    uses the method outlined in https://stackoverflow.com/questions/37061360/using-maxsat-queries-in-z3/37061846#37061846
    and in J. Wittocx paper : https://drive.google.com/file/d/19LT64T9oMoFKyuoZ_MWKMKf9tJwGVax-/view?usp=sharing

    This method is not faster than _propagate(), and falls back to it in some cases
    """
    todo = self._directional_todo()
    if todo:
        z3_formula = self.formula()

        solver = Solver(ctx=self.ctx)
        solver.add(z3_formula)
        result = solver.check()
        if result == sat:
            lookup, tests = {}, []
            for q in todo:
                solver.add(q.reified(self) == q.translate(self))  # in case todo contains complex formula
                if solver.check() != sat:
                    # print("Falling back !")
                    yield from self._propagate(tag=tag)
                test = Not(q.reified(self) == solver.model().eval(q.reified(self)))  #TODO compute model once
                tests.append(test)
                lookup[str(test)] = q
            solver.push()
            while True:
                solver.add(Or(tests))
                result = solver.check()
                if result == sat:
                    tests = [t for t in tests if is_false(solver.model().eval(t))]  #TODO compute model once
                    for t in tests:  # reset the other assignments
                        if is_true(solver.model().eval(t)):  #TODO compute model once
                            q = lookup[str(test)]
                            self.assignments.assert__(q, None, S.UNKNOWN)
                elif result == unsat:
                    solver.pop()
                    solver.check()  # not sure why this is needed
                    for test in tests:
                        q = lookup[str(test)]
                        val1 = solver.model().eval(q.reified(self))  #TODO compute model once
                        val = str_to_IDP(q, str(val1))
                        yield self.assignments.assert__(q, val, tag)
                    break
                else:  # unknown
                    # print("Falling back !!")
                    yield from self._propagate(tag=tag)
                    break
            yield "No more consequences."
        elif result == unsat:
            yield NOT_SATISFIABLE
            yield str(z3_formula)
        else:
            yield "Unknown satisfiability."
            yield str(z3_formula)
    else:
        yield "No more consequences."
Theory._batch_propagate = _batch_propagate


def _propagate_inner(self, tag, solver, todo):
    for q in todo.values():
        solver.add(q.reified(self) == q.translate(self))
        # reification in case todo contains complex formula

    res1 = solver.check()

    if res1 == sat:
        model = solver.model()
        valqs = [(model.eval(q.reified(self)), q) for q in todo.values()]
        for val1, q in valqs:
            if str(val1) == str(q.reified(self)):
                continue  # irrelevant
            solver.push()
            solver.add(Not(q.reified(self) == val1))
            res2 = solver.check()
            solver.pop()

            assert res2 != unknown, "Incorrect solver behavior"
            if res2 == unsat:
                val = str_to_IDP(q, str(val1))
                yield self.assignments.assert__(q, val, tag)

        yield "No more consequences."
    elif res1 == unsat:
        yield NOT_SATISFIABLE
        yield str(solver.sexpr())
    else:
        assert False, "Incorrect solver behavior"

Theory._propagate_inner = _propagate_inner


def _first_propagate(self, solver):
    """ determine universals

        Raises:
            IDPZ3Error: if theory is unsatisfiable
    """
    # NOTE: some universal assignments may be set due to the environment theory
    todo = OrderedSet(a.sentence for a in self.get_core_atoms(
        [S.UNKNOWN, S.EXPANDED, S.DEFAULT, S.GIVEN, S.CONSEQUENCE, S.ENV_CONSQ]))

    solver.push()

    for q in todo:
        solver.add(q.reified(self) == q.translate(self))
        # reification in case todo contains complex formula

    res1 = solver.check()
    if res1 == unsat:
        solver.pop()
        raise IDPZ3Error(NOT_SATISFIABLE)

    assert res1 == sat, "Incorrect solver behavior"
    model = solver.model()
    valqs = [(model.eval(q.reified(self)), q) for q in todo]
    for val1, q in valqs:
        if str(val1) == str(q.reified(self)):
            continue  # irrelevant
        solver.push()
        solver.add(Not(q.reified(self) == val1))
        res2 = solver.check()
        solver.pop()

        assert res2 != unknown, "Incorrect solver behavior"
        if res2 == unsat:
            val = str_to_IDP(q, str(val1))

            ass = self.assignments.get(q.code)
            if (ass.status in [S.GIVEN, S.DEFAULT, S.EXPANDED] and
                    not ass.value.same_as(val)):
                solver.pop()
                raise IDPZ3Error(NOT_SATISFIABLE)
            yield self.assignments.assert__(q, val, S.UNIVERSAL)

    solver.pop()
Theory._first_propagate = _first_propagate


def _propagate_ignored(self, tag=S.CONSEQUENCE, given_todo=None):
    assert self.ignored_laws, "Internal error"

    solver = self.solver_reified
    solver.push()

    todo = (given_todo.copy() if given_todo else
            {a.sentence.code: a.sentence
            for a in self.assignments.values()
            if a.status not in [S.GIVEN, S.DEFAULT, S.EXPANDED] and
            (a.status != S.STRUCTURE or a.sentence.code in self.ignored_laws)})

    self._add_assignment_ignored(solver)

    yield from self._propagate_inner(tag, solver, todo)
    solver.pop()
Theory._propagate_ignored = _propagate_ignored


def _propagate(self, tag=S.CONSEQUENCE, given_todo=None):
    """generator of new propagated assignments.  Update self.assignments too.
    :arg given_todo: custom collection of assignments to check during propagation.
    given_todo is organized as a dictionary where the keys function to quickly
    check if a certain assignment is in the collection.
    """

    global start
    start = time.process_time()

    if self.ignored_laws:
        yield from self._propagate_ignored(tag, given_todo)
        return

    if not self.previous_assignments:
        try:
            yield from self._first_propagate(self.solver)
        except IDPZ3Error:
            yield NOT_SATISFIABLE
            # can't access solver.sexpr()

    removed_choices, added_choices = self._set_consequences_get_changed_choices()

    dir_todo = given_todo is None
    if dir_todo:
        todo = self._directional_todo(removed_choices, added_choices)
    else:
        todo = given_todo.copy()  # shallow copy needed because todo might be adjusted

    if not removed_choices and not added_choices:
        # nothing changed since the previous propagation
        to_remove = []
        for a in todo.values():
            if a.code in self.assignments:
                to_remove.append(a)
                if self.assignments[a.code].status in [S.CONSEQUENCE, S.ENV_CONSQ]:
                    yield self.assignments[a.code]
        for a in to_remove:
            todo.pop(a.code)

    if not todo:
        yield "No more consequences."
        return

    solver = self.solver
    solver.push()

    self._add_assignment(solver)

    yield from self._propagate_inner(tag, solver, todo)
    solver.pop()

    if dir_todo:
        self.previous_assignments = copy(self.assignments)
Theory._propagate = _propagate


def _z3_propagate(self, tag=S.CONSEQUENCE):
    """generator of new propagated assignments.  Update self.assignments too.

    use z3's consequences API (incomplete propagation)
    """
    todo = self._directional_todo()
    if todo:
        z3_todo, unreify = [], {}
        for q in todo:
            z3_todo.append(q.reified(self))
            unreify[q.reified(self)] = q

        z3_formula = self.formula()

        solver = Solver(ctx=self.ctx)
        solver.add(z3_formula)
        result, consqs = solver.consequences([], z3_todo)
        if result == sat:
            for consq in consqs:
                atom = consq.children()[1]
                if is_not(consq):
                    value, atom = FALSE, atom.arg(0)
                else:
                    value = TRUE
                # try to unreify it
                if atom in unreify:
                    yield self.assignments.assert__(unreify[atom], value, tag)
                elif is_eq(consq):
                    assert value == TRUE, f"Internal error in z3_propagate"
                    term = consq.children()[0]
                    if term in unreify:
                        q = unreify[term]
                        val = str_to_IDP(q, consq.children()[1])
                        yield self.assignments.assert__(q, val, tag)
                    else:
                        print("???", str(consq))
                else:
                    print("???", str(consq))
            yield "No more consequences."
            #yield from self._propagate(tag=tag)  # incomplete --> finish with normal propagation
        elif result == unsat:
            yield NOT_SATISFIABLE
            yield str(z3_formula)
        else:
            yield "Unknown satisfiability."
            yield str(z3_formula)
    else:
        yield "No more consequences."
Theory._z3_propagate = _z3_propagate


Done = True
