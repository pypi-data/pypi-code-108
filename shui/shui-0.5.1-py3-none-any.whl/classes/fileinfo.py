"""Class to relate local and remote information about a Spark/Hadoop file"""
from tqdm import tqdm
import requests


class FileInfo:
    """Class to relate local and remote information about a Spark/Hadoop file"""

    def __init__(self, remote_url, local_path):
        self.url = remote_url
        self.path = local_path

    @property
    def name(self):
        """Get the name of the local file"""
        return self.path.name

    @property
    def is_hashfile(self):
        """Boolean indicating whether this is a hashfile"""
        return self.path.suffix == ".sha512"

    def download(self):
        """Download this Spark/Hadoop version from a remote URL to a local path"""
        response = requests.get(self.url, stream=True, allow_redirects=True)
        total_size = int(response.headers.get("content-length"))
        with open(self.path, "wb") as output_file:
            with tqdm(total=total_size, unit="B", unit_scale=True) as progress_bar:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        output_file.write(chunk)
                        progress_bar.update(len(chunk))

    def is_hash_for(self, other):
        """Boolean indicating whether this is the hashfile corresponding to another file"""
        return self.is_hashfile and self.path.stem == other.path.name

    def remove(self):
        """Remove the local file"""
        if self.path.is_file():
            self.path.unlink()
