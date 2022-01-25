import argparse
import asyncio
import copy
from enum import Enum
import hashlib
import io
import json
import logging
import os
from pathlib import Path
import pickle
import shutil
import sys
import tarfile
import tempfile
from typing import Any, Dict, List, Optional, Tuple, TYPE_CHECKING
from urllib.parse import urlparse
import uuid

import aiobotocore  # type: ignore
import conda_pack  # type: ignore
from filelock import FileLock
import yaml

from anyscale.api import configure_open_api_client_headers
import anyscale.utils.ray_conda as ray_conda
from anyscale.utils.ray_utils import _dir_travel, _get_excludes  # type: ignore


if TYPE_CHECKING:
    from ray.job_config import JobConfig

logger = logging.getLogger(__name__)

SINGLE_FILE_MINIMAL = 25 * 1024 * 1024  # 25MB
DELTA_PKG_LIMIT = 100 * 1024 * 1024  # 100MB


DIR_META_FILE_NAME = ".anyscale_runtime_dir"

event_loop = asyncio.new_event_loop()

# TODO (yic): Use ray._private.runtime_env.PKG_DIR instead
# Right now, with client server manager, the tmp dir is not set properly
# PKG_DIR will be set after node is constructed
PKG_DIR = "/tmp/ray/session_latest/runtime_resources/"


class ResourceType(Enum):
    WORKING_DIR: str = "working_dir_"
    CONDA: str = "conda_"


class PackagePrefix(Enum):
    """Theses are prefix of different packages. Packages are composed by
        base + [add] - del ==> resource_dir
    """

    # Base package is the base part for the resource
    BASE_PREFIX: str = "base_"
    # Add package is what to add to for the resource.
    ADD_PREFIX: str = "add_"
    # Del package is what to be deleted after
    DEL_PREFIX: str = "del_"
    # Resoruce dir pkg is where to unpack the data
    RESOURCE_DIR_PREFIX: str = "resource_dir_"


def _gen_token() -> Any:
    from anyscale.authenticate import get_auth_api_client
    from anyscale.sdk.anyscale_client.sdk import AnyscaleSDK

    auth_api_client = get_auth_api_client()
    sdk = AnyscaleSDK(
        auth_token=auth_api_client.credentials, host=auth_api_client.host,
    )
    configure_open_api_client_headers(sdk.api_client, "connect")
    api_client = auth_api_client.api_client
    configure_open_api_client_headers(api_client.api_client, "connect")
    org_id = api_client.get_user_info_api_v2_userinfo_get().result.organization_ids[0]
    token = sdk.get_organization_temporary_object_storage_credentials(
        organization_id=org_id, region="default",
    ).result.s3
    logger.debug(f"S3: bucket({token.bucket}) path({token.path})")
    token.path = org_id + "/"
    return token


def _create_s3_client(session: aiobotocore.AioSession, token: Any):  # type: ignore
    return session.create_client(
        "s3",
        region_name=token.region,
        aws_access_key_id=token.aws_access_key_id,
        aws_secret_access_key=token.aws_secret_access_key,
        aws_session_token=token.aws_session_token,
    )


async def _get_object(  # type: ignore
    s3, bucket: str, key: str,
):
    obj = await s3.get_object(Bucket=bucket, Key=key)
    return obj["Body"]


async def _put_object(s3, bucket: str, key: str, local_path: str,) -> None:  # type: ignore
    await s3.put_object(Body=open(local_path, "rb"), Bucket=bucket, Key=key)


async def _object_exists(s3, bucket: str, key: str,) -> bool:  # type: ignore
    try:
        await s3.head_object(
            Bucket=bucket, Key=key,
        )
    except Exception:
        return False
    return True


def _object_exists_sync(token: Any, bucket: str, key: str) -> bool:
    async def helper(key: str,) -> bool:
        session = aiobotocore.get_session()
        async with _create_s3_client(session, token) as s3:
            exists = await _object_exists(s3, bucket, key)
            return exists

    return event_loop.run_until_complete(helper(key))


def _hash_file_contents(local_path: Path, hasher: "hashlib._Hash") -> "hashlib._Hash":
    if local_path.is_file():
        buf_size = 4096 * 1024
        with local_path.open("rb") as f:
            data = f.read(buf_size)
            while len(data) != 0:
                hasher.update(data)
                data = f.read(buf_size)
    return hasher


def _entry_hash(local_path: Path, tar_path: Path) -> bytes:
    """Calculate the hash of a path

    If it's a directory:
        dir_hash = hash(tar_path)
    If it's a file:
        file_hash = dir_hash + hash(file content)
    """
    hasher = hashlib.md5()
    hasher.update(str(tar_path).encode())
    return _hash_file_contents(local_path, hasher).digest()


def _xor_bytes(left: Optional[bytes], right: Optional[bytes]) -> Optional[bytes]:
    """Combine two hashes that are commutative.

    We are combining hashes of entries. With this function, the ordering of the
    entries combining doesn't matter which avoid creating huge list and sorting.
    """
    if left and right:
        return bytes(a ^ b for (a, b) in zip(left, right))
    return left or right


class _PkgURI(object):
    """This class represents an internal concept of URI.

    An URI is composed of: pkg_type + hash_val. pkg_type is an entry of
    PackagePrefix.

    For example, `add_<content_hash>` or `del_<content_hash>`.

    The purpose of this class is to make the manipulation of URIs easier.
    """

    @classmethod
    def from_uri(cls, pkg_uri: str) -> "_PkgURI":
        """Constructor of _PkgURI from URI."""
        uri = urlparse(pkg_uri)
        assert uri.scheme == "s3"
        name = uri.netloc
        resource_type = None
        pkg_type = None
        for r in ResourceType:
            if name.startswith(r.value):
                resource_type = r
                name = name[len(r.value) :]
                break
        assert resource_type is not None

        for p in PackagePrefix:
            if name.startswith(p.value):
                pkg_type = p
                name = name[len(p.value) :]
        assert pkg_type is not None
        hash_val = name
        assert len(hash_val) != 0
        return cls(resource_type, pkg_type, hash_val)

    def __init__(
        self, resource_type: ResourceType, pkg_type: PackagePrefix, hash_val: str
    ):
        """Constructor of _PkgURI."""
        self._resource_type = resource_type
        self._pkg_type = pkg_type
        self._hash_val = hash_val
        # Right now we only support s3. Hard code it here.
        self._scheme = "s3"

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, _PkgURI):
            return NotImplemented
        return (
            self._scheme == other._scheme
            and self._pkg_type == other._pkg_type
            and self._hash_val == other._hash_val
        )

    def uri(self) -> str:
        return self._scheme + "://" + self.name()

    def local_path(self) -> Path:
        return Path(PKG_DIR) / self.name()

    def resource_type(self) -> ResourceType:
        return self._resource_type

    def name(self) -> str:
        assert isinstance(self._pkg_type.value, str)
        assert isinstance(self._resource_type.value, str)
        return self._resource_type.value + self._pkg_type.value + self._hash_val

    def is_base_pkg(self) -> bool:
        return self._pkg_type == PackagePrefix.BASE_PREFIX

    def is_add_pkg(self) -> bool:
        return self._pkg_type == PackagePrefix.ADD_PREFIX

    def is_del_pkg(self) -> bool:
        return self._pkg_type == PackagePrefix.DEL_PREFIX

    def is_resource_dir_pkg(self) -> bool:
        return self._pkg_type == PackagePrefix.RESOURCE_DIR_PREFIX


class _Pkg:
    """Class represent a package.

    A package is composed by pkg_uri + contents."""

    def __init__(
        self,
        root_dir: Path,
        resource_type: ResourceType,
        pkg_type: PackagePrefix,
        hash_val: str,
        contents: Optional[List[Tuple[Path, bytes]]] = None,
    ):
        self._uri = _PkgURI(resource_type, pkg_type, hash_val)
        self._root_dir = root_dir
        if contents is None:
            contents = []
        self._contents = contents

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, _Pkg):
            return NotImplemented
        return (
            self._uri == other._uri
            and self._root_dir == other._root_dir
            and set(self._contents) == set(other._contents)
        )

    def create_tar_file(self) -> str:
        """Create a physical package.

        It'll to through contents and put every file into a tar file.
        This function will return the path to the physical package. The caller
        need to clean it up once finish using it.

        TODO (yic): Support steaming way to update the pkg.
        """
        empty_file = io.BytesIO()
        with tempfile.NamedTemporaryFile(delete=False) as f:
            with tarfile.open(fileobj=f, mode="w:") as tar:
                for (to_path, _) in self._contents:
                    file_path = self._root_dir / to_path
                    if self._uri.is_del_pkg():
                        info = tarfile.TarInfo(str(to_path))
                        info.size = 0
                        tar.addfile(info, empty_file)
                    else:
                        if file_path.is_dir():
                            info = tarfile.TarInfo(str(to_path))
                            info.type = tarfile.DIRTYPE
                            info.mode = 0o775
                            tar.addfile(info)
                        else:
                            tar.add(file_path, to_path)
            return f.name

    def name(self) -> str:
        return self._uri.name()

    def uri(self) -> str:
        return self._uri.uri()

    def update_meta(self) -> None:
        """Persist the meta info into disk.

        This function is for base package only. It'll transform the contents
        into meta and writing to a disk file.
        """
        assert self._uri.is_base_pkg()
        files = {}
        for (to_path, hash_val) in self._contents:
            files[str(to_path)] = hash_val.hex()
        meta = {"hash_val": self._uri._hash_val, "files": files}
        with (self._root_dir / DIR_META_FILE_NAME).open("w") as meta_file:
            meta_file.write(json.dumps(meta))


def _read_dir_meta(
    work_dir: Path, _skip_check: bool = False
) -> Optional[Dict[str, Any]]:
    """Read meta from the meta file.

    Meta file is composed by json string. The structure of the file is like this:
    {
       "hash_val": "base_pkg_hash",
       "files": {
         "file1": "hash1",
         "file2": "hash2",
       }
    }
    """
    meta_file_path = work_dir / DIR_META_FILE_NAME
    if not meta_file_path.exists():
        return None
    meta_valid = True
    if not meta_file_path.is_file():
        meta_valid = False
    try:
        meta = json.loads(meta_file_path.read_text())
        if "hash_val" not in meta or "files" not in meta:
            meta_valid = False
    except Exception:
        meta_valid = False
        meta = None
    if not meta_valid or not isinstance(meta, dict):
        raise ValueError(
            f"Invalid meta file: f{meta_file_path}. This should be a"
            "file managed by anyscale. The content of the file is broken."
            "Please consider delete/move it and retry"
        )
    if _skip_check:
        return meta
    pkg_uri = _PkgURI(
        ResourceType.WORKING_DIR, PackagePrefix.BASE_PREFIX, meta["hash_val"]
    )
    try:
        token = _gen_token()
        if _object_exists_sync(token, token.bucket, token.path + pkg_uri.name()):
            logger.debug("Base meta exists in s3")
            # For mypy warning. It will raise exception before.
            assert isinstance(meta, dict)
            return meta
        else:
            return None
    except Exception:
        logger.error("Failed to check the meta existence. Treat it as not existing")
        return None


def _get_base_pkg_from_meta(working_dir: Path, meta: Dict[str, Any]) -> _Pkg:
    files = []
    for (f, h) in meta["files"].items():
        files.append((Path(f), bytes.fromhex(h)))
    return _Pkg(
        working_dir,
        ResourceType.WORKING_DIR,
        PackagePrefix.BASE_PREFIX,
        meta["hash_val"],
        files,
    )


""""
The following functions are related with package splitting and uploading
"""


def _calc_pkg_for_working_dir(
    working_dir: Path, excludes: List[str], meta: Optional[Dict[str, Any]]
) -> Tuple[
    Optional[_Pkg], Optional[_Pkg], Optional[_Pkg], List[_Pkg]
]:  # base  # add  # del  # files
    """Split the working directory and calculate the pkgs.

    The algorithm will go with this way:
       - create delta if we have base.
       - (or) create the base if no base.
       - if delta is too big (DELTA_PKG_LIMIT, default as 100MB), we update the
         base.

    All big files will be put into a separate package.

    Args:
        working_dir (Path): The working directory to split.
        excludes (List[str]): The pattern to exclude from. It follows gitignore.
        meta (Optional[Dict[str, Any]]): This is the base meta we have.

    Returns:
        List of packages(base_pkg, add_pkg, del_pkg, pkgs)
    """
    # TODO (yic) Try to avoid calling ray internal API
    if ".anyscale_runtime_dir" not in excludes:
        excludes.append(".anyscale_runtime_dir")
    excludes = _get_excludes(working_dir, excludes)
    pkgs = []
    files = []
    hash_val = None
    base_files = copy.deepcopy(meta["files"]) if meta is not None else {}
    delta_size = 0

    all_files = []
    all_hash_val = None

    def handler(path: Path) -> None:
        # These nonlocals are output of the traveling.
        #   hash_val: the hash value of delta package
        #   all_files: contain all files for the new base which will be used if we re-base
        #   all_hash_val: the hash value of new base
        #   pkgs: contains big files which size is greater than SINGLE_FILE_MINIMAL
        #   delta_size: the size of the delta
        nonlocal hash_val, all_files, all_hash_val, files, pkgs, delta_size
        to_path = path.relative_to(working_dir)
        if to_path == Path("."):
            return
        file_hash = _entry_hash(path, to_path)
        entry = (to_path, file_hash)
        # If it's a big file, put it into a separate pkg
        if path.is_file() and path.stat().st_size >= SINGLE_FILE_MINIMAL:
            pkg = _Pkg(
                working_dir,
                ResourceType.WORKING_DIR,
                PackagePrefix.ADD_PREFIX,
                file_hash.hex(),
                [entry],
            )
            pkgs.append(pkg)
        else:  # If it's a directory or just a small file
            if base_files.pop(str(to_path), None) != file_hash.hex():
                files.append(entry)
                hash_val = _xor_bytes(hash_val, file_hash)
                delta_size += path.stat().st_size
            # We also put it into all_files in case the delta is too big and we'd need
            # to change the base
            all_files.append(entry)
            all_hash_val = _xor_bytes(all_hash_val, file_hash)

    # Travel the dir with ray runtime env's api
    _dir_travel(working_dir, [excludes] if excludes else [], handler)

    # If there is no base or the delta is too big, we'll update the base
    if meta is None or delta_size > DELTA_PKG_LIMIT:
        base_pkg = None
        if all_hash_val is not None:
            base_pkg = _Pkg(
                working_dir,
                ResourceType.WORKING_DIR,
                PackagePrefix.BASE_PREFIX,
                all_hash_val.hex(),
                all_files,
            )
        return (base_pkg, None, None, pkgs)

    # Otherwise reuse base pkg
    base_pkg = _get_base_pkg_from_meta(working_dir, meta)
    add_pkg = None
    if hash_val is not None:
        add_pkg = _Pkg(
            working_dir,
            ResourceType.WORKING_DIR,
            PackagePrefix.ADD_PREFIX,
            hash_val.hex(),
            files,
        )
    # If there is some files existing in base, it means this files have been deleted.
    # In this case, we need to generate a del pkg.
    del_pkg = None
    if len(base_files) != 0:
        hash_val = None
        del_file_candidates = [f for (f, _) in base_files.items()]
        del_file_candidates.sort()
        last_item = None
        hasher = hashlib.md5()
        del_files = []
        for del_file in del_file_candidates:
            # del_file_candidates is sorted by file name
            # if one item is a prefix of the next one, it means the next
            # one has been covered. We don't need to add it there.
            # Ex.
            #    a/b/c
            #    a/b/c/d
            # If `a/b/c` is added to be deleted, it means `a/b/c/d` will
            # be deleted. So no need to add `a/b/c/d`
            if last_item is not None and del_file.startswith(last_item):
                continue
            del_files.append((Path(del_file), bytes()))
            hasher.update(del_file.encode())
            hash_val = _xor_bytes(hash_val, hasher.digest())
            last_item = del_file
        assert hash_val is not None
        del_pkg = _Pkg(
            working_dir,
            ResourceType.WORKING_DIR,
            PackagePrefix.DEL_PREFIX,
            hash_val.hex(),
            del_files,
        )
    return (base_pkg, add_pkg, del_pkg, pkgs)


async def _upload_pkg(
    session: aiobotocore.AioSession, token: Any, file_pkg: _Pkg
) -> bool:
    """Upload the package if it doesn't exist in s3"""
    async with _create_s3_client(session, token) as s3:
        # The content hash is encoded in the path of the package, so we don't
        # need to compare the contents of the package. Although, there might be
        # hash collision, given that it's using md5 128bits and we also put
        # files from different orgs into different paths, it won't happen in
        # the real world.
        exists = await _object_exists(s3, token.bucket, token.path + file_pkg.name())
        if exists:
            logger.debug(f"{file_pkg.name()} exists in s3. Skip uploading.")
            return False
        local_pkg = file_pkg.create_tar_file()
        # Print to stdout so that it can be streamed to ray
        logger.debug(f"Uploading runtime env {file_pkg.name()}")
        await _put_object(s3, token.bucket, token.path + file_pkg.name(), local_pkg)
        os.unlink(local_pkg)
        return True


async def _upload_file_pkgs(
    session: aiobotocore.AioSession, token: Any, file_pkgs: List[_Pkg],
) -> None:
    tasks = [_upload_pkg(session, token, pkg) for pkg in file_pkgs]
    _, pending = await asyncio.wait(tasks)
    assert not pending


"""
The following functions are related with package downloading and construction
"""


async def _fetch_dir_pkg(
    session: aiobotocore.AioSession, token: Any, pkg_uri: _PkgURI
) -> None:
    local_path = pkg_uri.local_path()
    with FileLock(str(local_path) + ".lock"):
        if local_path.exists():
            assert local_path.is_dir()
        else:
            async with _create_s3_client(session, token) as s3:
                local_path.mkdir()
                streambody = await _get_object(
                    s3, token.bucket, token.path + pkg_uri.name()
                )
                # TODO (yic) Use streaming mode instead of downloading everything
                with tempfile.NamedTemporaryFile() as tmp_tar:
                    async for data in streambody.iter_chunks():
                        tmp_tar.write(data)
                    tmp_tar.flush()
                    with tarfile.open(tmp_tar.name, mode="r:*") as tar:
                        tar.extractall(local_path)


async def _fetch_uris(
    session: aiobotocore.AioSession, token: Any, pkg_uris: List[_PkgURI],
) -> None:
    tasks = [
        _fetch_dir_pkg(session, token, pkg_uri)
        for pkg_uri in pkg_uris
        if not pkg_uri.is_resource_dir_pkg()
    ]
    if len(tasks) != 0:
        _, pending = await asyncio.wait(tasks)
        assert not pending


def _is_fs_leaf(path: Path) -> bool:
    return path.is_file() or (path.is_dir() and next(path.iterdir(), None) is None)


def _link_fs_children(from_path: Path, to_path: Path) -> None:
    assert from_path.is_dir() and to_path.is_dir()
    for f in from_path.glob("*"):
        (to_path / f.name).symlink_to(f)


def _merge_del(working_dir: Path, del_path: Path) -> None:
    """Recursively iterate through `del_path` and delete it from `working_dir`"""
    assert working_dir.is_dir() and not working_dir.is_symlink()
    for f in del_path.glob("*"):
        to_path = working_dir / f.name
        # If the target is a leaf, we can just delete it
        if _is_fs_leaf(f):
            to_path.unlink()
        else:
            # If the to_path is a symlink, it means it's a link from shared
            # resources. For isolation, we create a new dir and link all
            # children to the physical dir
            if to_path.is_symlink():
                true_path = to_path.resolve()
                to_path.unlink()
                to_path.mkdir()
                _link_fs_children(true_path, to_path)
            # We go one step deeper in the dir here.
            # to_path is working_dir/some_path
            # f is del_path/some_path
            _merge_del(to_path, f)


def _merge_add(working_dir: Path, delta_path: Path) -> None:
    """Recursively iterate through delta_path and merge it to working_dir"""
    assert working_dir.is_dir() and not working_dir.is_symlink()
    for f in delta_path.glob("*"):
        to_path = working_dir / f.name
        # We link it to the target directly if the target doesn't exist
        if not to_path.exists():
            to_path.symlink_to(f)
            continue
        else:
            # If the target exist, it means we might need to overwrite it
            if to_path.is_file() or (to_path.is_dir() and f.is_file()):
                # Working dir is not symlink, which means it's only visible
                # to current job. So we can delete the file directly from it.
                to_path.unlink()
                to_path.symlink_to(f)
            else:
                # If the target is a symlink, we need to create a folder and
                # link all the children to this new created one.
                if to_path.is_symlink():
                    true_path = to_path.resolve()
                    to_path.unlink()
                    to_path.mkdir()
                    _link_fs_children(true_path, to_path)
                _merge_add(to_path, f)


def _construct_from_uris(pkg_uris: List[_PkgURI]) -> Path:
    """Construct the working directory from the pkgs"""

    # Firstly, we split `pkg_uris` into three parts: base, adds and del.
    base_pkg = None
    add_pkg = []
    del_pkg = None
    resource_dir_pkg = None
    for p in pkg_uris:
        if p.is_base_pkg():
            assert base_pkg is None
            base_pkg = p
        elif p.is_add_pkg():
            add_pkg.append(p)
        elif p.is_del_pkg():
            assert del_pkg is None
            del_pkg = p
        elif p.is_resource_dir_pkg():
            assert resource_dir_pkg is None
            resource_dir_pkg = p
        else:
            assert False
    assert resource_dir_pkg is not None
    resource_dir = resource_dir_pkg.local_path()
    # Lock is necessary since multiple workers might be generating working dir at the same time.
    with FileLock(str(resource_dir) + ".lock"):
        if resource_dir.exists():
            assert resource_dir.is_dir()
            logger.debug("Skipping construction of working dir")
            return resource_dir
        # if we only have base_pkg, we'll use it directly
        # otherwise, soft link them to the temp dir
        if base_pkg is not None and len(add_pkg) == 0 and del_pkg is None:
            # We only have working dir, so link it directly
            resource_dir.symlink_to(base_pkg.local_path())
        else:
            resource_dir.mkdir()
            if base_pkg is not None:
                _link_fs_children(base_pkg.local_path(), resource_dir)
        # If there is delete pkg, merge it
        if del_pkg:
            _merge_del(resource_dir, del_pkg.local_path())
        # merge all add pkg
        for pkg in add_pkg:
            _merge_add(resource_dir, pkg.local_path())
        return resource_dir


"""
The following functions are to support working dir caching.
Ray setup script will use these functions instead of open source ones
"""


def rewrite_runtime_env_uris(job_config: "JobConfig") -> None:
    """Rewriting the job_config to calculate the packages needed for this runtime_env.

    In oss ray, the URIs for working are generated in this function.
    All URIs go to gcs for oss ray.
    Here we need to push them to s3 with delta support.
     1. read the base meta
     2. generate the URIs based on the meta and current working dir
     3. write these URIs into job_config so that it can be carried around
    """
    # If the uris has been set, we'll use this directly
    if job_config.runtime_env.get("uris") is not None:
        return
    working_dir = job_config.runtime_env.get("working_dir")
    excludes = job_config.runtime_env.get("excludes") or []
    if working_dir is None:
        return
    working_path = Path(working_dir).absolute()
    assert working_path.is_dir()
    meta = _read_dir_meta(Path(working_dir))
    # get working_dir pkgs
    (base_pkg, add_pkg, del_pkg, file_pkgs) = _calc_pkg_for_working_dir(
        working_path, excludes, meta
    )
    # Put all uris into `uris` field.
    # TODO(architkulkarni): Once runtime env URIs are downloaded in the
    # agent, we will need to modify the below to use the new
    # job_config.set_runtime_env_uris() API introduced in Ray 1.5.0
    job_config.runtime_env["uris"] = [p.uri() for p in file_pkgs]
    job_config.runtime_env["uris"].extend(
        [p.uri() for p in [base_pkg, add_pkg, del_pkg] if p is not None]
    )
    # Generate a random working dir.
    # Here we use a random working dir instead of the hash of the contents is
    # right now writing to working dir is not disabled, so we'd like to generate
    # new working dir instead of sharing it with other jobs.
    working_dir_uri = _PkgURI(
        ResourceType.WORKING_DIR, PackagePrefix.RESOURCE_DIR_PREFIX, uuid.uuid4().hex
    )
    job_config.runtime_env["uris"].append(working_dir_uri.uri())
    # Create a temp file to share infos around to avoid re-calculating the content hash
    # TODO (yic) We need better way to support this
    with tempfile.NamedTemporaryFile(delete=False) as f:
        Path(f.name).write_bytes(pickle.dumps((base_pkg, add_pkg, del_pkg, file_pkgs)))
        job_config.runtime_env["_pkg_contents"] = f.name
    logger.debug("rewriting finished")


def upload_runtime_env_package_if_needed(job_config: "JobConfig") -> None:
    """Uploading the packages to s3. This is an oss ray entry point for working dir.

    It'll check whether the URIs exist in s3 or not and then upload them to s3 if
    the URIs do not exist in S3.
    """
    logger.debug("Start to uploading")
    """If the uris doesn't exist, we'll upload them"""
    uris = job_config.runtime_env.get("uris")
    if not uris:
        return
    if "_skip_uploading" in job_config.runtime_env:
        logger.info("Skipping uploading for preset uris")
        return
    tmp_file = Path(job_config.runtime_env["_pkg_contents"])
    base_pkg, add_pkg, del_pkg, file_pkgs = pickle.loads(tmp_file.read_bytes())
    assert base_pkg is not None or (add_pkg is None and del_pkg is None)
    session = aiobotocore.get_session()
    all_pkgs = [p for p in ([base_pkg, add_pkg, del_pkg] + file_pkgs) if p is not None]
    token = _gen_token()
    if len(all_pkgs) != 0:
        event_loop.run_until_complete(_upload_file_pkgs(session, token, all_pkgs))
    if base_pkg is not None:
        base_pkg.update_meta()
    logger.debug("Uploading finished")
    tmp_file.unlink()
    # Upload successfully. Skip upload if we do retry
    job_config.runtime_env["_skip_uploading"] = True


def ensure_runtime_env_setup(uris: List[str]) -> Optional[str]:
    """Download uris from s3 if it doesn't exist locally."""
    if len(uris) == 0:
        return None
    pkg_uris = [_PkgURI.from_uri(uri) for uri in uris]
    # This funciton only take care of working dir right now.
    pkg_uris = [
        pkg_uri
        for pkg_uri in pkg_uris
        if pkg_uri.resource_type() == ResourceType.WORKING_DIR
    ]
    token = _gen_token()
    session = aiobotocore.get_session()
    task = _fetch_uris(session, token, pkg_uris)
    event_loop.run_until_complete(task)
    working_dir = _construct_from_uris(pkg_uris)
    sys.path.insert(0, str(working_dir))
    return str(working_dir)


"""
The following functions are to support caching conda
"""


async def _handle_cache_miss(
    s3,
    token: Any,
    base_pkg: _PkgURI,
    resource_dir_pkg: _PkgURI,
    conda_env: Dict[str, Any],
) -> None:  # type: ignore
    """In case of caching miss, we'll
        1. install from `conda_env`
        2. use conda_pack to pack it
        3. upload it to s3
    """
    logger.debug("Conda env doesn't exist in s3.")
    # if not exist, install first
    if not resource_dir_pkg.local_path().exists():
        yaml_str = yaml.dump(conda_env)
        logger.debug(f"Install conda env: {yaml_str}")
        with tempfile.NamedTemporaryFile(suffix=".yml") as f:
            Path(f.name).write_text(yaml_str)
            env_dir = Path(
                ray_conda.get_or_create_conda_env(  # type: ignore
                    f.name, resource_dir_pkg.name(), str(Path(PKG_DIR).resolve()),
                )
            )
            assert env_dir == resource_dir_pkg.local_path().resolve()
    # create package and upload it to s3
    with tempfile.NamedTemporaryFile() as f:
        logger.debug(f"Uploading conda package to: {base_pkg.name()}")
        conda_pack.pack(
            prefix=str(resource_dir_pkg.local_path().resolve()),
            ignore_missing_files=True,
            output=f.name,
            compress_level=0,
            format="tar",
            n_threads=4,
            force=True,
        )
        await _put_object(s3, token.bucket, token.path + base_pkg.name(), f.name)


async def _handle_cache_hit(
    s3,
    token: Any,
    base_pkg: _PkgURI,
    resource_dir_pkg: _PkgURI,
    conda_env: Dict[str, Any],
) -> None:  # type: ignore
    """In case of a cache hit, we'll
       1. download it from s3
       2. unpack it
    """
    logger.debug("Conda env has existed in s3.")
    if not resource_dir_pkg.local_path().exists():
        logger.debug("Fetching conda env from s3")
        # fetch it from s3 and unpack
        streambody = await _get_object(s3, token.bucket, token.path + base_pkg.name())
        with tempfile.NamedTemporaryFile() as tmp_tar:
            async for data in streambody.iter_chunks():
                tmp_tar.write(data)
            tmp_tar.flush()
            with tarfile.open(tmp_tar.name, mode="r:*") as tar:
                tar.extractall(resource_dir_pkg.local_path())
        # After downloading it from s3, we need to call conda-unpack
        # explicitly to overwrite all the relative links
        os.system(f"{str(resource_dir_pkg.local_path().resolve())}/bin/conda-unpack")


async def _prepare_conda_env(
    base_pkg: _PkgURI, resource_dir_pkg: _PkgURI, conda_env: Dict[str, Any],
) -> None:
    """Prepare conda env locally.

    In this funciton, it'll checking whether it exists in s3 or not
        - if exists, it'll download it and unpack it
        - if not exist, it'll install it and pack it and upload it

    Args:
        base_pkg: the base package of the conda env in s3
        resource_dir_pkg: the package of local conda env
        conda_env: the config file of conda env.
    Returns:
        None
    """
    token = _gen_token()
    session = aiobotocore.get_session()
    async with _create_s3_client(session, token) as s3:
        exists = await _object_exists(s3, token.bucket, token.path + base_pkg.name())
        if not exists:
            await _handle_cache_miss(s3, token, base_pkg, resource_dir_pkg, conda_env)
        else:
            await _handle_cache_hit(s3, token, base_pkg, resource_dir_pkg, conda_env)


def _get_conda_cache_uris(conda_env: Dict[str, Any]) -> Tuple[_PkgURI, _PkgURI]:
    """
    This function will rewrite conda env into uris
    """
    conda_str = yaml.dump(conda_env)
    pkg_hash = hashlib.md5(conda_str.encode()).hexdigest()
    resource_dir_pkg = _PkgURI(
        ResourceType.CONDA, PackagePrefix.RESOURCE_DIR_PREFIX, pkg_hash
    )
    # Right now base pkg is alway the same as resource pkg since we don't
    # support delta pkgs
    base_pkg = _PkgURI(ResourceType.CONDA, PackagePrefix.BASE_PREFIX, pkg_hash)
    return (resource_dir_pkg, base_pkg)


def _get_conda_dict(
    runtime_env: Dict[str, Any], session_dir: str
) -> Optional[Dict[Any, Any]]:
    """This function will call oss ray functions to construct
    the conda dict. But in addition to that, it'll also do the following things:
       - inject anyscale automatically
    If ANYSCALE_USER_WHEEL exists in os environment, it'll inject that, otherwise
    anyscale version in the cluster will be used.
    """

    from ray.workers.setup_runtime_env import (
        current_ray_pip_specifier,
        get_conda_dict,
        inject_dependencies,
    )

    # The reason we don't use session_dir here is that, session dir
    # always change which fail caching miss. Hard code here to put
    # data into /tmp/ray so that it won't change.
    conda_env = get_conda_dict(runtime_env, session_dir)
    if conda_env is None:
        return None
    # TODO(yic/archit): This code is copied from OSS ray.
    #    Find a better way to import it/make it pluggable from ray to avoid
    #    duplicate code.
    # https://github.com/ray-project/ray/blob/0dcd99647595c2e5e7872dd860b93b65cad1f32c/python/ray/workers/setup_runtime_env.py#L49-L54
    # Need to switch to ray function later.
    py_version = ".".join(map(str, sys.version_info[:3]))  # like 3.6.10
    ray_pip = current_ray_pip_specifier()
    extra_pip_dependencies = []
    if "ANYSCALE_USER_WHEEL" in os.environ:
        logger.debug(f"Using anyscale wheel {os.environ['ANYSCALE_USER_WHEEL']}")
        extra_pip_dependencies.append(os.environ["ANYSCALE_USER_WHEEL"])
    else:
        import anyscale

        extra_pip_dependencies.append(f"anyscale=={anyscale.__version__}")
    if ray_pip and not runtime_env.get("_skip_inject_ray"):
        extra_pip_dependencies.append(ray_pip)
        extra_pip_dependencies.append("ray[default]")
    return inject_dependencies(conda_env, py_version, extra_pip_dependencies)


def _get_conda_env_path(runtime_env: Dict[str, Any]) -> Optional[str]:
    """This function will prepare the conda environment and return the environment
    path. It first generates the conda env dict with the anyscale package injected
    automatically to requirements. If it turns out to be cached it is downloaded
    directly from S3, otherwise, it is installed locally and uploaded to S3 so
    it can be reused in the future.
    """

    conda_raw = runtime_env.get("conda")
    if isinstance(conda_raw, str):
        return conda_raw
    else:
        conda_env = _get_conda_dict(runtime_env, "/tmp/ray")
        if conda_env is None:
            return None
        resource_dir_pkg, base_pkg = _get_conda_cache_uris(conda_env)
        local_path = str(resource_dir_pkg.local_path())
        lock_file = local_path + ".lock"
        done_file = local_path + ".done"
        # If there are multiple workers starting to install the same conda env
        # we only want one to install it and block others. Once installed
        # the rest workers will just reuse the existing env.
        with FileLock(lock_file):
            if not Path(done_file).exists():
                if Path(local_path).exists():
                    shutil.rmtree(local_path)
                event_loop.run_until_complete(
                    _prepare_conda_env(base_pkg, resource_dir_pkg, conda_env)
                )
                Path(local_path + ".done").touch()
        return str(resource_dir_pkg.local_path().resolve())


def _update_env_vars(runtime_env: Dict[str, Any]) -> None:
    """This function will update the environment variables of the current
    process based on the env_vars field of the runtime_env argument.
    """
    if runtime_env.get("env_vars"):
        env_vars = runtime_env["env_vars"]
        os.environ.update(env_vars)


def worker_setup_func(input_args: Any) -> None:
    """This func will install conda env if not exists. And it'll activate it.

    This function is only used for ray<1.5.
    conda env should be:
      {
          uris: [] // s3 pkgs. It can be base_/add_
      }
    We'll use ensure_runtime_env_setup to prepare the local dir and we'll use
    code from oss ray to activate it.
    """
    # remaining_args contains the arguments to the original worker command,
    # minus the python executable, e.g. default_worker.py --node-ip-address=...
    logger.debug("Start to run shim process")
    # To make it compatible with shim process in oss ray
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--serialized-runtime-env",
        type=str,
        help="the serialized parsed runtime env dict",
    )

    parser.add_argument(
        "--session-dir", type=str, help="the directory for the current session"
    )
    args, remaining_args = parser.parse_known_args(args=input_args)

    commands = []
    runtime_env = json.loads(args.serialized_runtime_env or "{}")

    conda_path = _get_conda_env_path(runtime_env)
    if conda_path is not None:
        commands += ray_conda.get_conda_activate_commands(conda_path)  # type: ignore

    # After activating the conda environment, "python" will point to the
    # correct python executable for that environment.  If no conda environment
    # is specified, we should just use the current python executable.
    py_executable: str = "python" if conda_path is not None else sys.executable

    commands += [" ".join([f"exec {py_executable}"] + remaining_args)]
    command_separator = " && "
    command_str = command_separator.join(commands)
    logger.debug("Shim process setup finished.")

    _update_env_vars(runtime_env)

    os.execvp("bash", ["bash", "-c", command_str])


def setup_runtime_env(runtime_env: dict, session_dir):
    """Used for Ray 1.5+.  Sets up the given runtime environment."""

    from ray.workers.pluggable_runtime_env import RuntimeEnvContext

    conda_env_name = _get_conda_env_path(runtime_env)
    if conda_env_name is not None:
        return RuntimeEnvContext(conda_env_name)
    return RuntimeEnvContext()


"""
The following functions are anyscale related functions
"""


def register_runtime_env(env: Dict[str, Any]) -> List[str]:
    from ray.job_config import JobConfig

    job_config = JobConfig(runtime_env=env)
    rewrite_runtime_env_uris(job_config)
    upload_runtime_env_package_if_needed(job_config)
    uris = job_config.runtime_env["uris"]
    assert isinstance(uris, list)
    return uris


def runtime_env_setup() -> None:
    import ray
    import ray._private.runtime_env as ray_runtime_env

    ray_runtime_env.rewrite_runtime_env_uris = rewrite_runtime_env_uris
    ray_runtime_env.upload_runtime_env_package_if_needed = (
        upload_runtime_env_package_if_needed
    )
    ray_runtime_env.ensure_runtime_env_setup = ensure_runtime_env_setup

    import ray.ray_constants as ray_constants

    # TODO(architkulkarni): Refactor runtime_env so we have a stable interface
    # between OSS and product.
    if ray.__version__[:3] == "1.4":
        ray_constants.DEFAULT_WORKER_SETUP_HOOK = (
            "anyscale.utils.runtime_env.worker_setup_func"
        )
    elif ray.__version__[:3] in ["1.5", "1.6", "2.0"]:
        import ray.workers.setup_runtime_env as ray_setup_runtime_env

        ray_setup_runtime_env.setup_runtime_env = setup_runtime_env
        ray_constants.DEFAULT_RUNTIME_ENV_SETUP_HOOK = (
            "anyscale.utils.runtime_env.setup_runtime_env"
        )
    else:
        raise ValueError(
            "S3 caching for runtime envs is only supported on "
            "Ray 1.5 and 1.6.  Current Ray version: "
            f"{ray.__version__}."
        )
