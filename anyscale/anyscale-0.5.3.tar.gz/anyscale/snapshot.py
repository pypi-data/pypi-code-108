import logging
import shutil
from typing import Any

import requests


logger = logging.getLogger(__file__)


def copy_file(to_s3: bool, source: str, target: Any, download: bool) -> None:
    """Copy a file.

    The file source or target may be on S3.

    Args:
        to_s3 (bool): If this is True, then copy to/from S3, else the local
            disk. If this is True, then the file source or target will be a
            presigned URL to which GET or POST HTTP requests can be sent.
        source (str or S3 URL): Source file local pathname or S3 GET URL. If
            this is an S3 URL, target is assumed to be a local pathname.
        target (str or S3 URL): Target file local pathname or S3 URL with POST
            credentials. If this is an S3 URL, source is assumed to be a local
            pathname.
        download (bool): If this is True, then this will upload from source to
            target, else this will download.
    """
    try:
        if to_s3:
            if download:
                with open(target, "wb") as f:
                    response = requests.get(source)
                    for block in response.iter_content(1024):
                        f.write(block)
            else:
                with open(source, "rb") as f:
                    files = {"file": ("object", f)}
                    resp = requests.post(
                        target["url"], data=target["fields"], files=files
                    )
                    assert resp.ok, resp.text
        else:
            shutil.copyfile(source, target)
    except (OSError, AssertionError) as e:
        logger.warn("Failed to copy file %s , aborting", source)
        raise e
