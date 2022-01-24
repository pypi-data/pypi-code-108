import collections
import typing

from momotor.bundles.elements.base import Element
from momotor.options.parser.modifier import parse_mod
from momotor.options.parser.reference import parse_reference, generate_reference, Reference, ReferenceMatch
from momotor.options.parser.consts import VALUE_ATTR, OPERATIONS, OPERATIONS_WITHOUT_VALUE, CONDITION_RE
from momotor.options.providers import Providers


def parse_selector(selector: str) \
        -> typing.Tuple[
            str,
            typing.Tuple[Reference],
            typing.Optional[str],
            typing.Union[None, str, int, float],
            str
        ]:
    """ Parse a :ref:`selector <selector>` into its parts.

    :param selector: the :token:`~selector:selector` to parse
    :return: a 5-tuple containing
             the :token:`~reference:type`,
             a tuple of :py:class:`~momotor.options.parser.reference.Reference` objects,
             the `operator`,
             the `value`, and
             a string with the rest of the `selector` string remaining after parsing.
    :raises ValueError: the selector cannot be parsed

    Examples:

    >>> parse_selector('pass')
    ('pass', (Reference(provider=None, id=None, name=None, _source=''),), None, None, '')

    >>> parse_selector('prop[#test]?')
    ('prop', (Reference(provider=None, id='test', name=None, _source='#test'),), '?', None, '')

    >>> parse_selector('prop[#test]?123')
    ('prop', (Reference(provider=None, id='test', name=None, _source='#test'),), '?', None, '123')

    >>> parse_selector('prop[#test]>0')
    ('prop', (Reference(provider=None, id='test', name=None, _source='#test'),), '>', 0, '')

    >>> parse_selector('prop[#test]>1_000')
    ('prop', (Reference(provider=None, id='test', name=None, _source='#test'),), '>', 1000, '')

    >>> parse_selector('prop[#test]>1.5')
    ('prop', (Reference(provider=None, id='test', name=None, _source='#test'),), '>', 1.5, '')

    >>> parse_selector('prop[#test]>-2')
    ('prop', (Reference(provider=None, id='test', name=None, _source='#test'),), '>', -2, '')

    >>> parse_selector('prop[#test]>-2e2')
    ('prop', (Reference(provider=None, id='test', name=None, _source='#test'),), '>', -200.0, '')

    >>> parse_selector('prop[#test]>2e-2')
    ('prop', (Reference(provider=None, id='test', name=None, _source='#test'),), '>', 0.02, '')

    >>> parse_selector('prop[#test]=="test string"')
    ('prop', (Reference(provider=None, id='test', name=None, _source='#test'),), '==', 'test string', '')

    >>> parse_selector('prop[#test]>0 123')
    ('prop', (Reference(provider=None, id='test', name=None, _source='#test'),), '>', 0, ' 123')

    :return:
    """
    type_, refs, remainder = parse_reference(selector)
    if not type_:
        # A selector without reference makes no sense
        raise ValueError(f"Invalid selector {selector!r}")

    m_oper_value = CONDITION_RE.match(remainder)

    if m_oper_value:
        oper = m_oper_value.group('oper')
        value = m_oper_value.group('value')
    else:
        oper, value = None, None

    if oper or value:
        remainder = remainder[m_oper_value.end(m_oper_value.lastindex):]

    if oper:
        assert oper in OPERATIONS.keys()
    else:
        oper = None

    if value == '' or value is None:
        if oper not in OPERATIONS_WITHOUT_VALUE:
            raise ValueError(f"Invalid selector {selector!r} (operator {oper!r} requires a value)")

        value = None

    elif oper not in OPERATIONS_WITHOUT_VALUE:
        if value.startswith("'"):
            assert value.endswith("'")
            value = value[1:-1]
        elif value.startswith('"'):
            assert value.endswith('"')
            value = value[1:-1]
        elif '.' in value or 'e' in value:
            value = float(value)
        else:
            value = int(value)

    elif value:
        # The operator does not expect a value, so it's part of the remainder
        remainder = value + remainder
        value = None

    return type_, refs, oper, value, remainder


def resolve_selector(selector: str, bundles: Providers) \
        -> typing.Tuple[
            str,
            typing.Iterable[ReferenceMatch],
            typing.Callable,
            typing.Union[None, str, int, float],
            str
        ]:
    """ Resolve all parts of a :ref:`selector <selector>`

    :param selector: the :token:`~selector:selector` to parse
    :param bundles: The bundles to resolve the references too
    :return: A 5-tuple containing
             the attribute to get the reference value from (based on :token:`~reference:type`),
             an iterator for :py:class:`~momotor.options.parser.reference.ReferenceMatch` objects,
             the `operator`,
             the `value`, and
             a string with the rest of the `selector` string remaining after parsing.
    :raises ValueError: if the selector is not valid
    """

    type_, refs, oper, value, remainder = parse_selector(selector)

    try:
        matches = generate_reference(type_, refs, bundles)
    except ValueError as exc:
        raise ValueError(f"Invalid {type_!r} selector {selector!r}: {exc}")

    attr = VALUE_ATTR.get(type_, VALUE_ATTR[None])
    oper = OPERATIONS.get(oper)

    return attr, matches, oper, value, remainder


def filter_by_selector(selector: str, bundles: Providers) -> typing.Tuple[typing.Tuple[Element], str]:
    """ Filter the elements selected by :ref:`selector <selector>` from the bundles

    :param selector: the :token:`~selector:selector` to parse
    :param bundles: The bundles to resolve the references too
    :return: a 2-tuple containing
             a tuple with the selected elements, and
             a string with the rest of the `selector` string remaining after parsing.
    :raises ValueError: if the selector is not valid
    """
    attr, matches, oper, value, remainder = resolve_selector(selector, bundles)

    results: typing.MutableSequence[Element] = collections.deque()
    for match in matches:
        obj_values = [getattr(mv, attr, None) for mv in match.values]
        for obj_value in obj_values:
            if oper(obj_value, value):
                results.append(match.provider)
                break

    return tuple(results), remainder


def match_by_selector(selector: str, bundles: Providers, *, default_mod: str = 'all') -> typing.Tuple[bool, str]:
    """ Match the elements selected by :ref:`match selector <match>` from the bundles

    :param selector: the :token:`~match:match` selector to parse
    :param bundles: The bundles to resolve the references too
    :param default_mod: Default 'mod'
    :return: a 2-tuple containing
             a boolean indicating if there was a match, and
             a string with the rest of the `selector` string remaining after parsing.
    :raises ValueError: if the selector is not valid
    """
    mod, selector = parse_mod(selector)

    if not mod:
        mod = default_mod

    attr, matches, oper, value, remainder = resolve_selector(selector, bundles)

    def _match_all() -> bool:
        matched_any = False
        for match in matches:
            obj_values = [getattr(mv, attr, None) for mv in match.values]
            if obj_values:
                matched_any = True
            else:
                return False

            for obj_value in obj_values:
                if not oper(obj_value, value):
                    return False

        return matched_any

    def _match_any() -> bool:
        for match in matches:
            obj_values = [getattr(mv, attr, None) for mv in match.values]
            for obj_value in obj_values:
                if oper(obj_value, value):
                    return True

        return False

    if mod == 'all':
        result = _match_all()
    elif mod == 'any':
        result = _match_any()
    elif mod == 'notall':
        result = not _match_all()
    elif mod in {'not', 'notany'}:
        result = not _match_any()
    else:
        raise ValueError(f"Invalid modifier {mod!r} for selector {selector!r}")

    return result, remainder
