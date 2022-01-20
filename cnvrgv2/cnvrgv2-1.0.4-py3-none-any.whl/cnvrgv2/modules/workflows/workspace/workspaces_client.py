from cnvrgv2.config.error_messages import NOT_A_VOLUME_OBJECT, NOT_A_DATASET_LIST_OBJECT
from cnvrgv2.context import SCOPE
from cnvrgv2.config import routes
from cnvrgv2.errors import CnvrgArgumentsError

from cnvrgv2.modules.base.workflows_base import WorkflowsBase
from cnvrgv2.modules.dataset import Dataset
from cnvrgv2.modules.volumes.volume import Volume
from cnvrgv2.modules.workflows import Workspace, NotebookType
from cnvrgv2.utils.validators import validate_types_in_list


class WorkspacesClient(WorkflowsBase):
    def __init__(self, project):
        super().__init__(Workspace, "NotebookSession", project._context)

        scope = self._context.get_scope(SCOPE.PROJECT)
        self._route = routes.WORKSPACES_BASE.format(scope["organization"], scope["project"], "workspaces")

    def create(
            self,
            title=None,
            templates=None,
            notebook_type=NotebookType.JUPYTER_LAB,
            volume=None,
            datasets=None,
            *args,
            **kwargs):
        """
        Creates a new workspace with the given name
        @param title: Name of the workflow
        @param templates: List of template names to be used
        @param notebook_type: The type of the created notebook. Use NotebookType enum
        @param volume: A volume to attach to this workspace. (type: Volume object).
        @param datasets: List of datasets to connect with the workspace.
        @param kwargs: rest of optional attributes for creation
            image: Image object to create workspace with
            queue: Name of the queue to run this job on
        TODO: Add a list of optional attributes
        @return: The newly created workflow object
        """
        kwargs = {
            "notebook_type": notebook_type,
            **kwargs
        }

        if datasets and not validate_types_in_list(datasets, Dataset):
            raise CnvrgArgumentsError(NOT_A_DATASET_LIST_OBJECT)
        elif datasets:
            kwargs["job_datasets"] = [ds.as_request_params() for ds in datasets]

        if volume and not isinstance(volume, Volume):
            raise CnvrgArgumentsError(NOT_A_VOLUME_OBJECT)
        elif volume:
            kwargs["external_disk_slug"] = volume.slug

        return super().create(title, templates, *args, **kwargs)
