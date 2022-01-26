from __future__ import annotations

from typing import TYPE_CHECKING

from aasm.intermediate.agent import Agent
from aasm.utils.validation import is_valid_name, print_invalid_names

if TYPE_CHECKING:
    from aasm.parsing.state import State


def op_AGENT(state: State, name: str) -> None:    
    state.require(not state.in_agent, 'Already inside an agent.', 'First end current agent using EAGENT.')
    state.require(
        not state.in_message, 
        'Cannot define agents inside messages.', 
        'First end current message using EMESSAGE.'
    )
    state.require(not state.in_graph, 'Cannot define agents inside graphs.', 'First end current graph using EGRAPH.')
    state.require(not state.agent_exists(name), f'Agent {name} already exists in the current environment.')
    state.require(
        is_valid_name(name), 
        f'{name} is not a correct name.', 
        f'Names can only contain alphanumeric characters, underscores and cannot be: {print_invalid_names()}.'
    )
    
    state.in_agent = True
    state.add_agent(Agent(name))


def op_EAGENT(state: State) -> None:    
    state.require(state.in_agent, 'Not inside any agent.', 'Try defining new agents using AGENT.')
    state.require(
        not state.in_behaviour, 
        'Cannot end an agent inside a behaviour.', 
        'First end current behaviour using EBEHAV.'
    )
    
    state.in_agent = False
