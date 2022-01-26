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

from mycroft_bus_client import MessageBusClient, Message
from neon_mana_utils.constants import BASE_CONTEXT


def start_listening(client: MessageBusClient):
    """
    Emit a minimal message to start listening on a standalone device
    :param client: connected and running MessageBusClient
    """
    client.emit(Message("mycroft.mic.listen", context=BASE_CONTEXT))


def stop(client: MessageBusClient):
    """
    Emit a minimal message to 'stop' on a standalone device
    :param client: connected and running MessageBusClient
    """
    client.emit(Message("mycroft.stop", context=BASE_CONTEXT))


def say_to(client: MessageBusClient, utterance: str, lang: str = "en-us"):
    """
    Emit a minimal text input (mimics a minimal Mycroft message)
    :param client: connected and running MessageBusClient
    :param utterance: utterance to send as user input
    :param lang: BCP-47 language code associated with utterance
    """
    data = {"utterances": [utterance],
            "lang": lang}
    context = BASE_CONTEXT
    client.emit(Message("recognizer_loop:utterance", data, context))


def speak(client: MessageBusClient, utterance: str):
    """
    Emit a minimal speak message (mimics a minimal Mycroft message)
    :param client: connected and running MessageBusClient
    :param utterance: utterance to be spoken
    """
    data = {"utterance": utterance}
    context = BASE_CONTEXT
    client.emit(Message("speak", data, context))
