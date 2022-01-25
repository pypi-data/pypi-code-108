import hashlib
from pathlib import Path
from typing import List

from common_client_scheduler import AwsCredentials

from .. import global_client
from ...exceptions import TeralityClientError


def upload_local_files(path: str, aws_credentials: AwsCredentials, cache_disabled: bool) -> str:
    """
    Copy files from a local directory to a Terality-owned S3 bucket.

    Args:
        path: path to a single file or a directory. If a directory, all files in the directory will be uploaded.
    """
    try:
        if Path(path).is_file():
            file_checksum = _calculate_file_checksum(path)
            global_client().data_transfer().upload_local_file(
                aws_credentials,
                path,
                f"{file_checksum}/{0}.data",
                cache_disabled,
            )
            return file_checksum

        paths: List[str] = [str(path_) for path_ in sorted(Path(path).iterdir())]
        folder_checksum = _calculate_folder_checksum(paths)
        for file_num, _ in enumerate(paths):
            global_client().data_transfer().upload_local_file(
                aws_credentials,
                paths[file_num],
                f"{folder_checksum}/{file_num}.data",
                cache_disabled,
            )
        return folder_checksum
    except FileNotFoundError as e:
        raise TeralityClientError(
            f"File '{path}' could not be found in your local directory, please verify the path. If your file is stored on the cloud, make sure your path starts with 's3://', 'abfs://', or 'az://'.",
        ) from e


def _calculate_file_checksum(file_: str) -> str:
    sha512 = hashlib.sha512()
    with open(file_, "rb") as f:
        for chunk in iter(lambda: f.read(4_194_304), b""):
            sha512.update(chunk)
    return sha512.hexdigest()


def _calculate_folder_checksum(paths: List[str]) -> str:
    folder_checksum = ""
    for path_ in paths:
        file_checksum = _calculate_file_checksum(path_)
        folder_checksum = hashlib.sha512(f"{folder_checksum}{file_checksum}".encode()).hexdigest()
    return folder_checksum
