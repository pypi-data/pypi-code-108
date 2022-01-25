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

The following Python functions can be used to perform computations
using FO-dot knowledge bases:

"""

import time
import types
from typing import Any, Iterator, List, Union
from z3 import Solver

from .Parse import IDP, TheoryBlock, Structure
from .Problem import Theory
from .Assignments import Status as S, Assignments
from .utils import NEWL

last_call = time.process_time()  # define it as global

def model_check(*theories: Union[TheoryBlock, Structure, Theory]) -> str:
    """Returns a string stating whether the combination of theories is satisfiable.

    For example, ``print(model_check(T, S))`` will print ``sat`` if theory named ``T`` has a model expanding structure named ``S``.

    Args:
        theories (Union[TheoryBlock, Structure, Theory]): 1 or more (data) theories.

    Returns:
        str: ``sat``, ``unsat`` or ``unknown``
    """

    problem = Theory(*theories)
    z3_formula = problem.formula()

    solver = Solver(ctx=problem.ctx)
    solver.add(z3_formula)
    return str(solver.check())


def model_expand(*theories: Union[TheoryBlock, Structure, Theory],
                 max: int = 10,
                 timeout: int = 10,
                 complete: bool = False,
                 extended: bool = False,
                 sort: bool = False
                 ) -> Iterator[str]:
    """Returns a (possibly empty) list of models of the combination of theories,
    followed by a string message.

    For example, ``print(model_expand(T, S))`` will return (up to) 10
    string representations of models of theory named ``T``
    expanding structure named ``S``.

    The string message can be one of the following:

    - ``No models.``

    - ``More models may be available.  Change the max argument to see them.``

    - ``More models may be available.  Change the timeout argument to see them.``

    - ``More models may be available.  Change the max and timeout arguments to see them.``

    Args:
        theories (Union[TheoryBlock, Structure, Theory]): 1 or more (data) theories.
        max (int, optional): max number of models. Defaults to 10.
        timeout (int, optional): timeout in seconds. Defaults to 10.
        complete (bool, optional): True to obtain complete structures. Defaults to False.
        extended (bool, optional): use `True` when the truth value of
                inequalities and quantified formula is of interest
                (e.g. for the Interactive Consultant). Defaults to False.
        sort (bool, optional): True if the models should be in alphabetical order. Defaults to False.

    Yields:
        str
    """
    problem = Theory(*theories, extended=extended)
    ms = list(problem.expand(max=max, timeout=timeout, complete=complete))
    if isinstance(ms[-1], str):
        ms, last = ms[:-1], ms[-1]
    else:
        last = ""
    if sort:
        ms = sorted([str(m) for m in ms])
    out = ""
    for i, m in enumerate(ms):
        out = out + (f"{NEWL}Model {i+1}{NEWL}==========\n{m}\n")
    yield out + last


def model_propagate(*theories: Union[TheoryBlock, Structure, Theory],
                    sort: bool = False
                    ) -> Iterator[str]:
    """
    Returns a list of assignments that are true in any model of the combination of theories.

    Terms and symbols starting with '_' are ignored.

    For example, ``print(model_propagate(T, S))`` will return the assignments
    that are true in any expansion of the structure named ``S``
    consistent with the theory named ``T``.

    Args:
        theories (Union[TheoryBlock, Structure, Theory]): 1 or more (data) theories.
        sort (bool, optional): True if the assignments should be in alphabetical order. Defaults to False.

    Yields:
        str
    """
    problem = Theory(*theories)
    if sort:
        ms = [str(m) for m in problem._propagate(tag=S.CONSEQUENCE)]
        ms = sorted(ms[:-1]) + [ms[-1]]
        out = ""
        for i, m in enumerate(ms[:-1]):
            out = out + (f"{NEWL}Model {i+1}{NEWL}==========\n{m}\n")
        yield out + f"{ms[-1]}"
    else:
        yield from problem._propagate(tag=S.CONSEQUENCE)


def decision_table(*theories: Union[TheoryBlock, Structure, Theory],
                   goal_string: str = "",
                   timeout: int = 20,
                   max_rows: int = 50,
                   first_hit: bool = True,
                   verify: bool = False
                   ) -> Iterator[str]:
    """Experimental. Returns a decision table for `goal_string`, given the combination of theories.

    Args:
        theories (Union[TheoryBlock, Structure, Theory]): 1 or more (data) theories.
        goal_string (str, optional): the last column of the table.
            Must be a predicate application defined in the theory, e.g. ``eligible()``.
        timeout (int, optional): maximum duration in seconds. Defaults to 20.
        max_rows (int, optional): maximum number of rows. Defaults to 50.
        first_hit (bool, optional): requested hit-policy. Defaults to True.
        verify (bool, optional): request verification of table completeness.  Defaults to False

    Yields:
        a textual representation of each rule
    """
    problem = Theory(*theories, extended=True)
    for model in problem.decision_table(goal_string, timeout, max_rows,
                                        first_hit, verify):
        row = f'{NEWL}∧ '.join(str(a) for a in model
            if a.sentence.code != goal_string)
        has_goal = model[-1].sentence.code == goal_string
        yield((f"{(f'  {row}{NEWL}') if row else ''}"
              f"⇒ {str(model[-1]) if has_goal else '?'}"))
        yield("")
    yield "end of decision table"

def determine_relevance(*theories: Union[TheoryBlock, Structure, Theory]) -> Iterator[str]:
    """Generates a list of questions that are relevant,
    or that can appear in a justification of a ``goal_symbol``.

    The questions are preceded with `` ? `` when their answer is unknown.

    When an *irrelevant* value is changed in a model M of the theories,
    the resulting M' structure is still a model.
    Relevant questions are those that are not irrelevant.

    If ``goal_symbol`` has an enumeration in the theory
    (e.g., ``goal_symbol := {`tax_amount}``),
    relevance is computed relative to those goals.

    Definitions in the theory are ignored,
    unless they influence axioms in the theory or goals in ``goal_symbol``.

    Yields:
        relevant questions
    """
    problem = Theory(*theories, extended=True).propagate()
    problem.determine_relevance()
    for ass in problem.assignments.values():
        if ass.relevant:
            yield str(ass)


def pretty_print(x: Any ="") -> None:
    """Prints its argument on stdout, in a readable form.

    Args:
        x (Any, optional): the result of an API call. Defaults to "".
    """
    if type(x) is tuple and len(x)==2: # result of Theory.explain()
        facts, laws = x
        for f in facts:
            print(str(f))
        for l in laws:
            print(l.annotations['reading'])
    elif isinstance(x, types.GeneratorType):
        for i, xi in enumerate(x):
            if isinstance(xi, Assignments):
                print(f"{NEWL}Model {i+1}{NEWL}==========")
                print(xi)
            else:
                print(xi)
    elif isinstance(x, Theory):
        print(x.assignments)
    else:
        print(x)


def duration(msg: str = "") -> str:
    """Returns the processing time since the last call to `duration()`,
    or since the begining of execution"""
    global last_call
    out = round(time.process_time() - last_call, 3)
    last_call = time.process_time()
    return f"{out} {msg}"

def execute(self: IDP) -> None:
    """ Execute the ``main()`` procedure block in the IDP program """
    global last_call
    last_call = time.process_time()
    main = str(self.procedures['main'])
    mybuiltins = {}
    mylocals = {**self.vocabularies, **self.theories, **self.structures}
    mylocals['model_check'] = model_check
    mylocals['model_expand'] = model_expand
    mylocals['model_propagate'] = model_propagate
    mylocals['decision_table'] = decision_table
    mylocals['determine_relevance'] = determine_relevance
    mylocals['pretty_print'] = pretty_print
    mylocals['Theory'] = Theory
    mylocals['time'] = time
    mylocals['duration'] = duration

    exec(main, mybuiltins, mylocals)

IDP.execute = execute





Done = True
