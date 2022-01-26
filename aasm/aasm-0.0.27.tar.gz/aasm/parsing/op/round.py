from __future__ import annotations

from typing import TYPE_CHECKING

from aasm.intermediate.argument import Argument
from aasm.intermediate.instruction import Round

if TYPE_CHECKING:
    from aasm.parsing.state import State


def op_ROUND(state: State, arg1: str) -> None:
    state.require(state.in_action, 'Not inside any action.', f'ROUND can be used inside actions.')
    num = Argument(state, arg1)
    state.require(num.round_number_context(), 'Mismatched type in the round number context.', f'NUM {num.explain()}')

    state.last_action.add_instruction(Round(num))
