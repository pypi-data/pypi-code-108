import ast
import traceback
from dataclasses import dataclass
from pathlib import Path
from typing import List
from typing import Optional
from typing import Tuple

from colorama import Fore
from pygments import highlight
from pygments.formatters import TerminalFormatter
from pygments.lexers import PythonLexer

from .cli_utils import bold
from tecton.cli import printer
from tecton_proto.data.state_update_pb2 import ValidationMessage
from tecton_spark.id_helper import IdHelper


# Fallback: if extract_code_block failed to parse the file (maybe due to a syntax error in user
# code), just try to unintelligently extract some lines around lineno.
def extract_lines(file_path: Path, lineno: int) -> Tuple[Optional[str], Optional[int]]:
    with open(file_path) as f:
        lines = list(f.read().splitlines())

        result = []
        start_line = lineno
        for line in reversed(lines[:lineno]):
            result.append(line)
            start_line -= 1
            if line.strip() == "":
                break

        result.reverse()
        for line in lines[lineno:]:
            if line.strip() == "":
                break
            else:
                result.append(line)
        return "\n".join(result), start_line


# For Python stack traces, we only get an approximate line number if the call statement spans
# multiple lines. For example, if exception is thrown inside the constructor call below:
#  1   Something(
#  2        x,
#  3        y,
#  4        z
#  5   )
#
# .. stack frame info might say it is line 3.
#
# To produce nicer error messages, we parse python file and extract the entire code block that spans
# the line we got from the stack frame info.
#
# This function returns code block and the starting line of the code block.
def extract_code_block(file_path: Path, lineno: int) -> Tuple[Optional[str], Optional[int]]:
    with open(file_path) as f:
        source = f.read()

    code = None
    try:
        root = ast.parse(source, str(file_path))

        start_line = None
        end_line = None

        for node in ast.iter_child_nodes(root):
            if node.lineno > lineno:
                end_line = node.lineno - 1
                break
            start_line = node.lineno - 1

        code = "\n".join(source.splitlines()[start_line:end_line])
        return code, start_line
    except Exception as e:
        return extract_lines(file_path, lineno)


@dataclass
class PrettyFrameInfo:
    file_path: Path
    lineno: int
    code_block_start_line: int
    code_block: str


def pretty_error(
    file_path: Path,
    user_file_paths: List[Path],
    repo_root: Path,
    exception,
    error_message,
    error_details=None,
    debug=False,
):
    if debug:
        traceback.print_exception(type(exception), value=exception, tb=exception.__traceback__)
        return

    pretty_frames: List[PrettyFrameInfo] = []

    # Otherwise, get error info from the call stack by finding the frame that contains
    # user-provided Python code.
    # TODO: handle the case when there is more than one frame of user code in the stack trace.
    fail_frame = None
    user_files_set = set(path.resolve() for path in user_file_paths)

    for frame in traceback.extract_tb(exception.__traceback__):
        frame_file_path = Path(frame.filename).resolve()
        if frame_file_path in user_files_set:
            # Extract code block around the error location
            code, start_line = extract_code_block(frame_file_path, frame.lineno)
            if code is not None and start_line is not None:
                pretty_frames.append(
                    PrettyFrameInfo(
                        file_path=frame_file_path,
                        lineno=frame.lineno,
                        code_block=code,
                        code_block_start_line=start_line,
                    )
                )

    # For a syntax error, call stack is useless but there is error location info stored in the
    # exception itself.
    if isinstance(exception, SyntaxError):
        assert exception.filename is not None and exception.lineno is not None, "Missing information from exception"
        file_path = Path(exception.filename)
        line_no = exception.lineno
        code, start_line = extract_code_block(file_path, line_no)

        if code is not None and start_line is not None:
            pretty_frames.append(
                PrettyFrameInfo(
                    file_path=file_path,
                    lineno=line_no,
                    code_block=code,
                    code_block_start_line=start_line,
                )
            )

    # relative path formatting helper
    relp = lambda x: str(x.relative_to(repo_root))

    if pretty_frames:
        filename = pretty_frames[-1].file_path
        lineno = pretty_frames[-1].lineno
        printer.safe_print(
            Fore.RED
            + f"Error while processing {bold(relp(filename))}, at line {bold(str(lineno))}: {error_message}"
            + Fore.RESET
        )
    else:
        filename = file_path
        printer.safe_print(Fore.RED + f"Error while processing {bold(relp(filename))}: {error_message}" + Fore.RESET)

    for i, pretty_frame in enumerate(reversed(pretty_frames)):
        if i == 0:
            printer.safe_print(
                f"=================== Around this code block in {bold(relp(pretty_frame.file_path))} ==================="
            )
        else:
            printer.safe_print(
                f"=================== Called from here in {bold(relp(pretty_frame.file_path))} ==================="
            )
        tf = TerminalFormatter(bg="dark", linenos=True)
        tf._lineno = pretty_frame.code_block_start_line
        printer.safe_print(highlight(pretty_frame.code_block, PythonLexer(), tf))

    if error_details:
        printer.safe_print("=================== Error: ===============================")
        printer.safe_print(error_details)


def format_validation_location_lite(obj, repo_root: str) -> None:
    printer.safe_print(
        " " * 4,
        f"in {obj.__class__.__name__} {obj.name} declared in {bold(obj._source_info.source_filename + ':' + str(obj._source_info.source_lineno))}",
    )


def format_validation_location_fancy(obj, repo_root: str) -> None:
    filename = obj._source_info.source_filename
    file_path = Path(repo_root) / filename
    lineno = int(obj._source_info.source_lineno)

    code, start_line = extract_code_block(file_path, lineno)
    tf = TerminalFormatter(bg="dark", linenos=True)
    tf._lineno = start_line

    printer.safe_print(
        f"=================== {obj.__class__.__name__} {obj.name} declared in {bold(filename)} ==================="
    )
    printer.safe_print(highlight(code, PythonLexer(), tf))


def format_server_errors(messages: List[ValidationMessage], objects, repo_root: str):
    obj_by_id = {}
    for fco_obj in objects:
        obj_by_id[IdHelper.to_string(fco_obj._id())] = fco_obj

    for i, m in enumerate(messages):
        printer.safe_print(Fore.RED + m.message + Fore.RESET)
        for fco_ref in m.fco_refs:
            obj_id = IdHelper.to_string(fco_ref.fco_id)
            obj = obj_by_id[obj_id]

            # Print the first error with fancy code snippet, then use shorter format for others
            if i == 0 and obj._source_info.source_lineno:
                format_validation_location_fancy(obj, repo_root)
            else:
                format_validation_location_lite(obj, repo_root)
