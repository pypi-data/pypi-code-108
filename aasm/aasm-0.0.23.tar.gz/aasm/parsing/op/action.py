from __future__ import annotations

from typing import TYPE_CHECKING, List

from aasm.intermediate.action import ModifySelfAction, SendMessageAction
from aasm.utils.validation import is_valid_name, print_invalid_names

if TYPE_CHECKING:
    from aasm.parsing.state import State


def op_ACTION(state: State, name: str, category: str, args: List[str]) -> None:
    state.require(
        state.in_behaviour, 
        'Actions must be definied inside behaviours.', 
        'Try defining new behaviours using BEHAV.'
    )
    state.require(
        not state.in_action, 
        'Cannot define an action in another action.', 
        'Try finishing current action using EACTION.'
    )
    state.require(not state.last_behaviour.action_exists(name), f'Action {name} already exists in current behaviour.')
    state.require(
        is_valid_name(name), 
        f'{name} is not a correct name.', 
        f'Names can only contain alphanumeric characters, underscores and cannot be: {print_invalid_names()}.'
    )
    
    match category, args:
        case 'modify_self', [ ]:
            state.last_behaviour.add_action(ModifySelfAction(name))
            
        case 'send_msg', [ msg_type, msg_performative ]:
            state.require(
                state.message_exists(msg_type, msg_performative), 
                f'Message {msg_type}/{msg_performative} does not exist.', 
                'Try defining new messages using MESSAGE.'
            )

            state.last_behaviour.add_action(SendMessageAction(name, state.get_message_instance(msg_type, msg_performative)))
            
        case _:
            state.panic(f'Incorrect operation: ACTION {category} {args}')
    
    state.in_action = True


def op_EACTION(state: State) -> None:            
    state.require(state.in_action, 'Not inside any action.', 'Try defining new actions using ACTION.')
    state.require(
        state.last_action._nested_blocks_count == 0, 
        'There are unclosed blocks.', 
        'Try closing them using EBLOCK.'
    )
    
    state.in_action = False
