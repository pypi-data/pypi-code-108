from __future__ import annotations
import typing

# Required to avoid circular dependency issues:
# https://www.stefaanlippens.net/circular-imports-type-hints-python.html
if typing.TYPE_CHECKING:
    from continual.python.sdk.client import Client


class Resource:
    """Base resource class."""

    name: str
    name_pattern: str

    @classmethod
    def make_name(cls, parent: str, id: str) -> str:
        """Generates a resource name from parent and id.

        Adds wildcard for any missing parent elements.

        Arguments:
            parent: Parent resource name.
            id: Resource id.

        Returns:
            Resource name.
        """
        pattern_parts = cls.name_pattern.split("/")
        parent = parent or ""
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

    @property
    def id(self) -> str:
        """ID of resource."""
        return self.name.split("/").pop()

    @property
    def parent(self) -> str:
        """Parent resource name."""
        return "/".join(self.name.split("/")[0:-2])

    @property
    def client(self) -> Client:
        """Continual Client object."""
        return self._client
