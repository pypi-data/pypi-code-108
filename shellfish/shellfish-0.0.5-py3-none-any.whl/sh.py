# -*- coding: utf-8 -*-
"""shell utils"""
from __future__ import annotations

import asyncio
import signal
import sys

from distutils.dir_util import copy_tree
from enum import IntEnum
from functools import lru_cache, reduce
from glob import iglob
from operator import iconcat
from os import (
    chdir,
    chmod as _chmod,
    environ,
    fspath as _fspath,
    getcwd,
    listdir,
    makedirs,
    mkdir as _mkdir,
    path,
    remove,
    scandir,
    symlink,
    unlink,
)
from pathlib import Path
from platform import system
from shlex import quote as _quote, split as _shplit
from shutil import move, rmtree, which as _which
from subprocess import PIPE, CalledProcessError, CompletedProcess, SubprocessError, run
from time import time
from typing import (
    IO,
    Any,
    Callable,
    Dict,
    Iterable,
    Iterator,
    List,
    Optional,
    Sequence,
    Tuple,
    Type,
    Union,
)

from asyncify import asyncify
from jsonbourne.pydantic import JsonBaseModel
from shellfish import fs
from shellfish.process import is_win
from xtyping import STDIN, FsPath, IterableStr, T, TypedDict

__all__ = (
    "Done",
    "DoneError",
    "DoneObj",
    "Flag",
    "FlagMeta",
    "HrTime",
    "LIN",
    "Stdio",
    "WIN",
    "basename",
    "cd",
    "chmod",
    "cp",
    "cp_dir",
    "cp_file",
    "decode_stdio_bytes",
    "dirname",
    "do",
    "do_",
    "do_async",
    "doa",
    "echo",
    "export",
    "flatten_args",
    "link_dir",
    "link_dirs",
    "link_file",
    "link_files",
    "ls",
    "ls_dirs",
    "ls_files",
    "ls_files_dirs",
    "mkdir",
    "mkdirp",
    "mv",
    "pstderr",
    "pstdout",
    "pstdout_pstderr",
    "pwd",
    "q",
    "quote",
    "rm",
    "run",
    "setenv",
    "shplit",
    "source",
    "sync",
    "touch",
    "tree",
    "unlink_dir",
    "unlink_dirs",
    "unlink_file",
    "unlink_files",
    "where",
    "which",
    "which_lru",
)

IS_WIN: bool = is_win()

PopenArgs = Union[bytes, str, Sequence[str], Sequence[FsPath]]


class Stdio(IntEnum):
    """Standard-io enum object"""

    stdin = 0
    stdout = 1
    stderr = 2


class FlagMeta(type):
    """Meta class"""

    @staticmethod
    @lru_cache(maxsize=None)
    def attr2flag(string: str) -> str:
        """Convert and return attr to string"""
        return string.replace("_", "-")

    def __getattr__(self, name: str) -> str:
        return self.attr2flag(string=name)


class Flag(metaclass=FlagMeta):
    """Flag obj

    Examples:
        >>> Flag.__help
        '--help'
        >>> Flag._v
        '-v'

    """

    ...


def mkenv(env: Dict[str, str], extenv: bool = True) -> Dict[str, str]:
    if extenv:
        return {**{k: v for k, v in environ.items()}, **env}
    return env


def seconds2hrtime(seconds: Union[float, int]) -> Tuple[int, int]:
    """Return hr-time Tuple[int, int] (seconds, nanoseconds)

    Args:
        seconds (float): number of seconds

    Returns:
        Tuple[int, int]: (seconds, nanoseconds)

    """
    _sec, _ns = divmod(int(seconds * 1_000_000_000), 1_000_000_000)
    return _sec, _ns


class HrTimeObj(TypedDict):
    """High resolution time"""

    sec: int
    ns: int


class HrTime(JsonBaseModel):
    """High resolution time"""

    sec: int
    ns: int

    @classmethod
    def from_seconds(cls, seconds: float) -> "HrTime":
        """Return HrTime object from seconds

        Args:
            seconds (float): number of seconds

        Returns:
            HrTime object

        """
        _sec, _ns = seconds2hrtime(seconds)
        return cls(sec=_sec, ns=_ns)

    def hrdt_obj(self) -> HrTimeObj:
        return {
            "sec": self.sec,
            "ns": self.ns,
        }


class DoneError(SubprocessError):
    """Raised when run() is called with check=True and the process
    returns a non-zero exit status.

    Attributes:
      cmd, returncode, stdout, stderr, output
    """

    done: Done
    returncode: int
    stdout: str
    stderr: str
    cmd: List[str]

    def __init__(self, done: Done) -> None:
        self.returncode = done.returncode
        self.cmd = done.args
        self.stderr = done.stderr
        self.stdout = done.stdout
        self.cmd = done.args
        self.done = done

    def error_msg(self) -> str:
        if self.returncode and self.returncode < 0:
            try:
                return f"Command '{self.cmd}' died with {signal.Signals(-self.returncode)!r}."
            except ValueError:
                return f"Command '{self.cmd}' died with unknown signal {-self.returncode:d}."
        return (
            f"Command '{self.cmd}' returned non-zero exit status {self.returncode:d}."
        )

    def __str__(self) -> str:
        return f"{self.error_msg()}\n{self.done}"


class DoneObj(TypedDict):
    args: List[str]
    returncode: int
    stdout: str
    stderr: str
    ti: float
    tf: float
    dt: float
    hrdt: Optional[HrTimeObj]
    stdin: Optional[str]
    async_proc: bool
    verbose: bool


class Done(JsonBaseModel):
    """PRun => 'ProcessRun' for finished processes"""

    args: List[str]
    returncode: int
    stdout: str
    stderr: str
    ti: float
    tf: float
    dt: float
    hrdt: Optional[HrTime] = None
    stdin: Optional[str] = None
    async_proc: bool = False
    verbose: bool = False

    def __post_init__(self) -> None:
        """Write the stdout/stdout to sys.stdout/sys.stderr post object init"""
        if self.verbose:
            self.sys_print()

    def hrdt_obj(self) -> HrTimeObj:
        if self.hrdt:
            return self.hrdt.hrdt_obj()
        return HrTime.from_seconds(seconds=self.dt).hrdt_obj()

    def done_obj(self) -> DoneObj:
        """Return Done object typed dict"""
        return DoneObj(
            args=self.args,
            returncode=self.returncode,
            stdout=self.stdout,
            stderr=self.stderr,
            ti=self.ti,
            tf=self.tf,
            dt=self.dt,
            hrdt=self.hrdt_obj(),
            stdin=self.stdin,
            async_proc=self.async_proc,
            verbose=self.verbose,
        )

    def _error(self) -> DoneError:
        """Returns a CalledProcessError object"""
        return DoneError(done=self)

    def check(self) -> None:
        """Check returncode and stderr

        Raises:
            DoneError: If return code is non-zero and stderr is not None

        """
        if self.returncode and self.stderr:
            raise self._error()

    def sys_print(self) -> None:
        """Write self.stdout to sys.stdout and self.stderr to sys.stderr"""
        sys.stdout.write(self.stdout)
        sys.stderr.write(self.stderr)

    def write_stdout(self, filepath: str, *, append: bool = False) -> None:
        """Write stdout as a string to a fspath

        Args:
            filepath: Filepath to write stdout to
            append (bool): Flag to append to file or plain write to file

        """
        fs.wstring(Path(filepath), self.stdout, append=append)

    def write_stderr(self, filepath: str, *, append: bool = False) -> None:
        """Write stderr as a string to a fspath

        Args:
            filepath: Filepath of location to write stderr
            append (bool): Flag to append to file or plain write to file

        """
        fs.wstring(Path(filepath), self.stderr, append=append)

    def __gt__(self, filepath: str) -> None:  # type: ignore
        """Operator overload for writing a stdout to a fspath

        Args:
            filepath: Filepath to write stdout to

        """
        self.write_stdout(filepath)

    def __ge__(self, filepath: str) -> "Done":
        """Operator overload for writing stderr to fspath

        Args:
            filepath: Filepath of location to write stderr

        Returns:
            Done object; self

        """
        self.write_stderr(filepath)
        return self

    def __rshift__(self, filepath: str) -> None:
        """Operator overload for appending stdout to fspath

        Args:
            filepath: Filepath to write stdout to

        """
        self.write_stdout(filepath, append=True)

    def __irshift__(self, filepath: str) -> "Done":
        """Operator overload for appending stderr to fspath

        Args:
            filepath: Filepath of location to write stderr

        Returns:
            Done object; self

        """
        self.write_stderr(filepath, append=True)
        return self

    def grep(self, string: str) -> List[str]:
        """Return lines in stdout that have

        Args:
            string (str): String to search for

        Returns:
            List[str]: List of strings of stdout lines containing the given
                search string

        """
        return [
            line for line in self.stdout.splitlines(keepends=False) if string in line
        ]


def decode_stdio_bytes(stdio_bytes: bytes, lf: bool = True) -> str:
    """Return Stdio bytes from stdout/stderr as a string

    Args:
        stdio_bytes (bytes): STDOUT/STDERR bytes
        lf (bool): Replace `\r\n` line endings with `\n`

    Returns:
        str: decoded stdio bytes

    """
    if lf:
        return decode_stdio_bytes(stdio_bytes, lf=False).replace("\r\n", "\n")
    try:
        return str(stdio_bytes.decode())
    except AttributeError:
        return ""
    except Exception:
        pass

    try:
        return str(stdio_bytes.decode("utf-8"))
    except UnicodeDecodeError:
        pass
    return str(stdio_bytes.decode("latin-1"))


def pstdout(proc: CompletedProcess) -> str:
    """Get the STDOUT as a string from a subprocess

    Args:
        proc: python subprocess.process object with stdout

    Returns:
        STDOUT for the proc as as string

    """
    return decode_stdio_bytes(proc.stdout or b"")


def pstderr(proc: CompletedProcess) -> str:
    """Get the STDERR as a string from a subprocess

    Args:
        proc: python subprocess.process object with STDERR

    Returns:
        STDERR for the proc as as string

    """
    return decode_stdio_bytes(proc.stderr or b"")


def pstdout_pstderr(proc: CompletedProcess) -> Tuple[str, str]:
    """Get the STDOUT and STDERR as strings from a subprocess

    Args:
        proc: Completed-subprocess

    Returns:
        Tuple of two strings: (stdout-string, stderr-string)

    """
    return pstdout(proc), pstderr(proc)


def validate_stdin(stdin: STDIN) -> STDIN:
    if stdin is None:
        return None
    if stdin and isinstance(stdin, str):
        return validate_stdin(str(stdin).encode())
    if isinstance(stdin, (bytes, bytearray)):
        return bytes(stdin)
    raise ValueError(f"Invalid stdin: (type={str(type(stdin))}) {str(stdin)}")


def utf8_string(val: Union[str, bytes, bytearray]) -> str:
    if not isinstance(val, str):
        return val.decode("utf-8")
    return val


def flatten_args(*args: Union[Any, List[Any]]) -> List[str]:
    """Flatten possibly nested iterables of sequences to a list of strings

    Examples:
        >>> list(flatten_args("cmd", ["uno", "dos", "tres"]))
        ['cmd', 'uno', 'dos', 'tres']
        >>> list(flatten_args("cmd", ["uno", "dos", "tres", ["4444", "five"]]))
        ['cmd', 'uno', 'dos', 'tres', '4444', 'five']

    """
    return list(
        map(
            utf8_string,
            reduce(
                iconcat,
                [
                    flatten_args(*arg) if isinstance(arg, (list, tuple)) else (arg,)
                    for arg in args
                ],
                [],
            ),
        )
    )


def validate_popen_args(args: Union[PopenArgs, Tuple[PopenArgs, ...]]) -> List[str]:
    if len(args) == 0:
        raise ValueError("args must be a non-empty sequence")
    if len(args) == 1:
        _args = args[0]
        if isinstance(_args, str):
            return shplit(_args)
        return flatten_args(_args)
    return flatten_args(args)


def popen_has_pipe_character(args: Union[List[str], Tuple[str, ...]]) -> bool:
    return any(arg == "|" for arg in args)


def validate_popen_args_windows(
    args: PopenArgs, env: Optional[Dict[str, str]] = None
) -> PopenArgs:
    args = validate_popen_args(args)
    _path = None
    if env and "PATH" in env:
        _path = env["PATH"]
    fspath = which_lru(args[0], path=_path)
    if fspath:
        fspath_obj = Path(fspath)
        if fspath.lower().endswith(".cmd"):
            args[0] = str(fspath_obj.absolute())
        elif fspath.lower().endswith(".bat"):
            args[0] = str(fspath_obj.absolute())
    return args


def _do(
    args: PopenArgs,
    *,
    env: Optional[Dict[str, str]] = None,
    extenv: bool = True,
    cwd: Optional[FsPath] = None,
    shell: bool = False,
    check: bool = False,
    verbose: bool = False,
    input: STDIN = None,
    timeout: Optional[int] = None,
    text: bool = False,
) -> Done:
    """Run a subprocess synchronously

    Args:
        args: Args as strings for the subprocess
        env: Environment variables as a dictionary (Default value = None)
        cwd: Current working directory (Default value = None)
        shell: Run in shell or sub-shell
        check: Check the outputs (generally useless)
        input: Stdin to give to the subprocess
        verbose (bool): Flag to write the subprocess stdout and stderr to
            sys.stdout and sys.stderr
        timeout (Optional[int]): Timeout in seconds for the process if not None

    Returns:
        Finished PRun object which is a dictionary, so a dictionary

    """
    _input = validate_stdin(input)
    _args = [*args]
    if IS_WIN:
        _syspath = None
        if env:
            _syspath = env.get("PATH", environ["PATH"])

        exe_path = which_lru(_args[0], path=_syspath)
        if exe_path:
            _args[0] = exe_path
    if not shell and popen_has_pipe_character(_args):
        raise ValueError(
            f"WARNING: has a pipe character, but shell=False; args: {_args}"
        )
    _env = None if env is None else mkenv(env, extenv=extenv)
    args_str = " ".join(_args)
    ti = time()
    proc = run(
        args=_args if is_win() or not shell else args_str,
        stdout=PIPE,
        stderr=PIPE,
        env=_env,
        cwd=cwd,
        shell=shell,
        input=validate_stdin(input),
        timeout=timeout,
        universal_newlines=text,
    )
    tf = time()
    stdout_str = pstdout(proc)
    stderr_str = pstderr(proc)
    done = Done(
        args=proc.args if isinstance(proc.args, list) else [proc.args],
        returncode=proc.returncode,
        stdout=stdout_str,
        stderr=stderr_str,
        ti=ti,
        tf=tf,
        dt=tf - ti,
        hrdt=HrTime.from_seconds(tf - ti),
        verbose=verbose,
        stdin=_input,
    )
    if check:
        done.check()
    return done


def do(
    *popenargs: PopenArgs,
    args: Optional[PopenArgs] = None,
    env: Optional[Dict[str, str]] = None,
    extenv: bool = True,
    cwd: Optional[FsPath] = None,
    shell: bool = False,
    check: bool = False,
    verbose: bool = False,
    input: STDIN = None,
    timeout: Optional[int] = None,
) -> Done:
    """Run a subprocess synchronously

    Args:
        *popenargs: Args given as `*args`; Cannot use both *popenargs and args
        args: Args as strings for the subprocess
        env: Environment variables as a dictionary (Default value = None)
        cwd: Current working directory (Default value = None)
        shell: Run in shell or sub-shell
        check: Check the outputs (generally useless)
        input: Stdin to give to the subprocess
        verbose (bool): Flag to write the subprocess stdout and stderr to
            sys.stdout and sys.stderr
        timeout (Optional[int]): Timeout in seconds for the process if not None

    Returns:
        Finished PRun object which is a dictionary, so a dictionary

    """
    if args and popenargs:
        raise ValueError("Cannot give *args and args-keyword-argument")
    args = validate_popen_args([*args]) if args else validate_popen_args(popenargs)
    if is_win():
        args = validate_popen_args_windows(args, env)
    _input = validate_stdin(input)
    return _do(
        args=args,
        env=env,
        extenv=extenv,
        cwd=cwd,
        shell=shell,
        check=check,
        verbose=verbose,
        input=_input,
        timeout=timeout,
    )


def args2cmd(args: PopenArgs) -> Union[str, bytes]:
    """Return single command string from given popenargs"""
    if isinstance(args, (str, bytes)):
        return args
    return " ".join(map(str, args))


_run_async = asyncify(run)
_do_asyncify = asyncify(do)


async def run_async(
    *popenargs: PopenArgs,
    input: Optional[str] = None,
    capture_output: bool = False,
    timeout: Optional[int] = None,
    check: bool = False,
    **kwargs: Any,
) -> CompletedProcess:
    args = validate_popen_args(popenargs)
    complete_subprocess = await _run_async(
        args=args,
        input=input,
        capture_output=capture_output,
        timeout=timeout,
        check=check,
        **kwargs,
    )
    return complete_subprocess


async def do_asyncify(
    args: PopenArgs,
    *,
    env: Optional[Dict[str, str]] = None,
    extenv: bool = True,
    cwd: Optional[str] = None,
    shell: bool = False,
    verbose: bool = False,
    input: STDIN = None,
    check: bool = False,
    loop: Optional[Any] = None,
    timeout: Optional[int] = None,
) -> Done:
    """Run a subprocess asynchronously using asyncified version of do"""
    done = await _do_asyncify(  # type: ignore[call-arg]
        args=args,
        env=env,
        extenv=extenv,
        cwd=cwd,
        shell=shell,
        verbose=verbose,
        input=input,
        check=check,
        loop=loop,
        timeout=timeout,
    )
    done.async_proc = True
    return done


async def _do_async(
    args: PopenArgs,
    *,
    env: Optional[Dict[str, str]] = None,
    extenv: bool = True,
    cwd: Optional[str] = None,
    shell: bool = False,
    verbose: bool = False,
    input: STDIN = None,
    check: bool = False,
    loop: Optional[Any] = None,
    timeout: Optional[int] = None,
) -> Done:
    """Run a subprocess and await completion

    Args:
        args: Args as strings for the subprocess
        check (bool): Check the result returncode
        env: Environment variables as a dictionary (Default value = None)
        cwd: Current working directory (Default value = None)
        shell: Run in shell or sub-shell
        input: Stdin to give to the subprocess
        verbose (bool): Flag to write the subprocess stdout and stderr to
            sys.stdout and sys.stderr
        timeout (Optional[int]): Timeout in seconds for the process if not None

    Returns:
        Finished PRun object which is a dictionary, so a dictionary

    """
    # if is windows and python is below 3.7, use the asyncified-do func:w
    if is_win() and sys.version_info < (3, 8):
        done = await do_asyncify(  # type: ignore[call-arg]
            args=args,
            env=env,
            cwd=cwd,
            shell=shell,
            verbose=verbose,
            input=input,
            check=check,
            loop=loop,
            timeout=timeout,
        )
        done.async_proc = True
        return done

    _default_asyncio_stream_limit = 2 ** 16

    if input:
        input = validate_stdin(input)
    if isinstance(args, str):
        _args = [args]
    if isinstance(args, bytes):
        _args = [utf8_string(args)]
    elif isinstance(args, (list, tuple)):
        _args = flatten_args(args)
    else:
        _args = list(map(str, args))

    _env = None if env is None else mkenv(env, extenv=extenv)
    _cwd = pwd()
    if cwd and path.exists(cwd) and path.isdir(cwd):
        _cwd = cwd

    if is_win():
        shell = True

        # exe path
        _syspath = None
        if env:
            _syspath = env.get("PATH", environ["PATH"])

        exe_path = which_lru(_args[0], path=_syspath)
        if exe_path:
            _args[0] = exe_path

    try:
        if shell:
            _cmd = args2cmd(_args)
            ti = time()
            _proc = await asyncio.create_subprocess_shell(
                cmd=_cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=_env,
                shell=True,
                limit=_default_asyncio_stream_limit,
                cwd=_cwd,
            )
            tf = time()
        else:
            ti = time()
            _proc = await asyncio.create_subprocess_exec(
                *_args,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=_env,
                limit=_default_asyncio_stream_limit,
                cwd=_cwd,
            )
            tf = time()

        if timeout:
            try:
                _stdin = input if not isinstance(input, str) else input.encode()
                (stdout, stderr) = await asyncio.wait_for(
                    _proc.communicate(input=_stdin),  # wait for subprocess to finish
                    timeout=timeout,
                )
            except asyncio.TimeoutError as te:
                raise asyncio.TimeoutError(
                    str(
                        {
                            "args": args,
                            "input": input,
                            "env": env,
                            "cwd": cwd,
                            "shell": shell,
                            "asyncio.TimeoutError": str(te),
                        }
                    )
                )

        else:
            _input = input if not isinstance(input, str) else input.encode()
            (stdout, stderr) = await _proc.communicate(input=_input)  # wait fo
        if _proc.returncode and stderr and check:
            raise CalledProcessError(
                returncode=_proc.returncode, output=stdout, stderr=stderr, cmd=str(args)
            )
        return Done(
            args=args,
            returncode=_proc.returncode,
            stdout=decode_stdio_bytes(stdout),
            stderr=decode_stdio_bytes(stderr),
            stdin=input,
            ti=ti,
            tf=tf,
            dt=tf - ti,
            hrdt=HrTime.from_seconds(tf - ti),
            verbose=verbose,
            async_proc=True,
        )

    except NotImplementedError:  # windows python 3.7
        ...

    return do(
        args,
        env=env,
        extenv=extenv,
        cwd=cwd,
        shell=shell,
        verbose=verbose,
        input=input,
        timeout=timeout,
    )


async def do_async(
    *popenargs: PopenArgs,
    args: Optional[PopenArgs] = None,
    env: Optional[Dict[str, str]] = None,
    extenv: bool = True,
    cwd: Optional[str] = None,
    shell: bool = False,
    verbose: bool = False,
    input: STDIN = None,
    check: bool = False,
    loop: Optional[Any] = None,
    timeout: Optional[int] = None,
) -> Done:
    """Run a subprocess and await its completion

    Args:
        *popenargs: Args given as `*args`; Cannot use both *popenargs and args
        args: Args as strings for the subprocess
        check (bool): Check the result returncode
        env: Environment variables as a dictionary (Default value = None)
        cwd: Current working directory (Default value = None)
        shell: Run in shell or sub-shell
        input: Stdin to give to the subprocess
        verbose (bool): Flag to write the subprocess stdout and stderr to
            sys.stdout and sys.stderr
        timeout (Optional[int]): Timeout in seconds for the process if not None
        loop: Optional event loop to run subprocess in

    Returns:
        Finished PRun object which is a dictionary, so a dictionary

    """
    if args and popenargs:
        raise ValueError("Cannot give *args and args-keyword-argument")
    args = validate_popen_args([*args]) if args else validate_popen_args(popenargs)
    if is_win() and sys.version_info < (3, 8):
        done = await do_asyncify(  # type: ignore[call-arg]
            args=args,
            env=env,
            extenv=extenv,
            cwd=cwd,
            shell=shell,
            verbose=verbose,
            input=input,
            check=check,
            loop=loop,
            timeout=timeout,
        )
        done.async_proc = True
        return done
    if not shell and is_win():
        args = validate_popen_args_windows(args, env)
    return await _do_async(
        args=args,
        env=env,
        extenv=extenv,
        cwd=cwd,
        shell=shell,
        verbose=verbose,
        input=input,
        check=check,
        loop=loop,
        timeout=timeout,
    )


do_ = do_async


async def doa(
    *popenargs: PopenArgs,
    args: Optional[PopenArgs] = None,
    env: Optional[Dict[str, str]] = None,
    extenv: bool = True,
    cwd: Optional[str] = None,
    shell: bool = False,
    verbose: bool = False,
    input: STDIN = None,
    check: bool = False,
    loop: Optional[Any] = None,
    timeout: Optional[int] = None,
) -> Done:
    """Run a subprocess and await its completion

    Alias for sh.do_async

    Args:
        *popenargs: Args given as `*args`; Cannot use both *popenargs and args
        args: Args as strings for the subprocess
        check (bool): Check the result returncode
        env: Environment variables as a dictionary (Default value = None)
        cwd: Current working directory (Default value = None)
        shell: Run in shell or sub-shell
        input: Stdin to give to the subprocess
        verbose (bool): Flag to write the subprocess stdout and stderr to
            sys.stdout and sys.stderr
        timeout (Optional[int]): Timeout in seconds for the process if not None
        loop: Optional event loop to run subprocess in

    Returns:
        Finished PRun object which is a dictionary, so a dictionary

    """
    return await do_async(
        *popenargs,
        args=args,
        env=env,
        extenv=extenv,
        cwd=cwd,
        shell=shell,
        verbose=verbose,
        input=input,
        check=check,
        loop=loop,
        timeout=timeout,
    )


# =============================================================================
# /\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/
# =============================================================================
#  /\  /\  /\  /\  /\  /\  /\  /\  /\  /\  /\  /\  /\  /\  /\  /\  /\  /\  /\
# /  \/  \/  \/  \/  \/  \/  \/  \/  \/  \/  \/  \/  \/  \/  \/  \/  \/  \/  \
# =============================================================================
# \/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\
# =============================================================================
def chunks(iterable: Sequence[T], chunk_size: int) -> Iterable[Sequence[T]]:
    """Yield chunks of something slice-able with length <= chunk_size

    Args:
        iterable (Iterable[Any]): Iterable to chunk
        chunk_size (int): Size of the chunks

    Returns:
        Iterable of the chunks

    Examples:
        >>> list(chunks([1, 2, 3, 4, 5, 6], 3))
        [[1, 2, 3], [4, 5, 6]]
        >>> list(chunks([1, 2, 3, 4, 5, 6], 2))
        [[1, 2], [3, 4], [5, 6]]
        >>> list(chunks('abcdefghijklmnopqrstuvwxyz', 13))
        ['abcdefghijklm', 'nopqrstuvwxyz']

        Can chunk where iterable length is not divisible by chunk_size

        >>> list(chunks('abcdefghijklmnopqrstuvwxyz', 4))
        ['abcd', 'efgh', 'ijkl', 'mnop', 'qrst', 'uvwx', 'yz']

    """
    yield from (
        iterable[i : i + chunk_size] for i in range(0, len(iterable), chunk_size)
    )


class LIN:
    """Linux (and Mac) shell commands/methods container"""

    @staticmethod
    def rsync_args(
        src: str,
        dest: str,
        delete: bool = False,
        dry_run: bool = False,
        exclude: Optional[IterableStr] = None,
        include: Optional[IterableStr] = None,
    ) -> List[str]:
        """Return args for rsync command on linux/mac

        Args:
            src: path to remote (raid) tdir
            dest: path to local tdir
            delete: Flag that will do a 'hard sync'
            exclude: Strings/patterns to exclude
            include: Strings/patterns to include
            dry_run (bool): Perform operation as a dry run

        Returns:
            subprocess return code from rsync

        Rsync return codes::

            - 0 == Success
            - 1 == Syntax or usage error
            - 2 == Protocol incompatibility
            - 3 == Errors selecting input/output files, dirs
            - 4 == Requested  action not supported: an attempt was made to
              manipulate 64-bit files on a platform that cannot support them;
              or an option was specified that is supported by the client and
              not the server.
            - 5 == Error starting client-server protocol
            - 6 == Daemon unable to append to log-file
            - 10 == Error in socket I/O
            - 11 == Error in file I/O
            - 12 == Error in rsync protocol data stream
            - 13 == Errors with program diagnostics
            - 14 == Error in IPC code
            - 20 == Received SIGUSR1 or SIGINT
            - 21 == Some error returned by waitpid()
            - 22 == Error allocating core memory buffers
            - 23 == Partial transfer due to error
            - 24 == Partial transfer due to vanished source files
            - 25 == The --max-delete limit stopped deletions
            - 30 == Timeout in data send2viewserver/receive
            - 35 == Timeout waiting for daemon connection


        """
        if exclude is None:
            exclude = []
        if include is None:
            include = []

        if not dest.endswith("/"):
            dest = f"{dest}/"
        if not src.endswith("/"):
            src = f"{src}/"
        _args: List[Union[str, None]] = [  # type: ignore
            "rsync",
            "-a",
            "-O",
            "--no-o",
            "--no-g",
            "--no-p",
            "--delete" if delete else None,
            *(f'--exclude="{pattern}"' for pattern in exclude),
            *(f'--include="{pattern}"' for pattern in include),
            *(("--dry-run", "-i") if dry_run else (None,)),
            src,
            dest,
        ]
        return list(filter(None, _args))  # type: ignore

    @staticmethod
    def rsync(
        src: str,
        dest: str,
        delete: bool = False,
        mkdirs: bool = False,
        dry_run: bool = False,
        exclude: Optional[IterableStr] = None,
        include: Optional[IterableStr] = None,
    ) -> Done:
        """Run an `rsync` subprocess

        Args:
            mkdirs (bool): Make destination directories if they do not already
                exist; defaults to False.
            src (str): Source directory path
            dest (str): Destination directory path
            delete (bool): Delete files/directories in destination if they do
                exist in source
            exclude: Strings/patterns to exclude
            include: Strings/patterns to include
            dry_run (bool): Perform operation as a dry run

        Returns:
            Done: Done object containing the info for the rsync run

        Rsync return codes::

            - 0 == Success
            - 1 == Syntax or usage error
            - 2 == Protocol incompatibility
            - 3 == Errors selecting input/output files, dirs
            - 4 == Requested  action not supported: an attempt was made to
              manipulate 64-bit files on a platform that cannot support them;
              or an option was specified that is supported by the client and
              not the server.
            - 5 == Error starting client-server protocol
            - 6 == Daemon unable to append to log-file
            - 10 == Error in socket I/O
            - 11 == Error in file I/O
            - 12 == Error in rsync protocol data stream
            - 13 == Errors with program diagnostics
            - 14 == Error in IPC code
            - 20 == Received SIGUSR1 or SIGINT
            - 21 == Some error returned by waitpid()
            - 22 == Error allocating core memory buffers
            - 23 == Partial transfer due to error
            - 24 == Partial transfer due to vanished source files
            - 25 == The --max-delete limit stopped deletions
            - 30 == Timeout in data send2viewserver/receive
            - 35 == Timeout waiting for daemon connection

        """
        if exclude is None:
            exclude = []
        if include is None:
            include = []
        if mkdirs and not dry_run:
            makedirs(dest, exist_ok=True)
        rsync_args = LIN.rsync_args(
            src, dest, delete=delete, exclude=exclude, include=include, dry_run=dry_run
        )

        done = do(args=list(filter(None, rsync_args)))
        return done

    sync = rsync

    @staticmethod
    def link_dir(linkpath: str, targetpath: str, *, exist_ok: bool = False) -> None:
        """Make a directory symlink

        Args:
            linkpath (str): Path to the link to be made
            targetpath (str): Path to the target of the link to be made
            exist_ok (str): Allow link to exist

        """
        try:
            symlink(targetpath, linkpath)
        except FileExistsError as fee:
            if not exist_ok:
                raise fee

    @staticmethod
    def link_dirs(
        link_target_tuples: List[Tuple[str, str]], *, exist_ok: bool = False
    ) -> None:
        """Make multiple directory symlinks

        Args:
            link_target_tuples: Iterable of tuples of the form: (link, target)
                or a dictionary mapping with key => value pairs of the form
                link => target.
            exist_ok (bool): Allow link to exist

        """
        for link, target in link_target_tuples:
            LIN.link_dir(link, target, exist_ok=exist_ok)

    @staticmethod
    def link_file(linkpath: str, targetpath: str, *, exist_ok: bool = False) -> None:
        """Make a file symlink

        Args:
            linkpath (str): Path to the link to be made
            targetpath (str): Path to the target of the link to be made
            exist_ok (bool): Allow links to already exist

        """
        makedirs(path.split(linkpath)[0], exist_ok=True)
        try:
            symlink(targetpath, linkpath)
        except FileExistsError as fee:
            if not exist_ok:
                raise fee

    @staticmethod
    def link_files(
        link_target_tuples: List[Tuple[str, str]], *, exist_ok: bool = False
    ) -> None:
        """Make multiple file symlinks

        Args:
            exist_ok (bool): Allow links to already exist
            link_target_tuples: Iterable of tuples of the form: (link, target)
                or a dictionary mapping with key => value pairs of the form
                link => target.

        """
        for link, target in link_target_tuples:
            LIN.link_file(link, target, exist_ok=exist_ok)

    @staticmethod
    def unlink_dir(link: str) -> None:
        """Unlink a directory symlink given a path to the symlink

        Args:
            link: path to the symlink

        """
        unlink(str(link))

    @staticmethod
    def unlink_dirs(links: IterableStr) -> None:
        """Unlink directory symlinks given the paths the links

        Args:
            links: Iterable of paths to links

        """
        for link in links:
            LIN.unlink_dir(link)

    @staticmethod
    def unlink_file(link: str) -> None:
        """Unlink a file symlink given a path to the symlink

        Args:
            link: path to the symlink

        """
        unlink(str(link))

    @staticmethod
    def unlink_files(links: IterableStr) -> None:
        """Unlink directory symlinks given the paths the links

        Args:
            links: Iterable of paths to links

        """
        for link in links:
            LIN.unlink_file(link)


# =============================================================================
# /\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/
# =============================================================================
#  /\  /\  /\  /\  /\  /\  /\  /\  /\  /\  /\  /\  /\  /\  /\  /\  /\  /\  /\
# /  \/  \/  \/  \/  \/  \/  \/  \/  \/  \/  \/  \/  \/  \/  \/  \/  \/  \/  \
# =============================================================================
# \/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\
# =============================================================================


class WIN:
    """Windows shell commands/methods container"""

    _MAX_CMD_LENGTH: int = 8192

    @staticmethod
    def robocopy_args(
        src: str,
        dest: str,
        *,
        delete: bool = False,
        exclude_files: Optional[List[str]] = None,
        exclude_dirs: Optional[List[str]] = None,
        dry_run: bool = False,
    ) -> List[str]:
        """Return list of robocopy command args

        Args:
            src (str): path to source directory
            dest (str): path to destination directory
            delete (bool): Delete files in the destination directory if they do
                not exist in the source directory
            exclude_files: Strings/patterns with which to exclude files
            exclude_dirs: Strings/patterns with which to exclude directories
            dry_run (bool): Do the operation as a dry run

        Returns:
            subprocess return code from robocopy

        Robocopy return codes::

            0. No files were copied. No failure was encountered. No files were
               mismatched. The files already exist in the destination
               directory; therefore, the copy operation was skipped.
            1. All files were copied successfully.
            2. There are some additional files in the destination directory
               that are not present in the source directory. No files were
               copied.
            3. Some files were copied. Additional files were present. No
               failure was encountered.
            5. Some files were copied. Some files were mismatched. No failure
               was encountered.
            6. Additional files and mismatched files exist. No files were
               copied and no failures were encountered. This means that the
               files already exist in the destination directory.
            7. Files were copied, a file mismatch was present, and additional
               files were present.
            8. Several files did not copy.

        """
        if exclude_files is None:
            exclude_files = []
        if exclude_dirs is None:
            exclude_dirs = []
        _args = [
            "robocopy",
            src,
            dest,
            "/MIR" if delete else "/E",
            "/mt",
            "/W:1",
            "/R:1",
        ]
        if exclude_dirs:
            _args.extend(["/XD", *exclude_dirs])
        if exclude_files:
            _args.extend(["/XF", *exclude_files])
        if dry_run:
            _args.append("/L")
        return list(filter(None, _args))

    @staticmethod
    def robocopy(
        src: str,
        dest: str,
        *,
        mkdirs: bool = True,
        delete: bool = False,
        exclude_files: Optional[List[str]] = None,
        exclude_dirs: Optional[List[str]] = None,
        dry_run: bool = False,
    ) -> Done:
        """Robocopy wrapper function (crude in that it opens a subprocess)

        Args:
            src (str): path to source directory
            dest (str): path to destination directory
            delete (bool): Delete files in the destination directory if they do
                not exist in the source directory
            exclude_files: Strings/patterns with which to exclude files
            exclude_dirs: Strings/patterns with which to exclude directories
            dry_run (bool): Do the operation as a dry run
            mkdirs (bool): Flag to make destinaation directories if they do
                not already exist

        Returns:
            subprocess return code from robocopy

        Robocopy return codes::

            0. No files were copied. No failure was encountered. No files were
               mismatched. The files already exist in the destination
               directory; therefore, the copy operation was skipped.
            1. All files were copied successfully.
            2. There are some additional files in the destination directory
               that are not present in the source directory. No files were
               copied.
            3. Some files were copied. Additional files were present. No
               failure was encountered.
            5. Some files were copied. Some files were mismatched. No failure
               was encountered.
            6. Additional files and mismatched files exist. No files were
               copied and no failures were encountered. This means that the
               files already exist in the destination directory.
            7. Files were copied, a file mismatch was present, and additional
               files were present.
            8. Several files did not copy.

        """
        if exclude_files is None:
            exclude_files = []
        if exclude_dirs is None:
            exclude_dirs = []
        if mkdirs and not dry_run:
            makedirs(dest, exist_ok=True)
        _args = WIN.robocopy_args(
            src=src,
            dest=dest,
            delete=delete,
            exclude_files=exclude_files,
            exclude_dirs=exclude_dirs,
            dry_run=dry_run,
        )
        return do(args=_args)

    sync = robocopy

    @staticmethod
    def link_dir(linkpath: str, targetpath: str) -> None:
        """Make a directory symlink

        Args:
            linkpath (str): Path to the link to be made
            targetpath (str): Path to the target of the link to be made

        """
        makedirs(path.split(linkpath)[0], exist_ok=True)
        try:
            symlink(targetpath, linkpath, target_is_directory=True)
        except OSError:
            do(args=["mklink", "/D", linkpath, targetpath], shell=True)

    @staticmethod
    def link_dirs(link_target_tuples: List[Tuple[str, str]]) -> None:
        """Make multiple directory symlinks

        Args:
            link_target_tuples: Iterable of tuples of the form: (link, target)
                or a dictionary mapping with key => value pairs of the form
                link => target.

        """
        try:
            for link, target in link_target_tuples:
                WIN.link_dir(link, target)
        except OSError:
            _exists = [
                f"mklink /D {link} {target}"
                for link, target in link_target_tuples
                if WIN._check_link_target_dirs(link, target)
            ]
            _proc = do(args=" && ".join(_exists).split(" "), shell=True)
            stderr = _proc.stderr
            if "too" in stderr and "long" in stderr:
                tuple_chunks = list(
                    chunks(link_target_tuples, len(link_target_tuples) // 2)
                )
                for tuple_chunk in tuple_chunks:
                    WIN.link_dirs(list(tuple_chunk))

    @staticmethod
    def link_file(linkpath: str, targetpath: str) -> None:
        """Make a file symlink

        Args:
            linkpath (str): Path to the link to be made
            targetpath (str): Path to the target of the link to be made

        """
        try:
            symlink(targetpath, linkpath)
        except OSError:
            makedirs(path.split(linkpath)[0], exist_ok=True)
            do(args=["mklink", linkpath, targetpath], shell=True)

    @staticmethod
    def link_files(link_target_tuples: List[Tuple[str, str]]) -> None:
        """Make multiple file symlinks

        Args:
            link_target_tuples: Iterable of tuples of the form: (link, target)
                or a dictionary mapping with key => value pairs of the form
                link => target.

        """
        try:
            for link, target in link_target_tuples:
                WIN.link_file(link, target)
        except OSError:
            link_target_tuples = list(link_target_tuples)
            _exists = [
                f"mklink {link} {target}"
                for link, target in link_target_tuples
                if WIN._check_link_target_files(link, target)
            ]
            _proc = do(args=" && ".join(_exists).split(" "), shell=True)
            stdout = _proc.stdout
            stderr = _proc.stderr
            if ("too" in stderr and "long" in stderr) or (
                "too" in stderr and "long" in stdout
            ):
                tuple_chunks = list(
                    chunks(link_target_tuples, len(link_target_tuples) // 2)
                )
                for tuple_chunk in tuple_chunks:
                    WIN.link_files(list(tuple_chunk))

    @staticmethod
    def unlink_dir(link: str) -> None:
        """Unlink a directory symlink given a path to the symlink

        Args:
            link: path to the symlink

        """
        try:
            unlink(link)
        except OSError:
            do(args=["RD", link], shell=True)

    @staticmethod
    def unlink_dirs(links: IterableStr) -> None:
        """Unlink directory symlinks given the paths the links

        Args:
            links: Iterable of paths to links

        """
        try:
            for link in links:
                WIN.unlink_dir(link)
        except OSError:
            cmd_args = " && ".join(f"RD {link}" for link in links).split(" ")
            do(args=cmd_args, shell=True)

    @staticmethod
    def unlink_file(link: str) -> None:
        """Unlink a file symlink given a path to the symlink

        Args:
            link (str): path to the symlink

        """
        try:
            unlink(link)
        except OSError:
            do(args=["Del", link], shell=True)

    @staticmethod
    def unlink_files(links: IterableStr) -> None:
        """Unlink directory symlinks given the paths the links

        Args:
            links: Iterable of paths to links

        """
        try:
            for link in links:
                WIN.unlink_file(link)
        except OSError:
            cmd_args = " && ".join(f"Del {link}" for link in links).split(" ")
            do(args=cmd_args, shell=True)

    @staticmethod
    def _check_link_target_files(link: str, target: str) -> bool:
        """Check for valid symbolic link to specified target file"""
        link = str(link)
        target = str(target)
        try:
            assert path.exists(target)
            makedirs(path.split(link)[0], exist_ok=True)
            return True
        except Exception:
            ...
        return False

    @staticmethod
    def _check_link_target_dirs(link: str, target: str) -> bool:
        """Check for valid symbolic link to specified target directory"""
        link = str(link)
        target = str(target)
        try:
            assert path.exists(target) and path.isdir(target)
            makedirs(path.split(link)[0], exist_ok=True)
        except Exception:
            ...
        return True


# =============================================================================
# /\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/
# =============================================================================
#  /\  /\  /\  /\  /\  /\  /\  /\  /\  /\  /\  /\  /\  /\  /\  /\  /\  /\  /\
# /  \/  \/  \/  \/  \/  \/  \/  \/  \/  \/  \/  \/  \/  \/  \/  \/  \/  \/  \
# =============================================================================
# \/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\
# =============================================================================

##################
## OS DEPENDENT ##
##################
_OS: Union[Type[LIN], Type[WIN]] = (
    WIN if "windows" in system().lower() else LIN
)  # Use LIN/WIN as _OS
sync = _OS.sync
link_dir = _OS.link_dir
link_dirs = _OS.link_dirs
link_file = _OS.link_file
link_files = _OS.link_files
unlink_dir = _OS.unlink_dir
unlink_dirs = _OS.unlink_dirs
unlink_file = _OS.unlink_file
unlink_files = _OS.unlink_files


# =============================================================================
# /\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/
# =============================================================================
#  /\  /\  /\  /\  /\  /\  /\  /\  /\  /\  /\  /\  /\  /\  /\  /\  /\  /\  /\
# /  \/  \/  \/  \/  \/  \/  \/  \/  \/  \/  \/  \/  \/  \/  \/  \/  \/  \/  \
# =============================================================================
# \/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\
# =============================================================================

#############
## ALIASES ##
#############
def pwd() -> str:
    """Return present-working-directory path string; alias for os.getcwd

    Returns:
        str: present working directory as string

    Examples:
        >>> import os
        >>> pwd() == os.getcwd()
        True

    """
    return getcwd()


def dirname(fspath: FsPath) -> str:
    """Return dirname/parent-dir of given path; alias of os.path.dirname

    Args:
        fspath: File-system path

    Returns:
        str: basename of path

    """
    return path.dirname(_fspath(fspath))


def basename(fspath: FsPath) -> str:
    """Return the basename of given path; alias of os.path.dirname

    Args:
        fspath: File-system path

    Returns:
        str: basename of path

    """
    return path.basename(str(fspath))


def cd(dirpath: FsPath) -> None:
    """Change directory to given dirpath; alias for `os.chdir`

    Args:
        dirpath: Directory fspath

    """
    chdir(str(dirpath))


def chmod(fspath: FsPath, mode: int) -> None:
    """Change the access permissions of a file

    Args:
        fspath (FsPath): Path to file to chmod
        mode (int): Permissions mode as an int

    """
    return _chmod(path=str(fspath), mode=mode)


def echo(
    *args: Any, sep: str = " ", end: str = "\n", file: Optional[IO[Any]] = None
) -> None:
    """Print/echo function

    Args:
        *args: Item(s) to print/echo
        sep: Separator to print with
        end: End of print suffix; defaults to `\n`
        file: File like object to write to if not stdout

    """
    print(*args, sep=sep, end=end, file=file)  # noqa: T001


def export(key: str, val: Optional[str] = None) -> None:
    """Export/Set an environment variable

    Args:
        key (str): environment variable name/key
        val (str): environment variable value

    """
    if val:
        environ[key] = val
        return
    if "=" in key:
        _key = key.split("=")[0]
        return export(_key, key[len(_key) + 1 :])
    raise ValueError(
        f"Unable to parse env variable - key: {str(key)}, value: {str(val)}"
    )


def mkdir(fspath: FsPath, *, p: bool = False, exist_ok: bool = False) -> None:
    """Make directory at given fspath

    Args:
        fspath (FsPath): Directory path to create
        p (bool): Make parent dirs if True; do not make parent dirs if False
        exist_ok (bool): Throw error if directory exists and exist_ok is False

    """
    if p or exist_ok:
        return makedirs(_fspath(fspath), exist_ok=p or exist_ok)
    return _mkdir(_fspath(fspath))


def mkdirp(fspath: FsPath) -> None:
    """Make directory and parents"""
    return mkdir(fspath=fspath, p=True)


def setenv(key: str, val: Optional[str] = None) -> None:
    """Export/Set an environment variable

    Args:
        key (str): environment variable name/key
        val (str): environment variable value

    """
    return export(key=key, val=val)


def touch(fspath: FsPath) -> None:
    """Alias for shellfish.fs.touch

    Args:
        fspath (FsPath): File-system path for where to make an empty file

    """
    return fs.touch(fspath=fspath)


def shplit(string: str, comments: bool = False, posix: bool = True) -> List[str]:
    """Typed alias for shlex.split"""
    return _shplit(string, comments=comments, posix=posix)


def quote(string: str) -> str:
    """Typed alias for shlex.quote"""
    return _quote(string)


def q(string: str) -> str:
    """Typed alias for shlex.quote"""
    return _quote(string)


def which(cmd: str, path: Optional[str] = None) -> Optional[str]:
    """Return the result of `shutil.which`

    Args:
        cmd (str): Command/exe to find path of
        path (str): System path to use

    Returns:
        Optional[str]: path to command/exe

    """
    return _which(cmd, path=path)


def where(cmd: str, path: Optional[str] = None) -> Optional[str]:
    """Return the result of `shutil.which`; alias of shellfish.sh.which

    Args:
        cmd (str): Command/exe to find path of
        path (str): System path to use

    Returns:
        Optional[str]: path to command/exe

    """
    return which(cmd, path=path)


@lru_cache(maxsize=128)
def which_lru(cmd: str, path: Optional[str] = None) -> Optional[str]:
    """Return the result of `shutil.which` and cache the results

    Args:
        cmd (str): Command/exe to find path of
        path (str): System path to use

    Returns:
        Optional[str]: path to command/exe

    """
    return which(cmd, path=path)


class _DirTree:
    """DirTree object for use by the tree command"""

    _filename_prefix_mid: str = "├──"
    _filename_prefix_last: str = "└──"
    _parent_prefix_middle: str = "    "
    _parent_refix_last: str = "│   "

    def __init__(
        self,
        path: Union[str, Path],
        parent_path: Optional["_DirTree"],
        is_last: bool,
    ) -> None:
        """Construct a DirTree object

        Args:
            path: Path-string to start the directory tree at
            parent_path: The parent path to start the directory tree at
            is_last: Is the current tree the last diretory in the tree

        """
        self.path = Path(str(path))
        self.parent = parent_path
        self.is_last = is_last
        self.depth: int = self.parent.depth + 1 if self.parent else 0

    @classmethod
    def make_tree(
        cls,
        root: Path,
        parent: Optional["_DirTree"] = None,
        is_last: bool = False,
        filterfn: Optional[Callable[..., bool]] = None,
    ) -> Iterator["_DirTree"]:
        """Make a DirTree object

        Args:
            root: Root directory
            parent: Parent directory
            is_last: Is last
            filterfn: Function to filter with

        Yields:
            DirTree object

        """
        root = Path(str(root))
        filterfn = filterfn or _DirTree._default_filter

        displayable_root = cls(str(root), parent, is_last)
        yield displayable_root

        children = sorted(
            (fspath for fspath in root.iterdir() if filterfn(str(fspath))),
            key=lambda s: str(s).lower(),
        )
        count = 1
        for _path in children:
            is_last = count == len(children)
            if _path.is_dir():
                yield from cls.make_tree(
                    _path,
                    parent=displayable_root,
                    is_last=is_last,
                    filterfn=filterfn,
                )
            else:
                yield cls(_path, displayable_root, is_last)
            count += 1

    @staticmethod
    def _default_filter(path_string: str) -> bool:
        """Return True/False if the fspath is to be filtered/ignored"""
        ignore_strings = (".pyc", "__pycache__")
        return not any(
            ignored in str(path_string).lower() for ignored in ignore_strings
        )

    @property
    def displayname(self) -> str:
        """Diplay name for DirTree root path name

        Returns:
            str: root path name as a string

        """
        if self.path.is_dir():
            return self.path.name + "/"
        return self.path.name

    def displayable(self) -> str:
        """Return displayable tree string

        Returns:
            str: displayable tree string

        """
        if self.parent is None:
            return self.displayname

        _filename_prefix = (
            self._filename_prefix_last if self.is_last else self._filename_prefix_mid
        )

        parts = [f"{_filename_prefix!s} {self.displayname!s}"]

        parent = self.parent
        while parent and parent.parent is not None:
            parts.append(
                self._parent_prefix_middle
                if parent.is_last
                else self._parent_refix_last
            )
            parent = parent.parent

        return "".join(reversed(parts))


def tree(dirpath: FsPath, filterfn: Optional[Callable[[str], bool]] = None) -> str:
    """Create a directory tree string given a directory path

    Args:
        dirpath (FsPath): Directory string to make tree for
        filterfn: Function to filter sub-directories and sub-files with

    Returns:
        str: Directory-tree string

    Examples:
        >>> tmpdir = 'tree.doctest'
        >>> from os import makedirs; makedirs(tmpdir, exist_ok=True)
        >>> from pathlib import Path
        >>> filepath_parts = [
        ...     ("dir", "file1.txt"),
        ...     ("dir", "file2.txt"),
        ...     ("dir", "file3.txt"),
        ...     ("dir", "dir2", "file1.txt"),
        ...     ("dir", "dir2", "file2.txt"),
        ...     ("dir", "dir2", "file3.txt"),
        ...     ("dir", "dir2a", "file1.txt"),
        ...     ("dir", "dir2a", "file2.txt"),
        ...     ("dir", "dir2a", "file3.txt"),
        ... ]
        >>> expected_files = []
        >>> for f in filepath_parts:
        ...     fspath = path.join(*f)
        ...     fspath = path.join(tmpdir, fspath)
        ...     dirpath = path.dirname(fspath)
        ...     expected_files.append(fspath)
        ...     makedirs(dirpath, exist_ok=True)
        ...     Path(fspath).touch()
        >>> print(tree(tmpdir))
        tree.doctest/
        └── dir/
            ├── dir2/
            │   ├── file1.txt
            │   ├── file2.txt
            │   └── file3.txt
            ├── dir2a/
            │   ├── file1.txt
            │   ├── file2.txt
            │   └── file3.txt
            ├── file1.txt
            ├── file2.txt
            └── file3.txt
        >>> print(tree(tmpdir, lambda s: _DirTree._default_filter(s) and not "file2" in s))
        tree.doctest/
        └── dir/
            ├── dir2/
            │   ├── file1.txt
            │   └── file3.txt
            ├── dir2a/
            │   ├── file1.txt
            │   └── file3.txt
            ├── file1.txt
            └── file3.txt
        >>> from shutil import rmtree
        >>> rmtree(tmpdir)

    """
    return "\n".join(
        p.displayable() for p in _DirTree.make_tree(Path(dirpath), filterfn=filterfn)
    )


########
## CP ##
########


def cp_file(src: str, target: str) -> None:
    """Copy a file given a source-path and a destination-path

    Args:
        src (str): Source fspath
        target (str): Destination fspath

    """
    try:
        makedirs(path.dirname(target), exist_ok=True)
    except FileNotFoundError:
        pass
    fs.wbytes_gen(target, fs.lbytes_gen(src, blocksize=2 ** 18))


def cp_dir(src: str, target: str) -> None:
    """Copy a directory given a source and destination directory paths

    Args:
        src (str): Source directory path
        target (str): Destination directory path

    """
    if not path.exists(target):
        makedirs(target)
    copy_tree(src, target)


def cp(
    src: str,
    target: str,
    *,
    force: bool = True,
    recursive: bool = False,
    r: bool = False,
    f: bool = True,
) -> None:
    """Copy the directory/file src to the directory/file target

    Args:
        src (str): Source directory/file to copy
        target: Destination directory/file to copy
        force: Force the copy (like -f flag for cp in shell)
        recursive: Recursive copy (like -r flag for cp in shell)
        r: alias for recursive
        f: alias for force

    """
    _recursive = recursive or r
    for src in iglob(src, recursive=True):
        _dest = target
        if (path.exists(target) and not force) or src == target:
            return
        if path.isdir(src) and not _recursive:
            raise ValueError("Source ({}) is directory; use r=True")
        if path.isfile(src) and path.isdir(target):
            _dest = path.join(target, path.basename(src))
        if path.isfile(src) or path.islink(src):
            cp_file(src, _dest)
        if path.isdir(src):
            cp_dir(src, _dest)


def rm(
    fspath: FsPath,
    *,
    recursive: bool = False,
    verbose: bool = False,
    r: bool = False,
    v: bool = False,
) -> None:
    """Remove files & directories in the style of the shell

    Args:
        fspath (FsPath): Path to file or directory to remove
        recursive (bool): Flag to remove recursively (like the `-r` in `rm -r dir`)
        verbose (bool): Flag to be verbose
        v (bool): alias for verbose
        r (bool): alias for recursive kwarg

    """
    _recursive = recursive or r
    _verbose = verbose or v
    for _path_str in iglob(str(fspath), recursive=_recursive):
        try:
            remove(_path_str)
            if _verbose:
                echo(f"Removed file: {_path_str}")

        except Exception:
            if _recursive:
                rmtree(_path_str)
                if _verbose:
                    echo(f"Removed dir: {_path_str}")
            else:
                raise ValueError(_path_str + " is a directory -- use r=True")


def ls(dirpath: FsPath = ".", abspath: bool = False) -> List[str]:
    """List files and dirs given a dirpath (defaults to pwd)

    Args:
        dirpath (FsPath): path-string to directory to list
        abspath (bool): Give absolute paths

    Returns:
        List of the directory items

    """
    if abspath:
        return [el.path for el in scandir(str(dirpath))]
    return listdir(str(dirpath))


def ls_files(dirpath: FsPath = ".", *, abspath: bool = False) -> List[str]:
    """List the files in a given directory path

    Args:
        dirpath (FsPath): Directory path for which one might want to list files
        abspath (bool): Return absolute filepaths

    Returns:
        List of files as strings

    """
    files = (el for el in scandir(str(dirpath)) if el.is_file())
    if abspath:
        return list(map(lambda el: el.path, files))
    return list(map(lambda el: el.name, files))


def ls_dirs(dirpath: FsPath = ".", *, abspath: bool = False) -> List[str]:
    """List the directories in a given directory path

    Args:
        dirpath (FsPath): Directory path for which one might want list directories
        abspath (bool): Return absolute directory paths

    Returns:
        List of directories as strings

    """
    dirs = (el for el in scandir(str(dirpath)) if el.is_dir())
    if abspath:
        return list(map(lambda el: el.path, dirs))
    return list(map(lambda el: el.name, dirs))


def ls_files_dirs(
    dirpath: FsPath = ".", *, abspath: bool = False
) -> Tuple[List[str], List[str]]:
    """List the files and directories given directory path

    Args:
        dirpath (FsPath): Directory path to execute on
        abspath (bool): Return absolute file/directory paths

    Returns:
        Two lists of strings; the first is a list of the files and the second
            is a list of the directories

    """
    dir_items = fs.scandir_list(dirpath)
    dir_dir_entries = (el for el in dir_items if el.is_dir())
    file_dir_entries = (el for el in dir_items if el.is_file())
    if not abspath:
        return [el.name for el in file_dir_entries], [el.name for el in dir_dir_entries]
    return [el.path for el in file_dir_entries], [el.path for el in dir_dir_entries]


def mv(src: FsPath, dst: FsPath) -> None:
    """Move file(s) like on the command line

    Args:
        src (FsPath): source file(s)
        dst (FsPath): destination

    """
    _dst_str = str(dst)
    for file in iglob(str(src), recursive=True):
        move(file, _dst_str)


def source(filepath: FsPath, _globals: bool = True) -> None:
    """Execute/run a python file given a fspath and put globals in globasl

    Args:
        filepath (FsPath): Path to python file
        _globals (bool): Exec using globals

    """
    string = fs.lstring(str(filepath))
    if _globals:
        exec(string, globals())
    else:
        exec(string)


if __name__ == "__main__":
    from doctest import testmod

    testmod()
