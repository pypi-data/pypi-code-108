from typing import Callable
from uuid import uuid4, UUID

from j_chess_lib.communication import JchessMessage, JchessMessageType
from j_chess_lib.communication.schema import GameStartMessage, GameOverMessage, MoveMessage, MoveData
from j_chess_lib.ai import AI
from j_chess_lib.ai.Container import GameState
from .Match import Match


class Game:
    def __init__(self, data: GameStartMessage, recv: Callable[[], JchessMessage], send: Callable[[JchessMessage], None],
                 ai: AI, match: Match):
        self._id = uuid4()
        self._recv = recv
        self._send = send
        self._data = data
        self._ai = ai
        self._match = match
        self._ai.new_game(game_id=self.id, match_id=match.id, white_player=self._data.name_white)

    @property
    def id(self) -> UUID:
        return self._id

    def play(self) -> GameOverMessage:

        while True:
            message = self._recv()
            if message.message_type == JchessMessageType.AWAIT_MOVE:
                move_data = self._ai.get_move(game_id=self.id, match_id=self._match.id,
                                              game_state=GameState.from_await_move(data=message.await_move))
                move_message = self._match.client.base_msg()
                move_message.message_type = JchessMessageType.MOVE
                move_message.move = MoveMessage(move=move_data)
                self._send(move_message)
            elif message.message_type == JchessMessageType.GAME_OVER:
                winner = None if message.game_over.is_draw else message.game_over.winner
                self._ai.finalize_game(game_id=self.id, match_id=self._match.id,
                                       winner=winner, pgn=message.game_over.pgn)
                return message.game_over
