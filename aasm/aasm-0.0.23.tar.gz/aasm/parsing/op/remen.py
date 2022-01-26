from __future__ import annotations

from typing import TYPE_CHECKING

from aasm.intermediate.argument import Argument
from aasm.intermediate.instruction import RemoveNElements

if TYPE_CHECKING:
    from aasm.parsing.state import State


def op_REMEN(state: State, arg1: str, arg2: str) -> None:
    state.require(state.in_action, 'Not inside any action.', 'List modifications can be used inside actions.')
    lhs = Argument(state, arg1)
    rhs = Argument(state, arg2)
    state.require(
        lhs.list_n_removal_context(rhs), 
        'Mismatched types in the list n removal context.', 
        f'ARG1 {lhs.explain()}, ARG2 {rhs.explain()}'
    )
    
    state.last_action.add_instruction(RemoveNElements(lhs, rhs))
