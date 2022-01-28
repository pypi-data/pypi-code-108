"""Main object for RedBrick SDK."""
from typing import Dict

import tenacity

from redbrick_slicer.common.context import RBContext


class RBProject:
    """
    Interact with a RedBrick project.

    Attributes
    -----------
    export: redbrick_slicer.export.Export
        Interface for managing exporting data and
        labels from your redbrick_slicer ai projects.

    labeling: redbrick_slicer.labeling.Labeling
        Interface for programmatically labeling your
        redbrick_slicer ai tasks.
    """

    def __init__(self, context: RBContext, org_id: str, project_id: str) -> None:
        """Construct RBProject."""
        # pylint: disable=import-outside-toplevel
        from redbrick_slicer.labeling import Labeling
        from redbrick_slicer.export import Export

        self.context = context

        self._org_id = org_id
        self._project_id = project_id
        self._project_name: str
        self._td_type: str
        self._taxonomy_name: str
        self._project_url: str

        # check if project exists on backend to validate
        self._get_project()

        self.labeling = Labeling(context, org_id, project_id)
        self.export = Export(context, org_id, project_id)

    @property
    def org_id(self) -> str:
        """
        Read only property.

        Retrieves the unique Organization UUID that this project belongs to
        """
        return self._org_id

    @property
    def project_id(self) -> str:
        """
        Read only property.

        Retrieves the unique Project ID UUID.
        """
        return self._project_id

    @property
    def name(self) -> str:
        """
        Read only name property.

        Retrieves the project name.
        """
        return self._project_name

    @property
    def url(self) -> str:
        """
        Read only property.

        Retrieves the project URL.
        """
        return self._project_url

    @property
    def taxonomy_name(self) -> str:
        """
        Read only taxonomy_name property.

        Retrieves the taxonomy name.
        """
        return self._taxonomy_name

    def __wait_for_project_to_finish_creating(self) -> Dict:
        try:
            for attempt in tenacity.Retrying(
                reraise=True,
                stop=tenacity.stop_after_attempt(10),
                wait=tenacity.wait_exponential(multiplier=1, min=1, max=10),
                retry=tenacity.retry_if_not_exception_type(
                    (KeyboardInterrupt, PermissionError, ValueError)
                ),
            ):
                with attempt:
                    project = self.context.project.get_project(
                        self.org_id, self.project_id
                    )
                    if project["status"] == "CREATING":
                        if attempt.retry_state.attempt_number == 1:
                            print("Project is still creating...")
                        raise Exception("Unknown problem occurred")
        except tenacity.RetryError as error:
            raise Exception("Unknown problem occurred") from error

        if project["status"] == "REMOVING":
            raise Exception("Project has been deleted")
        if project["status"] == "CREATION_FAILURE":
            raise Exception("Project failed to be created")
        if project["status"] == "CREATION_SUCCESS":
            return project
        raise Exception("Unknown problem occurred")

    def _get_project(self) -> None:
        """Get project to confirm it exists."""
        project = self.__wait_for_project_to_finish_creating()

        self._project_name = project["name"]
        self._td_type = project["tdType"]
        self._taxonomy_name = project["taxonomy"]["name"]
        self._project_url = project["projectUrl"]

    def __str__(self) -> str:
        """Get string representation of RBProject object."""
        return f"RedBrick Project - {self.name} - id:( {self.project_id} )"

    def __repr__(self) -> str:
        """Representation of object."""
        return str(self)
