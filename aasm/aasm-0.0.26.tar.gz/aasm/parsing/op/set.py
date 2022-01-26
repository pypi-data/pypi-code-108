from __future__ import annotations

from typing import TYPE_CHECKING

from aasm.intermediate.argument import Argument
from aasm.intermediate.instruction import Set

if TYPE_CHECKING:
    from aasm.parsing.state import State


def op_SET(state: State, arg1: str, arg2: str) -> None:
    state.require(state.in_action, 'Not inside any action.', f'SET can be used inside actions.')
    lhs = Argument(state, arg1)
    rhs = Argument(state, arg2)
    state.require(
        lhs.assignment_context(rhs), 
        'Mismatched types in the assignment context.', 
        f'ARG1 {lhs.explain()}, ARG2 {rhs.explain()}'
    )    
    
    state.last_action.add_instruction(Set(lhs, rhs))
