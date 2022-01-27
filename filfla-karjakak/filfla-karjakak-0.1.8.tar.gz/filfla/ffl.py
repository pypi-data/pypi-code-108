# -*- coding: utf-8 -*-
# Copyright (c) 2022, KarjaKAK
# All rights reserved.

import os, stat
import argparse
from enum import Enum, unique
from excptr import excp


@unique
class FileFlags(Enum):
    """Flags"""

    HIDDEN = stat.UF_HIDDEN
    APPEND = stat.UF_APPEND
    COMPRESSED = stat.UF_COMPRESSED
    IMMUTABLE = stat.UF_IMMUTABLE
    NODUMP = stat.UF_NODUMP
    NOUNLINK = stat.UF_NOUNLINK
    OPAQUE = stat.UF_OPAQUE

    def __str__(self):
        return self.name


class FilFla:
    """File Flagging"""

    def __init__(self, pth: str):
        if os.path.exists(pth):
            self.pth = pth
        else:
            raise FileExistsError(f"{pth}\nis not exist!")
        self.flags = FileFlags._member_names_

    @excp(0)
    def prt(self):
        """Print status file's flags"""

        if ckv := self._chekers():
            print(f"{self.pth}\nFlag status: {ckv}")
        else:
            print(f"{self.pth}\nStatus: NORMAL")

    @excp(0)
    def _chekers(self):
        """Return status flags of a file"""

        st = os.stat(self.pth).st_flags
        try:
            ckv = set(
                FileFlags(i.value).name
                for i in dict(FileFlags.__members__).values()
                if st & i.value == i.value
            )
            if ckv:
                return str(ckv)
            else:
                return None
        except Exception as e:
            print(e)

    @excp(0)
    def flagger(self, flname: str):
        """Change file's flags"""

        if flname in self.flags:
            flag = FileFlags[flname].value
            st = os.stat(self.pth).st_flags
            os.chflags(self.pth, st ^ flag)
            self.prt()
        else:
            print("Not Implemeted")


@excp(0)
def main():
    """CLI"""

    parser = argparse.ArgumentParser(
        prog="File Flagger", description="File flag status check and change"
    )
    parser.add_argument("-p", "--path", type=str, help="Give file's path")
    args = parser.parse_args()

    match args.path:
        case path if os.path.exists(path):
            cho = input(
                'To check file flag or change file flag? ["C" to check and "A" to change] '
            )
            match cho.upper():
                case "C":
                    x = FilFla(path)
                    x.prt()
                case "A":
                    flag = input(f"Change flag? {FileFlags._member_names_} ")
                    x = FilFla(path)
                    x.flagger(flag)
                case _:
                    print("Abort!")
        case _:
            print(f"{args.path} is not a file!")


if __name__ == "__main__":
    main()
