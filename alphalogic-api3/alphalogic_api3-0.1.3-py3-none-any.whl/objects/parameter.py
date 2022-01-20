# -*- coding: utf-8 -*-
import datetime

from alphalogic_api3.protocol import rpc_pb2

from alphalogic_api3.attributes import Visible, Access
from alphalogic_api3.multistub import MultiStub
from alphalogic_api3 import utils
from alphalogic_api3.logger import log
from alphalogic_api3.utils import Exit


class AbstractParameter:
    """
    AbstractParameter implements ParameterService service (see `rpc.proto <https://github.com/Alphaopen/alphalogic_api3/
    blob/master/alphalogic_api3/protocol/proto/rpc.proto>`_)
    """

    def _call(self, func_name, *args, **kwargs):
        return self.multi_stub.parameter_call(func_name, id=self.id, *args, **kwargs)

    def name(self):
        """
        Return parameter name

        :rtype: str
        """
        answer = self._call('name')
        return answer.name

    def display_name(self):
        """
        Return parameter display name

        :rtype: str
        """
        answer = self._call('display_name')
        return answer.display_name

    def desc(self):
        """
        Return parameter description

        :rtype: str
        """
        answer = self._call('desc')
        return answer.desc

    def set_display_name(self, display_name):
        """
        Set parameter display name

        :arg display_name: str
        """
        answer = self._call('set_display_name', display_name=display_name)

    def set_desc(self, desc):
        """
        Set parameter description

        :arg desc: str
        """
        answer = self._call('set_desc', desc=desc)

    def is_string(self):
        """
        Return True if parameter value type is string

        :rtype: bool
        """
        answer = self._call('is_string')
        return answer.yes

    def is_long(self):
        """
        Return True if parameter value type is long

        :rtype: bool
        """
        answer = self._call('is_long')
        return answer.yes

    def is_double(self):
        """
        Return True if parameter value type is double

        :rtype: bool
        """
        answer = self._call('is_double')
        return answer.yes

    def is_datetime(self):
        """
        Return True if parameter value type is datetime

        :rtype: bool
        """
        answer = self._call('is_datetime')
        return answer.yes

    def is_bool(self):
        """
        Return True if parameter value type is bool

        :rtype: bool
        """
        answer = self._call('is_bool')
        return answer.yes

    def is_map(self):
        """
        Return True if parameter value type is map

        :rtype: bool
        """
        answer = self._call('is_map')
        return answer.yes

    def is_runtime(self):
        """
        Return True if parameter type is Visible.runtime

        :rtype: bool
        """
        answer = self._call('is_runtime')
        return answer.yes

    def is_setup(self):
        """
        Return True if parameter type is Visible.setup

        :rtype: bool
        """
        answer = self._call('is_setup')
        return answer.yes

    def is_hidden(self):
        """
        Return True if parameter type is Visible.hidden

        :rtype: bool
        """
        answer = self._call('is_hidden')
        return answer.yes

    def is_common(self):
        """
        Return True if parameter type is Visible.common

        :rtype: bool
        """
        answer = self._call('is_common')
        return answer.yes

    def set_runtime(self):
        """
        Set parameter type to Visible.runtime
        """
        answer = self._call('set_runtime')

    def set_setup(self):
        """
        Set parameter type to Visible.setup
        """
        answer = self._call('set_setup')

    def set_hidden(self):
        """
        Set parameter type to Visible.hidden
        """
        answer = self._call('set_hidden')

    def set_common(self):
        """
        Set parameter type to Visible.common
        """
        answer = self._call('set_common')

    def is_read_only(self):
        """
        Return True if parameter access type is Access.read_only

        :rtype: bool
        """
        answer = self._call('is_read_only')
        return answer.yes

    def is_read_write(self):
        """
        Return True if parameter access type is Access.read_write

        :rtype: bool
        """
        answer = self._call('is_read_write')
        return answer.yes

    def set_read_only(self):
        """
        Set parameter access type to Access.read_only
        """
        answer = self._call('set_read_only')

    def set_read_write(self):
        """
        Set parameter access type to Access.read_write
        """
        answer = self._call('set_read_write')

    def is_licensed(self):
        """
        Return True if parameter is the license key parameter

        :rtype: bool
        """
        answer = self._call('is_licensed')
        return answer.yes

    def set_licensed(self):
        """
        Set the license key parameter
        """
        answer = self._call('set_licensed')

    def clear(self):
        """
        Remove all predefined values from the 'choices' argument of the parameter
        """
        answer = self._call('clear')

    def get(self):
        """
        Get parameter value

        :rtype: long, float, datetime, bool or str
        """
        answer = self._call('get')
        return utils.value_from_rpc(answer.value)

    def set(self, value):
        """
        Set parameter value

        :arg value: The value type: long, float, datetime, bool or str
        """
        value_rpc = utils.get_rpc_value(self.value_type, value)
        self._call('set', value=value_rpc)

    def enums(self):
        """
        Get the predefined enumeration of values from the 'choices' argument of the parameter

        :rtype: List of values of long, float, datetime, bool or str type in a tuple as (value1, value2, value3 ….)
        """
        answer = self._call('enums')
        return [utils.value_from_rpc(key.value) for key in answer.enums]

    def set_enum(self, value, enum_name):
        """
        Add/replace enumeration member – a pair (value, name) – for the 'choices' argument of the parameter

        :param value: The value type: long, float, datetime, bool or str
        :param enum_name: enumeration member name
        """
        value_rpc = rpc_pb2.Value()
        utils.build_rpc_value(value_rpc, type(value), value)
        answer = self._call('set_enum', enum_name=enum_name, value=value_rpc)

    def set_enums(self, values):
        """
        Add/replace multiple enumeration members for the 'choices' argument of the parameter

        :param values: An array of values can be one of the following:

            * List of values of long, float, datetime, bool or str type in a tuple as (value1, value2, value3 ….)
            * List of enumeration members in a tuple of tuples as ((value1, 'enum_name1'), (value2, 'enum_name2'), ...)
        """
        value_type = self.value_type
        req = rpc_pb2.ParameterRequest(id=self.id)
        for val in values:
            e = req.enums.add()
            if isinstance(val, tuple):
                e.name = str(val[1])
                utils.build_rpc_value(e.value, type(val[0]), val[0])
            else:
                e.name = str(val)
                utils.build_rpc_value(e.value, type(val), val)

        self.multi_stub.call_helper('set_enums', fun_set=MultiStub.parameter_fun_set, request=req,
                                    stub=self.multi_stub.stub_parameter)

    def has_enum(self, enum_name):
        """
        Return True if parameter has a predefined enumeration of values

        :rtype: bool
        """
        answer = self._call('has_enum', enum_name=enum_name)
        return answer.yes

    def owner(self):
        """
        Return ID of the parameter's owner

        :rtype: uint64
        """
        answer = self._call('owner')
        return answer.owner


class Parameter(AbstractParameter):
    """
    Class Parameter inherits all data elements and methods from :class:`~alphalogic_api3.objects.parameter.AbstractParameter`.
    """
    index_number = 0

    def __init__(self, *args, **kwargs):
        self.index_number = Parameter.index_number
        Parameter.index_number += 1

        for arg in kwargs:
            self.__dict__[arg] = kwargs[arg]

        self.visible = kwargs.get('visible', Visible.runtime)
        self.access = kwargs.get('access', Access.read_write)
        self.callback = kwargs.get('callback', None)

        if 'value_type' not in kwargs:
            raise Exception('value_type not found in Parameter')

        if kwargs['value_type'] not in [bool, int, float, datetime.datetime, str, list, dict]:
            raise Exception(f'value_type={kwargs["value_type"]} is unknown')

        self.default = kwargs.get('default')
        self.choices = kwargs.get('choices', None)

    def set_multi_stub(self, multi_stub):
        self.multi_stub = multi_stub

    def __getattr__(self, item):
        if item == 'val':
            return self.get()

        if item in self.__dict__:
            return self.__dict__[item]

    def __setattr__(self, attr, value):
        if attr == 'val' and self.parameter_name.lower() == 'name':  # exclude change 'name' value
            log.error('Attempt to change name of device')
            raise Exit

        if attr == 'val':
            if value is not None:
                self.set(value)
        elif attr in ['value_type', 'visible', 'access', 'default', 'choices', 'multi_stub', 'id',
                      'parameter_name', 'callback', 'index_number']:
            self.__dict__[attr] = value
        return self

    def set_choices(self):
        if isinstance(self.choices, tuple):
            self.clear()
            self.set_enums(self.choices)

    def get_copy(self):
        return Parameter(value_type=self.value_type, default=self.default, visible=self.visible,
                         access=self.access, callback=self.callback, choices=self.choices)


class ParameterBool(Parameter):
    def __new__(cls, *args, **kwargs):
        return Parameter(*args, value_type=bool, **kwargs)


class ParameterLong(Parameter):
    def __new__(cls, *args, **kwargs):
        return Parameter(*args, value_type=int, **kwargs)


class ParameterDouble(Parameter):
    def __new__(cls, *args, **kwargs):
        return Parameter(*args, value_type=float, **kwargs)


class ParameterDatetime(Parameter):
    def __new__(cls, *args, **kwargs):
        return Parameter(*args, value_type=datetime.datetime, **kwargs)


class ParameterString(Parameter):
    def __new__(cls, *args, **kwargs):
        return Parameter(*args, value_type=str, **kwargs)


class ParameterList(Parameter):
    def __new__(cls, *args, **kwargs):
        return Parameter(*args, value_type=list, **kwargs)


class ParameterDict(Parameter):
    def __new__(cls, *args, **kwargs):
        return Parameter(*args, value_type=dict, **kwargs)