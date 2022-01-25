from concurrent.futures import as_completed, ThreadPoolExecutor
import time
from typing import AnyStr, Dict, List

import requests
from requests.adapters import HTTPAdapter
from rich.progress import BarColumn, Progress, TextColumn
from urllib3.util.retry import Retry


class UploadProgressCallback:
    """
    This class provides a interface for notifying upload progress
    """
    @staticmethod
    def upload_part_completed(part: int, etag: str):
        return NotImplemented


class S3Uploader:
    """
    # TODO - revamp this once datastore upload is moved to direct s3 upload
    This class uploads a source file with presigned urls to S3

    Attributes
    ----------
    source_file: str
        Source file to upload
    presigned_urls: Dict[int, str]
        Presigned urls dictionary, with key as part number and values as urls
    already_uploaded_parts: List[int]
        List of parts that have already been uploaded
    workers: int
        Amount of workers to upload parts
    retries: int
        Amount of retries when requests encounters an error
    backoff_factor: float
        A backoff factor to apply between attempts after the second try
    total_size: int
        Size of all files to upload
    name: str
        Name of this upload to display progress
    progress_callback: UploadProgressCallback
        Callback for notifying upload progress
    """
    workers: int = 8
    retries: int = 10000
    backoff_factor: float = 1.
    disconnect_retry_wait_seconds: int = 5

    progress = Progress(
        TextColumn("[bold blue]{task.description}", justify="left"), BarColumn(bar_width=None),
        "[self.progress.percentage]{task.percentage:>3.1f}%"
    )

    def __init__(
        self,
        presigned_urls: Dict[int, str],
        already_uploaded_parts: List[int],
        source_file: str,
        total_size: int,
        split_size: int,
        name: str,
        progress_callback: UploadProgressCallback = None
    ):
        self.presigned_urls = presigned_urls
        self.already_uploaded_parts = already_uploaded_parts
        self.source_file = source_file
        self.total_size = total_size
        self.split_size = split_size
        self.name = name
        self.progress_callback = progress_callback

    @staticmethod
    def upload_s3_data(
        url: str, data: bytes, retries: int, backoff_factor: float, disconnect_retry_wait_seconds: int
    ) -> str:
        """
        Send data to s3 url

        Parameters
        ----------
        url: str
            S3 url string to send data to
        data: bytes
             Bytes of data to send to S3
        retries: int
            Amount of retries
        backoff_factor: float
            Retry backoff factor
        disconnect_retry_wait_seconds: int
            Amount of seconds between disconnect retry

        Returns
        -------
        str
            ETag from response
        """
        disconnect_retries = retries
        while disconnect_retries > 0:
            try:
                s = requests.Session()
                retries = Retry(total=retries, backoff_factor=backoff_factor, status_forcelist=[500, 502, 503, 504])
                s.mount('http://', HTTPAdapter(max_retries=retries))
                response = s.put(url, data=data)
                if 'ETag' not in response.headers:
                    raise ValueError(f"Unexpected response from S3, response: {response.content}")
                return response.headers['ETag']
            except BrokenPipeError:
                time.sleep(disconnect_retry_wait_seconds)
                disconnect_retries -= 1

        raise ValueError(f"Unable to upload datastore part after disconnect retries")

    def _get_size(self, part_path: str, part: int) -> AnyStr:
        """
        Returns the size of a specific part.

        Parameters
        ----------
        part_path: str
            Path to part file
        part: int
            Part number
        Returns
        -------
        AnyStr
            Part size
        """
        with open(part_path, 'rb') as f:
            pos = self.split_size * (part - 1)
            f.seek(pos)
            data = f.read(self.split_size)

        return data

    def _progress_already_uploaded(self, task_id: str) -> None:
        """
        Moves the progress bar to account for previously
        uploaded parts so that it shows consistent and
        recoverable progress when resuming the upload.

        Parameters
        ----------
        task_id: str
            Task id for tracking progress
        """
        for part in self.already_uploaded_parts:
            data = self._get_size(part_path=self.source_file, part=part)

            self.progress.update(task_id, advance=len(data))

    def _upload_part(self, url: str, part_path: str, part: int, task_id: str) -> None:
        """
        Upload part of the data file with presigned url

        Parameters
        ----------
        url: str
            Presigned url to upload to S3
        part_path: str
            Path to part file
        part: int
            Part number
        task_id: str
            Task id for tracking progress
        """
        with open(part_path, 'rb') as f:
            pos = self.split_size * (part - 1)
            f.seek(pos)
            data = f.read(self.split_size)

        etag = self.upload_s3_data(url, data, self.retries, self.backoff_factor, self.disconnect_retry_wait_seconds)
        self.progress.update(task_id, advance=len(data))
        if self.progress_callback:
            self.progress_callback.upload_part_completed(part=part, etag=etag)

    def upload(self) -> None:
        """
        Upload files from source dir into target path in S3
        """
        task_id = self.progress.add_task("upload", filename=self.name, total=self.total_size)
        with ThreadPoolExecutor(max_workers=self.workers) as pool:
            try:
                self.progress.start()
                futures = []

                if self.already_uploaded_parts:
                    f = pool.submit(self._progress_already_uploaded, task_id)
                    futures.append(f)

                    for future in as_completed(futures):
                        future.result()

                for part, url in self.presigned_urls.items():
                    f = pool.submit(self._upload_part, url, self.source_file, part, task_id)
                    futures.append(f)

                    for future in as_completed(futures):
                        future.result()
            finally:
                self.progress.stop()
