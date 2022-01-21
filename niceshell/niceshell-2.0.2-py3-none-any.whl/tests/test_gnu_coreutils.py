#!/usr/bin/python3
import sys
from typing import Iterable, Union

import pytest

sys.path.extend([f"{sys.path[0]}/..", f"{sys.path[0]}/../.."])
from niceshell import core
from niceshell import gnu_coreutils


class TestGNUcoreutils:
    def test_cd(self):
        cd = gnu_coreutils.cd
        # Errors
        # path's type must be str.
        with pytest.raises(TypeError):
            cd(1)

        # Asserts
        def cd(path: str = '',
               short_args: Union[str, Iterable[str]] = []):
            return gnu_coreutils.cd(path, short_args, True)
        # Test short arguments
        assert cd('', "-L") == "cd -L --"
        assert cd('', "Pe") == "cd -P -e --"
        assert cd('', ['P', 'e', '@']) == "cd -P -e -@ --"

        # Without wildcard
        assert cd() == "cd  --"
        assert cd("path/to/smth"
                  ) == 'cd  -- "path/to/smth"'
        assert cd(R'path/with"\*"quotes_and_asterisk'
                  ) == R'cd  -- "path/with\"*\"quotes_and_asterisk"'
        assert cd(R'path/with"\\*"quotes_and_asterisk'
                  ) == R'cd  -- "path/with\"\*\"quotes_and_asterisk"'
        assert cd(R'path/with"\\\*"quotes_and_asterisk'
                  ) == R'cd  -- "path/with\"\\*\"quotes_and_asterisk"'

        # With wildcard
        assert cd("path/t*/s*th"
                  ) == 'cd  -- "path/t"*"/s"*"th"'
        assert cd('path/with"*"quotes_and_asterisk'
                  ) == R'cd  -- "path/with\""*"\"quotes_and_asterisk"'

    def test_cp(self):
        cp = gnu_coreutils.cp
        # Errors
        # source_path's type must be str or Iterable[str].
        with pytest.raises(TypeError):
            cp(1)
        with pytest.raises(TypeError):
            cp([])
        with pytest.raises(TypeError):
            cp([1])

        # destination_path's type must be str.
        with pytest.raises(TypeError):
            cp('', 1)

        # Asserts
        # batch=False
        def cp(source_path: Union[str, Iterable[str]],
               destination_path: str,
               short_args: Union[str, Iterable[str]] = [],
               long_args: Iterable[str] = [],
               sudo=False) -> str:
            return gnu_coreutils.cp(source_path, destination_path, short_args,
                                    long_args, False, sudo, True)
        # Test simple (edge) cases
        assert cp('', '') == 'cp  -- "" ""'
        assert cp([''], '') == 'cp  -- "" ""'
        assert cp(('', ''), '') == 'cp  -- "" "" ""'
        assert cp("file", "/tmp") == 'cp  -- "file" "/tmp"'
        # Test short/long arguments
        assert cp('', '', "-r") == 'cp -r -- "" ""'
        assert cp('', '', [], ["--update"]) == 'cp --update -- "" ""'
        assert cp('', '', "rf", ["update"]
                  ) == 'cp -r -f --update -- "" ""'
        assert cp('', '', ["r", "S .bak"], ["update"]
                  ) == 'cp -r -S .bak --update -- "" ""'
        # Test everything
        assert cp(
            "/folder with spaces/dir", "/different folder with spaces", 'r'
        ) == 'cp -r -- "/folder with spaces/dir" "/different folder with spaces"'
        assert cp(["../../tmp/file1", "file2", "f i l e 3"], "~/"
                  ) == 'cp  -- "../../tmp/file1" "file2" "f i l e 3" ~/""'
        assert cp(
            ["tmp/dir1", "dir2", "~/d i r 3/src/"], "~",
            ['r', 'f', 'b', "S .bak"], ["verbose"], True
        ) == 'sudo cp -r -f -b -S .bak --verbose -- "tmp/dir1" "dir2" ~/"d i r 3/src/" ~'

        # batch=True
        def cp(source_path: Union[str, Iterable[str]],
               destination_path: str,
               short_args: Union[str, Iterable[str]] = [],
               long_args: Iterable[str] = [],
               sudo=False) -> str:
            return gnu_coreutils.cp(source_path, destination_path, short_args,
                                    long_args, True, sudo, True)
        # Test simple/edge cases
        assert cp('', '') == 'cp  --  ""'
        assert cp([''], '') == 'cp  --  ""'
        assert cp(('', ''), '') == 'cp  --   ""'
        assert cp("/file", "/tmp") == 'cp  -- /file "/tmp"'
        # Test short/long arguments
        assert cp('', '', "-r") == 'cp -r --  ""'
        assert cp('', '', [], ["--update"]) == 'cp --update --  ""'
        assert cp('', '', "rf", ["update"]
                  ) == 'cp -r -f --update --  ""'
        assert cp('', '', ["r", "S .bak"], ["update"]
                  ) == 'cp -r -S .bak --update --  ""'
        # Test everything
        assert cp(
            ["tmp/dir1", "dir2", "~/dir3/src/*"], "~",
            ['r', 'f', 'b', "S .bak"], ["verbose"], True
        ) == 'sudo cp -r -f -b -S .bak --verbose -- tmp/dir1 dir2 ~/dir3/src/* ~'

        # Special cases (hacks)
        # Case #1
        assert cp("file1 file2", "~/dest"
                  ) == 'cp  -- file1 file2 ~/"dest"'
        assert cp(["file1 file2"], "~/dest"
                  ) == 'cp  -- file1 file2 ~/"dest"'

        # Case #2
        assert cp(['"/dir 1" dir2/*'], '~', 'r'
                  ) == 'cp -r -- "/dir 1" dir2/* ~'

    def test_ln(self):
        ln = gnu_coreutils.ln
        # Errors
        # source_path's type must be str or Iterable[str].
        with pytest.raises(TypeError):
            ln(1)
        with pytest.raises(TypeError):
            ln([])
        with pytest.raises(TypeError):
            ln([1])

        # destination_path's type must be str.
        with pytest.raises(TypeError):
            ln('', 1)

        # Asserts
        # batch=False
        def ln(source_path: Union[str, Iterable[str]],
               destination_path: str,
               short_args: Union[str, Iterable[str]] = [],
               long_args: Iterable[str] = [],
               sudo=False) -> str:
            return gnu_coreutils.ln(source_path, destination_path, short_args,
                                    long_args, False, sudo, True)
        # Test simple (edge) cases
        assert ln('', '') == 'ln  -- "" ""'
        assert ln([''], '') == 'ln  -- "" ""'
        assert ln(('', ''), '') == 'ln  -- "" "" ""'
        assert ln("/file", "/tmp") == 'ln  -- "/file" "/tmp"'
        # Test short/long arguments
        assert ln('', '', "-s") == 'ln -s -- "" ""'
        assert ln('', '', [], ["--force"]) == 'ln --force -- "" ""'
        assert ln('', '', "rs", ["force"]
                  ) == 'ln -r -s --force -- "" ""'
        assert ln('', '', ["r", "S .bak"], ["all"]
                  ) == 'ln -r -S .bak --all -- "" ""'
        # Test everything
        assert ln(
            "/folder with spaces/dir", "/different folder with spaces",
            's'
        ) == 'ln -s -- "/folder with spaces/dir" "/different folder with spaces"'
        assert ln(["../../tmp/file1", "file2", "f i l e 3"], "~/"
                  ) == 'ln  -- "../../tmp/file1" "file2" "f i l e 3" ~/""'
        assert ln(
            ["tmp/dir1", "dir2", "~/d i r 3/src/"], "~",
            ['r', 's', 'f', "S .bak"], ["verbose"], True
        ) == 'sudo ln -r -s -f -S .bak --verbose -- "tmp/dir1" "dir2" ~/"d i r 3/src/" ~'

        # batch=True
        def ln(source_path: Union[str, Iterable[str]],
               destination_path: str,
               short_args: Union[str, Iterable[str]] = [],
               long_args: Iterable[str] = [],
               sudo=False) -> str:
            return gnu_coreutils.ln(source_path, destination_path, short_args,
                                    long_args, True, sudo, True)
        # Test simple/edge cases
        assert ln('', '') == 'ln  --  ""'
        assert ln([''], '') == 'ln  --  ""'
        assert ln(('', ''), '') == 'ln  --   ""'
        assert ln("/file", "/tmp") == 'ln  -- /file "/tmp"'
        # Test short/long arguments
        assert ln('', '', "-s") == 'ln -s --  ""'
        assert ln('', '', [], ["--force"]) == 'ln --force --  ""'
        assert ln('', '', "rs", ["force"]
                  ) == 'ln -r -s --force --  ""'
        assert ln('', '', ["r", "S .bak"], ["all"]
                  ) == 'ln -r -S .bak --all --  ""'
        # Test everything
        assert ln(
            ["tmp/dir1", "dir2", "~/dir3/src/*"], "~",
            ['r', 's', 'f', "S .bak"], ["verbose"], True
        ) == 'sudo ln -r -s -f -S .bak --verbose -- tmp/dir1 dir2 ~/dir3/src/* ~'

        # Special cases (hacks)
        # Case #1
        assert ln("file1 file2", "~/dest"
                  ) == 'ln  -- file1 file2 ~/"dest"'
        assert ln(["file1 file2"], "~/dest"
                  ) == 'ln  -- file1 file2 ~/"dest"'

        # Case #2
        assert ln(['"/dir 1" dir2/*'], '~', 's'
                  ) == 'ln -s -- "/dir 1" dir2/* ~'

    def test_ls(self):
        ls = gnu_coreutils.ls
        # Errors
        # path's type must be str or Iterable[str].
        with pytest.raises(TypeError):
            ls(1, test=True)
        with pytest.raises(TypeError):
            ls([1], test=True)

        # Asserts
        # batch=False
        def ls(path: Union[str, Iterable[str]] = '',
               short_args: Union[str, Iterable[str]] = [],
               long_args: Iterable[str] = [],
               sudo=False) -> str:
            return gnu_coreutils.ls(
                path, short_args, long_args, False, sudo, True)
        # Test simple/edge cases
        assert ls() == "ls  --"
        assert ls(()) == "ls  --"
        assert ls(set('')) == "ls  --"
        assert ls(['', '']) == 'ls  -- "" ""'
        assert ls("/tmp") == 'ls  -- "/tmp"'
        assert ls("/folder with spaces/dir"
                  ) == 'ls  -- "/folder with spaces/dir"'
        assert ls(["dir1", "dir2", "d i r 3"]
                  ) == 'ls  -- "dir1" "dir2" "d i r 3"'
        # Test short/long arguments
        assert ls('', "a") == "ls -a --"
        assert ls('', [], ["--all"]) == "ls --all --"
        assert ls('', "ld", ["all"]
                  ) == "ls -l -d --all --"
        assert ls('', ["-l", "-d"], ["all"]
                  ) == "ls -l -d --all --"
        # Test everything
        assert ls(
            ["~/here/*", "~/there/*"],
            ['l', 'd', "-I PATTERN"], ["all"], True
        ) == 'sudo ls -l -d -I PATTERN --all -- ~/"here/*" ~/"there/*"'

        # batch=True
        def ls(path: Union[str, Iterable[str]] = '',
               short_args: Union[str, Iterable[str]] = [],
               long_args: Iterable[str] = [],
               sudo=False) -> str:
            return gnu_coreutils.ls(
                path, short_args, long_args, True, sudo, True)
        # Test simple/edge cases
        assert ls() == "ls  --"
        assert ls(()) == "ls  --"
        assert ls(set('')) == "ls  --"
        assert ls("/tmp") == "ls  -- /tmp"
        assert ls("/folder with spaces/dir"
                  ) == "ls  -- /folder with spaces/dir"
        assert ls(["dir1", "dir2", "dir3"]
                  ) == "ls  -- dir1 dir2 dir3"
        # Test short/long arguments
        assert ls('', "-a") == "ls -a --"
        assert ls('', [], ["--all"]) == "ls --all --"
        assert ls('', "ld", ["all"]
                  ) == "ls -l -d --all --"
        assert ls('', ["l", "d"], ["all"]
                  ) == "ls -l -d --all --"
        # Test everything
        assert ls(["here/*", "there/*"],
                  ['l', 'd', "I PATTERN"], ["all"], True
                  ) == "sudo ls -l -d -I PATTERN --all -- here/* there/*"

        # Special cases (hacks)
        # Case #1
        assert ls("dir1 dir2 dir3"
                  ) == "ls  -- dir1 dir2 dir3"
        assert ls(["dir1 dir2 dir3"]
                  ) == "ls  -- dir1 dir2 dir3"

        # Case #2
        assert ls(['"dir 1" "dir 2" dir3/*']
                  ) == 'ls  -- "dir 1" "dir 2" dir3/*'

    def test_mv(self):
        mv = gnu_coreutils.mv
        # Errors
        # source_path's type must be str or Iterable[str].
        with pytest.raises(TypeError):
            mv(1)
        with pytest.raises(TypeError):
            mv([])
        with pytest.raises(TypeError):
            mv([1])

        # destination_path's type must be str.
        with pytest.raises(TypeError):
            mv('', 1)

        # Asserts
        # batch=False
        def mv(source_path: Union[str, Iterable[str]],
               destination_path: str,
               short_args: Union[str, Iterable[str]] = [],
               long_args: Iterable[str] = [],
               sudo=False) -> str:
            return gnu_coreutils.mv(source_path, destination_path, short_args,
                                    long_args, False, sudo, True)
        # Test simple (edge) cases
        assert mv('', '') == 'mv  -- "" ""'
        assert mv([''], '') == 'mv  -- "" ""'
        assert mv(('', ''), '') == 'mv  -- "" "" ""'
        assert mv("file", "/tmp") == 'mv  -- "file" "/tmp"'
        # Test short/long arguments
        assert mv('', '', "-n") == 'mv -n -- "" ""'
        assert mv('', '', [], ["--update"]) == 'mv --update -- "" ""'
        assert mv('', '', "bf", ["update"]
                  ) == 'mv -b -f --update -- "" ""'
        assert mv('', '', ["b", "S .bak"], ["update"]
                  ) == 'mv -b -S .bak --update -- "" ""'
        # Test everything
        assert mv(
            "/folder with spaces/dir", "/different folder with spaces",
        ) == 'mv  -- "/folder with spaces/dir" "/different folder with spaces"'
        assert mv(["../../tmp/file1", "file2", "f i l e 3"], "~/"
                  ) == 'mv  -- "../../tmp/file1" "file2" "f i l e 3" ~/""'
        assert mv(
            ["tmp/dir1", "dir2", "~/d i r 3/src/"], "~",
            ['f', 'b', "S .bak"], ["verbose"], True
        ) == 'sudo mv -f -b -S .bak --verbose -- "tmp/dir1" "dir2" ~/"d i r 3/src/" ~'

        # batch=True
        def mv(source_path: Union[str, Iterable[str]],
               destination_path: str,
               short_args: Union[str, Iterable[str]] = [],
               long_args: Iterable[str] = [],
               sudo=False) -> str:
            return gnu_coreutils.mv(source_path, destination_path, short_args,
                                    long_args, True, sudo, True)
        # Test simple/edge cases
        assert mv('', '') == 'mv  --  ""'
        assert mv([''], '') == 'mv  --  ""'
        assert mv(('', ''), '') == 'mv  --   ""'
        assert mv("/file", "/tmp") == 'mv  -- /file "/tmp"'
        # Test short/long arguments
        assert mv('', '', "-n") == 'mv -n --  ""'
        assert mv('', '', [], ["--update"]) == 'mv --update --  ""'
        assert mv('', '', "bf", ["update"]
                  ) == 'mv -b -f --update --  ""'
        assert mv('', '', ["b", "S .bak"], ["update"]
                  ) == 'mv -b -S .bak --update --  ""'
        # Test everything
        assert mv(
            ["tmp/dir1", "dir2", "~/dir3/src/*"], "~",
            ['f', 'b', "S .bak"], ["verbose"], True
        ) == 'sudo mv -f -b -S .bak --verbose -- tmp/dir1 dir2 ~/dir3/src/* ~'

        # Special cases (hacks)
        # Case #1
        assert mv("file1 file2", "~/dest"
                  ) == 'mv  -- file1 file2 ~/"dest"'
        assert mv(["file1 file2"], "~/dest"
                  ) == 'mv  -- file1 file2 ~/"dest"'

        # Case #2
        assert mv(['"/dir 1" dir2/*'], '~', 'i'
                  ) == 'mv -i -- "/dir 1" dir2/* ~'

    def test_pwd(self):
        pwd = gnu_coreutils.pwd
        # Asserts
        # Test return value
        assert type(pwd()) == str
        assert type(pwd('L')) == core.Shell

        # Test short arguments
        def pwd(short_args: Union[str, Iterable[str]] = []):
            return gnu_coreutils.pwd(short_args, True)
        assert pwd("-L") == "pwd -L --"
        assert pwd("LP") == "pwd -L -P --"
        assert pwd(['L', 'P']) == "pwd -L -P --"

    def test_rm(self):
        rm = gnu_coreutils.rm
        # Errors
        # path's type must be str or Iterable[str].
        with pytest.raises(TypeError):
            rm(1)
        with pytest.raises(TypeError):
            rm([])
        with pytest.raises(TypeError):
            rm([1])

        # Asserts
        # batch=False
        def rm(path: Union[str, Iterable[str]],
               short_args: Union[str, Iterable[str]] = [],
               long_args: Iterable[str] = [],
               sudo=False) -> str:
            return gnu_coreutils.rm(
                path, short_args, long_args, False, sudo, True)
        # Test simple (edge) cases
        assert rm('') == 'rm  -- ""'
        assert rm(['']) == 'rm  -- ""'
        assert rm(('')) == 'rm  -- ""'
        assert rm("file") == 'rm  -- "file"'
        # Test short/long arguments
        assert rm('', "-r") == 'rm -r -- ""'
        assert rm('', [], ["--force"]) == 'rm --force -- ""'
        assert rm('', "rI", ["force"]
                  ) == 'rm -r -I --force -- ""'
        assert rm('', ["r", "I"], ["force"]
                  ) == 'rm -r -I --force -- ""'
        # Test everything
        assert rm("/folder with spaces/dir", 'r'
                  ) == 'rm -r -- "/folder with spaces/dir"'
        assert rm(["../../tmp/file1", "file2", "f i l e 3"]
                  ) == 'rm  -- "../../tmp/file1" "file2" "f i l e 3"'
        assert rm(
            ["tmp/dir1", "dir2", "~/d i r 3/src/"],
            ['r', 'f', "I"], ["verbose"], True
        ) == 'sudo rm -r -f -I --verbose -- "tmp/dir1" "dir2" ~/"d i r 3/src/"'

        # batch=True
        def rm(path: Union[str, Iterable[str]],
               short_args: Union[str, Iterable[str]] = [],
               long_args: Iterable[str] = [],
               sudo=False) -> str:
            return gnu_coreutils.rm(
                path, short_args, long_args, True, sudo, True)
        # Test simple/edge cases
        assert rm('') == "rm  --"
        assert rm(['']) == "rm  --"
        assert rm(('')) == "rm  --"
        assert rm("file") == "rm  -- file"
        # Test short/long arguments
        assert rm('', "-r") == "rm -r --"
        assert rm('', [], ["--force"]) == "rm --force --"
        assert rm('', "rI", ["force"]
                  ) == "rm -r -I --force --"
        assert rm('', ["r", "I"], ["force"]
                  ) == "rm -r -I --force --"
        # Test everything
        assert rm(
            ["tmp/dir1", "dir2", "~/dir3/src/*"],
            ['r', 'f', "I"], ["verbose"], True
        ) == "sudo rm -r -f -I --verbose -- tmp/dir1 dir2 ~/dir3/src/*"

        # Special cases (hacks)
        # Case #1
        assert rm("file1 file2"
                  ) == "rm  -- file1 file2"
        assert rm(["file1 file2"]
                  ) == "rm  -- file1 file2"

        # Case #2
        assert rm(['"/dir 1" dir2/*'], 'r'
                  ) == 'rm -r -- "/dir 1" dir2/*'


if __name__ == "__main__":
    pytest.main()
