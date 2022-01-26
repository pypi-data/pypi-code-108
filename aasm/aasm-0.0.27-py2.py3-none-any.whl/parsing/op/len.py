from __future__ import annotations

from typing import TYPE_CHECKING

from aasm.intermediate.argument import Argument
from aasm.intermediate.instruction import Length

if TYPE_CHECKING:
    from aasm.parsing.state import State


def op_LEN(state: State, arg1: str, arg2: str) -> None:
    state.require(state.in_action, 'Not inside any action.', 'LEN can be used inside actions.')
    lhs = Argument(state, arg1)
    rhs = Argument(state, arg2)
    state.require(
        lhs.list_length_context(rhs), 
        'Mismatched types in the list length context.', 
        f'ARG1 {lhs.explain()}, ARG2 {rhs.explain()}'
    )
    
    state.last_action.add_instruction(Length(lhs, rhs))
