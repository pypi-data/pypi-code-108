"""Client for communicating with the Annotell platform."""
import logging
from typing import List, Optional

import annotell.input_api.model.calibration as CalibrationModel
from annotell.input_api.resources.abstract import InputAPIResource

log = logging.getLogger(__name__)


class CalibrationResource(InputAPIResource):

    def get_calibration(self, id: str) -> CalibrationModel.SensorCalibrationEntry:  # pylint: disable=redefined-builtin
        """
        Queries the Input API for a specific calibration for the given id

        :param id: The id of the calibration to get
        :return CalibrationModel.SensorCalibrationEntry: The calibration entry
        """

        json_resp = self._client.get('v1/calibrations', params={"id": id})
        return CalibrationModel.SensorCalibrationEntry.from_json(js=json_resp)

    def get_calibrations(self, external_id: Optional[str] = None) -> List[CalibrationModel.SensorCalibrationEntry]:
        """
        Queries the Input API for a list of calibrations available, filtered on external_id
        if provided.

        :param external_id: The external_id to filter on.
        :return List[CalibrationModel.SensorCalibrationEntry]: A list of calibration entries
        """

        json_resp = self._client.get('v1/calibrations', params={"externalId": external_id})

        return [CalibrationModel.SensorCalibrationEntry.from_json(js) for js in json_resp] if isinstance(json_resp, list) \
            else [CalibrationModel.SensorCalibrationEntry.from_json(json_resp)]

    def create_calibration(self, sensor_calibration: CalibrationModel.SensorCalibration) -> CalibrationModel.SensorCalibrationEntry:
        """
        Creates a new calibration, given the SensorCalibration
        :param sensor_calibration: A SensorCalibration instance containing everything to create a calibration.
        :return SensorCalibrationEntry: Class containing the calibration id, external id and time of creation.
        """
        json_resp = self._client.post("v1/calibrations", json=sensor_calibration.to_dict())
        return CalibrationModel.SensorCalibrationEntry.from_json(json_resp)
