import dataclasses

import collections
import typing
from dataclasses import dataclass

from momotor.bundles import RecipeBundle, ConfigBundle, ProductBundle, ResultsBundle
from momotor.bundles.elements.files import FilesMixin, File
from momotor.bundles.elements.options import OptionsMixin, Option
from momotor.bundles.elements.properties import PropertiesMixin, Property
from momotor.bundles.elements.result import Outcome, Result
from momotor.bundles.elements.steps import Step
from momotor.bundles.utils.domain import merge_domains
from momotor.bundles.utils.text import smart_split
from momotor.options.parser.consts import VALUE_ATTR, REFERENCE_RE, REF_OPTION_RE
from momotor.options.parser.modifier import parse_mod, apply_combiner_modifier
from momotor.options.providers import Providers
from momotor.options.result_query import result_query_fn
from momotor.options.task_id import StepTaskId


ProviderElement = typing.Union[RecipeBundle, ConfigBundle, ProductBundle, Step, Result]
ValueElement = typing.Union[Property, File, Option, Result]


@dataclass(frozen=True)
class Reference:
    """ A reference
    """
    #: The ``provider`` of the references
    provider: typing.Optional[str]

    #: The ``id`` of the reference
    id: typing.Optional[str]

    #: The ``name`` of the reference, including the class or domain parts
    name: typing.Optional[str]

    #: The original string from which this reference was parsed (used in exceptions)
    _source: str


@dataclass(frozen=True)
class ReferenceMatch:
    """ A reference match
    """

    #: The provider containing the elements referenced
    provider: ProviderElement

    #: A tuple with the referenced elements
    values: typing.Tuple[ValueElement]


def _split_reference(reference: str) -> typing.Tuple[typing.Optional[str], typing.Optional[str], str]:
    """ Split a :ref:`reference` into its string parts.

    :param reference: the reference to parse
    :return: a 3-tuple containing
             the :token:`~reference:type`,
             a string with the options between ``[]``, and
             a string with the rest of the string remaining after parsing.

    >>> _split_reference("type")
    ('type', None, '')

    >>> _split_reference("type rest")
    ('type', None, ' rest')

    >>> _split_reference("type[]")
    ('type', '', '')

    >>> _split_reference("type []")
    ('type', '', '')

    >>> _split_reference("type[ ]")
    ('type', '', '')

    >>> _split_reference("type[] rest")
    ('type', '', ' rest')

    >>> _split_reference("type[option]")
    ('type', 'option', '')

    >>> _split_reference("type [option]")
    ('type', 'option', '')

    >>> _split_reference("type [ option ]")
    ('type', 'option', '')

    >>> _split_reference("type[option] ")
    ('type', 'option', ' ')

    :param reference:
    :return:
    """
    m_ref = REFERENCE_RE.match(reference)
    if m_ref is None:
        return None, None, reference

    type_ = m_ref.group('type')
    ref_option = m_ref.group('opt')
    if ref_option:
        ref_option = ref_option[1:-1].strip()

    remainder = reference[m_ref.end(m_ref.lastindex):]

    return type_, ref_option, remainder


def _split_options(ref_option: str) -> typing.Tuple[typing.Tuple[Reference], str]:
    """ Split the options of a reference (the part between ``[]``)

    :param ref_option: the reference options to parse
    :return: a 3-tuple containing
             the :token:`~reference:provider`,
             a tuple of :py:class:`Reference` objects, and
             a string with the rest of the string remaining after parsing.

    Examples: (not all of these variants make sense, but the syntax is legal)

    >>> _split_options('')
    ((Reference(provider=None, id=None, name=None, _source=''),), '')

    >>> _split_options('@provider')
    ((Reference(provider='provider', id=None, name=None, _source='@provider'),), '')

    >>> _split_options('@provider#id')
    ((Reference(provider='provider', id='id', name=None, _source='@provider#id'),), '')

    >>> _split_options('@provider:class#name')
    ((Reference(provider='provider', id=None, name='class#name', _source='@provider:class#name'),), '')

    >>> _split_options('@provider:name')
    ((Reference(provider='provider', id=None, name='name', _source='@provider:name'),), '')

    >>> _split_options('@provider#id:class#name')
    ((Reference(provider='provider', id='id', name='class#name', _source='@provider#id:class#name'),), '')

    >>> _split_options('@provider#id:name')
    ((Reference(provider='provider', id='id', name='name', _source='@provider#id:name'),), '')

    >>> _split_options('@provider #id, id2 : class#name')
    ((Reference(provider='provider', id='id, id2', name='class#name', _source='@provider #id, id2 : class#name'),), '')

    >>> _split_options('#id')
    ((Reference(provider=None, id='id', name=None, _source='#id'),), '')

    >>> _split_options('#id:name')
    ((Reference(provider=None, id='id', name='name', _source='#id:name'),), '')

    >>> _split_options('#id:class#name')
    ((Reference(provider=None, id='id', name='class#name', _source='#id:class#name'),), '')

    >>> _split_options(':name')
    ((Reference(provider=None, id=None, name='name', _source=':name'),), '')

    >>> _split_options(':class#name')
    ((Reference(provider=None, id=None, name='class#name', _source=':class#name'),), '')

    >>> _split_options('#id, id2')
    ((Reference(provider=None, id='id, id2', name=None, _source='#id, id2'),), '')

    >>> _split_options('@provider1#id1:name1,@provider2#id2:name2')
    ((Reference(provider='provider1', id='id1', name='name1', _source='@provider1#id1:name1'), Reference(provider='provider2', id='id2', name='name2', _source='@provider2#id2:name2')), '')

    >>> _split_options('@provider#id,id2:class#name,#id3')
    ((Reference(provider='provider', id='id,id2', name='class#name', _source='@provider#id,id2:class#name'), Reference(provider=None, id='id3', name=None, _source='#id3')), '')

    >>> _split_options('@provider#id,id2:class#name,:class2#name2')
    ((Reference(provider='provider', id='id,id2', name='class#name', _source='@provider#id,id2:class#name'), Reference(provider=None, id=None, name='class2#name2', _source=':class2#name2')), '')

    >>> _split_options('no-provider')
    ((Reference(provider=None, id=None, name=None, _source=''),), 'no-provider')

    :param ref_option:
    :return:
    """
    # m_provider = PROVIDER_RE.match(ref_option)
    #
    # provider = m_provider.group('provider')
    # if provider:
    #     remaining = ref_option[m_provider.end(m_provider.lastindex):]
    # else:
    #     remaining = ref_option

    remaining = ref_option or ''
    refs: typing.MutableSequence[Reference] = collections.deque()
    any_options = False
    while remaining.strip():
        m_ref = REF_OPTION_RE.match(remaining)
        if not m_ref:
            break

        provider = m_ref.group('provider') or None
        ids = m_ref.group('ids') or None
        name = m_ref.group('name') or None
        if provider or ids or name:
            any_options = True
            end_pos = m_ref.end(m_ref.lastindex)
            source, remaining = remaining[:end_pos].strip(), remaining[end_pos:].lstrip()

            refs.append(
                Reference(provider, ids, name, source)
            )

        if remaining.startswith(','):
            remaining = remaining[1:]
        else:
            break

    if not refs and not any_options:
        refs.append(
            Reference(provider=None, id=None, name=None, _source='')
        )

    return tuple(refs), remaining


def parse_reference(reference: str) -> typing.Tuple[str, typing.Tuple[Reference], str]:
    """ Parse a :ref:`reference <reference>` into its parts.

    :param reference: the reference to parse
    :return: a 3-tuple containing
             the :token:`~reference:type`,
             a tuple of :py:class:`Reference` objects, and
             a string with the rest of the `reference` string remaining after parsing.
    :raises ValueError: the reference cannot be parsed

    Examples:

    >>> parse_reference("type")
    ('type', (Reference(provider=None, id=None, name=None, _source=''),), '')

    >>> parse_reference("type rest")
    ('type', (Reference(provider=None, id=None, name=None, _source=''),), ' rest')

    >>> parse_reference("type[] rest")
    ('type', (Reference(provider=None, id=None, name=None, _source=''),), ' rest')

    >>> parse_reference("type[@provider] rest")
    ('type', (Reference(provider='provider', id=None, name=None, _source='@provider'),), ' rest')

    >>> parse_reference("type[@provider#id:class#name] rest")
    ('type', (Reference(provider='provider', id='id', name='class#name', _source='@provider#id:class#name'),), ' rest')

    >>> parse_reference("type[@provider#id,id2:class#name] rest")
    ('type', (Reference(provider='provider', id='id,id2', name='class#name', _source='@provider#id,id2:class#name'),), ' rest')

    """
    type_, ref_option, remainder = _split_reference(reference)

    refs, ref_remainder = _split_options(ref_option)
    if ref_remainder and ref_remainder.strip():
        raise ValueError(f"Invalid reference {reference.strip()}")

    return type_, refs, remainder


# def _resolve_id_references(objects: typing.Mapping, refs: typing.Sequence[Reference]) \
#         -> typing.Generator[typing.Tuple[typing.Any, typing.Optional[Reference]], None, None]:
#
#     if not refs:
#         for obj in objects.values():
#             yield obj, None
#
#     for ref in refs:
#         if ref.id:
#             try:
#                 yield objects[ref.id], ref
#             except KeyError:
#                 pass
#         else:
#             for result in objects.values():
#                 yield result, ref


def _split_name_class(nc: str) -> typing.Tuple[typing.Optional[str], typing.Optional[str]]:
    """
    Split a name/class reference into its parts.

    >>> _split_name_class('class')
    ('class', None)

    >>> _split_name_class('#name')
    (None, 'name')

    >>> _split_name_class('class#name')
    ('class', 'name')

    >>> _split_name_class('class#"name"')
    ('class', '"name"')

    >>> _split_name_class('class#*.txt')
    ('class', '*.txt')

    >>> _split_name_class('class#"spaced name.txt"')
    ('class', '"spaced name.txt"')

    >>> _split_name_class('class#"name"123' + "'test'")
    ('class', '"name"123\\'test\\'')

    >>> _split_name_class('#"noclass#name"')
    (None, '"noclass#name"')

    >>> _split_name_class('#"spaced name.txt"')
    (None, '"spaced name.txt"')

    :param nc:
    :return:
    """
    parts = list(smart_split(nc))

    if parts and '#' in parts[0] and parts[0][0] not in {'"', "'"}:
        class_, rest = parts[0].split('#', 1)
        if rest:
            parts[0] = rest
        else:
            parts.pop(0)

        name = ''.join(parts)

    else:
        class_ = ''.join(parts)
        name = None

    if not class_:
        class_ = None

    return class_, name


def _split_name_domain(nd: str) -> typing.Tuple[str, typing.Optional[str]]:
    """ Split name/domain reference into its parts

    >>> _split_name_domain('name')
    ('name', None)

    >>> _split_name_domain('name@domain')
    ('name', 'domain')

    """

    if '@' in nd:
        name, domain = nd.split('@', 1)
    else:
        name, domain = nd, None

    return name, domain


def _match_result_reference(type_: str, objects: typing.Iterable[typing.Tuple[Result, Reference]]) \
        -> typing.Generator[ReferenceMatch, None, None]:
    """ A generator to generate :py:class:`ReferenceMatch` objects for result and outcome references

    :param type_: The :token:`~reference:type`
    :param objects:
    :raises ValueError: the reference is invalid
    """

    if type_ == 'result':
        _test = lambda obj: True

    elif type_.startswith('not-'):
        try:
            outcome = Outcome(type_[4:])
        except ValueError:
            raise ValueError(f"Invalid type {type_}")

        _test = lambda obj: obj.outcome_enum != outcome

    else:
        try:
            outcome = Outcome(type_)
        except ValueError:
            raise ValueError(f"Invalid type {type_}")

        _test = lambda obj: obj.outcome_enum == outcome

    for obj, ref in objects:
        if ref and ref.name:
            # noinspection PyProtectedMember
            raise ValueError(
                f"{ref._source!r} is not valid: name or class not allowed"
            )

        result = (obj,) if _test(obj) else tuple()
        yield ReferenceMatch(obj, result)


def _match_prop_reference(objects: typing.Iterable[typing.Tuple[typing.Union[ProviderElement, PropertiesMixin], Reference]]) \
        -> typing.Generator[ReferenceMatch, None, None]:

    for obj, ref in objects:
        if ref is None:
            raise ValueError("a name is required")
        elif ref.name is None:
            # noinspection PyProtectedMember
            raise ValueError(
                f"{ref._source!r} is not valid: a name is required"
            )

        properties = obj.properties.filter(name=ref.name)
        yield ReferenceMatch(obj, properties)


def _match_file_reference(objects: typing.Iterable[typing.Tuple[typing.Union[ProviderElement, FilesMixin], Reference]]) \
        -> typing.Generator[ReferenceMatch, None, None]:

    for obj, ref in objects:
        files = obj.files
        if ref and ref.name:
            class_, name = _split_name_class(ref.name)

            filters = {}
            if name:
                filters['name__glob'] = name
            if class_:
                filters['class_'] = class_

            files = files.filter(**filters)

        yield ReferenceMatch(obj, files)


def _match_opt_reference(
        objects: typing.Iterable[typing.Tuple[typing.Union[ProviderElement, OptionsMixin], Reference]]
) -> typing.Generator[ReferenceMatch, None, None]:

    for obj, ref in objects:
        if ref is None:
            raise ValueError("a name is required")
        elif ref.name is None:
            # noinspection PyProtectedMember
            raise ValueError(
                f"{ref._source!r} is not valid: a name is required"
            )

        name, domain = _split_name_domain(ref.name)

        options = obj.options.filter(name=name, domain=merge_domains(domain, Option.DEFAULT_DOMAIN))
        yield ReferenceMatch(obj, options)


DEFAULT_VALID_PROVIDERS = {
    None: ('result', {'result'}),
    'prop': ('result', {'result'}),
    'file': (None, None),
    'opt': (None, None),
}


def _get_bundle_objects(type_: str, refs: typing.Sequence[Reference], bundles: Providers) \
        -> typing.Generator[typing.Tuple[ProviderElement, Reference], None, None]:
    if type_ in DEFAULT_VALID_PROVIDERS:
        default_provider, valid_providers = DEFAULT_VALID_PROVIDERS[type_]
    else:
        default_provider, valid_providers = DEFAULT_VALID_PROVIDERS[None]

    for ref in refs:
        provider = ref.provider or default_provider
        if provider is None:
            raise ValueError(f"no provider")

        if valid_providers is not None and provider not in valid_providers:
            raise ValueError(f"invalid provider {provider!r}")

        if provider == 'recipe' and bundles.recipe:
            if ref.id:
                raise ValueError('`id` not allowed for @recipe provider')

            yield bundles.recipe, ref

        elif provider == 'config' and bundles.config:
            if ref.id:
                raise ValueError('`id` not allowed for @config provider')

            yield bundles.config, ref

        elif provider == 'product' and bundles.product:
            if ref.id:
                raise ValueError('`id` not allowed for @product provider')

            yield bundles.product, ref

        elif provider == 'step' and bundles.recipe and bundles.task_id:
            if ref.id:
                raise ValueError('`id` not allowed for @step provider')

            try:
                step = bundles.recipe.steps[bundles.task_id.step_id]
            except KeyError:
                raise ValueError(f"invalid provider {provider!r} for task {bundles.task_id!s}")

            yield step, ref

        elif provider == 'result' and bundles.results:
            query_fn = result_query_fn(ref.id or '**', bundles.task_id)
            for result in bundles.results.results.values():
                if query_fn(result):
                    yield result, ref

        else:
            raise ValueError(f"invalid provider {provider!r}")


def generate_reference(type_: str, refs: typing.Sequence[Reference], bundles: Providers) \
        -> typing.Generator[ReferenceMatch, None, None]:

    """ A generator producing reference matches.

    Each :py:class:`ReferenceMatch` object generated is a single reference resolved.

    :param type_: The reference :token:`~reference:type`
    :param refs: The reference options
    :param bundles: The bundles to resolve the references too
    """
    objects = _get_bundle_objects(type_, refs, bundles)

    if type_ == 'prop':
        yield from _match_prop_reference(objects)

    elif type_ == 'file':
        yield from _match_file_reference(objects)

    elif type_ == 'opt':
        yield from _match_opt_reference(objects)

    else:
        yield from _match_result_reference(type_, objects)


def select_by_reference(reference: str, bundles: Providers) \
        -> typing.Tuple[typing.Optional[str], typing.Tuple[ReferenceMatch], str]:
    """ Parse a :ref:`reference <reference>` string and collect the referenced items

    :param reference: The :token:`~reference:reference` string to parse
    :param bundles: The providers providing the objects that are referenced
    :return: a 3-tuple containing
             the :token:`~reference:type`,
             a tuple of :py:class:`ReferenceMatch` objects, and
             a string with the rest of the `reference` string remaining after parsing.
    :raises ValueError: the reference cannot be parsed
    """

    type_, refs, remainder = parse_reference(reference)
    try:
        if type_:
            items = tuple(generate_reference(type_, refs, bundles))
        else:
            items = tuple()

    except ValueError as exc:
        raise ValueError(f"Invalid {type_!r} reference {reference!r}: {exc}")

    return type_, items, remainder


def select_by_prop_reference(reference: str, results: ResultsBundle = None, task_id: StepTaskId = None) \
        -> typing.Tuple[typing.Tuple[ReferenceMatch], str]:
    """ Parse a property :token:`~reference:reference` string and collect the referenced properties.

    This is similar to the ``prop[...]`` :ref:`reference syntax <reference>`,
    but does not require the ``prop`` nor the square brackets.

    :param reference: The reference to parse
    :param results: The results bundle containing the properties
    :param task_id: The task id to expand task references
    :return: a 2-tuple containing
             a tuple of :py:class:`ReferenceMatch` objects, and
             a string with the rest of the `reference` string remaining after parsing.
    """

    refs, remainder = _split_options(reference)

    try:
        objects = _get_bundle_objects('prop', refs, Providers(results=results, task_id=task_id))
    except ValueError as exc:
        raise ValueError(f"Invalid property reference {reference!r}: {exc}")

    return tuple(_match_prop_reference(objects)), remainder


def select_by_file_reference(reference: str, bundles: Providers) -> typing.Tuple[typing.Tuple[ReferenceMatch], str]:
    """ Parse a file :token:`~reference:reference` string and collect the referenced files.

    This is similar to the ``file[...]`` :ref:`reference syntax <reference>`,
    but does not require the ``file`` nor the square brackets.

    :param reference: The reference to parse
    :param bundles: The bundles to resolve the references too
    :return: a 2-tuple containing
             a tuple of :py:class:`ReferenceMatch` objects, and
             a string with the rest of the `reference` string remaining after parsing.
    """
    refs, remainder = _split_options(reference)

    try:
        objects = _get_bundle_objects('file', refs, bundles)
    except ValueError as exc:
        raise ValueError(f"Invalid file reference {reference!r}: {exc}")

    return tuple(_match_file_reference(objects)), remainder


def select_by_opt_reference(reference: str, bundles: Providers) -> typing.Tuple[typing.Tuple[ReferenceMatch], str]:
    """ Parse an option :token:`~reference:reference` string and collect the referenced options.

    This is similar to the ``opt[...]`` :ref:`reference syntax <reference>`,
    but does not require the ``opt`` nor the square brackets.

    :param reference:
    :param bundles: The bundles to resolve the references too
    :return: a 2-tuple containing
             a tuple of :py:class:`ReferenceMatch` objects, and
             a string with the rest of the `reference` string remaining after parsing.
    """
    refs, remainder = _split_options(reference)

    try:
        objects = _get_bundle_objects('opt', refs, bundles)
    except ValueError as exc:
        raise ValueError(f"Invalid option reference {reference!r}: {exc}")

    return tuple(_match_opt_reference(objects)), remainder


def resolve_reference_value(
        value_reference: str, bundles: Providers, *,
        default_mod: str = 'join'
) -> typing.Tuple[typing.Union[str, int, float, bool, None], str]:
    """ Resolve a :ref:`reference value <reference value>` string into the value

    :param value_reference: The :token:`~reference_value:value_reference`
    :param bundles: The bundles to resolve the references too
    :param default_mod: The default :token:`~reference_value:mod`
    :return: The resolved value
    """

    mod, remaining = parse_mod(value_reference)
    type_, refs, remaining = parse_reference(remaining)

    if not type_:
        return None, value_reference

    matches = tuple(
        generate_reference(type_, refs, bundles)
    )

    attr = VALUE_ATTR.get(type_, VALUE_ATTR[None])

    values = collections.deque()
    for match in matches:
        if match.values:
            values.extend(getattr(value, attr, None) for value in match.values)
        else:
            values.append(None)

    return apply_combiner_modifier(mod or default_mod, values), remaining
