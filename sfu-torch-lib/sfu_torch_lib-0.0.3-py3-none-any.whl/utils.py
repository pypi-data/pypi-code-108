import functools
import math
import re
from typing import List, Tuple, TypeVar, Generator, Type, Union, Sequence, Mapping, Callable

from torch.nn import ELU, Identity, ReLU, LeakyReLU, Sigmoid, Softmax, Tanh, Module
from torch.utils.data import Dataset


T = TypeVar('T')


def get_pairs(items: List[T]) -> Generator[Tuple[T, T], None, None]:
    for index in range(len(items) - 1):
        yield items[index], items[index + 1]


def create_selector(indices: Union[int, Sequence[int]]) -> Callable[[Sequence[T]], Union[T, Tuple[T, ...]]]:
    def select(items: Sequence[T]) -> Union[T, Tuple[T, ...]]:
        if isinstance(indices, int):
            return items[indices]

        return tuple(items[index] for index in indices)

    return select


def to_list(*args: Union[Sequence[T], T]) -> List[T]:
    items: List[T] = []

    for argument in args:
        if isinstance(argument, Sequence):
            items += argument
        else:
            items.append(argument)

    return items


def get_activation(name: str) -> Type[Module]:
    return {
        'elu': ELU,
        'identity': Identity,
        'relu': ReLU,
        'leaky_relu': LeakyReLU,
        'sigmoid': Sigmoid,
        'softmax': Softmax,
        'tanh': Tanh,
    }[name]


def parse_map_sequence(string: str, sequence_type: Type[T]) -> Mapping[str, Sequence[T]]:
    substrings = re.split(r'(?<=]),', string)

    output = {}

    for substring in substrings:
        key, value = substring.split(':')

        output[key] = list(map(sequence_type, value.strip('[]').split(',')))

    return output


def get_num_steps(dataset: Dataset, frequency: int = 10) -> int:
    return max(1, math.floor(len(dataset) / frequency))


parse_map_ints = functools.partial(parse_map_sequence, sequence_type=int)
parse_map_floats = functools.partial(parse_map_sequence, sequence_type=float)
parse_map_strings = functools.partial(parse_map_sequence, sequence_type=str)
