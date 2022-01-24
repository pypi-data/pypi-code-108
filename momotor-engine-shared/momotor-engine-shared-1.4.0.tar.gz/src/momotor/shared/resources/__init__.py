import collections
import itertools
import typing

from .const import STRONGEST, STRONG, NEUTRAL, WEAK, WEAKEST
from .exception import NoMatch
from .group import ResourceGroup
from .item import ResourceItem
from .utils import unique_everseen, quote_str

__all__ = ['NoMatch', 'Resources', "ResourceGroup"]


RT = typing.TypeVar('RT', bound='Resources')


def split_resources(resources: str) -> typing.Generator[typing.Tuple[str, str], None, None]:
    """ Split a resources string into group-name, group-definition tuples

    :param resources: One or more resource definitions (either multi-line or semi-colon separated),
                      including group names
    :raises :py:exc:`ValueError`: if the string is an invalid resources definition
    :return: A generator yielding group-name, group definition tuples
    """
    key = None
    current = ''
    whitespace = ''
    quote = None
    escape = False  # True: include next character unconditionally

    resources = resources.strip()
    if resources:
        for c in resources+'\n':
            if escape:
                # This character is escaped, so include it unconditionally
                escape = False
                current += c
            elif c == '\\':
                # Escape next character. Keep escape character in values
                if key is not None:
                    current += c
                escape = True
            elif quote:
                # Inside a quoted string. Quotes in keys should be removed, but in values they need to be kept
                if c == quote:
                    # End of string
                    if key is not None:
                        current += c
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
                if key is not None:
                    current += c
                whitespace = ''
            elif c in (';', '\n'):
                # Field separator. Ignore trailing whitespace, reset state
                if key is None:
                    raise ValueError(f"missing key in {current!r}")

                yield key, whitespace + current
                key = None
                current = ''
                whitespace = ''
            elif key is None and not (str.isalnum(c) or c in ('-', '_', '.')):
                key = current
                current = '' if c == ':' else c
                whitespace = ''
            else:
                # Any other character. Include whitespace too if it was collected
                current += whitespace + c
                whitespace = ''

        if quote:
            # Unterminated quoted string
            raise ValueError("unmatched quotes")

        assert key is None
        assert current == ''
        assert whitespace == ''


def combine_group(left: typing.Optional[float], right: typing.Optional[float]) -> typing.Optional[float]:
    """ Combine group values

    Returns the **weakest** match, ie. the higher numeric value.
    If one value is ``None``, returns the other value.
    """
    if left is None:
        return right
    elif right is None:
        return left
    else:
        return max(left, right)


class Resources:
    """ Manage resources for a task and worker.

    resource value handling:

    boolean items:

    * *tag*: required tag
    * *?tag*: optional tag
    * *~tag*: excluded tag

    The following table indicates the match value for boolean tags of given type,
    :py:class:`~momotor.shared.resources.NoMatch` indicates that the :py:class:`~momotor.shared.resources.NoMatch`
    exception is raised, any other value indicates that that value is returned.

    * `-`: worker or task does not have this tag defined
    * blank cell: ignore, no change in match value

    TODO numeric items

    :param definition: A dictionary of group names to resource groups

    """
    def __init__(self, definition: typing.Dict[str, ResourceGroup] = None):
        self._definition = definition or {}

    # Factories

    @classmethod
    def from_dict(cls: typing.Type[RT], definition: typing.Dict[str, typing.Union[str, typing.Iterable[str]]]) -> RT:
        """ Factory to create a :py:class:`~momotor.shared.resources.Resources` object from a dict
        of group names to group string definitions """
        return cls({
            key: ResourceGroup.create(value) for key, value in definition.items()
        })

    @classmethod
    def from_key_value(cls: typing.Type[RT], key: str, value: typing.Union[str, typing.Iterable[str]]) -> RT:
        """ Factory to create a :py:class:`~momotor.shared.resources.Resources` object from a key and values

        :param key: Group name
        :param value: Group definition string or list of strings
        """
        return cls({
            key: ResourceGroup.create(value)
        })

    @classmethod
    def from_string(cls: typing.Type[RT], value: typing.Union[str, typing.Iterable[str]]) -> RT:
        """ Factory to create a :py:class:`~momotor.shared.resources.Resources` object from
        one or more strings

        :param value: A string or iterable of strings containing resource definitions including a group name
        :return: The parsed resources
        :raises: :py:exc:`ValueError` if the string is an invalid resources definition
        """
        resources = collections.deque()

        if isinstance(value, str):
            resources.extend(split_resources(value))
        else:
            for s in value:
                resources.extend(split_resources(s))

        return cls.union(*(
            cls.from_key_value(key, value) for key, value in resources
        ))

    @classmethod
    def union(cls: typing.Type[RT], *resources: RT) -> RT:
        """ Merge multiple :py:class:`~momotor.shared.resources.Resources` objects into a new one

        :returns: The merged resources
        """

        return cls({
            key: ResourceGroup.union(*(resource.get(key) for resource in resources))
            for key in unique_everseen(
                itertools.chain(*(resource.group_names() for resource in resources))
            )
        })

    # Implementation

    def __len__(self):
        return len(self._definition)

    def group_names(self) -> typing.List[str]:
        """ Returns a list of group names

        :return: group names
        """
        return list(self._definition.keys())

    def get(self, key: str) -> ResourceGroup:
        """ Get the :py:class:`~momotor.shared.resources.ResourceGroup` by name

        :param key: Group name
        :return: The resource group matching the group name
        """
        return self._definition.get(key, ResourceGroup())

    def match(self, worker_resource: "Resources") -> float:
        """ Returns the match between these resources and the provided worker's resources.

        :param worker_resource: The worker's resources
        :return: match value, the lower the value, the better the match is (ranges from
                 -\ :py:data:`~math.inf` to +\ :py:data:`~math.inf`).
                 If nothing matches, but also nothing is excluded, will return
                 :py:data:`~momotor.shared.resources.const.NEUTRAL`
        :raises: :py:exc:`~momotor.shared.resources.NoMatch` if no match can be made (eg. due to an exclude)
        """
        match = None

        group_names = set(self.group_names()) | set(worker_resource.group_names())
        for name in group_names:
            group_match = self.get(name).match(worker_resource.get(name))
            match = combine_group(match, NEUTRAL if group_match is None else group_match)

        return NEUTRAL if match is None else match

    def as_tuples(self) -> typing.Iterable[typing.Tuple[str, typing.Tuple[str]]]:
        for key, group in self._definition.items():
            yield key, group.as_str_tuple()

    def as_str_tuples(self) -> typing.Iterable[typing.Tuple[str, str]]:
        for key, group in self._definition.items():
            yield key, group.as_str()

    def as_str(self, *, multiline: bool = False, compact: bool = False) -> str:
        """ Convert these resources into a string that can be parsed back into a
        :py:class:`~momotor.shared.resources.Resources` object using
        :py:meth:`~momotor.shared.resources.Resources.from_string`

        :param multiline: if True, use newlines to split groups, otherwise uses semicolons
        :param compact: if True, returns a compact representation, otherwise adds more whitespace
        :return: string representation of the resources
        """
        line_sep = '\n' if multiline else (';' if compact else '; ')
        key_sep = ':' if compact else ': '
        value = line_sep.join(f'{quote_str(key)}{key_sep}{group}'.strip() for key, group in self.as_str_tuples())
        if value and multiline and not compact:
            return value + '\n'
        return value

    def __str__(self) -> str:
        return '{' + self.as_str() + '}'
