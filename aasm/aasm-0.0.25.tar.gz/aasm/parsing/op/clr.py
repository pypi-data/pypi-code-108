from __future__ import annotations

from typing import TYPE_CHECKING

from aasm.intermediate.argument import Argument
from aasm.intermediate.instruction import Clear

if TYPE_CHECKING:
    from aasm.parsing.state import State


def op_CLR(state: State, arg1: str) -> None:
    state.require(state.in_action, 'Not inside any action.', 'CLR can be used inside actions.')
    list_ = Argument(state, arg1)
    state.require(list_.list_clear_context(), 'Mismatched type in the list clear context.', f'ARG {list_.explain()}')

    state.last_action.add_instruction(Clear(list_))
