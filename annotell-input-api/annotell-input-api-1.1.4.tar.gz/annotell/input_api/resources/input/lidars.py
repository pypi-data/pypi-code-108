import logging
from typing import Optional, List

import annotell.input_api.model.input.lidars as model
from annotell.input_api.model.input import CreateInputResponse
from annotell.input_api.resources.abstract import CreateableInputAPIResource

log = logging.getLogger(__name__)


class Lidars(CreateableInputAPIResource):
    path = 'lidars'

    def create(
        self,
        lidars: model.Lidars,
        project: Optional[str] = None,
        batch: Optional[str] = None,
        annotation_types: Optional[List[str]] = None,
        dryrun: bool = False
    ) -> Optional[CreateInputResponse]:
        """
        Upload files and create an input of type ``Lidars``.

        :param lidars: class containing 3D resources that constitute the input
        :param project: project to add input to
        :param batch: batch, defaults to latest open batch
        :param annotation_types: annotation types for which to produce annotations for. Defaults to `None` (corresponds to all available annotation types). Passing an empty list will result in the same behaviour as passing `None`.
        :param dryrun: If True the files/metadata will be validated but no input job will be created.
        :returns CreateInputResponse: Class containing id of the created input job, or `None` if dryrun.
        """

        imu_data = lidars.imu_data
        payload = lidars.to_dict()

        response = self._post_input_request(
            self.path, payload, project=project, batch=batch, annotation_types=annotation_types, imu_data=imu_data, dryrun=dryrun
        )

        if dryrun:
            return None

        log.info(f"Created inputs for files with uuid={response.input_uuid}")
        return CreateInputResponse.from_input_job_response(response)
