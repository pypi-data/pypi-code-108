import os
import json
import shutil
from pathlib import Path

import fsos


DEFAULT_FSOS_NAME = ".fsos"
FSOS_VERSION_KEY = "fsos_version"
FSOS_BUCKET_KEY = "buckets"


def _get_version() -> dict:
    return {FSOS_VERSION_KEY: fsos.__version__}


def _set_db(db: dict) -> None:
    fsos._FSOS_DB = db


def _get_db() -> dict:
    return fsos._FSOS_DB


def _check_fsos(ROOT_PATH: str) -> bool:
    return Path(os.path.join(ROOT_PATH), DEFAULT_FSOS_NAME).exists()


def _create_fsos(ROOT_PATH: str) -> bool:
    Path(ROOT_PATH).mkdir(parents=True, exist_ok=True)
    _set_db({**_get_version(), **{FSOS_BUCKET_KEY: {}}})
    _update_fsos(ROOT_PATH)

    return True


def _update_fsos(ROOT_PATH: str) -> bool:
    with open(Path(os.path.join(ROOT_PATH), DEFAULT_FSOS_NAME), "w") as out:
        json.dump(_get_db(), out)

    return True


def _load_fsos(ROOT_PATH: str) -> bool:
    with open(Path(os.path.join(ROOT_PATH), DEFAULT_FSOS_NAME), "r") as out:
        temp_db = None
        json.load(out, temp_db)
        _set_db(temp_db)

    return True


def _create_folder(ROOT_PATH: str, subdir: str) -> bool:
    Path(ROOT_PATH, subdir).mkdir()
    return True


def _remove_folder(ROOT_PATH: str, subdir: str) -> bool:
    Path(ROOT_PATH, subdir).rmdir()
    return True


def _copy_file(from_path: str, to_path: str) -> bool:
    shutil.copy(Path(from_path), Path(to_path))
    return True


def _remove_file(file_path: str) -> bool:
    Path(file_path).unlink()
    return True
