import copy
import enum
from multiprocessing.dummy import Value
from os import path
from tkinter import E

import valida.data
import valida.conditions as cnds
from valida.errors import (
    DuplicateRule,
    IncompatibleRules,
    MalformedContainerItemSpec,
    MalformedDataPathSpec,
)


def get_container_value_condition(
    condition,
    datum_condition,
    cls,
    cls_like,
    condition_label="condition",
    datum_condition_label="value",
):

    if condition is not None:
        if not isinstance(condition, cnds.ConditionLike):
            raise TypeError(
                f"If specified, `{condition_label}` must be a cnds.ConditionLike object."
            )
    else:
        condition = cnds.NullCondition()

    if datum_condition is not None:
        if not isinstance(datum_condition, cnds.NullCondition):
            if not isinstance(datum_condition, cnds.ConditionLike):
                datum_condition = cls.equal_to(datum_condition)
            if not datum_condition.is_like(cls_like):
                raise TypeError(
                    f"{datum_condition_label} must be a {cls.__name__} object."
                )
        condition = condition & datum_condition

    return condition


class Container(enum.Enum):

    CONTAINER = -1
    LIST = 0
    MAP = 1


class DataPathDatumType(enum.Enum):

    NONE = None
    DTYPE = 1
    LENGTH = 2
    MAP_KEYS = 3
    MAP_VALUES = 4


class DataPathMultiType(enum.Enum):

    NONE = None
    FIRST = 1  # Use just the first returned match
    LAST = 2  # Use just the final returned match
    SINGLE = 3  # As in FIRST, but raise/fail if more than one exists
    ALL = 4  #
    ANY = 5  #


class DataPath:
    """Class to represent a path within a nested data structure.

    A DataPath locates nodes within a nested data structure. It comprises an
    address of nested data types (mapping values or list items) that can be further
    refined using one ore more conditions. Validation rules are applied (i.e. tested) at
    the nodes identified by a ContainerPath.

    """

    DATUM_TYPE = DataPathDatumType.NONE
    MULTI_TYPE = DataPathMultiType.NONE

    def __init__(self, *parts, datum_type=None, multi_type=None, source_data=None):

        part_objs = []
        is_concrete = True
        for i in parts:
            if isinstance(i, ContainerValue):
                is_concrete = False
            else:
                if isinstance(i, (str, float)):
                    i = MapValue(i)
                elif isinstance(i, int):
                    i = MapOrListValue(key=i, index=i)  # could be either map or list
                else:
                    raise TypeError(
                        f"Cannot construct a DataPath from part of type: {type(i)}"
                    )
            part_objs.append(i)

        self.parts = tuple(part_objs)
        self.is_concrete = is_concrete
        self.source_data = source_data
        self.DATUM_TYPE = DataPathDatumType(datum_type)
        self.MULTI_TYPE = DataPathMultiType(multi_type)

    @property
    def DATUM_TYPE(self):
        return self._DATUM_TYPE

    @DATUM_TYPE.setter
    def DATUM_TYPE(self, value):
        self._DATUM_TYPE = DataPathDatumType(value)

    @property
    def MULTI_TYPE(self):
        return self._MULTI_TYPE

    @MULTI_TYPE.setter
    def MULTI_TYPE(self, value):
        multi_type = DataPathMultiType(value)
        if self.is_concrete and multi_type.value:
            raise ValueError(
                f"{self!r} has `MULTI_TYPE` set to {self.MULTI_TYPE.name!r}, but is a "
                f'"concrete" path for which there will only ever be at most a single '
                f"match. For concrete paths, `MULTI_TYPE` should not be set."
            )
        else:
            self._MULTI_TYPE = multi_type

    def __eq__(self, other):
        if (
            type(self) == type(other)
            and self.parts == other.parts
            and self.is_concrete == other.is_concrete
            and self.DATUM_TYPE == other.DATUM_TYPE
            and self.MULTI_TYPE == other.MULTI_TYPE
            and self.source_data == other.source_data
        ):
            return True
        return False

    @classmethod
    def from_spec(cls, spec):

        general_msg = (
            f'The specification key must start with "path" and optionally include, as '
            f'additional dot-delimited tokens, a `DATUM_TYPE` specifier (e.g. "path.map_keys", '
            f'"path.map_values", "path.type", "path.length") and/or a `MULTI_TYPE`'
            f' specifier (e.g. "path.single", "path.first", "path.last", '
            f'"path.all" or "path.single.map_keys" etc).'
        )

        DATUM_TYPE_MULTI_TYPE_LOOKUP = {
            "type": "dtype",
            "len": "length",
        }

        if not isinstance(spec, dict):
            raise MalformedDataPathSpec(general_msg)
        else:
            spec_key, spec_val = next(iter(spec.items()))  # single-item dict

        REPLACE = "path"
        ESC_CODE = rf"\{REPLACE}"
        is_escaped = False
        for k in list(spec.keys()):
            if ESC_CODE in k:
                is_escaped = True
                spec_val = spec.pop(k)
                k_new = k.replace(ESC_CODE, REPLACE)
                spec[k_new] = spec_val
        if is_escaped:
            return spec

        if len(spec) > 1:
            raise MalformedDataPathSpec(
                f"A data path should be specified with exactly one "
                f"specification key (but found keys: {list(spec.keys())}). {general_msg}"
            )

        if not isinstance(spec_key, str):
            raise MalformedDataPathSpec(general_msg)

        spec_key_split = [i.lower() for i in spec_key.split(".")]
        spec_key_split_len = len(spec_key_split)

        if spec_key_split[0] != "path" or spec_key_split_len not in range(1, 4):
            raise MalformedDataPathSpec(general_msg)

        obj = cls.from_part_specs(*spec_val)

        for i in spec_key_split[1:]:
            i = DATUM_TYPE_MULTI_TYPE_LOOKUP.get(i, i)
            try:
                obj = getattr(obj, i)()
            except AttributeError:
                raise MalformedDataPathSpec(
                    f"{i} if not a known DataPath DATUM_TYPE or MULTI_TYPE. {general_msg}"
                )

        return obj

    @classmethod
    def from_part_specs(cls, *parts):
        """Construct a DataPath from parts that might include dicts, where each dict
        describes the required ContainerItem using string keys."""

        spec_resolved_parts = []
        for i in parts:
            if isinstance(i, dict):
                i = ContainerValue.from_spec(i)
            spec_resolved_parts.append(i)

        return cls(*spec_resolved_parts)

    @classmethod
    def from_str(cls, path_str, delimiter="/"):

        if path_str:
            path_str_parts = path_str.split(delimiter)
        else:
            path_str_parts = []

        path_parts = []
        for i in path_str_parts:
            try:
                i_int = int(i)  # list index (int) or map key (int or str)
                i = MapOrListValue(key=cnds.Key.in_((i, i_int)), index=i_int)
            except ValueError:
                try:
                    i_float = float(i)  # map key (float or str)
                    i = MapValue(key=cnds.Key.in_((i, i_float)))
                except ValueError:
                    pass
            path_parts.append(i)

        return cls(*path_parts)

    def __truediv__(self, other):
        """Concatenating with other MapValue, ListItem, ContainerValue or ContainerPaths."""
        if isinstance(other, ContainerValue) or other in (  # TODO: this looks wonky
            MapValue,
            ListValue,
            MapOrListValue,
        ):
            return DataPath(*self.parts, other)
        elif isinstance(other, DataPath):
            return DataPath(*self.parts, *other.parts)

    def __rtruediv__(self, other):
        return self.__class__(other) / self

    def __iter__(self):
        for i in self.parts:
            yield i

    def __len__(self):
        return len(self.parts)

    def __getitem__(self, index):
        if isinstance(index, int):
            return self.parts[index]
        elif isinstance(index, slice):
            return self.__class__(*self.parts[index])

    def __repr__(self):
        return (
            f"{self.__class__.__name__}("
            f'{", ".join(f"{i!r}" for i in self.parts)}'
            f'{", " if self.DATUM_TYPE.value and self.parts else ""}'
            f'{f"datum_type={self.DATUM_TYPE}" if self.DATUM_TYPE.value else ""}'
            f'{", " if self.MULTI_TYPE.value and self.parts else ""}'
            f'{f"multi_type={self.MULTI_TYPE}" if self.MULTI_TYPE.value else ""}'
            f")"
        )

    def _copy_with_datum_type(self, datum_type):
        if self.DATUM_TYPE.value:
            raise ValueError(f"{self.__class__.__name__} DATUM_TYPE is already set.")
        obj = copy.copy(self)
        obj.DATUM_TYPE = datum_type
        return obj

    def _copy_with_multi_type(self, multi_type):
        if self.MULTI_TYPE.value:
            raise ValueError(f"{self.__class__.__name__} MULTI_TYPE is already set.")
        obj = copy.copy(self)
        obj.MULTI_TYPE = multi_type
        return obj

    def dtype(self):
        return self._copy_with_datum_type(DataPathDatumType.DTYPE)

    def length(self):
        return self._copy_with_datum_type(DataPathDatumType.LENGTH)

    def map_keys(self):
        return self._copy_with_datum_type(DataPathDatumType.MAP_KEYS)

    def map_values(self):
        return self._copy_with_datum_type(DataPathDatumType.MAP_VALUES)

    def first(self):
        return self._copy_with_multi_type(DataPathMultiType.FIRST)

    def last(self):
        return self._copy_with_multi_type(DataPathMultiType.LAST)

    def single(self):
        return self._copy_with_multi_type(DataPathMultiType.SINGLE)

    def any(self):
        # TODO: how to implement?
        return self._copy_with_multi_type(DataPathMultiType.ANY)

    def all(self):
        return self._copy_with_multi_type(DataPathMultiType.ALL)

    def resolve_implicit_types(self):
        # Note: we don't support "complex mappings" from YAML where keys are themselves
        # mappings or lists
        types = []
        for i in self.parts:
            try:
                type_i = i.CONTAINER_TYPE
            except AttributeError:
                raise TypeError(f'Unknown container item type: "{type(i)}"')
            types.append(type_i)

        return types

    def _extract_specified_datum_type(self, data):
        if self.DATUM_TYPE.value:
            if self.DATUM_TYPE == DataPathDatumType.DTYPE:
                data = [type(i) for i in data]
            elif self.DATUM_TYPE == DataPathDatumType.LENGTH:
                data = [len(i) for i in data]
            elif self.DATUM_TYPE == DataPathDatumType.MAP_KEYS:
                data = [list(i.keys()) for i in data]
            elif self.DATUM_TYPE == DataPathDatumType.MAP_VALUES:
                data = [list(i.values()) for i in data]
        return data

    def _match_specified_multi_type(self, data, concrete_paths):

        if self.MULTI_TYPE.value:
            if self.MULTI_TYPE == DataPathMultiType.FIRST:
                data = data[0]
            elif self.MULTI_TYPE == DataPathMultiType.LAST:
                data = data[-1]
            elif self.MULTI_TYPE == DataPathMultiType.SINGLE:
                if len(data) > 1:
                    paths_fmt = "\n".join(
                        f"Path {idx}: {tuple(i)}"
                        for idx, i in enumerate(concrete_paths, 1)
                    )
                    raise ValueError(
                        f"{self!r} has `MULTI_TYPE` set to SINGLE, meaning there "
                        f"should be only one match, but multiple ({len(data)}) matches "
                        f"found at paths:\n{paths_fmt}."
                    )
                data = data[0]
            elif self.MULTI_TYPE == DataPathMultiType.ALL:
                pass
            # TODO: how to implement DataPathMultiType.ANY?

        elif self.is_concrete:
            # `MULTI_TYPE` will be NONE if `is_concrete`
            data = data[0]

        return data

    def get_data(self, data=None, return_paths=False):
        """Get the data specified by this path."""

        if self.source_data:
            data = self.source_data
        elif not data:
            raise ValueError("Specify the `data` from which to get sub-data.")

        if not self.parts:
            if isinstance(data, valida.data.Data):
                data = data.original
            data = self._extract_specified_datum_type([data])[0]
            if return_paths:
                return (data, ())  # if no parts, also concrete so just return one item
            else:
                return data

        data = [data]
        concrete_paths = []

        for part_idx, part in enumerate(self.parts):

            new_data = []
            new_concrete_paths = []
            for datum_idx, datum in enumerate(data):

                try:
                    filtered_data = part.filter(datum)
                except TypeError:
                    continue

                new_data.extend(filtered_data.data)

                if part_idx == 0:
                    new_concrete_paths = [[i] for i in filtered_data.keys]
                else:
                    new_concrete_paths += [
                        concrete_paths[datum_idx] + [i] for i in filtered_data.keys
                    ]

            concrete_paths = new_concrete_paths
            data = new_data

        if not data:
            return None if self.is_concrete else []

        # TODO: handle and re-raise if DATUM_TYPE processing ?
        # maybe this should raise, but it should be caught by Condition.filter and
        # fail the rule without raising an exception?
        data = self._extract_specified_datum_type(data)

        if return_paths:
            out = [(i, tuple(j)) for i, j in zip(data, concrete_paths)]
        else:
            out = data

        out = self._match_specified_multi_type(out, concrete_paths)

        return out


class ContainerValue:
    """Class for representing a container value (i.e. an item within either a list or a
    mapping). A container item can be filtered according to both its relationship to its
    parent container (i.e. position within the list for a list item, or key for a mapping
    item) and its value.

    """

    def __repr__(self):
        return (
            f"{self.__class__.__name__}(condition={self.condition!r}"
            f'{f", label={self.label!r}" if self.label else ""}'
            f")"
        )

    def __eq__(self, other):
        if (
            type(self) == type(other)
            and self.condition == other.condition
            and self.label == other.label
        ):
            return True
        return False

    @staticmethod
    def from_spec(spec):
        CLS_LOOKUP = {
            "map_value": MapValue,
            "list_value": ListValue,
            "map_or_list_value": MapOrListValue,
        }
        container_type = spec.pop("type", "map_or_list_value")
        try:
            cls = CLS_LOOKUP[container_type]
        except KeyError:
            raise TypeError(
                f'Container item type "{container_type}" not understood. '
                f"Allowed container items are: {list(CLS_LOOKUP.keys())!r}."
            )

        # for all types:
        condition = spec.pop("condition", None)
        if condition is not None:
            condition = cnds.ConditionLike.from_spec(condition)
        else:
            condition = cnds.NullCondition()

        # for a ContainerValue type:
        list_condition = spec.pop("list_condition", None)
        if list_condition is not None:
            list_condition = cnds.ConditionLike.from_spec(list_condition)
        else:
            list_condition = cnds.NullCondition()

        # for a ContainerValue type:
        map_condition = spec.pop("map_condition", None)
        if map_condition is not None:
            map_condition = cnds.ConditionLike.from_spec(map_condition)
        else:
            map_condition = cnds.NullCondition()

        value = spec.pop("value", None)
        if value is not None:
            new_cond = cnds.ConditionLike.from_spec(value)
            if not new_cond.is_value_like:
                raise ValueError(
                    'Conditions specified in the "value" specification '
                    "must be value-like."
                )
            condition = condition & new_cond

        # shorthand specs:
        value_short_keys = [i for i in spec if i.startswith("value.")]
        value_short_cond_specs = {i: spec.pop(i) for i in value_short_keys}
        for spec_k, spec_v in value_short_cond_specs.items():
            condition = condition & cnds.ConditionLike.from_spec({spec_k: spec_v})

        if cls == MapValue:

            # shorthand specs:
            key_short_keys = [i for i in spec if i.startswith("key.")]
            key_short_cond_specs = {i: spec.pop(i) for i in key_short_keys}
            for spec_k, spec_v in key_short_cond_specs.items():
                condition = condition & cnds.ConditionLike.from_spec({spec_k: spec_v})

            key = spec.pop("key", None)
            if key is not None:
                new_cond = cnds.ConditionLike.from_spec(key)
                if not new_cond.is_key_like:
                    raise ValueError(
                        'Conditions specified in the "key" specification '
                        "must be key-like."
                    )
                condition = condition & new_cond

        elif cls == ListValue:

            # shorthand specs:
            index_short_keys = [i for i in spec if i.startswith("index.")]
            index_short_cond_specs = {i: spec.pop(i) for i in index_short_keys}
            for spec_k, spec_v in index_short_cond_specs.items():
                condition = condition & cnds.ConditionLike.from_spec({spec_k: spec_v})

            index = spec.pop("index", None)
            if index is not None:
                new_cond = cnds.ConditionLike.from_spec(index)
                if not new_cond.is_index_like:
                    raise ValueError(
                        'Conditions specified in the "index" specification '
                        "must be index-like."
                    )
                condition = condition & new_cond

        elif cls == MapOrListValue:

            # shorthand specs:
            index_short_keys = [i for i in spec if i.startswith("index.")]
            index_short_cond_specs = {i: spec.pop(i) for i in index_short_keys}
            for spec_k, spec_v in index_short_cond_specs.items():
                list_condition = list_condition & cnds.ConditionLike.from_spec(
                    {spec_k: spec_v}
                )

            # shorthand specs:
            key_short_keys = [i for i in spec if i.startswith("key.")]
            key_short_cond_specs = {i: spec.pop(i) for i in key_short_keys}
            for spec_k, spec_v in key_short_cond_specs.items():
                map_condition = map_condition & cnds.ConditionLike.from_spec(
                    {spec_k: spec_v}
                )

            index = spec.pop("index", None)
            if index is not None:
                new_cond = cnds.ConditionLike.from_spec(index)
                if not new_cond.is_index_like:
                    raise ValueError(
                        'Conditions specified in the "index" specification '
                        "must be index-like."
                    )
                list_condition = list_condition & new_cond

            key = spec.pop("key", None)
            if key is not None:
                new_cond = cnds.ConditionLike.from_spec(key)
                if not new_cond.is_key_like:
                    raise ValueError(
                        'Conditions specified in the "key" specification '
                        "must be key-like."
                    )
                map_condition = map_condition & new_cond

        label = spec.pop("label", None)
        if spec:
            raise ValueError(
                f"Unknown arguments to container item specification: {list(spec.keys())}"
            )

        if cls == MapOrListValue:
            return cls(
                condition=condition,
                list_condition=list_condition,
                map_condition=map_condition,
                label=label,
            )
        else:
            return cls(condition=condition, label=label)

    def __truediv__(self, other):
        """Concatenating with other DictValue, ListValue or DataPath objects."""
        return DataPath(self, other)

    def __rtruediv__(self, other):
        return DataPath(other) / self

    def filter(self, data):
        return self.condition.filter(data)


class MapValue(ContainerValue):

    CONTAINER_TYPE = Container.MAP

    def __init__(self, key=None, value=None, condition=None, label=None):

        condition = get_container_value_condition(
            condition,
            key,
            cnds.Key,
            cnds.KeyLike,
            datum_condition_label="key",
        )
        condition = get_container_value_condition(
            condition,
            value,
            cnds.Value,
            cnds.ValueLike,
        )
        self.condition = condition
        self.label = label


class ListValue(ContainerValue):

    CONTAINER_TYPE = Container.LIST

    def __init__(self, index=None, value=None, condition=None, label=None):

        condition = get_container_value_condition(
            condition,
            index,
            cnds.Index,
            cnds.IndexLike,
            datum_condition_label="index",
        )
        condition = get_container_value_condition(
            condition,
            value,
            cnds.Value,
            cnds.ValueLike,
        )
        self.condition = condition
        self.label = label


class MapOrListValue(ContainerValue):
    """To represent a value within a Map or a List."""

    CONTAINER_TYPE = Container.CONTAINER

    def __init__(
        self,
        key=None,
        index=None,
        value=None,
        list_condition=None,
        map_condition=None,
        condition=None,
        label=None,
    ):

        list_condition = get_container_value_condition(
            list_condition,
            index,
            cnds.Index,
            cnds.IndexLike,
            "lst_condition",
            "index",
        )
        map_condition = get_container_value_condition(
            map_condition,
            key,
            cnds.Key,
            cnds.KeyLike,
            "map_condition",
            "key",
        )
        condition = get_container_value_condition(
            condition,
            value,
            cnds.Value,
            cnds.ValueLike,
        )

        self.condition = condition
        self.list_condition = list_condition
        self.map_condition = map_condition
        self.label = label

    def __repr__(self):
        return (
            f"{self.__class__.__name__}(condition={self.condition!r}"
            f" list_condition={self.list_condition!r}, map_condition={self.map_condition!r}"
            f'{f", label={self.label!r}" if self.label else ""}'
            f")"
        )

    def filter(self, data):
        try:
            if data.is_list:
                condition = self.list_condition & self.condition
            else:
                condition = self.map_condition & self.condition

        except AttributeError:

            if isinstance(data, list):
                condition = self.list_condition & self.condition
            elif isinstance(data, dict):
                condition = self.map_condition & self.condition
            else:
                raise RuntimeError(
                    f"Datum type ({type(data)!r}) is not a list or dict: {data!r}"
                )
        return condition.filter(data)


def resolve_implicit_types(path):

    types = []
    for i in path:

        # Note: we don't support "complex mappings" from YAML where keys are themselves
        # mappings or lists
        try:
            type_i = i.CONTAINER_TYPE
        except AttributeError:
            raise TypeError(f'Unknown container item type: "{type(i)}"')

        types.append(type_i)

    return types


def validate_rule_paths(rules):

    seen_paths = []
    predicted_types = {}
    for r_idx, r in enumerate(rules):
        r_path = r["path"]
        if r_path in seen_paths:
            msg = f"Rule index {r_idx} shares with another rule the path: {r_path}"
            raise DuplicateRule(msg)
        else:
            seen_paths.append(r_path)
            # print(f'r_path: {r_path!r} is not in seen_paths:\n{seen_paths!r}\n')
        r_types = resolve_implicit_types(r_path)

        # print(f'predicted_types: {predicted_types}')

        for path_end_idx in range(len(r_path)):
            partial_path = r_path[0:path_end_idx]
            partial_path_str = f"{partial_path!r}"
            # print(path_end_idx, partial_path)
            if partial_path_str in predicted_types:
                predicted_types[partial_path_str]["rules"].append(r_idx)
                predicted_types[partial_path_str]["types"].append(r_types[path_end_idx])
            else:
                predicted_types[partial_path_str] = {
                    "rules": [r_idx],
                    "types": [r_types[path_end_idx]],
                }

    # Identify type, where possible, for each node
    for path, types_info in predicted_types.items():

        uniq_types = set(types_info["types"])

        if len(uniq_types) == 1:
            actual_type = list(uniq_types)[0]

        elif Container.LIST in uniq_types and Container.MAP in uniq_types:
            path_rules = [(i, rules[i]["path"]) for i in types_info["rules"]]
            # print(path_rules)
            path_rules_fmt = "\n\t" + "\n\t".join(
                f"Rule index {i[0]}: {i[1]!r}" for i in path_rules
            )
            msg = (
                f"Incompatible rules specified for path {path}; at least one rule "
                f"implies this node is a mapping, but at least one other rule implies "
                f"this node is a list. Associated rule paths are: {path_rules_fmt}"
            )
            raise IncompatibleRules(msg)

        elif Container.CONTAINER in uniq_types:

            if Container.LIST in uniq_types:
                actual_type = Container.LIST

            elif Container.MAP in uniq_types:
                actual_type = Container.MAP

        else:
            raise RuntimeError("Unique container types not understood.")

        predicted_types[path] = actual_type

    return predicted_types
