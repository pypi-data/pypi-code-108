from __future__ import annotations

from typing import TYPE_CHECKING

from aasm.utils.validation import is_int

if TYPE_CHECKING:
    from aasm.parsing.state import State


def op_SIZE(state: State, size: str) -> None:
    state.require(state.in_graph, 'Not inside any graph.', 'SIZE can be used inside graphs.')
    state.require(not state.graph.is_size_defined(), 'Size is already defined')
    state.require(is_int(size), 'Graph size must be an integer value.')
    state.require(int(size) >= 0, 'Graph size cannot be a negative number.')

    state.graph.set_size(int(size))
