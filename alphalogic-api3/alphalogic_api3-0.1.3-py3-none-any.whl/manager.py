# -*- coding: utf-8 -*-
import signal
import time
from threading import Thread
import traceback
from alphalogic_api3.protocol import rpc_pb2
from alphalogic_api3.multistub import MultiStub
from alphalogic_api3.objects.parameter import Parameter, ParameterDouble
from alphalogic_api3.objects.event import Event
from alphalogic_api3.objects.command import Command
from alphalogic_api3.logger import log
from alphalogic_api3.tasks_pool import TasksPool
from alphalogic_api3.utils import shutdown, decode_string
from alphalogic_api3.attributes import Visible
from alphalogic_api3.exceptions import ComponentNotFound
from alphalogic_api3.conf_inspector import ConfInspector
from alphalogic_api3 import options
from alphalogic_api3 import utils


class AbstractManager(object):
    def _call(self, name_func, id_object, *args, **kwargs):
        return self.multi_stub.object_call(name_func, id=id_object, *args, **kwargs)

    def root(self):
        answer = self.multi_stub.object_call('root')
        return answer.id

    def is_root(self, id_object):
        answer = self._call('is_root', id_object)
        return answer.yes

    def parent(self, id_object):
        answer = self._call('parent', id_object)
        return answer.id

    def type(self, id_object):
        answer = self._call('type', id_object)
        return answer.type

    def set_type(self, id_object, type_value):
        answer = self._call('set_type', id_object, type=type_value)

    def create_string_parameter(self, id_object, name):
        answer = self._call('create_string_parameter', id_object, name=name)
        return answer.id

    def create_long_parameter(self, id_object, name):
        answer = self._call('create_long_parameter', id_object, name=name)
        return answer.id

    def create_double_parameter(self, id_object, name):
        answer = self._call('create_double_parameter', id_object, name=name)
        return answer.id

    def create_datetime_parameter(self, id_object, name):
        answer = self._call('create_datetime_parameter', id_object, name=name)
        return answer.id

    def create_bool_parameter(self, id_object, name):
        answer = self._call('create_bool_parameter', id_object, name=name)
        return answer.id

    def create_map_parameter(self, id_object, name):
        answer = self._call('create_map_parameter', id_object, name=name)
        return answer.id

    def create_event(self, id_object, name):
        answer = self._call('create_event', id_object, name=name)
        return answer.id

    def create_string_command(self, id_object, name):
        answer = self._call('create_string_command', id_object, name=name)
        return answer.id

    def create_long_command(self, id_object, name):
        answer = self._call('create_long_command', id_object, name=name)
        return answer.id

    def create_double_command(self, id_object, name):
        answer = self._call('create_double_command', id_object, name=name)
        return answer.id

    def create_datetime_command(self, id_object, name):
        answer = self._call('create_datetime_command', id_object, name=name)
        return answer.id

    def create_bool_command(self, id_object, name):
        answer = self._call('create_bool_command', id_object, name=name)
        return answer.id

    def create_map_command(self, id_object, name):
        answer = self._call('create_map_command', id_object, name=name)
        return answer.id

    def parameters(self, id_object):
        answer = self._call('parameters', id_object)
        return answer.ids

    def events(self, id_object):
        answer = self._call('events', id_object)
        return answer.ids

    def commands(self, id_object):
        answer = self._call('commands', id_object)
        return answer.ids

    def children(self, id_object):
        answer = self._call('children', id_object)
        return answer.ids

    def parameter(self, id_object, name):
        answer = self._call('parameter', id_object, name=name)
        return answer.id

    def event(self, id_object, name):
        answer = self._call('event', id_object, name=name)
        return answer.id

    def command(self, id_object, name):
        answer = self._call('command', id_object, name=name)
        return answer.id

    def is_removed(self, id_object):
        answer = self._call('is_removed', id_object)
        return answer.yes

    def register_maker(self, id_object, name, type_str):
        answer = self._call('register_maker', id_object, name=name, type=type_str)
        return answer.yes

    def unregister_all_makers(self, id_object):
        self._call('unregister_all_makers', id_object)

    def is_connected(self, id_object):
        answer = self._call('is_connected', id_object)
        return answer.yes

    def is_error(self, id_object):
        answer = self._call('is_error', id_object)
        return answer.yes

    def is_ready_to_work(self, id_object):
        answer = self._call('is_ready_to_work', id_object)
        return answer.yes

    def state_no_connection(self, id_object, reason):
        self._call('state_no_connection', id_object, reason=reason)

    def state_connected(self, id_object, reason):
        self._call('state_connected', id_object, reason=reason)

    def state_error(self, id_object, reason):
        self._call('state_error', id_object, reason=reason)

    def state_ok(self, id_object, reason):
        self._call('state_ok', id_object, reason=reason)


class Manager(AbstractManager):
    dict_type_objects = {}  # Dictionary of nodes classes. 'type' as a key
    dict_user_name_type_objects = {}  # Dictionary of nodes classes. 'user display name in available_children' as a key
                                      # value - is type of object
    nodes = {}  # Nodes dictionary. 'id' as a key
    components = {}  # All commands, parameters, events dictionary. 'id' as a key
    components_for_device = {}  # All commands, parameters, events of node. Node 'id' as a key
    inspector = ConfInspector()

    def __init__(self):
        signal.signal(signal.SIGTERM, shutdown)
        signal.signal(signal.SIGINT, shutdown)

    def start_threads(self):
        self.g_thread = Thread(target=self.grpc_thread)
        self.tasks_pool = TasksPool()

    def configure_multi_stub(self, address):
        self.multi_stub = MultiStub(address)

    def prepare_for_work(self, object, id):
        Manager.nodes[id] = object
        list_id_parameters_already_exists = self.parameters(id)
        list_parameters_name_already_exists = list(map(lambda id: self.multi_stub.parameter_call('name', id=id).name,
                                                  list_id_parameters_already_exists))
        list_parameters_name_period = [getattr(object, name).period_name for name in object.run_function_names]
        list_parameters_name_should_exists = list(filter(lambda attr: type(getattr(object, attr)) is Parameter, dir(object)))

        list_parameters_name_should_exists = list(map(lambda x: (getattr(object, x), x), list_parameters_name_should_exists))
        list_parameters_name_should_exists = list(list(zip(*sorted(list_parameters_name_should_exists,key=lambda x: x[0].index_number)))[1])
        list_parameters_name_should_exists = list_parameters_name_should_exists + list_parameters_name_period
        list_parameters_name_should_exists = [name for name in list_parameters_name_should_exists
                                              if name not in list_parameters_name_already_exists]

        # order of call below function is important
        self.configure_run_function(object, id, list_id_parameters_already_exists)
        list_id_parameters_already_exists = self.parameters(id)
        self.configure_parameters(object, id, list_id_parameters_already_exists, list_parameters_name_should_exists)
        list_id_parameters_already_exists = self.parameters(id)
        self.configure_parameters(object, id, list_id_parameters_already_exists, list_parameters_name_already_exists)
        self.configure_commands(object, id)
        self.configure_events(object, id)

    def prepare_existing_devices(self, id_parent):
        for child_id in super(Manager, self).children(id_parent):
            class_name_str = self.get_type(child_id)
            if class_name_str not in Manager.dict_type_objects:
                Manager.dict_type_objects[class_name_str] = utils.get_class_name_from_str(class_name_str)
            class_name = Manager.dict_type_objects[class_name_str]

            if class_name:
                object = class_name(class_name_str, child_id)
                Manager.components_for_device[child_id] = []
                self.prepare_for_work(object, child_id)

        for child_id in super(Manager, self).children(id_parent):
            self.prepare_existing_devices(child_id)

    def call_handle_prepare_for_work(self, id_parent):
        for child_id in super(Manager, self).children(id_parent):
            self.call_handle_prepare_for_work(child_id)
            if child_id in self.nodes:
                object = self.nodes[child_id]
                object.handle_prepare_for_work()

    def create_object(self, object_id, user_name_display):
        class_name_str = self.get_type(object_id)
        class_name = Manager.dict_user_name_type_objects[user_name_display]
        object = class_name(class_name_str, object_id)
        Manager.components_for_device[object_id] = []
        self.prepare_for_work(object, object_id)
        object.handle_defaults_loaded(**object.__dict__['defaults_loaded_dict'])
        object.handle_prepare_for_work()
        Manager.nodes[object_id] = object

    def delete_object(self, object_id):
        self.tasks_pool.stop_operation_thread()

        with Manager.nodes[object_id].mutex:
            Manager.nodes[object_id].flag_removing = True
            Manager.nodes[object_id].handle_before_remove_device()

            def delete_id(id):
                del Manager.components[id]

            map(delete_id, Manager.components_for_device[object_id])
            del Manager.components_for_device[object_id]
            del Manager.nodes[object_id]
            self.tasks_pool.restart_operation_thread()
            self.recover_run_functions()
            log.info('Object {0} removed'.format(object_id))

    def get_available_children(self, id_device):
        device = Manager.nodes[id_device]
        available_devices = device.handle_get_available_children()
        self.unregister_all_makers(id_object=id_device)

        for callable_class_name, user_name_display in available_devices:
            if hasattr(callable_class_name, 'cls'):
                type_str = callable_class_name.cls
            else:
                type_str = callable_class_name

            self.register_maker(id_object=id_device, name=user_name_display, type_str=type_str.__name__)

            if user_name_display not in Manager.dict_user_name_type_objects:
                Manager.dict_user_name_type_objects[user_name_display] = callable_class_name

    def get_type(self, node_id):
        type_str = self.type(node_id)[7:]  # cut string 'device.'
        return type_str

    def create_parameter(self, name, object, object_id, list_id_parameters_already_exists, is_copy=True,
                         parameter=None):
        list_name_parameters_already_exists = [self.multi_stub.parameter_call('name', id=id).name for id in list_id_parameters_already_exists]

        if is_copy and name in object.__dict__:
            parameter = object.__dict__[name].get_copy()
        elif is_copy and name not in object.__dict__ and options.args.development_mode:
            return
        elif parameter is None:
            raise Exception(f'{name} is None')

        object.__dict__[name] = parameter
        parameter.parameter_name = name
        parameter.set_multi_stub(self.multi_stub)

        if name not in list_name_parameters_already_exists or options.args.development_mode:  # if parameter doesn't exist
            value_type = parameter.value_type
            id_parameter = getattr(self, utils.create_parameter_definer(value_type)) \
                (id_object=object_id, name=name)
            parameter.id = id_parameter
            getattr(parameter, parameter.visible.create_func)()
            getattr(parameter, parameter.access.create_func)()
            if parameter.choices is not None:
                parameter.set_choices()
            if id_parameter not in list_id_parameters_already_exists:
                parameter.val = getattr(parameter, 'default', None)
            elif parameter.choices is not None:
                is_tuple = type(parameter.choices[0]) is tuple
                if (is_tuple and parameter.val not in zip(*parameter.choices)[0]) \
                        or not is_tuple and parameter.val not in parameter.choices:
                    parameter.val = getattr(parameter, 'default', None)
        elif name in list_name_parameters_already_exists and not options.args.development_mode:
            id_parameter = self.parameter(object_id, name)
            parameter.id = id_parameter
            Manager.inspector.check_parameter_accordance(parameter)

        if is_copy:
            Manager.components[id_parameter] = parameter
            Manager.components_for_device[object_id].append(id_parameter)

    def configure_parameters(self, object, object_id, list_id_parameters_already_exists, list_names):
        for name in list_names:
            self.create_parameter(name, object, object_id, list_id_parameters_already_exists)

    def create_command(self, name, command, object_id):
        list_name_commands_already_exists = list(map(lambda id: self.multi_stub.command_call('name', id=id).name,
                                                self.commands(object_id)))
        command.set_multi_stub(self.multi_stub)
        if name not in list_name_commands_already_exists or options.args.development_mode:  # if event doesn't exist
            result_type = command.result_type
            id_command = getattr(self, utils.create_command_definer(result_type)) \
                (id_object=object_id, name=name)
            command.id = id_command
            command.clear()
            for arg in command.arguments:
                name_arg, value_arg = arg
                command.update_or_create_argument(name_arg, value_arg)
        elif name in list_name_commands_already_exists and not options.args.development_mode:
            id_command = self.command(object_id, name)
            command.id = id_command
            Manager.inspector.check_command_accordance(command)

        Manager.components[id_command] = command
        Manager.components_for_device[object_id].append(id_command)

    def configure_commands(self, object, object_id):
        list_commands = list(filter(lambda attr: type(getattr(object, attr)) is Command, dir(object)))
        for name in list_commands:
            command = object.__dict__[name]
            self.create_command(name, command, object_id)

    def configure_single_event(self, name, event, object_id):
        list_name_events_already_exists = list(map(lambda id: self.multi_stub.event_call('name', id=id).name,
                                               self.events(object_id)))
        event.set_multi_stub(self.multi_stub)
        if name not in list_name_events_already_exists or options.args.development_mode:  # if event doesn't exist
            event.id = self.create_event(id_object=object_id, name=name)
            getattr(event, event.priority.create_func)()
            event.clear()
            for name_arg, value_type in event.arguments:
                value_arg = utils.value_from_rpc(utils.get_rpc_value(value_type))
                event.update_or_create_argument(name_arg, value_arg)
        elif name in list_name_events_already_exists and not options.args.development_mode:
            id_event = self.event(object_id, name)
            event.id = id_event
            Manager.inspector.check_event_accordance(event)

        Manager.components[event.id] = event
        Manager.components_for_device[object_id].append(event.id)

    def configure_events(self, object, object_id):
        list_events = list(filter(lambda attr: type(getattr(object, attr)) is Event, dir(object)))
        for name in list_events:
            object.__dict__[name] = object.__dict__[name].get_copy()
            event = object.__dict__[name]
            self.configure_single_event(name, event, object_id)

    def get_components(self, object_id, component_type):
        ids = getattr(self, component_type)(id_object=object_id)
        #  Function return components in the adapter, except nonexistent.
        return list(self.components[id] for id in ids if id in self.components)

    def get_component_by_name(self, name, object_id, component_type):
        id = getattr(self, component_type)(id_object=object_id, name=name)
        if id in self.components:
            return self.components[id]
        raise ComponentNotFound(f'Can not found \'{name}\' in the \'{self.nodes[object_id].type}\' (id={object_id})')

    def root_id(self):
        return super(Manager, self).root()

    def parent(self, object_id):
        id = super(Manager, self).parent(object_id)
        return Manager.nodes[id] if id in Manager.nodes else None

    def root(self):
        id = self.root_id()
        return Manager.nodes[id] if id in Manager.nodes else None

    def children(self, object_id):
        ids = super(Manager, self).children(object_id)
        return list(Manager.nodes[id] for id in ids if id in Manager.nodes)

    def recover_run_functions(self):
        for id_object in Manager.nodes:
            object = Manager.nodes[id_object]
            self.configure_run_function(object, id_object)

    def configure_run_function(self, object, object_id, list_id_parameters_already_exists=None):
        if not list_id_parameters_already_exists:
            list_id_parameters_already_exists = self.parameters(object_id)

        for name in object.run_function_names:
            time_stamp = time.time()
            period_name = getattr(object, name).period_name
            period = getattr(object, name).period_default_value
            parameter_period = ParameterDouble(default=period, visible=Visible.setup)
            self.create_parameter(period_name, object, object.id, list_id_parameters_already_exists,
                                  is_copy=False, parameter=parameter_period)
            period = parameter_period.val  # Если параметр все-таки существует
            self.tasks_pool.add_task(time_stamp + period, getattr(object, name))

    def get_all_device(self, object_id, result):
        """
        Return list of id of all objects including calling object

        :arg object_id: :class:`~alphalogic_api3.objects.Object` id
        :arg result: result list of id
        """
        list_children = super(Manager, self).children(object_id)
        result.append(object_id)
        map(lambda x: self.get_all_device(x, result), list_children)

    def join(self):
        self.g_thread.start()
        while True:
            time.sleep(0.1)
            if not self.g_thread.is_alive():
                break

    """
    Infinity loop: get state from adapter
    """
    def grpc_thread(self):
        try:
            for r in self.multi_stub.stub_service.states(rpc_pb2.Empty()):
                try:
                    if r.state == rpc_pb2.StateStream.AFTER_CREATING_OBJECT:
                        log.info('Create device {0}'.format(r.id))
                        id_name = self.parameter(r.id, 'type_when_create')
                        rpc_value = self.multi_stub.parameter_call('get', id=id_name).value
                        user_name_display = utils.value_from_rpc(rpc_value)
                        self.create_object(r.id, user_name_display)

                    elif r.state == rpc_pb2.StateStream.BEFORE_REMOVING_OBJECT:
                        log.info('Remove device {0}'.format(r.id))
                        if r.id in Manager.nodes:
                            self.delete_object(r.id)
                        else:
                            log.warn('Object {0} not found'.format(r.id))

                    elif r.state == rpc_pb2.StateStream.GETTING_AVAILABLE_CHILDREN:
                        log.info('Get available children of {0}'.format(r.id))
                        self.get_available_children(r.id)

                    elif r.state == rpc_pb2.StateStream.AFTER_SETTING_PARAMETER:
                        if r.id in Manager.components:
                            if Manager.components[r.id].callback:
                                try:
                                    param = Manager.components[r.id]  # TODO check
                                    device = Manager.nodes[param.owner()]  # TODO check
                                    Manager.components[r.id].callback(device, param)
                                except Exception as err:
                                    t = traceback.format_exc()
                                    log.error('After set parameter value callback error:\n{0}'.format(decode_string(t)))
                        else:
                            log.warn('Parameter {0} not found'.format(r.id))

                    elif r.state == rpc_pb2.StateStream.EXECUTING_COMMAND:
                        if r.id in Manager.components:
                            Manager.components[r.id].call_function()  # try except inside
                        else:
                            log.warn('Command {0} not found'.format(r.id))

                except Exception as err:
                    t = traceback.format_exc()
                    try:
                        log.error('grpc_thread error: {0}'.format(decode_string(t)))
                    except Exception as ultimate_error:  # can't fall here
                        pass

                finally:
                    self.multi_stub.state_call('ack', id=r.id, state=r.state)

        except Exception as err:
            t = traceback.format_exc()
            log.error('grpc_thread error2: {0}'.format(decode_string(t)))
