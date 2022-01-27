"""Provides a namespaced key-value store.

Note:
    This module is currently in private beta. Please reach out if you'd like to test it.
"""


from typing import Any


def fetch(path: str):
    """Fetches a namespaced value from the key-value store.

    Namespaces can be nested with dot notation.
    e.g. fetch("users.titles.alice")

    Note:
        This function is currently in private beta. Please reach out if you'd like to test it.

    Args:
        path (str): A string in dot notation representing a nested namespace.

    Raises:
        KeyError: If a non-namespace object has already been set at a non-leaf node of ``path``.
    """


def put(path: str, value: Any):
    """Puts a namespaced value into the key-value store.

    Namespaces can be nested with dot notation.
    e.g. put("users.titles.alice", "manager")

    Note:
        This function is currently in private beta. Please reach out if you'd like to test it.

    Args:
        path (str): A string in dot notation representing a nested namespace.
        value: Any serializable value to store.

    Raises:
        KeyError: If a non-namespace object has already been set at a non-leaf node of ``path``.
    """
