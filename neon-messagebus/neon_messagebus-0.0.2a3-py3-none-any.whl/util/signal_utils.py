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

from threading import Event
from time import time
from typing import Optional, Dict
from mycroft_bus_client import MessageBusClient, Message
from neon_utils.logger import LOG
from neon_utils.configuration_utils import get_neon_local_config
from ovos_utils.signal import create_signal, check_for_signal

_SIGNAL_CONFIG = {"ipc_path": get_neon_local_config()['dirVars']['ipcDir']}


class Signal:
    def __init__(self):
        self.create_time = time()
        self._created_event = Event()
        self._cleared_event = Event()
        self._created_event.clear()
        self._cleared_event.set()

    @property
    def is_set(self):
        """
        Boolean state of signal creation
        """
        return self._created_event.is_set()

    def create(self):
        """
        Marks this signal as created
        """
        self.create_time = time()
        self._cleared_event.clear()
        self._created_event.set()

    def clear(self):
        """
        Marks this signal as cleared
        """
        self._created_event.clear()
        self._cleared_event.set()

    def wait_for_create(self, timeout: Optional[int] = None) -> bool:
        """
        Wait for the signal to be created
        :param timeout: Seconds to wait for the signal to be set
        :return: True if the signal is set
        """
        return self._created_event.wait(timeout)

    def wait_for_clear(self, timeout: Optional[int] = None) -> bool:
        """
        Wait for the signal to be cleared
        :param timeout: Seconds to wait for the signal to be cleared
        :return: True if the signal is set
        """
        self._cleared_event.wait(timeout)
        return self.is_set


class SignalManager:
    def __init__(self, bus: MessageBusClient = None, handle_files: bool = True):
        self._signals: Dict[str, Signal] = dict()
        self.bus = bus or MessageBusClient()
        self._handle_files = handle_files
        self._register_listeners()
        self.bus.run_in_thread()
        if not self.bus.connected_event.wait(60):
            LOG.error(f"Bus not connected after 60 seconds")

    def create_signal(self, signal: str) -> bool:
        """
        Set the specified signal, creating it if it doesn't exist
        """
        self._ensure_signal_is_defined(signal)
        self._signals[signal].create()
        if self._handle_files:
            create_signal(signal, config=_SIGNAL_CONFIG)
        return True

    def check_for_signal(self, signal: str, sec_lifetime: int = 0):
        """
        Check if the specified signal exists and is set, optionally clearing it
        """
        if signal not in self._signals or not self._signals[signal].is_set:
            # Signal not defined or not set
            return False
        if sec_lifetime == 0:
            # Clear the signal and return
            self._signals[signal].clear()
            if self._handle_files:
                check_for_signal(signal, config=_SIGNAL_CONFIG)
            return True
        if sec_lifetime == -1:
            # Return signal state (True)
            return True
        if self._signals[signal].create_time + sec_lifetime < time():
            # Signal is expired and must be cleared
            LOG.debug(f"Clearing expired signal: {signal}")
            self._signals[signal].clear()
            if self._handle_files:
                check_for_signal(signal, config=_SIGNAL_CONFIG)
            return False
        # Signal exists and is not yet expired
        return True

    def wait_for_signal_set(self, signal: str, sec_timeout: Optional[int] = None) -> bool:
        """
        Wait for the specified signal to be set and return set state after timeout
        """
        self._ensure_signal_is_defined(signal)
        return self._signals[signal].wait_for_create(sec_timeout)

    def wait_for_signal_clear(self, signal: str, sec_timeout: Optional[int] = None) -> bool:
        """
        Wait for the specified signal to be set and return set state after timeout
        """
        self._ensure_signal_is_defined(signal)
        return self._signals[signal].wait_for_clear(sec_timeout)

    def _ensure_signal_is_defined(self, signal):
        if signal not in self._signals or not isinstance(self._signals[signal], Signal):
            self._signals[signal] = Signal()

    def _register_listeners(self):
        """
        Register Event Handlers
        """
        self.bus.on("neon.create_signal", self._handle_create_signal)
        self.bus.on("neon.check_for_signal", self._handle_check_for_signal)
        self.bus.on("neon.wait_for_signal_create", self._handle_wait_for_signal_create)
        self.bus.on("neon.wait_for_signal_clear", self._handle_wait_for_signal_clear)
        self.bus.on("neon.signal_manager_active", self._handle_signal_manager_active)

    def _handle_create_signal(self, message: Message):
        signal_name = message.data["signal_name"]
        status = self.create_signal(signal_name)
        self.bus.emit(message.reply(f"neon.create_signal.{signal_name}",
                                    data={"signal_name": signal_name,
                                          "is_set": status}))

    def _handle_check_for_signal(self, message: Message):
        signal_name = message.data["signal_name"]
        status = self.check_for_signal(signal_name, message.data.get("sec_lifetime", 0))
        self.bus.emit(message.reply(f"neon.check_for_signal.{signal_name}",
                                    data={"signal_name": signal_name,
                                          "is_set": status}))

    def _handle_wait_for_signal_create(self, message: Message):
        signal_name = message.data["signal_name"]
        status = self.wait_for_signal_set(signal_name, message.data.get("timeout"))
        self.bus.emit(message.reply(f"neon.wait_for_signal_create.{signal_name}",
                                    data={"signal_name": signal_name,
                                          "is_set": status}))

    def _handle_wait_for_signal_clear(self, message: Message):
        signal_name = message.data["signal_name"]
        status = self.wait_for_signal_clear(signal_name, message.data.get("timeout"))
        LOG.debug(f"Wait returning {status}")
        self.bus.emit(message.reply(f"neon.wait_for_signal_clear.{signal_name}",
                                    data={"signal_name": signal_name,
                                          "is_set": status}))

    def _handle_signal_manager_active(self, message: Message):
        self.bus.emit(message.response())
