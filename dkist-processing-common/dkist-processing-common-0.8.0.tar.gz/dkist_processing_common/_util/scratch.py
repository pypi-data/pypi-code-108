"""
Scratch file system api
"""
import logging
from contextlib import contextmanager
from os import umask
from pathlib import Path
from shutil import rmtree
from typing import Generator
from typing import Iterable
from typing import Optional
from typing import Union

from dkist_processing_common._util.config import get_config
from dkist_processing_common._util.tags import TagDB


logger = logging.getLogger(__name__)


class WorkflowFileSystem:
    """
    Wrapper for interactions with the shared file system "scratch" supporting
    recipe run id based namespaces and tagged data
    """

    def __init__(
        self,
        recipe_run_id: Optional[int] = 0,
        task_name: str = "dev_task",
        scratch_base_path: Union[Path, str, None] = None,
    ):
        self.recipe_run_id = recipe_run_id
        self.task_name = task_name
        if not scratch_base_path:
            scratch_base_path = get_config("SCRATCH_BASE_PATH", "scratch/")
        self.scratch_base_path = scratch_base_path
        self.workflow_base_path = Path(self.scratch_base_path) / str(recipe_run_id)
        with self._mask():
            self.workflow_base_path.mkdir(parents=True, exist_ok=True)
        self._tag_db = TagDB(recipe_run_id=self.recipe_run_id, task_name=self.task_name)

    @staticmethod
    @contextmanager
    def _mask():
        """
        Set a permissive umask to allow other users (e.g. globus) to modify resources created
        by the scratch library
        """
        old_mask = umask(0)
        try:
            yield
        finally:
            umask(old_mask)

    def absolute_path(self, relative_path: Union[Path, str]) -> Path:
        """
        Convert a relative path to an absolute path with the base directories for the that workflow
        instance
        """
        relative_path = Path(relative_path)
        if relative_path.is_absolute():
            raise ValueError("Relative path must be relative")

        return self.workflow_base_path / relative_path

    def write(
        self,
        file_obj: bytes,
        relative_path: Union[Path, str],
        tags: Union[Iterable[str], None] = None,
    ) -> None:
        """
        Write a file object to the path specified and tagged with any tags listed in tags
        """
        path = self.absolute_path(relative_path)
        with self._mask():
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open(mode="wb") as f:
                f.write(file_obj)
        if tags:
            self.tag(path, tags)

    def delete(self, path: Union[Path, str]):
        path = Path(path)
        path.unlink(missing_ok=True)
        self._tag_db.clear_value(value=path)

    def tag(self, path: Union[Path, str], tags: Union[Iterable[str], str]) -> None:
        """
        Tag existing paths.  The path must be relative to the WorkflowFileSystem base path and
           must exist.
        """
        path = Path(path)
        if not (self.workflow_base_path in path.parents):
            raise ValueError(
                f"Cannot tag paths which are not children of the base path {self.workflow_base_path}"
            )
        if not path.exists():
            raise FileNotFoundError(f"Cannot tag paths which do not exist. {path=}")

        if isinstance(tags, str):
            self._tag_db.add(tags, str(path))
        else:
            for tag in tags:
                self._tag_db.add(tag, str(path))

    def tags(self, path: Union[Path, str]):
        value = str(path)
        return self._tag_db.tags_for_value(value=value)

    def find_any(self, tags: Iterable[str]) -> Generator[Path, None, None]:
        """
        Return a generator of Path objects that are tagged by the union of the input tags
        """
        paths = self._tag_db.any(tags)
        # Raise warning if the set is empty
        if len(paths) == 0:
            logger.warning(f"No files found containing any of the {tags=}")
        for path in paths:
            yield Path(path)

    def find_all(self, tags: Iterable[str]) -> Generator[Path, None, None]:
        """
        Return a generator of Path objects that are tagged by the intersection of the input tags
        """
        paths = self._tag_db.all(tags)
        # Raise warning if the set is empty
        if len(paths) == 0:
            logger.warning(f"No files found containing the set of {tags=}")
        for path in paths:
            yield Path(path)

    def count_any(self, tags: Iterable[str]) -> int:
        """
        Return the number of objects that are tagged by the union of the input tags
        """
        return len(self._tag_db.any(tags))

    def count_all(self, tags: Iterable[str]) -> int:
        """
        Return the number of objects that are tagged by the intersection of the input tags
        """
        return len(self._tag_db.all(tags))

    def close(self):
        """
        Close the db connection.  Call on __exit__ of a Task
        """
        self._tag_db.close()

    def purge(self, ignore_errors: bool = False):
        """
        Remove all data (tags, files, and folders) for the instance.
            Call when tearing down a workflow
        """
        rmtree(self.workflow_base_path, ignore_errors=ignore_errors)
        self._tag_db.purge()

    def __repr__(self):
        return f"WorkflowFileSystem(recipe_run_id={self.recipe_run_id}, task_name={self.task_name}, scratch_base_path={self.scratch_base_path})"

    def __str__(self):
        return f"{self!r} connected to {self._tag_db}"
