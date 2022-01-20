from collections.abc import Mapping, Iterator
import string, _string
from typing import Sequence, Any, MutableSet, Type, Tuple, Set

from nv.utils.typing import Missing

MISSING = Missing()


__ALL__ = ['StringFormatter', 'format_string', 'partial_format_string', 'format_string_with_tracking',  ]


class MissingKeyBehaviour:
    def __init__(self, key: str,
                 original_key: str = '',
                 default: str = '',
                 conversion: str | None = None,
                 format_spec: str = '',
                 args: Sequence[Any] = None,
                 kwargs: Mapping[str, Any] = None):
        self.key = key
        self.original_key = original_key or ''
        self.default = default or ''
        self.conversion = conversion
        self.format_spec = format_spec or ''
        self.args = args
        self.kwargs = kwargs

    def unwrap(self) -> Any:
        pass

    def __getitem__(self, item):
        self.key = f'{self.key}[{item}]'
        return self

    def __getattr__(self, item):
        self.key = f'{self.key}.{item}'
        return self

    def __bool__(self):
        return False

    def __repr__(self):
        return f'{self.__class__.__name__}({self.key})'

    def __str__(self):
        return f'missing key: {self.key} in {self.original_key}'


class StringFormatter(string.Formatter):

    class MissingKey:
        class Behaviour:
            class Raise(MissingKeyBehaviour):
                def unwrap(self) -> Any:
                    raise KeyError(f"{self.key} not found")

            class ReturnNone(MissingKeyBehaviour):
                def unwrap(self) -> Any:
                    return None

            class ReturnEmptyString(MissingKeyBehaviour):
                def unwrap(self) -> Any:
                    return ''

            class ReturnPlaceholder(MissingKeyBehaviour):
                def unwrap(self) -> Any:
                    default = f'|{self.default}' if self.default else ''
                    conversion = f'!{self.conversion}' if self.conversion else ''
                    format_spec = f':{self.format_spec}' if self.format_spec else ''
                    return f'{{{self.original_key or self.key}{default}{conversion}{format_spec}}}'

    def __init__(self,
                 *args,
                 behaviour: Type[MissingKeyBehaviour] = MissingKey.Behaviour.Raise,
                 parse_defaults: bool = True,
                 track: bool = False,
                 missing_keys_set: MutableSet[str] = None,
                 used_keys_set: MutableSet[str] = None,
                 **kwargs):
        super().__init__(*args, **kwargs)

        # Parsing behaviours
        self.behaviour = behaviour
        self.parse_defaults = parse_defaults

        # Trackers
        if track or missing_keys_set is not None or used_keys_set is not None:
            self._track = True
            self._missing_keys = missing_keys_set or set()
            self._used_keys = used_keys_set or set()
        else:
            self._track = False

    @property
    def track(self):
        return self._track

    @property
    def missing_keys(self):
        if self._track:
            return self._missing_keys
        raise AttributeError(f'{self.__class__.__name__} has not been initialized with track=True')

    @property
    def used_keys(self):
        if self._track:
            return self._used_keys
        raise AttributeError(f'{self.__class__.__name__} has not been initialized with track=True')

    def clear_missing_keys(self):
        if self._track:
            self._missing_keys.clear()
        raise AttributeError(f'{self.__class__.__name__} has not been initialized with track=True')

    def clear_used_keys(self):
        if self._track:
            self._missing_keys.clear()
        raise AttributeError(f'{self.__class__.__name__} has not been initialized with track=True')

    def check_unused_args(self, used_args: Sequence[int | str],
                          args: Sequence[Any], kwargs: Mapping[str, Any]) -> None:
        # This function is supposed to raise error if there are unused args at super() level
        pass

    def get_value(self, key: int | str, args: Sequence[Any], kwargs: Mapping[str, Any]) -> Any:
        try:
            return super().get_value(key, args, kwargs)
        except KeyError:
            return self.behaviour(key, args=args, kwargs=kwargs)

    def _get_field_rest(self, obj, rest, tracking):
        # Adapted from Python's original implementation of get_fields
        for is_attr, i in rest:
            if is_attr:
                obj = getattr(obj, i, MISSING)
                tracking = f'{tracking}.{i}'
            else:
                obj = obj.get(i, MISSING)
                tracking = f'{tracking}[{i}]'

            if obj is MISSING:
                return self.behaviour(key=tracking)

        return obj

    def get_field(self, field_name, args, kwargs):
        # Extracts default from field_name
        field_name, *default = field_name.split('|', 1)
        default = default[0] if default else None

        # Original implementation adapted
        first, rest = _string.formatter_field_name_split(field_name)

        obj = self.get_value(first, args, kwargs)

        if not isinstance(obj, MissingKeyBehaviour):
            # Root object was found, let's trace the rest of attrs or dict items
            obj = self._get_field_rest(obj, rest, first)

        if isinstance(obj, MissingKeyBehaviour):
            print(f'Failed parsing! {self.parse_defaults=} {default=}')
            # Handles either a missing root object or a missing nested object or dictionary item
            obj.original_key = field_name
            obj.default = default
            obj.args = args
            obj.kwargs = kwargs

            if self.track:
                self._missing_keys.add(obj.key)

            if self.parse_defaults and default is not None:
                # Will re-run the process with the default (which may require formatting)
                obj = self.vformat(default, args, kwargs)
        else:
            if self.track:
                self._used_keys.add(field_name)

        return obj, first

    def format_field(self, value: Any, format_spec) -> str:
        if format_spec.startswith('default='):
            return format_spec[8:]

        if isinstance(value, MissingKeyBehaviour):
            value.format_spec = format_spec
            # Execute the missing key behaviour (after the very last resource)
            return value.unwrap()

        return super().format_field(value, format_spec)

    def convert_field(self, value: Any, conversion) -> Any:
        if isinstance(conversion, MissingKeyBehaviour):
            value.conversion = conversion
            return value

        return super().convert_field(value, conversion)


def format_string(fmt_string: str,
                  mapping: Mapping[str, str | None],
                  missing_key: Type[MissingKeyBehaviour] = StringFormatter.MissingKey.Behaviour.Raise,
                  parse_defaults: bool = True,
                  missing_keys_set: MutableSet[str] | None = None,
                  used_keys_set: MutableSet[str] | None = None,
                  ) -> str:
    _formatter = StringFormatter(behaviour=missing_key,
                                 parse_defaults=parse_defaults,
                                 missing_keys_set=missing_keys_set,
                                 used_keys_set=used_keys_set)
    return _formatter.vformat(fmt_string, (), mapping)


def partial_format_string(fmt_string: str,
                          mapping: Mapping[str, str | None],
                          parse_defaults: bool = True,
                          missing_keys_set: MutableSet[str] | None = None,
                          used_keys_set: MutableSet[str] | None = None,
                          ) -> str:
    _formatter = StringFormatter(behaviour=StringFormatter.MissingKey.Behaviour.ReturnPlaceholder,
                                 parse_defaults=parse_defaults,
                                 missing_keys_set=missing_keys_set,
                                 used_keys_set=used_keys_set)
    return _formatter.vformat(fmt_string, (), mapping)


def partial_format_string_with_tracking(fmt_string: str,
                                        mapping: Mapping[str, str | None],
                                        parse_defaults: bool = True,
                                        ) -> Tuple[str, Set[str], Set[str]]:
    _formatter = StringFormatter(behaviour=StringFormatter.MissingKey.Behaviour.ReturnPlaceholder,
                                 parse_defaults=parse_defaults,
                                 track=True)
    return _formatter.vformat(fmt_string, (), mapping), _formatter.missing_keys, _formatter.used_keys
