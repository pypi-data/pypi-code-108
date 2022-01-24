"""
This module contains all the ports and connection functions
"""
import warnings
from enum import Enum
import logging
from inspect import signature, Signature, Parameter
from typing import (Any, Callable, Union, Dict, Tuple)
from shyft.time_series import utctime_now
from shyft.dashboard.base.hashable import Hashable


class PortError(RuntimeError):
    """PortError derived from RuntimeError"""
    pass


class PortConnectionError(RuntimeError):
    """PortConnectionError derived from RuntimeError"""
    pass


class PortConnectionWarning(RuntimeWarning):
    pass


class States(Enum):
    """
    States used as signal type by StatePorts
    """

    LOADING = 1
    INVALID = 2
    READY = 3
    ACTIVE = 4
    DEACTIVE = 5
    PROCESSING = 6
    EXPECTING_DATA = 7


class ReceiverFunc:
    """
    Class for an receiver port function which buffers the received object (self.obj), where the obj type annotation
    can be set in runtime.
    The sender function also saves the timestamp whenever the last obj was send.

    """
    def __init__(self, *, parent: 'portBase', callback: Callable[[Any], None], signal_type: Union[str, Any]) -> None:
        """
        Attributes
        ----------
        self.timestamp:
            timestamp since epoch of last received object

        Parameters
        ----------
        parent:
            Port class it belongs to
        callback:
            callback function which call on receiving an object
        signal_type:
            type annotation of the object to receive
        """
        self.parent = parent
        self.signal_type = signal_type
        self.timestamp = float(utctime_now())
        self.callback = callback

    def __call__(self, obj: Any) -> None:
        """
        Buffers the object when receiving it

        Parameters
        ----------
        obj
            Any signal to pass through
        """
        self.timestamp = float(utctime_now())
        self.callback(obj)

    @property
    def __signature__(self):
        """
        Modifies the signature of __call__
        Returns
        -------
        Signature of the call function
        """
        param = Parameter('obj', Parameter.POSITIONAL_ONLY, annotation=self.signal_type)
        return Signature(parameters=[param], return_annotation=Signature.empty)


class SenderFunc:
    """
    Class for a Sender port function, where the type annotation of the send object can be set in runtime.
    The sender function also saves the timestamp whenever the last obj was send.
    """
    def __init__(self, *,  parent: 'portBase', signal_type: Union[str, Any]) -> None:
        """
        Attributes
        ----------
        self.timestamp:
            timestamp since epoch of last send object


        Parameters
        ----------
        parent:
            Port class it belongs to
        signal_type:
            type annotation of the object to receive

        """
        self.parent = parent
        self.signal_type = signal_type
        self.timestamp = float(utctime_now())

    def __call__(self, signal: Any) -> Any:
        self.timestamp = float(utctime_now())
        return signal

    @property
    def __signature__(self):
        """
        Modifies the signature of __call__
        Returns
        -------
        Signature of the call function
        """
        param = Parameter('signal', Parameter.POSITIONAL_ONLY, annotation=self.signal_type)
        return Signature(parameters=[param], return_annotation=self.signal_type)


class PortTypes(Enum):
    """
    Defines the type of a Port
    """
    SENDER = 1
    RECEIVER = 2


class PortBase(Hashable):
    """
    Base port function
    Both Sender and Receiver are derived from this class which makes the implementation of both port types
    symmetric.
    The main difference between both are that they have a different func: ReceiverFunc, SenderFunc respectively.
    A Receiver will not have connected_ports and connected functions.
    """
    def __init__(self, *, parent: Any, name: str, func: Union[ReceiverFunc, SenderFunc], p_type: PortTypes) -> None:
        """
        Parameters
        ----------
        parent:
            instance in which the port resides
        name:
            name of the sender port
        func:
            function to be called to receive an the signal object
        p_type:
            type of the port: sender or receiver
        """
        super().__init__()
        self.logger = logging.getLogger()
        self.parent = parent
        self.func = func
        self.port_name = name
        self.p_type = p_type
        self.__state = States.ACTIVE

        self._connected_functions = {}
        self.connected_ports = []

    def __call__(self, *args, **kwargs):
        """
        The call function calls first its internal func representation (ReceiverFunc or SenderFunc),
        and in case the type is a Sender, all connected functions are called.

        Parameters
        ----------
        args:
            signal to send or receive
        kwargs:
            signal to send or receive

        Raises
        ------
        PortConnectionError:
            if the Sender is connected in a closed loop, and while sending the information comes back!
        """
        if self.__state == States.PROCESSING:
            msg = f"Sender '{self}' is connected in closed loop!"
            print("\nGroundhog Day:")
            print("-"*14, '\n')
            print(msg)
            print("connections:")
            print('\t\t', '\n\t\t'.join([f"{func.parent}" for func in self._connected_functions.values()]))
            print('\n')
            raise PortConnectionError(msg)
        self.__state = States.PROCESSING
        send_value = self.func(*args, **kwargs)
        for connected_function in self._connected_functions.values():
            try:
                connected_function(send_value)
            except Exception as e:
                self.__state = States.ACTIVE
                raise e
        self.__state = States.ACTIVE
        return send_value

    @property
    def signal_type(self) -> Any:
        return self.func.signal_type

    @property
    def connected(self) -> bool:
        """
        Property returns if Port is connected
        """
        return len(self.connected_ports) > 0


class Receiver(PortBase):
    def __init__(self, *, parent: Any, name: str, func: Callable, signal_type: Union[str, Any]) -> None:
        """
        Receiver, can be connected to a Sender with the connect_ports function.

        NB: the callback 'func' must have 1 parameter type annotated with 'signal_type'

        Class instances of Receiver ports should be named with the following pattern:

            self.receive_{what_will_be_received} = Receiver(...)

        The receiver function of the Receiver port, should have the same name as it's receiver starting with _:

            def __init__(self):
                self.receive_selections = Receiver(..., func=self._receive_selections, ...)

                def _receive_selections(self, ....):
                    ...

        Parameters
        ----------
        parent:
            instance in which the port resides
        name:
            name of the sender port
        func:
            function to be called to receive an the signal object
        signal_type:
            type annotation of the object to be received, if not provided type annotation of func is used

        Examples
        --------
        | # receiver function for signal_type: int
        |
        | def _receive_number(number: int) -> None:  # create a simple receiving function
        |     print("received ", number)
        |
        | receive_number = Receiver(parent='main.py', name='receive number', func=_receiver_func, signal_type=int)
        """

        f_an = list(signature(func).parameters.values())[0].annotation
        #  Function annotation "Any" allowed for flexibility with abstract classes
        if f_an != signal_type and f_an is not Any and signal_type is not Any:
            raise PortError(f"Signal_type and callable type annotation does not match! {signal_type} != {f_an}")

        receiver_func = ReceiverFunc(parent=self, callback=func, signal_type=signal_type)
        super().__init__(parent=parent, name=name, func=receiver_func, p_type=PortTypes.RECEIVER)

    def __repr__(self) -> str:
        return f">>===( {self.signal_type} )===¦ {self.parent}.{self.port_name}"


class Sender(PortBase):
    def __init__(self, *, parent: Any, name: str, signal_type: Union[str, Any]) -> None:
        """
        Sender Port, can be connected to a receiver port.
        Signal_type is the type annotation of the object to be send.
        It must correspond with the receiver port function object type annotation.

        Class instances of Receiver ports should be named with the following pattern:

            self.send_{what_will_be_send} =  Sender(...)

        Parameters
        ----------
        parent:
            instance in which the port resides
        name:
            name of the sender port
        signal_type:
            type annotation of the object to be send

        Examples
        --------
        | # sender function for signal_type: int
        |
        | send_number = Sender(parent='main.py', name='receive number',  signal_type=int)
        """
        self.__annotated_func = SenderFunc(parent=self, signal_type=signal_type)
        super().__init__(parent=parent, name=name, func=self.__annotated_func, p_type=PortTypes.SENDER)

    def __repr__(self) -> str:
        return f"{self.parent}.{self.port_name} ¦===( {self.signal_type} )===>>"

    def connect(self, receiver: Receiver) -> None:
        """
        Connect a Receiver to the Sender

        Parameters
        ----------
        receiver:
            Receiver port which should be connected to
        """
        check_port_compatibility(port_sender=self, port_receiver=receiver)
        if receiver not in self.connected_ports:
            self.connected_ports.append(receiver)
            receiver.connected_ports.append(self)
            self._connected_functions[receiver] = receiver.func
        else:
            msg = f"""Sender '{self.port_name}' of {self.parent} and receiver '{receiver.port_name}'
                      of {receiver.parent} are already connected"""
            warnings.warn(PortConnectionWarning(msg))

    def disconnect(self, receiver: Receiver) -> None:
        """
        Disconnect a Receiver from the Sender

        Parameters
        ----------
        receiver:
            Receiver port which should be connected to
        """
        if receiver in self.connected_ports:
            self.connected_ports.remove(receiver)
            receiver.connected_ports.remove(self)
            self._connected_functions.pop(receiver)


def check_port_compatibility(*, port_sender: Sender, port_receiver: Receiver) -> bool:
    """
    function to check if two ports can be connected

    Raises
    ------
    PortConnectionError: if ports are incompatible

    Parameters
    ----------
    port_sender:
        sender port to verify
    port_receiver:
        receiver port to verify

    Returns
    -------
    returns True if compatible
    """
    if port_sender.signal_type == port_receiver.signal_type \
            or port_sender.signal_type == Any \
            or port_receiver.signal_type == Any:
        return True
    print("Incompatible Ports:")
    print("-"*19, '\n')
    print(port_sender)
    print("    ", port_receiver)
    raise PortConnectionError(
            f"Incompatible Ports:    {port_sender}     {port_receiver}")


def connect_ports(port_sender: Sender, port_receiver: Receiver) -> bool:
    """
    Function to connect a sender and a receiver port

    Raises
    ------
    PortConnectionError:
        if ports are incompatible
    PortConnectionWarning:
        if ports are  already connected

    Parameters
    ----------
    port_sender:
        sender port to connect
    port_receiver:
        receiver port to connect

    Returns
    -------
    returns True if connected
    """
    if not port_sender:
        raise PortConnectionError("port_sender is NoneType")
    if not port_receiver:
        raise PortConnectionError("port_receiver is NoneType")
    if not isinstance(port_sender, Sender):
        raise PortConnectionError(f"'{port_sender}' is not instance of Sender")
    if not isinstance(port_receiver, Receiver):
        raise PortConnectionError(f"'{port_receiver}' is not instance of Receiver")

    # Finally connect if not already connected
    port_sender.connect(port_receiver)

    return True


def disconnect_ports(port_sender: Sender, port_receiver: Receiver) -> bool:
    """
    Function to disconnect a sender and a receiver port

    Parameters
    ----------
    port_sender:
        sender port to connect
    port_receiver:
        receiver port to connect

    Returns
    -------
    returns True if disconnected
    """
    port_sender.disconnect(port_receiver)
    return True


class StatePorts:

    def __init__(self, *, parent: Any, _receive_state: Callable[[States], None]) -> None:
        """
        State ports are 2 ports dedicated to send and receive States beweteen apps.
        For convenience sender and receiver ports are combined here.


        Parameters
        ----------
        parent:
            class/widget the port belongs to
        _receive_state:
            Callable receiver function, with type annotation state: States



        Examples
        --------
        | state_ports = StatePort(parent=parent, _receive_state=_receive_state)
        |
        | def _receive_state(states: States) -> None:
        |     if state == States.ACTIVE:
        |         print(state)
        """
        self.parent = parent
        self.receive_state = Receiver(parent=self, name='receive state', func=_receive_state, signal_type=States)
        self.send_state = Sender(parent=self, name='send state', signal_type=States)


def grep_ports(*, cls: Any,
               port_type: Union[Receiver, Sender, StatePorts]) -> Dict[str, Union[Receiver, Sender, StatePorts]]:
    """
    find port of port_type in a given cls

    Parameters
    ----------
    cls:
        cls parse for ports
    port_type:
        port type to search

    Returns
    -------
    returns dict with Dict[name:str, port:Union[Receiver, Sender, StatePorts]] with the found ports
    """
    ports = {}
    for m, t in cls.__dict__.items():
        if isinstance(t, port_type):
            ports[m] = t
    return ports


def connect_state_ports(sender_state_port: StatePorts, receiver_state_port: StatePorts) -> bool:
    """
    Function to coonnect state ports

    Raises
    ------
    PortConnectionError:
        if not possible to connect

    Parameters
    ----------
    sender_state_port:
        sender state port
    receiver_state_port:
        receiver state port

    Returns
    -------
    True if connected sucessfully
    """
    return connect_ports(sender_state_port.send_state, receiver_state_port.receive_state)


def connect_ports_and_state_ports(port_sender: Sender, port_receiver: Receiver) -> Tuple[bool, bool]:
    """
    Convenience wrapper function to connect a Sender and Receiver,
    in addition connect the state ports of the sender.parent and receiver.parent.

    Both parents must have a StatePort, the Sender.parent.state_port is treat as sender_state_port!

     Raises
    ------
    PortConnectionError:
        if ports are incompatible
    PortConnectionWarning:
        if ports are  already connected

    Parameters
    ----------
    port_sender:
        sender port to connect
    port_receiver:
        receiver port to connect

    Returns
    -------
    returns True if connected
    """

    # connect the ports
    success_connect_ports = connect_ports(port_sender, port_receiver)
    # check if both have parents
    if port_sender.parent is None:
        raise PortConnectionError(f"'{port_sender.port_name} has no parent")
    if port_receiver.parent is None:
        raise PortConnectionError(f"'{port_receiver.port_name} has no parent")
    # check if both parents have a StatePorts attribute
    sender_state_ports = grep_ports(cls=port_sender.parent, port_type=StatePorts)
    receiver_state_ports = grep_ports(cls=port_receiver.parent, port_type=StatePorts)
    if not sender_state_ports:
        msg = f"'{port_sender.port_name}' of '{port_sender.parent}' has no attribute of type <StatePorts>"
        raise PortConnectionError(msg)
    if not receiver_state_ports:
        msg = f"'{port_receiver.port_name}' of '{port_receiver.parent}' has no attribute of type <StatePorts>"
        raise PortConnectionError(msg)
    success_connect_state_ports = False
    # try to connect all StatePorts with each other
    for sender_state_port in sender_state_ports.values():
        for receiver_state_port in receiver_state_ports.values():
            success_connect_state_ports = connect_state_ports(sender_state_port, receiver_state_port)
    return success_connect_ports, success_connect_state_ports
