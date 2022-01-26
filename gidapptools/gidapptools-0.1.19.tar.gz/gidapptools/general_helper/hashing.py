"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
from typing import TYPE_CHECKING, Callable
from hashlib import blake2b
from pathlib import Path

# * Type-Checking Imports --------------------------------------------------------------------------------->
if TYPE_CHECKING:
    from gidapptools.types import PATH_TYPE

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


# FILE_HASH_INCREMENTAL_THRESHOLD: int = 104857600  # 100mb
FILE_HASH_INCREMENTAL_THRESHOLD: int = 52428800  # 50mb


def file_hash(in_file: "PATH_TYPE", hash_algo: Callable = blake2b) -> str:
    in_file = Path(in_file)
    if not in_file.is_file():
        raise OSError(f"The path {in_file.as_posix()!r} either does not exist or is a Folder.")
    if in_file.stat().st_size > FILE_HASH_INCREMENTAL_THRESHOLD:
        _hash = hash_algo(usedforsecurity=False)
        with in_file.open("rb", buffering=FILE_HASH_INCREMENTAL_THRESHOLD // 4) as f:
            for chunk in f:
                _hash.update(chunk)
        return _hash.hexdigest()

    return hash_algo(in_file.read_bytes(), usedforsecurity=False).hexdigest()


# region[Main_Exec]

if __name__ == '__main__':
    print(file_hash(Path(r"D:\Dropbox\hobby\Modding\Programs\Github\My_Repos\Antistasi_Logbook\antistasi_logbook\storage\storage.db")))

# endregion[Main_Exec]
