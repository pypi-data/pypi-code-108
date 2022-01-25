"""
    Xpress Insight Python package
    =============================

    This is an internal file of the 'xpressinsight' package. Do not import it directly.
    Offline interface definition.

    This material is the confidential, proprietary, unpublished property
    of Fair Isaac Corporation.  Receipt or possession of this material
    does not convey rights to divulge, reproduce, use, or allow others
    to use it without the specific written authorization of Fair Isaac
    Corporation and use must conform strictly to the license agreement.

    Copyright (c) 2021-2022 Fair Isaac Corporation. All rights reserved.
"""
from __future__ import annotations

from xpressinsight.types import check_simple_python_type


class RepositoryPath:
    """
    The RepositoryPath class can be used to build, analyze, and modify a repository path.

    Examples
    --------
    The following example shows how to build, analyze, and modify a path.

    >>> import xpressinsight as xi
    ... path_str = str(xi.RepositoryPath.encode(
    ...     ['App 1', 'Scenario 2021/09'],
    ...      is_absolute=True))
    ... print(path_str)
    /App 1/Scenario 2021\/09

    >>> path = xi.RepositoryPath(path_str)
    ... print('absolute:', path.is_absolute)
    ... print('decoded elements:', path.decode())
    absolute: True
    decoded elements: ['App 1', 'Scenario 2021/09']

    >>> path.pop()
    ... path.append('Optimization 2021/10')
    ... print(str(path))
    /App 1/Optimization 2021\/10

    See Also
    --------
    RepositoryPath.encode
    RepositoryPath.__init__
    ItemInfo
    """
    __is_absolute: bool
    __encoded_elements: list[str]

    @staticmethod
    def __validate_path_chars(path: str):
        """
        The function validates the characters in the input string: it does not allow ISO control characters,
        i.e., 0-31 and 127 are not allowed.

        Parameters
        ----------
        path : str
            The path to validate.

        Raises
        ------
        ValueError
            If the string contains control characters.
        """
        if any(c <= '\u001F' or c == '\u007F' for c in path):
            raise ValueError(f'A repository path cannot contain control characters (0-31 and 127). Path: {repr(path)}')

    @staticmethod
    def encode_element(unencoded_element: str) -> str:
        """
        Encode the name of a repository item such that it can be used as a repository path string element.

        Parameters
        ----------
        unencoded_element : str
            Unencoded repository path string element (e.g. app name, folder name, or item name).

        Returns
        -------
        encoded_element : str
            Encoded repository path string element.

        Notes
        -----
        The function first escapes each backslash and then each slash.

        See Also
        --------
        RepositoryPath.append
        RepositoryPath.decode_element
        RepositoryPath.encode
        RepositoryPath.decode
        """
        check_simple_python_type(unencoded_element, 'unencoded_element', str)
        return unencoded_element.replace('\\', '\\\\').replace('/', '\\/')

    @staticmethod
    def decode_element(encoded_element: str) -> str:
        """
        Get the item name that is represented by the given encoded repository path string element.

        Parameters
        ----------
        encoded_element : str
            Encoded repository path string element excluding a leading or tailing
            path element separator (slash "/").

        Returns
        -------
        decoded_element : str
            Decoded repository path string element (e.g. app name, folder name, or item name).

        Notes
        -----
        The function first unescapes each escaped slash and then each escaped backslash.

        Raises
        ------
        ValueError
            If the path is empty or contains an invalid character or escape sequence.

        See Also
        --------
        RepositoryPath.pop
        RepositoryPath.encode_element
        RepositoryPath.encode
        RepositoryPath.decode
        """
        return encoded_element.replace('\\/', '/').replace('\\\\', '\\')

    def __init__(self, path: str):
        """
        Creates a RepositoryPath object from the give path string.

        Parameters
        ----------
        path : str
            Repository path string. The path elements must be seperated by a slash "/". In path elements,
            the special characters backslash and slash must be escaped with the help of a backslash.

        See Also
        --------
        RepositoryPath.encode
        RepositoryPath.is_absolute
        RepositoryPath.elements
        RepositoryPath.abspath
        """
        self.__is_absolute: bool = False
        self.__encoded_elements: list[str] = []

        check_simple_python_type(path, 'path', str)
        RepositoryPath.__validate_path_chars(path)

        i = 0
        j = 0
        len_path = len(path)

        while j < len_path:
            c = path[j]

            if c == '/':
                if i < j:
                    self.__encoded_elements.append(path[i:j])
                elif j == 0:
                    self.__is_absolute = True

                i = j+1
            elif c == '\\':
                j += 1

                if j == len_path or path[j] not in ['\\', '/']:
                    raise ValueError(f'Invalid escape sequence "{path[j-1:j+1]}" at position {j} '
                                     f'in repository path. Only "\\\\" and "\\/" are supported. Path: {path}')

            j += 1

        if i < len_path:
            self.__encoded_elements.append(path[i:j])

    @staticmethod
    def encode(unencoded_elements: list[str], is_absolute: bool = True) -> RepositoryPath:
        """
        Encode the elements of a path and append them to a new path.

        Parameters
        ----------
        unencoded_elements : list[str]
            Unencoded repository path string elements (e.g. app name, folder name, or item name).

        is_absolute : bool = True
            Whether the returned path shall be absolute or relative.

        Returns
        -------
        path : RepositoryPath
            A new repository path containing the encoded elements.

        See Also
        --------
        RepositoryPath.__init__
        RepositoryPath.abspath
        RepositoryPath.decode
        RepositoryPath.encode_element
        """
        check_simple_python_type(unencoded_elements, 'unencoded_elements', list)
        check_simple_python_type(is_absolute, 'is_absolute', bool)

        path = RepositoryPath('/' if is_absolute else '')

        for unencoded_element in unencoded_elements:
            path.append(unencoded_element)

        return path

    @property
    def is_absolute(self) -> bool:
        """ True if the path starts with a path element separator (slash "/"). """
        return self.__is_absolute

    def decode(self) -> list[str]:
        """
        Get the list of decoded path string elements of the RepositoryPath.

        See Also
        --------
        RepositoryPath.elements
        RepositoryPath.decode_element
        """
        return [RepositoryPath.decode_element(element) for element in self.__encoded_elements]

    @property
    def elements(self) -> list[str]:
        """
        Get the list of encoded path string elements of the RepositoryPath.

        See Also
        --------
        RepositoryPath.append
        RepositoryPath.pop
        RepositoryPath.decode
        RepositoryPath.encode
        RepositoryPath.__init__
        """
        return self.__encoded_elements.copy()

    def __str__(self) -> str:
        path = '/'.join(self.__encoded_elements)

        if self.is_absolute:
            return '/' + path
        else:
            return path

    def __repr__(self) -> str:
        return f'xpressinsight.RepositoryPath({repr(str(self))})'

    def pop(self) -> str:
        """
        Remove the last element of the path.

        Returns
        -------
        encoded_path_element : str
            Encoded path element which has been removed from
            the end of the list of repository path elements.

        Raises
        ------
        ValueError
            If the path is empty.

        See Also
        --------
        RepositoryPath.elements
        RepositoryPath.append
        """
        if len(self.__encoded_elements) == 0:
            raise ValueError(f'Cannot pop element from empty path.')

        return self.__encoded_elements.pop()

    def append(self, unencoded_element: str) -> None:
        """
        Append an unencoded repository path string element (e.g. an item name) to the end of the RepositoryPath.

        Parameters
        ----------
        unencoded_element : str
            Unencoded repository path string element (e.g. an item name).

        See Also
        --------
        RepositoryPath.elements
        RepositoryPath.pop
        """
        encoded_element = RepositoryPath.encode_element(unencoded_element)

        if encoded_element != '':
            self.__encoded_elements.append(encoded_element)

    def __abspath_raw(self, current_dir: RepositoryPath) -> RepositoryPath:
        """
        Get the absolute path of a repository path.

        Parameters
        ----------
        current_dir : RepositoryPath
            Absolute path to the current working directory in the repository.

        Returns
        -------
        raw_absolute_path : RepositoryPath
            Raw absolute path, still containing "." and ".." elements.

        Raises
        ------
        ValueError
            If `current_dir` is relative (only raised if `self` is also relative).
        """
        new_path = RepositoryPath('/')

        if not self.is_absolute:
            check_simple_python_type(current_dir, 'current_dir', RepositoryPath)

            if not current_dir.is_absolute:
                raise ValueError('RepositoryPath "current_dir" must be absolute.')

            new_path.__encoded_elements.extend(current_dir.__encoded_elements)

        new_path.__encoded_elements.extend(self.__encoded_elements)
        return new_path

    def abspath(self, current_dir: RepositoryPath) -> RepositoryPath:
        """
        Get a normalized absolute version of the path.
        In particular, process "." and ".." path elements.

        Parameters
        ----------
        current_dir : RepositoryPath
            Absolute path to the current working directory in the repository.

        Returns
        -------
        absolute_path : RepositoryPath
            Normalized absolute path without "." and ".." elements.

        Raises
        ------
        ValueError
            If the path contains too many ".." elements or the current directory is not absolute.

        See Also
        --------
        RepositoryPath.__init__
        RepositoryPath.encode
        """
        abs_path = self.__abspath_raw(current_dir)
        new_path = RepositoryPath('/')

        for element in abs_path.__encoded_elements:
            if element == '..':
                try:
                    new_path.pop()
                except ValueError as e:
                    raise ValueError(f'Cannot resolve repository path. '
                                     f'Too many ".." elements in: {str(abs_path)}') from None
            elif element != '.':
                new_path.__encoded_elements.append(element)

        return new_path
