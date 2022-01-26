from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aasm.parsing.state import State


def op_EBLOCK(state: State) -> None:            
    state.require(state.in_action, 'Cannot end blocks outside actions.')
    state.require(state.last_action._nested_blocks_count > 0, 'No more blocks to close', 'Try removing this statement.')
    
    state.last_action.end_block()
