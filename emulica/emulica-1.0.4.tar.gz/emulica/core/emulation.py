# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
# ## BEGIN LICENSE
# Copyright (C) 2013 Rémi Pannequin, Centre de Recherche en Automatique de
# Nancy remi.pannequin@univ-lorraine.fr
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 3, as published
# by the Free Software Foundation
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranties of
# MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR
# PURPOSE.  See the GNU General Public License for more details
#
# You should have received a copy of the GNU General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>
# ## END LICENSE

"""Emulica, the python Systemic Emulation Modelling and Execution envionnement,
is a SimPy-based simulation package, that enable emulation of manufacturing
systems.

Classes:

    Model -- The main class, that represents an emulation model
    Module -- The root classe for any object that is named in the model
    Product -- Moving entities in the model

    Request -- a message sent to a module that trigger operation
    Report -- a message sent by a module that report events

    Holder -- Module that holds products

    PullObserver -- Module that observe products in a holder, automatic
        observation
    PushObserver -- Module that observe products in a holder, observe when
        requested

    Actuator -- Generic Module that alow transformation on products

    CreateAct -- Actuator that creates new products
    DisposeAct -- Actuator that disposes products (i.e. remove them from the
        model)
    ShapeAct -- Actuator that changes the physical attributes of products
    SpaceAct -- Actuator that moves products
    AssembleAct -- Actuator that assemble one or more products toghether
    DisassembleAct -- Actuator that create several product from one

Function:
    evaluate_property -- evaluate a physical property

Exceptions:
    EmulicaError -- Raised when an excecution occurs during emulation

"""

import random
import logging
import copy

import simpy
from . import properties
from . plot import Monitor

logger = logging.getLogger('emulica.emulation')


# Control utilities
def wait_idle(report_socket):
    """This function may be useful in control sytems. It get repetitively Reports
    on the given socket until found a report with what == 'idle'.

    Arguments
        report_socket -- the report socket to inspect
    """
    finished = False
    while not finished:
        event = yield report_socket.get()
        finished = (event.what == 'idle')


class Module(object):
    """A module is a part of a model. It is identified by its name. This class
    is abstract : it is implemented by modelling primitives (see below) and
    Models (to represent more complex objects).

    Every module send events about its state to its environment (typically its
    control system) using report sockets. Module might also have request socket
    if they are controllable.

    A Module's behaviour is determined by a set of properties (ModuleProperties).

    Attributes:
        * name
            Module's name
        * report_socket
            Store object where report will be put. Using create_report() method
            is recommended
        * request_socket
            Store object where request can be put.
        * accept_observer
            True if the module.create_report_socket will return a valid
            report_socket
        * properties
            a properties.Registry objet, that contain the module's props.

    Signals:
        'state-changed'
            called when the runtime state of the module change. Callback profile:
            cb(state, data)
        'property-changed'
            called when a property definition changes. Callback profile:
            cb(prop, module, data)
        'name-changed'
            called when the name of the module is changed
            cb(name, module, data)
    """

    STATE_CHANGE_SIGNAL = 'state-changed'
    PROPERTIES_CHANGE_SIGNAL = 'property-changed'
    NAME_CHANGE_SIGNAL = 'name-changed'

    def __init__(self, model, name):
        """Create a new instance of Module."""
        self.model = model
        self.name = name
        self.properties = properties.Registry(self, self.model.rng)
        self.__listeners = {Module.STATE_CHANGE_SIGNAL: dict(),
                            Module.PROPERTIES_CHANGE_SIGNAL: dict(),
                            Module.NAME_CHANGE_SIGNAL: dict()}
        self.accept_observer = True
        self.__multiplier = None
        self.report_socket = None
        self.request_socket = None
    
    def fullname(self):
        """Return the module fully qualified name, of the form
        'submodel1.submodel2.module', or 'module2' or 'submodel1.submodel2'"""
        if self.model.is_main:
            return self.name
        return '.'.join([self.model.fullname(), self.name])

    def is_model(self):
        """Return True if this module is a model.
        NB: Overriden by the is_model implementation of Model, that returns True.
        """
        return False

    def initialize(self):
        """Make a module ready to be simulated"""
        self.report_socket = simpy.Store(env=self.get_sim())
        self.request_socket = simpy.Store(env=self.get_sim())
        self.accept_observer = True
        self.__multiplier = None

    def rename(self, new_name):
        """Change the module's name.
        Raise:
            EmulicaError -- if the name is already used in the model
        """
        if new_name in self.model.modules.keys():
            raise EmulicaError(self, _("""Cannot rename module {name} in {new_name}: there is already a module of this name.""").format(name=self.name, new_name=new_name))
        else:
            del self.model.modules[self.name]
            self.name = new_name
            self.model.modules[self.name] = self
            self.emit('name-changed', self.name, self)

    def create_report_socket(self, multiple_observation=False):
        """Create a new Store object in which reports from the module will be put
        Each client should call this method once, and re-use the created object
        during the simulation. If more than one client observe this module, an
        EventMultiplier is activated.

        Arguments:
            multiple_observation
                If True, an EventMultiplier is created, which may slow down
                simulation a bit (default = False)

        Returns:
            a Store that will contain future Report messages

        Raises:
            EmulicaError, if this method is called several time without
            multiple_observation set to True
        """
        if not self.accept_observer:
            raise EmulicaError(self, _("""A new request_socket must be created, but there is already one, and the multiple_observation parameter was not set to True"""))
        if not multiple_observation:
            self.accept_observer = False
            return self.report_socket
        else:
            if self.__multiplier is None:
                self.__multiplier = EventMultiplier(self.get_sim(), self.report_socket)
                self.get_sim().process(self.__multiplier.run())
            return self.__multiplier.create_client()

    def attach_report_socket(self, socket):
        """Attach a Store object, in which report will be put.

        Arguments:
            multiple_observation -- If True, an EventMultiplier is created,
            which may slow down simulation a bit (default = False)
            socket -- the Store in which Reports will be put

        Raises:
            EmulicaError, if this method is called several time without
            multiple_observation set to True
        """
        if not self.accept_observer:
            raise EmulicaError(self, _("""A new request_socket must be created, but there is already one, and the multiple_observation parameter was not set to True"""))
        if self.__multiplier is None:
            self.__multiplier = EventMultiplier(self.get_sim(), self.report_socket)
            self.get_sim().process(self.__multiplier.run())
        self.__multiplier.attach_client(socket)

    def connect(self, signal, handler, *args):
        """Connect a handler with a signal. This method should be used by (graphical) user
        interfaces (Views in the MVC paradigm) of the module (model). When there is a change
        in the model, the update method is called (if it exists) on each observer.

        Arguments:
            signal -- the signal to wait
            handler -- the observer to add in the model
            *args -- arguments passed to the handler when calling back
        """
        self.__listeners[signal][handler] = args

    def emit(self, signal, *args):
        """Trigger a signal."""
        #to prevent bug when deepcopying modules
        if not '__listener' in dir(self):
            return
        for (handler, cb_args) in self.__listeners[signal].items():
            handler(*(args+cb_args))

    def register_signal(self, signal_name):
        """Register a new signal."""
        self.__listeners[signal_name] = dict()

    def __getitem__(self, name):
        """Provide convenient access to the properties of the module."""
        return self.properties[name]

    def __setitem__(self, name, value):
        """Provide convenient access to the properties of the module."""
        self.properties[name] = value

    def current_time(self):
        """Return the simulation current time, by queriying the model
        """
        return self.model.current_time()

    def get_sim(self):
        """Return the SimPy.simulation object of this model"""
        return self.model.get_sim()


class Model(Module):
    """a Model instance is an emulation model. it contains modules and products.

    Attributes:
        modules -- dictionary of modules (including submodels) contained in
                   this model, but excluding the submodel's modules
        products -- dictonary of existing products
        control_classes -- list of registered control classes. contains
                           (control_class, pem, args) tuples.
        control_system -- a list of the instanciated control classes (empty
        before emulation)
        rng -- the model random number generator
        inputs -- the inputs interface of the model a dict of the form
                  input_name => (module_name, property_name)

    Signals:
        'module_added' -- callback(model, module)
        'module_removed' -- callback(model, module)
    """

    def __init__(self, step=False, model=None, name='main', path=None):
        """Initialize the discrete-events simulation core, and activate all modules.
        if it is not specified, seeding is made from system time or from a random source.

        Arguments:
            step -- If true, the SimulationStep alternative simulation library is used
        """
        self.is_main = model is None
        if self.is_main:
            self.sim = None
            self.rng = random.Random()
            Module.__init__(self, self, name)
        else:
            self.rng = model.rng
            Module.__init__(self, model, name)
        self.register_signal('module-added')
        self.register_signal('module-removed')
        self.modules = dict()
        self.control_classes = list()
        self.control_system = list()
        self.inputs = dict()
        if not self.is_main:
            self.products = model.products
            #if not path:
            #    logger.warning(_("a default path will be used"))
            self.path = path or '{0}.emu'.format(name)
            self.model.register_emulation_module(self)
        else:
            self.__next_pid = 1
            self.products = dict()

    def module_list(self):
        """Return the list of modules in this model, and in its submodels"""
        l = list()
        for mod in self.modules.values():
            l.append(mod)
            if mod.is_model():
                l.extend(mod.module_list())
        return l

    def get_module(self, name):
        """Return a module belonging to this model, or to one of its submodels.

        Arguments:
            name -- the module name, in the model name space.

        Returns
            the module instance
        Raises
            EmulicaError if module has not been found
        """
        if name is None or not name:
            logger.warning(_("get_module returned None because name was None or ''"))
            return None
        if name == self.name:
            return self
        names = name.split('.', 1)
        if len(names) == 1:
            if self.is_model():
                return self.modules[names[0]]
            else:
                raise EmulicaError(self, _("""Invalid module name: {0}. Not present in model""").format(name))
        else:
            submodel = self.modules[names[0]]
            return submodel.get_module(names[1])

    def has_module(self, name):
        """Return True, if this module can be found in this model or in one of
        its submdel (i.e. get_module(name) found a module."""
        if name is None or not name:
            return False
        if name == self.name:
            return True
        names = name.split('.', 1)
        if len(names) == 1:
            if self.is_model():
                return names[0] in self.modules.keys()
            else:
                raise EmulicaError(self, _("""Invalid module name: {0}. Not present in model""").format(name))
        else:
            submodel = self.modules[names[0]]
            return submodel.has_module(names[1])

    def is_model(self):
        """Enable to distinguish between a model and a module."""
        return True

    def apply_inputs(self):
        """apply inputs list"""
        for (name, (mod_name, prop_name)) in self.inputs.items():
            #add a property in the module
            module = self.get_module(mod_name)
            display = module.properties.get_display(prop_name)
            value = module.properties.get(prop_name)
            self.properties.add_with_display(name, display.type, value)
            #link the modules property to the model property
            module.properties[prop_name] = "model['{0}']".format(name)
            module.properties.set_auto_eval(prop_name)

    def emulate(self, until, rt=False, callback=lambda: None, step=1, seed=None, rt_factor=1):
        """Wrap SimPy simulate method. At the end of the simulation, trace are flushed.

        Arguments:
            until -- time until when emulation stops
            rt -- If true, emulation is executed in real time mode (default = False)
            callback -- if in step mode, the callback function to use
            stepping_delay --  if in RT mode, the minimun amound of time between two
                               call of the callback function
            seed -- seed used to initialize the random number generator (default = None)
            rt_factor -- real time factor
        """
        if not self.is_main:
            raise EmulicaError(self, _("""Submodels cannot use this method. Only the top level model can be executed."""))
        self.until = until
        self.clear(rt, rt_factor)
        if seed:
            self.rng.seed(seed)
        if step:
            class Timer:
                def run(self, sd, until):
                    """P.E.M. : put the request in the receiver queue and finish"""
                    while self.sim.now < until:
                        yield self.sim.timeout(sd)
                        callback()
            timer_process = Timer()
            timer_process.sim = self.sim
            self.sim.process(timer_process.run(step, until))
            self.sim.run(until=until)
        else:
            self.sim.run(until=until)
        for mod in self.modules.values():
            if 'record_end' in dir(mod):
                mod.record_end()
        for p in self.products.values():
            if p.is_active():
                p.dispose()

    def clear(self, rt=False, factor=1):
        """Clear the model."""
        #init of SimPy
        #if in real-time mode, initialize environment as simpy.rt.RealtimeEnvironment(factor=1)
        if rt:
            self.sim = simpy.rt.RealtimeEnvironment(factor=factor, strict=False)
        else:
            self.sim = simpy.Environment()
        #self.sim.initialize()
        #clean products registry
        self.products = dict()
        self.__next_pid = 1
        self.control_system = list()
        #modules activation
        self.initialize()
        for mod in self.module_list():
            if 'initialize' in dir(mod):
                mod.initialize()

    def stop(self):
        """Stop emulation / simulation"""
        if not self.is_main:
            raise EmulicaError(self, _("""Submodels cannot use this method. Only the top level model can be executed."""))
        logger.info(_("simulation stopped at t={0}").format(self.sim.now))
        #TODO: stop simulation

    def next_pid(self):
        """Return the next available product ID (int)"""
        if self.is_main:
            pid = self.__next_pid
            self.__next_pid += 1
            return pid
        return self.model.next_pid()

    def register_control(self, control_class, pem_name='run', pem_args=None):
        """activate and register in the model a list of control Classes.

        Arguments:
            control class -- The control class (uninstanciated class object)
            pem_name -- the process execution method name (as string)
            args -- an iterable of the arguments of the pem
        """
        args = pem_args or (self,)
        self.control_classes.append((control_class, pem_name, args))

    def register_emulation_module(self, module):
        """Register a module in the model. If the module is a (sub)model, call
        apply_input on it.
        Arguments:
            name -- the module name that will be registered in the model
            module -- the module to register

        Return:
            the modules fully qualified name
        """
        name = module.name
        if name in self.modules.keys():
            raise EmulicaError(self, _("""Cannot create module {0}: there is already a module of this name""").format(name))
        #if name is main, throw an exception
        if name == 'main':
            raise EmulicaError(self, _("'main' is a reserved name"))
        self.modules[name] = module
        if module.is_model():
            module.apply_inputs()
        logger.debug("module {0} added to the model".format(module.name))
        self.emit('module-added', self, module)

    def unregister_emulation_module(self, name):
        """Remove an emulation module from the model. If the module is not
        private, cascade unregister to submodels. If there is no modules of
        this name, do nothing.
        """
        names = name.split('.', 1)
        if len(names) == 1:
            module = self.modules[names[0]]
            del self.modules[names[0]]
            self.emit('module-removed', self, module)
        else:
            submodel = self.modules[names[0]]
            submodel.unregister_emulation_module(names[1])

    def insert_request(self, request):
        """insert the request in the model"""
        class Dispatcher:
            def run(self, request, receiver):
                """P.E.M. : put the request in the receiver queue and finish"""
                yield receiver.request_socket.put(request)
        logger.info(_("inserting request for module {0}".format(request.who)))
        receiver = self.get_module(request.who)
        insert_process = Dispatcher()
        self.sim.process(insert_process.run(request, receiver))

    def initialize(self):
        """Activate the control of the model, and initialize it as a module."""
        #initialize report and request queues by calling Module.initialize(self)
        Module.initialize(self)
        #activate control processes
        for (control_class, pem, args) in self.control_classes:
            process = control_class()
            logger.info(_("registering control process {0}").format(str(process)))
            pem = getattr(process, pem)
            process.sim = self.get_sim()
            self.get_sim().process(pem(*args))
            self.control_system.append(process)

    def new_report_socket(self):
        return simpy.Store(self.get_sim())

    def current_time(self):
        if self.is_main:
            if self.sim is None:
                logger.warning('no simulation instance')
                return 0
            return self.get_sim().now
        return Module.current_time(self)

    def get_sim(self):
        """Return the SimPy.simulation object of this model"""
        if self.is_main:
            return self.sim
        else:
            return self.model.get_sim()

    def clone(self):
        """Return a clone of this model"""
        clone = Model()
        
        
        

class EventMultiplier(object):
    """
    An EventMultiplier is used internally to enable several client to get Report
    from a module.
    """
    def __init__(self, sim, source_socket):
        """Create a new instance of a EventMultiplier.
        Arguments:
            source_socket -- the source of event that must be multiplied
        """
        self.env = sim
        self.source = source_socket
        self.clients = list()

    def run(self):
        """Process Execution Method"""
        while True:
            ev = yield self.source.get()
            for client in self.clients:
                new_ev = copy.copy(ev)
                yield client.put(new_ev)

    def create_client(self):
        """Add a client to the event multiplier.
        Returns:
            a new Store where event will be put
        """
        client = simpy.Store(self.env)
        self.clients.append(client)
        return client

    def attach_client(self, client):
        """Add a client to the event multiplier.

        Arguments:
            store -- the Store to attach
        """
        self.clients.append(client)


class Product(object):
    """A product is an entity that moves in the emulated system
    It is identified by a productID, a productType, and a set of physical
    properties. Physical properties can be accessed with as items (for instance
    prod1['mass'] may be used to access the 'mass' property od product 'prod1'

    Attribute:
        create_time -- time when the product was create
        dispose_time -- time when this product was disposed
        properties -- a dictionary of physical properties
        components -- a dictionary of other products that compose this one
        space_history -- history of space transformations
        shape_history -- history of shape transformations
        composition_history -- history of assembling
    """

    def __init__(self, model, pid=0, product_type='defaultType'):
        """Create a new product with its product identifier given from parameter
        'pid', and its type from parameter 'product_type'
        If 'pid' as already been given to another product or is defaulted,
        The value model.next_pid() is used instead.
        Product type is defaulted to 'defaultType'

        Arguments:
            model -- the emulation model
            pid -- the identifier of the new product instance (default = )
            product_type -- the type of the new product (default = 'defaultType')

        Raises:
            EmulicaError, if the pid has already been given to another product
        """
        if not pid == 0 and pid in model.products:
            raise EmulicaError(model, _("product ID {0} has already been used").format(pid))
        while pid == 0 or pid in model.products:
            pid = model.next_pid()
        self.pid = pid
        self.model = model
        model.products[pid] = self
        if model.get_sim():
            self.create_time = model.current_time()
        else:
            self.create_time = 0
        self.dispose_time = 0
        self.product_type = product_type
        self.properties = properties.Registry(self, model.rng)
        #self.attributes = dict()
        self.components = dict()
        self.space_history = list()
        self.shape_history = list()
        self.composition_history = list()
        self.__active = True
        logger.info(_("product {pid} created at {time}").format(pid=self.pid,
                                                                time=self.create_time))

    def record_position(self, space):
        """
        Add a new element in the trajectory (a list of (date, position)
        tupples) of this product. Date is obtained using now(). This
        method should be called only by space actuators.

        Arguments:
            space -- the new space of the product
        """
        now = self.model.current_time()
        self.space_history.append((now, space))
        for child in self.components.values():
            child.space_history.append((now, space))

    def record_transformation(self, start, end, actuator, program):
        """
        Add a new element in the list of morphological transformations
        (a list of (date, actuator, program) tupples) of this product.
        Date is obtained using now(). This method should be called only
        by shape actuators.

        Arguments:
            actuator -- name of the module executing the transformation
            program -- the program being executed
        """
        self.shape_history.append((start, end, actuator, program))
        for child in self.components.values():
            child.shape_history.append((start, end, actuator, program))

    def dispose(self):
        """
        Dispose this product: dispose time is set to current time.
        """
        if self.__active:
            self.dispose_time = self.model.current_time()
            logger.info(_("product {pid} disposed at {time}").format(pid=self.pid,
                                                                     time=self.dispose_time))
            self.__active = False
        else:
            logger.warning(_("""warning, not disposing product {pid} at {time}: not active""").format(pid=self.pid, time=self.model.current_time()))

    def assemble(self, component, actuator, key=None):
        """
        Aggregate another product (the 'component') with this one, if parameter
        'key' is specified, it can be used to find back the component (e.g. in
        a disassembing process). By default, the key is the number of the added
        component (first is 0).
        """
        self.composition_history.append((self.model.current_time(), actuator, component.pid))
        if key is None:
            key = len(self.components)
        self.components[key] = component

    def disassemble(self, key=None):
        """Disagregate a composite product. Return a component by its key. If no
        key are specified, the componnent with the bigest key is returned (LIFO
        order)."""
        #what if a product has no componnents ? split ?
        if len(self.components) == 0:
            return self
        if key is None:
            #search for the biggest key in dict
            key = -1
            for k in self.components.keys():
                if k > key:
                    key = k
        result = self.components[key]
        del self.components[key]
        return result

    def __getitem__(self, name):
        """Provide convenient access to the properties of the module."""
        return self.properties[name]

    def __setitem__(self, name, value):
        """Provide convenient access to the properties of the module."""
        self.properties[name] = value

    def is_active(self):
        return self.__active


class Request(object):
    """
    A request triggers a change in the meulation model
    It has six attributes: (who, where, why, how, when, what)

    Attributes:
        who -- the entity in the model that must execute the action
        what - the name of the action to be executed
        how - a dictionary of parameters to configure the action
        when -- the date at which the action must be executed
        where -- the location where the action must be executed
                 (i.e. the same as who in most cases)
        why -- a human-readable comment string
    """

    def __init__(self, actor, action, location=None, date=None, comment='', params=None):
        """
        Create a new instance of a Request

        Arguments:
            actor -- the name of the module who must execute the request (who)
            action -- what to execute
            params -- a dictionnary containing instruction on how to perform
                      the request (default = empty dict)
            location -- where the request should take place (usually not
                        usefull) (default = same value as actor)
            date -- the date at when the action must begin (default = now)
            comment -- a human-readable description of the request (why)
                       (default = empty str)
        """
        self.who = actor
        self.where = location or actor
        self.how = params or dict()
        self.why = comment
        self.what = action
        self.when = date

    def __repr__(self):
        """Return a human-readable string representation of a Request"""
        s = _("Request {what} to {who} at t={when}").format(what=self.what,
                                                            who=self.who,
                                                            when=self.when)
        opt_param = list()
        if self.how:
            opt_param.append(_("parameters={0}").format(str(self.how)))
        if self.where:
            opt_param.append(_("location={0}").format(self.where))
        if self.why:
            opt_param.append(_("comment={0}").format(self.why))
        if opt_param:
            return "{0} ({1})".format(s, ", ".join(opt_param))
        return s

    def __eq__(self, other):
        """Test whether two reports or request are equals.
        They are considered equals if all their field are.
        """
        for i in ['who', 'what', 'when', 'where', 'how', 'why']:
            if not getattr(self, i) == getattr(other, i):
                return False
        return True


class Report(object):
    """A report give information about an event that has occured in the emulation model
    It has six attributes: (who, where, why, how, when, what)

    Attributes:
        who -- the entity in the model that relates to the event
        what -- the name of the event that has occured
        how -- a dictionary of parameters that give additionnal information about the event
        when -- the date at which the event took place
        where -- the location where the event has been observed (i.e. the same as who in most cases)
        why -- a human-readable comment string
    """
    def __init__(self, source, event, location=None, date=None, comment='', params=None):
        """Create a new instance of a Request
        Arguments:
            source -- the module that emit the report (who)
            event -- the main information of the report (what)
            location -- the place wher the event took place (where)
            date -- the time at which the event happened (when)
            params -- any additionnal information describing the event (how)
            comment -- an interpretation/explanation of the event (why)
        """
        self.who = source
        self.what = event
        self.when = date
        self.where = location or source
        self.how = params or dict()
        self.why = comment

    def __eq__(self, other):
        """Test whether two reports or request are equals.
        They are considered equals if all their field are.
        """
        for i in ['who', 'what', 'when', 'where', 'how', 'why']:
            if not getattr(self, i) == getattr(other, i):
                return False
        return True

    def __repr__(self):
        """Return a human-readable string representation of a Report"""
        s = _("Report {what} from {who} at t={when}").format(what=self.what,
                                                             who=self.who,
                                                             when=self.when)
        opt_param = list()
        if self.how:
            opt_param.append(_("parameters={0}").format(str(self.how)))
        if self.where:
            opt_param.append(_("location={0}").format(self.where))
        if self.why != None and self.why:
            opt_param.append(_("comment={0}").format(self.why))
        if opt_param:
            return "{0} ({1})".format(s, ", ".join(opt_param))
        return s


class Actuator(Module):
    """
    Abstract class that is used by every module that act on products.

    Attributes:
        resource -- the SimPy Resource associated with this actuator
        trace -- execution trace. A list of tupple of the form '(begin, end, state)'
        performance_ratio -- a positive float that represent the performance ratio
    """
    def __init__(self, model, name):
        """Create an Actuator."""
        Module.__init__(self, model, name)
        self.trace = list()
        self.__rec = list()
        self.performance_ratio = 1.
        self.must_interrupt = False

    def record_begin(self, state):
        """Record resource operation as a list of tupples (start, end, program).
        Program is tre name of the program being executed, or 'setup' or 'failed'
        """
        self.__rec.append((self.model.current_time(), state))
        self.emit(Module.STATE_CHANGE_SIGNAL, state)

    def record_end(self, state=None):
        """Record the end of a state. If the optional parameter state is specified,
        the first record of this state is ended. If not specified, the first
        record of the stack is ended"""
        if not len(self.__rec) == 0:
            if state:
                i = len(self.__rec) - 1
                while self.__rec[i][1] != state and i >= 0:
                    i -= 1
                rec = self.__rec[i]
                self.__rec.remove(rec)
            else:
                rec = self.__rec.pop()
            self.trace.append((rec[0], self.model.current_time(), rec[1]))
        self.emit(Module.STATE_CHANGE_SIGNAL, 'idle')
        #else : throw exception

    def initialize(self):
        """Make a module ready to be simulated"""
        Module.initialize(self)
        #reset traces
        self.trace = list()
        self.__rec = list()
        #reset perf ratio
        self.performance_ratio = 1.
        ##this resource is used to apply faillures on an actuation process
        self.resource = simpy.Resource(env=self.get_sim())
        #ModuleProcess is defined in sub-classes
        self.process = self.ModuleProcess(sim=self.get_sim())
        self.action = self.get_sim().process(self.process.run(self))
        self.emit(Module.STATE_CHANGE_SIGNAL, 'idle')

    def degrade(self, ratio, caller):
        """Degrade or restore performance of an actuator, by multipling its
        performance ratio by ratio. This method will check if the actuator is
        currently running, and if so, cancel it."""
        self.performance_ratio = max(0.0, self.performance_ratio - ratio)
        if self.must_interrupt:
            self.action.interrupt()

    def add_program(self, name, delay, prog_transform=None, prog_resources=[]):
        """Add a program to the actuator's program_table.
        If the actuator is a createAct or a DisposeAct, that don't have program
        tables, an exception is risen.
        The parameter prog_resource enable to model that the program require the
        given resource(s) to be run. By default this parameyter is an empty list
        """
        if 'program_table' in self.properties.keys():
            self.properties['program_table'].add_program(name,
                                                         delay,
                                                         prog_transform,
                                                         prog_resources)
        else:
            logger.warning(_("""Can not add programs to actuator without program tables (create and dispose actuators)"""))


class EmptyModule(Module):
    """Empty module. Just to be able to have an address, and get requests
    """

    def __init__(self, model, name):
        Module.__init__(self, model, name)
        self.model.register_emulation_module(self)

    def initialize(self):
        """Make a module ready to be simulated"""
        Module.initialize(self)
        #self.process = self.ModuleProcess(sim=self.get_sim())
        #self.action = self.get_sim().process(self.process.run(self))

    #class ModuleProcess:
        #def __init__(self, sim):
            #self.env = sim

        #def run(self, module):
            #logger.info(_("""Launching module {0}.""".format(module.name)))
            #while True:
                #request_cmd = yield module.request_socket.get()
                #logger.info(request_cmd)
                #yield module.report_socket.put(request_cmd)


class Failure(Module):
    """A Failure is a Module that enable to model unavaillablilities of resources.
    A Failure can either be complete (i.e. the resource is completely bloqued), or
    partial (i.e. the processing time of the resource is multiplied by a factor).

    Attributes:

    Properties:
        process_list -- a list of Actuators on which to apply the failure
        mtbf -- mean time before failure
        mttr -- mean time to repair (ie failure duration)
        degradadation -- a float
        repeat -- boolean, True if the Failure repeats
    """

    request_params = []

    def __init__(self, model, name, mtbf=None, mttr=None, actuators=list()):
        """Instanciate a new Failure object
        """
        Module.__init__(self, model, name)
        self.properties.add_with_display('process_list',
                                         properties.Display.REFERENCE_LIST,
                                         actuators,
                                         _("Processes"))
        self.properties.add_with_display('mtbf', properties.Display.EVALUABLE, mtbf, _("MTBF"))
        self.properties.add_with_display('mttr', properties.Display.EVALUABLE, mttr, _("MTTR"))
        self.properties.add_with_display('degradation',
                                         properties.Display.FLOAT,
                                         0.,
                                         _("Performance Degradation"))
        self.properties.add_with_display('repeat', properties.Display.BOOL_VALUE, True, _("Repeat"))
        self.model.register_emulation_module(self)

    def get_mtbf(self):
        """Return an evaluation of the mtbf if it is a string
        representing a probability distribution, or else, its value
        """
        try:
            value = self.properties.evaluate('mtbf')
        except TypeError:
            value = self.properties['mtbf']
        return value

    def get_mttr(self):
        """Return an evaluation of the mttr if it is a string
        representing a probability distribution, or else, its value
        """
        try:
            value = self.properties.evaluate('mttr')
        except TypeError:
            value = self.properties['mttr']
        return value

    def add_actuator(self, actuator):
        self.process_list.append(actuators)

    def initialize(self):
        """Make a module ready to be simulated"""
        Module.initialize(self)
        self.process = self.ModuleProcess(sim=self.get_sim())
        self.action = self.get_sim().process(self.process.run(self))

    class ModuleProcess:

        def __init__(self, sim):
            self.env = sim

        def run(self, module):
            """Process Excecution Method"""
            loop = True
            while loop:
                #wait some time before failure
                yield self.env.timeout(module.get_mtbf())
                #preempt resource, record failure
                degradation = module.properties['degradation']
                mttr = module.get_mttr()
                for act in module.properties['process_list']:
                    if degradation > 0.:
                        act.degrade(degradation, module)
                    else:
                        act.degrade(1, module)
                    #report failure
                    report = Report(module.fullname(),
                                    'failure-begin',
                                    params={'mttr': mttr, 'degradation': degradation})
                    yield module.report_socket.put(report)
                    act.record_begin('failure')
                #repair delay
                yield self.env.timeout(mttr)
                #release resource, record end
                for act in module.properties['process_list']:
                    if degradation > 0:
                        act.degrade(-degradation, module)
                    else:
                        act.degrade(-1, module)
                    #report failure end
                    report = Report(module.fullname(),
                                    'failure-end',
                                    params={'mttr': mttr, 'degradation': degradation})
                    yield module.report_socket.put(report)
                    act.record_end('failure')
                loop = module.properties['repeat']


class CreateAct(Actuator):
    """A create actuator instanciate a new emulated product when requested.
    The 'how' attribute of the request is used to tune the creation process:
    if this attribute is a dictionary containing a key 'productID', this ID
    will be used to create the product. If it contains a key 'productType'
    the product created will have this type (a string); If there is a key
    productClass, a product of this class will be instanciated.

    Properties:
        destination -- destination holder
        product_prop -- a list of physical properties that the created product
                        will have

    Attributes:
        quantity_created -- the number of product created

    Raise:
        EmulicaError -- if destination is None when the module is activated
    """

    produce_keyword = 'create'
    request_params = ['productType', 'productID']

    def __init__(self, model, name, destination=None):
        Actuator.__init__(self, model, name)
        self.properties.add_with_display('destination',
                                         properties.Display.REFERENCE,
                                         destination,
                                         _("Destination"))
        self.properties.add_with_display('product_prop',
                                         properties.Display.PHYSICAL_PROPERTIES_LIST,
                                         properties.ChangeTable(self.properties, 'product_prop'),
                                         _("Products properties"))
        self.quantity_created = 0
        self.model.register_emulation_module(self)

    def initialize(self):
        """Reset the module attributes"""
        self.quantity_created = 0
        Actuator.initialize(self)

    class ModuleProcess:
        def __init__(self, sim):
            self.env = sim

        def run(self, module):
            "Process Execution Method"
            if module.properties['destination'] is None:
                exp = EmulicaError(module, _("""This module has not be properly initialized: destination has not been set"""))
                raise exp
            while True:
                ##wait for a request to arrive
                request_cmd = yield module.request_socket.get()
                logger.info(request_cmd)
                now = self.env.now
                if request_cmd.when and request_cmd.when > now:
                    yield self.env.timeout(request_cmd.when - now)
                if 'productID' in request_cmd.how.keys():
                    pid = request_cmd.how['productID']
                else:
                    pid = 0
                if 'productType' in request_cmd.how.keys():
                    prod_type = request_cmd.how['productType']
                else:
                    prod_type = 'defaulType'
                module.quantity_created += 1
                module.emit(Module.STATE_CHANGE_SIGNAL, prod_type)
                prod = Product(module.model, pid, prod_type)
                #Set physical properties of the product
                for (prop, value) in module.properties['product_prop'].items():
                    prod[prop] = value
                if 'physical-properties' in request_cmd.how.keys():
                    for (prop, value) in request_cmd.how['physical-properties'].items():
                        if prop in module.properties['product_prop'].keys():
                            logger.warning(_("""physical property {0} from create request supersedes property from module""").format(prop))
                        prod[prop] = value
                if request_cmd.what == CreateAct.produce_keyword:
                    for ev in module.properties['destination'].put_product(prod):
                        yield ev
                    report = Report(module.fullname(), 'create-done', date=self.env.now)
                    yield module.report_socket.put(report)


class DisposeAct(Actuator):
    """A dispose actuator fetch product from a Holder when requested, and dispose it.

    Attributes:
        source -- source holder

    Raise:
        EmulicaError -- if destination is None when the module is activated
    """

    produce_keyword = 'dispose'
    request_params = []

    def __init__(self, model, name, source=None):
        """instanciate a new Dispose actuator module"""
        Actuator.__init__(self, model, name)
        self.properties.add_with_display('source',
                                         properties.Display.REFERENCE,
                                         source,
                                         _("Source"))
        self.model.register_emulation_module(self)

    class ModuleProcess:
        def __init__(self, sim):
            self.env = sim

        def run(self, module):
            """Process Execution Method"""
            if module.properties['source'] is None:
                raise EmulicaError(module, _("""This module has not be properly initialized: source has not been set"""))
            while True:
                ##wait for a resquest to arrive
                request_cmd = yield module.request_socket.get()
                logger.info(request_cmd)
                now = self.env.now
                if request_cmd.when and request_cmd.when > now:
                    yield self.env.timeout(request_cmd.when - now)
                if request_cmd.what == DisposeAct.produce_keyword:
                    lock_rq = module.properties['source'].lock.request()
                    yield lock_rq
                    prod = module.properties['source'].fetch_product()
                    prod.dispose()
                    module.properties['source'].lock.release(lock_rq)
                    report = Report(module.fullname(), 'dispose-done', date=self.env.now)
                    yield module.report_socket.put(report)
                    module.emit(Module.STATE_CHANGE_SIGNAL, None)


class SpaceAct(Actuator):
    """This actuator change the position of a product.
    It is configured with a program_table (i.e. a dictionary that associate
    a Program with its name.
    execution keyword is 'move'

    Attributes:
        program_table -- a dictionary of programs, identified by their names
        setup -- Setup Matrix
        program -- programm currently set up
    """

    produce_keyword = 'move'
    program_keyword = [('source',
                        properties.Display(properties.Display.REFERENCE,
                                           _("Source"))),
                       ('destination',
                        properties.Display(properties.Display.REFERENCE,
                                           _("Destination")))]
    request_params = ['program']

    def __init__(self, model, name):
        Actuator.__init__(self, model, name)
        self.properties.add_with_display('program_table',
                                         properties.Display.PROGRAM_TABLE,
                                         properties.ProgramTable(self.properties,
                                                                 'program_table',
                                                                 self.program_keyword),
                                         _("Program table"))
        self.properties.add_with_display('setup',
                                         properties.Display.SETUP,
                                         properties.SetupMatrix(self.properties, 0, 'setup'),
                                         _("Setup matrix"))
        self.program = None
        self.model.register_emulation_module(self)

    class ModuleProcess:
        def __init__(self, sim):
            self.env = sim

        def run(self, module):
            """Process Execution Method"""
            while True:
                request_cmd = yield module.request_socket.get()
                logger.info(request_cmd)
                now = self.env.now
                if request_cmd.when and request_cmd.when > now:
                    yield self.env.timeout(request_cmd.when - now)
                ##if requested action is 'setup', perform setup
                new_program = request_cmd.how['program']
                if not new_program in module.properties['program_table'].keys():
                    raise EmulicaError(module,
                                       _("program {0} is not in the program table".format(new_program)))
                if request_cmd.what == 'setup' or (request_cmd.what == SpaceAct.produce_keyword and module.program != new_program):
                    logger.info(_("module {name} doing setup at {t}").format(name=module.name,
                                                                             t=self.env.now))
                    implicit = (module.program != new_program)
                    for yield_elt in self.__setup(new_program, module, implicit):
                        yield yield_elt
                #if requested action is 'produce', perform setup if needed,
                #and transform the product
                if request_cmd.what == SpaceAct.produce_keyword:
                    #retrieve one product from source holder (according to prog)
                    source = module.properties['program_table'][module.program].transform['source']
                    #request own resource (to model failure)
                    resource_rq = module.resource.request()
                    yield resource_rq
                    module.record_begin(module.program)
                    #lock source holder
                    src_lock_rq = source.lock.request()
                    yield src_lock_rq
                    #fetch product from source
                    product = source.fetch_product()
                    #record product position (space name is the name of this actuator)
                    product.record_position(module.fullname())
                    #unlock source
                    source.lock.release(src_lock_rq)
                    #report state change
                    report = Report(module.fullname(),
                                    'busy',
                                    params={'program':module.program},
                                    date=self.env.now)
                    yield module.report_socket.put(report)
                    #transportation delay
                    #multiplied by the degradation ration
                    time = module.properties['program_table'][module.program].time(product)
                    time /= module.performance_ratio
                    #hold (with interruption)
                    self.must_interrupt = True
                    old_ratio = module.performance_ratio
                    left = time
                    while left > 0:
                        try:
                            if module.performance_ratio > 0:
                                #performance is degraded
                                start = self.env.now
                                yield self.env.timeout(left / module.performance_ratio)
                                left = left - module.performance_ratio * left
                            else:
                                #resource is failed : loop on wait indefinitely (until interruption)
                                yield self.env.timeout(1)
                            #The hold statement returns : the production time has completely elapsed
                        except simpy.Interrupt:
                            # process has been interrupted by a failure :
                            # modification of performance ratio
                            left = left - old_ratio * (self.env.now - start)
                            old_ratio = module.performance_ratio
                    self.must_interrupt = False
                    #release resources and record end
                    ##put product in destination holder (according to prog)
                    dest = module.properties['program_table'][module.program].transform['destination']
                    #no need to lock destination (done in put_product)
                    #put product in destination holder
                    for ev in dest.put_product(product):
                        yield ev
                    #release own resouce
                    module.resource.release(resource_rq)
                    module.record_end(module.program)
                    #report state change
                    report = Report(module.fullname(),
                                    'idle',
                                    params={'program': module.program},
                                    date=self.env.now)
                    yield module.report_socket.put(report)

        def __setup(self, new_program, module, implicit):
            """Generate SimPy signals to execute a setup.
            If implicit is true, the setup is *not* reported.
            """
            if not new_program in module.properties['program_table'].keys():
                raise EmulicaError(module, "No program named {0}".format(new_program))
            #setup time : the actuator resource is requested, and released after setup time
            setup = module.properties['setup'].get(module.program, new_program)
            resource_rq = module.resource.request()
            yield resource_rq
            module.record_begin('setup')
            delay = setup
            yield self.env.timeout(delay)
            module.resource.release(resource_rq)
            module.record_end('setup')
            module.program = new_program
            if not implicit:
                report = Report(module.fullname(),
                                'setup-done',
                                params={'program':module.program},
                                date=self.env.now)
                yield module.report_socket.put(report)


class ShapeAct(Actuator):
    """A Shape actuator models morphological transformations of products.
    Execution method is 'make'

    Attributes:
        program_table --
        setup --
        holder --
        program --

    Raises:
        EmulicaError -- if holder has not been set at activation time
    """

    produce_keyword = 'make'
    program_keyword = [('change',
                        properties.Display(properties.Display.PHYSICAL_PROPERTIES_LIST,
                                           _("Physical changes")))]
    request_params = ['program']

    def __init__(self, model, name, holder=None):
        Actuator.__init__(self, model, name)
        self.properties.add_with_display('program_table',
                                         properties.Display.PROGRAM_TABLE,
                                         properties.ProgramTable(self.properties,
                                                                 'program_table',
                                                                 self.program_keyword),
                                         _("Program table"))
        self.properties.add_with_display('setup',
                                         properties.Display.SETUP,
                                         properties.SetupMatrix(self.properties, 0, 'setup'),
                                         _("Setup matrix"))
        self.properties.add_with_display('holder',
                                         properties.Display.REFERENCE,
                                         holder,
                                         _("Holder"))
        self.program = None
        self.model.register_emulation_module(self)

    class ModuleProcess:
        def __init__(self, sim):
            self.env = sim

        def run(self, module):
            """Process Execution Method"""
            if module.properties['holder'] is None:
                raise EmulicaError(self, _("""This module has not be properly initialized: holder has not been set"""))
            while True:
                #wait for a request to arrive
                request_cmd = yield module.request_socket.get()
                logger.info(request_cmd)
                now = self.env.now
                if request_cmd.when and request_cmd.when > now:
                    yield self.env.timeout(request_cmd.when - now)
                ##if requested action is 'setup', perform setup
                if 'program' in request_cmd.how:
                    new_program = request_cmd.how['program']
                else:
                    new_program = module.program
                if request_cmd.what == 'setup' or (request_cmd.what == ShapeAct.produce_keyword and module.program != new_program):
                    logger.info(_("module {name} doing setup at {t}").format(name=module.name,
                                                                             t=self.env.now))
                    implicit = (module.program != new_program)
                    setup = module.properties['setup'].get(module.program, new_program)
                    #request own resource, and record beginning of operation
                    resource_rq = module.resource.request()
                    yield resource_rq
                    module.record_begin('setup')
                    #setup delay
                    delay = setup
                    #hold (with interruption)
                    module.must_interrupt = True
                    old_ratio = module.performance_ratio
                    left = delay
                    while left > 0:
                        try:
                            if module.performance_ratio > 0:
                                #performance is degraded
                                timeout_start = self.env.now
                                yield self.env.timeout(left / module.performance_ratio)
                                left = left - module.performance_ratio * left
                            else:
                                #resource is failed : loop on wait indefinitely (until interruption)
                                yield self.env.timeout(1)
                            #The hold statement returns : the production time has completely elapsed
                        except simpy.Interrupt:
                            # process has been interrupted by a failure :
                            # modification of performance ratio
                            left = left - old_ratio * (self.env.now - timeout_start)
                            old_ratio = module.performance_ratio
                    module.must_interrupt = False
                    module.program = new_program
                    #release own resource, record end
                    module.resource.release(resource_rq)
                    module.record_end('setup')
                    #report if not implicit
                    if not implicit:
                        report = Report(module.fullname(),
                                        'setup-done',
                                        params={'program':module.program},
                                        date=self.env.now)
                        yield module.report_socket.put(report)
                #now do the actual production
                if request_cmd.what == ShapeAct.produce_keyword:
                    #request own resource, record beginning
                    resource_rq = module.resource.request()
                    yield resource_rq
                    #request program's resources
                    #TODO: request a resource allocation lock before, to avoid interlocking
                    prog_res_rq = []
                    for res in module.properties['program_table'][module.program].resources:
                        rq = res.request()
                        prog_res_rq.append(rq)
                        yield rq
                    module.record_begin(module.program)
                    #lock the workplace holder
                    holder_rq = module.properties['holder'].lock.request()
                    yield holder_rq
                    products = module.properties['holder'].get_products()
                    #report busy
                    report = Report(module.fullname(),
                                    'busy',
                                    params={'program':module.program},
                                    date=self.env.now)
                    yield module.report_socket.put(report)
                    product = products[0]
                    if len(products) > 1:
                        logger.warning(_("cannot treat more than one product at once"))
                    time = module.properties['program_table'][module.program].time(product)
                    time /= module.performance_ratio
                    if 'change' in module.properties['program_table'][module.program].transform:
                        #TODO: verify when setting changeset that it is not None !
                        changeset = (module.properties['program_table'][module.program].transform['change'] or {})
                        for (prop, value) in changeset.items():
                            if prop in product.properties.keys():
                                if type(value) == str:
                                    product.properties.eval_and_set(prop, value)
                                else:
                                    product.properties[prop] = value
                            else:
                                logger.warning(_("could not find physical property {0}").format(prop))
                    #record start
                    start = self.env.now
                    #hold (with interruption)
                    module.must_interrupt = True
                    old_ratio = module.performance_ratio
                    left = time
                    while left > 0:
                        try:
                            if module.performance_ratio > 0:
                                #performance is degraded
                                timeout_start = self.env.now
                                yield self.env.timeout(left / module.performance_ratio)
                                left = left - module.performance_ratio * left
                            else:
                                #resource is failed : loop on wait indefinitely (until interruption)
                                yield self.env.timeout(1)
                            #The hold statement returns : the production time has completely elapsed
                        except simpy.Interrupt:
                            # process has been interrupted by a failure :
                            # modification of performance ratio
                            left = left - old_ratio * (self.env.now - timeout_start)
                            old_ratio = module.performance_ratio
                    module.must_interrupt = False
                    #release resources and record end
                    for p in products:
                        p.record_transformation(start,
                                                self.env.now,
                                                module.fullname(),
                                                module.program)
                        #transformation is recorded at the *end* of the transformation period,
                        # and specify both its start and end date
                    #unlock holder
                    module.properties['holder'].lock.release(holder_rq)
                    #release program's resources
                    for res in module.properties['program_table'][module.program].resources:
                        res.release(prog_res_rq)
                    #release own resource, record end
                    module.resource.release(resource_rq)
                    module.record_end(module.program)
                    report = Report(module.fullname(),
                                    'idle',
                                    params={'program':module.program},
                                    date=self.env.now)
                    yield module.report_socket.put(report)


class AssembleAct(Actuator):
    """This module assemble two products : one that is already on its 'assembling holder'
    and another one that is taken from one other product holders
    (according to a program parameter 'source')
    Execution keyword is assemble

    Attributes:
        program_table --
        setup --
        holder --
        program --

    Raises:
        EmulicaError -- if holder has not been set at activation time
    """

    produce_keyword = 'assy'
    program_keyword = [('source', properties.Display(properties.Display.REFERENCE,
                                                     _("Source")))]
    request_params = ['program']

    def __init__(self, model, name, assy_holder=None):
        """instanciate a new Assemble actuator module"""
        Actuator.__init__(self, model, name)
        self.properties.add_with_display('holder',
                                         properties.Display.REFERENCE,
                                         assy_holder,
                                         _("Holder"))
        self.program = None
        self.properties.add_with_display('program_table',
                                         properties.Display.PROGRAM_TABLE,
                                         properties.ProgramTable(self.properties,
                                                                 'program_table',
                                                                 self.program_keyword),
                                         _("Program table"))
        self.properties.add_with_display('setup',
                                         properties.Display.SETUP,
                                         properties.SetupMatrix(self.properties,
                                                                0,
                                                                'setup'),
                                         _("Setup matrix"))
        self.model.register_emulation_module(self)

    class ModuleProcess:
        def __init__(self, sim):
            self.env = sim

        def run(self, module):
            """Process Execution Method"""
            if module.properties['holder'] is None:
                raise EmulicaError(module, _("""This module has not be properly initialized: holder has not been set"""))
            logger.debug(_("starting assembleAct {0}").format(module.name))
            while True:
                request_cmd = yield module.request_socket.get()
                logger.info(request_cmd)
                now = module.model.current_time()
                if request_cmd.when and request_cmd.when > now:
                    logger.debug(_("""module {name} waiting {time}...""").format(name=module.name, delay=request_cmd.when - now()))
                    yield self.env.timeout(request_cmd.when - now)
                ##if requested action is 'setup', perform setup
                if 'program' in request_cmd.how:
                    new_program = request_cmd.how['program']
                else:
                    new_program = module.program
                if request_cmd.what == 'setup' or (request_cmd.what == AssembleAct.produce_keyword and module.program != new_program):
                    now = module.model.current_time()
                    logger.info(_("module {name} doing setup at {t}").format(name=module.name,
                                                                             t=now))
                    implicit = (module.program != new_program)
                    logger.info(_("module {name} doing setup at {t}").format(name=module.name,
                                                                             t=now))
                    for yield_elt in self.__setup(new_program, module, implicit):
                        yield yield_elt
                if request_cmd.what == AssembleAct.produce_keyword:
                    logger.info(_("""module {name} doing assembly at{t}""").format(name=module.name, t=module.model.current_time()))
                    for yield_elt in self.__produce(module):
                        yield yield_elt
                logger.info(_("module {name} ready at {t}").format(name=module.name,
                                                                   t=module.model.current_time()))

        def __setup(self, new_program, module, implicit):
            """Generate SimPy signals to execute a setup. If implicit is true, 
            the setup is *not* reported
            """
            logger.debug(_("begining setup on module {0}").format(module.name))
            setup = module.properties['setup'].get(module.program, new_program)
            #request own resource, and record begining of operation
            resource_rq = module.resource.request()
            yield resource_rq
            module.record_begin('setup')
            #setup delay
            delay = setup / module.performance_ratio
            for elt in self.__hold(delay, module):
                yield elt
            module.program = new_program
            #release own resource, record end
            module.resource.release(resource_rq)
            module.record_end('setup')
            #report
            logger.debug(_("finished setup on module {0}").format(module. name))
            if not implicit:
                report = Report(module.fullname(),
                                'setup-done',
                                params={'program':module.program},
                                date=self.env.now)
                yield module.report_socket.put(report)

        def __produce(self, module):
            #request own resource, record begining
            logger.debug(_("begining assembly on module {0}").format(module. name))
            resource_rq = module.resource.request()
            yield resource_rq
            module.record_begin(module.program)
            #first lock 'master' product
            logger.debug(_("locking holder on module {0}").format(module. name))
            holder_rq = module.properties['holder'].lock.request()
            yield holder_rq
            masters = module.properties['holder'].get_products()
            #then fetch product to assemble from holder
            logger.debug(_("fetching products to assemble in module {0}").format(module. name))
            program = module.properties['program_table'][module.program]
            source = program.transform['source']
            source_rq = source.lock.request()
            yield source_rq
            assemblee = source.fetch_product()
            assemblee.record_position(module.properties['holder'].fullname())
            source.lock.release(source_rq)
            #send a busy report
            start = self.env.now
            yield module.report_socket.put(Report(module.fullname(),
                                                   'busy',
                                                   params={'program':module.program},
                                                   date=self.env.now))
            time = program.time()
            time /= module.performance_ratio
            #TODO: manage physical attribute
            #hold (with interruption)
            for elt in self.__hold(time, module):
                yield elt
            #release resources and record end
            if len(masters) > 1: logger.warning(_("""ignoring product in holder {0} other than the first one""").format(module.properties['holder'].name))
            if len(masters) >= 1:
                masters[0].assemble(assemblee, module.fullname())
                masters[0].record_transformation(start,
                                                self.env.now,
                                                module.fullname(),
                                                module.program)
            else:
                logger.warning(_("assembling with an empty product"))
                for ev in module.properties['holder'].put_product(assemblee):
                    yield ev
            module.properties['holder'].lock.release(holder_rq)
            module.resource.release(resource_rq)
            module.record_end(module.program)
            #send a report
            yield module.report_socket.put(Report(module.fullname(),
                                                   'idle',
                                                   params={'program':module.program},
                                                   date=self.env.now))

        def __hold(self, time, module):
            old_ratio = module.performance_ratio
            while time != 0:
                yield self.env.timeout(time)
                #The hold statement returns : either the production time has
                #completely elapsed, or it has been interrupted by a failure (cancel called)
                #TODO
                #if (self.interrupted()):
                #    time = self.interruptLeft * old_ratio / module.performance_ratio
                #    old_ratio = module.performance_ratio
                #else:
                time = 0


class DisassembleAct(Actuator):
    """This class disassemble the product currently present in unassy_holder, and send
    resulting sub_product to other holder according to current program

    Attributes:
        program_table --
        setup --
        holder --
        program --

    Raises:
        EmulicaError -- if holder has not been set at activation time
    """
    produce_keyword = 'unassy'
    program_keyword = [('destination',
                        properties.Display(properties.Display.REFERENCE, _("Destination")))]
    request_params = ['program']

    def __init__(self, model, name, unassy_holder=None):
        """instanciate a new Disassemble Actuator module"""
        Actuator.__init__(self, model, name)
        self.properties.add_with_display('holder',
                                         properties.Display.REFERENCE,
                                         unassy_holder,
                                         _("Holder"))
        self.properties.add_with_display('setup',
                                         properties.Display.SETUP,
                                         properties.SetupMatrix(self.properties, 0, 'setup'),
                                         _("Setup matrix"))
        self.properties.add_with_display('program_table',
                                         properties.Display.PROGRAM_TABLE,
                                         properties.ProgramTable(self.properties,
                                                                 'program_table',
                                                                 self.program_keyword),
                                         _("Program table"))
        self.program = None
        self.model.register_emulation_module(self)

    class ModuleProcess:
        def __init__(self, sim):
            self.env = sim

        def run(self, module):
            """Process Execution Method"""
            if module.properties['holder'] is None:
                raise EmulicaError(self, _("""This module has not be properly initialized: holder has not been set"""))
            while True:
                logger.debug(_("'disassembleAct {0} waiting for requests").format(module.name))
                request_cmd = yield module.request_socket.get()
                logger.info(request_cmd)
                now = module.current_time()
                if request_cmd.when and request_cmd.when > now:
                    yield self.env.timeout(request_cmd.when - now)
                ##if requested action is 'setup', perform setup
                if 'program' in request_cmd.how:
                    new_program = request_cmd.how['program']
                else:
                    new_program = module.program
                if request_cmd.what == 'setup' or (request_cmd.what == DisassembleAct.produce_keyword and module.program != new_program):
                    implicit = (module.program != new_program)
                    logger.info(_("""module {name} doing setup at {t}""").format(name=module.name, t=module.current_time()))
                    setup = module.properties['setup'].get(module.program, new_program)
                    #request own resource, and record begining of operation
                    resource_rq = module.resource.request()
                    yield resource_rq
                    module.record_begin('setup')
                    #setup delay
                    delay = setup / module.performance_ratio
                    for elt in self.__hold(delay, module):
                        yield elt
                    module.program = new_program
                    #release own resource, record end
                    module.resource.release(resource_rq)
                    module.record_end('setup')
                    #report
                    if not implicit:
                        report = Report(module.fullname(),
                                        'setup-done',
                                        params={'program':module.program},
                                        date=self.env.now)
                        yield module.report_socket.put(report)
                    
                if request_cmd.what == DisassembleAct.produce_keyword:
                    for yield_elt in self.__produce(module):
                        yield yield_elt


        def __produce(self, module):
            #request own resource, record begining
            resource_rq = module.resource.request()
            yield resource_rq
            module.record_begin(module.program)
            logger.debug(_("begining disassembling on module {0}").format(module. name))
            #first lock 'master' product
            holder_rq = module.properties['holder'].lock.request()
            yield holder_rq
            masters = module.properties['holder'].get_products()
            #send a busy report
            yield module.report_socket.put(Report(module.fullname(),
                                                  'busy',
                                                  params={'program':module.program}))
            #TODO: manage physical attribute
            program = module.properties['program_table'][module.program]
            #hold (with interruption)
            time = program.time()
            time /= module.performance_ratio
            for elt in self.__hold(time, module):
                yield elt
            #release resources and record end
            #get component
            #key = program.transform['key']
            if len(masters) > 1:
                logger.warning(_("""ignoring product in holder {0} other than the first one""").format(module.properties['holder'].name))
            if len(masters) >= 1:
                component = masters[0].disassemble()
                #TODO: manage dissembling key !!
            else:
                logger.warning(_("""ignoring request to disassemble: no product in holder {0}""").format(module.properties['holder'].name))
                #send an exception ???
            #send component to destination
            dest = program.transform['destination']
            #dest_rq = dest.lock.request()
            logger.debug(_("""requesting destination holder, to put dissassembled product."""))
            #yield dest_rq
            for ev in dest.put_product(component):
                yield ev
            #dest.lock.release(dest_rq)
            logger.debug(_("releasing destination holder"))
            #release holer and resource
            module.properties['holder'].lock.release(holder_rq)
            logger.debug(_("releasing working holder"))
            module.resource.release(resource_rq)
            logger.debug(_("releasing resource"))
            module.record_end(module.program)
            #send a report
            yield module.report_socket.put(Report(module.fullname(),
                                                  'idle',
                                                  params={'program':module.program},
                                                  date=self.env.now))

        def __hold(self, time, module):
            old_ratio = module.performance_ratio
            while time != 0:
                #TODO: manage failures
                yield self.env.timeout(time)
                time = 0


class Holder(Module):
    """a holder contains products, and can be associated with Observers.
    Product can be accessed using list syntax

    Attributes:
        observers -- a list of observers that monitor this holder
        lock -- a resource that must be requested before accessing the products
        monitor -- a Monitor that record the number of products in the holder
        internal -- a HolderState that represent current spacial setting of the products inside
        the holder capacity -- Holder capacity (0 means infinite capacity)
        speed -- Holder speed (0 means inifinite speed)
    """

    def __init__(self, model, name, speed=0, capacity=0):
        Module.__init__(self, model, name)
        self.observers = list()
        self.properties.add_with_display('capacity',
                                         properties.Display.INT,
                                         capacity,
                                         _("Capacity"))
        self.properties.add_with_display('speed',
                                         properties.Display.FLOAT,
                                         speed,
                                         _("Speed"))
        self.model.register_emulation_module(self)
        self.internal = HolderState(self)

    def initialize(self):
        """Make a module ready to be simulated"""
        Module.initialize(self)
        self.monitor = Monitor(env=self.get_sim())
        self.lock = simpy.Resource(env=self.get_sim(), capacity=1)
        #self.internal = HolderState(self)
        self.emit(Module.PROPERTIES_CHANGE_SIGNAL, 'holder')
        self.emit(Module.STATE_CHANGE_SIGNAL, len(self.internal))
    
    def set_content(self, products):
        """Set products as the content of the holder.
        this should be called before emulation start.
        Arguments:
            products -- the list of products (instance of Products) to use in initialisation
        """
        self.internal.set_content(products)
    
    def put_product(self, product):
        """Insert a product at the tail of the queue.

        Arguments:
            product -- the product that must be inserted
        """
        capacity = self.properties['capacity']
        speed = self.properties['speed']
        pos = self.internal.positions()
        p_last = self.internal.last()
        logger.info("internal state of holder {name} is {pos}".format(name=self.name, pos=pos))
        while capacity > 0 and p_last >= (capacity - 1) and speed != 0:
            logger.info("""t={t}, last product is in position {p} in {holder} and capacity is {c}""".format(t=self.get_sim().now, p=p_last, c=capacity, holder=self.name))
            t = 1. / speed
            yield self.get_sim().timeout(t)
            self.internal.update_positions()
            p_last = self.internal.last()
        logger.info("""t={t}, inserting product in {holder}""".format(t=self.get_sim().now, holder=self.name))
        lock_rq = self.lock.request()
        yield lock_rq
        self.internal.append(product)
        product.record_position(self.fullname())
        self.emit(Module.STATE_CHANGE_SIGNAL, len(self.internal))
        self.__notif_observers(delay=self.internal.observation_delay())
        self.lock.release(lock_rq)

    def fetch_product(self):
        """Remove and return the product currently at the head of the queue.

        Returns:
            the product

        Raise:
            EmulicaError -- if the holder is empty
        """
        if not self.internal.is_first_ready():
            raise EmulicaError(self, _("no product ready in this holder"))
        prod = self.internal.pop()
        self.emit(Module.STATE_CHANGE_SIGNAL, len(self.internal))
        self.__notif_observers(delay=self.internal.observation_delay())
        return prod

    def get_products(self):
        """Return the list of products in the holder (without removing them).

        Returns:
            a list of products in the queue
        """
        return self.internal.product_list()

    def __notif_observers(self, delay):
        """Activate the process excecution method of the observers."""
        self.monitor.observe(len(self.internal))
        for obs in self.observers:
            obs.update(self.internal)
            now = self.model.current_time()
            logger.info(_("""t={now}: reactivating obs {name} (ev is {ev}); product ready at {delayed}""").format(now=now,  delayed=now + delay, ev=obs.process.reactivate, name=obs.name))
            obs.process.reactivate(delay)


class HolderState(object):
    """A HolderState is the internal object used to
    represent the state of products in a holder.

    Attributes:
    positions -- a dictionary that associate positions (as keys) to products

    """
    def __init__(self, parent):
        #__last_time is the time when position in __products have been computed
        self.__last_time = 0
        #__phy_pos the physical position of the products in the HState
        self.__phy_pos = list()
        #__prod the list of products in the HState
        self.__prod = list()
        #__parent: the parent holder
        self.__parent = parent

    def last(self):
        """Return the physical position of the last product in holder"""
        if not len(self.__phy_pos) == 0:
            return self.__phy_pos[-1]
        else:
            return 0

    def positions(self):
        """Return a list of (postion, product) tuples"""
        self.update_positions()
        res = list()
        assert len(self.__phy_pos) == len(self.__prod)
        for i in range(len(self.__prod)):
            res.append((self.__phy_pos[i], self.__prod[i]))
        return res

    def update_positions(self):
        """
        Update position in the __phy_pos list according to speed
        set __last_date to current time.
        """
        elapsed = self.__parent.current_time() - self.__last_time
        block = 0
        #compute the new phy_pos:
        for i in range(len(self.__phy_pos)):
            old_position = self.__phy_pos[i]
            if not self.__parent['speed'] == 0:
                progress = elapsed * self.__parent['speed']
            else:
                progress = old_position
            new_position = max(block, old_position - progress)
            self.__phy_pos[i] = new_position
            block = new_position + 1
        self.__last_time = self.__parent.current_time()

    def observation_delay(self):
        if self.__parent.properties['speed'] == 0 or len(self) == 0:
            delay = 0
        else:
            delay = (self.__phy_pos[0]) / self.__parent.properties['speed']
        return delay

    def append(self, product):
        if not self.__parent['capacity'] == 0:
            initial_pos = self.__parent['capacity'] - 1
        else:
            initial_pos = 0
        self.__phy_pos.append(initial_pos)
        self.__prod.append(product)
        self.update_positions()

    def set_content(self, products):
        pos = 0
        for p in products:
            self.__phy_pos.append(pos)
            self.__prod.append(p)
            #self.update_positions()
            pos += 1

    def pop(self):
        self.update_positions()
        if self.__phy_pos[0] < 1e-9:
            product = self.__prod.pop(0)
            position = self.__phy_pos.pop(0)
        else:
            logger.error("""no product ready at the end of holder (position of first product is {0})""".format(self.__phy_pos[0]))
        self.update_positions()
        return product

    def __len__(self):
        """Return the current number of product in the holder"""
        return len(self.__prod)

    def product_list(self):
        return self.__prod

    def is_first_ready(self):
        return (len(self.__prod) > 0) and (self.__phy_pos[0] < 1e-9)

    def get_first(self):
        return self.__prod[0]

    def __repr__(self):
        return repr(self.__last_time)+ repr(self.__phy_pos)+ repr(self.__prod)+ repr(self.__parent)


class PushObserver(Module):
    """
    An observer gives information about products.

    Attributes:
      event_name -- the name of the event which is raised
      logic -- the Observation logic to use (an Object with trigger and response methods)
    """

    class FirstProductLogic:
        """
        This observation logic is triggered when a new first product is ready in the observed Holder.
        The separation between observer and logic enable to customize the behaviour of an Observer.

        Attributes:
            obs_type -- True if products type should be included in reports
            identify -- True if products ID should be included in reports
            obs_absence -- True if this observer should send report when the product leaves the
                observed zone (i.e. falling edge). In this case the events will have a parameter
                "present" with a boolean value.
        """
        def __init__(self, observer):
            self.__prod = None
            self.observer = observer

        def trigger(self, product_list):
            """check if a new Report should be sent.
            If the product that is at the first position has already been 
            reported, return False.
            """
            product_list.update_positions()
            if product_list.is_first_ready():
                if self.__prod is None or (self.__prod != None and product_list.get_first() != self.__prod):
                    self.__prod = product_list.get_first()
                    logger.info(_("""product {pid} is ready at {time}""").format(pid=self.__prod.pid, time=self.observer.current_time()))
                    return True
                else:
                    return False
            else:
                logger.info(_("""no products ready at {time} ({internal_state})""").format(time=self.observer.current_time(), internal_state=product_list))
                self.__prod = None
                return False
        
        def is_gone(self, product_list):
            """Check if the product that triggered the observer is gone (and 
            thus that we need to report a product absence)"""
            return self.__prod is None or (len(product_list) and self.__prod != product_list.get_first())
            
        
        def response(self, product_list):
            """Return a list of reports to send"""
            report = Report(self.observer.name,
                            self.observer.properties['event_name'],
                            location=self.observer.properties['holder'].name,
                            date=self.observer.get_sim().now)
            if self.observer.properties['observe_type']:
                report.how['productType'] = self.__prod.product_type
            if self.observer['identify']:
                report.how['productID'] = self.__prod.pid
            if self.observer['observe_absence']:
                report.how['present'] = True
            return report

    def __init__(self, model, name, event_name=None, observe_type=True, identify=False, holder=None, observe_absence=False):
        """Create a new instance of an Observer

        Observers take a list of products as inputs (from a product Holder).
        A first function (on the list) is then applied to decide whether the observer
        is triggered, or not. Then, a filtering function is called, to compute the
        Report object according to the input.

        Arguments:
            name -- module name
            event_name -- the name of the event which is raised 
                          (default = None, then the name of the observer is used instead)
            observe_type -- True if products type should be included in reports (default = True)
            identify -- True if products ID should be included in reports (default = False)
            observe_absence -- True if this observer should send report when the product leaves the
                observed zone (i.e. falling edge). In this case the events will have a parameter
                "present" with a boolean value. (default = False)
        """
        Module.__init__(self, model, name)
        self.properties.add_with_display('event_name',
                                         properties.Display.VALUE,
                                         event_name or name,
                                         _("Event Name"))
        self.properties.add_with_display('holder',
                                         properties.Display.REFERENCE,
                                         holder,
                                         _("Holder"))
        def prop_changed(prop, module):
            if prop == 'holder' and not module[prop] is None:
                module[prop].observers.append(module)
        self.connect(Module.PROPERTIES_CHANGE_SIGNAL, prop_changed)
        if holder != None:
            holder.observers.append(self)
        self.properties.add_with_display('identify',
                                         properties.Display.BOOL_VALUE,
                                         identify,
                                         _("Observe identity"))
        self.properties.add_with_display('observe_type',
                                         properties.Display.BOOL_VALUE,
                                         observe_type,
                                         _("Observe Type"))
        self.properties.add_with_display('observe_absence',
                                         properties.Display.BOOL_VALUE,
                                         observe_absence,
                                         _("Observe Absence"))
        self.logic = PushObserver.FirstProductLogic(self)
        self.product_list = HolderState(self)
        self.model.register_emulation_module(self)

    def initialize(self):
        """Make a module ready to be simulated"""
        Module.initialize(self)
        self.process = self.ModuleProcess(sim=self.get_sim())
        self.get_sim().process(self.process.run(self))

    class ModuleProcess:

        def __init__(self, sim):
            self.env = sim
            self.__reactivate = self.env.event()
            self.reactivate_dates = []
            self.last_report = None

        def __wait_and_reactivate(self, delay):
            delayed = self.env.now + delay
            logger.info(_("t={now}: will reactivate observer at {delayed}").format(now=self.env.now,
                                                                                   delayed=delayed))
            yield self.env.timeout(delay)
            self.reactivate_dates.remove(delayed)
            self.__reactivate_now()

        def __reactivate_now(self):
            logger.info(_("t={now}: reactivating obs (ev is {ev})").format(now=self.env.now,
                                                                           ev=self.__reactivate))
            self.__reactivate.succeed()
            self.__reactivate = self.env.event()
            logger.info(_("""t={t}: observator reactivated; new reactivate event is {ev} """).format(t=self.env.now, ev=self.__reactivate))

        def reactivate(self, delay):
            if delay == 0:
                self.__reactivate_now()
            else:
                delayed = self.env.now + delay
                if not delayed in self.reactivate_dates:
                    self.reactivate_dates.append(delayed)
                    self.env.process(self.__wait_and_reactivate(delay))
                else:
                    logger.info("not adding reactivation: already running.")

        def run(self, module):
            """Process Execution Method"""
            while True:
                if not module.logic.trigger(module.product_list):
                    logger.info(_("t={t}: product not ready").format(t=self.env.now))
                    if self.last_report is not None and module.logic.is_gone(module.product_list):
                        #send message about product no longer present
                        rp = self.last_report
                        rp.how['present'] = False
                        yield module.report_socket.put(rp)
                        self.last_report = None
                    if len(module.product_list):
                        #schedule event when product is ready ?
                        #TODO: compute ready date
                        #yield self.env.timeout(0.1)
                        pass
                    else:
                        module.emit(Module.STATE_CHANGE_SIGNAL, False)
                else:
                    module.emit(Module.STATE_CHANGE_SIGNAL, True)
                    reports = module.logic.response(module.product_list)
                    if module.properties['observe_absence']:
                        self.last_report = reports
                    logger.info(_("t={0}: observation done!").format(self.env.now))
                    yield module.report_socket.put(reports)
                logger.info(_("""t={t}: observator passivated; waiting for event {ev} """).format(t=self.env.now, ev=self.reactivate))
                #yield passivate, self
                yield self.__reactivate
                logger.info(_("t={t}: observator reactivated...").format(t=self.env.now))

    def report_now(self):
        """Generate a report based on the current product queue"""
        if self.logic.trigger(self.product_list):
            self.emit(Module.STATE_CHANGE_SIGNAL, True)
            reports = self.logic.response(self.product_list)
            yield self.report_socket.put(reports)

    def update(self, product_list):
        """Update the internal product list.
        This method is called by the observed Holder before reactivating the module.
        Arguments:
            product_list -- a HolderState object describing current holder state.
        """
        self.product_list = product_list


class PullObserver(Module):
    """This observer is trigerred when a Request is received (action keyword "query").
    So, the control system 'pull' observation events.

    Attributes:
        logic -- the observation logic (an object with a response method)
    """
    produce_keyword = 'observe'
    request_params = []

    class PositionLogic:
        """
        This Observation logic return position information for all the products
        in the observed holder.

        Attributes:

        """
        def __init__(self, observer):
            """Create a new instance of a PositionLogic"""
            self.observer = observer

        def trigger(self, product_list):
            return True

        def response(self, product_list):
            """Return one report that give for each product its ID, type and
             position"""
            r = Report(self.observer.name,
                       self.observer['event_name'],
                       location=self.observer['holder'].name,
                       date=self.observer.current_time())
            id_by_position = dict()
            type_by_position = dict()
            for position, product in product_list.positions():
                id_by_position[position] = product.pid
                type_by_position[position] = product.product_type
            r.how['ID_by_position'] = id_by_position
            r.how['Type_by_position'] = type_by_position
            return r

    def __init__(self, model, name, event_name=None, holder=None):
        """Create e new intance of a PullObserver"""
        Module.__init__(self, model, name)
        self.logic = PullObserver.PositionLogic(self)
        self.properties.add_with_display('event_name',
                                         properties.Display.VALUE,
                                         event_name or name,
                                         _("Event Name"))
        self.properties.add_with_display('holder',
                                         properties.Display.REFERENCE,
                                         holder,
                                         _("Holder"))
        self.model.register_emulation_module(self)

    def initialize(self):
        """Make a module ready to be simulated"""
        Module.initialize(self)
        self.process = self.ModuleProcess(sim=self.get_sim())
        self.get_sim().process(self.process.run(self))

    class ModuleProcess:
        def __init__(self, sim):
            self.env = sim

        def run(self, module):
            """Process Execution Method"""
            if module.properties['holder'] is None:
                #TODO: raise exception
                logger.error("no holder has been set")
            product_list = module.properties['holder'].internal
            while True:
                request_cmd = yield module.request_socket.get()
                logger.info(request_cmd)
                now = module.current_time()
                if request_cmd.when and request_cmd.when > now:
                    yield self.env.timeout(request_cmd.when - now)
                product_list.update_positions()
                module.emit(Module.STATE_CHANGE_SIGNAL, True)
                reports = module.logic.response(product_list)
                logger.info(_("t={0}: observation done!").format(now))
                yield module.report_socket.put(reports)


class EmulicaError(Exception):
    """Exception in the Emulica module

    Attributes:
        module -- the module where the exception has been raised
        time -- the time when the error was raised (default = None, then the
            value of now() is used)
        exception -- the error message
    """
    def __init__(self, module, exception=None, err_time=None):
        if exception:
            self.module = module
            self.err_time = err_time or module.model.current_time()
            self.exception = exception
            Exception.__init__(self, _("""(module {name}, t={time}): {message}""").format(name=self.module.name, time=self.err_time, message=self.exception))
        else:
            #in this case, module is a string
            Exception.__init__(self, module)
