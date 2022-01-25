from abc import ABC, abstractmethod
from typing import Optional, Tuple, Dict
from uuid import UUID

from ..communication.schema import MatchStatusData, MatchFormatData, MoveData
from .Container import GameState


class AI(ABC):

    def __init__(self, name: str = None):
        self._name = f"{self.__class__.__name__}-PyAI" if name is None else name

    @property
    def name(self) -> str:
        return self._name

    def __str__(self):
        return self.name

    @abstractmethod
    def new_match(self, match_id: UUID, enemy: str, match_format: MatchFormatData):
        pass

    @abstractmethod
    def finalize_match(self, match_id: UUID, status: MatchStatusData, statistics: str):
        pass

    @abstractmethod
    def new_game(self, game_id: UUID, match_id: UUID, white_player: str):
        pass

    @abstractmethod
    def finalize_game(self, game_id: UUID, match_id: UUID, winner: Optional[str], pgn: str):
        pass

    @abstractmethod
    def get_move(self, game_id: UUID, match_id: UUID, game_state: GameState) -> MoveData:
        pass


class DumbAI(AI, ABC):

    def new_match(self, match_id: UUID, enemy: str, match_format: MatchFormatData):
        pass

    def finalize_match(self, match_id: UUID, status: MatchStatusData, statistics: str):
        pass

    def new_game(self, game_id: UUID, match_id: UUID, white_player: str):
        pass

    def finalize_game(self, game_id: UUID, match_id: UUID, winner: Optional[str], pgn: str):
        pass


class StoreAI(AI, ABC):

    def __init__(self, name: str = None):
        super().__init__(name)
        self._match_storage: Dict[UUID, Tuple[str, MatchFormatData]] = {}
        self._game_storage: Dict[Tuple[UUID, UUID], str] = {}

    def get_match(self, match_id: UUID) -> Optional[Tuple[str, MatchFormatData]]:
        return self._match_storage.get(match_id, None)

    def get_game(self, game_id: UUID, match_id: UUID) -> Optional[str]:
        return self._game_storage.get((match_id, game_id), None)

    def new_match(self, match_id: UUID, enemy: str, match_format: MatchFormatData):
        self._match_storage[match_id] = (enemy, match_format)

    def finalize_match(self, match_id: UUID, status: MatchStatusData, statistics: str):
        pass

    def new_game(self, game_id: UUID, match_id: UUID, white_player: str):
        self._game_storage[(match_id, game_id)] = white_player

    def finalize_game(self, game_id: UUID, match_id: UUID, winner: Optional[str], pgn: str):
        pass
