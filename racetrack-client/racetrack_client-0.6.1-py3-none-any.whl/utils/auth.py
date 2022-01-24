from enum import Enum
from typing import Dict

RT_USER_AUTH_HEADER = "X-Racetrack-User-Auth"
RT_INTERNAL_AUTH_HEADER = "X-Racetrack-Internal-Auth"
RT_FATMAN_AUTH_HEADER = "X-Racetrack-Fatman-Auth"
RT_ESC_AUTH_HEADER = 'X-Racetrack-Esc-Auth'

RT_SESSION_USER_AUTH_KEY = 'RACETRACK_SESSION_USER_AUTH'


class RacetrackAuthMethod(Enum):
    USER = 'racetrackUserAuth'
    INTERNAL = 'racetrackInternalAuth'
    FATMAN = 'racetrackFatmanAuth'
    ESC = 'racetrackESCAuth'


def get_auth_request_headers(user_auth: str) -> Dict:
    return {
        RT_USER_AUTH_HEADER: user_auth if user_auth != "" else None
    }
