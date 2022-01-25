from typing import Optional
from uuid import uuid4, UUID
import threading
import queue

from ..communication import Connection, JchessMessage, JchessMessageType
from ..communication.schema import LoginMessage
from ..ai import AI
from .Exceptions import UnhandledMessageError, LoginFailedError, InterruptClient


class Client(threading.Thread):

    def __init__(self, connection: Connection, ai: AI):
        self._id = uuid4()
        self._original_id = self._id
        self._ai = ai
        self._connection = connection
        self._send_queue: queue.Queue[JchessMessage] = queue.Queue()
        self._recv_queue: queue.Queue[JchessMessage] = queue.Queue()
        super().__init__(daemon=False, name=f"ClientThread-{ai.name}")

        class SendThread(threading.Thread):
            def __init__(self, _connection: Connection, _send_queue: queue.Queue[JchessMessage]):
                super().__init__(daemon=True)
                self._connection = _connection
                self._send_queue = _send_queue

            def run(self) -> None:
                while True:
                    message = self._send_queue.get()
                    self._connection.send(message=message)

        class RecvThread(threading.Thread):
            def __init__(self, _connection: Connection, _recv_queue: queue.Queue[JchessMessage]):
                super().__init__(daemon=True)
                self._connection = _connection
                self._recv_queue = _recv_queue

            def run(self) -> None:
                while True:
                    message = self._connection.recv()
                    # print("MESSAGE", message)
                    self._recv_queue.put(message)

        send_thread = SendThread(_connection=connection, _send_queue=self._send_queue)
        recv_thread = RecvThread(_connection=connection, _recv_queue=self._recv_queue)
        send_thread.start()
        recv_thread.start()

    @property
    def id(self) -> UUID:
        return self._id

    @property
    def ai(self) -> AI:
        return self._ai

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if isinstance(other, Client):
            return other.id == self.id
        return False

    def __str__(self):
        return f"Client {self.id} with {self.ai.name}"

    def base_msg(self) -> JchessMessage:
        return JchessMessage(player_id=str(self.id))

    def _send(self, message: JchessMessage):
        self._send_queue.put(message)

    def _recv(self) -> JchessMessage:
        message = self._recv_queue.get()
        message = self._intercept_disconnect(message=message)
        message = self._intercept_heartbeat(message=message)
        if message is None:
            return self._recv()
        return message

    def run(self):
        try:
            # --Region Login--
            new_id = self._handle_login()
            if new_id is None:
                print("Login failed")
                raise LoginFailedError()
            print(f"Login success{f' id changed {self._id} -> {new_id}'}" if self._id != new_id else '')
            self._original_id = self._id
            self._id = new_id
            # --Region Login--

            while True:
                message = self._recv()
                if message.message_type == JchessMessageType.MATCH_FOUND:
                    self._handle_match(message=message)

        except InterruptClient as e:
            print("Client interrupeted and killed")
            print(f"Cause: {e}")

    def _intercept_disconnect(self, message: JchessMessage) -> Optional[JchessMessage]:
        if message is None:
            return message
        if message.message_type == JchessMessageType.DISCONNECT:
            raise InterruptClient(message.disconnect.error_type_code)
        return message

    def _intercept_heartbeat(self, message: JchessMessage) -> Optional[JchessMessage]:
        if message is None:
            return message
        if message.message_type == JchessMessageType.HEART_BEAT:
            print("Received a heartbeat")
            return None
        return message

    def _handle_login(self) -> Optional[UUID]:
        login = LoginMessage(name=self.ai.name)
        message = self.base_msg()
        message.login = login
        message.message_type = JchessMessageType.LOGIN
        self._send(message=message)
        message = self._recv()
        if message.message_type == JchessMessageType.LOGIN_REPLY:
            repl_id = message.login_reply.new_id
            return UUID(repl_id)
        elif message.message_type == JchessMessageType.ACCEPT:
            return self._handle_login()
        elif message.message_type == JchessMessageType.DISCONNECT:
            return None
        else:
            raise UnhandledMessageError(message=message)

    def _handle_match(self, message: JchessMessage):
        from .match import Match
        match: Match = Match.handle_match(message=message, recv=self._recv, ai=self.ai, client=self, send=self._send)
        match.play_match()
