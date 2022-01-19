import time
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class Event:
    timestamp: float = field(
        default_factory=time.time,
        init=False,
        compare=False,
    )
