import io
import json
import logging
from typing import Dict, List, Optional, Tuple

import annotell.input_api.model as IAM
from annotell.input_api.cloud_storage import FileResourceClient
from annotell.input_api.http_client import HttpClient
from annotell.input_api.model import IMUData
from annotell.input_api.model.ego.validated_imu_data import ValidatedIMUData, ValidateIMUDataRequest
from annotell.input_api.model.input.initialized_input import InitializedInput

log = logging.getLogger(__name__)

INPUTS_ROUTE = "v1/inputs"


class CreateableInputAPIResource:

    def __init__(self, client: HttpClient, file_resource_client: FileResourceClient):
        super().__init__()
        self._client = client
        self._file_resource_client = file_resource_client

    def _post_input_request(
        self,
        resource_path: str,
        body: dict,
        project: Optional[str],
        batch: Optional[str],
        annotation_types: Optional[List[str]] = None,
        imu_data: Optional[List[IMUData]] = None,
        dryrun: bool = False
    ) -> Optional[IAM.InputJobCreated]:
        """
        Send input to Input API. if dryrun is true, only validation is performed
        Otherwise, returns `InputJobCreated`
        """

        body, initialized_input = self._get_input_uuid(body)

        body, validated_imu_data = self._validate_imu_data(body, imu_data, initialized_input.internal_id, dryrun)

        body = self._append_annotation_types(body, annotation_types)

        input_job_json = self._validate_and_create_scene(
            resource_path=resource_path, body=body, project=project, batch=batch, dryrun=dryrun
        )

        if not dryrun:

            response = IAM.InputJobCreated.from_json(input_job_json)

            local_files_uploaded = self._upload_local_files(response)

            local_files_uploaded += self._upload_imu_data(validated_imu_data)

            if local_files_uploaded:
                self._client.post(f"{INPUTS_ROUTE}/{response.input_uuid}/actions/commit", discard_response=True)

            return response

    def _get_input_uuid(self, body: Dict) -> Tuple[Dict, InitializedInput]:
        json_resp = self._client.post(INPUTS_ROUTE + "/initialize")

        init_input = InitializedInput.from_json(json_resp)
        body["internalId"] = init_input.internal_id

        return body, init_input

    def _validate_imu_data(self, body: Dict, imu_data: Optional[List[IMUData]], input_uuid: str,
                           dryrun: bool) -> Tuple[Dict, Optional[ValidatedIMUData]]:
        if imu_data is None or len(imu_data) == 0:
            return body, None

        imu_request = ValidateIMUDataRequest(imu_data=imu_data, internal_id=input_uuid)
        json_resp = self._client.post(f"v1/imu", json=imu_request.to_dict(), dryrun=dryrun)

        valid_imu_data = None
        if json_resp is not None and not dryrun:
            json_resp["imuData"] = imu_data
            valid_imu_data = ValidatedIMUData.from_json(json_resp)
            body["imuData"] = valid_imu_data.resource_id

        return body, valid_imu_data

    def _append_annotation_types(self, body: Dict, annotation_types: Optional[List[str]]) -> Dict:
        if annotation_types:
            body['annotationTypes'] = annotation_types
        return body

    def _validate_and_create_scene(
        self, *, resource_path: str, body: dict, project: Optional[str], batch: Optional[str], dryrun: bool = False
    ) -> Optional[Dict]:

        log.debug("POST:ing to %s input %s", resource_path, body)
        request_url = self._resolve_request_url(resource_path, project, batch)
        return self._client.post(request_url, json=body, dryrun=dryrun)

    def _upload_local_files(self, response: IAM.InputJobCreated) -> bool:
        if len(response.files) > 0:
            self._file_resource_client.upload_files(response.files)
            return True
        return False

    def _upload_imu_data(self, validated_imu_data: Optional[ValidatedIMUData]) -> bool:
        if validated_imu_data is not None and validated_imu_data.signed_url is not None:
            file = io.BytesIO(json.dumps(validated_imu_data.serialize_imu_data()).encode("utf-8"))
            self._file_resource_client.upload_json(file, validated_imu_data.signed_url)
            return True
        return False

    @staticmethod
    def _resolve_request_url(resource_path: str, project: Optional[str] = None, batch: Optional[str] = None) -> str:
        """
        Resolves which request url to use for input based on if project and batch is specified
        """
        url = INPUTS_ROUTE + "/"

        if project is not None:
            url += f"project/{project}/"
            if batch is not None:
                url += f"batch/{batch}/"

        url += resource_path

        return url
