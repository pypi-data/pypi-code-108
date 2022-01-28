import logging
from typing import Optional, List

import annotell.input_api.model.input as InputModel
from annotell.input_api.resources.abstract import CreateableInputAPIResource

log = logging.getLogger(__name__)


class Cameras(CreateableInputAPIResource):
    path = 'cameras'

    def create(
        self,
        cameras: InputModel.Cameras,
        project: Optional[str] = None,
        batch: Optional[str] = None,
        annotation_types: Optional[List[str]] = None,
        dryrun: bool = False
    ) -> Optional[InputModel.CreateInputResponse]:
        """
        Upload files and create an input of type ``cameras``.

        :param cameras: class containing 2D resources that constitute the input
        :param project: project to add input to
        :param batch: batch, defaults to latest open batch
        :param annotation_types: annotation types for which to produce annotations for. Defaults to `None` (corresponds to all available annotation types). Passing an empty list will result in the same behaviour as passing `None`.
        :param dryrun: If True the files/metadata will be validated but no input job will be created.
        :returns InputJobCreated: Class containing id of the created input job, or `None` if dryrun.
        """

        payload = cameras.to_dict()

        response = self._post_input_request(
            self.path, payload, project=project, batch=batch, annotation_types=annotation_types, dryrun=dryrun
        )

        if dryrun:
            return None

        log.info(f"Created inputs for files with uuid={response.input_uuid}")
        return InputModel.CreateInputResponse.from_input_job_response(response)
