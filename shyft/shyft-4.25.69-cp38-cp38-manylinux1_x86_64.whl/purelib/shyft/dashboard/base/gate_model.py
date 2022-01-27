"""
This module contains the gate models.

Gates are used to control the signal flow of Sender to its Receiver.

This is very useful whenever we want to only send data to a widget whenever the user
e.g.
 * opens a tab
 * clicks on a button
 * triggers a selection

Different then the selectors for the gates, the GatePresenter ties the the GateModel and the GateView together:
GatePresenter(GateView, GateModel)
See also ref::gate_presenter.

The information flow is:
GateView -> GatePresenter -> GateModel

Whenever the user triggers a GateView, a signal (open/close) is send to the GatePresenter.
The GatePresenter triggers the GateModel.
The Gate model connects/disconnects its ports.
"""

import logging

from typing import Union, Optional, List, Any
from inspect import signature
from enum import Enum
import abc

from shyft.dashboard.widgets.logger_box import LoggerBox
from .ports import (Sender, Receiver, connect_ports, connect_state_ports, connect_ports_and_state_ports,
                    disconnect_ports, check_port_compatibility, ReceiverFunc)


class GateError(RuntimeError):
    """
    Gate Error
    """

    pass


ConnectFunctions = Union[connect_ports, connect_state_ports, connect_ports_and_state_ports]


class GateState(Enum):
    """
    States of a Gate

    Attributes
    ----------
    Open:
        the gate is open
    Closed:
        the gate is closed
    """

    Open = 1
    Closed = 2


class GateBase:
    """
    Base class and interface for Gates
    """

    def __init__(self,
                 logger: Optional[LoggerBox]=None):
        """
        Base function for gates
        """
        self.logger = logger or logging.getLogger(__file__)
        self.gate_state = GateState.Closed
        self.receive_gate_state = Receiver(parent=self, name='receive gate state', func=self._receive_gate_state,
                                           signal_type=GateState)

    def _receive_gate_state(self, gate_state: GateState) -> None:
        """
        Receives gate state; initiates open and close gate

        Parameters
        ----------
        gate_state:
            state of the gate, if the gate is open or closed

        """
        if gate_state == GateState.Open:
            self.open()
        elif gate_state == GateState.Closed:
            self.close()

    @abc.abstractmethod
    def open(self) -> None:
        """
        Function to open the gate
        """
        pass

    @abc.abstractmethod
    def close(self):
        """
        Function to close the gate
        """
        pass


class SingleGate(GateBase):

    def __init__(self,
                 sender: Sender,
                 receiver: Receiver,
                 connect_function: Optional[ConnectFunctions]=None,
                 buffer: bool=True,
                 clear_buffer_after_send: bool=False,
                 initial_gate_state: GateState=GateState.Closed,
                 logger: Optional[LoggerBox]=None) -> None:
        """
        A single Gate: Connects a single Sender to a single Receiver when the gate is opened, and disconnects if closed

        Parameters
        ----------
        sender:
            sender port for the gate
        receiver:
            receiver port for the gate
        connect_function:
            connection function which should be used, when opening the gate
        buffer:
            Buffer object from sender function during closed gate and send it when gate is opened!
            This should be True if connected to a Button view
        clear_buffer_after_send:
            Delete buffered object after it was send when gate is opened
        initial_gate_state:
            Initial state of the gate

        """
        super().__init__(logger=logger)
        connect_function = connect_function or connect_ports
        check_port_compatibility(port_sender=sender, port_receiver=receiver)

        self.sender = sender
        self.receiver = receiver

        self.use_buffer = buffer
        self.buffer = None
        self.clear_buffer_after_send = clear_buffer_after_send
        self.connect_function = connect_function

        _receive_values_to_buffer = ReceiverFunc(parent=self, callback=self._send_buffer_notification,
                                                 signal_type=signature(sender.func).return_annotation)
        self.receive_values_to_buffer = Receiver(parent=self, name='general receiver', func=_receive_values_to_buffer,
                                                 signal_type=signature(sender.func).return_annotation)
        connect_ports(sender, self.receive_values_to_buffer)

        self.send_buffer_notification = Sender(parent=self, name='send buffer notification', signal_type="SingleGate")

        # set initial gate state
        self.gate_state = None  # set to None such that it can be opened or closed depending on GateState.Closed
        self.receive_gate_state(initial_gate_state)

    def open(self) -> None:
        """
        Function to open the gate
        """
        if self.gate_state == GateState.Open:
            return
        # 1. connect both ports
        self.connect_function(self.sender, self.receiver)
        # 2. send saved obj
        if self.use_buffer and self.buffer is not None:
            self.receiver(self.buffer)
            # # 3. clear saved obj
            if self.clear_buffer_after_send:
                self.buffer = None
        self.gate_state = GateState.Open

    def close(self):
        """
        Function to close the gate
        """
        if self.gate_state == GateState.Closed:
            return
        # 1. disconnect ports
        disconnect_ports(self.sender, self.receiver)
        self.gate_state = GateState.Closed

    def _send_buffer_notification(self, buffer_object: Any) -> None:
        """
        Returns
        -------
        send notification when the object is received
        """
        if self.gate_state == GateState.Open and self.use_buffer and self.clear_buffer_after_send:
            self.buffer = None
        else:
            self.buffer = buffer_object
            self.send_buffer_notification(self)


class AggregatedGate(GateBase):

    def __init__(self,
                 gates=List[SingleGate],
                 initial_gate_state: Optional[GateState]=GateState.Closed,
                 logger: Optional[LoggerBox] = None
                 ) -> None:
        """
        Aggregation of gates, used to control multiple gates derived from GateBase as one gate.
        This can be used when a GateView e.g. a Button should trigger multiple gates at the same time.


        Parameters
        ----------
        gates:
            List of Gates
        """
        super().__init__(logger=logger)
        for gate in gates:
            if not isinstance(gate, GateBase):
                raise GateError(f"{gate} is not of type SingleGate or AggregatedGate!")
        self.gates = gates
        self.buffer_gate_order = gates
        # set initial gate state
        self.gate_state = None  # set to None such that it can be opened or closed depending on GateState.Closed
        self.receive_gate_state(initial_gate_state)

        self.receive_buffer_notification = Receiver(parent=self, name="receive use_buffer notification",
                                                    func=self._receive_buffer_notification, signal_type="SingleGate")
        for gate in self.gates:
            connect_ports(gate.send_buffer_notification, self.receive_buffer_notification)

    def _receive_buffer_notification(self, gate: "SingleGate") -> None:
        """
        Receiver function of the gate buffer to order the gates

        Parameters
        ----------
        gate:
            a gate to push back from its place in the queue to the end
        """
        self.gates.remove(gate)
        self.gates.append(gate)

    def open(self) -> None:
        """
        Function to open the gate
        """
        if self.gate_state == GateState.Open:
            return
        for gate in self.gates:
            gate.open()
        self.gate_state = GateState.Open

    def close(self):
        """
        Function to close the gate
        """
        if self.gate_state == GateState.Closed:
            return
        for gate in self.gates:
            gate.close()
        self.gate_state = GateState.Closed

