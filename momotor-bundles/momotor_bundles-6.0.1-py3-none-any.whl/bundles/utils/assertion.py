import typing

import momotor.bundles
import momotor.bundles.elements.base


__all__ = [
    'assert_elements_bundle',
    'assert_sequence_instanceof',
    'assert_elements_instanceof',
    'assert_mapping_instanceof',
    'assert_element_mapping_instanceof'
]

ElementsType = typing.TypeVar("ElementsType",
                              bound=typing.Optional[typing.Iterable["momotor.bundles.elements.base.Element"]])
IterableType = typing.TypeVar("IterableType", bound=typing.Optional[typing.Iterable])
MappingType = typing.TypeVar("MappingType", bound=typing.Optional[typing.Mapping])
ElementMappingType = typing.TypeVar(
    "ElementMappingType",
    bound=typing.Optional[typing.Mapping[typing.Hashable, "momotor.bundles.elements.base.Element"]]
)


def assert_elements_bundle(elements: ElementsType, bundle: "momotor.bundles.Bundle") -> ElementsType:
    """ Assert that all elements are linked the correct bundle. Returns `elements`

    :param elements: sequence of :py:class:`~momotor.bundles.elements.base.Element` objects
    :param bundle: expected bundle instance for each element
    """
    # Make this a no-op if Python is started with the -O option
    if __debug__ and elements is not None:
        for element in elements:
            assert element.bundle == bundle, \
                f"Element {element!r} is not related to the expected bundle {bundle!r} but {element.bundle!r}"

    return elements


def assert_sequence_instanceof(items: IterableType, expected_type: typing.Type) -> IterableType:
    """ Assert that all items are of the expected type. Returns `items`

    :param items: The items to test
    :param expected_type: The expected type of each item
    """
    # Make this a no-op if Python is started with the -O option
    if __debug__ and items is not None:
        for item in items:
            assert isinstance(item, expected_type), \
                f"Item {item!r} is not of the expected type {expected_type}"

    return items


# noinspection PyUnreachableCode
def assert_elements_instanceof(elements: ElementsType,
                               expected_type: typing.Type["momotor.bundles.elements.base.Element"],
                               bundle: "momotor.bundles.Bundle") -> ElementsType:
    """ Combines :py:func:`assert_elements_bundle` and :py:func:`assert_sequence_instanceof`

    :param elements: sequence of :py:class:`~momotor.bundles.elements.base.Element` objects
    :param expected_type: The expected type of each element
    :param bundle: expected bundle instance for each element
    """
    # Make this a no-op if Python is started with the -O option
    if __debug__ and elements is not None:
        for element in elements:
            assert isinstance(element, expected_type), \
                f"Element {element!r} is not of the expected type {expected_type}"
            assert element.bundle == bundle, \
                f"Element {element!r} is not related to the expected bundle {bundle!r} but {element.bundle!r}"

    return elements


def assert_mapping_instanceof(mapping: MappingType,
                              expected_key_type: typing.Type[typing.Hashable],
                              expected_value_type: typing.Type) -> MappingType:
    """ Assert that all items in the mapping have the expected key and value types. Returns `mapping`

    :param mapping: A mapping containing items to test
    :param expected_key_type: Expected type for the keys
    :param expected_value_type: Expected type for the values
    """
    # Make this a no-op if Python is started with the -O option
    if __debug__ and mapping is not None:
        for key, value in mapping.items():
            assert isinstance(key, expected_key_type), \
                f"Key {key!r} is not of the expected type {expected_key_type}"
            assert isinstance(value, expected_value_type), \
                f"Item {value!r} is not of the expected type {expected_value_type}"

    return mapping


def assert_element_mapping_instanceof(mapping: ElementMappingType,
                                      expected_key_type: typing.Type[typing.Hashable],
                                      expected_value_type: typing.Type["momotor.bundles.elements.base.Element"],
                                      bundle: "momotor.bundles.Bundle") -> ElementMappingType:
    """ Combines :py:func:`assert_elements_bundle` and :py:func:`assert_mapping_instanceof`

    :param mapping: A mapping containing items to test
    :param expected_key_type: Expected type for the keys
    :param expected_value_type: Expected type for the values
    :param bundle: expected bundle instance for each element
    """
    # Make this a no-op if Python is started with the -O option
    if __debug__ and mapping is not None:
        for key, element in mapping.items():
            assert isinstance(key, expected_key_type), \
                f"Key {key!r} is not of the expected type {expected_key_type}"
            assert isinstance(element, expected_value_type), \
                f"Element {element!r} is not of the expected type {expected_value_type}"
            assert element.bundle == bundle, \
                f"Element {element!r} is not related to the expected bundle {bundle!r} but {element.bundle!r}"

    return mapping
