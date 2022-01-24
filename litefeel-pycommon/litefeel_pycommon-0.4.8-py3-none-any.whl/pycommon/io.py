"some function for io"

import os
import shutil


def makedirs(filename, isfile=False):
    "like os.makedirs, can pass a filename"
    dirname = os.path.dirname(filename) if isfile else filename
    if dirname and not os.path.exists(dirname):
        os.makedirs(dirname)


def write_file(filename, data, mode=None, encoding="utf-8", newline=None, append=False):
    "save data to file"
    makedirs(filename, isfile=True)
    if not mode:
        mode = "w" if isinstance(data, str) else "wb"
    if append:
        mode = mode.replace("w", "a")
    if isinstance(data, (bytearray, bytes)):
        encoding = None
        newline = None
    with open(filename, mode=mode, encoding=encoding, newline=newline) as f:
        f.write(data)


def read_file(filename, isbin=False, encoding="utf-8"):
    "read data from file"
    mode = "rb" if isbin else "r"
    with open(filename, mode=mode, encoding=encoding) as f:
        return f.read()


def write_lines(
    filename,
    lines: list[str],
    encoding="utf-8",
    newline="\n",
    newlineinlines=False,
    append=False,
):
    "save lines to file"
    mode = "at" if append else "wt"
    with open(filename, mode=mode, encoding=encoding) as f:
        if newlineinlines:
            f.writelines(lines)
        else:
            for line in lines:
                f.write(line)
                f.write(newline)


def read_lines(filename, encoding="utf-8", keepends=False):
    "read lines from file"
    with open(filename, mode="r", encoding=encoding) as f:
        if keepends:
            return f.readlines()
        else:
            return f.read().splitlines(keepends)


def copy_file(src, dst):
    makedirs(dst, True)
    shutil.copyfile(src, dst)


def check_encoding(filename: str, *encodings: str):
    "check encoding on file"
    for encoding in encodings:
        with open(filename, mode="r", encoding=encoding) as f:
            try:
                f.read()
                return encoding
            except UnicodeDecodeError:
                pass
    return None
