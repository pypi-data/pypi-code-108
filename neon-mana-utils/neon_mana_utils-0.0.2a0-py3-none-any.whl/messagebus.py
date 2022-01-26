# NEON AI (TM) SOFTWARE, Software Development Kit & Application Framework
# All trademark and other rights reserved by their respective owners
# Copyright 2008-2022 Neongecko.com Inc.
# Contributors: Daniel McKnight, Guy Daniels, Elon Gasper, Richard Leeds,
# Regina Bloomstine, Casimiro Ferreira, Andrii Pernatii, Kirill Hrymailo
# BSD-3 License
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from this
#    software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS  BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
# OR PROFITS;  OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE,  EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import json

from os.path import expanduser, isfile, abspath
from ruamel.yaml import YAML
from typing import Optional
from threading import Event
from mycroft_bus_client import MessageBusClient, Message
from typing import Set
from pprint import pprint

from neon_mana_utils.config import get_event_filters
from neon_mana_utils.constants import BASE_CONTEXT


def tail_messagebus(include: Set[str] = None, exclude: Set[str] = None,
                    format_output: bool = False, block: bool = False,
                    client: MessageBusClient = None):
    """
    Follow Messagebus activity like you would a logger
    :param include: set of msg_type prefixes to include in output (None to include all)
    :param exclude: set of msg_type prefixes to exclude in output (None to exclude none)
    :param format_output: if True, pformat logged messages
    :param block: if True, block this thread until keyboard interrupt
    :param client: MessageBusClient object to connect and use to monitor
    """
    def handle_message(serial_message: str):
        message = Message.deserialize(serial_message)
        if include and not any([x for x in include if message.msg_type.startswith(x)]):
            # Message not specified in included types
            return
        if exclude and any([x for x in exclude if message.msg_type.startswith(x)]):
            # Message is specified in excluded types
            return
        if format_output:
            pprint(json.loads(message.serialize()))
            print('---')
        else:
            print(message.serialize())

    default_filters = get_event_filters()
    include = include or default_filters["include"]
    exclude = exclude or default_filters["exclude"]

    print(f"Connecting to "
          f"{client.config.host}:{client.config.port}{client.config.route}")
    client.on('message', handle_message)
    if block:
        event = Event()
        try:
            event.wait()
        except KeyboardInterrupt:
            pass


def send_message_file(file_path: str, bus: MessageBusClient,
                      response: Optional[str] = None) -> Optional[Message]:
    """
    Parse a requested file into a Message object and send it over the bus.
    If `response` is specified, wait for and return the response message
    :param file_path: path to json or yaml defined message object to send
    :param bus: running MessageBusClient session to send message
    :param response: optional response msg_type to listen for and return
    :returns: Message if response is specified and received
    """
    file = abspath(expanduser(file_path))
    if not isfile(file):
        raise FileNotFoundError(file)
    with open(file) as f:
        try:
            serial = json.load(f)
        except json.JSONDecodeError:
            f.seek(0)
            serial = YAML().load(f)
    if not serial or not isinstance(serial, dict):
        raise ValueError(f"Invalid message specified in {file_path}")

    serial["context"] = serial.get("context") or BASE_CONTEXT
    try:
        message = Message(serial["msg_type"],
                          serial["data"], serial["context"])
    except KeyError:
        raise ValueError(f"Invalid message specified in {file_path}")

    if response:
        return bus.wait_for_response(message, response, 10)
    else:
        bus.emit(message)
