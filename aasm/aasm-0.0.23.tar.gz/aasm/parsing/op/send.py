from __future__ import annotations

from typing import TYPE_CHECKING

from aasm.intermediate.action import SendMessageAction
from aasm.intermediate.argument import Argument
from aasm.intermediate.instruction import Send

if TYPE_CHECKING:
    from aasm.parsing.state import State


def op_SEND(state: State, arg1: str) -> None:
    state.require(state.in_action, 'Not inside any action.', 'SEND can be used inside send_msg actions.')
    state.require(
        isinstance(state.last_action, SendMessageAction), 
        'Not inside send_msg action.', 
        'SEND can be used inside send_msg actions.'
    )
    receivers = Argument(state, arg1)
    state.require(receivers.send_context(), 'Mismatched type in the send context.', f'ARG1 {receivers.explain()}')

    state.last_action.add_instruction(Send(receivers))
