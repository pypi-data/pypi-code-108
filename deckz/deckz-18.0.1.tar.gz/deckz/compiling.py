from pathlib import Path
from subprocess import run
from typing import Optional

from attr import attrib, attrs

from deckz.settings import Settings


@attrs(auto_attribs=True, frozen=True)
class CompilePaths:
    latex: Path
    build_pdf: Path
    output_pdf: Path
    build_log: Path
    output_log: Path


@attrs(auto_attribs=True, frozen=True)
class CompileResult:
    ok: bool
    stdout: Optional[str] = attrib(default="")
    stderr: Optional[str] = attrib(default="")


def compile(latex_path: Path, settings: Settings) -> CompileResult:
    completed_process = run(
        settings.build_command + [latex_path.name],
        cwd=latex_path.parent,
        capture_output=True,
        encoding="utf8",
    )
    return CompileResult(
        completed_process.returncode == 0,
        completed_process.stdout,
        completed_process.stderr,
    )
