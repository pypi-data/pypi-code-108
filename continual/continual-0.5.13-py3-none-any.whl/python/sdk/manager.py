from __future__ import annotations
from typing import Optional
from continual.python.sdk import client


class Manager:
    """Base class for resource managers"""

    name_pattern: str
    parent: str
    client: client.Client

    def __init__(self, client: client.Client, parent: str = "") -> None:
        self.client = client
        self.parent = parent

    def name(self, id: str, parent: Optional[str] = None) -> str:
        """Generates a resource name from parent and id.

        Adds wildcard for any missing parent elements.

        Arguments:
            id: Name or id of resource.
            parent: (Optional) Override parent name.
        """
        if "/" in id:
            # Don't allow names to override manager parent config since this is confusing
            # and is typically a bug in the user code.
            if parent is not None and parent != "" and not id.startswith(parent):
                raise ValueError(f"Resource {id} not a child of {parent}.")
            return id
        pattern_parts = self.name_pattern.split("/")
        parent = parent or self.parent or ""
        parent_parts = parent.split("/")
        out = []
        for i in range(len(pattern_parts)):
            if (i + 1) % 2 == 0:
                if i < len(parent_parts):
                    out.append(parent_parts[i])
                else:
                    out.append("-")
            else:
                out.append(pattern_parts[i])
        out[-1] = id
        return "/".join(out)
