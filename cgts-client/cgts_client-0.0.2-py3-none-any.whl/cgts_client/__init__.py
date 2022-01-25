# Copyright (C) 2022  Karl Sundequist Blomdahl <karl.sundequist.blomdahl@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import argparse
import asyncio
import logging
import requests
import sys
import time
from collections import deque
from typing import List

logging.basicConfig()
LOGGER = logging.getLogger('cgts_client')

def parse_args(args: List[str]):
    parser = argparse.ArgumentParser(description='Computer Go Tournament Client')
    parser.add_argument('--debug', action='store_true', help='enable debugging output')
    parser.add_argument('--key', nargs='?', required=True, help='unique engine identifier')
    parser.add_argument('command', nargs=1)
    parser.add_argument('arguments', nargs='*')
    return parser.parse_args(args)

class Engine:
    def __init__(self, command: str, arguments: List[str]):
        self._command = command
        self._arguments = arguments
        self._logger = LOGGER.getChild('engine')
        self._seq = 1000
        self._proc = None
        self._setUp()

    def _setUp(self):
        self._name = self.communicate('name')
        self._version = self.communicate('version')
        self._played_sequence = []

    async def _start_process(self):
        self._logger.debug(f'starting subprocess \'{self._command}\' with arguments {self._arguments}')
        self._played_sequence = []
        self._proc = await asyncio.create_subprocess_exec(
            self._command,
            *self._arguments,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

    async def _ensure_process(self):
        if self._proc is None or self._proc.stdin.is_closing():
            if self._proc is not None:
                self._logger.warning(f'subprocess exited with status code {self._proc.returncode}')
            await self._start_process()

    async def _write_stdin(self, line: str):
        self._logger.getChild('stdin').info(line.rstrip())
        self._proc.stdin.write(line.encode('utf-8'))
        await self._proc.stdin.drain()

    async def _handle_stderr(self):
        async for line in self._proc.stderr:
            self._logger.getChild('stderr').info(line.decode('utf-8').rstrip())

    async def _handle_stdout(self):
        is_error = False
        response = []

        async for line in self._proc.stdout:
            line = line.decode('utf-8')
            self._logger.getChild('stdout').info(line.rstrip())

            if line == '\n':
                break
            elif line.startswith(f'={self._seq}'):
                response = [
                    line.replace(f'={self._seq}', '', 1).strip()
                ]
            elif line.startswith(f'?{self._seq}'):
                is_error = True
                response = [
                    line.replace(f'?{self._seq}', '', 1).strip()
                ]
            else:
                response.append(line.rstrip())

        if is_error:
            raise ValueError('\n'.join(response))
        return '\n'.join(response)

    async def _communicate(self, command: str) -> str:
        try:
            await self._ensure_process()
            await self._write_stdin(f'{self._seq} {command}\n')

            handle_stdout = asyncio.create_task(self._handle_stdout())
            handle_stderr = asyncio.create_task(self._handle_stderr())
            done, pending = await asyncio.wait(
                [handle_stdout, handle_stderr],
                return_when=asyncio.FIRST_COMPLETED
            )

            for task in pending:
                task.cancel()

            if handle_stdout in done:
                return handle_stdout.result()
            return None
        finally:
            self._seq += 1

    def _skip_played_prefix(self, sequence):
        remaining = deque(sequence)

        for played_move in self._played_sequence:
            if not remaining or played_move.lower() != remaining[0].lower():
                break
            remaining.popleft()

        return remaining

    @property
    def name(self) -> str:
        return self._name

    @property
    def version(self) -> str:
        return self._version

    def ensure_sequence(self, sequence: List[str]):
        for move in self._skip_played_prefix(sequence):
            self._played_sequence.append(move)
            self.communicate(f'play {move}')

    def communicate(self, command: str) -> str:
        for _ in range(3):
            result = asyncio.get_event_loop().run_until_complete(
                self._communicate(command)
            )

            if result is not None:
                return result

    def genmove(self, color: str) -> str:
        response = self.communicate(f'genmove {color}')

        if response:
            self._played_sequence.append(f'{color} {response}')
            return response

def _retry_loop(callback, max_wait=15.0):
    retry_time = 0.5

    while True:
        response = callback()
        if response is not None:
            return response

        time.sleep(retry_time)
        retry_time = min(2.0 * retry_time, max_wait)

class Beat:
    def __init__(self, session, sequence, action, webhook_url):
        self._session = session
        self._sequence = sequence
        self._action = action
        self._webhook_url = webhook_url
        self._logger = LOGGER.getChild('webhook')

    @property
    def sequence(self):
        return self._sequence

    @property
    def action(self):
        return self._action

    def _post(self, response_text: str):
        response = self._session.post(f'https://cgts.herokuapp.com/{self._webhook_url}', json={'response': response_text})
        if response.status_code != 200:
            self._logger.error(f'received status {response.status_code} from {response.url}')
            return None
        else:
            return response

    def post(self, response_text: str):
        return _retry_loop(lambda: self._post(response_text))

class Server:
    def __init__(self, key):
        self._key = key
        self._logger = LOGGER.getChild('heartbeat')
        self._session = requests.Session()

    def _heartbeat(self) -> Beat:
        response = self._session.get(f'https://cgts.herokuapp.com/api/v1/heartbeat/{self._key}')
        if response.status_code != 200:
            self._logger.error(f'received status {response.status_code} from {response.url}')
        else:
            body = response.json()

            return Beat(
                self._session,
                body['sequence'],
                body['action'],
                body['webhook_url']
            )

    def heartbeat(self) -> Beat:
        return _retry_loop(self._heartbeat)

def main():
    args = parse_args(sys.argv[1:])
    if args.debug:
        LOGGER.setLevel(logging.DEBUG)

    engine = Engine(args.command[0], args.arguments)
    upstream = Server(args.key)

    while True:
        beat = upstream.heartbeat()
        engine.ensure_sequence(beat.sequence)
        if beat.action == 'genmove b':
            response = engine.genmove('b')
        elif beat.action == 'genmove w':
            response = engine.genmove('w')
        else:
            response = engine.communicate(beat.action)
        beat.post(response)
