import os
import subprocess
import pwd
from datetime import datetime
from pathlib import Path
from marshmallow import Schema
from typing import List, Optional

from edr_agent_validator.activity import Activity, ActivityType

import desert


schema: Schema = desert.schema(Activity)


def start_process(executable: Path, args: Optional[List[str]]) -> Activity:
    args = [] if not args else args
    proc: subprocess.Popen = subprocess.Popen([executable, *args])
    return Activity(
        datetime.utcnow(),
        pwd.getpwuid(os.getuid()).pw_name,
        executable.name,
        [str(executable), *args],
        proc.pid,
        ActivityType.PROCESS_LAUNCH,
    )
