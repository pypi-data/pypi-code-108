import typing

from .const import STRONGEST, STRONG, WEAK, WEAKEST
from .exception import NoMatch

PRIO_MAPPING = {
    (True, True): STRONGEST,
    (True, False): STRONG,
    (False, True): WEAK,
    (False, False): WEAKEST,
}


def split_items(items: str) -> typing.Generator[str, None, None]:
    current = ''  # Current value being collected
    whitespace = ''  # Whitespace that might or might not be part of the value
    quote = None  # None: not inside a quoted string, otherwise the quote itself
    escape = False  # True: include next character unconditionally

    for c in items+',':
        if escape:
            # This character is escaped, so include it unconditionally
            escape = False
            current += c
        elif c == '\\':
            # Escape next character
            escape = True
        elif quote:
            # Inside a quoted string
            if c == quote:
                # End of string
                quote = None
            else:
                # Include any other character
                current += c
        elif c in (' ', '\t'):
            # Whitespace. Ignore leading whitespace, collect all other whitespace in a separate variable
            if current:
                whitespace += c
        elif c in ('"', "'"):
            # Start of a quoted string. Also include whitespace into current
            quote = c
            current += whitespace
            whitespace = ''
        elif c == ',':
            # Field separator. Ignore trailing whitespace, reset current value
            yield current
            current = ''
            whitespace = ''
        elif c == ':':
            # An unescaped colon is not allowed (See #3)
            raise ValueError("colons in items must be escaped")
        else:
            # Any other character. Include whitespace too if it was collected
            current += whitespace + c
            whitespace = ''

    if quote:
        # Unterminated quoted string
        raise ValueError("unmatched quotes")

    assert current == ''
    assert whitespace == ''


RIT = typing.TypeVar('RIT', bound='ResourceItem')


class ResourceItem:
    def __init__(self, value: str, required: bool, excluded: bool):
        if required and excluded:
            raise ValueError('cannot combine required and excluded flags')

        self.value = value
        self.required = required
        self.excluded = excluded

    @classmethod
    def _create_item(cls: typing.Type[RIT], value) -> RIT:
        from .tag import Tag
        return Tag(value)

    @classmethod
    def create(cls: typing.Type[RIT], value: typing.Union[str, typing.Iterable[str]]) -> typing.Iterable[RIT]:
        if isinstance(value, str):
            for item in split_items(value):
                if item:
                    yield cls._create_item(item)
        else:
            for element in value:
                for item in split_items(element):
                    if item:
                        yield cls._create_item(item)

    def comparable(self, worker: RIT) -> bool:
        return type(self) == type(worker)

    def compare(self, worker: RIT) -> typing.Optional[float]:
        """
            +-----------+------------------------------------------------------+----------------------------------------------------+-----------------------------------------------+
            | . worker  | required                                             | optional                                           | excluded                                      |
            | task      |                                                      |                                                    |                                               |
            +-----------+------------------------------------------------------+----------------------------------------------------+-----------------------------------------------+
            | required  | :py:data:`~momotor.shared.resources.const.STRONGEST` | :py:data:`~momotor.shared.resources.const.STRONG`  | :py:class:`~momotor.shared.resources.NoMatch` |
            +-----------+------------------------------------------------------+----------------------------------------------------+-----------------------------------------------+
            | optional  | :py:data:`~momotor.shared.resources.const.WEAK`      | :py:data:`~momotor.shared.resources.const.WEAKEST` | :py:class:`~momotor.shared.resources.NoMatch` |
            +-----------+------------------------------------------------------+----------------------------------------------------+-----------------------------------------------+
            | excluded  | :py:class:`~momotor.shared.resources.NoMatch`        | :py:class:`~momotor.shared.resources.NoMatch`      |                                               |
            +-----------+------------------------------------------------------+----------------------------------------------------+-----------------------------------------------+
        """
        if self.comparable(worker):
            if self.excluded or worker.excluded:
                if self.excluded and worker.excluded:
                    return None
                else:
                    raise NoMatch

            return PRIO_MAPPING[(self.required, worker.required)]

        return None

    @classmethod
    def compare_missing(cls: typing.Type[RIT], worker: RIT) -> typing.Optional[float]:
        """
            +----------+-----------------------------------------------+----------------------------------------------------+------------------------------------------------+
            | . worker | required                                      | optional                                           | excluded                                       |
            | task     |                                               |                                                    |                                                |
            +----------+-----------------------------------------------+----------------------------------------------------+------------------------------------------------+
            | `-`      | :py:class:`~momotor.shared.resources.NoMatch` |                                                    |                                                |
            +----------+-----------------------------------------------+----------------------------------------------------+------------------------------------------------+
        """
        if worker.required:
            raise NoMatch

        return None

    def as_str(self) -> str:
        if self.excluded:
            prefix = '~'
        elif self.required:
            prefix = ''
        else:
            prefix = '?'

        return prefix + self.value
