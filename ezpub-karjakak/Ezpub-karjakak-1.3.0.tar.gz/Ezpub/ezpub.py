# -*- coding: utf-8 -*-
# Copyright © karjakak (K A K)

from typing import Any
from .AttSet import AttSet
import os
import shutil
import sys
import argparse
import traceback
from subprocess import Popen, PIPE
from datetime import datetime as dt
from Clien import clien
from sys import platform
from pathlib import Path
from filepmon.pgf import FilePermission as fpm
from filfla.ffl import FilFla as ff
from io import StringIO
from contextlib import redirect_stdout
from functools import wraps

# Reference:
# stackoverflow.com/.../constantly-print-subprocess-output-while-process-is-running


def excp(b: bool = True) -> Any:
    """Decorator for Exception"""

    if not isinstance(b, bool):
        raise ValueError(f'b = "{b}" Need to be boolean instead!')

    def ckerr(f):
        ckb = b

        @wraps(f)
        def trac(*args, **kwargs):
            
            try:
                if fn := f(*args, **kwargs):
                    return fn
                del fn
            except Exception:
                match ckb:
                    case True:
                        raise
                    case False:
                        exc_type, exc_value, exc_traceback = sys.exc_info()
                        print(f"ERROR - <{f.__name__}>:")
                        traceback.print_exception(
                            exc_type, exc_value, exc_traceback, limit=0
                        )
                        del exc_type, exc_value, exc_traceback

        return trac

    return ckerr


class Ezpub:
    """Building and Publishing project to PyPI"""

    def pathpypi(self) -> str:
        """Creating path default"""

        pth = "USERPROFILE" if platform.startswith("win") else "HOME"
        if os.environ.get(pth):
            pth = os.path.join(os.environ[pth], ".pypirc")
        else:
            raise EnvironmentError(f"{pth} is not exist!")
        return pth

    @excp(False)
    def prre(self, pth: str, lock: bool = True) -> None:
        """MacOS X file protection"""

        v = None
        pr = None
        fl = None

        if lock:
            v = StringIO()
            with redirect_stdout(v):
                fl = ff(pth)
                fl.flagger("IMMUTABLE")
                pr = fpm(pth)
                pr.changeperm(644)
                v.flush()
        else:
            v = StringIO()
            with redirect_stdout(v):
                pr = fpm(pth)
                pr.changeperm(000, True)
                fl = ff(pth)
                fl.flagger("IMMUTABLE")
                v.flush()
        del pth, v, pr, fl

    @excp(False)
    def winatt(self, pth: str, lock: bool = True) -> None:
        """Windows file protection."""

        a = None
        if lock:
            a = AttSet(pth)
            for i in [
                a.FILE_ATTRIBUTE_HIDDEN,
                a.FILE_ATTRIBUTE_SYSTEM,
                a.FILE_ATTRIBUTE_READONLY,
            ]:
                a.set_file_attrib(i)
        else:
            a = AttSet(pth, True)
            for i in [
                a.FILE_ATTRIBUTE_HIDDEN,
                a.FILE_ATTRIBUTE_SYSTEM,
                a.FILE_ATTRIBUTE_READONLY,
            ]:
                a.set_file_attrib(i)
        del a

    def tokfile(self, token: str = None) -> None:
        """Create token for publish to PyPI"""

        pth = self.pathpypi()
        vr = "TOKEN_PYPI"

        match token:
            case "d":
                match os.path.isfile(pth):
                    case True:
                        if platform.startswith("win"):
                            self.winatt(pth)
                        else:
                            self.prre(pth)
                        os.remove(pth)
                        print("Token Removed")
                    case _:
                        print("Nothing to remove, token not created yet!")
            case None:
                print(f"IMPORTANT!")
                print(f"Please fill var: {vr}")
                gtt = clien.insdat()
                if gtt and gtt[1] == vr:
                    clien.cmsk(gtt[0], gtt[2], gtt[1])
                else:
                    if gtt is None:
                        print("All fields need to be filled!")
                    else:
                        print(f'Field "var:" must be "{vr}"!')
            case _ as ky:
                if all([os.getenv(vr, False) == ky, pss := clien.pssd()]):
                    if ky := clien.reading(ky, pss):
                        if not os.path.isfile(pth):
                            with open(pth, "w") as tkn:
                                tkn.write(
                                    f"[pypi]\nusername = __token__\npassword = {ky}"
                                )
                            del ky
                            if platform.startswith("win"):
                                self.winatt(pth, False)
                            else:
                                self.prre(pth, False)
                            print("Token created")
                        else:
                            print("Nothing to create, token already created!")
                    else:
                        print("Unable to create token!")
                else:
                    if os.getenv(vr, False):
                        print("Missing passcode!!!")
                    else:
                        print(
                            'Variable for token is not exist!!!\nPlease type: "ezpub -t None"'
                        )

    def build(self, path: str) -> None:
        """
        Build egg info, build, dist for upload to PyPI.
        When rebuild, existing ones will be removed auto or manually by user.
        """

        pth = Path(os.path.abspath(path))
        if os.path.isdir(pth):
            os.chdir(pth)
            folds = [
                f
                for i in ["build", "dist", ".egg-info"]
                for f in os.listdir()
                if i in f
            ]
            if folds:
                fda = Path(
                    os.path.join(
                        ("Archive_" + pth.name),
                        f'{str(dt.timestamp(dt.now())).replace(".", "_")}',
                    )
                )
                if not os.path.isdir(fda.parent):
                    os.mkdir(fda.parent)
                os.mkdir(fda)
                try:
                    for i in folds:
                        shutil.move(i, fda)
                except Exception as e:
                    print(e)
                    print(f"Please remove {folds} manually!")
                    if platform.startswith("win"):
                        os.startfile(path)
                    else:
                        os.system(f"open {path}")
                    sys.exit(1)
            match all(
                os.path.exists(pth.joinpath(i)) for i in ["setup.cfg", "pyproject.toml"]
            ):
                case True:
                    pnam = (
                        f"py -m build"
                        if platform.startswith("win")
                        else "python3 -m build".split()
                    )
                    self.popenp(pnam)
                case _:
                    print("This package need 'setup.cfg' and 'pyproject.toml'")

    def popenp(self, pnam: str | list) -> None:
        """Utility for Sub-Process"""

        with Popen(
            pnam, stdout=PIPE, bufsize=1, universal_newlines=True, text=True
        ) as p:
            for line in p.stdout:
                print(line, end="")

    def publish(self, path: str) -> None:
        """Upload to PyPI with twine"""

        pth = os.path.abspath(path)
        ppth = self.pathpypi()
        ckplt = (
            (Path(ppth), True) if platform.startswith("win") else (Path(ppth), False)
        )
        match (altr := os.path.exists(ckplt[0]), ckplt[1]):
            case (True, True):
                os.chdir(ckplt[0].parent)
                pnam = f'py -m twine upload "{pth}"'
                self.popenp(pnam)
            case (True, False):
                os.chdir(ckplt[0].parent)
                self.prre(ppth)
                pnam = ["python3", "-m", "twine", "upload", f"{pth}"]
                self.popenp(pnam)
                self.prre(ppth, False)
            case (False, _):
                print("Please create token first!")
        del pth, ppth, ckplt, altr


def main() -> None:
    """This will only work in cli"""

    parser = argparse.ArgumentParser(
        prog="Ezpub", description="Upload projects to PyPi"
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-t", "--token", type=str, help="Token for publish.")
    group.add_argument(
        "-b", "--build", type=str, help="Build project, ready for publish."
    )
    group.add_argument("-p", "--publish", type=str, help="Publish to pypi.")
    group.add_argument("-v", "--version", action='version', version='%(prog)s 1.3')
    args = parser.parse_args()

    ez = Ezpub()
    if args.token:
        if args.token == "None":
            ez.tokfile()
        else:
            ez.tokfile(args.token)
    elif args.build:
        ez.build(args.build)
    elif args.publish:
        ez.publish(args.publish)
    elif args.version:
        print("Ezpub version: 1.3".upper())
    del ez, args, group, parser


if __name__ == "__main__":
    main()
