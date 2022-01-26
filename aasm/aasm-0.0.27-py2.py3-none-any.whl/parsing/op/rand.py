from __future__ import annotations

from typing import TYPE_CHECKING, List

from aasm.intermediate.argument import Argument
from aasm.intermediate.instruction import ExpDist, NormalDist, UniformDist
from aasm.parsing.op.round import op_ROUND

if TYPE_CHECKING:
    from aasm.parsing.state import State


def op_RAND(state: State, arg1: str, arg2: str, arg3: str, args: List[str]) -> None:
    state.require(state.in_action, 'Not inside any action.', f'RAND can be used inside actions.')
    result = Argument(state, arg1)

    match arg3, args:
        case 'uniform', [ a, b ]:
            a_arg = Argument(state, a)
            b_arg = Argument(state, b)
            state.require(
                result.random_number_generation_context(a_arg, b_arg), 
                'Mismatched types in the random number generation context.', 
                f'RESULT {result.explain()}, A {a_arg.explain()}, B {b_arg.explain()}'
            )

            state.last_action.add_instruction(UniformDist(result, a_arg, b_arg))

        case 'normal', [ mean, std_dev ]:
            mean_arg = Argument(state, mean)
            std_dev_arg = Argument(state, std_dev)
            state.require(
                result.random_number_generation_context(mean_arg, std_dev_arg), 
                'Mismatched types in the random number generation context.', 
                f'RESULT {result.explain()}, MEAN {mean_arg.explain()}, STD_DEV {std_dev_arg.explain()}'
            )

            state.last_action.add_instruction(NormalDist(result, mean_arg, std_dev_arg))

        case 'exp', [ lambda_ ]:
            lambda_arg = Argument(state, lambda_)
            state.require(
                result.random_number_generation_context(lambda_arg), 
                'Mismatched types in the random number generation context.', 
                f'RESULT {result.explain()}, LAMBDA {lambda_arg.explain()}'
            )

            state.last_action.add_instruction(ExpDist(result, lambda_arg))

        case _:
            state.panic(f'Incorrect operation: RAND {arg1} {arg2} {arg3} {args}')

    match arg2:
        case 'float':
            ...

        case 'int':
            op_ROUND(state, arg1)

        case _:
            state.panic(f'Incorrect operation: RAND {arg1} {arg2} {arg3} {args}')
