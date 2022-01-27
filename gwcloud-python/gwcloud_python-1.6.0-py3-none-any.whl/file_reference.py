from dataclasses import dataclass, field
from collections import UserList
from pathlib import Path
from .utils import remove_path_anchor, file_filters


@dataclass
class FileReference:
    """Object used to facilitate simpler downloading of files.
    """
    path: str
    file_size: int = field(repr=False)
    download_token: str = field(repr=False)

    def __post_init__(self):
        self.path = remove_path_anchor(Path(self.path))
        self.file_size = int(self.file_size)


class FileReferenceList(UserList):
    """Used to store FileReference objects and provide simple methods with which to obtain their data.
    As a subclass of ~collections.UserList, this class contains the same functionality as a regular list.
    It also contains several other useful methods.

    Parameters
    ----------
    initlist : list
        List of FileReference objects
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for item in self.data:
            if not isinstance(item, FileReference):
                raise Exception('FileReferenceList must be initialised with a list of FileReference objects')

    def append(self, item):
        """Use as you would list.append()

        Parameters
        ----------
        item : FileReference
            If this is not a FileReference instance, the method will fail

        Raises
        ------
        Exception
            Raised if item is not a FileReference
        """
        if not isinstance(item, FileReference):
            raise Exception('Appended item must be a FileReference object')
        self.data.append(item)

    def filter_list(self, file_filter_fn, *args, **kwargs):
        """Create a subset of this list by filtering the contents with a function.

        Parameters
        ----------
        file_filter_fn : function
            Must take a list of FileReference objects and return only those that are desired

        Returns
        -------
        FileReferenceList
            Filtered list
        """
        return FileReferenceList(file_filter_fn(self.data, *args, **kwargs))

    def filter_list_by_path(self, directory=None, name=None, extension=None):
        """Create a subset of this list by filtering the contents based on their path attributes

        Parameters
        ----------
        directory : str, optional
            Matches any of the directories in the file path, by default None
        name : str, optional
            Matches the name of the file, by default None
        extension : str, optional
            Matches the file extension, by default None

        Returns
        -------
        FileReferenceList
            Filtered list
        """
        return self.filter_list(file_filters.custom_path_filter, directory, name, extension)

    def get_total_bytes(self):
        """Sum the total size of each file represented in the list

        Returns
        -------
        int
            Total size of all files
        """
        total_bytes = 0
        for ref in self.data:
            total_bytes += ref.file_size

        return total_bytes

    def get_tokens(self):
        """Get all the download tokens in a list

        Returns
        -------
        list
            List of download tokens
        """
        return [ref.download_token for ref in self.data]

    def get_paths(self):
        """Get all the file paths in a list

        Returns
        -------
        list
            List of file paths
        """
        return [ref.path for ref in self.data]

    def get_output_paths(self, root_path, preserve_directory_structure=True):
        """Get all the file paths modified to give them a base directory.
        Can also optionally remove any existing directory structure

        Parameters
        ----------
        root_path : str or ~pathlib.Path
            Directory to add to the beginning of the file paths
        preserve_directory_structure : bool, optional
            Retain existing directory structure in the file paths, by default True

        Returns
        -------
        list
            List of output file paths
        """
        paths = []
        for ref in self.data:
            if preserve_directory_structure:
                paths.append(root_path / ref.path)
            else:
                paths.append(root_path / Path(ref.path.name))
        return paths
