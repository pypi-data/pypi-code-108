from cnvrgv2.modules.workflows.webapp.webapp import WebappType
from cnvrgv2.config.error_messages import NOT_A_DATASET_LIST_OBJECT, FAULTY_VALUE
from cnvrgv2.context import SCOPE
from cnvrgv2.config import routes
from cnvrgv2.errors import CnvrgArgumentsError

from cnvrgv2.modules.base.workflows_base import WorkflowsBase
from cnvrgv2.modules.dataset import Dataset
from cnvrgv2.modules.workflows import Webapp
from cnvrgv2.utils.validators import validate_types_in_list


class WebappsClient(WorkflowsBase):
    def __init__(self, project):
        super().__init__(Webapp, "Webapp", project._context)

        scope = self._context.get_scope(SCOPE.PROJECT)
        self._route = routes.WEBAPPS_BASE.format(scope["organization"], scope["project"])

    def create(self, webapp_type, file_name, title=None, templates=None, datasets=None, *args, **kwargs):
        """
        Create a new webapp
        @param webapp_type: The type of webapp to create (shiny, dash or voila)
        @param file_name: The file for webapp creating
        @param title: Name of the webapp
        @param templates: List of template names to be used
        @param datasets: List of datasets to connect with the webapp.
        @param args: optional arguments
        @param kwargs: Dictionary. Rest of optional attributes for creation
            image: Image object to create webapp with
            queue: Name of the queue to run this job on
        TODO: Add a list of optional attributes
        @return: The newly created webapp object
        """

        if webapp_type not in [WebappType.SHINY, WebappType.DASH, WebappType.VOILA]:
            raise CnvrgArgumentsError(FAULTY_VALUE.format(webapp_type))

        kwargs = {
            "webapp_type": webapp_type,
            "file_name": file_name,
            **kwargs
        }

        if datasets and not validate_types_in_list(datasets, Dataset):
            raise CnvrgArgumentsError(NOT_A_DATASET_LIST_OBJECT)
        elif datasets:
            kwargs["job_datasets"] = [ds.as_request_params() for ds in datasets]

        return super().create(title, templates, *args, **kwargs)
