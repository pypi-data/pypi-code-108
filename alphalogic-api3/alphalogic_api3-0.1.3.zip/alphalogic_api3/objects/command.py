# -*- coding: utf-8 -*-
import traceback
from alphalogic_api3.protocol import rpc_pb2
from alphalogic_api3.multistub import MultiStub
from alphalogic_api3 import utils
from alphalogic_api3.utils import decode_string
from alphalogic_api3.logger import log


class AbstractCommand(object):
    """
    AbstractCommand implements CommandService service (see `rpc.proto <https://github.com/Alphaopen/alphalogic_api3/blob/
    master/alphalogic_api3/protocol/proto/rpc.proto>`_)
    """

    def _call(self, func_name, *args, **kwargs):
        return self.multi_stub.command_call(func_name, id=self.id, *args, **kwargs)

    def name(self):
        """
        Return command name

        :rtype: str
        """
        answer = self._call('name')
        return answer.name

    def display_name(self):
        """
        Return command display name

        :rtype: str
        """
        answer = self._call('display_name')
        return answer.display_name

    def desc(self):
        """
        Return command description

        :rtype: str
        """
        answer = self._call('desc')
        return answer.desc

    def set_display_name(self, display_name):
        """
        Set command display name

        :arg display_name: str
        """
        self._call('set_display_name', display_name=display_name)

    def set_desc(self, desc):
        """
        Set command description

        :arg desc: str
        """
        self._call('set_desc', desc=desc)

    def is_string(self):
        """
        Return True if command return type is string

        :rtype: bool
        """
        answer = self._call('is_string')
        return answer.yes

    def is_long(self):
        """
        Return True if command return type is int

        :rtype: bool
        """
        answer = self._call('is_long')
        return answer.yes

    def is_double(self):
        """
        Return True if command return type is double

        :rtype: bool
        """
        answer = self._call('is_double')
        return answer.yes

    def is_datetime(self):
        """
        Return True if command return type is datetime

        :rtype: bool
        """
        answer = self._call('is_datetime')
        return answer.yes

    def is_bool(self):
        """
        Return True if command return type is bool

        :rtype: bool
        """
        answer = self._call('is_bool')
        return answer.yes

    def is_map(self):
        """
        Return True if command return type is map

        :rtype: bool
        """
        answer = self._call('is_map')
        return answer.yes

    def set_result(self, value):
        """
        Set command return value

        :arg value: The value type: long, float, datetime, bool or str
        """
        value_rpc = utils.get_rpc_value(type(value), value)
        self._call('set_result', value=value_rpc)

    def set_exception(self, reason):
        """
        Set exception in command.
        Information about exception will be called for adapter's side.

        :arg reason: state string
        """
        self._call('set_exception', exception=reason)

    def clear(self):
        """
        Remove command arguments
        """
        self._call('clear')

    def argument_list(self):
        """
        Return list of command arguments

        :rtype: list of command argument names
        """
        answer = self._call('argument_list')
        return answer.names

    def argument(self, name_argument):
        """
        Return command argument with value by argument name

        :arg name_argument: command argument name
        :rtype: name/value pair as a tuple (argument name, argument value)
        """
        answer = self._call('argument', argument=name_argument)
        return answer.name, answer.value

    def update_or_create_argument(self, name_arg, value):
        """
        Add command argument / overwrite argument value

        :arg name_arg: command argument name
        :arg value: command argument value
        """
        cur_choices = self.choices[name_arg] if name_arg in self.choices else None
        if cur_choices is None:
            value_rpc = utils.get_rpc_value(type(value), value)
            self._call('update_or_create_argument', argument=name_arg, value=value_rpc)
        else:
            req = rpc_pb2.CommandRequest(id=self.id, argument=name_arg)
            utils.build_rpc_value(req.value, type(value), value)
            for val in cur_choices:
                e = req.enums.add()
                if isinstance(val, tuple):
                    e.name = val[1]
                    utils.build_rpc_value(e.value, type(val[0]), val[0])
                else:
                    e.name = str(val)
                    utils.build_rpc_value(e.value, type(val), val)

            self.multi_stub.call_helper('update_or_create_argument', fun_set=MultiStub.command_fun_set,
                                        request=req, stub=self.multi_stub.stub_command)

    def owner(self):
        """
        Return ID of the command's owner

        :rtype: uint64
        """
        answer = self._call('owner')
        return answer.owner


class Command(AbstractCommand):
    """
    | Class Command is used in command decorator.
    | Class Command inherits all data elements and methods from :class:`~alphalogic_api3.objects.command.AbstractCommand`.

    :arg device: has :class:`~alphalogic_api3.objects.Object` type
    :arg function: executed function
    """
    def __init__(self, device, function):
        self.function = function
        self.result_type = function.result_type
        self.arguments = function.arguments
        self.arguments_type = function.arguments_type
        self.choices = function.choices
        self.device = device

    def set_multi_stub(self, multi_stub):
        self.multi_stub = multi_stub

    def call_function(self):
        """
        Call function when command executed

        :rtype: The return type depends on the function code
        """
        try:
            arg_list = self.argument_list()
            function_dict = {}
            info = []
            for name_arg in arg_list:
                type_arg = self.arguments_type[name_arg]
                function_dict[name_arg] = utils.value_from_rpc(self.argument(name_arg)[1])
                info.append('{0}({1}): {2}'.format(name_arg, type_arg, function_dict[name_arg]))

            log.info('Execute command \'{0}\' with arguments [{1}] from device \'{2}\''
                     .format(self.name(), '; '.join(info), self.device.id))
            self.function(self.device, **function_dict)

        except Exception as err:
            t = traceback.format_exc()
            log.error('Command \'{0}\' raise exception: {1}'.format(self.name(), decode_string(t)))
