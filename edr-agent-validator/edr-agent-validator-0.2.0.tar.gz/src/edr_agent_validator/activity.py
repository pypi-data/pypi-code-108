from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List


class ActivityType(Enum):
    PROCESS_LAUNCH = "PROCESS_LAUNCH"
    CREATE_FILE = "CREATE_FILE"
    MODIFY_FILE = "MODIFY_FILE"
    DELETE_FILE = "DELETE_FILE"
    NETWORK_ACTIVITY = "NETWORK_ACTIVITY"


@dataclass
class Activity:
    timestamp: datetime
    username: str
    process_name: str
    process_cmd_line: List[str]
    process_id: int
    activity_type: ActivityType
