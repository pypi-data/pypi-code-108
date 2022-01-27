from __future__ import annotations

import _thread
import dataclasses
import json
import logging
import re
import sys
import threading
import time
import requests

from typing import Callable, Optional

from requests import Response

try:
    import thread
except ImportError:
    import _thread as thread

import websocket

logging.getLogger().setLevel(logging.INFO)
_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.INFO)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
# add the handler to the root logger
_LOGGER.addHandler(console)

from enum import Enum, auto

from dataclasses import dataclass, field
from dataclasses_json import dataclass_json, LetterCase, config


class KosmosError(Exception):
    """ a generic Kosmos Error"""
    pass


class KosmosConflictError(KosmosError):
    """
    there was a conflict (for example if the resource already existed, or the validation failed)
    """
    pass


class KosmosNotFoundError(KosmosError):
    """
        the resource was not found
    """
    pass


class KosmosAuthInvalid(KosmosError):
    """
        The provided credentials are not correct
    """

    def __init__(self):
        super().__init__("The provided credentials are not correct")

    pass


class KosmosRequestFailed(KosmosError):
    """
        The provided credentials are not correct
    """

    def __init__(self, response: Response):
        self.response = response
        super().__init__(f"The request failed! ({response.status_code}) - {response.reason} - {response.text}")

    pass


class KosmosForbidden(KosmosError):
    """
        The credentials are not valid for this request
    """

    def __init__(self):
        super().__init__("The provided credentials are not suitable for this request")

    pass


class _EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        return super().default(o)


class KosmosEvent(Enum):
    """
    Event Enums for Kosmos

    Notes
    -----
    if you use subscribe to these events please make sure the function has the correct keyword parameters!
    """
    auth_ok = auto()
    """
    will be triggered once the auth to kosmos was successful
    
    Parameter
    ---------
        kosmos: KosmosClient
            the kosmos client
    """
    connection_established = auto()
    """
        will be triggered everytime we have a new connection established with kosmos

        Parameter
        ---------
            kosmos: KosmosClient
                the kosmos client
        """

    connection_lost = auto()
    """
        will be triggered everytime we lose the connection to kosmos

        Parameter
        ---------
            kosmos: KosmosClient
                the kosmos client
        """
    stopped = auto()
    """
        will be triggered once if the stop method was called

        Parameter
        ---------
            kosmos: KosmosClient
                the kosmos client
        """
    device_updated = auto()
    """
        will be triggered once for each update to a device's state

        Parameter
        ---------
            kosmos: KosmosClient
                the kosmos client
            device: KosmosDevice 
                the device that was updated                    
        """

    device_attribute_updated = auto()
    """
        will be triggered once for each change to an attribute of a device

        Parameter
        ---------
            kosmos: KosmosClient
                the kosmos client
            device: KosmosDevice 
                the device that was updated    
            attribute: str | int | float
                the attribute that changed
            value: str | int | bool | float | list | tuple | None | dict 
                the new value
        """

    device_removed = auto()
    """
        will be triggered once for each device that was removed from the kosmos

        Parameter
        ---------
            kosmos : KosmosClient
                the kosmos client
            device : KosmosDevice 
                the device that was removed                    
        """

    device_created = auto()
    """
        will be triggered once for a new device, will also be triggered while doing the initial sync

        Parameter
        ---------
            kosmos : KosmosClient
                the kosmos client
            device : KosmosDevice 
                the new device that was found                    
        """


@dataclass_json(letter_case=LetterCase.CAMEL)  # we need this to accept the lastUpdate as last_update and so on
@dataclass
class KosmosDevice:
    """

    """
    uuid: str
    name: str = None
    schema: str = None
    last_update = 0
    last_change = 0
    state: dict = field(default_factory=dict)

    def __str__(self):
        return f"Kosmos Device {self.uuid}({self.schema}) {self.state}"


@dataclass_json
@dataclass
class KosmosLocation:
    x: Optional[int] = None
    y: Optional[int] = None
    z: Optional[int] = None
    w: Optional[int] = None
    d: Optional[int] = None
    h: Optional[int] = None
    yaw: Optional[int] = None
    roll: Optional[int] = None
    pitch: Optional[int] = None
    area: Optional[str] = None


@dataclass_json
@dataclass
class KosmosScopeList:
    read: Optional[KosmosScope]
    write: Optional[KosmosScope]
    delete: Optional[KosmosScope] = field(metadata=config(field_name="del"))


@dataclass_json
@dataclass
class KosmosUser:
    id: int
    name: str


@dataclass_json
@dataclass
class KosmosGroup:
    id: int
    name: str


@dataclass_json
@dataclass
class KosmosScope:
    users: list[KosmosUser]
    admins: list[KosmosUser]
    adminGroups: list[KosmosGroup]
    userGroups: list[KosmosGroup]
    name: str
    id: int

    @staticmethod
    def from_dict_(s) -> KosmosScope:
        scope = KosmosScope(name=s["name"], id=s["id"], users=[], admins=[], userGroups=[], adminGroups=[])
        if "users" in s:
            for u in s["users"]:
                scope.users.append(KosmosUser.from_dict(u))
        if "admins" in s:
            for u in s["admins"]:
                scope.admins.append(KosmosUser.from_dict(u))
        if "userGroups" in s:
            for u in s["userGroups"]:
                scope.users.append(KosmosGroup.from_dict(u))
        if "adminGroups" in s:
            for u in s["adminGroups"]:
                scope.admins.append(KosmosGroup.from_dict(u))

        return scope


class KosmosClient(websocket.WebSocketApp, threading.Thread):
    """
    The baseclass for our Kosmos Client
    """
    __regex_state_pattern = re.compile(r"^device\/(?P<uuid>.*?)\/state:(?P<payload>.*)$")
    __regex_config_pattern = re.compile(r"^device\/(?P<uuid>.*?)\/config:(?P<payload>.*)$")

    def __init__(self, base: str, username: str, password: str, subs: dict = None):
        """
        creates a new instance of the Kosmos Client

        Parameters
        ----------
        base : str
            the base for the server
        username : str
            the username to use
        password : str
            the password to use
        subs: dict[KosmosEvent,Callable]
            the subscriptions to start with

        Examples
        --------

        sync without async updates
        >>> kosmos = KosmosClient("http://localhost:18080", "user", "pass")



        async with listeners
        >>> with KosmosClient("http://localhost:18080", "user", "pass",
        >>>               subs={
        >>>                   KosmosEvent.auth_ok: on_auth_ok,
        >>>                   KosmosEvent.device_created: on_device_created,
        >>>                   KosmosEvent.device_attribute_updated: on_device_attribute_changed
        >>>               }) as kosmos:

        """
        threading.Thread.__init__(self)
        self.__ws = None
        self.__connected = False
        self.__stopped = False
        self.__devices = dict()
        self.__subscribers = dict()
        self.__token = None
        if subs is not None:
            for i, (event_type, fn) in enumerate(subs.items()):
                self.subscribe(event_type, fn)
        if base.startswith("http://"):
            self.__wsurl = f"ws://{base[7:]}/ws"

        elif base.startswith("https://"):
            self.__wsurl = f"wss://{base[8:]}/ws"

        else:
            raise ValueError(f"cannot parse url: {base} - pleae provide it in the form of 'http://localhost:18080'")

        self.__base = base
        self.__username = username
        self.__password = password

    def __enter__(self):
        # _LOGGER.info("enter")
        self.__connected = False
        self.start()
        while not self.__connected and not self.__stopped:
            time.sleep(0.5)
        return self

    def __post_event(self, event_type: KosmosEvent, data):
        # _LOGGER.info(f"publishing {event_type} with data:{data}")
        if event_type not in self.__subscribers:
            return
        for fn in self.__subscribers[event_type]:
            fn(self, **data)

    def __exit__(self, type, value, traceback):
        self.stop()

    def __on_message(self, ws, message=None):
        if message is None:
            message = ws

        message = str(message)
        #_LOGGER.info(f"received {message}")
        if message == "auth successful":
            self.__connected = True
            self.__post_event(KosmosEvent.auth_ok, {})
            return
        if message == "auth failed":
            # self.__connected = True
            # self.__post_event(KosmosEvent.auth_ok, {})
            _LOGGER.error("could not auth to kosmos!")

            self.stop()
            raise KosmosAuthInvalid()

        idx = message.find(':')
        if idx != -1:
            url = message[:idx]

            args = message[idx + 1:]
            if url == "devices":
                # init devices
                d = json.loads(args)
                for dd in d:
                    dev = KosmosDevice.from_dict(dd)
                    if dev.uuid not in self.__devices:  # we need to overwrite it here before the event is triggered
                        self.__devices[dev.uuid] = dev
                        self.__post_event(event_type=KosmosEvent.device_created, data={'device': dev})
                    else:  # we might as well "update" it here
                        self.__devices[dev.uuid] = dev
                self.__connected = True
                return
            m = self.__regex_state_pattern.match(message)
            if m is not None:
                dev = self.__devices[m.group('uuid')]
                if dev is not None:
                    js = json.loads(m.group('payload'))
                    for attribute in js:
                        value = js[attribute]
                        if attribute not in dev.state:
                            dev.state[attribute] = value
                            self.__post_event(event_type=KosmosEvent.device_attribute_updated,
                                              data={'device': dev, 'attribute': attribute, 'value': value})
                            self.__post_event(event_type=KosmosEvent.device_updated,
                                              data={'device': dev})
                            continue

                        if dev.state[attribute] != value:
                            dev.state[attribute] = value
                            self.__post_event(event_type=KosmosEvent.device_attribute_updated,
                                              data={'device': dev, 'attribute': attribute, 'value': value})
                            self.__post_event(event_type=KosmosEvent.device_updated,
                                              data={'device': dev})
                            continue
                        # else:
                        #    _LOGGER.info(f"update was useless? {js} vs {dev.state}")
                else:
                    _LOGGER.warning(f"could not find device {m.group('uuid')}?")
                return
            m = self.__regex_config_pattern.match(message)

            if m is not None:
                payload = m.group('payload')

                if len(payload) > 0:
                    dev = KosmosDevice.from_dict(json.loads(payload))
                    if dev.uuid not in self.__devices:  # we need to overwrite it here before the event is triggered
                        self.__devices[dev.uuid] = dev
                        self.__post_event(event_type=KosmosEvent.device_created, data={'device': dev})
                    else:  # we might as well "update" it here
                        self.__devices[dev.uuid] = dev
                    return
                uuid = m.group("uuid")
                if uuid in self.__devices:  # we need to overwrite it here before the event is triggered
                    self.__post_event(event_type=KosmosEvent.device_removed, data={'device': self.__devices[uuid]})
                    del (self.__devices[uuid])
                return
            self.__connected = True
            return
        # self.connected = True

    def __on_error(self, ws=None, error=None):
        self.__connected = False
        _LOGGER.info(f"kosmos error: {error}")

        pass

    def __on_close(self, ws=None, status=None, message=None):
        self.__connected = False
        # _LOGGER.info(f"kosmos closed")
        self.__post_event(KosmosEvent.connection_lost, data={'status': status, 'message': message})
        pass

    def __on_open(self, ws=None):
        # _LOGGER.info(f"kosmos opened")

        # self.connected = True
        self.__ws.send('user/auth:{"user":"' + self.__username + '","pass":"' + self.__password + '"}')
        self.__ws.send('user/type:PythonClient')
        self.__post_event(KosmosEvent.connection_established, {})

        def pinger(*args):
            while self.__connected:
                time.sleep(30)
                self.__ws.send("ping")

        thread.start_new_thread(pinger, ())

    def run(self):
        """
        the runner that automatically reconnects the websocket if needed

        """
        self.__ws = websocket.WebSocketApp(self.__wsurl,
                                           on_message=self.__on_message,
                                           on_error=self.__on_error,
                                           on_close=self.__on_close,
                                           on_open=self.__on_open)

        while not self.__stopped:
            # _LOGGER.info("kosmos reconnecting")
            self.__ws.run_forever(ping_interval=10)
            # _LOGGER.error("kosmos disconnected")

            if self.__stopped:
                break
            time.sleep(5)

    def subscribe(self, event_type: KosmosEvent, fn: Callable) -> None:
        """
        subscribe to an event with the given Callable

        Parameters
        ----------
        event_type : KosmosEvent
            the event type to listen to
        fn : Callable
            the function that fulfills the keyword parameters seen in the documentation for each KosmosEvent
        Examples
        --------

        Subscribe to auth events
        >>> def on_auth_ok(kosmos: KosmosClient):
        >>>     print(f"auth okay  on {kosmos}...")
        >>> kosmos.subscribe(KosmosEvent.auth_ok, on_auth_ok)


        Subscribe to changed attributes
        >>> def on_device_attribute_changed(kosmos: KosmosClient, device: KosmosDevice, attribute: str | int | float, value: str | int | bool | float | list | tuple | None | dict):
        >>>     print(f"change on {kosmos} {device} - set {attribute} to {value}")
        >>> kosmos.subscribe(KosmosEvent.device_attribute_updated, on_device_attribute_changed)


        """
        if event_type not in self.__subscribers:
            self.__subscribers[event_type] = []
        self.__subscribers[event_type].append(fn)

    def is_connected(self) -> bool:
        """
        checks if a connection is established

        Returns
        -------
        True if connection is established and most likely alive
        """
        return self.__connected

    def is_stopped(self) -> bool:
        """
        check if the client got the command to stop itself

        Returns
        -------
        bool:
        True if the client should be stopping
        """
        return self.__stopped

    def connect(self) -> None:
        """
        connect to the kosmos backend

        """
        self.__connected = False
        self.start()
        while not self.__connected:
            time.sleep(0.5)

    def stop(self) -> None:
        """
        Signal the client that we would want to stop the client.
        Will close all connections
        """
        self.__stopped = True
        self.__ws.close()
        self.__post_event(KosmosEvent.stopped, {})

    def reconnect(self) -> None:
        """
        closes the current Connection, will be reestablished as long as __stopped is not True
        """
        self.__ws.close()

    def get_device(self, uuid: str) -> KosmosDevice:
        """
        get the device from internal cache if possible - get from api otherwise

        Parameters
        ----------
        uuid : str
            the uuid of the device

        Returns
        -------
        KosmosDevice
            the KosmosDevice we wanted to get

        Raises
        -------
        KosmosAuthInvalid
            the auth was invalid
        KosmosForbidden
            the auth has not sufficient access to delete the device
        KosmosNotFoundError
            the device was not found
        KosmosError
            another error occurred

        Examples
        --------


        >>> print(kosmos.get_device("virt_lamp_0"))
        >>> print(kosmos.get_device("virt_lamp_1").state["on"])

        """
        if uuid in self.__devices:
            return self.__devices[uuid]
        d = KosmosDevice.from_dict(
            self.__do_request('GET', "/device/get", params={"id": uuid}, wanted_status=200).json())
        # self.__devices[uuid] = d DONT cache get api - because they are not always accurate at the next time we want to get the data
        return d

    def set(self, device: str | KosmosDevice, value: dict[str, any]) -> None:
        """
        Set the state of a device in the kosmos backend

        Parameters
        ----------
        device : str | KosmosDevice
            the uuid or the actual KosmosDevice to update
        value : dict
            a dict of one or multiple attributes to change

        Raises
        -------
        KosmosAuthInvalid
            the auth was invalid
        KosmosForbidden
            the auth has not sufficient access to delete the device
        KosmosNotFoundError
            the device was not found
        KosmosConflict
            the set could not be executed
        KosmosError
            another error occurred

        Examples
        --------
        >>> kosmos.set("virt_heater_3", {"heatingTemperatureSetting": 21})

        sets the attribute "heatingTemperatureSetting" of "virt_heater_3" to 21
        """

        if isinstance(device, KosmosDevice):
            if self.is_connected():
                self.__ws.send(f"device/{device.uuid}/set:{json.dumps(value)}")
            else:
                value["uuid"] = device.uuid
                self.__do_request("POST", "/device/set", body=json.dumps(value), wanted_status=200)
            return
        if isinstance(device, str):
            if self.is_connected():
                self.__ws.send(f"device/{device}/set:{json.dumps(value)}")
            else:
                value["uuid"] = device
                self.__do_request("POST", "/device/set", body=json.dumps(value), wanted_status=200)
            return
        raise ValueError(f"could not parse Parameter device ({device})")

    def set_attribute(self, device: str | KosmosDevice, attribute: str | int | float,
                      value: str | int | bool | float | list | tuple | None | dict):
        """
        sets the given attribute on the kosmos backend to a specified value

        Parameters
        ----------
        device : str | KosmosDevice
            the uuid or the actual KosmosDevice to update
        attribute : str
            the attribute to change
        value
            the new value to set (will be converted to JSON)

        Raises
        -------
        KosmosAuthInvalid
            the auth was invalid
        KosmosForbidden
            the auth has not sufficient access to delete the device
        KosmosNotFoundError
            the device was not found
        KosmosConflict
            the set could not be executed because it failed validation
        KosmosError
            another error occurred

        Examples
        --------
        >>> kosmos.set_attribute("virt_heater_3", "heatingTemperatureSetting", 24)

        sets the attribute "heatingTemperatureSetting" of "virt_heater_3" to 24
        """

        if isinstance(device, KosmosDevice):
            if self.is_connected():
                self.__ws.send(f"device/{device.uuid}/set:{json.dumps({attribute: value})}")
            else:
                self.__do_request("POST", "/device/set", body=json.dumps({attribute: value, "uuid": device.uuid}),
                                  wanted_status=200)
            return
        if isinstance(device, str):

            if self.is_connected():
                self.__ws.send(f"device/{device}/set:{json.dumps({attribute: value})}")
            else:
                self.__do_request("POST", "/device/set", body=json.dumps({attribute: value, "uuid": device}),
                                  wanted_status=200)
            return
        raise ValueError(f"could not parse Parameter device ({device})")

    def add_device(self, uuid: str, state: dict = {}, schema: str = "https://kosmos-lab.de/schema/NoSchema.json",
                   scopes: KosmosScopeList = None) -> None:
        """
        add a device to Kosmos

        Parameters
        ----------
        uuid: str
            the UUID to use for the device

        state: dict
            the current state of the device - NEEDS to contain everything that is required by the schema!

        schema: str
            the $id of the Schema, defaults to https://kosmos-lab.de/schema/NoSchema.json

        scopes: KosmosScopeList
            the Scopes to use - defaults to no Scopes

        Raises
        -------
        KosmosAuthInvalid
            the auth was invalid
        KosmosNotFoundError
            the schema was not found
        KosmosConflictError
            the uuid is already in use or the validation against the schema failed
        KosmosError
            another error occurred

        Examples
        -------
        >>> kosmos.add_device(uuid="virt_hsv_lamp_3", state={"on": False, "hue": 120, "saturation": 60, "dimmingLevel": 50},
        >>>              schema="https://kosmos-lab.de/schema/HSVLamp.json")
        """
        js = {"uuid": uuid, "schema": schema}
        if scopes is not None:
            js["scopes"] = dataclasses.asdict(scopes)
            if "delete" in js[
                "scopes"]:  # should maybe find a better solution, but well it works (python does not allow the attribute name 'del')
                js["scopes"]["del"] = js["scopes"]["delete"]
                del (js["scopes"]["delete"])
        if state is not None:
            js["state"] = state
        # if self.is_connected():
        #    self.__ws.send(f"device/{uuid}/config:{json.dumps(js, cls=_EnhancedJSONEncoder)}")
        # else:

        self.__do_request("POST", "/device/add", body=json.dumps(js, cls=_EnhancedJSONEncoder), wanted_status=204)
        return

    def delete_device(self, device: str | KosmosDevice) -> None:
        """
        deletes a device from Kosmos

        Parameters
        ----------
        device: str | KosmosDevice
            the device to update

        Raises
        -------
        KosmosAuthInvalid
            the auth was invalid
        KosmosForbidden
            the auth has not sufficient access to delete the device
        KosmosNotFoundError
            the device was not found
        KosmosError
            another error occurred

        Examples
        --------
        >>> kosmos.delete_device("virt_lamp_3")
        """
        if isinstance(device, KosmosDevice):
            if self.is_connected():
                self.__ws.send(f"device/{device.uuid}/config:")
            else:
                self.__do_request("DELETE", "/device/delete", body=json.dumps({'id': device.uuid}),
                                  wanted_status=204)
            return

        if isinstance(device, str):
            if self.is_connected():
                self.__ws.send(f"device/{device}/config:")
            else:
                self.__do_request("DELETE", "/device/delete", params={'id': device},
                                  wanted_status=204)
            return
        raise ValueError(f"could not parse Parameter device ({device})")

    def delete_schema(self, schemaid: str) -> None:
        """
        deletes as schema from kosmos

        Parameters
        ----------
        schemaid: str
            the id of the schema

        Raises
        -------
        KosmosAuthInvalid
            the auth was invalid
        KosmosForbidden
            the auth has not sufficient access to delete the schema
        KosmosNotFoundError
            the schema was not found
        KosmosConflictError
            the schema cannot be deleted - it is still in use
        KosmosError
            another error occurred

        Examples
        --------
        >>> kosmos.delete_schema("https://kosmos-lab.de/schema/TestSchema1.json")
        """

        self.__do_request("DELETE", "/schema/delete", params={'id': schemaid},
                          wanted_status=204)

    def get_schema(self, schemaid: str) -> dict:
        """
        get a schema back from kosmos

        Parameters
        ----------
        schemaid: str
            the $id of the schema

        Returns
        -------
        dict
            the schema

        Raises
        -------
        KosmosAuthInvalid
            the auth was invalid
        KosmosForbidden
            the auth has not sufficient access to delete the schema
        KosmosNotFoundError
            the schema was not found
        KosmosError
            something else went wrong with the communication
        Examples
        --------
        >>> print(kosmos.get_schema("https://kosmos-lab.de/schema/TestSchema1.json"))
        """

        return self.__do_request('GET', f"{self.__base}/schema/get", params={"id": schemaid}, wanted_status=200).json()

    def list_schemas(self) -> list[dict]:
        """
        list all schemas in the kosmos

        Returns
        -------
        List with currently known Schemas (List of Dicts)

        Raises
        -------
        KosmosAuthInvalid
            the auth was invalid
        KosmosForbidden
            the auth has not sufficient access the list of schemas
        KosmosError
            another error occurred
        Examples
        --------
        >>> print(kosmos.list_schemas())
        """

        return self.__do_request('GET', f"{self.__base}/schema/list", wanted_status=200).json()

    def add_schema(self, schema: dict) -> None:
        """
        add a schema to kosmos

        Parameters
        ----------
        schema: dict
            the schema to add - needs to be a valid schema

        Raises
        -------
        KosmosAuthInvalid
            the auth was invalid
        KosmosForbidden
            the auth has not sufficient access to delete the schema
        KosmosConflictError
            something could not be added due to a conflict
        KosmosError
            anything else went wrong

        Examples
        --------
        >>> kosmos.add_schema({
        >>>         "failures": [
        >>>         ],
        >>>         "$schema": "http://json-schema.org/draft-07/schema#",
        >>>         "examples": [
        >>>         ],
        >>>         "additionalProperties": True,
        >>>         "title": "TestSchema1",
        >>>         "type": "object",
        >>>         "properties": {
        >>>         },
        >>>         "$id": "https://kosmos-lab.de/schema/TestSchema1.json"
        >>>     })
        """

        self.__do_request("POST", url="/schema/add", body=schema, wanted_status=200)

    def add_scope(self, scope: str | KosmosScope) -> KosmosScope:
        """
        add a scope to kosmos

        Parameters
        ----------
        name: str
            the name of the new scope


        Raises
        -------
        KosmosAuthInvalid
            the auth was invalid
        KosmosForbidden
            the auth has not sufficient access to delete the schema
        KosmosConflictError
            could not add scope, name is in use
        KosmosNotFoundError
            the device could not be found!
        KosmosError
            anything else went wrong

        """
        if isinstance(scope, KosmosScope):
            return KosmosScope.from_dict_(
                self.__do_request("POST", url="/scope/add", body=scope.to_dict(), wanted_status=200).json())
        elif isinstance(scope, str):
            return KosmosScope.from_dict_(
                self.__do_request("POST", url="/scope/add", body={"name": scope}, wanted_status=200).json())

    def get_scope(self, scope: str | int) -> KosmosScope:
        """
        add a scope to kosmos

        Parameters
        ----------
        name: str
            the name of the new scope


        Raises
        -------
        KosmosAuthInvalid
            the auth was invalid
        KosmosForbidden
            the auth has not sufficient access to delete the schema
        KosmosConflictError
            could not add scope, name is in use
        KosmosNotFoundError
            the device could not be found!
        KosmosError
            anything else went wrong

        """
        if isinstance(scope, int):
            return KosmosScope.from_dict_(
                self.__do_request("GET", url="/scope/get", body={"id": scope}, wanted_status=200).json())
        elif isinstance(scope, str):
            return KosmosScope.from_dict_(
                self.__do_request("GET", url="/scope/get", body={"name": scope}, wanted_status=200).json())

    def delete_scope(self, scope: str | int | KosmosScope) -> None:
        """
        delete a scope from kosmos

        Parameters
        ----------
        scope: str | int
            the name or id of the scope


        Raises
        -------
        KosmosAuthInvalid
            the auth was invalid
        KosmosForbidden
            the auth has not sufficient access to delete the scope
        KosmosConflictError
            could not add scope, name is in use
        KosmosNotFoundError
            the device could not be found!
        KosmosError
            anything else went wrong

        """
        if isinstance(scope, int):
            self.__do_request("DELETE", url="/scope/delete", body={"id": scope}, wanted_status=204)
        elif isinstance(scope, str):
            self.__do_request("DELETE", url="/scope/delete", body={"name": scope}, wanted_status=204)
        elif isinstance(scope, KosmosScope):
            if scope.id > 0:
                self.__do_request("DELETE", url="/scope/delete", body={"id": scope.id}, wanted_status=204)
            else:
                self.__do_request("DELETE", url="/scope/delete", body={"name": scope.name}, wanted_status=204)

    def set_location(self, device: str | KosmosDevice, location: KosmosLocation) -> None:
        """
        set the location of a device

        Parameters
        ----------

        device: str | KosmosDevice
            the device to update
        location: KosmosLocation
            the location to set it to

        """
        l = {k: v for k, v in location.to_dict().items() if v is not None}
        # print(l)
        # print(type(l))

        if isinstance(device, KosmosDevice):
            if self.is_connected():
                self.__ws.send(f"device/{device.uuid}/location:{json.dumps(l)}")
            else:
                l["uuid"] = device.uuid
                self.__do_request("POST", "/device/location", body=json.dumps(l), wanted_status=200)
            return
        if isinstance(device, str):
            if self.is_connected():
                self.__ws.send(f"device/{device}/location:{json.dumps(l)}")
            else:
                l["uuid"] = device
                self.__do_request("POST", "/device/location", body=json.dumps(l), wanted_status=200)
            return
        raise ValueError(f"could not parse Parameter device ({device})")

    def get_location(self, device: str | KosmosDevice) -> KosmosLocation:
        """
        gets the location of a given UUID back from kosmos

        Parameters
        ----------
        device: str
            the unique ID of the device

        Returns
        -------
        KosmosLocation
            the Location of the device

        Raises
        -------
        KosmosNotFoundError
            the device could not be found!
        KosmosAuthInvalid
            the auth was invalid
        KosmosForbidden
            the auth has not sufficient access to delete the schema
        KosmosConflictError
            could not add scope, name is in use
        KosmosError
            anything else went wrong



        """
        uuid = None
        if isinstance(device, KosmosDevice):
            uuid = device.uuid

        elif isinstance(device, str):
            uuid = device
        else:
            raise ValueError(f"could not parse Parameter device ({device})")

        r = self.__do_request('GET', "/device/location", params={"uuid": uuid}, wanted_status=200)
        if r is not None:
            if r.status_code == 200:
                return KosmosLocation.from_json(r.text)
            raise KosmosNotFoundError(f"could not find location for : {uuid}")
        return KosmosError()

    def __refresh_token(self):
        r = requests.post(f"{self.__base}/user/login", data={"user": self.__username, "pass": self.__password})
        if r.status_code == 200:
            # _LOGGER.info(f"logged in with token:{r.text}")
            self.__token = r.text
        else:
            _LOGGER.error(f"login FAILED {r.status_code} {r.text}")
            self.__token = None

    def __do_request(self, method: str, url: str, params: dict = None, body: str = None, tries_left: int = 1,
                     wanted_status: int = None) -> Response:
        """
        send a request to kosmos

        Parameters
        ----------
        method: str
            the HTTP-Method to use (POST,GET,DELETE,OPTIONS,PUT)
        url: str
            the url to use - if its not a fully qualified url it will be prefixed with the base url
        params: dict
            a dict with the parameters, defaults to None

        body: str
            the body to send with a post or put, defaults to None
        tries_left: int
            the number of tries we want to try it for, defaults to 1

        wanted_status: int
            the HTTP Status Code we expect, if plausible the request will be tried again if the actual HTTP Status Code differs

        Raises
        -------
        KosmosRequestFailed
            the request failed for some reason (most likely its return code was not equal to wanted_status
        KosmosAuthInvalid
            the auth was returned as invalid
        KosmosForbidden
            the auth has no access to this
        KosmosError
            some error occured


        """

        if self.__token is None:
            self.__refresh_token()
        if not url.startswith("http://") and not url.startswith("https://"):
            if url.startswith("/"):
                url = f"{self.__base}{url}"
            else:
                url = f"{self.__base}/{url}"

        if self.__token is not None:
            if isinstance(body, dict) or isinstance(body, list):
                # convert to stringified json
                body = json.dumps(body, default=str)
            headers = {"authorization": f"Bearer {self.__token}"}
            # add header
            r = requests.request(method=method, url=url, params=params, headers=headers, data=body)
            # _LOGGER.info(f"got result {r.status_code} for {url} - tries left {tries_left}")
            if wanted_status is not None and r.status_code == wanted_status:
                return r
            if r.status_code == 409:
                # we cannot fix 409, dont try again  if its already there it is already there
                raise KosmosConflictError(f"{r.reason} {r.text}")
            if r.status_code == 404:
                # we cannot fix 404, dont try again
                raise KosmosNotFoundError(f"{r.reason} {r.text}")
            if r.status_code == 403:
                # we cannot fix 409, dont try again  if its already there it is already there
                raise KosmosForbidden(f"{r.reason} {r.text}")
            if tries_left > 0:
                # check if we would be allowed to try again
                if r.status_code == 401:
                    # 401 can be saved, reset the token first
                    self.__token = None
                    return self.__do_request(method, url, params, body, tries_left - 1, wanted_status)
                if wanted_status is not None and r.status_code != wanted_status:
                    # the status was not what we wanted and might be fixable
                    return self.__do_request(method, url, params, body, tries_left - 1, wanted_status)
            if r.status_code == 401:
                raise KosmosAuthInvalid()

            raise KosmosRequestFailed(r)
        raise KosmosAuthInvalid()

    def __str__(self):
        return f"Kosmos Client ({self.__base})"
