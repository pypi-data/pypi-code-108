"""
Tag cloud manager
"""
from pathlib import Path
from typing import Iterable
from typing import List
from typing import Set
from typing import Tuple
from typing import Union

from redis import Redis

from dkist_processing_common._util.config import get_mesh_config


class TagDB:
    def __init__(self, recipe_run_id: int, task_name: str, namespace: str = "path"):
        """
        Initialize a connection to a tag database whose instance is uniquely identified by
        the recipe_run_id and whose client connection is identified with the task_name
        """
        self.recipe_run_id = recipe_run_id
        self.task_name = task_name
        host, port = self._db_host_port()
        self._db = self.recipe_run_id % 15
        self.namespace = f"{self.recipe_run_id}:{namespace}:"
        connection_name = f"{self.namespace}{self.task_name}"
        self.db = Redis(db=self._db, host=host, port=port, client_name=connection_name)

    @staticmethod
    def _db_host_port() -> Tuple[str, int]:
        mesh_default = '{"automated-processing-scratch-inventory": {"mesh_address": "localhost", "mesh_port": 6379}}'
        mesh_config = get_mesh_config(default=mesh_default)
        return (
            mesh_config["automated-processing-scratch-inventory"]["mesh_address"],
            mesh_config["automated-processing-scratch-inventory"]["mesh_port"],
        )

    @staticmethod
    def _format_query_result(result: List[bytes]) -> Set[str]:
        return {r.decode("utf8") for r in result}

    def _add_name_space(self, tags: Union[Iterable[str], str]) -> Union[Iterable[str], str]:
        if isinstance(tags, str):
            return self.namespace + tags
        return [f"{self.namespace}{t}" for t in tags]

    def _remove_name_space(self, raw_tags: Union[Iterable[bytes], bytes]) -> Iterable[str]:
        prefix_length = len(self.namespace)
        if isinstance(raw_tags, bytes):
            raw_tags = [raw_tags]
        return [str(k[prefix_length:], "UTF-8") for k in raw_tags]

    def add(self, tag: str, value: str):
        """
        Add values to a tag
        """
        tag = self._add_name_space(tag)
        self.db.sadd(tag, value)

    def clear_tag(self, tag: str) -> None:
        """
        Remove a tag from the database
        """
        tag = self._add_name_space(tag)
        self.db.delete(tag)

    def clear_value(self, value: Union[Path, str]) -> None:
        """
        Remove a value from all tags in the DB
        """
        for tag in self._namespace_keys:
            self.remove(tag, value)

    def remove(self, tag: Union[str, bytes], value: Union[Path, str]):
        """
        Remove a value from a tag
        """
        if isinstance(value, Path):
            value = str(value)
        self.db.srem(tag, value)

    def any(self, tags: Union[Iterable[str], str]) -> Set[str]:
        """
        Return a set of values that match any of the tags
        """
        tags = self._add_name_space(tags)
        r = self.db.sunion(tags)
        return self._format_query_result(r)

    def all(self, tags: Union[Iterable[str], str]) -> Set[str]:
        """
        Return a set of values that match all of the tags
        """
        tags = self._add_name_space(tags)
        r = self.db.sinter(tags)
        return self._format_query_result(r)

    def tags_for_value(self, value: str) -> Iterable[str]:
        """
        Return list of tags assigned to a value
        """
        value_tags = [t for t in self._namespace_keys if self.db.sismember(t, value)]
        return self._remove_name_space(value_tags)

    def close(self):
        """
        Close the connection to the tag db.  For use at the end of a task
        """
        self.db.close()

    @property
    def _namespace_keys(self) -> List[bytes]:
        return self.db.keys(f"{self.namespace}*")

    @property
    def tags(self) -> Iterable[str]:
        return self._remove_name_space(self._namespace_keys)

    def purge(self) -> None:
        """
        Remove the database of tags.  For use at the end of a workflow.
        """
        if keys := self._namespace_keys:
            self.db.delete(*keys)

    def __repr__(self):
        return f"TagDB(recipe_run_id={self.recipe_run_id}, task_name={self.task_name})"

    def __str__(self):
        return f"{self!r} connected to {self.db}"
