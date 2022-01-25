"""
    Xpress Insight Python package
    =============================

    This is an internal file of the 'xpressinsight' package. Do not import it directly.

    This material is the confidential, proprietary, unpublished property
    of Fair Isaac Corporation.  Receipt or possession of this material
    does not convey rights to divulge, reproduce, use, or allow others
    to use it without the specific written authorization of Fair Isaac
    Corporation and use must conform strictly to the license agreement.

    Copyright (c) 2020-2022 Fair Isaac Corporation. All rights reserved.
"""

#
from abc import ABC, abstractmethod
from enum import Enum
import pandas as pd
import numpy as np
from typing import Type, Dict, Union, Tuple, List, Any, Optional
import re

from xpressinsight.mosel_keywords import MOSEL_KEYWORDS

MAX_STR_LENGTH_BYTES = 1000000
MAX_STR_LENGTH_CHARS = int(MAX_STR_LENGTH_BYTES / 4)

VALID_IDENT_REGEX_STR = "[_a-zA-Z][_a-zA-Z0-9]*"
VALID_IDENT_REGEX = re.compile(VALID_IDENT_REGEX_STR)
VALID_IDENT_MAX_LENGTH = 1000

VALID_ANNOTATION_STR_REGEX_STR = "[\n\r\0]"
VALID_ANNOTATION_STR_REGEX = re.compile(VALID_ANNOTATION_STR_REGEX_STR)
VALID_ANNOTATION_STR_MAX_LENGTH = 5000


def is_valid_identifier(ident: str, max_length: int = VALID_IDENT_MAX_LENGTH) -> bool:
    """ Checks if a string is a valid identifier for an Xpress Insight entity. """

    if len(ident) > max_length:
        raise ValueError("The identifier {} must not be longer than {} characters."
                         .format(repr(ident), max_length))

    return VALID_IDENT_REGEX.fullmatch(ident) is not None


def validate_ident(ident: str, ident_for: str = None, ident_name: str = "identifier") -> str:
    if not is_valid_identifier(ident):
        if ident_for is None:
            err_msg = "Invalid {0} {1}. Identifier must satisfy regex {3}."
        else:
            err_msg = "Invalid {0} {1} for {2}. Identifier must satisfy regex {3}."
        raise ValueError(err_msg.format(ident_name, repr(ident), ident_for, repr(VALID_IDENT_REGEX_STR)))

    if ident in MOSEL_KEYWORDS:
        if ident_for is None:
            err_msg = "Invalid {0} {1}. Identifier must not be a reserved keyword."
        else:
            err_msg = "Invalid {0} {1} for {2}. Identifier must not be a reserved keyword."
        raise ValueError(err_msg.format(ident_name, repr(ident), ident_for))

    return ident


def validate_raw_ident(ident: str, ident_name: str = "identifier") -> str:
    """ Check whether a string is a valid identifier in an annotation. """
    if not is_valid_identifier(ident):
        raise ValueError('{} is not a valid {}. Identifier must satisfy regex {}.'
                         .format(repr(ident), ident_name, repr(VALID_IDENT_REGEX_STR)))
    return ident


def validate_annotation_str(s: str,
                            str_name: str = 'annotation string',
                            max_length: int = VALID_ANNOTATION_STR_MAX_LENGTH) -> str:
    """ Check whether annotation string contains unsupported characters or is too long. """
    if "!)" in s:
        raise ValueError('The {} must not contain the substring "!)": {}.'.format(str_name, repr(s)))
    if len(s) > max_length:
        raise ValueError("The {} must not be longer than {} characters: {}.".format(str_name, max_length, repr(s)))
    if VALID_ANNOTATION_STR_REGEX.search(s) is not None:
        raise ValueError("The {} {} contains unsupported characters. It must not match the regular expression {}"
                         .format(str_name, repr(s), repr(VALID_ANNOTATION_STR_REGEX_STR)))
    return s


def check_simple_python_type(attr: Any, attr_name: str, attr_type: Type, parent: Type = None):
    if not isinstance(attr, attr_type):
        attr_name = re.sub(r'_.*__', '', attr_name)
        parent = f"of {parent.__name__} " if parent is not None else ""
        raise TypeError(f'The "{attr_name}" parameter {parent}must be a "{attr_type.__name__}" object, '
                        f'but it is a "{type(attr).__name__}" and has value "{attr}".')


def check_instance_attribute_types(class_instance: Any):
    """ Type check for all instance attributes with class level type hints. """
    class_type = type(class_instance)

    for attr_name, attr_type in class_type.__annotations__.items():
        attr = getattr(class_instance, attr_name)

        if attr_type == BASIC_TYPE:
            if not issubclass(attr, (boolean, integer, string, real)):
                type_err_msg = 'The "{}" parameter of {} must be the {}, but it is a "{}" and has value "{}".'
                attr_name = re.sub(r'_.*__', '', attr_name)
                raise TypeError(type_err_msg.format(attr_name, class_type.__name__,
                                                    'Insight type string, integer, boolean, or real',
                                                    type(attr).__name__, attr))
        else:
            check_simple_python_type(attr, attr_name, attr_type, class_type)


class XiEnum(Enum):
    #
    def __repr__(self):
        return "{}.{}".format(self.__class__.__name__, self._name_)


class Manage(XiEnum):
    """
    How and whether Insight handles an entity.

    Attributes
    ----------
    INPUT : str
        Included in the scenario input data.
    RESULT : str
        Included in the scenario results data.

    Examples
    --------
    Manage a scalar entity as an input

    >>> MyInteger: xi.Scalar(dtype=xi.integer,
    ...                      alias='My Integer',
    ...                      manage=xi.Manage.INPUT)
    """

    INPUT = "input"
    RESULT = "result"


class Hidden(XiEnum):
    """
    Possible values of whether the UI should hide an entity where appropriate.

    Attributes
    ----------
    ALWAYS : str
        Indicates that the UI should hide the entity always.
    TRUE : str
        Indicates that the UI should hide the entity where appropriate.
    FALSE : str
        Indicates that the UI should show the entity where appropriate.

    Examples
    --------
    Always hide an entity in the Insight UI

    >>> MyInteger: xi.Scalar(dtype=xi.integer,
    ...                      alias='My Integer',
    ...                      hidden=xi.Hidden.ALWAYS)
    """

    ALWAYS = "always"
    TRUE = "true"
    FALSE = "false"


class DataConnector(ABC):
    #
    @abstractmethod
    def __init__(self, app):
        pass

    @abstractmethod
    def clear_input(self):
        pass

    @abstractmethod
    def save_input(self):
        pass

    @abstractmethod
    def load_input(self):
        pass

    @abstractmethod
    def save_result(self):
        pass


class BasicType:
    pass


#
class boolean(BasicType):
    """
    Declare the entity to be (or to contain) boolean (`True` or `False`) values.
    If not specified, the default value is `False`.

    Examples
    --------
    Example of declaring a scalar entity to be boolean.

    >>> my_bool: xi.Scalar(dtype=xi.boolean)
    ... my_bool: xi.Scalar(False)
    ... my_bool: xi.Scalar(True)

    See Also
    --------
    Scalar
    Param
    Index
    Series
    Column
    """

    pass


#
class integer(BasicType):
    """
    Declare the entity to be (or to contain) integer (whole number) values.
    Each value must fit into a signed 32-bit integer.
    If not specified, the default value is `0`.

    Examples
    --------
    Example of declaring a scalar entity to be integer.

    >>> my_int: xi.Scalar(dtype=xi.integer)
    ... my_int: xi.Scalar(0)
    ... my_int: xi.Scalar(100)
    ... my_int: xi.Scalar(-10)

    See Also
    --------
    Scalar
    Param
    Index
    Series
    Column
    """

    pass


#
#
class string(BasicType):
    """
    Declare the entity to be (or to contain) string (UTF-8 encoded) values. The length
    (in bytes) of a string scalar (Scalar or Param) must not exceed 1,000,000 bytes.
    The length of a string in a container (Index, Series, or DataFrame) must not exceed
    250,000 characters. A string must not contain the null character.
    If not specified, the default value of a string scalar is the empty string `""`.

    Examples
    --------
    Example of declaring a scalar entity to be a string.

    >>> my_string: xi.Scalar(dtype=xi.string)
    ... my_string: xi.Scalar("Hello World!")

    See Also
    --------
    Scalar
    Param
    Index
    Series
    Column
    """

    pass


#
class real(BasicType):
    """
    Declare the entity to be (or to contain) floating-point (whole number) values.
    If not specified, the default value is `0.0`.

    Examples
    --------
    Example of declaring a scalar entity to be a floating-point value.

    >>> my_real: xi.Scalar(dtype=xi.real)
    >>> my_real: xi.Scalar(100.0)
    >>> my_real: xi.Scalar(123.456)

    See Also
    --------
    Scalar
    Param
    Index
    Series
    Column
    """

    pass


ALL_BASIC_TYPE = [boolean, integer, string, real]

BASIC_TYPE = Type[BasicType]

#
BASIC_TYPE_MAP: Dict[Type[BasicType], Type] = {
    boolean: bool,
    integer: int,
    string: str,
    real: float,
}

#
SCALAR_DEFAULT_VALUES = {
    boolean: False,
    integer: 0,
    string: "",
    real: 0.0,
}


def python_int_to_bool(value: int, name: str = None) -> bool:
    if value == int(True):
        return True
    elif value == int(False):
        return False
    else:
        if name is None:
            msg = "Invalid boolean, expecting {} (True) or {} (False) but got {}.".format(
                int(True), int(False), value
            )
        else:
            msg = "{} invalid boolean, expecting {} (True) or {} (False) but got {}.".format(
                name, int(True), int(False), value
            )
        raise ValueError(msg)


class EntityBase(ABC):
    __name: str

    def __init__(self):
        self.__name = ''

    @property
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, name: str):
        if self.__name == '':
            self.__name = validate_ident(name, type(self).__name__, 'name')
        else:
            raise AttributeError('Cannot set name of {} to "{}" because it has already been initialized to "{}".'
                                 .format(type(self).__name__, name, self.__name))

    @abstractmethod
    def is_managed(self, manage: Manage) -> bool:
        pass


class Entity(EntityBase):
    """
    Abstract class for all Insight entities.
    """

    __dtype: BASIC_TYPE
    __alias: str
    __format: str
    __hidden: Hidden
    __manage: Manage
    __read_only: bool
    __transform_labels_entity: str
    __update_after_execution: bool

    #
    def __init__(self,
                 dtype: BASIC_TYPE,
                 #
                 alias: str = "",
                 format: str = "",
                 hidden: Hidden = Hidden.FALSE,
                 manage: Manage = Manage.INPUT,
                 read_only: bool = False,
                 transform_labels_entity: str = "",
                 update_after_execution: bool = False,
                 #
                 ):
        """
        The constructor.

        Parameters
        ----------
        dtype : BASIC_TYPE
            The data-type.
        alias : str = ""
            Used to provide an alternative name for an entity in the UI.
            The value is used in place of the entity name where appropriate in the UI.
        format : str = ""
            The formatting string used for displaying numeric values.
        hidden : Hidden = Hidden.FALSE
            Indicates whether the UI should hide the entity where appropriate.
        manage : Manage = Manage.INPUT
            How and whether Insight handles an entity. Defines how the system manages the entity data.
        read_only : bool = False
            Whether an entity is readonly. Specifies that the value(s) of the entity cannot be modified. See also `hidden`.
        transform_labels_entity : str = ""
            An entity in the schema to be used as a labels entity. The value is the name of the entity.
            The type of the index set of the labels entity much match the data type of this entity.
            The data type of the labels entity can be any primitive type.
        update_after_execution : bool = False
            Whether the value of the entity in the scenario is updated with the value of the corresponding model entity at the end of the scenario execution.
            If `True` the value of the entity is updated to correspond with the model entity after execution.
        """
        super().__init__()
        self.__dtype = dtype
        #
        self.__alias = alias
        self.__format = format
        self.__hidden = hidden
        self.__manage = manage
        self.__read_only = read_only
        self.__transform_labels_entity = transform_labels_entity.replace('.', '_')
        self.__update_after_execution = update_after_execution
        #
        check_instance_attribute_types(self)
        validate_annotation_str(alias, 'entity alias')
        validate_annotation_str(format, 'entity format')

        if transform_labels_entity != "":
            validate_ident(self.__transform_labels_entity, "transform labels entity")

        if update_after_execution and manage == Manage.RESULT:
            raise ValueError('Cannot set parameter update_after_execution to true for a result entity. '
                             'This parameter is only valid for input entities.')

    @property
    def dtype(self) -> BASIC_TYPE:
        return self.__dtype

    @property
    def alias(self) -> str:
        return self.__alias

    @property
    def format(self) -> str:
        return self.__format

    @property
    def hidden(self) -> Hidden:
        return self.__hidden

    @property
    def manage(self) -> Manage:
        return self.__manage

    @property
    def read_only(self) -> bool:
        return self.__read_only

    @property
    def transform_labels_entity(self) -> str:
        return self.__transform_labels_entity

    @property
    def update_after_execution(self) -> bool:
        return self.__update_after_execution

    def is_managed(self, manage: Manage) -> bool:
        """ Check whether the entity is managed as the given management type: input/result. """
        return self.__manage == manage or (self.__update_after_execution and manage == Manage.RESULT)


class ScalarBase(Entity):
    #
    def __init__(
            self,
            default: Union[str, bool, int, float] = None,
            dtype: BASIC_TYPE = None,
            #
            alias: str = "",
            format: str = "",
            hidden: Hidden = Hidden.FALSE,
            manage: Manage = Manage.INPUT,
            read_only: bool = False,
            transform_labels_entity: str = "",
            update_after_execution: bool = False,
            #
    ):
        """
        The constructor.

        Parameters
        ----------
        default : Union[str, bool, int, float] = None
            The default value.
        dtype : BASIC_TYPE
            The data-type.
        alias : str = ""
            Used to provide an alternative name for an entity in the UI.
            The value is used in place of the entity name where appropriate in the UI.
        format : str = ""
            The formatting string used for displaying numeric values.
        hidden : Hidden = Hidden.FALSE
            Indicates whether the UI should hide the entity where appropriate.
        manage : Manage = Manage.INPUT
            How and whether Insight handles an entity. Defines how the system manages the entity data.
        read_only : bool = False
            Whether an entity is readonly. Specifies that the value(s) of the entity cannot be modified. See also `hidden`.
        transform_labels_entity : str = ""
            An entity in the schema to be used as a labels entity. The value is the name of the entity.
            The type of the index set of the labels entity much match the data type of this entity.
            The data type of the labels entity can be any primitive type.
        update_after_execution : bool = False
            Whether the value of the entity in the scenario is updated with the value of the corresponding model entity at the end of the scenario execution.
            If `True` the value of the entity is updated to correspond with the model entity after execution.
        """
        #
        if dtype is None:
            #
            if default is None:
                raise TypeError('It is necessary to specify at least one of the following parameters: '
                                'dtype (data type), default (default value).')
            if isinstance(default, str):
                dtype = string
            elif isinstance(default, bool):
                dtype = boolean
            elif isinstance(default, int):
                dtype = integer
            elif isinstance(default, float):
                dtype = real
            else:
                raise TypeError('The default value of a scalar or parameter must be a str, int, bool, '
                                'or float, but it is a "{}".'.format(type(default)))

        #
        super().__init__(
            dtype=dtype,
            #
            alias=alias,
            format=format,
            hidden=hidden,
            manage=manage,
            read_only=read_only,
            transform_labels_entity=transform_labels_entity,
            update_after_execution=update_after_execution,
            #
        )

        if default is None:
            self.__default = SCALAR_DEFAULT_VALUES[dtype]
            assert (self.__default is not None)
        else:
            self.check_type(default)
            self.__default = default

    def check_type(self, value: Any):
        """ Check if the type is correct and check the bounds. """

        #
        if (self.dtype == integer and isinstance(value, bool)) or\
                not isinstance(value, BASIC_TYPE_MAP.get(self.dtype)):
            raise TypeError("Value {} has type {} but should be {}.".format(
                value, type(value), BASIC_TYPE_MAP[self.dtype]
                #
                #
                #
            ))

        #
        if isinstance(value, str):
            if not len(value.encode("utf-8")) <= MAX_STR_LENGTH_BYTES:
                msg = """
                String {} must not take more space than {} bytes.
                """.format(self.name, MAX_STR_LENGTH_BYTES)
                raise ValueError(msg)

            if '\0' in value:
                msg = r"""
                String {} must not contain the null character "\0".
                """.format(self.name)
                raise ValueError(msg)

        elif isinstance(value, int) and not isinstance(value, bool):

            #
            int32_limits = np.iinfo(np.int32)

            if not (
                    (int32_limits.min <= value) and (value <= int32_limits.max)
            ):
                msg = """
                Integer {} must fit into signed 32-bit integer.
                """.format(
                    self.name
                )
                raise TypeError(msg)

        elif isinstance(value, float):

            #
            pass

    @property
    def default(self) -> Union[str, int, bool, float]:
        return self.__default


class Scalar(ScalarBase):
    """
    Represents a *scalar* entity.

    Examples
    --------
    Some examples of declaring scalar entities in the data model.

    >>> @xi.AppConfig(name="My First Insight Python App",
    ...               version=xi.AppVersion(0, 1, 2))
    ... class MyApp(xi.AppBase):
    ...
    ...     # Examples where data type is inferred from default value
    ...     # Scalar "NumFactory" of type "xi.integer"; default value 10
    ...     NumFactory: xi.Scalar(10)
    ...     # Scalar "IsOn" of type "xi.boolean"; default value True
    ...     IsOn: xi.Scalar(True)
    ...
    ...     # Examples where data type is explicitly given.
    ...     RealScalar: xi.Scalar(dtype=xi.real)      # default value 0.0
    ...     StringScalar: xi.Scalar(dtype=xi.string)  # default value ""

    See Also
    --------
    Param
    """

    pass


class Param(ScalarBase):
    """
    Represents a *parameter* entity. Parameters can be used to configure an Xpress Insight app. When parameters are declared, their name, data type,
    and default value must be specified. Parameters are typically read-only.

    Examples
    --------
    Some examples of declaring parameter entities in the data model.

    >>> @xi.AppConfig(name="My First Insight Python App",
    ...               version=xi.AppVersion(0, 1, 2))
    ... class MyApp(xi.AppBase):
    ...
    ...     # examples where data type is inferred from the default value
    ...     # Param "P" of type "xi.integer" with default value 100
    ...     P: xi.Param(100)
    ...     # Param "DEBUG" of type "xi.boolean" with default value False
    ...     DEBUG: xi.Param(False)
    ...     # Param "PI" of type "xi.real" with default value 3.14
    ...     PI: xi.Param(3.14)
    ...     # Param "STR_PARAM" of type xi.string with a default value
    ...     STR_PARAM: xi.Param('My String Param')
    ...
    ...     # examples where data type is explicitly given
    ...     BOOL_PARAM: xi.Param(dtype=xi.boolean)  # default value False
    ...     INT_PARAM: xi.Param(dtype=xi.integer)  # default value 0
    ...     REAL_PARAM: xi.Param(dtype=xi.real)  # default value 0.0
    ...     STRING_PARAM: xi.Param(dtype=xi.string)  # default value ""

    See Also
    --------
    Scalar
    """

    def __init__(
            self,
            default: Union[str, int, bool, float] = None,
            dtype: BASIC_TYPE = None,
    ):
        """
        Initializes `Param` with the data type or a default value (in which case data type is inferred).

        Parameters
        ----------
        default: Union[str, int, bool, float]
            The default value.
        dtype: BASIC_TYPE
            The data type of the parameter.
        """

        super().__init__(
            default,
            dtype=dtype,
        )


class Index(Entity):
    """
    Represents an *index* entity. To be used in conjunction with `xpressinsight.Series` or `xpressinsight.DataFrame` objects.

    Examples
    --------
    Example creating an index of integer values with an alias.

    >>> Indices: xi.Index(dtype=xi.integer, alias='Array Indices')

    See Also
    --------
    Series
    DataFrame
    """
    def check_type(self, value: Any, name: str):
        if not isinstance(value, pd.Index):
            msg = """
            Problem with {}:
                Expected: pandas.Index
                Actual: {}.
            """.format(name, type(value))
            raise TypeError(msg)

        if value.size == 0:
            return

        if self.dtype == integer:
            #
            if not pd.api.types.is_integer_dtype(value.dtype):
                msg = """
                All values in {} must be integers, but the data type is: {}.
                """.format(name, value.dtype)
                raise TypeError(msg)

            check_type_np(value.values, integer, name)

        elif self.dtype == real:
            #
            check_type_np(value.values, real, name)

        elif self.dtype == string:
            #
            check_type_np(value.values, string, name)

        elif self.dtype == boolean:
            if not value.is_boolean():
                msg = """
                All values in {} must be Booleans.
                """.format(name)
                raise TypeError(msg)

        else:
            raise ValueError("Unexpected type: {}".format(self.dtype))


def __get_parent_name(parent_obj_or_none: Any) -> str:
    return '' if parent_obj_or_none is None else ' of ' + type(parent_obj_or_none).__name__


def validate_list(parent_obj_or_none: Any, attr_name: str, item_type: Type, item_type_name: str,
                  value: Any) -> Tuple:
    """ Validate and normalize list of Index/Column -> Convert it to immutable tuple of Index/Column. """
    if isinstance(value, item_type):
        return value,
    else:
        error_msg = 'The "{0}" parameter{1} must be a {2} object or a list of {2} objects, '

        if isinstance(value, list):
            value = tuple(value)

        if isinstance(value, tuple):
            if len(value) == 0:
                raise TypeError((error_msg + 'but the {0} list is empty.')
                                .format(attr_name, __get_parent_name(parent_obj_or_none), item_type_name))

            for item in value:
                if not isinstance(item, item_type):
                    raise TypeError((error_msg + 'but the {0} list contains an object of type "{3}" and value: {4}.')
                                    .format(attr_name, __get_parent_name(parent_obj_or_none), item_type_name,
                                            type(item).__name__, repr(item)))
        else:
            raise TypeError((error_msg + 'but the {0} parameter has type "{3}" and value: {4}.')
                            .format(attr_name, __get_parent_name(parent_obj_or_none), item_type_name,
                                    type(value).__name__, repr(value)))
        return value


def get_index_tuple(parent_obj: EntityBase, index_names: Tuple[str], entities: Dict[str, EntityBase]) -> Tuple[Index]:
    result: List[Index] = []

    for index_name in index_names:
        index = entities.get(index_name, None)

        if isinstance(index, Index):
            result.append(index)
        else:
            if index is None:
                raise KeyError('Invalid index "{0}" for xpressinsight.{1} "{2}". Entity "{0}" not declared.'
                               .format(index_name, type(parent_obj).__name__, parent_obj.name))
            else:
                raise KeyError('Invalid index "{0}" for xpressinsight.{1} "{2}". '
                               'Entity "{0}" is a {3}, but must be an xpressinsight.Index.'
                               .format(index_name, type(parent_obj).__name__, parent_obj.name, type(index)))

    return tuple(result)


class Series(Entity):
    """
    Represent a *Series* entity, a declaration of a pandas `Series` datastructure.
    Every series must has at least one index.

    Examples
    --------
    Example of creating a `Result` series containing floating-point values, and is managed by Insight as a result entity.
    It is indexed by `Indices`, which must have been declared previously.

    >>> Indices: xi.Index(...) # previous declaration
    ... Result: xi.Series(index=['Indices'], dtype=xi.real,
    ...                   manage=xi.Manage.RESULT, alias='Result Array')

    See Also
    --------
    Index
    """

    #
    def __init__(
            self,
            index: Union[str, List[str]],
            dtype: BASIC_TYPE,
            #
            alias: str = "",
            format: str = "",
            hidden: Hidden = Hidden.FALSE,
            manage: Manage = Manage.INPUT,
            read_only: bool = False,
            transform_labels_entity: str = "",
            update_after_execution: bool = False,
            #
    ):
        """
        Initializes `Series`.

        Parameters
        ----------
        index : Union[str, List[str]]
            The index to use.
        dtype : BASIC_TYPE
            The data-type.
        alias : str = ""
            Used to provide an alternative name for an entity in the UI.
            The value is used in place of the entity name where appropriate in the UI.
        format : str = ""
            The formatting string used for displaying numeric values.
        hidden : Hidden = Hidden.FALSE
            Indicates whether the UI should hide the entity where appropriate.
        manage : Manage = Manage.INPUT
            How and whether Insight handles an entity. Defines how the system manages the entity data.
        read_only : bool = False
            Whether an entity is readonly. Specifies that the value(s) of the entity cannot be modified. See also `hidden`.
        transform_labels_entity : str = ""
            An entity in the schema to be used as a labels entity. The value is the name of the entity.
            The type of the index set of the labels entity much match the data type of this entity.
            The data type of the labels entity can be any primitive type.
        update_after_execution : bool = False
            Whether the value of the entity in the scenario is updated with the value of the corresponding model entity at the end of the scenario execution.
            If `True` the value of the entity is updated to correspond with the model entity after execution.
        """
        super().__init__(
            dtype=dtype,
            #
            alias=alias,
            format=format,
            hidden=hidden,
            manage=manage,
            read_only=read_only,
            transform_labels_entity=transform_labels_entity,
            update_after_execution=update_after_execution,
            #
        )

        self.__index_names: Tuple[str] = validate_list(self, 'index', str, 'string', index)
        self.__index: Optional[Tuple[Index]] = None

    def _init(self, entities: Dict[str, EntityBase]):
        if self.__index is None:
            self.__index = get_index_tuple(self, self.__index_names, entities)
        else:
            raise RuntimeError('The {} "{}" has already been initialized.'.format(type(self).__name__, self.name))

    @property
    def index(self) -> Tuple[Index]:
        return self.__index


class Column(Entity):
    """
    Represent a single column within a *DataFrame* entity.

    Examples
    --------
    Example of declaring a column `IntCol` which will contain integer values. Note: this declaration should appear
    as part of a `xpressinsight.DataFrame` declaration.

    >>> xi.Column("IntCol", dtype=xi.integer, alias="Input Integer Column")

    See Also
    --------
    DataFrame
    """

    #
    def __init__(
            self,
            name: str,
            dtype: BASIC_TYPE,
            #
            alias: str = "",
            format: str = "",
            hidden: Hidden = Hidden.FALSE,
            manage: Manage = Manage.INPUT,
            read_only: bool = False,
            transform_labels_entity: str = "",
            update_after_execution: bool = False,
            #
    ):
        """
        Initializes `Column`.

        Parameters
        ----------
        name : str
            The name of the column.
        dtype : BASIC_TYPE
            The data-type.
        alias : str = ""
            Used to provide an alternative name for an entity in the UI.
            The value is used in place of the entity name where appropriate in the UI.
        format : str = ""
            The formatting string used for displaying numeric values.
        hidden : Hidden = Hidden.FALSE
            Indicates whether the UI should hide the entity where appropriate.
        manage : Manage = Manage.INPUT
            How and whether Insight handles an entity. Defines how the system manages the entity data.
        read_only : bool = False
            Whether an entity is readonly. Specifies that the value(s) of the entity cannot be modified. See also `hidden`.
        transform_labels_entity : str = ""
            An entity in the schema to be used as a labels entity. The value is the name of the entity.
            The type of the index set of the labels entity much match the data type of this entity.
            The data type of the labels entity can be any primitive type.
        update_after_execution : bool = False
            Whether the value of the entity in the scenario is updated with the value of the corresponding model entity at the end of the scenario execution.
            If `True` the value of the entity is updated to correspond with the model entity after execution.
        """
        super().__init__(
            dtype=dtype,
            #
            alias=alias,
            format=format,
            hidden=hidden,
            manage=manage,
            read_only=read_only,
            transform_labels_entity=transform_labels_entity,
            update_after_execution=update_after_execution,
            #
        )
        #
        self.name = name


class DataFrame(EntityBase):
    """
    Represent a *DataFrame* entity.

    Examples
    --------
    Example declaring a data-frame `MixedTable` which has three columns.

    >>> MixedTable: xi.DataFrame(index='Years', columns=[
    ...     xi.Column("IntCol", dtype=xi.integer,
    ...               alias="Input Integer Column"),
    ...     xi.Column("StrCol", dtype=xi.string,
    ...               alias="Input String Column",
    ...               update_after_execution=True),
    ...     xi.Column("ResultCol", dtype=xi.real,
    ...               alias="Result Real Column",
    ...               manage=xi.Manage.RESULT)
    ... ])

    See Also
    --------
    Column
    Index
    """

    def __init__(
            self,
            index: Union[str, List[str]],
            columns: Union[Column, List[Column]]):
        """
        Initializes `DataFrame`.

        Parameters
        ----------
        index : Union[str, List[str]]
            The index to use.
        columns : Union[Column, List[Column]])
            The columns which make up this data-frame.
        """
        super().__init__()
        self.__index_names: Tuple[str] = validate_list(self, 'index', str, 'string', index)
        self.__index: Optional[Tuple[Index]] = None
        self.__columns: Tuple[Column] = validate_list(self, 'columns', Column, 'xpressinsight.Column', columns)

    def _init(self, entities: Dict[str, EntityBase]):
        if self.__index is None:
            self.__index = get_index_tuple(self, self.__index_names, entities)
        else:
            raise RuntimeError('The {} "{}" has already been initialized.'.format(type(self).__name__, self.name))

    @property
    def index(self) -> Tuple[Index]:
        return self.__index

    @property
    def columns(self) -> Tuple[Column]:
        return self.__columns

    def is_managed(self, manage: Manage) -> bool:
        """ Check whether the DataFrame has a column that is managed as the given management type. """
        return any(column.is_managed(manage) for column in self.columns)


def data_frame_get_empty_index(df: DataFrame) -> pd.Index:
    """ Creates an empty pandas Index or MultiIndex with dtype and name information. """
    index_list = [
        pd.Index([], dtype=BASIC_TYPE_MAP[index.dtype], name=index.name)
        for index in df.index
    ]

    if len(df.index) == 1:
        pd_index = index_list[0]
    else:
        pd_index = pd.MultiIndex.from_product(index_list)

    return pd_index


def check_str(s: Any) -> bool:
    """ Check if a value is a valid exportable string. """
    return isinstance(s, str) and len(s) <= MAX_STR_LENGTH_CHARS and '\0' not in s


def check_type_np(x: np.ndarray, t: Type[BasicType], name: str):
    """ Check if type of NumPy array x is compatible with type t and check bounds."""
    if x.size == 0:
        return

    if t == string:
        #
        #
        if not np.all(np.vectorize(check_str)(x)):
            msg = r"""
            All values in {} must be strings, 
            must not be longer than {} characters, 
            and must not contain the null character "\0".
            """.format(name, MAX_STR_LENGTH_CHARS)
            raise TypeError(msg)

    elif t == integer:
        if x.dtype.kind != "i":
            msg = """
            All values in {} must be integers, but the data type is: {}.
            """.format(
                name, x.dtype
            )
            raise TypeError(msg)

        #
        int32_limits = np.iinfo(np.int32)
        values = x

        if not (
                np.all(int32_limits.min <= values) and np.all(values <= int32_limits.max)
        ):
            msg = """
            All values in {} must fit into signed 32-bit integers.
            """.format(
                name
            )
            raise TypeError(msg)

    elif t == real:
        if x.dtype.kind != "f":
            msg = """
            All values in {} must be floats, but the data type is: {}.
            """.format(
                name, x.dtype
            )
            raise TypeError(msg)

        if np.finfo(x.dtype).bits > 64:
            msg = """
            All values in {} must fit into 64-bit floats.
            """.format(
                name
            )
            raise TypeError(msg)

    elif t == boolean:
        if x.dtype.kind != "b":
            msg = """
            All values in {} must be Booleans, but the data type is: {}.
            """.format(
                name, x.dtype
            )
            raise TypeError(msg)

    else:
        raise ValueError("Unexpected type passed to check_type_np: {}".format(t))


def check_type(
        x: Any, e: EntityBase, name: str, manage: Optional[Manage]
):
    """ Verify that x is the same type as given by e. """

    if isinstance(e, (Scalar, Param, Series)):
        if not issubclass(e.dtype, BasicType):
            msg = "dtype of {} must be a subclass of BasicType.".format(e)
            raise TypeError(msg)

    #
    #
    #

    if isinstance(e, (Scalar, Param)):
        e.check_type(x)

    elif isinstance(e, Index):
        e.check_type(x, name)

    elif isinstance(e, (Series, DataFrame)):
        if isinstance(e, Series) and not isinstance(x, pd.Series):
            msg = """
            Problem with entity "{}":
                Expected: pandas Series
                Actual: {}.
            """.format(
                name, type(x)
            )
            raise TypeError(msg)

        if isinstance(e, DataFrame) and not isinstance(x, pd.DataFrame):
            msg = """
            Problem with entity "{}":
                Expected: pandas DataFrame
                Actual: {}.
            """.format(
                name, type(x)
            )
            raise TypeError(msg)

        #
        if len(e.index) != x.index.nlevels:
            msg = f"""
            Problem with entity "{name}": dimension of index set is {x.index.nlevels} but expecting {len(e.index)}.
            """

            raise TypeError(msg)

        for idx_id, idx_entity in enumerate(e.index):
            idx_entity.check_type(x.index.get_level_values(idx_id),
                                  'index {} ("{}") of entity "{}"'.format(idx_id, idx_entity.name, name))

        #
        if isinstance(e, Series):
            check_type_np(x.values, e.dtype, name)

        elif isinstance(e, DataFrame):
            #
            #
            for column in e.columns:
                if manage is None or column.is_managed(manage):

                    if column.name not in x.columns:
                        raise TypeError("Missing column '{}' in DataFrame '{}'".format(column.name, e.name))

                    check_type_np(
                        x.loc[:, column.name].values,
                        column.dtype,
                        "{}.{}".format(name, column.name),
                    )

    else:
        raise ValueError("Unexpected type passed to check_type: {}".format(e))


class AppVersion:
    """
    Class to represent the version number of an Insight Python app, according to semver
    (Semantic Versioning) conventions.

    Examples
    --------
    Example of specifying version "1.2.3"

    >>> @xi.AppConfig(name="My App", version=xi.AppVersion(1, 2, 3))
    ... class InsightApp(xi.AppBase):
    ...     pass
    """

    def __init__(self, major: int = 0, minor: int = 0, patch: int = 0):
        """
        Initializes `AppVersion` with major, minor, and patch version information.

        Parameters
        ----------
        major : int
            The major version between 0 and 999.
        minor : int
            The minor version between 0 and 999.
        patch : int
            The patch version between 0 and 999.
        """

        for i in [major, minor, patch]:
            if not isinstance(i, int):
                raise TypeError('The parameters of AppVersion must be integers, '
                                f'but one parameter is a {type(i).__name__} and has value {i}.')
            if i < 0 or 999 < i:
                raise ValueError("The parameters of AppVersion must be integers between 0 and 999, "
                                 "but one parameter value is {}.".format(i))

        self.__major: int = major
        self.__minor: int = minor
        self.__patch: int = patch

    @property
    def major(self) -> int:
        return self.__major

    @property
    def minor(self) -> int:
        return self.__minor

    @property
    def patch(self) -> int:
        return self.__patch

    def __str__(self):
        return "{}.{}.{}".format(self.__major, self.__minor, self.__patch)

    def __repr__(self):
        return "AppVersion({}, {}, {})".format(self.__major, self.__minor, self.__patch)


class ResultDataDelete(XiEnum):
    """
    When to delete scenario results data.

    Attributes
    ----------
    ON_CHANGE
        Delete scenario result data when the scenario input-data is edited, or when scenario is queued for execution.
    ON_EXECUTE
        Delete scenario result data when scenario starts to execute.
    ON_QUEUE
        Delete scenario result data when scenario is queued for execution.
    """

    ON_CHANGE = "on-change"
    ON_EXECUTE = "on-execute"
    ON_QUEUE = "on-queue"


class ResultData:
    """
    Class which specifies how to handle result data within the Insight server.

    Examples
    --------
    Example showing how to configure Insight to delete the result data when the
    scenario is queued for execution.

    >>> @xi.AppConfig(name="My App",
    ...               version=xi.AppVersion(1, 0, 0),
    ...               result_data=xi.ResultData(
    ...                   delete=xi.ResultDataDelete.ON_QUEUE
    ...               ))
    ... class InsightApp(xi.AppBase):
    ...     pass
    """

    __delete: ResultDataDelete

    def __init__(self, delete: ResultDataDelete = ResultDataDelete.ON_CHANGE):
        """
        Initializes `ResultData` with delete strategy.

        Parameters
        ----------
        delete: ResultDataDelete
            When to delete scenario results data.
            Results data is deleted when a certain state change occurs for the scenario.
            This attribute identifies this state change as either whenever a scenario is modified,
            when it is queued, or when it begins execution.
        """

        self.__delete = delete
        check_instance_attribute_types(self)

    def __repr__(self):
        return "ResultData(delete={})".format(repr(self.delete))

    @property
    def delete(self) -> ResultDataDelete:
        return self.__delete
