from __future__ import annotations

from typing import TYPE_CHECKING

from aasm.intermediate.argument import Argument
from aasm.intermediate.instruction import Add, Divide, Multiply, Subtract

if TYPE_CHECKING:
    from aasm.parsing.state import State


def handle_math_statement(state: State, op: str, arg1: str, arg2: str) -> None:
    state.require(state.in_action, 'Not inside any action', f'{op} can be used inside actions.')
    lhs = Argument(state, arg1)
    rhs = Argument(state, arg2)
    state.require(
        lhs.math_context(rhs),
        'Mismatched types in the math statement.', 
        f'ARG1 {lhs.explain()}, ARG2 {rhs.explain()}'
    )

    match op:
        case 'ADD':
            state.last_action.add_instruction(Add(lhs, rhs))

        case 'SUBT':
            state.last_action.add_instruction(Subtract(lhs, rhs))

        case 'MULT':
            state.last_action.add_instruction(Multiply(lhs, rhs))

        case 'DIV':
            state.last_action.add_instruction(Divide(lhs, rhs))

        case _:
            state.panic(f'Unexpected error: {op} {arg1} {arg2}')
