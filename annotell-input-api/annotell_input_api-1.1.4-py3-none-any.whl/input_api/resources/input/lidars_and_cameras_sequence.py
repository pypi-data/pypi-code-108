import logging
from typing import Optional, List

import annotell.input_api.model.input as InputModel
from annotell.input_api.resources.abstract import CreateableInputAPIResource

log = logging.getLogger(__name__)


class LidarsAndCamerasSequence(CreateableInputAPIResource):

    path = 'lidars-and-cameras-sequence'

    def create(
        self,
        lidars_and_cameras_sequence: InputModel.LidarsAndCamerasSequence,
        project: Optional[str] = None,
        batch: Optional[str] = None,
        annotation_types: Optional[List[str]] = None,
        dryrun: bool = False
    ) -> Optional[InputModel.CreateInputResponse]:
        """
        Upload files and create an input of type ``LidarsAndCamerasSequence``.

        :param lidars_and_cameras_sequence: class containing 2D and 3D resources that constitute the input
        :param project: project to add input to
        :param batch: batch, defaults to latest open batch
        :param annotation_types: annotation types for which to produce annotations for. Defaults to `None` (corresponds to all available annotation types). Passing an empty list will result in the same behaviour as passing `None`.
        :param dryrun: If True the files/metadata will be validated but no input job will be created.
        :returns InputJobCreated: Class containing id of the created input job, or `None` if dryrun.
        """

        imu_data = lidars_and_cameras_sequence.imu_data
        payload = lidars_and_cameras_sequence.to_dict()

        response = self._post_input_request(
            self.path, payload, project=project, batch=batch, annotation_types=annotation_types, imu_data=imu_data, dryrun=dryrun
        )

        if dryrun:
            return None

        log.info(f"Created inputs for files with uuid={response.input_uuid}")
        return InputModel.CreateInputResponse.from_input_job_response(response)
