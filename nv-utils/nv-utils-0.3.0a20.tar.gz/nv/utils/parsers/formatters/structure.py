from collections.abc import Mapping
from enum import IntFlag
from functools import partial
from typing import Any, Callable, MutableSet, Tuple, Set, Type

from ..core import (build_parsing_map, build_parser_from_map, as_element_parser,
                    remove_none_objects, remove_empty_strings, remove_empty_collections, UnknownParser,
                    InternalParser)

from .string import StringFormatter, MissingKeyBehaviour

__ALL__ = ['StructureFormatter', 'format_structure', 'partial_format_structure',
           'partital_format_structure_with_tracker', ]


class _CleanUp:
    class Behaviour(IntFlag):
        NO_CLEANUP = 0
        NONE = 1
        EMPTY_STRING = 2
        EMPTY_COLLECTIONS = 4
        EMPTY = 6
        ALL = 255

    @classmethod
    def cleanup(cls, obj: Any, behaviour: Behaviour = Behaviour.ALL) -> Any | None:
        if behaviour & cls.Behaviour.NONE:
            obj = remove_none_objects(obj)
        if behaviour & cls.Behaviour.EMPTY_STRING:
            obj = remove_empty_strings(obj)
        if behaviour & cls.Behaviour.EMPTY_COLLECTIONS:
            obj = remove_empty_collections(obj)
        return obj


class StructureFormatter:
    BASIC_ELEMENTS = (str, )
    CleanUp = _CleanUp
    MissingKey = StringFormatter.MissingKey

    def __init__(self,
                 # StringFormatter behaviour
                 missing_key: Type[MissingKeyBehaviour] = MissingKey.Behaviour.Raise,
                 parse_defaults: bool = True,
                 # Tracking options
                 track: bool = False,
                 missing_keys_set: MutableSet[str] | None = None,
                 used_keys_set: MutableSet[str] | None = None,
                 # Structure parsing settings
                 clean_up: CleanUp.Behaviour = CleanUp.Behaviour.EMPTY,
                 format_keys: bool = False,
                 # Parser settings
                 unknown_parser: UnknownParser.Behaviour = UnknownParser.Behaviour.IGNORE,
                 parser_replacement: Any | Callable[[Any], Any | None] | None = UnknownParser.DEFAULT,
                 default_parser: InternalParser | None = None,
                 **parser_kwargs: Any,
                 ):

        self._string_formatter = StringFormatter(
            behaviour=missing_key,
            parse_defaults=parse_defaults,
            track=track,
            missing_keys_set=missing_keys_set,
            used_keys_set=used_keys_set)

        # Parser
        parsing_map = build_parsing_map(element_parser=as_element_parser(self._string_formatter.vformat, ()),
                                        elements=self.BASIC_ELEMENTS)

        self._format = build_parser_from_map(parsing_map,
                                             behaviour=unknown_parser,
                                             replacement=parser_replacement,
                                             wrapper=partial(StructureFormatter.CleanUp.cleanup, behaviour=clean_up),
                                             default_parser=default_parser,
                                             parse_keys=format_keys,
                                             **parser_kwargs,
                                             )

    def format(self, obj: Any, mapping: Any) -> Any:
        return self._format(obj, (), mapping)

    @property
    def track(self):
        return self._string_formatter.track

    @property
    def missing_keys(self):
        return self._string_formatter.missing_keys

    @property
    def used_keys(self):
        return self._string_formatter.used_keys

    def clear_missing_keys(self):
        self._string_formatter.clear_missing_keys()

    def clear_used_keys(self):
        self._string_formatter.clear_used_keys()


def format_structure(obj: Any,
                     mapping: Mapping[str, str | None],
                     missing_key: Type[MissingKeyBehaviour] = StructureFormatter.MissingKey.Behaviour.Raise,
                     parse_defaults: bool = True,
                     missing_keys_set: MutableSet[str] | None = None,
                     used_keys_set: MutableSet[str] | None = None,
                     clean_up: StructureFormatter.CleanUp.Behaviour = StructureFormatter.CleanUp.Behaviour.EMPTY,
                     format_keys: bool = False,
                     ):

    formatter = StructureFormatter(missing_key=missing_key,
                                   parse_defaults=parse_defaults,
                                   missing_keys_set=missing_keys_set,
                                   used_keys_set=used_keys_set,
                                   clean_up=clean_up,
                                   format_keys=format_keys,
                                   )
    return formatter.format(obj, mapping)


def partial_format_structure(obj: Any,
                             mapping: Mapping[str, str | None],
                             parse_defaults: bool = True,
                             missing_keys_set: MutableSet[str] | None = None,
                             used_keys_set: MutableSet[str] | None = None,
                             clean_up: StructureFormatter.CleanUp.Behaviour = StructureFormatter.CleanUp.Behaviour.EMPTY,
                             format_keys: bool = False,
                             ):

    formatter = StructureFormatter(missing_key= StructureFormatter.MissingKey.Behaviour.ReturnPlaceholder,
                                   parse_defaults=parse_defaults,
                                   missing_keys_set=missing_keys_set,
                                   used_keys_set=used_keys_set,
                                   clean_up=clean_up,
                                   format_keys=format_keys,
                                   )
    return formatter.format(obj, mapping)


def partial_format_structure_with_tracking(obj: Any,
                                           mapping: Mapping[str, str | None],
                                           parse_defaults: bool = True,
                                           clean_up: StructureFormatter.CleanUp.Behaviour = StructureFormatter.CleanUp.Behaviour.EMPTY,
                                           format_keys: bool = False,
                                           ) -> Tuple[str, Set[str], Set[str]]:

    formatter = StructureFormatter(missing_key=StructureFormatter.MissingKey.Behaviour.ReturnPlaceholder,
                                   track=True,
                                   parse_defaults=parse_defaults,
                                   clean_up=clean_up,
                                   format_keys=format_keys,
                                   )

    return formatter.format(obj, mapping), formatter.missing_keys, formatter.used_keys
