"""NanamiLang Contrib :: Window Data Structure"""

# This file is a part of NanamiLang Project
# This project licensed under GNU GPL version 2
# Initially made by @jedi2light (aka Stoian Minaiev)
# But! This particular module is licensed under WTFPL


class Window:
    """NanamiLang Window Data Structure Class"""

    _size: int = None
    _container: list = None

    def __init__(self, size: int) -> None:
        """
        Initialize new Window Data Structure
        :param size: a fixed size of the container
        """

        assert isinstance(size, int), 'Window: integer expected'

        self._size = size
        self._container = [None] * size

        # Initialize Window with container (list) full of NoneTypes

    def full(self) -> bool:
        """
        Container is full or not?
        :return: container is full or not
        """

        return None not in self._container

    def _nearest_free_position(self) -> int:
        """
        Return nearest free position of container

        :return: nearest free position of container
        """

        for i in range(self._size):
            if self._container[i] is None:
                return i  # <- 'i' stands for actual free position

        return -1  # <- unreachable, but just to make Pylint happy

    def _shift_container_elements(self) -> None:
        """
        Shift container's elements to the right side (last goes away)

        :return: nothing, this method just shifts elements :)
        """

        self._container.append(None)

        for i in range(self._size, -1, -1):
            self._container[i] = None if not i else self._container[i - 1]

        self._container.pop()

        # This algorithm is not smart enough, but it works at least :shrug:

    def push(self, element) -> None:
        """
        i.e.: size is 3

        `[ ... ... ... ] -> [ item ... ... ]`\n
        `[ foo ... ... ] -> [ item foo ... ]`\n
        `[ baz foo ... ] -> [ baz  bar foo ]`\n
        `[ baz bar foo ] -> [ item baz bar ]`\n

        :param element: new element to push
        :return: nothing, this method just pushes element :)
        """

        self._shift_container_elements()
        self._container[self._nearest_free_position()] = element

    def get(self, index: int, default=None):
        """
        Get an element from container by its index (or None)

        :param index: number of the element in self._container
        :param default: default value to return (None by default)
        :return: NoneType or an element by its index from container
        """

        assert isinstance(index, int), 'Window: an index needs to be a number'

        if index not in range(self._size):
            return default

        possible = self._container[index]
        return possible if possible is not None else default

        # Return an element (or default value which is a NoneType) by its index
