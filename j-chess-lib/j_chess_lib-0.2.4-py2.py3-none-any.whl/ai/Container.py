from dataclasses import dataclass

from j_chess_lib.communication.schema import AwaitMoveMessage, MoveData


@dataclass(frozen=True)
class BoardState:
    fen: str


@dataclass(frozen=True)
class GameState:
    enemy_time: int
    your_time: int
    last_move: MoveData
    board_state: BoardState

    @classmethod
    def from_await_move(cls, data: AwaitMoveMessage) -> "GameState":
        return GameState(
            enemy_time=data.time_control.enemy_time_in_ms,
            your_time=data.time_control.your_time_in_ms,
            last_move=data.last_move,
            board_state=BoardState(fen=data.position),
        )
