from __future__ import annotations

from typing import TYPE_CHECKING, List

from aasm.intermediate.behaviour import (CyclicBehaviour,
                                         MessageReceivedBehaviour,
                                         OneTimeBehaviour, SetupBehaviour)
from aasm.utils.validation import is_float, is_valid_name, print_invalid_names

if TYPE_CHECKING:
    from aasm.parsing.state import State


def op_BEHAV(state: State, name: str, category: str, args: List[str]):
    state.require(state.in_agent, 'Cannot define behaviours outside agents.', 'Try defining new agents using AGENT.')
    state.require(
        not state.in_behaviour,
        'Cannot define behaviours inside other behaviours.',
        'First end current behaviour using EBEHAV.'
    )
    state.require(not state.last_agent.name_exists(name), f'{name} already exists in current agent.')
    state.require(
        is_valid_name(name), 
        f'{name} is not a correct name.', 
        f'Names can only contain alphanumeric characters, underscores and cannot be: {print_invalid_names()}.'
    )
    
    match category, args:
        case 'setup', [ ]:
            state.last_agent.add_setup_behaviour(SetupBehaviour(name))
            
        case 'one_time', [ delay ]:
            state.require(is_float(delay) and float(delay) >= 0, f'{delay} is not a valid delay value.')

            state.last_agent.add_one_time_behaviour(OneTimeBehaviour(name, delay))
            
        case 'cyclic', [ period ]:
            state.require(is_float(period) and float(period) > 0, f'{period} is not a valid period value.')

            state.last_agent.add_cyclic_behaviour(CyclicBehaviour(name, period))
            
        case 'msg_rcv', [ msg_type, msg_performative ]:
            state.require(
                state.message_exists(msg_type, msg_performative), 
                f'Message {msg_type}/{msg_performative} does not exist.', 
                'Try defining new messages using MESSAGE'
            )
            state.require(
                not state.last_agent.behaviour_for_template_exists(msg_type, msg_performative), 
                f'Behaviour for template {msg_type}/{msg_performative} already exists in current agent.'
            )

            state.last_agent.add_message_received_behaviour(
                MessageReceivedBehaviour(name, state.get_message_instance(msg_type, msg_performative))
            )
            
        case _:
            state.panic(f'Incorrect operation: BEHAV {name} {category} {args}')
    
    state.in_behaviour = True


def op_EBEHAV(state: State) -> None:            
    state.require(state.in_behaviour, 'Not inside any behaviour.', 'Try defining new behaviours using BEHAV.')
    state.require(
        not state.in_action, 
        'Cannot end behaviours inside actions.', 
        'Try ending current action using EACTION.'
    )
    
    state.in_behaviour = False
