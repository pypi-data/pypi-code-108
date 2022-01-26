from __future__ import annotations

from typing import TYPE_CHECKING, List

from aasm.intermediate.agent import \
    ConnectionListParam as AgentConnectionListParam
from aasm.intermediate.agent import DistExpFloatParam as AgentDistExpFloatParam
from aasm.intermediate.agent import \
    DistNormalFloatParam as AgentDistNormalFloatParam
from aasm.intermediate.agent import EnumParam as AgentEnumParam
from aasm.intermediate.agent import InitFloatParam as AgentInitFloatParam
from aasm.intermediate.agent import MessageListParam as AgentMessageListParam
from aasm.intermediate.message import FloatParam as MessageFloatParam
from aasm.utils.validation import (is_float, is_valid_enum_list, is_valid_name,
                                   print_invalid_names)

if TYPE_CHECKING:
    from parsing.state import State


def op_agent_PRM(state: State, name: str, category: str, args: List[str]) -> None:    
    state.require(
        state.in_agent, 
        'Cannot define agent parameters outside agent scope.', 
        'Try defining new agents using AGENT.'
    )
    state.require(
        not state.in_behaviour, 
        'Cannot define agent parameters inside a behaviour.', 
        'Parameters must appear after AGENT.'
    )
    state.require(not state.last_agent.name_exists(name), f'{name} already exists inside current agent.')
    state.require(
        is_valid_name(name), 
        f'{name} is not a correct name.', 
        f'Names can only contain alphanumeric characters, underscores and cannot be: {print_invalid_names()}.'
    )
    
    match category, args:
        case 'float', [ 'init', value ]:
            state.require(is_float(value), f'{value} is not a valid float.')

            state.last_agent.add_init_float(AgentInitFloatParam(name, value))
            
        case 'float', [ 'dist', 'normal', mean, std_dev ]:
            state.require(is_float(mean), f'{mean} is not a valid float.')
            state.require(is_float(std_dev), f'{std_dev} is not a valid float.')

            state.last_agent.add_dist_normal_float(AgentDistNormalFloatParam(name, mean, std_dev))
            
        case 'float', [ 'dist', 'exp', lambda_ ]:
            state.require(is_float(lambda_), f'{lambda_} is not a valid float.')
            state.require(
                float(lambda_) > 0, 
                f'{lambda_} is not a valid lambda parameter.', 
                'Lambda must be non-negative.'
            )

            state.last_agent.add_dist_exp_float(AgentDistExpFloatParam(name, lambda_))
            
        case 'list', [ 'conn' ]:
            state.last_agent.add_connection_list(AgentConnectionListParam(name))
            
        case 'list', [ 'msg' ]:
            state.last_agent.add_message_list(AgentMessageListParam(name))
            
        case 'enum', enums:
            state.require(
                is_valid_enum_list(enums),
                f'{enums} is not a valid enum list.', 
                'The correct pattern is [name, percent, ...], where percent(s) sum up to 100 (+/- 1).'
            )

            state.last_agent.add_enum(AgentEnumParam(name, enums))
            
        case _:
            state.panic(f'Incorrect operation: (agent) PRM {name} {category} {args}')


def op_message_PRM(state: State, name: str, category: str) -> None:    
    state.require(
        state.in_message, 
        'Cannot define message parameters outside message scope.', 
        'Try defining new messages using MESSAGE.'
    )
    state.require(not state.last_message.param_exists(name), f'Parameter {name} already exists inside current message.')
    state.require(
        is_valid_name(name), 
        f'{name} is not a correct name.', 
        f'Names can only contain alphanumeric characters, underscores and cannot be: {print_invalid_names()}.'
    )
    
    match category:
        case 'float':
            state.last_message.add_float(MessageFloatParam(name))

        case _:
            state.panic(f'Incorrect operation: (message) PRM {name} {category}')
