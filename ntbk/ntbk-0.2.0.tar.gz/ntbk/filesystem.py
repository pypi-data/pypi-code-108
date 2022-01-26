"""Provides Fileystem class for interacting with the filesystem"""

# system imports
import subprocess
from pathlib import Path


class Filesystem():
    """This class should always be used to retrieve paths and create files

    Arguments:
        config -- Config instance
    """

    def __init__(self, config):
        self.config = config

    def get_notebook_base_path(self):
        """Get the pathlib.Path object to the notebook root folder"""
        return Path(self.config.get('ntbk_dir')).expanduser()

    def get_collection_base_path(self):
        """Get the pathlib.Path object to the collections folder"""
        return self.get_notebook_base_path() / 'collections'

    def get_log_base_path(self):
        """Get the pathlib.Path object to the log folder"""
        return self.get_notebook_base_path() / 'log'

    def get_templates_base_path(self):
        """Get the pathlib.Path object to the _templates folder (or whatever is configured)"""
        return self.get_notebook_base_path() / self.config.get('template_dir')

    def create_file(self, filepath, content=None): #pylint: disable=no-self-use
        """Create a file. Parent directories will be created.

        Arguments:
            filepath -- Path object to file
            content -- optional content to write to file
        """
        filepath.parent.mkdir(parents=True, exist_ok=True)

        if content is not None:
            filepath.write_text(content)
        else:
            filepath.touch()

    def append_to_file(self, filepath, content): #pylint: disable=no-self-use
        """Write content to the end of the given file (filepath must be a Path object)

        Arguments:
            filepath -- Path object to the file
            content -- string content to write to the file
        """
        # in case the parent directories don't exist yet
        filepath.parent.mkdir(parents=True, exist_ok=True)

        with filepath.open(mode='a') as file:
            file.write(content)

    def open_file_in_editor(self, path):
        """Open the given path in the configured editor.

        Arguments:
            path -- String or Path object. Must be the absolute path
        """
        subprocess.run([self.config.get('editor'), path])
