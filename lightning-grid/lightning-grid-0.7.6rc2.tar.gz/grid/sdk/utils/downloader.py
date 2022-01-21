from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

import requests
from tqdm import tqdm


@dataclass
class DownloadableObject:
    """Object that can be downloaded from an URL into a local path."""
    url: str
    download_path: str
    filename: str
    downloaded: bool = False


class Downloader:
    """
    Downloads multiple files into their respective location
    using background threads.

    Attributes
    ----------
    workers: int
        Number of background threads to use.
    progress: Progress
        Instance of a Progress bar object.
    Parameters
    ----------
    urls: List[DownloadableObject]
        List of URL objects containing.
    """
    def __init__(self, downloadable_objects: List[DownloadableObject], base_dir: str):

        self.downloadable_objects = downloadable_objects
        self.download_chunk_size = 1024  # in bytes
        self.base_dir = base_dir

    @staticmethod
    def create_dir_tree(dest_dir: str, base_dir: Optional[str] = None) -> None:
        """
        Creates directory structure for downloading file.

        Parameters
        ----------
        dest_dir: str
            Destination directory for where to download file.
        base_dir: str
            Base directory to place all targer directories into.
        """
        if base_dir:
            P = Path(base_dir) / Path(dest_dir)
        else:
            P = Path(dest_dir)

        P.mkdir(parents=True, exist_ok=True)

    def download(self):
        """
        Download multuple files to the given directory. This will download
        files using a ThreadPoolExecutor so that multiple files can
        be downloaded concurrently. We can set the concurrency level
        by changing the class' workers` attribute.
        """
        tqdm_iter = tqdm(self.downloadable_objects, unit="files")
        for obj in tqdm_iter:
            obj: DownloadableObject
            tqdm_iter.set_description(desc=obj.filename)
            # Creates directory tree if it doesn't exist
            Downloader.create_dir_tree(obj.download_path, self.base_dir)

            # Creates destination path in tree
            destination_path = Path(self.base_dir) / Path(obj.download_path) / Path(obj.filename)

            # Download file to path
            response = requests.get(obj.url, allow_redirects=True, stream=True)
            with open(destination_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=self.download_chunk_size):
                    if chunk:
                        file.write(chunk)

            # Mark object as downloaded
            obj.downloaded = True
