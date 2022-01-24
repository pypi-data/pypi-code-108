import itertools
import typing

from .exception import NoMatch
from .item import ResourceItem
from .utils import unique_everseen, quote_str, escape_str


UNSAFE_CHARS = {',', ':', ';', '"', "'"}


def quote_item(item: str) -> str:
    if item.startswith(' ') or item.endswith(' ') or '\t' in item or '\n' in item:
        return quote_str(item)

    return escape_str(item, UNSAFE_CHARS)


def combine_item(left: typing.Optional[float], right: typing.Optional[float]) -> typing.Optional[float]:
    """ Combine item values

    Returns the **strongest** match, ie. the lower numeric value.
    If one value is ``None``, returns the other value.
    """
    if left is None:
        return right
    elif right is None:
        return left
    else:
        return min(left, right)


RGT = typing.TypeVar('RGT', bound='ResourceGroup')


class ResourceGroup:
    """ A group of :py:class:`~momotor.shared.resources`.
    """
    def __init__(self, items: typing.Iterable[ResourceItem] = None):
        self._items = tuple(items) if items is not None else tuple()

    # Factories

    @classmethod
    def create(cls: typing.Type[RGT], value: typing.Union[str, typing.Iterable[str]]) -> RGT:
        return cls(ResourceItem.create(value))

    @classmethod
    def union(cls: typing.Type[RGT], *groups: RGT) -> RGT:
        """ Merge multiple resource groups into a new one """
        return cls(unique_everseen(itertools.chain(*(group.items for group in groups))))

    # Implementation

    def __len__(self):
        return len(self._items)

    @property
    def items(self) -> typing.Tuple[ResourceItem]:
        return self._items

    def match(self, worker_group: typing.Optional["ResourceGroup"]) -> typing.Optional[float]:
        """ Returns the match between this resource group and the provided worker's resource group

        :param worker_group: The worker's resource group
        :return: match value, the lower the value, the better the match is (ranges from
                 -\ :py:data:`~math.inf` to +\ :py:data:`~math.inf`)
        :raises: :py:exc:`~momotor.shared.resources.NoMatch` if there are missing or excluded tags
        """
        match = None
        unmatched = frozenset(worker_group.items) if worker_group is not None else frozenset()
        for task_resource in self.items:
            matched = set()
            for worker_resource in unmatched:
                if task_resource.comparable(worker_resource):
                    matched.add(worker_resource)
                    match = combine_item(match, task_resource.compare(worker_resource))

            # If no tag matched, but the task tag is required, it's no match
            if not matched and task_resource.required:
                raise NoMatch

            unmatched -= matched

        # process resources defined on the worker but not the task
        for worker_resource in unmatched:
            match = combine_item(match, worker_resource.compare_missing(worker_resource))

        return match

    def as_str_tuple(self) -> typing.Tuple[str]:
        return tuple(item.as_str() for item in self._items)

    def as_str(self) -> str:
        return ','.join(quote_item(item) for item in self.as_str_tuple())
