import io
import logging
import re
from dataclasses import dataclass
from typing import List, Optional

logger = logging.getLogger(__name__)


@dataclass
class YeadocSnippet:
    code: str
    lineno: int
    id: str
    syntax: Optional[str] = None


def extract_from_buffer(f: io.TextIOBase, max_num_lines: int = 10000) -> List[YeadocSnippet]:
    out: List[YeadocSnippet] = []
    previous_nonempty_line = None
    k = 1

    while True:
        line = f.readline()
        k += 1
        if not line:
            # EOF
            break

        if line.strip() == "":
            continue

        if line.lstrip()[:3] == "```":
            syntax = line.strip()[3:]
            num_leading_spaces = len(line) - len(line.lstrip())
            lineno = k - 1
            # read the block
            code_block = []
            while True:
                line = f.readline()
                k += 1
                if not line:
                    raise RuntimeError("Hit end-of-file prematurely. Syntax error?")
                if k > max_num_lines:
                    raise RuntimeError(f"File too large (> {max_num_lines} lines). Set max_num_lines.")
                # check if end of block
                if line.lstrip()[:3] == "```":
                    break
                # Cut (at most) num_leading_spaces leading spaces
                nls = min(num_leading_spaces, len(line) - len(line.lstrip()))
                line = line[nls:]
                code_block.append(line)

            if previous_nonempty_line is None:
                previous_nonempty_line = line
                continue

            # check for keywords
            m = re.match(  # type: ignore
                r"<!--[-\s]*yeadoc-test:(.*)-->",
                previous_nonempty_line.strip(),
            )
            if m is None:
                pass  # ignore test because it is not labeled
            else:
                id = m.group(1).strip("- ")
                out.append(YeadocSnippet("".join(code_block), lineno, id, syntax))
                continue

        previous_nonempty_line = line

    return out


def load_tests_from_docstring(docstring: str) -> List[YeadocSnippet]:
    return extract_from_buffer(io.StringIO(docstring))
