"""Containers"""


from typing import Callable, Iterable, List, Any


class Array:
    """Class for array functionality"""

    def __init__(self, iterable: Iterable[Any]) -> None:
        self.iterable = iterable

    def filter(self, func: Callable):
        """Filter the array using a provided lambda function

        Args:
            func (Callable): Function or lambda function to use to filter

        Returns:
            Array: Array of filtered items
        """
        return Array(list(filter(func, self.iterable)))

    def map(self, func: Callable):
        """Apply a function to each entry in the array

        Args:
            func (Callable): Function or lambda function to apply

        Returns:
            Array: Array of mapped items
        """
        return Array([func(x) for x in self.iterable])

    def flatten(self):
        """Flattens a list of lists into a single list

        Returns:
            Array: Array of the flattened lists
        """
        return Array([item for sublist in self.iterable for item in sublist])

    def all(self) -> List[Any]:
        """Returns all the items as a Python list

        Returns:
            list: Python list of items in the array
        """
        return self.iterable

    def length(self) -> int:
        """Returns the length of the array

        Returns:
            int: Number of items in array
        """
        return len(self.iterable)

    def get(self, index: int):
        """Get the item at the index number provided

        Args:
            index (int): Index of item

        Returns:
            Any: Item at index
        """
        try:
            return self.iterable[index]
        except IndexError:
            return None

    def first(self) -> Any:
        """Gets the first item in the array

        Returns:
            Any: Item in the array
        """
        try:
            return self.iterable[0]
        except IndexError:
            return None
