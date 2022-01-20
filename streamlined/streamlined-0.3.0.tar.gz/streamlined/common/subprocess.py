import asyncio
from dataclasses import dataclass, field
from subprocess import DEVNULL, PIPE
from typing import IO, Any, Dict, List, Optional, Union

from .predicates import IS_LIST, IS_STR

Stream = Optional[Union[int, IO]]
StdinStream = Union[Stream, bytes]


@dataclass
class SubprocessResult:
    args: str
    stdin: StdinStream
    stdout: bytes
    stderr: bytes
    pid: int
    returncode: int
    kwargs: Dict[str, Any] = field(default_factory=dict)


async def run(
    args: Union[str, List[str]],
    stdin: StdinStream = DEVNULL,
    stdout: Stream = PIPE,
    stderr: Stream = PIPE,
    kwargs: Optional[Dict[str, Any]] = None,
) -> SubprocessResult:
    """
    Execute a shell command.

    Argument can either be the entire command string like 'echo `"Hello World!"'` or list of string like `['echo', 'Hello World!']`.
    """
    if kwargs is None:
        kwargs = dict()

    if IS_STR(args) and " " in args:
        args = args.split(maxsplit=1)

    if isinstance(stdin, bytes):
        _stdin = PIPE
    else:
        _stdin = stdin
        stdin = None

    if IS_LIST(args):
        process = await asyncio.create_subprocess_exec(
            *args, stdin=_stdin, stdout=stdout, stderr=stderr, **kwargs
        )
        argstr = " ".join(str(arg) for arg in args)
    else:  # IS_STR(args)
        process = await asyncio.create_subprocess_exec(
            args, stdin=_stdin, stdout=stdout, stderr=stderr, **kwargs
        )
        argstr = args

    stdout, stderr = await process.communicate(input=stdin)
    return SubprocessResult(
        argstr, stdin or _stdin, stdout, stderr, process.pid, process.returncode, kwargs
    )
