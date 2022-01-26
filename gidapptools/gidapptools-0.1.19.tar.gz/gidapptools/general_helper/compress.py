"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
import shutil
from typing import TYPE_CHECKING
from pathlib import Path
from zipfile import ZIP_LZMA, ZipFile
from multiprocessing import Process

# * Third Party Imports --------------------------------------------------------------------------------->

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


def compress_file(source: "PATH_TYPE", target: "PATH_TYPE", suffix: str = '.zip'):
    source = Path(source)

    target = Path(target)
    zip_target = target.with_suffix(suffix)
    with ZipFile(zip_target, "w", ZIP_LZMA) as zippy:
        zippy.write(source, source.name)


def compress_in_process(source: "PATH_TYPE", target: "PATH_TYPE", suffix: str = '.zip'):
    process = Process(daemon=False, target=compress_file, kwargs={"source": source, "target": target})
    process.start()
    return process


# region[Main_Exec]
if __name__ == '__main__':
    pass

# endregion[Main_Exec]
