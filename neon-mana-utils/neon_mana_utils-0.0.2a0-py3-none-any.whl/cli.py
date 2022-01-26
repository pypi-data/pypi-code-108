# NEON AI (TM) SOFTWARE, Software Development Kit & Application Development System
# All trademark and other rights reserved by their respective owners
# Copyright 2008-2021 Neongecko.com Inc.
# BSD-3
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
from pprint import pformat

import click
from click_default_group import DefaultGroup
from mycroft_bus_client import MessageBusClient

from neon_mana_utils.config import get_messagebus_config
from neon_mana_utils.version import __version__


@click.group("mana", cls=DefaultGroup,
             no_args_is_help=True, invoke_without_command=True,
             help="Mana: Message Application for Neon AI.\n\n"
                  "See also: mana COMMAND --help")
@click.option("--version", "-v", is_flag=True, required=False,
              help="Print the current version")
def neon_mana_cli(version: bool = False):
    if version:
        click.echo(f"Mana version {__version__}")


@neon_mana_cli.command(help="Set Messagebus Config")
@click.option('--host', '-h', default="0.0.0.0",
              help="Default Host (IP or hostname)")
@click.option('--port', '-p', default=8181,
              help="Default Port")
@click.option('--ssl', default=False,
              help="Use SSL")
@click.option('--route', '-r', default="/core",
              help="Default Route")
def configure_messagebus(host, port, route, ssl):
    from neon_mana_utils.config import set_messagebus_config
    set_messagebus_config(host, port, route, ssl)


@neon_mana_cli.command(help="Show configurations")
def print_config():
    from neon_mana_utils.config import print_config, get_config_dir
    conf = print_config()
    click.echo(f"Config Path: {get_config_dir()}\n")
    click.echo(conf)


@neon_mana_cli.command(help="Monitor messages sent over the messagebus")
@click.option('--include', '-i', multiple=True,
              help="Optional msg_type prefix to include in output")
@click.option('--exclude', '-e', multiple=True,
              help="Optional msg_type prefix to exclude from output")
@click.option('--format', '-f', is_flag=True, default=False,
              help="Format printed message outputs")
@click.option('--host', '-h', default=None,
              help="host to connect to (IP or hostname)")
@click.option('--port', '-p', default=None,
              help="port to connect to")
@click.option('--ssl', default=False,
              help="Connect using secured websocket")
@click.option('--route', '-r', default=None,
              help="websocket route to connect to")
def tail_messagebus(host, port, route, ssl, format, include, exclude):
    from neon_mana_utils.messagebus import tail_messagebus
    default = get_messagebus_config()
    config = {"host": host or default["host"],
              "port": port or default["port"],
              "route": route or default["route"],
              "ssl": ssl or default["ssl"]}
    client = MessageBusClient(**config)
    client.run_in_thread()
    tail_messagebus(include, exclude, format, True, client)
    click.echo("Exiting")


@neon_mana_cli.command(help="Start listening immediately")
def listen():
    from neon_mana_utils.core_commands import start_listening
    client = MessageBusClient(**get_messagebus_config())
    client.run_in_thread()
    start_listening(client)


@neon_mana_cli.command(help="Emit a stop message")
def stop():
    from neon_mana_utils.core_commands import stop
    client = MessageBusClient(**get_messagebus_config())
    client.run_in_thread()
    stop(client)


@neon_mana_cli.command(help="Emit a minimal user input message")
@click.option('--lang', '-l', default="en-us",
              help="Language of the input text")
@click.argument('utterance')
def say_to(utterance, lang):
    from neon_mana_utils.core_commands import say_to
    client = MessageBusClient(**get_messagebus_config())
    client.run_in_thread()
    say_to(client, utterance, lang)


@neon_mana_cli.command(help="Emit a minimal speak message")
@click.argument('utterance')
def speak(utterance):
    from neon_mana_utils.core_commands import speak
    client = MessageBusClient(**get_messagebus_config())
    client.run_in_thread()
    speak(client, utterance)


@neon_mana_cli.command(help="Get an STT response")
@click.option('--file', '-f', default=None,
              help="File to transcribe")
@click.option('--lang', '-l', default="en-us",
              help="Language of audio in file")
def get_stt(file, lang):
    from neon_mana_utils.bus_api import get_stt

    if not file:
        click.echo("No audio file specified")
        return

    client = MessageBusClient(**get_messagebus_config())
    client.run_in_thread()
    message = get_stt(client, audio_path=file, lang=lang)
    if message:
        click.echo(pformat(json.loads(message.serialize())))
    else:
        click.echo("No Response")


@neon_mana_cli.command(help="Get a TTS response")
@click.option('--text', '-t', default=None,
              help="Text to synthesize")
def get_tts(text):
    from neon_mana_utils.bus_api import get_tts

    if not text:
        click.echo("No text specified")

    client = MessageBusClient(**get_messagebus_config())
    client.run_in_thread()
    message = get_tts(client, text)
    if message:
        click.echo(pformat(json.loads(message.serialize())))
    else:
        click.echo("No Response")


@neon_mana_cli.command(help="Get a skill response")
@click.option('--utterance', '-u',
              help="Input utterance to send to skills")
@click.option('--lang', '-l', default="en-us",
              help="Language of the input utterance")
def get_response(utterance, lang):
    from neon_mana_utils.bus_api import get_response
    # TODO: Handle message loading DM
    if not utterance:
        click.echo("Empty utterance received")
    client = MessageBusClient(**get_messagebus_config())
    client.run_in_thread()
    message = get_response(client, utterance, lang)
    if message:
        click.echo(pformat(json.loads(message.serialize())))
    else:
        click.echo("No Response")


@neon_mana_cli.command(help="Send a json or yaml serialized message")
@click.option('--response', '-r', default=None,
              help="Optional response message type to listen to")
@click.argument('file')
def send_message(response, file):
    from neon_mana_utils.messagebus import send_message_file
    client = MessageBusClient(**get_messagebus_config())
    client.run_in_thread()
    try:
        response = send_message_file(file, client, response)
        if response:
            click.echo(pformat(json.loads(response.serialize())))
        elif response:
            click.echo("No Response")
        else:
            click.echo("Message Sent")
    except Exception as e:
        click.echo(e)
