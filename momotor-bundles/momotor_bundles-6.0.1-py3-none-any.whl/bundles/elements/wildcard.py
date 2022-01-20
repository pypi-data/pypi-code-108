import collections.abc
import typing

from momotor.bundles.utils.arguments import BundleConstructionArguments, BundleFactoryArguments
from momotor.bundles.utils.immutable import ImmutableOrderedDict

try:
    from typing import final
except ImportError:
    from typing_extensions import final

__all__ = ['WildcardAttrsMixin']


CT = typing.TypeVar('CT', bound=object)


class WildcardAttrsMixin(typing.Generic[CT]):
    __unset: typing.ClassVar = object()
    _attrs: ImmutableOrderedDict[str, str] = __unset

    @final
    @property
    def attrs(self) -> ImmutableOrderedDict[str, str]:
        """ Wildcard attributes """
        assert self._attrs is not self.__unset, "Uninitialized attribute `attrs`"
        return self._attrs

    @attrs.setter
    def attrs(self, attrs: typing.Optional[typing.Mapping[str, str]]):
        assert self._attrs is self.__unset, "Immutable attribute `attrs`"
        if attrs:
            assert isinstance(attrs, collections.abc.Mapping)
            self._attrs = ImmutableOrderedDict(attrs)
        else:
            self._attrs = ImmutableOrderedDict()

    def _create_attrs_from_node(self, node: CT, *, args: BundleFactoryArguments):
        self._attrs = ImmutableOrderedDict(node.any_attributes)

    def _construct_attrs(self, node: CT, *, args: BundleConstructionArguments) -> CT:
        if self.attrs:
            attrs = {}
            if node.any_attributes:
                attrs.update(self.attrs)
                attrs.update(node.any_attributes)

            node.any_attributes = attrs

        return node
