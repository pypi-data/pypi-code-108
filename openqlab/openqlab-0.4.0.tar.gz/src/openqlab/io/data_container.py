# from __future__ import annotations # with this one can use the class as return type inside the class itself
import contextlib
import io
import json
import warnings
from io import StringIO
from typing import (
    IO,
    Any,
    Callable,
    ContextManager,
    Dict,
    List,
    Optional,
    Type,
    Union,
    cast,
    overload,
)

import numpy as np
import pandas as pd
from matplotlib.axes import Axes
from numpy import ndarray
from pandas.core.frame import DataFrame

from openqlab._typing import FilepathOrBuffer


@contextlib.contextmanager
@overload
def _open_file_or_buff(filepath_or_buffer: None, mode: str) -> ContextManager[StringIO]:
    pass  # overloaded


@contextlib.contextmanager
@overload
def _open_file_or_buff(
    filepath_or_buffer: StringIO, mode: str
) -> ContextManager[StringIO]:
    pass  # overloaded


@contextlib.contextmanager
@overload
def _open_file_or_buff(
    filepath_or_buffer: FilepathOrBuffer, mode: str
) -> ContextManager[IO]:
    pass  # overloaded


@contextlib.contextmanager  # type: ignore
def _open_file_or_buff(filepath_or_buffer, mode="r"):
    file_handler = None
    try:
        try:
            file_handler = open(  # pylint: disable=consider-using-with
                filepath_or_buffer, mode=mode, newline=""
            )
        except TypeError:
            file_handler = filepath_or_buffer
        if filepath_or_buffer is None:
            file_handler = io.StringIO()
        yield file_handler
    finally:
        try:
            file_handler.close()
        except AttributeError:
            pass


def header_wrapper(func: Callable) -> Callable:
    def wrapper(*args, **kwargs):
        header = {}
        first_arg = args[0]
        if isinstance(first_arg, DataContainer):
            header = first_arg.header
        elif isinstance(first_arg, list):
            for item in first_arg:
                if isinstance(item, DataContainer):
                    header = item.header
        for arg in args:
            header = _combine_header(header, arg)
        dataframe = func(*args, **kwargs)
        if isinstance(dataframe, pd.DataFrame):
            return DataContainer(dataframe, header=header)
        if isinstance(dataframe, pd.Series):
            return DataContainerSeries(dataframe, header=header)
        if isinstance(dataframe, type(None)):
            first_arg.header = header
            return None
        # raise TypeError("Not a DataFrame like object.")

    return wrapper


def wrapper_factory(
    func: str,
    bases: List[Type[DataFrame]],
    mro: list,
) -> Callable:
    for parent in mro:
        if func in parent.__dict__:

            @header_wrapper
            def wrapped_function(self, *args, **kwargs):
                return parent.__dict__[func](  # pylint: disable=cell-var-from-loop
                    self, *args, **kwargs
                )

            docstring = parent.__dict__[func].__doc__
            wrapped_function.__doc__ = docstring
            return wrapped_function
    raise LookupError(
        f"No function called '{func}' in original functions from {bases}. It might be deprecated."
    )


docstring_replacements = [
    ("DataFrame", "DataContainer"),
    ("dataframe", "DataContainer"),
    ("pd.DataContainer", "DataContainer"),
    ("frame's", "DataContainer's"),
    ("Series", "DataContainerSeries"),
]


def clean_docstring(docstring: Optional[str]) -> Optional[str]:
    if docstring is None:
        return None
    for original_expression, replacement_expression in docstring_replacements:
        docstring = docstring.replace(original_expression, replacement_expression)
    return docstring


class MetaDataContainer(type):
    magic_methods = [
        "__add__",
        "__sub__",
        "__mul__",
        "__floordiv__",
        "__truediv__",
        "__mod__",
        "__pow__",
        "__and__",
        "__xor__",
        "__or__",
        "__iadd__",
        "__isub__",
        "__imul__",
        "__ifloordiv__",
        "__itruediv__",
        "__imod__",
        "__ipow__",
        "__iand__",
        "__ixor__",
        "__ior__",
    ]
    # single_parameter_magic_methods = ["__neg__", "__abs__", "__invert__"]
    binary_operator = [
        "add",
        "sub",
        "mul",
        "div",
        "divide",
        "truediv",
        "floordiv",
        "mod",
        "pow",
        "dot",
        "radd",
        "rsub",
        "rmul",
        "rdiv",
        "rtruediv",
        "rfloordiv",
        "rmod",
        "rpow",
    ]
    combining = ["append", "join", "merge", "combine", "combine_first"]
    indexing = [
        "isin",
        # "where",
        # "mask",
        # "query"
    ]
    function_application = [
        "apply",
        # "applymap",
        "agg",
        "aggregate",
        "transform",
    ]

    computations = [
        "corrwith",
        # "eval"
    ]
    reindexing = [
        # "add_prefix",
        # "add_suffix",
        # "at_time",
        # "between_time",
        # "drop",
        # "drop_duplicates",
        # "filter",
        # "first",
        # "last",
        # "reindex",
        "reindex_like",
        # "rename",
        # "rename_axis",
        # "reset_index",
        # "sample",
        # "set_axis",
        # "set_index",
        # "take",
        # "truncate",
    ]
    reshaping = [
        "pivot",
        # "pivot_table",
        # "reorder_levels",
        # "sort_values",
        # "sort_index",
        # "nlargest",
        # "nsmallest",
        # "swaplevel",
        # "stack",
        # "unstack",
        # "swapaxes",
        "melt",
        # "squeeze",
        # "transpose",
    ]
    time_series = [
        # "asfreq",
        "asof",
        # "shift",
        # "slice_shift",
        # "tshift",
        # "to_period",
        # "to_timestamp",
        # "tz_convert",
        # "tz_localize",
    ]
    normal_methods = (
        binary_operator
        + combining
        + indexing
        + function_application
        + computations
        + reindexing
        + reshaping
        + time_series
    )
    functions = normal_methods + magic_methods

    def __new__(mcs, name, bases, clsdict):
        mro = {parent: None for base in bases for parent in base.mro()}.keys()
        for function_ in MetaDataContainer.functions:
            try:
                clsdict[function_] = wrapper_factory(function_, bases, mro)
            except LookupError as error:
                warnings.warn(f"{error}", Warning)
        for object_ in clsdict.values():
            if callable(object_):
                object_.__doc__ = clean_docstring(object_.__doc__)
        return super().__new__(mcs, name, bases, clsdict)


class DataContainerBase:
    _metadata = ["_header"]

    def __init__(
        self,
        *args,
        header: Optional[dict] = None,
        header_type: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self._header: dict = {}
        self.header_type = header_type
        if header:
            self.header = header

    def __repr__(self) -> str:
        header_string = ""
        for key in self.header:
            header_string += "{0} : {1}\n".format(key, self.header[key])
        maxlen = 60
        length = maxlen  # if (maxlen < len(header_string)) else len(header_string)
        string = (
            "-" * length
            + "\n"
            + header_string
            + "-" * length
            + "\n"
            + super().__repr__()
        )

        return string

    @property
    def header(self) -> dict:
        return self._header

    @header.setter
    def header(self, header: dict):
        if not isinstance(header, dict):
            raise TypeError("DataContainer.header must be a dict!")
        self._header = header

    @property
    def attrs(self) -> dict:
        return self._header

    @attrs.setter
    def attrs(self, attrs: dict):
        self._header = attrs


class DataContainerSeries(DataContainerBase, pd.Series):
    @property
    def _constructor(self):
        return DataContainerSeries

    @property
    def _constructor_expanddim(self):
        return DataContainer


class DataContainer(DataContainerBase, pd.DataFrame, metaclass=MetaDataContainer):
    """
    DataContainer inherits from pandas.DataFrame and works with header variable to store additional information
    besides plain data.
    """

    @property
    def _constructor(self):
        return DataContainer

    @property
    def _constructor_sliced(self):
        return DataContainerSeries

    general_keys = ["xUnit", "yUnit", "Date"]
    header_keys: Dict[Optional[str], List[str]] = {
        "spectrum": ["RBW", "VBW", "Span", "CenterFrequency"] + general_keys,
        "osci": general_keys,
    }
    JSON_PREFIX = "-----DataContainerHeader\n"
    JSON_SUFFIX = "-----DataContainerData\n"

    # todo: tidy up the init function and shift common code to DataContainerBase
    def __init__(
        self,
        *args,
        header: Optional[dict] = None,
        header_type: Optional[str] = None,
        type: Optional[str] = None,
        **kwargs,
    ) -> None:  # pylint: disable=redefined-builtin
        super().__init__(*args, **kwargs)

        if args:
            data = args[0]
        else:
            data = kwargs.get("data")

        if type:
            warnings.warn(
                "Argument 'type' is deprecated. Use 'header_type' instead.",
                DeprecationWarning,
            )
            if not header_type:
                header_type = type
        self.header_type = header_type

        with warnings.catch_warnings():  # pandas otherwise gives userwarning
            warnings.simplefilter("ignore")

            self._header: dict = {}
            if header:
                self.header = header
            else:
                if isinstance(data, DataContainer):
                    self.header = data.header
                elif header_type:
                    self._header_from_keys()
                else:
                    self.header = dict()

    def _ensure_type(self, obj: DataFrame) -> DataFrame:
        """Ensure that an object has same type as self.

        Used by type checkers.
        """
        assert isinstance(
            obj, (type(self), pd.DataFrame)
        ), f"{type(obj)} not a {pd.DataFrame}"
        return obj

    def _header_from_keys(self) -> None:
        try:
            self.header = dict.fromkeys(DataContainer.header_keys[self.header_type])
        except KeyError:
            raise TypeError(
                f"'{self.header_type}' is not a valid header_type for {self.__class__}."
            ) from None

    @staticmethod
    @header_wrapper
    def concat(*args, **kwargs):
        return pd.concat(*args, **kwargs)

    def update_header(self, other: dict) -> None:
        self.header = {**self.header, **other}
        empty_keys = self.emtpy_keys()
        if empty_keys:
            print(
                "Could not determine values for {0}".format(
                    "'" + ",".join(empty_keys) + "'"
                )
            )

    def emtpy_keys(self) -> List[str]:
        empty = []
        for key in self.header:
            if self.header[key] is None:
                empty.append(key)
        return empty

    @overload
    def to_csv(
        self,
        path_or_buf: FilepathOrBuffer,
        header: Union[List[str], bool] = True,
        mode: str = "w",
        **kwargs,
    ) -> None:
        pass  # overloaded

    @overload
    def to_csv(
        self,
        path_or_buf: None,
        header: Union[List[str], bool] = True,
        mode: str = "w",
        **kwargs,
    ) -> str:
        pass  # overloaded

    def to_csv(
        self, path_or_buf=None, header=True, mode="w", **kwargs
    ):  # pylint: disable=signature-differs
        with _open_file_or_buff(path_or_buf, mode=mode) as file:
            if header:
                file.write(self._header_to_json())
            super().to_csv(path_or_buf=file, header=header, **kwargs)
            if path_or_buf is None:
                return file.getvalue()
            return

    @classmethod
    def from_csv(cls, *args, **kwargs) -> "DataContainer":
        return cls.read_csv(*args, **kwargs)

    @classmethod
    def read_csv(
        cls, filepath_or_buffer: FilepathOrBuffer, *args, index_col=0, **kwargs
    ) -> "DataContainer":
        with _open_file_or_buff(filepath_or_buffer, mode="r") as file:
            header_dict = cls._json_to_header(file)
            df = pd.read_csv(file, *args, index_col=index_col, **kwargs)
            if header_dict and kwargs.get("header", "infer"):
                return DataContainer(df, header=header_dict)
            return DataContainer(df)

    @overload
    def to_json(
        self,
        filepath_or_buffer: FilepathOrBuffer,
        mode: str = "w",
        orient: Optional[str] = None,
        **kwargs,
    ) -> None:
        pass  # overloaded

    @overload
    def to_json(
        self,
        filepath_or_buffer: None,
        mode: str = "w",
        orient: Optional[str] = None,
        **kwargs,
    ) -> str:
        pass  # overloaded

    def to_json(self, filepath_or_buffer=None, mode="w", orient=None, **kwargs):
        with _open_file_or_buff(filepath_or_buffer, mode=mode) as file:
            header = kwargs.get("header", True)
            if header:
                file.write(self._header_to_json())
            super().to_json(path_or_buf=file, orient=orient, **kwargs)
            if filepath_or_buffer is None:
                return file.getvalue()

    @classmethod
    def from_json(cls, *args, **kwargs) -> "DataContainer":
        return cls.read_json(*args, **kwargs)

    @classmethod
    def read_json(
        cls, filepath_or_buffer: FilepathOrBuffer, *args, orient=None, **kwargs
    ) -> "DataContainer":
        try:
            with _open_file_or_buff(filepath_or_buffer, mode="r") as file:
                header_dict = cls._json_to_header(file)
                return DataContainer(
                    pd.read_json(file, *args, orient=orient, **kwargs),
                    header=header_dict,
                )
        except (FileNotFoundError, OSError):
            filepath_or_buffer = cast(str, filepath_or_buffer)
            if (
                filepath_or_buffer[0] == "{" and filepath_or_buffer[-1] == "}"
            ) or filepath_or_buffer.startswith(DataContainer.JSON_PREFIX):
                file = io.StringIO(filepath_or_buffer)
                header_dict = cls._json_to_header(file)
                return DataContainer(
                    pd.read_json(file, *args, orient=orient, **kwargs),
                    header=header_dict,
                )
            return DataContainer()

    def to_hdf(
        self,
        filepath_or_buffer: FilepathOrBuffer,
        key: str,
        **kwargs,  # pylint: disable=unused-argument
    ) -> None:  # pylint: disable=unused-argument
        df = pd.DataFrame(self)
        with pd.HDFStore(filepath_or_buffer) as store:
            store.put(key, df)
            store.get_storer(key).attrs.metadata = self.header

    @staticmethod
    def read_hdf(filepath_or_buffer: FilepathOrBuffer, key: str):
        with pd.HDFStore(filepath_or_buffer) as store:
            data = store.get(key)
            header = store.get_storer(key).attrs.metadata
            return DataContainer(data=data, header=header)

    @classmethod
    def from_hdf(cls, *args, **kwargs) -> "DataContainer":
        return cls.read_hdf(*args, **kwargs)

    @staticmethod
    def read_pickle(
        filepath_or_buffer: FilepathOrBuffer, *args, **kwargs
    ) -> "DataContainer":
        return pd.read_pickle(filepath_or_buffer, *args, **kwargs)

    def _header_to_json(self) -> str:
        prefix = self.JSON_PREFIX
        suffix = self.JSON_SUFFIX
        try:
            header_string = prefix + json.dumps(self.header) + "\n" + suffix
        except TypeError as e:
            raise TypeError(
                e.__str__().join(". Remove it in order to save to file")
            ) from None
        return header_string

    @classmethod
    def _json_to_header(
        cls, f: IO
    ) -> Optional[Union[Dict[str, Union[int, str]], Dict[str, int], Dict[str, str]]]:
        prefix = cls.JSON_PREFIX.strip()
        suffix = cls.JSON_SUFFIX.strip()
        first = f.readline().strip()
        header = f.readline().strip()
        last = f.readline().strip()

        if not (first == prefix and last == suffix):
            f.seek(0)
            header = None
        else:
            header = json.loads(header)
        return header

    def plot(self, *args, **kwargs) -> Union[ndarray, Axes]:
        plotter = pd.DataFrame.plot(self)
        ax = plotter(*args, **kwargs)
        xUnit = self.header.get("xUnit")
        if xUnit:
            xlabel = "{0} ({1})".format(self.index.name, xUnit)
            if isinstance(ax, np.ndarray):
                ax[-1].set_xlabel(xlabel)
            else:
                ax.set_xlabel(xlabel)
        return ax


def _combine_header(header: Dict[str, Any], other: Any) -> Dict[str, Any]:
    if isinstance(other, list):
        itemlist = other[:]  # otherwise also other would be affectec by itemlist.pop()
        while itemlist:
            item = itemlist.pop()
            if isinstance(item, DataContainer):
                header = _combine_header(header, item.header)
            elif isinstance(item, dict):
                header = _combine_header(header, item)
            else:
                pass
    elif isinstance(other, DataContainer):
        header = _combine_header(header, other.header)
    elif isinstance(other, dict):
        d = dict()
        for key in header.keys() & other.keys():
            if header[key] == other[key]:
                d.update({key: header[key]})
        header = d
    return header
