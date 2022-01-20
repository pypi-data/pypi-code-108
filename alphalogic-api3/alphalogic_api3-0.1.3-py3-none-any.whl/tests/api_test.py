# -*- coding: utf-8 -*-
import datetime

from alphalogic_api3.attributes import Visible, Access
from alphalogic_api3.objects import Root, Object
from alphalogic_api3.objects import MajorEvent
from alphalogic_api3.objects import Parameter, ParameterBool, ParameterLong, \
    ParameterDouble, ParameterDatetime, ParameterString
from alphalogic_api3 import init
from alphalogic_api3.exceptions import ComponentNotFound
from alphalogic_api3.decorators import command, run
from alphalogic_api3 import utils


def handle_after_set_double(node, parameter):
    node.log.info('double changed')
    node.after_set_value_test_event.emit(value=parameter.val)


class MyRoot(Root):
    param_string = ParameterString(default='noop', visible=Visible.setup)
    param_bool = ParameterBool(default=False, visible=Visible.common)
    param_int = ParameterLong(default=2, visible=Visible.runtime, access=Access.read_only)
    param_double = ParameterDouble(default=2.3, callback=handle_after_set_double)
    param_timestamp = ParameterDatetime(default=datetime.datetime.utcnow())
    param_hid = ParameterDouble(default=2.2, visible=Visible.hidden)
    param_vect = ParameterLong(default=1, choices=(0, 1, 2, 3))
    param_vect2 = ParameterLong(default=2, choices=((0, 'str 77'), (1, 'str 88'), (2, 'str 2'), (3, 'str 3')))

    alarm = MajorEvent(('where', str),
                       ('when', datetime.datetime),
                       ('why', int))
    simple_event = MajorEvent()
    after_set_value_test_event = MajorEvent(('value', float))

    def handle_create(self):
        pass

    def handle_remove(self):
        pass

    def handle_get_available_children(self):
        return [
            (Controller, 'Controller')
        ]

    @command(result_type=bool)
    def cmd_simple_event(self):
        self.simple_event.emit()
        return True

    @command(result_type=bool)
    def cmd_simple_event_manual_time(self, timestamp=0):
        self.simple_event.set_time(timestamp)
        self.simple_event.emit()
        return True

    @command(result_type=bool)
    def cmd_alarm(self, where='here', when=datetime.datetime.now(), why=2):

        assert ['where', 'when', 'why'] == self.alarm.argument_list()
        self.alarm.emit(where=where, when=when, why=why)

        assert ['where', 'when', 'why'] == self.alarm.argument_list()
        return True

    @command(result_type=str)
    def check(self, where='here'):
        #self.relax(1, 2, 3, 4)
        return 'abc'

    @command(result_type=bool)
    def failed_cmd(self):
        self.log.info("failed cmd start")
        raise Exception("command failed")
        return False

    # Check Command return

    @command(result_type=int)
    def cmd_return_int(self):
        return int(utils.milliseconds_from_epoch(datetime.datetime.utcnow()) / 1000.0)

    @command(result_type=float)
    def cmd_return_float(self):
        return int(utils.milliseconds_from_epoch(datetime.datetime.utcnow()) % 1000.0) / 1000.0

    @command(result_type=str)
    def cmd_return_unicode(self):
        return 'некоторый текст'

    @command(result_type=datetime.datetime)
    def cmd_return_datetime(self):
        return datetime.datetime.utcnow()

    @command(result_type=bool)
    def cmd_exception(self):
        raise Exception('fire!')
        return True

    #
    @command(result_type=bool, which=(1, 2, 3), which2=((True, 'On'), (False, 'Off')))
    def relax(self, where='room', why=42, which=2, which2=False):
        self.log.info(f'where={where}; why={why}; which={which}; which2={which2}')
        return True

    counter = ParameterLong(default=0)

    @run(period_one=1)
    def run_one(self):
        self.counter.val += 1

    run_event = MajorEvent()

    @run(period_two=2)
    def run_two(self):
        self.run_event.emit()

    run2_event = MajorEvent()
    param_run_exception = ParameterBool(default=False)

    @run(period_three=2)
    def run_three(self):
        if self.param_run_exception.val:
            raise Exception('exception in run')
        self.run2_event.emit()

    run4_event = MajorEvent()

    @run(period_four=1)
    def run_four(self):
        # Тормозит все остальные run
        #time.sleep(5)
        self.run4_event.emit()


class Controller(Object):

    # Parameters:
    hostname = ParameterString(visible=Visible.setup, access=Access.read_write, default='1', choices=('1', '2'))
    mode = ParameterBool(visible=Visible.setup, default=True, choices=((True, 'On'), (False, 'Off')))
    version = Parameter(value_type=int, visible=Visible.common)
    counter = ParameterDouble(default=1.0, access=Access.read_only)
    counter_spec = ParameterDouble(default=1.0, access=Access.read_write)

    @command(result_type=bool, which=((True, 'On'), (False, 'Off')))
    def relax(self, where='room', when=datetime.datetime.now(), why=42, which=False):
        return True

    @run(period=20)
    def run_third(self):
        self.log.info(str(self.id) + ' c_run')
        val = self.counter_spec.val
        self.counter_spec.val = val+1

    def handle_get_available_children(self):
        return [
            (Controller, 'Controller')
        ]


if __name__ == '__main__':

    # python loop
    root = MyRoot()
    root.alarm.emit(where='asdadsadg', why=3, when=datetime.datetime.now())

    # Parameters
    try:
        root.parameter('asgasdgg')
        assert False, 'ComponentNotFound doesnt\' works'
    except ComponentNotFound as err:
        pass

    pars = root.parameters()
    assert list(x.name() == 'param_bool' for x in pars)
    param = root.parameter('param_bool')
    assert not param.val
    param = root.parameter('param_int')
    assert param.val == 2

    # Events
    try:
        root.event('asgasdgg')
        assert False, 'ComponentNotFound doesnt\' works'
    except ComponentNotFound as err:
        pass

    events = root.events()
    assert list(x.name() == 'alarm' for x in events)
    ev = root.event('alarm')

    # Commands

    try:
        root.command('asgasdgg')
        assert False, 'ComponentNotFound doesnt\' works'
    except ComponentNotFound as err:
        pass

    cmds = root.commands()
    assert list(x.name() == 'cmd_simple_event' for x in cmds)
    cmd = root.command('cmd_simple_event')
    cmd = root.command('check')

    root.join()


'''
assert root.param_string.val == 'noop'
assert root.param_string.is_setup()
assert not root.param_bool.val
assert root.param_bool.is_common()
assert root.param_int.val == 2
assert root.param_int.is_runtime()
assert root.param_int.is_read_only()
assert root.param_double.val == 2.3
assert root.param_double.is_runtime(), 'default wrong'
assert root.param_double.is_read_write(), 'default wrong'
#assert (datetime.datetime.now() - root.param_timestamp.val).total_seconds() < 10

#assert root.param_vect.val == (0, 1, 2, 3)


root.param_double.val = 5.0
assert root.param_double.val == 5.0

#check read_only
#try:
#    root.param_int.val = 3
#    assert False
#except Exception:
#    pass


#adapter.relax(1, 2, 3, 4)

root.simple_event.emit()

root.alarm.set_time(int(time.time()) * 1000 - 100000)
root.alarm.emit(where='asdadsadg', why=3, when=datetime.datetime.now())
'''
