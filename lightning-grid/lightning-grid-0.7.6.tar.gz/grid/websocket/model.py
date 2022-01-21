from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Dict


@dataclass
class ClusterLogsRequest:
    cluster_id: str
    follow: bool
    start: int  # unix timestamp
    end: int  # unix timestamp
    limit: int

    def as_dict(self) -> Dict:
        params = asdict(self)
        # type of the value must be string for downstream url
        # preparation (PreparedRequest().prepare_url()) to work
        params['follow'] = "true" if params.get("follow") else "false"
        return params


@dataclass
class ClusterLogsResponse:
    message: str
    timestamp: datetime
    level: str
    labels: Dict[str, str]

    def as_dict(self) -> Dict:
        return asdict(self)
