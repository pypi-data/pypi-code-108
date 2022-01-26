from __future__ import annotations

from typing import TYPE_CHECKING

from aasm.intermediate.argument import Argument
from aasm.intermediate.instruction import Subset

if TYPE_CHECKING:
    from aasm.parsing.state import State


def op_SUBS(state: State, arg1: str, arg2: str, arg3: str) -> None:
    state.require(state.in_action, 'Not inside any action.', f'SUBS can be used inside actions.')
    dst_list = Argument(state, arg1)
    src_list = Argument(state, arg2)
    num = Argument(state, arg3)
    state.require(
        dst_list.list_subset_context(src_list, num), 
        'Mismatched types in the subset context.', 
        f'ARG1 {dst_list.explain()}, ARG2 {src_list.explain()}, ARG3 {num.explain()}'
    )
    
    state.last_action.add_instruction(Subset(dst_list, src_list, num))
