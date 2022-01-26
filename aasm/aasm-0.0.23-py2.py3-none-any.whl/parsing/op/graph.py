from __future__ import annotations

from typing import TYPE_CHECKING

from aasm.intermediate.graph import StatisticalGraph

if TYPE_CHECKING:
    from aasm.parsing.state import State


def op_GRAPH(state: State, category: str) -> None:    
    state.require(not state.in_graph, 'Already inside a graph.', 'First end current graph using EGRAPH.')
    state.require(not state.in_agent, 'Cannot define graphs inside agents.', 'First end current message using EAGENT.')
    state.require(
        not state.in_message, 
        'Cannot define graphs inside messages.', 
        'First end current message using EMESSAGE.'
    )
    state.require(not state.graph_exists(), 'Graph already exists in the current environment.')

    match category:
        case 'statistical':
            state.add_graph(StatisticalGraph())

        case _:
            state.panic(f'Incorrect operation: GRAPH {category}')
    
    state.in_graph = True


def op_EGRAPH(state: State) -> None:    
    state.require(state.in_graph, 'Not inside any graph.', 'Try defining new graphs using GRAPH.')
    if isinstance(state.graph, StatisticalGraph) and state.graph.is_agent_percent_amount_used():
        state.require(
            state.graph.is_size_defined(), 
            'Graph size is not defined.', 
            'Graph size must be defined to use agent percent amount.'
        )
    
    state.in_graph = False
