import os
from io import BytesIO
from typing import Optional, Tuple
from pathlib import Path
from shutil import copyfile

from common_client_scheduler import AwsCredentials
import hashlib
from terality._terality.data_transmitter import DataTransmitter

from common_client_scheduler.config import SessionInfoLocal, SessionInfoType


class DataTransmitterLocal(DataTransmitter):
    def __init__(self):
        self._session = None

    def get_upload_aws_region(self) -> str:
        raise NotImplementedError()

    def get_download_source_bucket_and_prefix(
        self, aws_region: Optional[str], transfer_id: str
    ) -> Tuple[str, str]:
        raise NotImplementedError()

    def set_current_session(self, session: Optional[SessionInfoType]):
        if session is None:
            self._session = None
            return

        if not isinstance(session, SessionInfoLocal):
            raise ValueError(f"Type of session must be SessionInfoLocal, got {type(session)}.")
        self._session = session

    def upload_bytes(
        self,
        aws_credentials: AwsCredentials,  # pylint: disable=unused-argument
        data: BytesIO,
    ) -> str:
        assert self._session is not None
        upload_id = hashlib.sha512(data.getvalue()).hexdigest()
        upload_folder = self._session.upload_config.path / upload_id
        try:
            upload_folder.mkdir(exist_ok=False, parents=False)
            (upload_folder / "0.parquet").write_bytes(data.getvalue())
        except FileExistsError:
            # Cached
            # If the file already exists under the same hash folder, do not re-upload
            return upload_id
        return upload_id

    def upload_local_file(
        self,
        aws_credentials: AwsCredentials,  # pylint: disable=unused-argument
        local_file: str,
        file_suffix: str,
        cache_disabled: bool,
    ) -> None:
        assert self._session is not None
        upload_config = self._session.upload_config
        (upload_config.path / file_suffix).parent.mkdir(exist_ok=True, parents=True)

        if not cache_disabled and (upload_config.path / file_suffix).is_file():
            # If file exists in directory, no need to recreate it
            return

        copyfile(Path(local_file), upload_config.path / file_suffix)

    def download_to_bytes(
        self,
        aws_credentials: AwsCredentials,  # pylint: disable=unused-argument
        transfer_id: str,
    ) -> BytesIO:
        assert self._session is not None
        return BytesIO(
            (self._session.download_config.path / transfer_id / "0.parquet").read_bytes()
        )

    def download_to_local_files(
        self,
        aws_credentials: AwsCredentials,  # pylint: disable=unused-argument
        transfer_id: str,
        path: str,
        is_folder: bool,
        with_leading_zeros: bool,
    ) -> None:
        assert self._session is not None
        download_dir = self._session.download_config.path / transfer_id
        files = sorted(download_dir.iterdir())
        if is_folder:
            dirname = os.path.dirname(path)
            filename = os.path.basename(path)
            Path(dirname).mkdir(parents=True, exist_ok=True)
            for num, file in enumerate(files):
                file_num = f"{num:0{len(str(len(files)))}d}" if with_leading_zeros else str(num + 1)
                copyfile(file, f"{dirname}/{filename.replace('*', file_num)}")
        else:
            copyfile(files[0], path)
