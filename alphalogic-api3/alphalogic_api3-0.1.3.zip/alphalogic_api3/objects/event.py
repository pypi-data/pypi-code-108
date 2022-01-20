# -*- coding: utf-8 -*-
from alphalogic_api3 import utils
from alphalogic_api3.attributes import Priority


class AbstractEvent(object):
    """
    AbstractEvent implements EventService service (see `rpc.proto <https://github.com/Alphaopen/alphalogic_api3/blob/
    master/alphalogic_api3/protocol/proto/rpc.proto>`_)
    """

    def _call(self, func_name, *args, **kwargs):
        return self.multi_stub.event_call(func_name, id=self.id, *args, **kwargs)

    def name(self):
        """
        Return event name

        :rtype: str
        """
        return self._call('name').name

    def display_name(self):
        """
        Return event display name

        :rtype: str
        """
        return self._call('display_name').display_name

    def desc(self):
        """
        Return event description

        :rtype: str
        """
        return self._call('desc').desc

    def set_display_name(self, display_name):
        """
        Set event display name

        :arg display_name: str
        """
        self._call('set_display_name', display_name=display_name)

    def set_desc(self, desc):
        """
        Set event description

        :arg desc: str
        """
        self._call('set_desc', desc=desc)

    def is_trivial(self):
        """
        Return True if event severity is trivial

        :rtype: bool
        """
        return self._call('is_trivial').yes

    def is_minor(self):
        """
        Return True if event severity is minor

        :rtype: bool
        """
        return self._call('is_minor').yes

    def is_major(self):
        """
        Return True if event severity is major

        :rtype: bool
        """
        return self._call('is_major').yes

    def is_critical(self):
        """
        Return True if event severity is critical

        :rtype: bool
        """
        return self._call('is_critical').yes

    def is_blocker(self):
        """
        Return True if event severity is blocker

        :rtype: bool
        """
        return self._call('is_blocker').yes

    def set_trivial(self):
        """
        Set event severity to trivial
        """
        self._call('set_trivial')

    def set_minor(self):
        """
        Set event severity to minor
        """
        self._call('set_minor')

    def set_major(self):
        """
        Set event severity to major
        """
        self._call('set_major')

    def set_critical(self):
        """
        Set event severity to critical
        """
        self._call('set_critical')

    def set_blocker(self):
        """
        Set event severity to blocker
        """
        self._call('set_blocker')

    def set_time(self, timestamp):
        """
        Set event time (UTC)

        :param timestamp: int(time.time() * 1000) (мс)
        """
        self._call('set_time', time=timestamp)

    def emit(self, **kwargs):
        """
        | Emit event with the current UTC time.
        | In order to use timestamp other than the current UTC time, you should call set_time function with required
         timestamp before executing emit function.

        :param kwargs: name/value pairs of event arguments separated by commas, each argument name followed by an equal sign
        """
        for arg_name, arg_type in self.arguments:
            if arg_name not in kwargs:
                raise Exception('Incorrect argument name of event {0}'.format(self.name))

            value_rpc = utils.get_rpc_value(arg_type, kwargs[arg_name])
            self._call('set_argument_value', argument=arg_name, value=value_rpc)

        self._call('emit')

    def clear(self):
        """
        Remove event arguments
        """
        self._call('clear')

    def argument_list(self):
        """
        Return list of event arguments

        :rtype: list of event argument names
        """
        answer = self._call('argument_list')
        return answer.names

    def argument(self, name_argument):
        """
        Return event argument with value by argument name

        :arg name_argument: event argument name
        :rtype: name/value pair as a tuple (argument name, argument value)

        """
        answer = self._call('argument', argument=name_argument)
        return answer.name, answer.value

    def update_or_create_argument(self, name_arg, value):
        """
        Add event argument / overwrite argument value

        :arg name_arg: event argument name
        :arg value: event argument value
        """
        value_type = utils.value_type_field_definer(type(value))

        if value_type not in ['list', 'tuple']:
            value_rpc = utils.get_rpc_value(type(value), value)
            self._call('update_or_create_argument', argument=name_arg, value=value_rpc)
        else:
            raise Exception('Event argument type not supported')

    def set_argument_value(self, name_arg, value):
        """
        Set argument value

        :arg name_arg: event argument name
        :arg value: event argument value
        """
        value_type = utils.value_type_field_definer(type(value))

        if value_type not in ['list', 'tuple']:
            value_rpc = utils.get_rpc_value(type(value), value)
            self._call('set_argument_value', argument=name_arg, value=value_rpc)
        else:
            raise Exception('Event argument type not supported')

    def owner(self):
        """
        Return ID of the event's owner

        :rtype: uint64
        """
        answer = self._call('owner')
        return answer.owner


class Event(AbstractEvent):
    """
    Class Event inherits all data elements and methods from :class:`~alphalogic_api3.objects.event.AbstractEvent`.

    :arg priority: trivial, minor, major, critical or blocker
    :arg args: name/type pairs in a tuple of tuples (argument name, argument type)
    """
    def __init__(self, priority, *args, **kwargs):
        self.arguments = args
        self.id = kwargs.get('id', None)
        self.priority = priority
        self.multi_stub = None

    def set_multi_stub(self, multi_stub):
        self.multi_stub = multi_stub

    def get_copy(self):
        return Event(self.priority, *self.arguments, id=self.id)


class TrivialEvent(Event):
    def __new__(cls, *args):
        return Event(Priority.trivial, *args)


class MinorEvent(Event):
    def __new__(cls, *args):
        return Event(Priority.minor, *args)


class MajorEvent(Event):
    def __new__(cls, *args):
        return Event(Priority.major, *args)


class CriticalEvent(Event):
    def __new__(cls, *args):
        return Event(Priority.critical, *args)


class BlockerEvent(Event):
    def __new__(cls, *args):
        return Event(Priority.blocker, *args)
