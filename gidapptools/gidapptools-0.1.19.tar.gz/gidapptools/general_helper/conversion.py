# * Standard Library Imports ---------------------------------------------------------------------------->
import re
from enum import Flag, auto
from typing import Any, Union, ClassVar, Iterable
from datetime import timedelta
from operator import neg, or_, pos
from functools import reduce, total_ordering, cached_property
from collections import defaultdict

# * Third Party Imports --------------------------------------------------------------------------------->
import attr
import inflect
import pyparsing as pp
import pyparsing.common as ppc
from sortedcontainers import SortedList

# * Gid Imports ----------------------------------------------------------------------------------------->
from gidapptools.general_helper.deprecation import deprecated_argument

NANOSECONDS_IN_SECOND: int = 1_000_000_000


RAW_STRING_TRUE_VALUES = {'yes',
                          'y',
                          '1',
                          'true',
                          '+'}

RAW_STRING_FALSE_VALUES = {'no',
                           'n',
                           '0',
                           'false',
                           '-'}


STRING_TRUE_VALUES = {str(value).casefold() for value in RAW_STRING_TRUE_VALUES}

STRING_FALSE_VALUES = {str(value).casefold() for value in RAW_STRING_FALSE_VALUES}


@total_ordering
class FileSizeUnit:

    def __init__(self, short_name: str, long_name: str, factor: int, aliases: Iterable[str] = None) -> None:
        self._short_name = short_name
        self._long_name = long_name
        self.factor = factor
        self.aliases = [] if aliases is None else aliases
        self.aliases += self._get_default_aliases()
        self.all_names = self._get_names()
        self.all_names_casefolded = {name.casefold() for name in self.all_names}

    @cached_property
    def short_name(self) -> str:
        return f"{self._short_name}b"

    @cached_property
    def long_name(self) -> str:
        return f"{self._long_name}bytes"

    def _get_names(self) -> set[str]:
        all_names = [self.short_name, self.long_name] + self.aliases
        all_names += [name.removesuffix('s') for name in all_names]
        all_names += [name + 's' for name in all_names if not name.endswith('s')]
        return set(all_names)

    def _get_default_aliases(self) -> Iterable[str]:
        _out = []

        _out.append(f"{self._long_name} bytes")

        return _out

    def __eq__(self, o: object) -> bool:
        if isinstance(o, self.__class__):
            return self.factor == o.factor

        if isinstance(o, int):
            return self.factor == o

        if isinstance(o, str):
            return o in {self.short_name, self.long_name}.union(set(self.aliases))

        return NotImplemented

    def __lt__(self, o: object) -> bool:
        if isinstance(o, self.__class__):
            return self.factor < o.factor
        if isinstance(o, int):
            return self.factor < o

        return NotImplemented

    def __truediv__(self, o: object) -> float:
        if isinstance(o, self.__class__):
            return self.factor / o.factor
        if isinstance(o, int):
            return self.factor / o

        if isinstance(o, float):
            return float(self.factor) / o
        return NotImplemented

    def __rtruediv__(self, o: object) -> float:
        if isinstance(o, self.__class__):
            return o.factor / self.factor
        if isinstance(o, int):
            return o / self.factor

        if isinstance(o, float):
            return o / float(self.factor)

        return NotImplemented

    def __str__(self) -> str:
        return self.short_name


class FileSizeByte(FileSizeUnit):
    # pylint: disable=super-init-not-called
    def __init__(self) -> None:
        self.short_name = 'b'
        self.long_name = 'bytes'
        self.factor = 1
        self.aliases = []
        self.all_names = self._get_names()
        self.all_names_casefolded = {name.casefold() for name in self.all_names}


class FileSizeReference:

    def __init__(self) -> None:
        self.byte_unit = FileSizeByte()
        self.units: tuple[FileSizeUnit] = None
        self._make_units()

    def _make_units(self) -> None:
        self.units = []
        symbol_data = [('K', 'Kilo'),
                       ('M', 'Mega'),
                       ('G', 'Giga'),
                       ('T', 'Tera'),
                       ('P', 'Peta'),
                       ('E', 'Exa'),
                       ('Z', 'Zetta'),
                       ('Y', 'Yotta')]
        temp_unit_info = {s: 1 << (i + 1) * 10 for i, s in enumerate(symbol_data)}
        for key, value in temp_unit_info.items():
            self.units.append(FileSizeUnit(short_name=key[0], long_name=key[1], factor=value))
        self.units = tuple(sorted(self.units))

    @property
    def symbols(self) -> tuple[str]:
        return tuple(item.short_name for item in self.units)

    @property
    def long_names(self) -> tuple[str]:
        return tuple(item.long_name for item in self.units)

    def get_unit_by_name(self, name: str, case_insensitive: bool = True) -> FileSizeUnit:
        try:
            all_names = [unit for unit in self.units if name in unit.all_names_casefolded]
            return all_names[0]
        except IndexError as error:
            if name in self.byte_unit.all_names_casefolded:
                return self.byte_unit
            raise KeyError(name) from error


FILE_SIZE_REFERENCE = FileSizeReference()


@deprecated_argument(arg_name='annotate')
def bytes2human(n: int, annotate: bool = True) -> str:
    # http://code.activestate.com/recipes/578019
    # >>> bytes2human(10000)
    # '9.8K'
    # >>> bytes2human(100001221)
    # '95.4M'
    # if annotate is not None:

    # symbols = ('Kb', 'Mb', 'Gb', 'Tb', 'Pb', 'Eb', 'Zb', 'Yb')
    # prefix = {s: 1 << (i + 1) * 10 for i, s in enumerate(symbols)}

    for unit in reversed(FILE_SIZE_REFERENCE.units):
        if n >= unit:
            _out = float(n) / unit

            _out = f'{_out:.1f} {unit}'
            return _out
    _out = n

    return f"{_out} b"


def human2bytes(in_text: str, strict: bool = False) -> int:
    def _clean_name(name: str) -> str:
        name = name.strip()
        name = name.casefold()
        name = white_space_regex.sub(' ', name)
        return name
    if in_text.strip() == "0" and strict is False:
        return ""
    white_space_regex = re.compile(r"\s{2,}")
    number_regex_pattern = r"(?P<number>[\d\.\,]+)"
    name_regex_pattern = r"(?P<name>\w([\w\s]+)?)"
    parse_regex = re.compile(number_regex_pattern + r'\s*' + name_regex_pattern)

    match = parse_regex.match(in_text.strip())
    if match:
        number = float(match.group('number'))
        name = _clean_name(match.group('name'))
        unit = FILE_SIZE_REFERENCE.get_unit_by_name(name)
        return int(number * unit.factor)
    else:
        # TODO: custom error
        raise RuntimeError(f"Unable to parse input string {in_text!r}.")


def ns_to_s(nano_seconds: int, decimal_places: int = None) -> Union[int, float]:
    seconds = nano_seconds / NANOSECONDS_IN_SECOND
    if decimal_places is None:
        return seconds
    return round(seconds, decimal_places)


@attr.s(auto_attribs=True, auto_detect=True, frozen=True)
class TimeUnit:
    inflect_engine: ClassVar[inflect.engine] = inflect.engine()
    name: str = attr.ib()
    symbol: str = attr.ib()
    factor: int = attr.ib()
    aliases: tuple[str] = attr.ib(default=tuple(), converter=tuple)

    @property
    def plural(self):
        return self.inflect_engine.plural_noun(self.name)

    def convert_seconds(self, in_seconds: int) -> int:
        return in_seconds / self.factor

    def convert_with_rest(self, in_seconds: int) -> tuple[int, int]:
        _amount, _rest = divmod(in_seconds, self.factor)

        return int(_amount), _rest

    def value_to_string(self, in_value: int, use_symbols: bool = False) -> str:
        if use_symbols is True:
            return f"{in_value}{self.symbol}"
        if in_value == 1:
            return f"{in_value} {self.name}"
        return f"{in_value} {self.plural}"


TIMEUNITS = [TimeUnit(*item) for item in [('nanosecond', 'ns', 1 / NANOSECONDS_IN_SECOND), ("microsecond", "us", (1 / 1000) / 1000, ["mi", "mis", "mü", "müs", "μs"]), ('millisecond', 'ms', 1 / 1000), ('second', 's', 1, ["sec"]),
                                          ('minute', 'm', 60, ["min", "mins"]), ('hour', 'h', 60 * 60), ('day', 'd', 60 * 60 * 24), ('week', 'w', 60 * 60 * 24 * 7), ("year", "y", (60 * 60 * 24 * 7 * 52) + (60 * 60 * 24))]]
TIMEUNITS = sorted(TIMEUNITS, key=lambda x: x.factor, reverse=True)


class TimeUnits:

    def __init__(self, with_year: bool = True) -> None:
        self._units = SortedList(TIMEUNITS.copy(), key=lambda x: -x.factor)
        self.with_year = with_year

    @cached_property
    def smallest_unit(self) -> TimeUnit:
        return self.units[-1]

    @cached_property
    def name_dict(self) -> dict[str, TimeUnit]:
        return {item.name.casefold(): item for item in self.units} | {item.plural.casefold(): item for item in self.units}

    @cached_property
    def symbol_dict(self) -> dict[str, TimeUnit]:
        return {item.symbol.casefold(): item for item in self.units}

    @cached_property
    def alias_dict(self) -> dict[str, TimeUnit]:
        _out = {}
        for item in self.units:
            for alias in item.aliases:
                _out[alias.casefold()] = item
        return _out

    @cached_property
    def full_dict(self) -> dict[str, TimeUnit]:
        return self.name_dict | self.symbol_dict | self.alias_dict

    def __getitem__(self, key: Union[int, str]) -> TimeUnit:
        if isinstance(key, int):
            return self.units[key]

        return self.full_dict[key]

    @property
    def units(self):
        if self.with_year is False:
            return [u for u in self._units.copy() if u.name != 'year']
        return self._units.copy()

    def __iter__(self):
        return iter(self.units)


def seconds2human(in_seconds: Union[int, float, timedelta], as_list_result: bool = False, as_symbols: bool = False, with_year: bool = True, min_unit: str = None) -> Union[dict[TimeUnit, int], str]:

    rest = in_seconds.total_seconds() if isinstance(in_seconds, timedelta) else in_seconds
    sign = ""
    if rest < 0:
        print(f"it is {in_seconds=}")
        rest = abs(rest)
        sign = "-"
    result = {}

    _time_units = TimeUnits(with_year=with_year)

    if min_unit is None:
        sub_min_units = set()
    else:
        min_unit = _time_units[min_unit.casefold()]
        sub_min_units = {unit for unit in _time_units if unit.factor < min_unit.factor}

    for unit in _time_units:
        amount, rest = unit.convert_with_rest(rest)
        if amount:
            result[unit] = int(amount)
    if as_list_result is True:
        return {k: v for k, v in result.items() if k not in sub_min_units}
    results = [k.value_to_string(v, as_symbols) for k, v in result.items() if k not in sub_min_units]

    if not results:
        _unit = _time_units.smallest_unit if min_unit is None else min_unit
        _name = f" {_unit.plural}" if as_symbols is False else _unit.symbol
        return f"0{_name}"
    if len(results) > 1:
        return sign + ' '.join(results[:-1]) + ' and ' + results[-1]
    return sign + results[0]


class TimedeltaConversionModifiers(Flag):
    POSITIVE = auto()
    NEGATIVE = auto()

    @property
    def sign(self):
        if self.__class__.NEGATIVE in self and self.__class__.POSITIVE in self:
            raise ValueError("Parsed timedelta can not have positive and negative modifiers at the same time.")
        if self.__class__.NEGATIVE in self:
            return neg

        return pos


def get_timedelta_parsing_grammar() -> pp.ParserElement:

    possible_time_units = []
    _time_units = TimeUnits(with_year=True)

    def _time_data_action(in_token: pp.ParseResults) -> dict[TimeUnit, int]:
        _out = defaultdict(int)

        for item in in_token:
            key = item[1]
            value = item[0]
            if key == _time_units['y']:
                value = value * key.factor
                key = _time_units['s']
            elif key == _time_units['ns']:
                value = value * key.factor
                key = _time_units['s']

            _out[key] += value

        return dict(_out)

    for unit in _time_units:
        possible_time_units.append(unit.name)
        possible_time_units.append(unit.symbol)
        possible_time_units.append(unit.plural)
        possible_time_units += list(unit.aliases)

    possible_time_units = pp.one_of(possible_time_units, caseless=True).set_parse_action(lambda x: _time_units[x[0]])

    combine_words = pp.one_of(["and", ",", ":", ";"], caseless=True).suppress()
    time_item = pp.Group(ppc.integer + possible_time_units)
    prefixes = pp.Keyword("in", caseless=True).set_parse_action(lambda: TimedeltaConversionModifiers.POSITIVE) | pp.Keyword("since", caseless=True).set_parse_action(
        lambda: TimedeltaConversionModifiers.NEGATIVE) | pp.Literal('-').set_parse_action(lambda: TimedeltaConversionModifiers.NEGATIVE)

    postfixes = pp.Keyword("ago", caseless=True).set_parse_action(lambda: TimedeltaConversionModifiers.NEGATIVE)

    return pp.ZeroOrMore(prefixes)("prefix") + pp.OneOrMore(time_item + pp.Optional(combine_words))('time_data').set_parse_action(_time_data_action) + pp.ZeroOrMore(postfixes)("postfix")


TIMEDELTA_PARSING_GRAMMAR = get_timedelta_parsing_grammar()


def human2timedelta(in_text: str, default: Any = timedelta()) -> timedelta:
    try:
        tokens = TIMEDELTA_PARSING_GRAMMAR.parse_string(in_text, parse_all=True).as_dict()
    except pp.ParseBaseException:
        return default
    _raw_modifier_data = tokens.get("prefix") + tokens.get('postfix')
    if _raw_modifier_data == []:
        _raw_modifier_data = [TimedeltaConversionModifiers.POSITIVE]
    modifiers = reduce(or_, {i for i in _raw_modifier_data if i})

    raw_timedelta_kwargs = {k.plural: v for k, v in tokens.get('time_data').items() if v}

    raw_timedelta = timedelta(**raw_timedelta_kwargs)
    return modifiers.sign(raw_timedelta)


def str_to_bool(in_string: str, strict: bool = False) -> bool:
    if isinstance(in_string, bool):
        return in_string
    mod_string = in_string.casefold().strip()
    if strict is False:
        return mod_string in STRING_TRUE_VALUES

    if mod_string in STRING_TRUE_VALUES:
        return True
    if mod_string in STRING_FALSE_VALUES:
        return False

    raise TypeError(f'Unable to convert string {in_string!r} to a Boolean value.')


if __name__ == '__main__':
    import pp
    pp(TIMEUNITS)
