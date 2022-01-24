# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Defines Part C of the logging schema, keys that can be customized for telemetry data."""
from typing import Any, List


class ExtensionFieldKeys:
    """Keys for extension fields."""

    DISK_USED_KEY = 'DiskUsed'
    MEMORY_USED_KEY = 'MemoryUsed'

    @classmethod
    def keys(cls) -> List[str]:
        """Keys for extension fields."""
        return [
            ExtensionFieldKeys.DISK_USED_KEY,
            ExtensionFieldKeys.MEMORY_USED_KEY
        ]


class ExtensionFields(dict):
    """Defines Part C of the logging schema, keys that can be customized for telemetry data."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize a new instance of the ExtensionFields."""
        super(ExtensionFields, self).__init__(*args, **kwargs)

    @property
    def disk_used(self):
        """Disk used."""
        return self.get(ExtensionFieldKeys.DISK_USED_KEY, None)

    @disk_used.setter
    def disk_used(self, value):
        """
        Set Disk used.

        :param value: Value to set to.
        """
        self[ExtensionFieldKeys.DISK_USED_KEY] = value

    @property
    def memory_used(self):
        """Memory used."""
        return self.get(ExtensionFieldKeys.MEMORY_USED_KEY, None)

    @memory_used.setter
    def memory_used(self, value):
        """
        Set Memory.

        :param value: Value to set to.
        """
        self[ExtensionFieldKeys.MEMORY_USED_KEY] = value
