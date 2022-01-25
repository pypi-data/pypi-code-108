from abc import ABC, abstractmethod
from typing import Callable, List
from uuid import uuid4, UUID

from j_chess_lib.ai import AI
from j_chess_lib.communication import JchessMessage, JchessMessageType
from j_chess_lib.communication.schema import MatchFormatData, MatchFoundMessage, MatchOverMessage
from j_chess_lib.client.Exceptions import WrongMessageType
from j_chess_lib.client.Client import Client


class Match:

    def __init__(self, data: MatchFoundMessage, recv: Callable[[], JchessMessage],
                 send: Callable[[JchessMessage], None], ai: AI, client: Client):
        self._recv = recv
        self._send = send
        self._ai = ai
        self._client = client
        self._match_id: UUID = None
        self._enemy: str = None
        self._format: MatchFormatData = None
        self.new_match(data=data)

    @property
    def client(self) -> Client:
        return self._client

    @property
    def id(self) -> UUID:
        return self._match_id

    @classmethod
    def handle_match(cls, message: JchessMessage, recv: Callable[[], JchessMessage],
                     send: Callable[[JchessMessage], None], ai: AI, client: Client) -> "Match":
        if not message.message_type == JchessMessageType.MATCH_FOUND:
            raise WrongMessageType(message=message, expected_type=(JchessMessageType.MATCH_FOUND, ))

        return cls(data=message.match_found, recv=recv, send=send, ai=ai, client=client)

    def new_match(self, data: MatchFoundMessage):
        self._match_id = UUID(data.match_id)
        self._enemy = data.enemy_name
        self._format = data.match_format
        self._ai.new_match(match_id=self._match_id, enemy=self._enemy, match_format=self._format)

    def end_match(self, data: MatchOverMessage):
        self._ai.finalize_match(match_id=self._match_id, status=data.match_status, statistics=data.statistics)
        self._match_id = None
        self._enemy = None
        self._format = None

    def play_match(self):
        while True:
            message = self._recv()
            if message.message_type == JchessMessageType.MATCH_FOUND:
                self.new_match(data=message.match_found)
            elif message.message_type == JchessMessageType.MATCH_OVER:
                self.end_match(data=message.match_over)
            elif message.message_type == JchessMessageType.GAME_START:
                from .Game import Game
                game: Game = Game(data=message.game_start, recv=self._recv, send=self._send, ai=self._ai, match=self)
                message = game.play()



