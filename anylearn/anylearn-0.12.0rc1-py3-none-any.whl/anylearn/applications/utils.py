import hashlib
from pathlib import Path
import random
import shutil
import string
from typing import Optional, Union

from ..config import AnylearnConfig
from ..utils import logger
from ..utils.errors import AnyLearnMissingParamException


def make_name_by_path(path: Union[str, Path]) -> str:
    if not path:
        raise AnyLearnMissingParamException("`path` required.")
    path = Path(path)
    basename = path.name
    suffix = hashlib.sha1(str(path).encode('utf-8')).hexdigest()[:8]
    return f"{basename}-{suffix}"


def generate_random_name() -> str:
    return ''.join(random.sample(string.ascii_lowercase + string.digits, 8))


def _check_resource_input(id: Optional[str]=None,
                          dir_path: Optional[Union[str, Path]]=None,
                          archive_path: Optional[str]=None):
    if not any([id, dir_path, archive_path]):
        raise AnyLearnMissingParamException((
            "At least one of the parameters "
            "['id', 'dir_path', 'archive_path'] "
            "should be specified."
        ))


def _get_or_create_resource_archive(name,
                                    dir_path: Optional[Union[str, Path]]=None,
                                    archive_path: Optional[str]=None):
    logger.info("Packaging resources...")
    if not archive_path or not Path(archive_path).exists():
        archive_path = shutil.make_archive(
            AnylearnConfig.workspace_path / name,
            "zip",
            dir_path
        )
    return archive_path


def _get_archive_checksum(archive_path: str, buffer_size: int=65536):
    checksum = hashlib.blake2b()
    with open(archive_path, "rb") as f:
        while True:
            chunk = f.read(buffer_size)
            if not chunk:
                break
            checksum.update(chunk)
    return checksum.hexdigest()
