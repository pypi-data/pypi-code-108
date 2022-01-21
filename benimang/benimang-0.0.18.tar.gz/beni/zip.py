from pathlib import Path
from typing import Callable
from zipfile import ZIP_DEFLATED, ZipFile

from beni import getpath, list_path, make_dirs


def zipFile(to_file: Path, path_dict: dict[str, Path]):
    make_dirs(to_file.parent)
    with ZipFile(to_file, 'w', ZIP_DEFLATED) as f:
        for fname in sorted(path_dict.keys()):
            file = path_dict[fname]
            if file.is_file():
                f.write(file, fname)


def zipfolder(to_file: Path, dir: Path, filter_func: Callable[[Path], bool] | None = None):
    ary = list_path(dir, True)
    if filter_func:
        ary = list(filter(filter_func, ary))
    zipFile(to_file, {str(x.relative_to(dir)): x for x in ary})


def zipextract(file: Path, to_dir: Path | None = None):
    to_dir = to_dir or file.parent
    with ZipFile(file) as f:
        for subFile in sorted(f.namelist()):
            try:
                # zipfile 代码中指定了cp437，这里会导致中文乱码
                encodeSubFile = subFile.encode('cp437').decode('gbk')
            except:
                encodeSubFile = subFile
            f.extract(subFile, to_dir)
            # 处理压缩包中的中文文件名在windows下乱码
            if subFile != encodeSubFile:
                toFile = getpath(to_dir, encodeSubFile)
                getpath(to_dir, subFile).rename(toFile)
