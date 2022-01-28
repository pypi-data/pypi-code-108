"""Client for communicating with the Annotell platform."""
import logging

from annotell.auth.authsession import DEFAULT_HOST as DEFAULT_AUTH_HOST

from annotell.input_api.cloud_storage import FileResourceClient
from annotell.input_api.http_client import HttpClient
from annotell.input_api.resources.annotation.annotation import AnnotationResource
from annotell.input_api.resources.calibration.calibration import CalibrationResource
from annotell.input_api.resources.input.cameras import Cameras
from annotell.input_api.resources.input.cameras_sequence import CamerasSequence
from annotell.input_api.resources.input.input import InputResource
from annotell.input_api.resources.input.lidars_and_cameras import LidarsAndCameras
from annotell.input_api.resources.input.lidars_and_cameras_sequence import LidarsAndCamerasSequence
from annotell.input_api.resources.input.lidars import Lidars
from annotell.input_api.resources.input.lidars_sequence import LidarsSequence
from annotell.input_api.resources.project.project import ProjectResource

DEFAULT_HOST = "https://input.annotell.com"

log = logging.getLogger(__name__)


class InputApiClient:
    """Creates Annotell inputs from local files."""

    def __init__(
        self,
        *,
        auth=None,
        host: str = DEFAULT_HOST,
        auth_host: str = DEFAULT_AUTH_HOST,
        client_organization_id: int = None,
        max_retry_attempts: int = 23,
        max_retry_wait_time: int = 60,
        timeout: int = 60
    ):
        """
        :param auth: auth credentials, see https://github.com/annotell/annotell-python/tree/master/annotell-auth
        :param host: override for input api url
        :param auth_host: override for authentication url
        :param client_organization_id: Overrides your users organization id. Only works with an Annotell user.
        :param max_upload_retry_attempts: Max number of attempts to retry uploading a file to GCS.
        :param max_upload_retry_wait_time:  Max with time before retrying an upload to GCS.
        """

        self._client = HttpClient(auth=auth, host=host, auth_host=auth_host, client_organization_id=client_organization_id, timeout=timeout)
        self._file_client = FileResourceClient(
            max_retry_attempts=max_retry_attempts, max_retry_wait_time=max_retry_wait_time, timeout=timeout
        )

        self.calibration = CalibrationResource(self._client, self._file_client)
        self.project = ProjectResource(self._client, self._file_client)
        self.annotation = AnnotationResource(self._client, self._file_client)
        self.input = InputResource(self._client, self._file_client)

        self.lidar_and_cameras = LidarsAndCameras(self._client, self._file_client)
        self.lidars_and_cameras_sequence = LidarsAndCamerasSequence(self._client, self._file_client)
        self.cameras = Cameras(self._client, self._file_client)
        self.cameras_sequence = CamerasSequence(self._client, self._file_client)
        self.lidars = Lidars(self._client, self._file_client)
        self.lidars_sequence = LidarsSequence(self._client, self._file_client)
