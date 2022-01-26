from __future__ import annotations

from typing import TYPE_CHECKING

from aasm.intermediate.message import Message
from aasm.utils.validation import is_valid_name, print_invalid_names

if TYPE_CHECKING:
    from aasm.parsing.state import State


def op_MESSAGE(state: State, msg_type: str, msg_performative) -> None:
    state.require(not state.in_message, 'Already inside a message.', 'First end current message using EMESSAGE.')
    state.require(not state.in_agent, 'Cannot define messages inside agents.', 'First end current agent using EAGENT.')
    state.require(not state.in_graph, 'Cannot define messages inside graphs.', 'First end current graph using EGRAPH.')
    state.require(
        not state.message_exists(msg_type, msg_performative), 
        f'Message {msg_type}/{msg_performative} already exists in the current environment.'
    )
    state.require(
        is_valid_name(msg_type), 
        f'{msg_type} is not a correct name.', 
        f'Names can only contain alphanumeric characters, underscores and cannot be: {print_invalid_names()}.'
    )
    state.require(
        is_valid_name(msg_performative), 
        f'{msg_performative} is not a correct name.', 
        f'Names can only contain alphanumeric characters, underscores and cannot be: {print_invalid_names()}.'
    )
    
    state.in_message = True
    state.add_message(Message(msg_type, msg_performative))


def op_EMESSAGE(state: State) -> None:    
    state.require(state.in_message, 'Not inside any message.', 'Try defining new messages using MESSAGE.')
    
    state.in_message = False
