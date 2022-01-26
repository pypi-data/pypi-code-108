from dataclasses import dataclass

from .artifact import _Base
from .git_version import GitVersion


@dataclass
class __CodeData:
    gitVersion: GitVersion
    """
    git information structure extracted automatically by the SDK.
    """


@dataclass
class CodeVersion(_Base, __CodeData):
    def __post_init__(self):
        self.parentName = self.gitVersion.repositoryName
