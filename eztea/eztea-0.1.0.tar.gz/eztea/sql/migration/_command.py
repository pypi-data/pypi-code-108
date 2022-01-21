import io
import logging
import os
import os.path
import sys
from contextlib import contextmanager
from typing import List

from alembic import command as _alembic
from alembic.config import Config as _AlembicConfig
from alembic.util.exc import CommandError as _AlembicCommandError

from eztea import clock

from ._directory import MigrationDirectory
from ._error import CommandError

LOG = logging.getLogger(__package__)


@contextmanager
def _alembic_config_output(directory: MigrationDirectory):
    output = io.StringIO()
    cfg = _AlembicConfig(
        directory.alembic_ini,
        output_buffer=output,
        stdout=output,
    )
    try:
        try:
            yield cfg, output
        finally:
            sys.stdout.write(output.getvalue())
    except _AlembicCommandError as ex:
        raise CommandError(str(ex)) from ex


def init(app: str):
    directory = MigrationDirectory.from_app_dir(app)
    directory.app_dir.mkdir(exist_ok=True)
    directory.migration.mkdir(exist_ok=True)
    directory.versions.mkdir(exist_ok=True)
    directory.ddl.mkdir(exist_ok=True)

    alembic_ini = directory.template_alembic_ini.read_text("utf-8")
    alembic_ini = alembic_ini.replace("<<myapp>>", directory.app_name)
    directory.alembic_ini.write_text(alembic_ini, encoding="utf-8")

    env_py = directory.template_env_py.read_text("utf-8")
    env_py = env_py.replace("<<myapp>>", directory.app_name)
    directory.env_py.write_text(env_py, encoding="utf-8")

    script_py = directory.template_script_py_mako.read_text("utf-8")
    directory.script_py_mako.write_text(script_py, encoding="utf-8")


def auto_revision():
    directory = MigrationDirectory.from_base_dir()
    directory.versions.mkdir(exist_ok=True)
    message = clock.format_iso8601(clock.now())
    with _alembic_config_output(directory) as (cfg, _):
        _alembic.revision(cfg, autogenerate=True, message=message)


def _load_versions(directory: MigrationDirectory) -> List[str]:
    version_s = []
    for version_filepath in directory.versions.glob("*.py"):
        filename, _ = os.path.splitext(version_filepath.name)
        version_s.append(filename)
    return list(sorted(version_s))


def _revision_of(filename: str):
    return filename.rsplit("_", 1)[-1]


def _generate_ddl_upgrade(
    directory: MigrationDirectory, filename, prev_revision, revision
):
    target = directory.ddl / f"{filename}.sql"
    if not target.exists():
        with _alembic_config_output(directory) as (cfg, output):
            revision_range = f"{prev_revision}:{revision}"
            _alembic.upgrade(cfg, sql=True, revision=revision_range)
            target.write_text(output.getvalue())


def _generate_ddl_downgrade(
    directory: MigrationDirectory, filename, prev_revision, revision
):
    target = directory.ddl / f"{filename}.rollback.sql"
    if not target.exists():
        with _alembic_config_output(directory) as (cfg, output):
            revision_range = f"{revision}:{prev_revision}"
            _alembic.downgrade(cfg, sql=True, revision=revision_range)
            target.write_text(output.getvalue())


def generate_ddl():
    directory = MigrationDirectory.from_base_dir()
    directory.ddl.mkdir(exist_ok=True)
    prev_revision = "base"
    for filename in _load_versions(directory):
        revision = _revision_of(filename)
        _generate_ddl_upgrade(directory, filename, prev_revision, revision)
        _generate_ddl_downgrade(directory, filename, prev_revision, revision)
        prev_revision = revision


def _current_revision(directory: MigrationDirectory) -> str:
    with _alembic_config_output(directory) as (cfg, output):
        _alembic.current(cfg)
        revision = output.getvalue().strip()
    if not revision:
        revision = "base"
    # alembic output example: 4ed04aaf7743 (head)
    revision = revision.split()[0]
    return revision


def migrate(target: str):
    directory = MigrationDirectory.from_base_dir()
    versions = _load_versions(directory)
    if not versions:
        raise CommandError("no migration versions")
    revision_map = {"base": (0, "base")}
    for idx, filename in enumerate(versions, 1):
        revision_map[_revision_of(filename)] = (idx, filename)
    if target == "head":
        target = list(revision_map.keys())[-1]
    target = _revision_of(target)
    if target not in revision_map:
        raise CommandError(f"target revision {target!r} not found")
    target_idx, target_version = revision_map[target]
    current = _current_revision(directory)
    assert current in revision_map, f"current revision {current!r} not found"
    current_idx, current_version = revision_map[current]
    LOG.info(f"Migrate {current_version} -> {target_version}")
    if target_idx == current_idx:
        return
    with _alembic_config_output(directory) as (cfg, _):
        if current_idx < target_idx:
            _alembic.upgrade(cfg, target)
        else:
            _alembic.downgrade(cfg, target)
