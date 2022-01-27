from pathlib import Path
from typing import List


class Deployment:
    def __init__(
        self,
        project: str,
        code_path: Path,
        version: str,
        secret_names: List[str],
    ):
        self.project = project
        self.code_path = code_path
        self.version = version
        self.secret_names = secret_names
