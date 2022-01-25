from typing import Any, Dict

from expiringdict import ExpiringDict  # type: ignore


MAX_LENGTH = 1000
# One day:  24 * 60 * 60
MAX_AGE_SECONDS = 86400


class NodeProviderCache:
    """Base class for storing cached node information, used to avoid excessive
    API calls to cloud providers in some cases.

    This implementation stores all information in memory.
    """

    def __init__(self) -> None:
        # tags_map and node_map are not guaranteed to be in sync in current
        # implementation.
        # Using ExpiringDict which implements a simple cache with locking and TTL.
        self.node_map: Dict[str, Any] = ExpiringDict(
            max_len=MAX_LENGTH, max_age_seconds=MAX_AGE_SECONDS
        )
        self.tags_map: Dict[str, Dict[str, str]] = ExpiringDict(
            max_len=MAX_LENGTH, max_age_seconds=MAX_AGE_SECONDS
        )

    def get_node(self, node_id: str) -> Any:
        """Returns a cached node obj with given node ID."""
        return self.node_map.get(node_id)

    def set_node(self, node_id: str, node: Any) -> None:
        """Stores a node obj into cache with given node ID."""
        self.node_map[node_id] = node
        self.tags_map.setdefault(node_id, {})

    def node_exists(self, node_id: str) -> bool:
        """Returns whether a node obj with given node ID exists in cache."""
        return node_id in self.node_map

    def get_tags(self, node_id: str) -> Dict[str, str]:
        """Returns a dict of tags associated with given node ID."""
        return self.tags_map.get(node_id, {})

    def set_tags(self, node_id: str, tags: Dict[str, str]) -> None:
        """Stores the tags into cache with given node ID."""
        self.tags_map[node_id] = tags

    def tags_exist(self, node_id: str) -> bool:
        """Returns whether tags with given node ID exists in cache."""
        return node_id in self.tags_map

    def delete_node_and_tags(self, node_id: str) -> None:
        """Deletes nodes and tags with given node ID from cache."""
        if node_id in self.node_map:
            self.node_map.pop(node_id)
        if node_id in self.tags_map:
            self.tags_map.pop(node_id)

    def cleanup(self) -> None:
        """Deletes all nodes and tags from cache."""
        self.node_map = ExpiringDict(
            max_len=MAX_LENGTH, max_age_seconds=MAX_AGE_SECONDS
        )
        self.tags_map = ExpiringDict(
            max_len=MAX_LENGTH, max_age_seconds=MAX_AGE_SECONDS
        )
