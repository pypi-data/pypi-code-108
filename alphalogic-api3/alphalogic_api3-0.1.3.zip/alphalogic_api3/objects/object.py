# -*- coding: utf-8 -*-
import sys
import traceback
from threading import Lock
from alphalogic_api3.objects.event import Event
from alphalogic_api3.objects.command import Command
from alphalogic_api3.objects.parameter import Parameter, ParameterString, ParameterBool, ParameterLong
from alphalogic_api3.attributes import Visible, Access
from alphalogic_api3.manager import Manager
from alphalogic_api3.logger import log
from alphalogic_api3.utils import Exit, decode_string
from alphalogic_api3 import init


class Object:
    """
    Adapter object can have a number of interactions (parameters, commands, events) and run functions.
    All the declarations of the object interactions must be placed inside the Object class body.
    Each of them must have a unique name among instances of the same class.
    """
    manager = Manager()

    name = ParameterString(visible=Visible.setup, access=Access.read_only)
    displayName = ParameterString(visible=Visible.setup, access=Access.read_write)
    desc = ParameterString(visible=Visible.setup, access=Access.read_write)
    type_when_create = ParameterString(visible=Visible.hidden, access=Access.read_only)
    isService = ParameterBool(visible=Visible.common, access=Access.read_write)
    connected = ParameterBool(visible=Visible.common, access=Access.read_only)
    ready_to_work = ParameterBool(visible=Visible.common, access=Access.read_only)
    error = ParameterBool(visible=Visible.common, access=Access.read_only)
    number_of_errors = ParameterLong(visible=Visible.setup, access=Access.read_write)
    status = ParameterString(visible=Visible.common, access=Access.read_only)

    def __init__(self, type_device, id_device, **kwargs):
        self.__dict__['log'] = log
        self.__dict__['type'] = type_device
        self.__dict__['id'] = id_device
        self.__dict__['flag_removing'] = False
        self.__dict__['mutex'] = Lock()
        # this arguments will be used in creation of Object's subclass
        self.__dict__['defaults_loaded_dict'] = kwargs if kwargs else {}

        # Parameters
        list_parameters_name = list(filter(lambda attr: type(getattr(self, attr)) is Parameter, dir(self)))
        for name in list_parameters_name:
            if name in type(self).__dict__:
                self.__dict__[name] = type(self).__dict__[name]
            elif name in Object.__dict__:
                self.__dict__[name] = Object.__dict__[name]
            elif name in Root.__dict__:
                self.__dict__[name] = Root.__dict__[name]

        # Commands
        is_callable = lambda x: callable(getattr(self, x)) and not x.startswith('_') and\
                                hasattr(getattr(self, x), 'result_type')
        list_command_name = list(filter(is_callable, dir(self)))
        for name in list_command_name:
            self.__dict__[name] = Command(self, type(self).__dict__[name])

        # Events
        for name in list(filter(lambda attr: type(getattr(self, attr)) is Event, dir(self))):
            self.__dict__[name] = type(self).__dict__[name]

        # Run functions
        is_runnable = lambda x: callable(getattr(self, x)) and not x.startswith('_') and\
                                hasattr(getattr(self, x), 'runnable')
        self.__dict__['run_function_names'] = list(filter(is_runnable, dir(self)))

    def parameters(self):
        """
        Return parameters of the object

        :rtype: list of :class:`~alphalogic_api3.objects.parameter.Parameter`
        """
        return self.manager.get_components(self.id, 'parameters')

    def events(self):
        """
        Return events of the object

        :rtype: list of :class:`~alphalogic_api3.objects.event.Event`
        """
        return self.manager.get_components(self.id, 'events')

    def commands(self):
        """
        Return commands of the object

        :rtype: list of :class:`~alphalogic_api3.objects.command.Command`
        """
        return self.manager.get_components(self.id, 'commands')

    def parameter(self, name):
        """
        Get parameter by name

        :arg name: parameter name
        :rtype: :class:`~alphalogic_api3.objects.parameter.Parameter`
        """
        return self.manager.get_component_by_name(name, self.id, 'parameter')

    def event(self, name):
        """
        Get event by name

        :arg name: event name
        :rtype: :class:`~alphalogic_api3.objects.event.Event`
        """
        return self.manager.get_component_by_name(name, self.id, 'event')

    def command(self, name):
        """
        Get command by name

        :arg name: command name
        :rtype: :class:`~alphalogic_api3.objects.command.Command`
        """
        return self.manager.get_component_by_name(name, self.id, 'command')

    def parent(self):
        """
        Get parent object

        :rtype: parent :class:`~alphalogic_api3.objects.Object`
        """
        return self.manager.parent(self.id)

    def root(self):
        """
        Get root object

        :rtype: :class:`~alphalogic_api3.objects.Root`
        """
        return self.manager.root()

    def children(self):
        """
        Get child objects

        :rtype: list of child :class:`~alphalogic_api3.objects.Object`
        """
        return self.manager.children(self.id)

    def get_type(self):
        """
        Return :class:`~alphalogic_api3.objects.Object` type

        :rtype: str
        """
        return self.manger.get_type(self.id)

    def get_all_device(self):
        """
        Return list of id of all objects including calling object

        :rtype: list of id
        """
        result = []
        self.manager.get_all_device(self.id, result)
        return result

    def is_connected(self, id_object):
        """
        Return True if object has connected state

        :rtype: bool
        """
        return self.manager.is_connected(self.id)

    def is_error(self, id_object):
        """
        Return True if object has error state

        :rtype: bool
        """
        return self.manager.is_error(self.id)

    def is_ready_to_work(self, id_object):
        """
        Return True if object is ready to work

        :rtype: bool
        """
        return self.manager.is_ready_to_work(self.id)

    def state_no_connection(self, reason):
        """
        Set no connection object state
        """
        self.manager.state_no_connection(self.id, reason=reason)

    def state_connected(self, id_object, reason):
        """
        Set connected object state
        """
        self.manager.state_connected(self.id, reason=reason)

    def state_error(self, id_object, reason):
        """
        Set error object state
        """
        self.manager.state_error(self.id, reason=reason)

    def state_ok(self, id_object, reason):
        """
        Set ok object state (ready to work)
        """
        self.manager.state_ok(self.id, reason=reason)

    '''
    def __getattr__(self, name):
        return self.__dict__[name]
     
    def __setattr__(self, name, value):
        if issubclass(type(value), Parameter):
            self.parameters.append(name)
            value.name = name
            self.__dict__[name] = value
    '''
    def handle_get_available_children(self):
        """
        Handler is executed before object will be removed
        Parameters, commands, events have already created.
        """
        return []

    def handle_before_remove_device(self):
        """
        Handler is executed before object will be removed
        Parameters, commands, events have already created.
        """
        pass

    def handle_prepare_for_work(self):
        """
        Handler is executed before work of object
        Parameters, commands, events have already created.
        """
        pass

    def handle_defaults_loaded(self, **kwargs):
        """
        Handler for configure Object after creation.
        Parameters, commands, events have already created.
        """
        if kwargs:
            for param_name in kwargs:
                if param_name in self.__dict__:
                    self.__dict__[param_name].val = kwargs[param_name]
                else:
                    raise Exception('Unknown parameter {0}'.format(param_name))


class Root(Object):
    """
    Root object inherits from :class:`~alphalogic_api3.objects.Object`.
    This kind of object is a child for the adapter service node. Root object is created automatically when starting the adapter instance.

    :arg host: hostname of the gRPC stub instance of the composite adapter
    :arg port: port of the gRPC stub instance of the composite adapter
    """

    version = ParameterString(visible=Visible.setup, access=Access.read_only)

    def __init__(self):
        try:
            host, port = init()
            self.manager.start_threads()
            self.joinable = False
            self.manager.configure_multi_stub(host + ':' + str(port))
            id_root = self.manager.root_id()
            type_device = self.manager.get_type(id_root)
            super().__init__(type_device, id_root)

            log.info(f'Connecting to {host}:{port}')
            self.init(id_root)
            self.joinable = True
            log.info('Root connected OK')

        except Exception as err:
            t = traceback.format_exc()
            log.error(decode_string(t))  # cause Exception can raise before super(Root)
            self.manager.tasks_pool.stop_operation_thread()
            log.info('The attempt of stub\'s run was failed')
            sys.exit(2)

    def init(self, id_root):
        list_id_device_exist = []
        self.manager.get_all_device(id_root, list_id_device_exist)
        list_need_to_delete = set(Manager.nodes.keys()) - set(list_id_device_exist)
        map(self.manager.delete_object, list_need_to_delete)
        Manager.components_for_device[id_root] = []
        self.manager.prepare_for_work(self, id_root)
        self.manager.prepare_existing_devices(id_root)
        self.manager.call_handle_prepare_for_work(id_root)
        self.handle_prepare_for_work()

    def join(self):
        """
        Wait until all threads within stub process terminate.
        This function provides an infinite communication loop between the adapter core and gRPC stub instance.
        Must be placed in the code of the adapter to keep it working till the process be stopped by the user or an error happens.
        """
        if self.joinable:
            try:
                self.manager.join()
            except Exit:
                log.info('Stub receive exit signal')
            except BaseException as err:
                t = traceback.format_exc()
                log.error('Root join error: {0}'.format(decode_string(t)))
            finally:
                try:
                    self.manager.tasks_pool.stop_operation_thread()
                    self.manager.multi_stub.channel.close()
                    if self.manager.g_thread.is_alive():
                        self.manager.g_thread.join()
                except BaseException as err:
                    t = traceback.format_exc()
                    log.error('Root finally join error: {0}'.format(decode_string(t)))
            log.info('Stub has stopped successfully')
