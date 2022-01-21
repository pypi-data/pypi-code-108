import dataclasses
import typing
from dataclasses import dataclass

from momotor.bundles.elements.content import NoContent
from momotor.bundles.elements.options import Option, OptionsMixin
from momotor.bundles.utils.boolean import to_bool
from momotor.bundles.utils.domain import unsplit_domain
from momotor.options.providers import Providers
from momotor.options.task_id import StepTaskId
from momotor.options.types import OptionTypeLiteral, LocationLiteral, SubDomainDefinitionType

__all__ = ['OptionDefinition', 'OptionNameDomain', 'OPTION_TYPE_MAP', 'OPTION_TYPE_CAST_MAP']

OPTION_TYPE_MAP: typing.Dict[OptionTypeLiteral, typing.Type] = {
    'str': str,
    'bool': bool,
    'int': int,
    'float': float,
}

OPTION_TYPE_CAST_MAP: typing.Dict[OptionTypeLiteral, typing.Callable] = {
    **OPTION_TYPE_MAP,
    'bool': to_bool,
}

VALID_LOCATIONS = frozenset(['step', 'recipe', 'config', 'product'])

_NO_DEFAULT = object()


@dataclass(frozen=True)
class OptionNameDomain:
    name: str
    domain: str = Option.DEFAULT_DOMAIN

    def __str__(self):
        if self.domain == Option.DEFAULT_DOMAIN:
            return self.name
        else:
            return f'{self.name}@{self.domain}'


@dataclass(frozen=True)
class OptionDefinition:
    """ Definition of an option.

    Options are provided by steps, recipes, configs and products. When resolving the option to a value, these
    are inspected based on the :py:attr:`.location` attribute. Depending on the other settings like
    :py:attr:`.multiple` and :py:attr:`required` one or more option values are returned when resolving the option.
    """

    #: Name of the option. Required
    name: typing.Union[OptionNameDomain, str]

    #: Expected type of the option. Optional. If not set, the type as given by the <option> node is used
    #: as-is. Allowed values: ``str``, ``bool``, ``int`` and ``float``
    type: typing.Optional[OptionTypeLiteral] = None

    #: Documentation of the option
    doc: typing.Optional[str] = None

    #: This option is required. If the option is not defined by any of the providers, :py:meth:`.resolve` will throw a
    #: :py:exc:`ValueError` exception: Default: ``False``
    required: bool = False

    #: This option can be provided multiple times. If `True`, :py:meth:`.resolve` will return a FilterableTuple of
    #: matched options. If `False`, :py:meth:`.resolve` will return a single value, or throw a :py:exc:`ValueError`
    #: if multiple options match. Default: ``False``
    multiple: bool = False

    #: When :py:attr:`.multiple` is True, :py:meth:`.resolve` will match the first provider in :py:attr:`.location`
    #: that defines an option with the correct :py:attr:`.name` and :py:attr:`.domain`.
    #: Set :py:attr:`.all` to True to resolve all matching options of all providers listed in :py:attr:`location`.
    #: Has no effect when :py:attr:`.multiple` is False.
    all: bool = False

    #: The names and order of the providers :py:meth:`.resolve` looks for the options. Can be provided as a
    #: comma separated string, or as a sequence of strings. Required. CheckletBaseMeta provides the default.
    #: When accessing, will always be a sequence
    location: typing.Union[str, typing.Sequence[str], None] = None

    #: The domain of the option:
    #: Momotor defines the following values for :py:attr:`.domain`:
    #:
    #: * **checklet**: (Default) These options are used by checklets.
    #: * **step**: Options used for executing and scheduling the step.
    #: * **x-...**: "Experimental", or private use domains
    #:
    #: Domain names starting with **x-** can be used for private use cases. All other domain names are reserved for
    #: use by Momotor in the future.
    #:
    #: Cannot have a subdomain. Required (but can be provided through the `name` argument)
    domain: typing.Optional[str] = None

    #: The default value if the option is not provided by any provider.
    default: typing.Any = _NO_DEFAULT

    #: If `False` this OptionDefinition will be disabled (i.e. ignored as if it was not listed)
    enable: bool = True

    # Cast a value into the correct type for this option
    _cast: typing.Callable[[typing.Any], typing.Any] = dataclasses.field(init=False)

    @property
    def fullname(self) -> OptionNameDomain:
        """ Full name, including domain """
        return OptionNameDomain(self.name, self.domain)

    def __post_init__(self):
        assert self.type is None or self.type in OPTION_TYPE_CAST_MAP

        # If `name` is an OptionNameDomain, split it into name and domain strings
        if isinstance(self.name, OptionNameDomain):
            assert self.domain is None
            name = self.name.name
            domain = self.name.domain
            object.__setattr__(self, 'name', name)
            object.__setattr__(self, 'domain', domain)

        if self.domain and '#' in self.domain:
            raise TypeError('domain cannot contain a subdomain')

        # Turn `location` into a tuple
        location = self.location
        if location is None:
            location_seq = None
        elif isinstance(location, str):
            location_seq = tuple(loc.strip() for loc in location.split(','))
        else:
            location_seq = tuple(location)

        assert location_seq is None or set(location_seq) <= VALID_LOCATIONS

        object.__setattr__(self, 'location', typing.cast(typing.Optional[typing.Sequence[LocationLiteral]], location_seq))

        # Create self._cast helper
        cast = OPTION_TYPE_CAST_MAP.get(self.type, lambda value: value)
        object.__setattr__(self, '_cast', cast)

        # Cast default value to correct type
        if self.default is not _NO_DEFAULT:
            object.__setattr__(self, 'default', cast(self.default))

    def resolve(
            self, providers: Providers, subdomains: typing.Union[SubDomainDefinitionType, bool] = None
    ) -> typing.Any:

        """ Resolve the value of this option by inspecting the options of the providers.

        Sub-domains to look for can be specified for each provider.
        Options including a specified sub-domain take priority over options without the sub-domain.

        If the subdomains option is not provided, a default is generated from the providers.task_id value
        if this is specified. To disable the default subdomains, set `subdomains` to `False`

        :param providers: The providers
        :param subdomains: For each provider, a sequence of subdomains to take into account when looking for
               options. Merged with :py:attr:`.domain`. Missing values and empty sequences are interpreted
               as containing ``None``. If not set or ``True``, generates subdomains based on ``providers.task_id``.
               Set to ``False`` to disable generation of subdomains.
        :return: The resolved option value. A tuple of values if :py:attr:`.multiple` is True.
        """
        if not self.enable:
            raise ValueError('Option is disabled')

        if self.domain is None:
            raise ValueError('domain not defined')

        if self.location is None:
            raise ValueError('location not defined')

        def _get_loc_domain() -> typing.Generator[typing.Tuple[OptionsMixin, str], None, None]:
            # Collect pairs of (provider, domain). In order to guarantee priority for the most-specified domains, we
            # do two loops here, one for domains with subdomains, one for domains without.
            loc: LocationLiteral

            if subdomains:
                for loc in self.location:
                    prov = getattr(providers, loc)
                    if prov is not None and loc in subdomains:
                        loc_subdomains = subdomains.get(loc)

                        if not isinstance(loc_subdomains, (list, tuple)):
                            loc_subdomains = [loc_subdomains]

                        for loc_subdomain in loc_subdomains:
                            if loc_subdomain:
                                yield prov, unsplit_domain(self.domain, loc_subdomain)

            for loc in self.location:
                prov = getattr(providers, loc)
                if prov is not None:
                    loc_subdomains = subdomains.get(loc, None) if subdomains else None
                    if not isinstance(loc_subdomains, (list, tuple)):
                        loc_subdomains = [loc_subdomains]

                    if not loc_subdomains or None in loc_subdomains or '' in loc_subdomains:
                        yield prov, self.domain

        if subdomains is None:
            # generate subdomains if `providers.task_id` is set
            subdomains = providers.task_id is not None

        if subdomains is True:
            # Generate default subdomains for 'recipe' and 'config' providers
            if providers.task_id is None:
                raise ValueError("providers.task_id must be provided to generate default subdomains")

            subdomains = self._default_subdomains(providers.task_id)

        matched = []
        for provider, domain in _get_loc_domain():
            try:
                options = provider.get_options(self.name, domain=domain)
            except KeyError:
                pass
            else:
                for option in options:
                    try:
                        matched.append(self._cast(option.value))
                    except NoContent:
                        pass

                if not self.all:
                    break

        if not matched:
            if self.required:
                raise ValueError(f"Required option '{self.fullname}' missing")
            if self.default is not _NO_DEFAULT:
                matched.append(self.default)
            elif not self.multiple:
                matched.append(None)

        return tuple(matched) if self.multiple else matched[0]

    @staticmethod
    def _default_subdomains(task_id: StepTaskId) -> SubDomainDefinitionType:
        step_id = task_id.step_id
        task_number = task_id.task_number

        subdomains = []
        while task_number:
            subdomains.append(
                str(StepTaskId(step_id, task_number))
            )
            task_number = task_number[:-1]

        subdomains.extend([step_id, None])

        return {
            'config': tuple(subdomains),
            'recipe': tuple(subdomains),
        }
