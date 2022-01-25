from pathlib import Path

from ._utils import PathType


class BaseArchiveHandler:
    """Base class for dealing with dataice handlers"""

    _archive_type = "base"

    def __init__(self, dir_path: PathType):
        """"""
        self.path = Path(dir_path)

    def save(self, **kwargs):
        """Save objects to file with names from keyword arguments."""
        raise NotImplementedError

    def load(self, args):
        """Load objects from a file with names from keyword arguments."""
        raise NotImplementedError

    def get_object_list(self):
        """Get the list of objects from the archive."""
        raise NotImplementedError
