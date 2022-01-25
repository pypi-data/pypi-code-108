from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


@dataclass
class DrawResponseMessage:
    accept: Optional[bool] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "",
            "required": True,
        }
    )


class ErrorType(Enum):
    NO_ERROR = "NO_ERROR"
    ERROR = "ERROR"
    AWAIT_LOGIN = "AWAIT_LOGIN"
    TIMEOUT = "TIMEOUT"
    TOO_MANY_TRIES = "TOO_MANY_TRIES"
    UNSUPPORTED_OPERATION = "UNSUPPORTED_OPERATION"
    DUPLICATE_NAME = "DUPLICATE_NAME"
    VERSION_MISMATCH = "VERSION_MISMATCH"


@dataclass
class GameOverMessage:
    winner: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "",
            "required": True,
        }
    )
    is_draw: Optional[bool] = field(
        default=None,
        metadata={
            "name": "isDraw",
            "type": "Element",
            "namespace": "",
            "required": True,
        }
    )
    pgn: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "",
            "required": True,
        }
    )


@dataclass
class GameStartMessage:
    name_white: Optional[str] = field(
        default=None,
        metadata={
            "name": "nameWhite",
            "type": "Element",
            "namespace": "",
            "required": True,
        }
    )


@dataclass
class HeartBeatMessage:
    pass


class JchessMessageType(Enum):
    ACCEPT = "Accept"
    LOGIN = "Login"
    LOGIN_REPLY = "LoginReply"
    HEART_BEAT = "HeartBeat"
    DISCONNECT = "Disconnect"
    MATCH_FOUND = "MatchFound"
    MATCH_OVER = "MatchOver"
    MATCH_STATUS = "MatchStatus"
    GAME_START = "GameStart"
    GAME_OVER = "GameOver"
    AWAIT_MOVE = "AwaitMove"
    MOVE = "Move"
    REQUEST_DRAW = "RequestDraw"
    DRAW_RESPONSE = "DrawResponse"


@dataclass
class LoginMessage:
    name: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "",
            "required": True,
        }
    )


@dataclass
class LoginReplyMessage:
    new_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "newId",
            "type": "Element",
            "namespace": "",
            "required": True,
            "pattern": r"([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})|(\{[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\})",
        }
    )


@dataclass
class MatchStatusData:
    name_player1: Optional[str] = field(
        default=None,
        metadata={
            "name": "namePlayer1",
            "type": "Element",
            "namespace": "",
            "required": True,
        }
    )
    name_player2: Optional[str] = field(
        default=None,
        metadata={
            "name": "namePlayer2",
            "type": "Element",
            "namespace": "",
            "required": True,
        }
    )
    score_player1: Optional[int] = field(
        default=None,
        metadata={
            "name": "scorePlayer1",
            "type": "Element",
            "namespace": "",
            "required": True,
        }
    )
    score_player2: Optional[int] = field(
        default=None,
        metadata={
            "name": "scorePlayer2",
            "type": "Element",
            "namespace": "",
            "required": True,
        }
    )


@dataclass
class MatchTypeData:
    pass


class MatchTypeValue(Enum):
    WIN_X = "WIN_X"
    SCORE = "SCORE"


@dataclass
class MoveData:
    from_value: Optional[str] = field(
        default=None,
        metadata={
            "name": "from",
            "type": "Element",
            "namespace": "",
            "required": True,
            "pattern": r"[abcdefgh][1-8]",
        }
    )
    to: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "",
            "required": True,
            "pattern": r"[abcdefgh][1-8]",
        }
    )
    promotion_unit: Optional[str] = field(
        default=None,
        metadata={
            "name": "promotionUnit",
            "type": "Element",
            "namespace": "",
            "pattern": r"[nNbBrRqQ]",
        }
    )


class RequestDrawType(Enum):
    OFFER = "OFFER"
    FIFTY_MOVE_RULE = "FIFTY_MOVE_RULE"


@dataclass
class TimeControlData:
    your_time_in_ms: Optional[int] = field(
        default=None,
        metadata={
            "name": "yourTimeInMs",
            "type": "Element",
            "namespace": "",
            "required": True,
        }
    )
    enemy_time_in_ms: Optional[int] = field(
        default=None,
        metadata={
            "name": "enemyTimeInMs",
            "type": "Element",
            "namespace": "",
            "required": True,
        }
    )


@dataclass
class AcceptMessage:
    accept: Optional[bool] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "",
            "required": True,
        }
    )
    error_type_code: Optional[ErrorType] = field(
        default=None,
        metadata={
            "name": "errorTypeCode",
            "type": "Element",
            "namespace": "",
            "required": True,
        }
    )


@dataclass
class AwaitMoveMessage:
    position: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "",
            "required": True,
            "pattern": r"\s*([rnbqkpRNBQKP1-8]+/){7}([rnbqkpRNBQKP1-8]+)\s[bw-]\s(([kqKQ]{1,4})|(-))\s(([a-h][36])|(-))\s\d+\s\d+\s*",
        }
    )
    last_move: Optional[MoveData] = field(
        default=None,
        metadata={
            "name": "lastMove",
            "type": "Element",
            "namespace": "",
        }
    )
    time_control: Optional[TimeControlData] = field(
        default=None,
        metadata={
            "name": "timeControl",
            "type": "Element",
            "namespace": "",
            "required": True,
        }
    )


@dataclass
class DisconnectMessage:
    error_type_code: Optional[ErrorType] = field(
        default=None,
        metadata={
            "name": "errorTypeCode",
            "type": "Element",
            "namespace": "",
            "required": True,
        }
    )


@dataclass
class MatchFormatData:
    match_type_value: Optional[MatchTypeValue] = field(
        default=None,
        metadata={
            "name": "matchTypeValue",
            "type": "Element",
            "namespace": "",
            "required": True,
        }
    )
    match_type_data: Optional[MatchTypeData] = field(
        default=None,
        metadata={
            "name": "matchTypeData",
            "type": "Element",
            "namespace": "",
            "required": True,
        }
    )
    time_per_side: Optional[int] = field(
        default=None,
        metadata={
            "name": "timePerSide",
            "type": "Element",
            "namespace": "",
            "required": True,
        }
    )
    time_per_side_increment: Optional[int] = field(
        default=None,
        metadata={
            "name": "timePerSideIncrement",
            "type": "Element",
            "namespace": "",
            "required": True,
        }
    )
    time_per_side_per_move: Optional[int] = field(
        default=None,
        metadata={
            "name": "timePerSidePerMove",
            "type": "Element",
            "namespace": "",
            "required": True,
        }
    )


@dataclass
class MatchStatusMessage:
    match_status: Optional[MatchStatusData] = field(
        default=None,
        metadata={
            "name": "matchStatus",
            "type": "Element",
            "namespace": "",
            "required": True,
        }
    )


@dataclass
class MatchTypeScore(MatchTypeData):
    amount_to_play: Optional[int] = field(
        default=None,
        metadata={
            "name": "amountToPlay",
            "type": "Element",
            "namespace": "",
            "required": True,
        }
    )
    points_per_win: int = field(
        init=False,
        default=2,
        metadata={
            "name": "pointsPerWin",
            "type": "Element",
            "namespace": "",
            "required": True,
        }
    )
    points_per_draw: int = field(
        init=False,
        default=1,
        metadata={
            "name": "pointsPerDraw",
            "type": "Element",
            "namespace": "",
            "required": True,
        }
    )


@dataclass
class MatchTypeWinX(MatchTypeData):
    amount_to_win: Optional[int] = field(
        default=None,
        metadata={
            "name": "amountToWin",
            "type": "Element",
            "namespace": "",
            "required": True,
        }
    )


@dataclass
class MoveMessage:
    move: Optional[MoveData] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "",
            "required": True,
        }
    )


@dataclass
class RequestDrawMessage:
    reason: Optional[RequestDrawType] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "",
            "required": True,
        }
    )


@dataclass
class MatchFoundMessage:
    match_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "matchId",
            "type": "Element",
            "namespace": "",
            "required": True,
            "pattern": r"([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})|(\{[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\})",
        }
    )
    enemy_name: Optional[str] = field(
        default=None,
        metadata={
            "name": "enemyName",
            "type": "Element",
            "namespace": "",
            "required": True,
        }
    )
    match_format: Optional[MatchFormatData] = field(
        default=None,
        metadata={
            "name": "matchFormat",
            "type": "Element",
            "namespace": "",
            "required": True,
        }
    )


@dataclass
class MatchOverMessage:
    match_status: Optional[MatchStatusData] = field(
        default=None,
        metadata={
            "name": "matchStatus",
            "type": "Element",
            "namespace": "",
            "required": True,
        }
    )
    match_format: Optional[MatchFormatData] = field(
        default=None,
        metadata={
            "name": "matchFormat",
            "type": "Element",
            "namespace": "",
            "required": True,
        }
    )
    statistics: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "",
            "required": True,
        }
    )


@dataclass
class JchessMessage:
    class Meta:
        name = "JChessMessage"

    accept: Optional[AcceptMessage] = field(
        default=None,
        metadata={
            "name": "Accept",
            "type": "Element",
            "namespace": "",
        }
    )
    login: Optional[LoginMessage] = field(
        default=None,
        metadata={
            "name": "Login",
            "type": "Element",
            "namespace": "",
        }
    )
    login_reply: Optional[LoginReplyMessage] = field(
        default=None,
        metadata={
            "name": "LoginReply",
            "type": "Element",
            "namespace": "",
        }
    )
    heart_beat: Optional[HeartBeatMessage] = field(
        default=None,
        metadata={
            "name": "HeartBeat",
            "type": "Element",
            "namespace": "",
        }
    )
    disconnect: Optional[DisconnectMessage] = field(
        default=None,
        metadata={
            "name": "Disconnect",
            "type": "Element",
            "namespace": "",
        }
    )
    match_found: Optional[MatchFoundMessage] = field(
        default=None,
        metadata={
            "name": "MatchFound",
            "type": "Element",
            "namespace": "",
        }
    )
    match_over: Optional[MatchOverMessage] = field(
        default=None,
        metadata={
            "name": "MatchOver",
            "type": "Element",
            "namespace": "",
        }
    )
    match_status: Optional[MatchStatusMessage] = field(
        default=None,
        metadata={
            "name": "MatchStatus",
            "type": "Element",
            "namespace": "",
        }
    )
    game_start: Optional[GameStartMessage] = field(
        default=None,
        metadata={
            "name": "GameStart",
            "type": "Element",
            "namespace": "",
        }
    )
    game_over: Optional[GameOverMessage] = field(
        default=None,
        metadata={
            "name": "GameOver",
            "type": "Element",
            "namespace": "",
        }
    )
    await_move: Optional[AwaitMoveMessage] = field(
        default=None,
        metadata={
            "name": "AwaitMove",
            "type": "Element",
            "namespace": "",
        }
    )
    move: Optional[MoveMessage] = field(
        default=None,
        metadata={
            "name": "Move",
            "type": "Element",
            "namespace": "",
        }
    )
    request_draw: Optional[RequestDrawMessage] = field(
        default=None,
        metadata={
            "name": "RequestDraw",
            "type": "Element",
            "namespace": "",
        }
    )
    draw_response: Optional[DrawResponseMessage] = field(
        default=None,
        metadata={
            "name": "DrawResponse",
            "type": "Element",
            "namespace": "",
        }
    )
    message_type: Optional[JchessMessageType] = field(
        default=None,
        metadata={
            "name": "messageType",
            "type": "Attribute",
            "required": True,
        }
    )
    player_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "playerId",
            "type": "Attribute",
            "required": True,
            "pattern": r"([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})|(\{[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\})",
        }
    )
    schema_version: str = field(
        init=False,
        default="0.1.1",
        metadata={
            "name": "schemaVersion",
            "type": "Attribute",
            "required": True,
        }
    )
