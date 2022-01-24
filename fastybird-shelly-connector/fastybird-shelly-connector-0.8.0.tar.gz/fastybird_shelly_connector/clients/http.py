#!/usr/bin/python3

#     Copyright 2021. FastyBird s.r.o.
#
#     Licensed under the Apache License, Version 2.0 (the "License");
#     you may not use this file except in compliance with the License.
#     You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.

"""
Shelly connector clients module CoAP client
"""

# Python base dependencies
import base64
import json
import re
import time
from http import client
from socket import gethostbyaddr, timeout  # pylint: disable=no-name-in-module
from typing import Optional, Tuple

# Library libs
from fastybird_shelly_connector.clients.base import IClient
from fastybird_shelly_connector.logger import Logger
from fastybird_shelly_connector.receivers.receiver import Receiver
from fastybird_shelly_connector.registry.model import (
    AttributesRegistry,
    BlocksRegistry,
    CommandsRegistry,
    DevicesRegistry,
)
from fastybird_shelly_connector.registry.records import DeviceRecord, SensorRecord
from fastybird_shelly_connector.types import (
    ClientMessageType,
    ClientType,
    DeviceAttribute,
    DeviceCommandType,
    DeviceDescriptionSource,
    WritableSensor,
)
from fastybird_shelly_connector.utilities.helpers import DataTransformHelpers


class HttpClient(IClient):  # pylint: disable=too-many-instance-attributes
    """
    Basic HTTP API client

    @package        FastyBird:ShellyConnector!
    @module         clients/http

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __receiver: Receiver

    __devices_registry: DevicesRegistry
    __attributes_registry: AttributesRegistry
    __commands_registry: CommandsRegistry
    __blocks_registry: BlocksRegistry

    __logger: Logger

    __SHELLY_INFO_ENDPOINT: str = "/shelly"
    __STATUS_ENDPOINT: str = "/status"
    __DESCRIPTION_ENDPOINT: str = "/cit/d"
    __SET_CHANNEL_SENSOR_ENDPOINT: str = "/{channel}/{index}?{action}={value}"

    __SENDING_CMD_DELAY: float = 60

    # -----------------------------------------------------------------------------

    def __init__(  # pylint: disable=too-many-arguments
        self,
        receiver: Receiver,
        devices_registry: DevicesRegistry,
        attributes_registry: AttributesRegistry,
        commands_registry: CommandsRegistry,
        blocks_registry: BlocksRegistry,
        logger: Logger,
    ) -> None:
        self.__receiver = receiver

        self.__devices_registry = devices_registry
        self.__attributes_registry = attributes_registry
        self.__commands_registry = commands_registry
        self.__blocks_registry = blocks_registry

        self.__logger = logger

    # -----------------------------------------------------------------------------

    @property
    def type(self) -> ClientType:
        """Client type"""
        return ClientType.HTTP

    # -----------------------------------------------------------------------------

    def start(self) -> None:
        """Start communication"""

    # -----------------------------------------------------------------------------

    def stop(self) -> None:
        """Stop communication"""

    # -----------------------------------------------------------------------------

    def is_connected(self) -> bool:
        """Check if client is connected"""
        return True

    # -----------------------------------------------------------------------------

    def discover(self) -> None:
        """Send discover command"""

    # -----------------------------------------------------------------------------

    def handle(self) -> None:
        """Process HTTP requests"""
        for device_record in self.__devices_registry:
            ip_address_attribute = self.__attributes_registry.get_by_attribute(
                device_id=device_record.id,
                attribute_type=DeviceAttribute.IP_ADDRESS,
            )

            if ip_address_attribute is None or not isinstance(ip_address_attribute.value, str):
                continue

            if DeviceDescriptionSource.HTTP_SHELLY not in device_record.description_source:
                self.__send_command(
                    device_record=device_record,
                    host=ip_address_attribute.value,
                    endpoint=self.__SHELLY_INFO_ENDPOINT,
                    command=DeviceCommandType.GET_SHELLY,
                )

                return

            if DeviceDescriptionSource.HTTP_STATUS not in device_record.description_source:
                self.__send_command(
                    device_record=device_record,
                    host=ip_address_attribute.value,
                    endpoint=self.__STATUS_ENDPOINT,
                    command=DeviceCommandType.GET_STATUS,
                )

                return

            if DeviceDescriptionSource.HTTP_DESCRIPTION not in device_record.description_source:
                self.__send_command(
                    device_record=device_record,
                    host=ip_address_attribute.value,
                    endpoint=self.__DESCRIPTION_ENDPOINT,
                    command=DeviceCommandType.GET_DESCRIPTION,
                )

                return

    # -----------------------------------------------------------------------------

    def write_sensor(self, sensor_record: SensorRecord) -> None:
        """Write value to device sensor"""
        block_record = self.__blocks_registry.get_by_id(block_id=sensor_record.block_id)

        if block_record is None:
            return

        device_record = self.__devices_registry.get_by_id(device_id=block_record.device_id)

        if device_record is None:
            return

        ip_address_attribute = self.__attributes_registry.get_by_attribute(
            device_id=device_record.id,
            attribute_type=DeviceAttribute.IP_ADDRESS,
        )

        if ip_address_attribute is None or not isinstance(ip_address_attribute.value, str):
            return

        match = re.compile("(?P<channelName>[a-zA-Z]+)_(?P<channelIndex>[0-9_]+)")

        test = match.fullmatch(block_record.description)

        if test is None:
            return

        expected_value = DataTransformHelpers.transform_to_device(
            data_type=sensor_record.data_type,
            value_format=sensor_record.format,
            value=sensor_record.expected_value,
        )

        if expected_value is None:
            return

        success, _ = self.__send_http_get(
            host=ip_address_attribute.value,
            url=self.__SET_CHANNEL_SENSOR_ENDPOINT.replace("{channel}", test.group("channelName"))
            .replace("{index}", test.group("channelIndex"))
            .replace("{action}", self.__build_action(sensor_record=sensor_record))
            .replace("{value}", str(expected_value)),
            username=device_record.username,
            password=device_record.password,
        )

        self.__commands_registry.create_or_update(
            device_id=device_record.id,
            client_type=self.type,
            command_type=DeviceCommandType.SET_SENSOR,
            command_status=success,
        )

    # -----------------------------------------------------------------------------

    def __send_command(
        self,
        device_record: DeviceRecord,
        host: Optional[str],
        endpoint: str,
        command: DeviceCommandType,
    ) -> None:
        http_command = self.__commands_registry.get_by_command(
            device_id=device_record.id, client_type=self.type, command_type=command
        )

        if http_command is None or time.time() - http_command.command_timestamp >= self.__SENDING_CMD_DELAY:
            if host is not None:
                success, response = self.__send_http_get(
                    host=host,
                    url=endpoint,
                    username=device_record.username,
                    password=device_record.password,
                )

                self.__commands_registry.create_or_update(
                    device_id=device_record.id,
                    client_type=self.type,
                    command_type=command,
                    command_status=success,
                )

                if success:
                    self.__receiver.on_http_message(
                        device_identifier=device_record.identifier.lower(),
                        device_ip_address=host,
                        message_payload=response,
                        message_type=self.__get_message_type_for_command(command=command),
                    )

            else:
                self.__commands_registry.create_or_update(
                    device_id=device_record.id,
                    client_type=self.type,
                    command_type=command,
                    command_status=False,
                )

    # -----------------------------------------------------------------------------

    def __send_http_get(  # pylint: disable=too-many-locals,too-many-arguments
        self,
        host: str,
        url: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        log_error: bool = True,
    ) -> Tuple[bool, str]:
        """Send HTTP GET request"""
        res = ""
        success = False
        conn = None

        try:
            self.__logger.debug(
                "http://%s%s",
                host,
                url,
                extra={
                    "client": {
                        "type": ClientType.HTTP.value,
                    },
                },
            )

            conn = client.HTTPConnection(host, timeout=5)

            headers = {"Connection": "close"}

            conn.request("GET", url, None, headers)

            resp = conn.getresponse()

            if resp.status == 401 and username is not None and password is not None:
                combo = f"{username}:{password}"
                auth = str(base64.b64encode(combo.encode()), "cp1252")

                headers["Authorization"] = f"Basic {auth}"

                conn.request("GET", url, None, headers)

                resp = conn.getresponse()

            if resp.status == 200:
                body = resp.read()

                res = json.dumps(json.loads(str(body, "cp1252")))

                success = True

                self.__logger.debug(
                    "http://%s%s - OK",
                    host,
                    url,
                    extra={
                        "client": {
                            "type": ClientType.HTTP.value,
                        },
                    },
                )

            else:
                res = f"Error, {resp.status} {resp.reason} http://{host}{url}"

                self.__logger.warning(
                    res,
                    extra={
                        "client": {
                            "type": ClientType.HTTP.value,
                        },
                    },
                )

        except Exception as ex:  # pylint: disable=broad-except
            success = False

            if isinstance(ex, timeout):
                msg = f"Timeout connecting to http://{host}{url}"

                try:
                    res = gethostbyaddr(host)[0]
                    msg += " [" + res + "]"

                except Exception:  # pylint: disable=broad-except
                    pass

                self.__logger.error(
                    msg,
                    extra={
                        "client": {
                            "type": ClientType.HTTP.value,
                        },
                    },
                )

            else:
                res = str(ex)

                if log_error:
                    self.__logger.error(
                        "Error http GET: http://%s%s",
                        host,
                        url,
                        extra={
                            "client": {
                                "type": ClientType.HTTP.value,
                            },
                            "exception": {
                                "message": str(ex),
                                "code": type(ex).__name__,
                            },
                        },
                    )

                else:
                    self.__logger.debug(
                        "Fail http GET: %s %s %s",
                        host,
                        url,
                        ex,
                        extra={
                            "client": {
                                "type": ClientType.HTTP.value,
                            },
                        },
                    )
        finally:
            if conn:
                conn.close()

        return success, res

    # -----------------------------------------------------------------------------

    @staticmethod
    def __get_message_type_for_command(command: DeviceCommandType) -> ClientMessageType:
        if command == DeviceCommandType.GET_SHELLY:
            return ClientMessageType.HTTP_SHELLY

        if command == DeviceCommandType.GET_STATUS:
            return ClientMessageType.HTTP_STATUS

        if command == DeviceCommandType.GET_DESCRIPTION:
            return ClientMessageType.HTTP_DESCRIPTION

        raise AttributeError("Provided command is not supported by connector")

    # -----------------------------------------------------------------------------

    @staticmethod
    def __build_action(sensor_record: SensorRecord) -> str:
        if sensor_record.description == WritableSensor.OUTPUT.value:
            return "turn"

        if sensor_record.description == WritableSensor.COLOR_TEMP.value:
            return "temp"

        return sensor_record.description
