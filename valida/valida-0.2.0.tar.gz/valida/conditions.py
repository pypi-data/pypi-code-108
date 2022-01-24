import enum
import operator
from subprocess import call
import warnings


import valida.data
import valida.datapath
from valida import callables as call_funcs
from valida.errors import (
    InvalidCallable,
    MalformedConditionLikeSpec,
    MalformedDataPathSpec,
)
from valida.utils import (
    classproperty,
    get_func_args_by_kind,
    null_condition_binary_check,
)


class PreparedConditionCallable:
    def __init__(self, func, *args, **kwargs):
        self._func = func
        self._args = args
        self._kwargs = kwargs

    def __call__(self, trial_datum, source_data=None):
        res_args, res_kwargs = self._get_resolved_data_path_args(source_data)
        return self.func(trial_datum, *res_args, **res_kwargs)

    def _get_resolved_data_path_args(self, source_data):
        if not source_data:
            return self.args, self.kwargs

        resolved_args = []
        for arg in self.args:
            if isinstance(arg, valida.datapath.DataPath):
                arg = arg.get_data(source_data, return_paths=False)
            resolved_args.append(arg)

        resolved_kwargs = {}
        for k, v in self.kwargs.items():
            if isinstance(v, valida.datapath.DataPath):
                v = v.get_data(source_data, return_paths=False)
            resolved_kwargs[k] = v

        return tuple(resolved_args), resolved_kwargs

    @property
    def func(self):
        return self._func

    @property
    def name(self):
        return self.func.__name__

    @property
    def args(self):
        return self._args

    @property
    def kwargs(self):
        return self._kwargs


class GeneralCallables:
    @classmethod
    def equal_to(cls, value):
        return cls(call_funcs.equal_to, value=value)

    @classmethod
    def not_equal_to(cls, value):
        return cls(call_funcs.not_equal_to, value=value)

    @classmethod
    def less_than(cls, value):
        return cls(call_funcs.less_than, value=value)

    @classmethod
    def greater_than(cls, value):
        return cls(call_funcs.greater_than, value=value)

    @classmethod
    def less_than_or_equal_to(cls, value):
        return cls(call_funcs.less_than_or_equal_to, value=value)

    @classmethod
    def greater_than_or_equal_to(cls, value):
        return cls(call_funcs.greater_than_or_equal_to, value=value)

    @classmethod
    def in_(cls, value):
        return cls(call_funcs.in_, value=value)

    @classmethod
    def not_in(cls, value):
        return cls(call_funcs.not_in, value=value)

    @classmethod
    def in_range(cls, lower, upper):
        return cls(call_funcs.in_range, lower=lower, upper=upper)

    @classmethod
    def not_in_range(cls, value):
        return cls(call_funcs.not_in_range, value=value)

    @classmethod
    def equal_to_approx(cls, value, tolerance=1e-8):
        return cls(call_funcs.equal_to_approx, value=value, tolerance=tolerance)

    @classmethod
    def factor_of(cls, value):
        return cls(call_funcs.factor_of, value)

    @classmethod
    def has_factor(cls, value):
        return cls(call_funcs.has_factor, value)

    @classmethod
    def truthy(cls):
        return cls(call_funcs.truthy)

    @classmethod
    def falsy(cls):
        return cls(call_funcs.falsy)

    @classmethod
    def null(cls):
        return cls(call_funcs.null)

    # Aliases for convenience:
    eq = equal_to
    lt = less_than
    gt = greater_than
    lte = less_than_or_equal_to
    gte = greater_than_or_equal_to

    OP_SYMBOL_MAP = {
        "==": equal_to,
        "<": less_than,
        ">": greater_than,
        "<=": less_than_or_equal_to,
        ">=": greater_than_or_equal_to,
    }


class MapCallables:
    @classmethod
    def keys_contain(cls, key):
        return cls(call_funcs.keys_contain, key=key)

    @classmethod
    def keys_contain_any_of(cls, *keys):
        return cls(call_funcs.keys_contain_any_of, *keys)

    @classmethod
    def keys_contain_all_of(cls, *keys):
        return cls(call_funcs.keys_contain_all_of, *keys)

    @classmethod
    def keys_contain_N_of(cls, N, keys):
        return cls(call_funcs.keys_contain_N_of, N=N, keys=keys)

    @classmethod
    def keys_contain_at_least_N_of(cls, N, keys):
        return cls(call_funcs.keys_contain_at_least_N_of, N=N, keys=keys)

    @classmethod
    def keys_contain_at_most_N_of(cls, N, keys):
        return cls(call_funcs.keys_contain_at_most_N_of, N=N, keys=keys)

    @classmethod
    def keys_contain_one_of(cls, *keys):
        return cls(call_funcs.keys_contain_one_of, *keys)

    @classmethod
    def keys_contain_at_least_one_of(cls, keys):
        return cls(call_funcs.keys_contain_at_least_one_of, keys=keys)

    @classmethod
    def keys_contain_at_most_one_of(cls, keys):
        return cls(call_funcs.keys_contain_at_most_one_of, keys=keys)

    @classmethod
    def keys_equal_to(cls, *keys):
        return cls(call_funcs.keys_equal_to, *keys)

    @classmethod
    def items_contain(cls, **items):
        return cls(call_funcs.items_contain, **items)

    @classmethod
    def allowed_keys(cls, *keys):
        return cls(call_funcs.allowed_keys, *keys)

    @classmethod
    def required_keys(cls, *keys):
        return cls(call_funcs.required_keys, *keys)

    @classmethod
    def forbidden_keys(cls, *keys):
        return cls(call_funcs.forbidden_keys, *keys)


class AllCallables(GeneralCallables, MapCallables):
    pass


class ConditionLike:
    def __or__(self, other):
        return ConditionOr(self, other)

    def __and__(self, other):
        return ConditionAnd(self, other)

    def __xor__(self, other):
        return ConditionXor(self, other)

    def is_like(self, cls):
        return all(isinstance(i, cls) for i in self.flatten()[0])

    @property
    def is_null(self):
        return isinstance(self, NullCondition)

    @property
    def is_key_like(self):
        return self.is_like(KeyLike)

    @property
    def is_index_like(self):
        return self.is_like(IndexLike)

    @property
    def is_value_like(self):
        return self.is_like(ValueLike)

    def filter(self, data, data_has_paths=False, source_data=None):
        if not isinstance(data, valida.data.Data):
            data = valida.data.Data(data)
        return self._filter(
            data, data_has_paths=data_has_paths, source_data=source_data
        )

    def test(self, datum):
        return self.filter([datum]).result[0]

    def test_all(self, data):
        return all(self.filter(data).result)

    def flatten(self):
        """Get a flattened list of all conditions."""
        all_cnds = []
        all_ops = []

        try:
            for idx, cnd_i in enumerate(self.children):
                flatten_i = cnd_i.flatten()
                all_cnds.extend(flatten_i[0])
                all_ops.extend(flatten_i[1])
                if idx == 0:
                    all_ops.append(self.FLATTEN_SYMBOL)

        except AttributeError:
            all_cnds.append(self)

        return all_cnds, all_ops

    @staticmethod
    def from_spec(spec):

        if not spec:
            return NullCondition()
        elif not isinstance(spec, dict):
            raise TypeError("`spec` must be a dict with a single item.")

        BINARY_OPS = {
            "and": ConditionAnd,
            "or": ConditionOr,
            "xor": ConditionXor,
        }
        CONDITION_DATUM_TYPES = {
            "value": Value,
            "key": Key,
            "index": Index,
        }
        CALLABLE_LOOKUP = {
            "in": "in_",
        }
        PRE_PROC_LOOKUP = {
            "type": "dtype",
            "dtype": "dtype",
            "length": "length",
            "len": "length",
        }
        DTYPE_LOOKUP = {
            "int": int,
            "float": float,
            "str": str,
            "list": list,
            "dict": dict,
            "map": dict,
            int: int,
            float: float,
            str: str,
            list: list,
            dict: dict,
        }
        ALL_PRE_PROCS = list(PRE_PROC_LOOKUP.keys())

        if len(spec) > 1:
            raise MalformedConditionLikeSpec(
                f"A condition-like should be specified with exactly one "
                f"specification key (but found keys: {list(spec.keys())}). Allowed specifications "
                f"keys are the binary operators: {list(BINARY_OPS.keys())!r}, and the "
                f"condition-specifications, which are strings that start with one of the "
                f"condition datum types: {list(CONDITION_DATUM_TYPES.keys())!r}."
            )
        else:
            spec_key, spec_val = next(iter(spec.items()))  # single-item dict

        spec_key_split = [i.lower() for i in spec_key.split(".")]
        spec_key_split_len = len(spec_key_split)

        if spec_key in BINARY_OPS:
            cls = BINARY_OPS[spec_key]

            if not isinstance(spec_val, (list, tuple)):
                raise MalformedConditionLikeSpec(
                    f"A condition binary operator must be associated with a "
                    f"*list* of condition-likes, but value is not list-like, with type "
                    f"{type(spec_val)!r}."
                )

            condition_like = NullCondition()
            for i in spec_val:
                i_obj = ConditionLike.from_spec(i)
                condition_like = cls(condition_like, i_obj)

        elif spec_key_split[0] in CONDITION_DATUM_TYPES:

            if (
                spec_key_split_len not in [2, 3]
                or spec_key_split_len == 2
                and spec_key_split[-1] in ALL_PRE_PROCS
            ):
                raise MalformedConditionLikeSpec(
                    f"Condition specification must be a dot-delimited string with either "
                    f"two tokens: <datum type>.<callable name>; or three tokens "
                    f"<datum type>.<pre-processor name>.<callable name>, but specification "
                    f"was given as: {spec_key!r}."
                )

            condition_type_str = spec_key_split[0]
            cls = CONDITION_DATUM_TYPES[condition_type_str]
            pre_proc_str = None

            if spec_key_split_len == 3:

                try:
                    pre_proc_str = spec_key_split[1]
                    pre_proc_str = PRE_PROC_LOOKUP.get(pre_proc_str, pre_proc_str)
                    if pre_proc_str == "dtype":
                        try:
                            spec_val = DTYPE_LOOKUP[
                                spec_val
                            ]  # convert strings to types
                        except KeyError:
                            raise MalformedConditionLikeSpec(
                                f"Data type {spec_val!r} is not understood. Available data "
                                f"types are: {list(DTYPE_LOOKUP.keys())!r}."
                            )

                    cls = getattr(cls, pre_proc_str)

                except AttributeError:
                    raise MalformedConditionLikeSpec(
                        f"Condition pre-processor {pre_proc_str!r} not understood. "
                        f'Available pre-processors are "length" and "type"/"dtype", but '
                        f"not all pre-processors are applicable to all condition types."
                    )
            try:
                cond_call_str = spec_key_split[-1]
                cond_call_str = CALLABLE_LOOKUP.get(cond_call_str, cond_call_str)
                cond_method = getattr(cls, cond_call_str)

            except AttributeError:
                msg = (
                    f'Condition callable "{cond_call_str}" is not known or not '
                    f'compatible with specified condition type "{condition_type_str}"'
                )
                if pre_proc_str:
                    msg += f' and condition pre-processor "{pre_proc_str}"'
                msg += "."
                raise MalformedConditionLikeSpec(msg)

            func_args = get_func_args_by_kind(cond_method)

            # Coerce arguments to `DataPath`s where specified as such:
            if isinstance(spec_val, dict):
                try:
                    spec_val = valida.datapath.DataPath.from_spec(spec_val)
                except MalformedDataPathSpec:
                    # Check values for DataPath specs:
                    for k, v in spec_val.items():
                        try:
                            spec_val[k] = valida.datapath.DataPath.from_spec(v)
                        except MalformedDataPathSpec:
                            pass
            elif isinstance(spec_val, (list, tuple)):
                # Check items for DataPath specs:
                for idx, v in enumerate(spec_val):
                    try:
                        spec_val[idx] = valida.datapath.DataPath.from_spec(v)
                    except MalformedDataPathSpec:
                        pass

            if not any(
                func_args[i]
                for i in ("POSITIONAL_OR_KEYWORD", "VAR_POSITIONAL", "VAR_KEYWORD")
            ):
                # no arguments, check value given is None and invoke:
                if spec_val is not None:
                    warnings.warn(
                        f'Condition callable "{cond_method}" takes no argument, but an '
                        f'argument was supplied: "{spec_val}". This will be ignored.'
                    )
                condition = cond_method()

            elif len(func_args["POSITIONAL_OR_KEYWORD"]) == 1 and not any(
                func_args[i] for i in ("VAR_POSITIONAL", "VAR_KEYWORD")
            ):
                # exactly one single positional-or-keyword; pass as a positional:
                condition = cond_method(spec_val)

            elif len(func_args["POSITIONAL_OR_KEYWORD"]) > 1 and not any(
                func_args[i] for i in ("VAR_POSITIONAL", "VAR_KEYWORD")
            ):
                # More than one positional-or-keyword, and no other kinds:
                if isinstance(spec_val, dict):
                    condition = cond_method(**spec_val)
                elif isinstance(spec_val, (list, tuple)):
                    condition = cond_method(*spec_val)
                else:
                    raise MalformedConditionLikeSpec(
                        f"Condition callable {cond_method} accepts multuple positional-or-"
                        f"keyword arguments, and so must be parametrised with a dict or "
                        f"list/tuple of values, but the following was supplied: {spec_val!r}"
                    )

            elif len(func_args["VAR_POSITIONAL"]) == 1 and not any(
                func_args[i] for i in ("POSITIONAL_OR_KEYWORD", "VAR_KEYWORD")
            ):
                if not isinstance(spec_val, list):
                    raise MalformedConditionLikeSpec(
                        f'Condition callable "{cond_method}" accepts a variable-positional '
                        f"argument, and so must be parametrised with a list of values, "
                        f'but the following was supplied: "{spec_val}".'
                    )
                condition = cond_method(*spec_val)

            elif len(func_args["VAR_KEYWORD"]) == 1 and not func_args["VAR_POSITIONAL"]:
                # zero or more positional-or-keyword args and a variable-keyword arg:
                if not isinstance(spec_val, dict):
                    raise MalformedConditionLikeSpec(
                        f'Condition callable "{cond_method}" accepts a variable-keyword '
                        f"argument and zero or more positional-or-keyword arguments, and "
                        f"so must be parametrised with a dict of values, but the following "
                        f'was supplied: "{spec_val}".'
                    )
                condition = cond_method(**spec_val)

            else:
                raise MalformedConditionLikeSpec(
                    f"Condition callable arguments {spec_val!r} with type {type(spec_val)} "
                    f"not allowed."
                )
            condition_like = condition

        else:
            raise MalformedConditionLikeSpec(
                f"Condition-like specification keys not understood: {list(spec.keys())}). "
                f"Allowed specifications keys are the binary operators: "
                f"{list(BINARY_OPS.keys())!r}, and the condition-specifications, which are "
                f"strings that start with one of the condition datum types: "
                f"{list(CONDITION_DATUM_TYPES.keys())!r}."
            )

        return condition_like


class Condition(ConditionLike):

    PRE_PROCESSOR = None

    def __init__(self, callable, *args, **kwargs):
        """
        Parameters
        ----------
        callable : Callable
            A callable whose first argument is the trial datum that is to be tested.
        args : tuple
            Callable positional arguments.
        kwargs : dict
            Callable keyword arguments.

        """

        self.callable = PreparedConditionCallable(callable, *args, **kwargs)

    def __repr__(self):

        out = f"{self.__class__.__name__}.{self.callable.name}"
        args = [f"{v!r}" for v in self.callable.args] + [
            f"{k}={v!r}" for k, v in self.callable.kwargs.items()
        ]
        out += "(" + ", ".join(args) + ")"

        return out

    def __eq__(self, other):
        if type(other) is type(self) and self._members() == other._members():
            return True
        return False

    def _members(self):
        """Return data used in __eq__"""
        return (
            self.callable.name,
            self.callable.args,
            self.callable.kwargs,
        )

    def _filter(self, data, data_has_paths=False, source_data=None):

        processed = []
        pre_processor_error = []
        callable_error = []
        callable_false = []
        for datum in getattr(data, self.DATUM_TYPE.value)():

            if data_has_paths:
                datum, _ = datum

            try:
                processed_i = self.PRE_PROCESSOR(datum) if self.PRE_PROCESSOR else datum
                is_valid_i = True
                pre_processor_error_i = False
            except TypeError:
                processed_i = None
                is_valid_i = False
                pre_processor_error_i = True

            callable_error_i = False
            callable_false_i = False
            if is_valid_i:

                try:
                    result_i = self.callable(processed_i, source_data=source_data)

                    if not isinstance(result_i, bool):
                        raise InvalidCallable(
                            f"Callable {self.callable} did not return a boolean."
                        )
                    if not result_i:
                        callable_false_i = True

                except (TypeError, AttributeError):
                    callable_error_i = True

            pre_processor_error.append(pre_processor_error_i)
            callable_error.append(callable_error_i)
            callable_false.append(callable_false_i)
            processed.append(processed_i)

        return valida.data.FilteredData(
            self,
            data,
            processed,
            pre_processor_error,
            callable_error,
            callable_false,
            data_has_paths=data_has_paths,
        )


class FilterDatumType(enum.Enum):

    KEYS = "keys"
    VALUES = "values"


class NullCondition(Condition):
    """Class to represent a null condition that all data satisfies."""

    DATUM_TYPE = FilterDatumType.VALUES

    def __init__(self, *args, **kwargs):
        super().__init__(call_funcs.null)

    def __repr__(self):
        return f"{self.__class__.__name__}()"


class ConditionBinaryOp(ConditionLike):
    def __new__(cls, *conditions):
        """If one of the conditions is a NullCondition, then abort object construction,
        and just return the non-null condition."""
        return null_condition_binary_check(*conditions) or super().__new__(cls)

    def __init__(self, *conditions):

        super().__init__()

        self.children = conditions

        # Nonsensical to combine key-like and index-like conditions:
        flattened_conds = self.flatten()[0]
        num_key_likes = sum(isinstance(i, KeyLike) for i in flattened_conds)
        num_index_likes = sum(isinstance(i, IndexLike) for i in flattened_conds)
        if num_key_likes > 0 and num_index_likes > 0:
            raise TypeError("Cannot combine `Key` and `Index` conditions.")

    def __repr__(self):
        return f"{self.__class__.__name__}({self.children[0]}, {self.children[1]})"

    def __eq__(self, other):
        if type(self) is type(other) and (
            (
                self.children[0] == other.children[0]
                and self.children[1] == other.children[1]
            )
            or (
                self.children[0] == other.children[1]
                and self.children[1] == other.children[0]
            )
        ):
            return True
        return False

    def _filter(self, data, binary_op, data_has_paths=False, source_data=None):

        if data_has_paths:
            # Data paths will be removed on the first child _filter:
            data_has_paths = [True, False]
        else:
            data_has_paths = [False, False]

        return binary_op(
            *(
                i._filter(data, data_has_paths[idx], source_data=source_data)
                for idx, i in enumerate(self.children)
            )
        )


class ConditionAnd(ConditionBinaryOp):
    FLATTEN_SYMBOL = "and"

    def _filter(self, data, data_has_paths=False, source_data=None):
        return super()._filter(
            data, operator.and_, data_has_paths=data_has_paths, source_data=source_data
        )


class ConditionOr(ConditionBinaryOp):
    FLATTEN_SYMBOL = "or"

    def _filter(self, data, data_has_paths=False, source_data=None):
        return super()._filter(
            data, operator.or_, data_has_paths=data_has_paths, source_data=source_data
        )


class ConditionXor(ConditionBinaryOp):
    FLATTEN_SYMBOL = "xor"

    def _filter(self, data, data_has_paths=False, source_data=None):
        return super()._filter(
            data, operator.xor, data_has_paths=data_has_paths, source_data=source_data
        )


class LengthPreProcessor:
    PRE_PROCESSOR = len


class DataTypePreProcessor:
    PRE_PROCESSOR = type


class ValueLike(Condition):
    DATUM_TYPE = FilterDatumType.VALUES


class KeyLike(Condition):
    DATUM_TYPE = FilterDatumType.KEYS

    def filter(self, data, data_has_paths=False, source_data=None):

        if (isinstance(data, valida.data.Data) and data.is_list) or not isinstance(
            data, (valida.data.Data, dict)
        ):
            raise TypeError("`Key` condition can only filter a mapping (i.e. a dict).")

        return super().filter(
            data, data_has_paths=data_has_paths, source_data=source_data
        )

    def test(self, datum):
        """For testing a single-item mapping."""
        if len(datum) != 1:
            raise TypeError("Test can only be used to test a single-item mapping.")
        return self.filter(datum).result[0]


class IndexLike(Condition):
    DATUM_TYPE = FilterDatumType.KEYS

    def filter(self, data, data_has_paths=False, source_data=None):

        if (isinstance(data, valida.data.Data) and not data.is_list) or not isinstance(
            data, (valida.data.Data, list)
        ):
            raise TypeError("`Index` condition can only filter a list.")
        return super().filter(
            data, data_has_paths=data_has_paths, source_data=source_data
        )

    def test(self, datum):
        """Not allowed, since the index of a list item is unknown to the item itself."""
        raise NotImplementedError


class Value(ValueLike, AllCallables):
    @classproperty
    def length(cls):
        return ValueLength

    @classproperty
    def dtype(cls):
        return ValueDataType


class ValueLength(LengthPreProcessor, ValueLike, GeneralCallables):
    pass


class ValueDataType(DataTypePreProcessor, ValueLike, GeneralCallables):
    pass


class Key(KeyLike, AllCallables):
    @classproperty
    def length(cls):
        return KeyLength

    @classproperty
    def dtype(cls):
        return KeyDataType


class KeyLength(LengthPreProcessor, KeyLike, GeneralCallables):
    pass


class KeyDataType(DataTypePreProcessor, KeyLike, GeneralCallables):
    pass


class Index(IndexLike, GeneralCallables):
    pass
