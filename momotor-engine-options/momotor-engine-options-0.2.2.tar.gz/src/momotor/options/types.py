import typing

try:
    from typing import Literal  # Python 3.8+
except ImportError:
    from typing_extensions import Literal


StepTasksType = typing.Tuple[int, ...]
StepTaskNumberType = typing.Optional[typing.Tuple[int, ...]]

OptionTypeLiteral = Literal['str', 'bool', 'int', 'float']
LocationLiteral = Literal['step', 'recipe', 'config', 'product']

SubDomainDefinitionType = typing.Dict[
    LocationLiteral,
    typing.Union[str, typing.Sequence[typing.Optional[str]], None]
]
