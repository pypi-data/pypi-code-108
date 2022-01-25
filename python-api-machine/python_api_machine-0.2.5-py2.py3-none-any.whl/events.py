from dataclasses import dataclass


class Event:
    pass


class RuntimeEvent(Event):
    pass


class ServiceEvent(RuntimeEvent):
    pass


@dataclass
class ServiceCallEvent(ServiceEvent):
    msg: object


class ServiceBeforeCall(ServiceCallEvent):
    """ Before a service processes a message"""
    pass


@dataclass
class ServiceAfterCall(ServiceCallEvent):
    """ After a service processed a message """
    result: object


class ServiceAfterSuccess(ServiceAfterCall):
    """ After a service processed a message successfully """
    pass


class ServiceAfterFail(ServiceAfterCall):
    """ After a service failed a message """
    pass
