"""
Nozomi
Render Dependency Module
Author: hugh@blinkybeach.com
"""


class RenderDependency:
    """
    Abstract class providing underlying functionality for rendering
    dependencies built from files.
    """

    _DEFAULT_NAME = 'Render Dependency'

    def __init__(
        self,
        script_name: str,
        extension: str,
        path: str,
        name: str = None,
    ):
        assert isinstance(extension, str)
        assert isinstance(script_name, str)

        assert extension[:1] == '.'

        self._extension = extension
        self._name = name if name is not None else self._DEFAULT_NAME

        assert isinstance(script_name, str)
        self._script_name = script_name

        assert isinstance(path, str)
        if path[-1] != '/':
            path += '/'

        self._full_path = path + self._script_name + self._extension
        self._content = self._load_file(self._full_path)
        return

    def _load_file(self, full_path) -> str:
        """
        Return a file's contents as a string
        """
        with open(full_path, 'r') as file:
            return file.read()

    def __str__(self) -> str:
        return self._content

    def __repr__(self) -> str:
        return self._name + ': ' + self._script_name + self._extension
