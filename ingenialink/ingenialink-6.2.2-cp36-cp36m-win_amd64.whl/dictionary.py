from abc import ABC, abstractmethod


class Categories(ABC):
    """Categories Abstract Base Class.

    Args:
        dictionary (Dictionary): Ingenia dictionary instance.

    """
    def __init__(self, dictionary):
        self._dictionary = dictionary

    @abstractmethod
    def labels(self, category_id):
        raise NotImplementedError

    @property
    def category_ids(self):
        raise NotImplementedError


class Dictionary(ABC):
    """Ingenia dictionary Abstract Base Class.

    Args:
        dictionary_path (str): Dictionary file path.

    Raises:
        ILCreationError: If the dictionary could not be created.

    """
    def __init__(self, dictionary_path):
        self.path = dictionary_path
        """str: Path of the dictionary."""
        self.version = None
        """str: Version of the dictionary."""
        self.firmware_version = None
        """str: Firmware version declared in the dictionary."""
        self.product_code = None
        """int: Product code declared in the dictionary."""
        self.part_number = None
        """str: Part number declared in the dictionary."""
        self.revision_number = None
        """int: Revision number declared in the dictionary."""
        self.interface = None
        """str: Interface declared in the dictionary."""
        self.subnodes = None
        """int: Number of subnodes in the dictionary."""
        self.categories = None
        """Categories: Instance of all the categories in the dictionary."""
        self.errors = None
        """Errors: Instance of all the errors in the dictionary."""

    @abstractmethod
    def registers(self, subnode):
        raise NotImplementedError
