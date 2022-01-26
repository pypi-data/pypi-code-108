from __future__ import annotations

from typing import TYPE_CHECKING

from aasm.intermediate.argument import Argument
from aasm.intermediate.instruction import (IfEqual, IfGreaterThan,
                                           IfGreaterThanOrEqual, IfLessThan,
                                           IfLessThanOrEqual, IfNotEqual,
                                           WhileEqual, WhileGreaterThan,
                                           WhileGreaterThanOrEqual,
                                           WhileLessThan, WhileLessThanOrEqual,
                                           WhileNotEqual)

if TYPE_CHECKING:
    from aasm.parsing.state import State


def handle_unordered_conditional_statement(state: State, op: str, arg1: str, arg2: str) -> None:
    state.require(state.in_action, 'Not inside any action.', f'{op} can be used inside actions.')     
    lhs = Argument(state, arg1)
    rhs = Argument(state, arg2)
    state.require(
        lhs.unordered_comparaison_context(rhs), 
        'Mismatched types in the unordered comparaison context.', 
        f'ARG1 {lhs.explain()}, ARG2 {rhs.explain()}'
    )
    
    match op:
        case 'IEQ':
            state.last_action.add_instruction(IfEqual(lhs, rhs))

        case 'INEQ':
            state.last_action.add_instruction(IfNotEqual(lhs, rhs))

        case 'WEQ':
            state.last_action.add_instruction(WhileEqual(lhs, rhs))

        case 'WNEQ':
            state.last_action.add_instruction(WhileNotEqual(lhs, rhs))

        case _:
            state.panic(f'Unexpected error: {op} {arg1} {arg2}')
    
    state.last_action.start_block()


def handle_ordered_conditional_statement(state: State, op: str, arg1: str, arg2: str) -> None:
    state.require(state.in_action, 'Not inside any action.', f'{op} can be used inside actions.')     
    lhs = Argument(state, arg1)
    rhs = Argument(state, arg2)
    state.require(
        lhs.ordered_comparaison_context(rhs),
        'Mismatched types in the ordered comparaison context.', 
        f'ARG1 {lhs.explain()}, ARG2 {rhs.explain()}'
    )
    
    match op:
        case 'IGT':
            state.last_action.add_instruction(IfGreaterThan(lhs, rhs))

        case 'IGTEQ':
            state.last_action.add_instruction(IfGreaterThanOrEqual(lhs, rhs))

        case 'ILT':
            state.last_action.add_instruction(IfLessThan(lhs, rhs))

        case 'ILTEQ':
            state.last_action.add_instruction(IfLessThanOrEqual(lhs, rhs))

        case 'WGT':
            state.last_action.add_instruction(WhileGreaterThan(lhs, rhs))

        case 'WGTEQ':
            state.last_action.add_instruction(WhileGreaterThanOrEqual(lhs, rhs))

        case 'WLT':
            state.last_action.add_instruction(WhileLessThan(lhs, rhs))

        case 'WLTEQ':
            state.last_action.add_instruction(WhileLessThanOrEqual(lhs, rhs))

        case _:
            state.panic(f'Unexpected error: {op} {arg1} {arg2}')
    
    state.last_action.start_block()
