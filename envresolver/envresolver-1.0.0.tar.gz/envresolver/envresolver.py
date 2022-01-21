import datetime
import datetime as dt
import xml.etree.ElementTree as ET
from re import fullmatch
from os import getenv
from sys import stderr
from json import loads
from typing import Type, Any, Callable, get_origin, get_args


class Types:
    class Json:
        """Json type representation"""
    class Xml:
        """XML type representation"""


class EnvResolver:
    """
    Class for resolving environment variables with attention to type.

    Since environment variables are generally accessible only with an apparent
    string-type, type conversions and deductions have to conducted explicitly.
    """

    class _Var:
        """
        Representation of a single variable
        """
        def __init__(self, name, t, val):
            self.name: str = name
            self.t: Type = t
            self.val = val

    class _Ns(object):
        """
        Empty namespace object
        """

    def __init__(self, datetime_fmt: str = "%Y-%m-%d %H:%M:%S",
                 list_separator: str = ",", silent: bool = False):
        """
        Initializes the instance and sets verbosity

        :param datetime_fmt: Format for parsing timestamps
        :param list_separator: List separator symbol
        :param silent: If True, error messages will be printed to `stderr`
        """
        self._silent = silent
        self._datetime_fmt = datetime_fmt
        self._list_separator = list_separator
        self._params: {str, EnvResolver._Var} = {}
        self._converters: {Type: Callable} = {
            str: None,
            int: lambda e: int(e),
            float: lambda e: float(e),
            bool: EnvResolver._get_bool,
            Types.Json: EnvResolver._get_json,
            Types.Xml: EnvResolver._get_xml,
            datetime.datetime: self._get_datetime,
            list: self._get_list
        }

        self.ns = EnvResolver._Ns

    @staticmethod
    def _validate_env_var_name(e: str):
        return fullmatch(r"[a-zA-Z_]+[a-zA-Z0-9_]*", e)

    def _get_datetime(self, e: str):
        return dt.datetime.strptime(e, self._datetime_fmt)

    @staticmethod
    def _get_bool(e: str):
        t = ("true", "y", "yes", "1")
        f = ("false", "n", "no", "0")
        lower = e.lower()
        if lower in t:
            return True
        elif lower in f:
            return False
        else:
            raise ValueError

    def _get_list(self, e: str):
        return e.split(self._list_separator)

    @staticmethod
    def _get_json(e: str):
        return loads(e)

    @staticmethod
    def _get_xml(e: str):
        return ET.fromstring(e)

    def _get_from_env(self, p: _Var):
        env = getenv(p.name)
        if not env:
            return
        try:
            if p.t == str:
                p.val = env
            elif p.t == list or get_origin(p.t) == list:
                l = self._converters[list](env)
                if p.t == list:
                    p.val = l
                    return
                else:
                    try:
                        t_content = get_args(p.t)[0]
                    except IndexError:
                        p.val = l
                        return
                    values_temp = []
                    for item in l:
                        values_temp.append(self._converters[t_content](item))
                    p.val = values_temp
            else:
                p.val = self._converters[p.t](env)

        except ValueError:
            if not self._silent:
                print(f"Variable {p.name} with type {p.t} found in the "
                      f"current env with invalid value: {env}", file=stderr)
            return

    def set_list_separator(self, sep: str):
        """
        Sets default separator for list conversions
        """
        self._list_separator = sep

    def set_datetime_format(self, fmt: str):
        """
        Sets default format for `datetime.datetime` conversions
        """
        self._datetime_fmt = fmt

    def add_converter(self, t: Type, c: Callable):
        """
        Adds a custom converter/parser to the instance

        :param t: Converter type
        :param c: Converter callable accepting a single string-type argument
        :return: None
        """
        if not t:
            raise TypeError("Type cannot be None")
        if not callable(c):
            raise TypeError(f"parameter c must be a callable, got "
                            f"{str(type(c))}")
        self._converters[t] = c

    def add_variable(self, name: str, t: Type = str, default: Any = None):
        """
        Adds a variable for resolving

        :param name: Variable name
        :param t: Variable type
        :param default: Default value
        :return: None
        """
        if not self._validate_env_var_name(name):
            raise ValueError(f"Env var name {name} containing illegal "
                             f"characters!")

        if t not in self._converters and get_origin(t) not in self._converters:
            raise NotImplementedError(f"Conversion support for type {str(t)} "
                                      f"not added!")
        self._params[name] = EnvResolver._Var(name, t, default)

    def resolve(self):
        """
        Resolves all configured variables

        :return: None
        """
        for p in self._params.values():
            self._get_from_env(p)
            setattr(self.ns, p.name, p.val)

    def getr(self, name: str):
        """
        Gets a variables value from the previously parsed cache.

        :param name: Variable name
        :return: Variable value
        """
        return self._params[name].val

    def get(self, name: str, t: Type = str, default: Any = None):
        """
        Gets a variable directly from the current environment.

        :param name: Variable name
        :param t: Variable type
        :param default: Default value
        :return:
        """
        if not self._validate_env_var_name(name):
            raise ValueError(f"Env var name {name} containing illegal "
                             f"characters!")

        v = EnvResolver._Var(name, t, default)
        self._get_from_env(v)
        return v.val



