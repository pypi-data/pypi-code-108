# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Utility methods for downloading files."""
from typing import List, Optional

import errno
import hashlib
import logging
import os
from requests import RequestException
import requests
import shutil
import time
from urllib.parse import urljoin
import zipfile

from azureml._common._error_definition import AzureMLError
from azureml.automl.core.shared._diagnostics.automl_error_definitions import DiskFull, InsufficientMemory
from azureml.automl.core.shared import logging_utilities
from azureml.automl.core.shared.exceptions import ClientException, ResourceException
from azureml.automl.core.shared.reference_codes import ReferenceCodes

logger = logging.getLogger(__name__)


class Downloader:
    """Helper class for assisting with generic file downloads."""

    @staticmethod
    def _is_download_needed(file_path: str, md5hash: Optional[str]) -> bool:
        """
        Delete as needed stuff at the file_path.

        :param file_path: File path to check and remove if needed.
        :param md5hash: md5hash of the expected file. Do not remove if the hash matches.
        :return: True if download is needed. False, otherwise.
        """
        if os.path.exists(file_path):
            if os.path.isdir(file_path):
                logger.info("Deleting a directory")
                shutil.rmtree(file_path)
            elif md5hash is not None and md5hash == Downloader.md5(file_path):
                logger.info("md5hash matched. No download necessary.")
                return False

        return True

    @classmethod
    def get_download_path(cls, file_name: str, target_dir: str, prefix: Optional[str] = None) -> str:
        """
        Build the path to which the specified file will be downloaded.

        :param file_name: File name requested.
        :param target_dir: Directory in which the file will be saved.
        :param prefix: Prefix corresponding to the class that has requested this download,
        to be prepended to the file_name.
        :return: Path to which we will try to download the file.
        """
        return os.path.join(target_dir, "{prefix}_{file_name}".format(prefix=prefix or '',
                                                                      file_name=file_name))

    @classmethod
    def download(cls, download_prefix: str, file_name: str, target_dir: str, md5hash: Optional[str] = None,
                 prefix: Optional[str] = None, retries: int = 4) -> Optional[str]:
        """
        Download the given url.

        :param download_prefix: Url to download from.
        :param file_name: File name requested in case of an archive.
        :param target_dir: Target directory in which we should download and store.
        :param md5hash: md5hash of the file being downloaded to prevent random files from getting downloaded.
        :param prefix: Prefix corresponding the class that has requested this download.
        :return: Path to the downloaded file name or None if the file doesn't exist or any failure.
        """

        download_path = Downloader.get_download_path(file_name=file_name,
                                                     target_dir=target_dir,
                                                     prefix=prefix)
        download_url = urljoin(download_prefix, file_name)

        # Clean up and check hash.
        if not Downloader._is_download_needed(download_path, md5hash):
            logger.info("File already found at {}. Skipping download".format(download_path))
            return download_path

        if cls._download_with_retries(download_url, download_path, retries, md5hash=md5hash):
            return download_path
        else:
            return None

    @classmethod
    def _download_with_retries(cls, download_url: str, download_path: str, retries: int,
                               md5hash: Optional[str] = None) -> bool:
        download_succeeded = False
        for retry_attempt in range(0, retries + 1):
            try:
                download_succeeded = cls._download(download_url=download_url,
                                                   download_path=download_path,
                                                   md5hash=md5hash)
                break
            except ClientException as ce:
                # Retry on client exceptions
                if retry_attempt < retries:
                    time_to_sleep_secs = pow(2, retry_attempt)
                    logger.warning("Exception when downloading {}.\n Retrying attempt {} after {} seconds".format(
                                   ce, retry_attempt + 1, time_to_sleep_secs))
                    time.sleep(time_to_sleep_secs)
                    continue
                else:
                    raise
        return download_succeeded

    @classmethod
    def _download(cls, download_url: str, download_path: str, md5hash: Optional[str] = None) -> bool:
        has_download_failed = False
        try:
            download_hash = cls._download_file(download_url, download_path)
        except RequestException as re:
            has_download_failed = True
            # Failed to download model
            logging_utilities.log_traceback(re, logger, is_critical=False)
            raise ClientException("Request exception when trying to download the file")
        except MemoryError as me:
            has_download_failed = True
            raise ResourceException._with_error(
                AzureMLError.create(
                    InsufficientMemory,
                    target='download',
                    operation_name='download',
                    reference_code=ReferenceCodes._DOWNLOAD_FAILED_WITH_MEMORY_ERROR
                ), inner_exception=me) from me
        except OSError as ose:
            has_download_failed = True
            logger.warning("Exception when trying to download model: {}".format(ose.strerror))
            logging_utilities.log_traceback(ose, logger, is_critical=False)
            if ose.errno == errno.ENOSPC:
                raise ResourceException._with_error(
                    AzureMLError.create(
                        DiskFull,
                        target='download',
                        operation_name='download',
                        reference_code=ReferenceCodes._DOWNLOAD_FAILED_WITH_DISK_FULL,
                    ), inner_exception=ose) from ose
            else:
                raise
        except Exception as e:
            has_download_failed = True
            logging_utilities.log_traceback(e, logger, is_critical=False)
            raise ClientException("Exception when trying to download the file")
        finally:
            if has_download_failed:
                Downloader.remove_file(download_path)
                logger.error("Download failed while trying to download file")

        if md5hash and download_hash != md5hash:
            error_message = "md5hash validation failed. This downloaded file will not be used " \
                            "and will be removed."
            Downloader.remove_file(download_path)
            logging_utilities.log_traceback(
                ClientException(error_message),
                logger,
                is_critical=False
            )
            has_download_failed = True
            raise ClientException(error_message)
        return not has_download_failed

    @staticmethod
    def _download_file(download_url: str, download_path: str) -> str:
        hash_md5 = hashlib.md5()
        chunk_size = 10 * 1024 * 1024
        download_start_time = time.clock()

        with requests.get(download_url, stream=True) as r, open(download_path, 'wb') as fd:
            if r.status_code != 404:
                for chunk in r.iter_content(chunk_size):  # 10M
                    if chunk:
                        fd.write(chunk)
                        hash_md5.update(chunk)
                        fd.flush()
                download_end_time = time.clock()

                logger.info("Embeddings download time: {time_taken}".format(
                    time_taken=download_end_time - download_start_time))
        return hash_md5.hexdigest()

    @classmethod
    def md5(cls, file_path: str) -> Optional[str]:
        """
        Calculate md5hash of the given file name if the path exists. Else, return None.

        :param file_path: Path to the file.
        :return: md5digest or None
        """
        if file_path is not None and os.path.exists(file_path):
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(65536), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        return None

    @classmethod
    def unzip_file(cls, zip_fname, extract_path):
        """
        Unzip the contents of the file, whose name is passed in

        :param zip_fname: name of the file to be un-zipped
        :param extract_path: path for the zipped folder to extracted to
        :return: Unzip the contents of the file, whose name is passed in
        """
        with zipfile.ZipFile(os.path.join(os.getcwd(), zip_fname), 'r') as zf:
            try:
                # Try around extracting.
                # The extractall() throws in a multinode context when using a shared filesystem
                zf.extractall(extract_path)
            except (IOError, OSError):
                msg = """Problem in extracting zip file in automl sdk file downloader.
                             In a distributed training context, this is expected to occur
                             for up to n_nodes - 1 times."""
                logger.warning(msg)
                pass
        return zf.filelist

    @staticmethod
    def get_zip_filelist(zip_fname: str) -> List[zipfile.ZipInfo]:
        """
        Get the list of files inside a zip archive without extracting them.

        :param zip_fname: The name of the file to be un-zipped.
        :return: The zipfile filelist.
        """
        with zipfile.ZipFile(os.path.join(os.getcwd(), zip_fname), 'r') as zf:
            return zf.filelist

    @staticmethod
    def remove_file(file_path: str) -> None:
        """
        Safely remove a file from disk given it's path.

        :param file_path: The path of the file to remove.
        """
        try:
            os.remove(file_path)
        except Exception as ex:
            logging_utilities.log_traceback(ex,
                                            logger,
                                            override_error_msg="Removing file failed",
                                            is_critical=False)
