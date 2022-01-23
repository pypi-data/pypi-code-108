# -*- coding: utf-8 -*-
# Copyright (c) 2022, KarjaKAK
# All rights reserved.

import stat
import ctypes
import os
import argparse
from enum import IntEnum, unique
from pprint import pprint
from pathlib import Path
from functools import wraps


def excp(f):
    """Exception decorator"""

    @wraps(f)
    def inner(*args, **kwargs):
        try:
            if fn := f(*args, **kwargs):
                return fn
            del fn
        except Exception as e:
            trc = str(e.with_traceback).partition("of ")[2].rpartition(" object")[0]
            print(trc + ":", e)

    return inner


@unique
class WinAtt(IntEnum):
    """Windows Attributes"""

    ARCHIVE = stat.FILE_ATTRIBUTE_ARCHIVE
    COMPRESSED = stat.FILE_ATTRIBUTE_COMPRESSED
    DEVICE = stat.FILE_ATTRIBUTE_DEVICE
    DIRECTORY = stat.FILE_ATTRIBUTE_DIRECTORY
    ENCRYPTED = stat.FILE_ATTRIBUTE_ENCRYPTED
    HIDDEN = stat.FILE_ATTRIBUTE_HIDDEN
    INT_STREAM = stat.FILE_ATTRIBUTE_INTEGRITY_STREAM
    NORMAL = stat.FILE_ATTRIBUTE_NORMAL
    NO_CON_INDEXED = stat.FILE_ATTRIBUTE_NOT_CONTENT_INDEXED
    NO_SCR_DATA = stat.FILE_ATTRIBUTE_NO_SCRUB_DATA
    OFFLINE = stat.FILE_ATTRIBUTE_OFFLINE
    READONLY = stat.FILE_ATTRIBUTE_READONLY
    REP_POINT = stat.FILE_ATTRIBUTE_REPARSE_POINT
    SPA_FILE = stat.FILE_ATTRIBUTE_SPARSE_FILE
    SYSTEM = stat.FILE_ATTRIBUTE_SYSTEM
    TEMPORARY = stat.FILE_ATTRIBUTE_TEMPORARY
    VIRTUAL = stat.FILE_ATTRIBUTE_VIRTUAL

    def __init__(self, att):
        self.att = att

    def set_att(self, value: int, st: bool = False) -> int:

        match value, st:
            case v, _ if not isinstance(v, int):
                raise ValueError(f"[{v}] is not int!")
            case v, _ if isinstance(v, bool):
                raise ValueError(f"[{v}] expect appropriate int and not bool!")
            case _, s if not isinstance(s, bool):
                raise ValueError(f"[{s}] is not bool!")
            case _, _:
                if st:
                    return value | self.att
                else:
                    return value & ~self.att


class AttSet:
    """Setting attributes for Windows"""

    def __init__(self, filename: str, state: bool = False):
        match filename, state:
            case f, _ if not isinstance(f, str):
                raise ValueError(f"[{filename}] must be str!")
            case f, _ if not os.path.isfile(filename):
                raise FileExistsError(f"{filename} not exist!")
            case _, s if not isinstance(s, bool):
                raise ValueError(f"[{state}] must be bool!")
            case _, _:
                self.filename = filename
                self.state = state

    def curstat(self) -> dict:
        """Checking file attributes status"""

        current = os.stat(self.filename).st_file_attributes
        ck = {
            i: True for i, j in WinAtt._member_map_.items() if current & j.att == j.att
        }
        if ck:
            return {Path(self.filename).name: ck}
        else:
            return {Path(self.filename).name: "No Attributes set!"}

    @excp
    def set_file_attrib(self, attr: int) -> None:
        """Setting file attributes"""

        match attr:
            case a if not isinstance(a, int):
                raise ValueError("Must be int!")
            case a if isinstance(a, bool):
                raise ValueError("Must be appropriate int not bool!")
            case _:
                if [j for j in WinAtt._member_map_.values() if attr == j]:
                    current = os.stat(self.filename).st_file_attributes
                    if self.state:
                        changed = WinAtt(attr).set_att(current, self.state)
                    else:
                        changed = WinAtt(attr).set_att(current)
                    if current != changed:
                        if not ctypes.windll.kernel32.SetFileAttributesW(
                            self.filename, changed
                        ):
                            raise ctypes.WinError(ctypes.get_last_error())
                    else:
                        print(
                            f"Current {Path(self.filename).name} file state"
                            f" of {WinAtt(attr).name} no changes!"
                        )
                else:
                    print("No such attribute!")


@excp
def main():
    """Cli usage"""

    parser = argparse.ArgumentParser(
        prog="WinAtt", description="Change file attributes!"
    )
    parser.add_argument("-p", "--path", type=str, help="File's path")
    args = parser.parse_args()

    ch = None
    fl = None
    atr = None
    match args.path:
        case p if os.path.isfile(p):
            match ch := input('Check file attributes status or change? ["C" or "A"] '):
                case ch if ch.upper() == "C":
                    fl = AttSet(args.path)
                    pprint(fl.curstat())
                case ch if ch.upper() == "A":
                    atr = input(f"{WinAtt._member_names_}\nWhich one? ")
                    match atr:
                        case atr if atr in WinAtt._member_names_:
                            fl = AttSet(args.path)
                            if fl.curstat()[Path(args.path).name].get(atr, None):
                                fl.set_file_attrib(WinAtt[atr].att)
                            else:
                                fl.state = True
                                fl.set_file_attrib(WinAtt[atr].att)
                            pprint(fl.curstat())
                        case _:
                            print("No such attributes!")
                case _:
                    print("Abort!")
        case _:
            raise FileExistsError("No such file!")
    del parser, args, ch, fl, atr


if __name__ == "__main__":
    main()
