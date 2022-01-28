"""Interface for getting basic information about a project."""
from typing import Dict
from abc import ABC, abstractmethod


class ProjectRepoInterface(ABC):
    """Abstract interface to Project APIs."""

    @abstractmethod
    def get_project(self, org_id: str, project_id: str) -> Dict:
        """
        Get project name and status.

        Raise an exception if project does not exist.
        """
