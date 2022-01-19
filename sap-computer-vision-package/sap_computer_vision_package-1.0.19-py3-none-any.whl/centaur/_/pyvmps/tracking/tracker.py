from typing import Dict, List, Optional
from centaur._.pyvmps.cfg.config import EnvVarGoPyCommon
from centaur._.pyvmps.tracking.constants import Tracking
from centaur._.pyvmps.utils.common import current_milli_time
from centaur._.pyvmps.logger.get_logger import get_logger

_logger = get_logger(__file__)


class _Tracker:
    def __init__(self):
        self.map: Dict[str, List[int]] = {}

    def create_entry(self, msg_id: str):
        _logger.debug("create_entry,msg_id=%s", msg_id)
        self.map[msg_id] = [0 for i in range(len(Tracking))]

    def insert_anchor(self, msg_id: str, anchor: int, timestamp: Optional[int] = None):
        if not EnvVarGoPyCommon.ENABLE_HTTP_DEBUG:
            return
        _logger.debug("insert_anchor,msg_id=%s,anchor=%s", msg_id, anchor)
        try:
            t: int = timestamp if timestamp else current_milli_time()
            self.map[msg_id][anchor] = t
        except Exception:
            _logger.exception("error inserting anchor")
            _logger.debug("type=%s", type(msg_id))
            _logger.debug(self.map)

    def pop_entry(self, msg_id: str):
        _logger.debug("pop_entry,msg_id=%s", msg_id)
        if msg_id in self.map:
            self.map.pop(msg_id)

    def get_anchors(self, msg_id: str) -> List[int]:
        try:
            return self.map[msg_id]
        except KeyError:
            _logger.debug("no anchor found")
            return []


tracker = _Tracker()
