import asyncio
import logging
import os
from uuid import uuid4
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Any, Iterable, Set

import click

from .db_admin import click_main
from .. import local_database, protocol

logger = logging.getLogger(__name__)


@click_main.command()
@click.pass_context
@click.option("--quarantine/--no-quarantine", default=False)
def check(ctx, quarantine):
    with Check(ctx.obj) as check_manager:
        bad_files = check_manager.bitrot_check()
        if quarantine:
            check_manager.quarantine_files(bad_files)

        bad_files = check_manager.structural_check()
        if quarantine:
            check_manager.quarantine_files(bad_files)


class Check:
    def __init__(self, database: local_database.LocalDatabase):
        self._database = database
        self.success = True
        self.concurrent_max = os.cpu_count()
        self._executor = ProcessPoolExecutor(self.concurrent_max)

    @staticmethod
    def quarantine_files(files: Set[Path]):
        for file in files:
            new_name = file.parent / f"{file.name}.{uuid4()}.quarantine"
            logger.info(f"Moving {file} to {new_name}")
            file.rename(new_name)

    def bitrot_check(self) -> Set[Path]:
        logger.info("Bitrot check...")
        results = asyncio.get_event_loop().run_until_complete(
            self._check_all(self._all_files(), self._check_file_hash)
        )
        logger.info("Bitrot check complete")
        if results:
            logger.warning(f"Found {len(results)} bad files!")
            for result in sorted(results):
                logger.warning(f"BAD: {result}")
        else:
            logger.info("... All Good!")
        return set(results)

    def _all_files(self, path: Path = None, level: int = None, expect_prefix: str = '') -> Iterable[Path]:
        if path is None:
            path = self._database._base_path / self._database._STORE_DIR
            level = self._database.config.store_split_count
        if level > 0:
            for child in sorted(path.iterdir()):
                if child.is_dir() and len(child.name) == self._database.config.store_split_size:
                    yield from self._all_files(child, level-1, expect_prefix+child.name)
        else:
            for child in path.iterdir():
                if child.is_file() and not child.is_symlink() and child.name.startswith(expect_prefix):
                    yield child

    async def _check_all(self, items: Iterable[Any], coroutine):
        iterator = iter(items)
        active_tasks = {}
        failed_files = set()
        try:
            while len(active_tasks) <= self.concurrent_max:
                file = next(iterator)
                active_tasks[asyncio.create_task(coroutine(file))] = file
            while True:
                done, pending = await asyncio.wait(active_tasks.keys(), return_when=asyncio.FIRST_COMPLETED)
                for task in done:
                    item = active_tasks.pop(task)
                    if not task.result():
                        failed_files.add(item)
                while len(active_tasks) <= self.concurrent_max:
                    file = next(iterator)
                    active_tasks[asyncio.create_task(coroutine(file))] = file

        except StopIteration:
            pass

        while active_tasks:
            done, _ = await asyncio.wait(active_tasks.keys(), return_when=asyncio.FIRST_COMPLETED)
            for task in done:
                item = active_tasks.pop(task)
                if not task.result():
                    failed_files.add(item)

            logger.debug(f"{len(active_tasks)}")

        return failed_files

    async def _check_file_hash(self, file_path: Path) -> bool:
        logger.debug(f"Checking {file_path}")
        file_hash = await asyncio.get_running_loop().run_in_executor(self._executor, self.hash_file, file_path)
        file_name = file_path.name
        if file_name.endswith(local_database.LocalDatabaseServerSession._DIR_SUFFIX):
            file_name = file_name[:-len(local_database.LocalDatabaseServerSession._DIR_SUFFIX)]
        if file_hash != file_name:
            logger.error(f"Incorrect file hash; possible bitrot for file {file_path} - calculated has {file_hash}")
            return False
        return True

    def structural_check(self):
        logger.info("Structural Check")
        verified: Set[str] = set()
        bad = set()
        really_bad = set()
        for file in self._all_files():
            self._verify_dir(file, verified, bad, really_bad)
        logger.info("Structural check complete")
        if bad:
            logger.info(f"Missing or corrupted files: {len(really_bad)} "
                        f"invalidating {len(bad) - len(really_bad)} others.")
            for file in really_bad:
                logger.error(f"Missing / Corrupt: {file}")

            for file in bad:
                if file not in really_bad:
                    logger.error(f"Invalidated: {file}")
        logger.info("... All Good!")
        return bad


    def _verify_dir(self, path: Path, verified: Set[Path], bad: Set[Path], really_bad: Set[Path]):
        if path in verified:
            return True
        if path in bad:
            return False
        if not path.exists() and path.is_file():
            really_bad.add(path)
            bad.add(path)
            return False

        try:
            if path.name.endswith(local_database.LocalDatabaseServerSession._DIR_SUFFIX):
                logger.debug(f"Checking {path}")
                directory = protocol.Directory.parse_file(path)
                for inode in directory.children.values():
                    if inode.type is protocol.FileType.DIRECTORY:
                        ref_hash = inode.hash + local_database.LocalDatabaseServerSession._DIR_SUFFIX
                    else:
                        ref_hash = inode.hash
                    if not self._verify_dir(self._database.store_path_for(ref_hash), verified, bad, really_bad):
                        bad.add(path)
                        return False

        except Exception as error:
            logger.error(f"Bad File {path}: {str(error)}")
            really_bad.add(path)
            bad.add(path)
            return False
        else:
            verified.add(path)
            return True


    def __enter__(self):
        if self._executor is None:
            self._executor = ProcessPoolExecutor()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._executor.shutdown()
        self._executor = None

    @staticmethod
    def hash_file(file_path: Path) -> str:
        logger.debug("hashing")
        assert bytes(1)
        hsh_obj = protocol.HashType()
        with file_path.open('rb') as file:
            bytes_read = file.read(protocol.READ_SIZE)
            while bytes_read:
                hsh_obj.update(bytes_read)
                bytes_read = file.read(protocol.READ_SIZE)
        logger.debug("hashed")
        return hsh_obj.hexdigest()
