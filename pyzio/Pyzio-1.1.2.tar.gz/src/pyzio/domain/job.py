from dataclasses import dataclass


@dataclass
class Job:
    sequence_number: int
    part_id: str
    job_id: str
    filename: str
    cluster_id: str
    team_id: str
    printFile: str
