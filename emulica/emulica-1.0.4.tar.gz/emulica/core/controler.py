# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
### BEGIN LICENSE
# Copyright (C) 2013 Rémi Pannequin, Centre de Recherche en Automatique de Nancy 
# remi.pannequin@univ-lorraine.fr
# This program is free software: you can redistribute it and/or modify it 
# under the terms of the GNU General Public License version 3, as published 
# by the Free Software Foundation.
# 
# This program is distributed in the hope that it will be useful, but 
# WITHOUT ANY WARRANTY; without even the implied warranties of 
# MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR 
# PURPOSE.  See the GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along 
# with this program.  If not, see <http://www.gnu.org/licenses/>.
### END LICENSE
"""
This module enable running simulation/emulation model with various time advances
strategies (discrete-events, real-time, hybrid). It also support running emulation
model across a network.
"""


from . import emuML, emulation
import time, threading, traceback, sys
from twisted.protocols.basic import LineReceiver
from twisted.internet.protocol import Factory
from twisted.internet import reactor
import logging
import copy

EVENT_TIME = 1
EVENT_FINISH = 2
EVENT_START = 3
EXCEPTION = 4
NAME = 'emulator'
ACTIONS = ['start', 'stop', 'resume', 'pause']

logger = logging.getLogger('emulica.controler')

class TimeControler(threading.Thread):
    """This class enable to execute a simulation or emulation model in a new thread.
    Time avance mode can be either discrete-events or real-time. In real-time, 
    the simulation time advance according to the system time (multiplied 
    by a coefficient, called real-time factor) 
    
    Attributes:
        model -- the model being executed
        real_time -- boolean indicating if run mod is real_time
        rt_factor -- real time factor
        until -- time limit for simulation execution
        finished_condition -- a threading.Condition that is notified when execution stops
        finished -- boolean, True if simulation is finished
        paused -- boolean, True if model is paused
        
    Signals:
        EVENT_TIME -- signal trigerred when time change in the simulation
        EVENT_FINISH -- signal trigerred when execution finish
        EVENT_START -- signal triggered when execution begins
        EXCEPTION -- signal triggered when execution encounter an exception
                     callback handler(Exception e, traceback tb)
                     NB: the tb is the result of the extract_tb of module traceback
    """
    
    
    
    def __init__(self, model, real_time=False, rt_factor=1, until=0, step=-1):
        """Create a new instance of a TimeControler
        
        Arguments:
            model -- the model to run
            real_time -- whether or not run real-time (default = False)
            rt_factor -- real-time factor
            until -- limit time for run
            step -- if true, EVENT_TIME is called at each event. If real time is
                    true, step is forced to true. (default = False)
        """
        threading.Thread.__init__(self)
        self.model = model
        self.real_time = real_time
        self.rt_factor = rt_factor
        self.until = until
        if step == -1:
            self.step = 1 / rt_factor
        else:
            self.step = step
        self.setDaemon(True)
        self.paused = False
        self.finished = False
        self.__pause_condition = threading.Condition()
        self.__pause_delay = 0
        self.callbacks = {EVENT_TIME: [], EVENT_FINISH: [], EVENT_START: [], EXCEPTION: []}
        self.__event_condition = threading.Condition()
        
    def run(self):
        """Start the thread"""
        for c in self.callbacks[EVENT_START]:
            c(self.model)
        try:
            if self.until == 0 and not self.real_time:
                raise RunTimeError(_("a time limit must be set if executing in discrete-events mode"))#@UndefinedVariable
            self.__begin = time.time()
            self.model.emulate(self.until, 
                               rt = self.real_time, 
                               step = self.step, 
                               callback = self.__callback, 
                               rt_factor=self.rt_factor)
        except Exception as e:
            #extract line number and pass it to the handler...
            tb = traceback.extract_tb(sys.exc_info()[2])
            traceback.print_exc()
            logger.warning(e)
            logger.warning(tb)
            for handler in self.callbacks[EXCEPTION]:
                handler(e, tb)
        finally:
            for c in self.callbacks[EVENT_FINISH]:
                c(self.model)

    def __delay(self):
        """Returns system time elapsed from the begining of simulation"""
        return time.time() - self.__begin - self.__pause_delay
    
    def __correction(self):
        """Returns the real-time correction to apply"""
        delta = (self.model.sim.now / self.rt_factor) - self.__delay() - 0.002
        return max(delta, 0.0)
    
    def __callback(self):
        """Method that is called after every simulation event """
        if self.paused:
            self.__pause_condition.acquire()
            self.__pause_condition.wait()
            self.__pause_condition.release()
        #delta = self.__correction()
        #if not delta == 0:
        for c in self.callbacks[EVENT_TIME]:
            c(self.model)
        #else:
        #    logger.debug('delta == 0')
        #if self.real_time:
        #    #wait for a timeout (delta) or for an interruption
        #    self.__event_condition.acquire()
        #    self.__event_condition.wait(delta)
        #    self.__event_condition.release()
        #print "elapsed=%f, st=%f, correction=%f"%(self.__delay(), self.model.current_time(), delta)
    
    def add_callback(self, callback, event):
        """Add a callback on event
        
        Arguments:
            callback -- function to call (it will called with the model as parameter)
            event -- the event on which the callback is registered (see constants of this module)
        """
        self.callbacks[event].append(callback)
    
    def pause(self):
        """Pause emulation"""
        self.__pause_condition.acquire()
        self.__pause_begin = time.time()
        self.paused = True
        self.__pause_condition.release()
    
    def resume(self):
        """Resume emulation"""
        self.__pause_condition.acquire()
        self.__pause_delay += time.time() - self.__pause_begin
        self.paused = False
        self.__pause_condition.notify()
        self.__pause_condition.release()
    
    def stop(self):
        """Stop emulation"""
        self.model.stop()
    
    def dispatch(self, request):
        """Send a request to an emulation module."""
        if request.who == NAME:
            if request.what in ACTIONS:
                logger.debug(_("Request {0.who} to {0.what}").format(request))
                action = getattr(TimeControler, request.what)
                action(self)
            else:
                logger.warning(_("Unknown action {0}".format(request.what)))
        elif self.model.has_module(request.who):
            #insert event in model
            logger.info(_("Inserting request for module {0.who} to do {0.what} into model").format(request))
            self.model.insert_request(request)
            #interrupt sleep
            #self.__event_condition.acquire()
            #self.__event_condition.notify()
            #self.__event_condition.release()
        else:
            logger.warning(_("unknown module {0}").format(request.who))


class EmulationServer:
    """This class implements a TCP server that runs an emulation model. 
    This server can receive Requests, and sent Reports : it take requests as 
    input, and send them to the right emulation module (using a dispatch 
    method). When reports are generated by modules, it send them to clients.
    
    Attributes:
        model -- the emulation model
        factory -- twisted's Factory
    """
    
    def __init__(self, model, port, rt_factor=1.):
        """Create an instance of an EmulationServer"""
        self.factory = Factory()
        self.factory.protocol = EmulationProtocol
        self.factory.clients = dict()
        self.factory.app = self
        self.port = port
        self.model = model
        self.rt_factor = rt_factor
    
    def start(self):
        """Start the server"""
        reactor.listenTCP(self.port, self.factory)#@UndefinedVariable
        reactor.run()#@UndefinedVariable
    
    def initialize_controler(self, client):
        """Make the emulation thread ready to run"""
        #first make a deepcopy of the emulation model
        new_model = copy.deepcopy(self.model)
        #create a new controller instance and initialize it
        controler = TimeControler(new_model, real_time=True, rt_factor=self.rt_factor, until=100000, step=True)
        controler.add_callback(client.notify_stop, EVENT_FINISH)
        controler.add_callback(client.notify_start, EVENT_START)
        controler.add_callback(client.notify_time, EVENT_TIME)
        #add callback to generate emulator reports, using the ReportSource class
        controler.model.register_control(ReportSource, pem_args = (controler.model, client.send_report))
        #store client and corresponding controler
        self.factory.clients[client] = controler


class ReportSource:
    """This simPy Process is used to get Reports from emulation modules."""
    def run(self, model, send):
        """PEM : create a Store, and attach it to every module in the model"""
        r = model.new_report_socket()
        for module in model.module_list():
            module.attach_report_socket(r)
            logging.info(_("attaching reports store to module {0}").format(module.name))
        while True:
            report = yield r.get()
            send(report)


class EmulationProtocol(LineReceiver):
    """
    This class is the protocol used by the server...
    First version of the protocol: only one client can connect !
    """
    delimiter = b"\n"
    MAX_CLIENT = 100
    
    def connectionMade(self):
        """Serve a client, that has just opened a connection. 
        """
        if len(self.factory.clients) < EmulationProtocol.MAX_CLIENT:
            logging.info(_("connection opened by {0}").format(self.transport.getPeer().host))
            self.factory.app.initialize_controler(self)
            self.send_report(emulation.Report(NAME, 'ready'))
        else:
            self.sendLine(_("Another client is already connected: disconnecting..."))
            self.transport.loseConnection()
       
    def connectionLost(self, reason):
        """a connection just closed: remove protocol from clients table"""
        if self in self.factory.clients:
            del self.factory.clients[self]
    
    def lineReceived(self, line):
        """an XML message has been received"""
        try:
            request = emuML.parse_request(line)
            logging.info(_("received request {0}").format(str(request)))
            self.factory.clients[self].dispatch(request)
        except emuML.EmuMLError as message:
            logging.warning(_("Error in processing message: {0}").format(message))
    
    def notify_stop(self, model):
        """Stop the server"""
        print("Emulation finished")
        self.send_report(emulation.Report(NAME, 'finished'))
        #reactor.stop()
    
    def notify_start(self, model):
        """Notify starting of emulation"""
        self.send_report(emulation.Report(NAME, 'running'))
    
    def notify_time(self, model):
        """Notify of time advance"""
        #print(model.current_time())
        pass
    
    def send_report(self, report):
        """Send a report to the client"""
        message = emuML.write_report(report)
        logging.info(_("sending report {0}").format(message))
        self.sendLine(message)
        reactor.wakeUp()#@UndefinedVariable
