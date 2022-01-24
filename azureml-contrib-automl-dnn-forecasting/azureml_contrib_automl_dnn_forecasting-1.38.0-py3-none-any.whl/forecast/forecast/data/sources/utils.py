"""Tools for simplifying the creation of data sources."""

import os.path as osp
import tempfile
import zipfile

import requests


def fetch_zipped_data(out_path: str, url: str) -> None:
    """Fetches and extracts zipped data to a specified path.

    Parameters
    ----------
    out_path: str
        The desired path where the data should ultimately reside
    url:
        The url from which the data can be fetched

    Returns
    -------
    None

    """
    if osp.exists(out_path):
        return

    # download zip to temporary directory if it doesn't exist
    r = requests.get(url)
    temp_dir = tempfile.TemporaryDirectory()
    temp_path = osp.join(temp_dir.name, 'zipped.zip')
    with open(temp_path, 'wb') as f:
        f.write(r.content)

    # unzip
    with zipfile.ZipFile(temp_path, 'r') as zipped:
        # if we're extracting a directory (and the path contains a trailing /), dirname will return the input
        # we're seeking the parent directory so we must strip the trailing / if it exists
        parent_dir, fname = osp.split(out_path)

        # extract the file/directory in the zip to the directory specified by out_path
        zipped.extract(fname, parent_dir)
