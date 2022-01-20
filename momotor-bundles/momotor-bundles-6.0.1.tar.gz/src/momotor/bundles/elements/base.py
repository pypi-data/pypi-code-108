import collections
import typing
from abc import ABC

import momotor.bundles
from momotor.bundles.exception import BundleFormatError
from momotor.bundles.utils.arguments import BundleConstructionArguments, BundleFactoryArguments

try:
    from typing import final, Final
except ImportError:
    from typing_extensions import final, Final

__all__ = ['Element', 'NestedElement']

ET = typing.TypeVar('ET', bound="Element")
CT = typing.TypeVar('CT', bound=object)
PCT = typing.TypeVar('PCT', bound=object)


class Element(typing.Generic[CT], ABC):
    """ Abstract base class for all elements of a :py:class:`~momotor.bundles.Bundle`

    :param bundle: The :py:class:`~momotor.bundles.Bundle` containing this element
    :type bundle: :py:class:`~momotor.bundles.Bundle`
    """

    #: The :py:class:`~momotor.bundles.Bundle` containing this element
    bundle: Final["momotor.bundles.Bundle"]

    def __init__(self, bundle: "momotor.bundles.Bundle"):
        from momotor.bundles.base import Bundle
        assert isinstance(bundle, Bundle)

        self.bundle = bundle

    def create(self: ET, **kwargs) -> ET:
        """ Set this element's attributes

        Usage:

        .. code-block:: python

           element = Element(bundle).create(...)

        :return: self
        """
        raise NotImplementedError

    def recreate(self: ET, target_bundle: "momotor.bundles.Bundle") -> ET:
        """ Recreate this element in a target bundle

        :param target_bundle: The target bundle
        :type target_bundle: :py:class:`~momotor.bundles.Bundle`
        """
        raise NotImplementedError

    # noinspection PyShadowingBuiltins
    @classmethod
    def recreate_list(cls: typing.Type[ET],
                      elements: typing.Optional[typing.Iterator[ET]],
                      target_bundle: "momotor.bundles.Bundle",
                      filter: typing.Callable[[ET], bool] = None) -> typing.Optional[typing.List[ET]]:
        """ Recreate a list of elements

        :param elements: List of elements to recreate (can be None)
        :param target_bundle: The target bundle
        :type target_bundle: :py:class:`~momotor.bundles.Bundle`
        :param filter: An optional callable to filter the list of elements before recreation. The callable receives
                       an element and should return a boolean
        :return: a list of elements or None if `elements` param was None
        """
        if elements is not None:
            if filter:
                return [element.recreate(target_bundle) for element in elements if filter(element)]
            else:
                return [element.recreate(target_bundle) for element in elements]

        return None

    def _create_from_node(self: ET, node: CT, *, args: BundleFactoryArguments) -> ET:
        """ Set this element's attributes from an XML dom node

        :param node: XML dom node
        :return: self
        """
        raise NotImplementedError

    def _construct_node(self, *, args: BundleConstructionArguments) -> CT:
        """ Create a complex type definition from this element """
        raise NotImplementedError

    @staticmethod
    def get_node_type() -> typing.Type[CT]:
        """ Get the xsData node type
        """
        raise NotImplementedError

    @classmethod
    def _check_node_type(cls, node, allow_none: bool = False):
        """ Check that node has the expected type. Throws :py:exc:`~momotor.bundles.BundleFormatError` if not

        :param node: The node to check
        :param allow_none: Allow node to be None
        """
        expected_type = cls.get_node_type()

        if allow_none and node is None:
            return

        if not isinstance(node, expected_type):
            raise BundleFormatError("Unexpected node type {}, expected {}"
                                    .format(node.__class__.__name__, expected_type.__name__))


def noop_preprocessor(x: str) -> str:
    return x


# noinspection PyMethodOverriding
class NestedElement(Element[CT], typing.Generic[CT, PCT], ABC):
    """ Abstract base class for an elements of a Bundle that's nested and has one or two parents, eg:

    .. code-block:: xml

       <file basename="1">
         <file name="2">
       <file>

       <file basename="3">
         <file ref="2">
       </file>

    The option in the first options list has one parent, with basename 1,
    the option in the second options list has two parents, with basenames 1 and 3

    The full name for the first option will be 1.2,
    the full name for the second option will be 1.3.2
    """
    @typing.overload
    def _create_from_node(self: ET, node: CT, direct_parent: PCT, *,
                          args: BundleFactoryArguments) -> ET:
        ...

    def _create_from_node(self: ET, node: CT, direct_parent: PCT, ref_parent: PCT = None, *,
                          args: BundleFactoryArguments) -> ET:
        """ Set this element's attributes from an XML dom node

        :param node: XML dom node
        :param direct_parent: The XML dom node's direct parent
        :param ref_parent: The XML dom node's ref parent (optional)
        :return: self
        """
        raise NotImplementedError

    # noinspection PyMethodMayBeStatic
    def _get_attr_base_parts(self, attr: str, node: CT, direct_parent: PCT, ref_parent: typing.Optional[PCT],
                             preprocess: typing.Callable[[str], str] = noop_preprocessor, *,
                             base_attr: str = None,
                             allow_base_only=False) -> typing.Optional[typing.Tuple[str, ...]]:
        parts = collections.deque()
        value = getattr(node, attr, None)
        if value is not None or allow_base_only:
            if base_attr is None:
                base_attr = f'base{attr}'

            parent_value = getattr(direct_parent, base_attr, None)
            if parent_value is not None:
                parts.append(preprocess(parent_value))

            if ref_parent:
                ref_value = getattr(ref_parent, base_attr, None)
                if ref_value is not None:
                    parts.append(preprocess(ref_value))

            if value is not None:
                parts.append(preprocess(value))

        return tuple(parts)

    @staticmethod
    def _get_parent_type() -> typing.Type[PCT]:
        """ Get the xsData node type
        """
        raise NotImplementedError

    @classmethod
    def _check_parent_type(cls, parent, allow_none: bool = False):
        """ Check that parent has the expected type. Throws :py:exc:`~momotor.bundles.BundleFormatError` if not

        :param parent: The node to check
        :param allow_none: Allow node to be None
        """
        expected_type = cls._get_parent_type()

        if allow_none and parent is None:
            return

        if not isinstance(parent, expected_type):
            raise BundleFormatError("Unexpected node type {}, expected {}"
                                    .format(parent.__class__.__name__, expected_type.__name__))
