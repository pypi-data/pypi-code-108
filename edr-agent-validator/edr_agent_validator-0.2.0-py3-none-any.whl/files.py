from dataclasses import dataclass
from datetime import datetime
import os
from pathlib import Path

import desert
import typer
import psutil
from marshmallow import Schema

from edr_agent_validator.activity import Activity, ActivityType


@dataclass
class FileIOActivity(Activity):
    path: str


schema: Schema = desert.schema(FileIOActivity)


def create_file(filename: Path) -> FileIOActivity:
    try:
        with open(filename, mode="a"):
            pass
    except OSError as e:
        typer.echo(f"Failed to create file {filename.name} due to error: {e}")

    proc = psutil.Process()
    return FileIOActivity(
        datetime.fromtimestamp(proc.create_time()),
        proc.username(),
        proc.name(),
        proc.cmdline(),
        proc.pid,
        ActivityType.CREATE_FILE,
        str(filename),
    )


def modify_file(filename: Path, contents_to_append: str) -> FileIOActivity:
    try:
        with open(filename, mode="a") as f:
            f.write(contents_to_append)
    except OSError as e:
        typer.echo(f"Failed to modify file {filename.name} due to error: {e}")

    proc = psutil.Process()
    return FileIOActivity(
        datetime.utcnow(),
        proc.username(),
        proc.name(),
        proc.cmdline(),
        proc.pid,
        ActivityType.MODIFY_FILE,
        str(filename),
    )


def delete_file(filename: Path) -> FileIOActivity:
    try:
        os.remove(filename)
    except OSError as e:
        typer.echo(f"Failed to delete file {filename.name} due to error: {e}")

    proc = psutil.Process()
    return FileIOActivity(
        datetime.fromtimestamp(proc.create_time()),
        proc.username(),
        proc.name(),
        proc.cmdline(),
        proc.pid,
        ActivityType.DELETE_FILE,
        str(filename),
    )
