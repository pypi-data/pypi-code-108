"""
    Network utilities of LHAPDF
"""
from pathlib import Path
import urllib.parse
import urllib.request
import logging
import math
import shutil
import tempfile

try:
    from tqdm import tqdm

    _enable_fancy_progress = True
except ImportError:
    _enable_fancy_progress = False

    class tqdm:
        pass


from .configuration import environment

logger = logging.getLogger(__name__)


def _byte_print(byte_size):
    """Return size as a nicely-formatted string"""
    units = ("B", "KB", "MB", "GB")
    order = int(math.log(byte_size, 1024))
    value = byte_size / 1024 ** order
    if value > 0:
        return f"{value:.2f} {units[order]}"
    return "0 B"


class _ProgressBar(tqdm):
    """Progress bar prepared for urllib.request.urlretrieve"""

    def progress_update(self, block_num=1, block_size=1, total_size=None):
        """
        block_num: int
            Number of blocks already transferred
        block_size: int
            Size of each block
        total_size: int
            Total size
        """
        if total_size is not None:
            self.total = total_size
        self.update(block_num * block_size - self.n)
        # At every point self.n is set to = block_num * block_Size


def _copy_file(source, destination, dryrun=False):
    """Copies a file from source to destination"""
    source_path = Path(source)
    # Check whether it exists and fail otherwise)
    if not source_path.exists():
        raise FileNotFoundError(f"{source_path} not found")
    logger.debug("Copying the data from %s to %s", source_path, destination)
    if dryrun:
        file_size = source_path.stat().st_size
        logger.info("%s [%s]", source_path.name, _byte_print(file_size))
    # Finally, copy
    shutil.copy(source_path, destination)


def _download_url(source_url, dest_path):
    """Download a file from a source url to a destination
    It first downloads to some temporary folder"""
    tmp_dest = tempfile.mktemp()
    if _enable_fancy_progress:
        with _ProgressBar(unit="B", unit_scale=True, unit_divisor=1024, miniters=1, desc=dest_path.name) as pbar:
            urllib.request.urlretrieve(source_url, tmp_dest, pbar.progress_update)
    else:
        urllib.request.urlretrieve(source_url, tmp_dest)
        logger.info("%s [%s]", source_url, _byte_print(Path(tmp_dest).stat().st_size))
    shutil.move(tmp_dest, dest_path)


def _get_remote_size(source_url):
    """Query the remote for the size of the object that would
    be downloaded"""
    req = urllib.request.Request(source_url, method="HEAD")
    url_open = urllib.request.urlopen(req)
    if url_open.status != 200:
        raise urllib.request.URLError
    return int(url_open.headers.get("Content-Length", 0))


def download_magic(target_name, destination, dry=False):
    """Utilizes the internal sources (with an option for a list of more)
    to download (or copy) the target name to the given destination.

    This function tries to avoid failing in order to behave similarly to previous LHAPDF releases
    logs all errors only on total failure.

    The final result is the download/copy of ``target_name`` to ``destination/target_name``

    Parameters
    ---------
        target_name: str
            Name of the target item to be downloaded
        destination: path or str
            Destination folder for the download
        dry: bool
            If true do not download anything
    """
    dest_dir = Path(destination)
    dest_dir.mkdir(exist_ok=True, parents=True)
    dest_path = dest_dir / target_name

    errors = []

    # Using a "better ask forgiveness rather than permission" approach for now
    for source in environment.sources:
        source_url = urllib.parse.urlparse(source)
        if source_url.path and not source_url.netloc:
            try:
                source_path = Path(source_url.path) / target_name
                _copy_file(source_path, dest_path)
                return True
            except FileNotFoundError:
                errors.append(f"{source} not found")
                continue

        try:
            url = source + target_name
            if dry:
                b_size = _get_remote_size(url)
                print(f"{target_name} [{_byte_print(b_size)}]")
                # logger.info("%s [%s]", target_name, _byte_print(b_size))
                return True

            _download_url(url, dest_path)
            return True
        except urllib.request.URLError as e:
            errors.append(f"Unable to download from {url}: {e}")
        except KeyboardInterrupt:
            # Allow cancelling specific downloads
            logger.error("Download halted by user")
    for error in errors:
        logger.error(error)
    return False
