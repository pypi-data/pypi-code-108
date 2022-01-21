from dataclasses import dataclass, field
from enum import Enum
import json
import logging
import math
import os
from pathlib import Path
import shutil
from threading import Lock
from typing import Dict, List, Optional
import uuid

from click import ClickException
from dataclasses_json import dataclass_json
import requests
import yaspin

from grid.openapi import Body2, Body3, DatastoreServiceApi, V1CompletePresignedUrlUpload
from grid.sdk._gql.queries import create_datastore
from grid.sdk.client import create_swagger_client
from grid.sdk import env
from grid.sdk.utils.tar import get_split_size, tar_path
from grid.sdk.utils.uploader import S3Uploader, UploadProgressCallback
from grid.sdk.rest import GridRestClient

SUPPORTED_FILE_EXTENSIONS = [".zip", ".tar", ".tar.gz"]


def clear_cache():
    session_path = Path.home().joinpath(DatastoreUploadSession.grid_datastores_path)
    if session_path.exists():
        shutil.rmtree(str(session_path))


def find_supported_extension(path_or_url: str) -> Optional[str]:
    """Returns the supported extension if exists"""
    for extension in SUPPORTED_FILE_EXTENSIONS:
        if path_or_url.endswith(extension):
            return extension

    return None


def check_source(source: str):
    """
    Check if the source is a valid source for datastore
    """
    if source.startswith("s3://"):
        return

    if source.startswith("http"):
        if not find_supported_extension(source):
            raise ClickException(
                f"""
                Grid currently only supports remote files with the
                following extensions: {SUPPORTED_FILE_EXTENSIONS}
                """
            )

        # Check if url is accessible
        status = requests.head(source, allow_redirects=True)
        if status.status_code != 200:
            raise ClickException(f"Source url {source} is not reachable")
        return

    source_path = Path(source)
    if source_path.exists() is False:
        raise ClickException(f"Source local path {source} doesn't exist")

    if source_path.is_file():
        if not find_supported_extension(source):
            raise ClickException(
                f"""
                Grid currently only supports local file upload with the
                following extensions: {SUPPORTED_FILE_EXTENSIONS}
                """
            )
        return

    if not source_path.is_dir():
        raise ClickException(
            f"""
             Grid currently only supports local sources that are either
             a compressed file or directory.
        """
        )


def create_datastore_session(name: str, source: str, compression: bool, cluster: Optional[str] = None):
    """Creates datastore session based on source"""
    check_source(source)
    if cluster is None:
        if env.CONTEXT is None:
            raise RuntimeError(
                "Cluster not found! Try logging in again. If the problem persist, "
                "reach out to support@grid.ai"
            )
        cluster = env.CONTEXT
    if source.startswith("http") or source.startswith("s3://"):
        return DatastoreRemoteUpload(name=name, source_url=source, cluster=cluster)

    s = DatastoreUploadSession(name=name, source_dir=source, compression=compression, cluster_id=cluster)
    s.configure()
    return s


class InvalidDatastoreError(Exception):
    """Error that is non-recoverable when uploading datastore"""


class UnsupportedDatastoreImplementationError(Exception):
    """Error when trying to recover a non-supported datastore implementation"""


class DatastoreUploadSteps(str, Enum):
    CREATE_DATASTORE = "create_datastore"
    GET_PRESIGNED_URLS = "get_presigned_urls"
    COMPRESS_SOURCE_DIRECTORY = "compress_source_directory"
    UPLOAD_PARTS = "upload_parts"
    MARK_UPLOAD_COMPLETE = "mark_upload_complete"


def create_datastore_api_client() -> DatastoreServiceApi:
    return GridRestClient(api_client=create_swagger_client())


class DatastoreRemoteUpload:
    """
    This class handles creating a datastore in Grid.

    Attributes
    ----------
    name: str
        Name of the datastore
    source_url: str
        Source data url
    """
    def __init__(self, name: str, source_url: str, cluster: Optional[str] = None):
        self.name = name
        self.source_url = source_url
        self.logger = logging.getLogger("grid.sdk.utils.datastore_uploader")
        self.cluster = cluster

    def upload(self):
        spinner = yaspin.yaspin(text=f'Creating datastore {self.name}', color="yellow")
        spinner.start()

        try:
            create_datastore(
                name=self.name,
                source=self.source_url,
                cluster=self.cluster,
            )
        except Exception as e:
            spinner.text = "Failed to create datastore"
            spinner.fail("✘")
            raise e

        spinner.text = "Finished creating datastore"
        spinner.ok("✔")


@dataclass_json
@dataclass
class DatastoreUploadSession(UploadProgressCallback):
    """This class handles uploading datastore

    Attributes
    ----------
    name: str
        Name of the datastore
    source_dir: str
        Source directory to upload from
    presigned_urls: Dict[int, str]
        Presigned urls retrieved from backend
    etags: Dict[int, str]
        Etags per part after uploading to cloud
    session_path: str
        Path to session files (data and state file)
    session_state_file: str
        Path to session state file
    """
    # This version is a datastore implementation version. If we change this
    # version means we no longer able to recover sessions that is not the same
    # version. This is assuming to be fine as datastore upload recovering
    # should be a optimization.
    DATASTORE_VERSION = 2
    # Path storing datastore session and compressed data
    grid_datastores_path = '.grid/datastores'

    # Datastore upload fields
    name: str
    source_dir: str

    version: int = 1
    id: str = ""
    upload_id: str = ""
    original_size: int = 0
    compressed_size: int = 0
    part_count: int = 0

    # Session state
    session_id: str = ""
    session_path: str = ""
    session_state_file: str = ""
    last_completed_step: DatastoreUploadSteps = None

    presigned_urls: Dict[int, str] = field(default_factory=dict)
    etags: Dict[int, str] = field(default_factory=dict)

    # Compression
    compression: bool = False

    cluster_id: Optional[str] = None

    def configure(self):
        self.lock = Lock()
        self.logger = logging.getLogger("uploader.DatastoreUploadSession")
        self.spinner = None

    @staticmethod
    def recover_sessions() -> List['DatastoreUploadSession']:
        """Recover all upload sessions that wasn't completed, so user can resume them.

        Returns
        -------
        List[DatastoreUploadSession]
            List of resumable sessions
        """
        logger = logging.getLogger("DatastoreUploadSession")
        sessions = []
        session_path = str(Path.home().joinpath(DatastoreUploadSession.grid_datastores_path))
        session_dirs = os.listdir(session_path)
        for session_dir in session_dirs:
            session_dir = os.path.join(session_path, session_dir)
            try:
                session = DatastoreUploadSession.recover(session_dir)
                last_completed_step = session.last_completed_step
                if last_completed_step in [None, DatastoreUploadSteps.COMPRESS_SOURCE_DIRECTORY]:
                    # We choose not to resume sessions that hasn't finished getting
                    # presigned_urls, since the datastore version is only determined
                    # when that's called, and we don't know what version we're going
                    # to be resuming.
                    raise ValueError("Session not yet finished compression")

                sessions.append(session)
            except (ValueError, UnsupportedDatastoreImplementationError) as e:
                logger.warning(f"Removing incomplete session {session_dir}, reason: {e}")
                shutil.rmtree(session_dir, ignore_errors=True)

        return sessions

    @staticmethod
    def recover(session_dir: str) -> "DatastoreUploadSession":
        """Recover session if sessions exists
        """
        session_state_file = os.path.join(session_dir, "session.json")
        if not os.path.exists(session_state_file):
            raise ValueError("Session state file does not exist")

        with open(session_state_file, "r") as f:
            content = json.load(f)
            datastore_version = 0
            if "DATASTORE_VERSION" in content:
                datastore_version = content["DATASTORE_VERSION"]
            if datastore_version != DatastoreUploadSession.DATASTORE_VERSION:
                name = content["name"]
                version = content["version"]
                session_name = f"{name}-v{version}"
                raise UnsupportedDatastoreImplementationError(
                    f"Incomplete datastore session {session_name} is no " +
                    "longer supported. Please restart this upload."
                )

            session = DatastoreUploadSession.from_dict(content)

        return session

    def _update_progress(self, text: str):
        """Update current progress

        Parameters
        ----------
        text: str
            Latest progress text
        """
        if self.spinner:
            self.spinner.text = text

    def _get_presigned_urls(self):
        """Gets presigned urls from backend
        """
        if self.part_count <= 0:
            raise InvalidDatastoreError(f"Invalid part count calculated for datastore: {self.part_count}")

        self._update_progress("Requesting presigned URLs from Grid...")

        object_key = f"datastores/{self.id}/data/{self.uploaded_target_file}"

        api_client = create_datastore_api_client()
        response = api_client.datastore_service_create_datastore_presigned_urls(
            cluster_id=self.cluster_id, datastore_id=self.id, body=Body2(count=self.part_count, object_key=object_key)
        )

        self.upload_id = response.upload_id
        presigned_map = {}
        for url in response.urls:
            presigned_map[int(url.part_number)] = url.url

        self.presigned_urls = presigned_map

    @property
    def target_file(self) -> str:
        """Get target compressed data file"""
        source_path = Path(self.source_dir)
        if source_path.is_dir():
            return os.path.join(self.session_path, "data.tar.gz")
        else:
            return self.source_dir

    @property
    def uploaded_target_file(self) -> str:
        """The target file name we will upload into S3"""
        source_path = Path(self.source_dir)
        if source_path.is_dir():
            # Since we're compressing the directory ourselves, we know the file name is ending with .tar.gz
            return "data.tar.gz"
        else:
            extension = find_supported_extension(self.source_dir)
            return f"data{extension}"

    def _create_datastore(self):
        self._update_progress("Creating datastore in Grid...")
        datastore_data = create_datastore(name=self.name, source=self.uploaded_target_file, cluster=self.cluster_id)
        self.id = datastore_data['datastoreId']
        self.version = datastore_data['datastoreVersion']

    def _compress_source(self):
        source_path = Path(self.source_dir)
        if source_path.is_file():
            # We assume we already checked that the file is a compressed archive. Skip compressing
            # We don't know the uncompressed size, so leaving it None so we can compute it online.
            self.original_size = 0
            self.compressed_size = source_path.stat().st_size
            split_size = get_split_size(self.compressed_size)
            self.part_count = math.ceil(self.compressed_size / split_size)
            return

        # Source is a directory, compress it into a tar file.
        if self.compression:
            self._update_progress(f"Packaging and compressing datastore {self.name}...")
        else:
            self._update_progress(f"Packaging datastore {self.name}...")

        tar_results = tar_path(source_path=self.source_dir, target_file=self.target_file, compression=self.compression)

        self.original_size = tar_results.before_size
        self.compressed_size = tar_results.after_size
        split_size = get_split_size(self.compressed_size)
        self.part_count = math.ceil(self.compressed_size / split_size)

    def _create_uploader(self, presigned_urls: Dict[int, str], already_uploaded_parts: List[int]):
        # We added compressed size later, so if a session didn't have it serialized we will
        # look it up. This is used for the progress bar only and not affect functionality.
        size = self.compressed_size
        if size == 0:
            size = os.stat(self.target_file).st_size
        split_size = get_split_size(size)

        return S3Uploader(
            source_file=self.target_file,
            presigned_urls=presigned_urls,
            already_uploaded_parts=already_uploaded_parts,
            name=f"{self.name}-{self.version}",
            split_size=split_size,
            total_size=size,
            progress_callback=self
        )

    def _upload_parts(self):
        self._update_progress(f"Uploading datastore {self.name} (v{self.version}) datastore" + " to S3...")

        # Split urls depending on whether they were already uploaded or not.
        # This can happen if we resume an upload session.
        # The already uploaded ones are useful to show an accurate progress percentage.
        unuploaded_presigned_urls, already_uploaded_parts = {}, []
        for part, url in self.presigned_urls.items():
            if part not in self.etags:
                unuploaded_presigned_urls[part] = url
            else:
                already_uploaded_parts.append(part)
        uploader = self._create_uploader(
            presigned_urls=unuploaded_presigned_urls, already_uploaded_parts=already_uploaded_parts
        )

        # Stopping and starting the spinner, as the progress bar
        # in uploader will conflict with the spinner
        if self.spinner:
            self.spinner.stop()

        uploader.upload()

        if self.spinner:
            self.spinner.start()

    def _mark_upload_complete(self):
        self._update_progress("Completing multi-part uploads with Grid...")

        key = f"datastores/{self.id}/data/{self.uploaded_target_file}"
        urls = []
        for part, etag in self.etags.items():
            urls.append(V1CompletePresignedUrlUpload(etag=etag, part_number=int(part)))

        api_client = create_datastore_api_client()
        api_client.datastore_service_complete_datastore_presigned_urls_upload(
            datastore_id=self.id,
            upload_id=self.upload_id,
            cluster_id=self.cluster_id,
            body=Body3(object_key=key, urls=urls)
        )

        self._update_progress("Completing datastore upload...")

    def _create_session_file(self, session_id: str):
        """Create session state file so we can resume upload progress.
        """
        self.session_path = os.path.join(self.grid_datastores_path, session_id)
        self.session_path = str(Path.home().joinpath(self.session_path))
        Path.home().joinpath(self.session_path).mkdir(parents=True, exist_ok=True)
        self.session_file = os.path.join(self.session_path, "session.json")

    @property
    def session_name(self) -> str:
        return f"{self.name}-v{self.version}"

    def upload(self):
        """Upload completes the full datastore upload operation.

        It also records the progress of the upload, so it can be resumed later.
        """
        if self.session_id == "":
            self.session_id = str(uuid.uuid4())

        self._create_session_file(self.session_id)

        self.spinner = yaspin.yaspin(text=f'Uploading datastore {self.name} v{self.version}', color="yellow")
        self.spinner.start()

        steps = [(self._create_datastore, DatastoreUploadSteps.CREATE_DATASTORE),
                 (self._compress_source, DatastoreUploadSteps.COMPRESS_SOURCE_DIRECTORY),
                 (self._get_presigned_urls, DatastoreUploadSteps.GET_PRESIGNED_URLS),
                 (self._upload_parts, DatastoreUploadSteps.UPLOAD_PARTS),
                 (self._mark_upload_complete, DatastoreUploadSteps.MARK_UPLOAD_COMPLETE)]

        current_step = 0
        if self.last_completed_step:
            for i, step in enumerate(steps):
                if step[1] == self.last_completed_step:
                    current_step = i + 1
                    break

            if current_step == 0:
                raise ValueError(f"Unsupported upload step: " + self.last_completed_step)

        try:
            while current_step < len(steps):
                func, step = steps[current_step]
                func()
                self.last_completed_step = step
                self._write_session()
                current_step += 1

            self._remove_session()

            self.spinner.text = "\n".join([
                f"Datastore '{self.name}' finished uploading!",
                "To access the datastore in a new grid session:",
                f"   grid session create --datastore_name {self.name} --datastore_version {self.version}",
                "To access the datastore in a new grid run:",
                f"   grid run --datastore_name {self.name} --datastore_version {self.version} <your script and args here!>",
            ])

            self.spinner.ok("✔")

        except InvalidDatastoreError as e:
            self.spinner.fail("✘")
            self.logger.error(
                f"""
            An non-recoverable error occured when uploading datastore
            {self.session_name}.

            Please try again or contact Grid for support
            """
            )
            raise e
        except (Exception, KeyboardInterrupt) as e:
            self.spinner.fail("✘")
            message = f"""
            Whoops, your datastore creation failed!

            To resume, run:

            grid datastore resume {self.session_name}
            """
            raise e
        finally:
            self.spinner.stop()

    def upload_part_completed(self, part: int, etag: str):
        """Mark part uploaded

        Parameters
        ----------
        part: int
            Part number
        etag: str
            ETag returned
        """
        self.logger.debug(f"Part {part} finished uploading")
        with self.lock:
            self.etags[part] = etag
            self._write_session()

    def _write_session(self):
        """Writes the session state into session file
        """
        with open(self.session_file, "w") as f:
            data = self.to_dict()
            data["DATASTORE_VERSION"] = self.DATASTORE_VERSION
            json.dump(data, f)

    def _remove_session(self):
        shutil.rmtree(self.session_path, ignore_errors=True)
