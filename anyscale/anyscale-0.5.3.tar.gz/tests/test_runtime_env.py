# type: ignore

import copy
import os
from pathlib import Path
import random
import shutil
import subprocess
import sys
import tempfile
from typing import Any, AsyncGenerator, Dict, Generator, Optional, Set, Tuple
from unittest.mock import Mock

import pytest
import ray

import anyscale
from anyscale.utils.ray_conda import get_conda_activate_commands
from anyscale.utils.runtime_env import (
    _calc_pkg_for_working_dir,
    _get_conda_dict,
    _get_conda_env_path,
    _read_dir_meta,
    ensure_runtime_env_setup,
    rewrite_runtime_env_uris,
    upload_runtime_env_package_if_needed,
)


@pytest.fixture(scope="function")
def random_working_dir() -> Generator[Tuple[Path, Set[Path], Set[Path]], None, None]:
    """This fixture is trying to randomly build a working directory have big and small files.
    We'll use this working_dir to test uploading/downloading
    """
    anyscale.utils.runtime_env.SINGLE_FILE_MINIMAL = 256 * 1024  # 256kb
    os.environ["ANYSCALE_DEBUG"] = "1"
    with tempfile.TemporaryDirectory() as tmp_dir:
        item_num = 0
        root = Path(tmp_dir) / "test"
        root.mkdir()
        big_files = set()
        small_files = set()
        with tempfile.NamedTemporaryFile(dir=root, delete=False) as f:
            f.write(b"A" * (anyscale.utils.runtime_env.SINGLE_FILE_MINIMAL))
            big_files.add(Path(f.name).relative_to(root))

        for _ in range(5):
            with tempfile.NamedTemporaryFile(dir=root, delete=False) as f:
                f.write(b"A" * (anyscale.utils.runtime_env.SINGLE_FILE_MINIMAL - 1))
                small_files.add(Path(f.name).relative_to(root))

        def construct(path: Path, depth: int = 0) -> None:
            nonlocal item_num
            nonlocal big_files
            nonlocal root
            path.mkdir(parents=True, exist_ok=True)
            dir_num = random.randint(0, 5)
            file_num = random.randint(0, 5)
            if path != root:
                small_files.add(path.relative_to(root))
            if (
                depth > 8
                or item_num > 1000
                or (dir_num == 0 and file_num == 0 and depth != 0)
            ):
                return
            for _ in range(dir_num):
                tmp_dir = tempfile.mkdtemp(dir=path)
                dir_path = Path(tmp_dir)
                item_num += 1
                construct(dir_path, depth + 1)

            if item_num > 1000:
                return

            for _ in range(file_num):
                with tempfile.NamedTemporaryFile(dir=path, delete=False) as f:
                    data_size = 2 ** random.choice(range(10)) * 1024
                    f.write(b"A" * data_size)
                    if data_size >= anyscale.utils.runtime_env.SINGLE_FILE_MINIMAL:
                        big_files.add(Path(f.name).relative_to(root))
                    else:
                        small_files.add(Path(f.name).relative_to(root))
                item_num += 1

        construct(root)

        yield (root, big_files, small_files)


def test_get_conda_dict() -> None:
    """This test is to check whether anyscale/ray[default]/python version
    got injected correctly in anyscale product code path.
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        with open("requirements.txt", "w") as t:
            t.write(
                """pip-install-test==0.5
ray"""
            )
        import ray.workers.setup_runtime_env

        current_ray_pip_specifier = Mock()
        current_ray_pip_specifier.return_value = "ray==test"
        ray.workers.setup_runtime_env.current_ray_pip_specifier = (
            current_ray_pip_specifier
        )
        py_version = ".".join(map(str, sys.version_info[:3]))
        test_wheel = "ANYSCALE_TEST_WHEEL_ADDR"
        # With this flag on, it'll use user wheel for anyscale
        # this is useful for testing
        os.environ["ANYSCALE_USER_WHEEL"] = test_wheel
        pip_txt = "test1\test2"
        runtime_env = {
            "working_dir": ".",
            "pip": pip_txt,
        }

        conda_dict = _get_conda_dict(runtime_env, tmp_dir)
        deps = conda_dict["dependencies"]
        assert deps[0] == "pip"
        # anyscale is always put at the beginning
        pips = deps[1]["pip"]
        assert len(pips) == 4
        pips[3] = Path(pips[3].split()[1]).read_text()
        assert pips == [test_wheel, "ray==test", "ray[default]", pip_txt]
        assert deps[2] == f"python={py_version}"

        # Test the case when it's off and use anyscale.__version__
        # automatically
        os.environ.pop("ANYSCALE_USER_WHEEL")
        conda_dict = _get_conda_dict(runtime_env, tmp_dir)
        deps = conda_dict["dependencies"]
        assert deps[0] == "pip"
        pips = deps[1]["pip"]
        assert len(pips) == 4
        pips[3] = Path(pips[3].split()[1]).read_text()
        assert pips == [
            f"anyscale=={anyscale.__version__}",
            "ray==test",
            "ray[default]",
            pip_txt,
        ]
        assert deps[2] == f"python={py_version}"


def test_split_no_base(random_working_dir: Tuple[Path, Set[Path], Set[Path]]) -> None:
    # Test splitting when there is no base dir
    (working_dir, big_files, small_files) = random_working_dir
    assert _read_dir_meta(working_dir, True) is None
    (base_pkg, add_pkg, del_pkg, file_pkgs) = _calc_pkg_for_working_dir(
        working_dir, [], None
    )
    # check pkgs are good
    assert len(file_pkgs) == len(big_files)
    files = set()
    for pkg in file_pkgs:
        assert len(pkg._contents) == 1
        files.add(pkg._contents[0][0])
    assert big_files == files
    assert del_pkg is None
    assert add_pkg is None
    assert base_pkg is not None
    files = {u[0] for u in base_pkg._contents}
    assert files == small_files

    # Update meta and check it
    base_pkg.update_meta()
    meta = _read_dir_meta(working_dir, True)
    assert meta is not None
    assert meta["hash_val"] == base_pkg._uri._hash_val
    contents = [(Path(k), bytes.fromhex(v)) for (k, v) in meta["files"].items()]
    contents.sort()
    base_pkg._contents.sort()
    assert contents == base_pkg._contents
    # Re-split the working_dir, but now with base pkg
    new_base_pkg, new_add_pkg, new_del_pkg, new_file_pkgs = _calc_pkg_for_working_dir(
        working_dir, [], meta
    )
    assert new_base_pkg == base_pkg
    assert new_add_pkg == add_pkg
    assert new_del_pkg == del_pkg
    assert new_file_pkgs == file_pkgs


def test_split_with_base_del(
    random_working_dir: Tuple[Path, Set[Path], Set[Path]]
) -> None:
    # Try to split the working dir without base
    (working_dir, big_files, small_files_set) = random_working_dir
    _calc_pkg_for_working_dir(working_dir, [], None)
    (base_pkg, _, _, file_pkgs) = _calc_pkg_for_working_dir(working_dir, [], None)
    assert base_pkg is not None
    # Update the base
    base_pkg.update_meta()
    # We'll delete files to test the del pkg
    del_big_file = random.choice(list(big_files))
    file_pkgs = [f for f in file_pkgs if f._contents[0][0] != del_big_file]
    (working_dir / del_big_file).unlink()
    (new_base_pkg, new_add_pkg, new_del_pkg, new_file_pkgs) = _calc_pkg_for_working_dir(
        working_dir, [], _read_dir_meta(working_dir, True)
    )
    # Since this is a big file deletion, so only file_pkgs will be impacted
    assert new_add_pkg is None
    assert new_del_pkg is None
    assert base_pkg == new_base_pkg
    assert file_pkgs == new_file_pkgs
    small_files = list(small_files_set)
    random.shuffle(small_files)
    del_small_file = None
    for small_file in small_files:
        p = working_dir / small_file
        if not p.is_dir() or next(p.iterdir(), None) is None:
            del_small_file = small_file
            break
    small_files.remove(del_small_file)
    # Now delete a small file
    p = working_dir / del_small_file
    del_bytes = 0
    if p.is_dir():
        p.rmdir()
    else:
        del_bytes += p.stat().st_size
        p.unlink()
    # We delete a small file, which will generate a del pkg
    (new_base_pkg, new_add_pkg, new_del_pkg, new_file_pkgs) = _calc_pkg_for_working_dir(
        working_dir, [], _read_dir_meta(working_dir, True)
    )
    assert new_add_pkg is None
    assert base_pkg == new_base_pkg
    assert file_pkgs == new_file_pkgs
    assert new_del_pkg is not None
    assert new_del_pkg._contents[0][0] == Path(del_small_file)


def test_split_with_base_update(
    random_working_dir: Tuple[Path, Set[Path], Set[Path]]
) -> None:
    # We now test the split for base update cases
    anyscale.utils.runtime_env.DELTA_PKG_LIMIT = 1024 * 1024  # 1mb
    (working_dir, _, small_files_set) = random_working_dir
    _calc_pkg_for_working_dir(working_dir, [], None)
    (base_pkg, _, _, file_pkgs) = _calc_pkg_for_working_dir(working_dir, [], None)
    assert base_pkg is not None
    base_pkg.update_meta()

    # update a small file
    small_files = list(small_files_set)
    random.shuffle(small_files)
    updated_bytes = 0
    while True:
        p = working_dir / small_files.pop()
        if p.is_dir():
            continue
        val = b"B" * p.stat().st_size
        with p.open("wb") as f:
            f.write(val)
        updated_bytes += p.stat().st_size
        break
    (new_base_pkg, new_add_pkg, new_del_pkg, new_file_pkgs) = _calc_pkg_for_working_dir(
        working_dir, [], _read_dir_meta(working_dir, True)
    )
    assert new_base_pkg == base_pkg
    assert new_del_pkg is None
    assert new_file_pkgs == file_pkgs
    assert new_add_pkg is not None
    assert len(new_add_pkg._contents) == 1
    assert working_dir / new_add_pkg._contents[0][0] == p

    # update a lot small files to trigger updating base
    while updated_bytes <= anyscale.utils.runtime_env.DELTA_PKG_LIMIT:
        p = working_dir / small_files.pop()
        if p.is_dir():
            continue
        val = b"B" * p.stat().st_size
        with p.open("wb") as f:
            f.write(val)
        updated_bytes += p.stat().st_size
    (new_base_pkg, new_add_pkg, new_del_pkg, new_file_pkgs) = _calc_pkg_for_working_dir(
        working_dir, [], _read_dir_meta(working_dir, True)
    )
    assert new_base_pkg != base_pkg
    assert new_add_pkg is None
    assert new_del_pkg is None
    assert new_file_pkgs == file_pkgs


def test_split_with_all_big_files() -> None:
    anyscale.utils.runtime_env.SINGLE_FILE_MINIMAL = 256 * 1024  # 256kb
    with tempfile.TemporaryDirectory() as tmp_dir:
        for _ in range(10):
            with tempfile.NamedTemporaryFile(dir=tmp_dir, delete=False) as f:
                f.write(b"A" * (anyscale.utils.runtime_env.SINGLE_FILE_MINIMAL + 1))
        (
            new_base_pkg,
            new_add_pkg,
            new_del_pkg,
            new_file_pkgs,
        ) = _calc_pkg_for_working_dir(
            Path(tmp_dir), [], _read_dir_meta(Path(tmp_dir), True)
        )
        assert new_base_pkg is None
        assert new_add_pkg is None
        assert new_del_pkg is None
        assert len(new_file_pkgs) == 10


def dir_hash(path: Optional[str]) -> int:
    s = 0
    if path is None:
        return s
    excluded = [os.path.join(path, anyscale.utils.runtime_env.DIR_META_FILE_NAME)]
    for root, dirs, files in os.walk(
        path, topdown=True, onerror=None, followlinks=True
    ):
        for f in files:
            curr_path = Path(root) / f
            if str(curr_path) in excluded:
                continue
            s += sum(curr_path.read_bytes())
            s += sum(str(curr_path.relative_to(Path(path))).encode())
        for d in dirs:
            curr_path = Path(root) / d
            s += sum(str(curr_path.relative_to(Path(path))).encode())
    return s


class MockS3Meta:
    db: Dict[str, Any] = {}
    put_cnt: int = 0
    get_cnt: int = 0


def mock_setup_s3_related_funcs() -> MockS3Meta:
    meta = MockS3Meta()

    async def _object_exists(s3: Any, bucket: str, key: str) -> bool:
        nonlocal meta
        return key in meta.db

    async def _put_object(s3: Any, bucket: str, key: str, p: str) -> None:
        nonlocal meta
        meta.put_cnt += 1
        meta.db[key] = Path(p).read_bytes()

    class StreamBody:
        def __init__(self, data: bytes):
            self._data = data

        async def iter_chunks(self) -> AsyncGenerator[bytes, None]:
            n = 64
            for i in range(0, len(self._data), n):
                yield self._data[i : i + n]

    async def _get_object(s3: Any, bucket: str, key: str) -> StreamBody:
        nonlocal meta
        meta.get_cnt += 1
        return StreamBody(meta.db.get(key, b""))

    def _gen_token() -> Any:
        class Token:
            def __init__(self) -> None:
                self.region = "west"
                self.aws_access_key_id = ""
                self.aws_secret_access_key = ""
                self.aws_session_token = ""
                self.bucket = "test"
                self.path = "/"

        return Token()

    # Inject s3 related functions
    anyscale.utils.runtime_env._object_exists = _object_exists
    anyscale.utils.runtime_env._put_object = _put_object
    anyscale.utils.runtime_env._get_object = _get_object
    anyscale.utils.runtime_env._gen_token = _gen_token
    return meta


def test_split_with_base_del_2() -> None:
    with tempfile.TemporaryDirectory() as d:
        pkg_dir = Path(d) / "pkg_dir"
        pkg_dir.mkdir()
        working_dir = Path(d) / "working_dir"
        working_dir.mkdir()

        (working_dir / "sub").mkdir()
        (working_dir / "sub" / "text").write_text("a" * 128)
        (working_dir / "sub2").mkdir()
        (working_dir / "sub2" / "text").write_text("a" * 128)

        _calc_pkg_for_working_dir(working_dir, [], None)
        base_pkg = _calc_pkg_for_working_dir(working_dir, [], None)[0]
        assert base_pkg is not None
        # Update the base
        base_pkg.update_meta()
        (working_dir / "sub" / "text").unlink()
        (working_dir / "sub2" / "text").unlink()
        (working_dir / "sub2").rmdir()

        (_, new_add_pkg, new_del_pkg, new_file_pkgs,) = _calc_pkg_for_working_dir(
            working_dir, [], _read_dir_meta(working_dir, True)
        )

        assert new_add_pkg is None
        assert len(new_file_pkgs) == 0
        assert new_del_pkg is not None
        assert len(new_del_pkg._contents) == 2
        assert {str(c[0]) for c in new_del_pkg._contents} == {"sub/text", "sub2"}


def test_e2e(random_working_dir: Tuple[Path, Set[Path], Set[Path]]) -> None:
    with tempfile.TemporaryDirectory() as d:
        anyscale.utils.runtime_env.PKG_DIR = d
        meta = mock_setup_s3_related_funcs()
        (working_dir, big_files, small_files_set) = random_working_dir

        def run(working_dir: str = str(working_dir)) -> Optional[str]:
            job_config = ray.job_config.JobConfig(
                runtime_env={"working_dir": working_dir}
            )
            rewrite_runtime_env_uris(job_config)
            upload_runtime_env_package_if_needed(job_config)
            uris = job_config.runtime_env.get("uris")
            assert uris is not None
            return ensure_runtime_env_setup(uris)

        assert dir_hash(str(working_dir)) == dir_hash(run())
        old_put_cnt, old_get_cnt = meta.put_cnt, meta.get_cnt
        assert dir_hash(str(working_dir)) == dir_hash(run())
        assert old_put_cnt == meta.put_cnt
        assert old_get_cnt == meta.get_cnt

        del_big_file = random.choice(list(big_files))
        (working_dir / del_big_file).unlink()
        assert dir_hash(str(working_dir)) == dir_hash(run())
        assert old_put_cnt == meta.put_cnt
        assert old_get_cnt == meta.get_cnt

        small_files = list(small_files_set)
        random.shuffle(small_files)
        updated_bytes = 0
        while True:
            p = working_dir / small_files.pop()
            if p.is_dir():
                continue
            val = b"B" * p.stat().st_size
            with p.open("wb") as f:
                f.write(val)
            updated_bytes += p.stat().st_size
            break
        assert dir_hash(str(working_dir)) == dir_hash(run())
        assert old_put_cnt + 1 == meta.put_cnt
        assert old_get_cnt + 1 == meta.get_cnt

        # update a lot small files to trigger updating base
        anyscale.utils.runtime_env.DELTA_PKG_LIMIT = 1024 * 1024  # 1mb
        while updated_bytes <= anyscale.utils.runtime_env.DELTA_PKG_LIMIT:
            p = working_dir / small_files.pop()
            if p.is_dir():
                continue
            val = b"B" * p.stat().st_size
            with p.open("wb") as f:
                f.write(val)
            updated_bytes += p.stat().st_size
        old_put_cnt, old_get_cnt = meta.put_cnt, meta.get_cnt
        assert dir_hash(str(working_dir)) == dir_hash(run())
        assert old_get_cnt + 1 == meta.get_cnt
        assert old_put_cnt + 1 == meta.put_cnt

        # now add some files
        with tempfile.NamedTemporaryFile(dir=working_dir, delete=False) as f1:
            f1.write(b"A" * (anyscale.utils.runtime_env.SINGLE_FILE_MINIMAL - 1))
        with tempfile.NamedTemporaryFile(dir=working_dir, delete=False) as f2:
            f2.write(b"A" * (anyscale.utils.runtime_env.SINGLE_FILE_MINIMAL + 1))
        old_put_cnt, old_get_cnt = meta.put_cnt, meta.get_cnt
        assert dir_hash(str(working_dir)) == dir_hash(run())
        assert old_get_cnt + 2 == meta.get_cnt
        assert old_put_cnt + 2 == meta.put_cnt

        # Now create a new dir with all big files
        with tempfile.TemporaryDirectory() as big_tmp:
            for _ in range(10):
                with tempfile.NamedTemporaryFile(dir=big_tmp, delete=False) as f:
                    f.write(b"A" * (anyscale.utils.runtime_env.SINGLE_FILE_MINIMAL + 1))
            assert dir_hash(big_tmp) == dir_hash(run(big_tmp))

        # Now create a new dir with all small files
        with tempfile.TemporaryDirectory() as big_tmp:
            for _ in range(10):
                with tempfile.NamedTemporaryFile(dir=big_tmp, delete=False) as f:
                    f.write(b"A" * (anyscale.utils.runtime_env.SINGLE_FILE_MINIMAL - 1))
            assert dir_hash(big_tmp) == dir_hash(run(big_tmp))

        # Now create a new dir with no files
        with tempfile.TemporaryDirectory() as big_tmp:
            assert dir_hash(big_tmp) == dir_hash(run(big_tmp))


@pytest.mark.skipif(True, reason="Need pinned ray updates to test it")
@pytest.mark.parametrize("env_type", ["pip", "conda"])
def test_client_setver_env_prep_e2e(env_type: str) -> None:
    with tempfile.TemporaryDirectory() as d:
        anyscale.utils.runtime_env.PKG_DIR = d
        assert _get_conda_env_path({"conda": "test_env"}, d) == "test_env"
        from anyscale.connect import REQUIRED_RAY_COMMIT

        ray_release = "master/" + REQUIRED_RAY_COMMIT
        if env_type == "conda":
            input_runtime_env = {
                "conda": {
                    "dependencies": [
                        "pip",
                        {
                            "pip": [
                                "pip-install-test==0.5",
                                "opentelemetry-api==1.1.0",
                                "opentelemetry-sdk==1.1.0",
                            ]
                        },
                    ]
                },
                "_ray_release": ray_release,
            }
        else:
            input_runtime_env = {
                "pip": """pip-install-test==0.5
opentelemetry-api==1.1.0
opentelemetry-sdk==1.1.0""",
                "_ray_release": ray_release,
            }

        meta = mock_setup_s3_related_funcs()

        # conda pkg created
        with pytest.raises(ModuleNotFoundError):
            # Ensure pip-install-test is not installed on the test machine
            import pip_install_test  # noqa
        conda_path = _get_conda_env_path(copy.deepcopy(input_runtime_env), d)
        assert conda_path is not None
        cmds = get_conda_activate_commands(conda_path)
        cmds.append("python -c 'import pip_install_test; print(0)'")
        out = subprocess.run(  # noqa: B1
            " && ".join(cmds),
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ).stdout
        assert out.split()[-1] == b"0"

        old_get_cnt, old_put_cnt = meta.get_cnt, meta.put_cnt
        # Re-run it and it'll skip downloading
        conda_path = _get_conda_env_path(copy.deepcopy(input_runtime_env), d)
        assert old_get_cnt == meta.get_cnt
        assert old_put_cnt == meta.put_cnt
        # Delete it and set it up from caching
        shutil.rmtree(conda_path)
        old_get_cnt, old_put_cnt = meta.get_cnt, meta.put_cnt
        conda_path = _get_conda_env_path(copy.deepcopy(input_runtime_env), d)
        assert old_put_cnt == meta.put_cnt
        assert old_get_cnt + 1 == meta.get_cnt
        out = subprocess.run(  # noqa: B1
            " && ".join(cmds),
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ).stdout
        assert out.split()[-1] == b"0"
