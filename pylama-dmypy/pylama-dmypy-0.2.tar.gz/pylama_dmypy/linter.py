from pylama.lint import LinterV2 as Abstract
from pylama.context import RunContext

from pathlib import Path
from mypy import api
import re

regexes = {
    "dmypy_message": re.compile(
        r"(?P<filename>[^:]+):(?P<lnum>\d+):(?P<col>\d+): (?P<type>\w+): (?P<message>.+)"
    )
}


class Linter(Abstract):
    name = "dmypy"

    def run_check(self, ctx: RunContext):
        """Check code with dmypy."""
        args = ["run", "--", Path(ctx.temp_filename).parts[0], "--show-column-numbers"]
        stdout, a, b = api.run_dmypy(args)

        for line in stdout.splitlines():
            if not line:
                continue

            self.add_line(ctx, line, ctx.temp_filename)

    def add_line(self, ctx: RunContext, line: str, filename: str):
        m = regexes["dmypy_message"].match(line)
        if not m:
            return

        groups = m.groupdict()

        if groups["filename"] != filename:
            return

        lnum = int(groups["lnum"])
        col = int(groups["col"])
        mtype = groups["type"][0].upper()
        text = groups["message"].strip()

        ctx.push(source="dmypy", lnum=lnum, col=col, type=mtype, text=text)
