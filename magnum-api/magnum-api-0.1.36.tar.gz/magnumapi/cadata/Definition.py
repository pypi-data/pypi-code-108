from dataclasses import dataclass
from abc import ABC, abstractmethod


@dataclass
class Definition(ABC):
    """Base class for a definition.

       Attributes:
           name (str): The name of a definition (serves as a primary key).
           comment (str): The comment.
    """
    name: str
    comment: str

    @staticmethod
    @abstractmethod
    def get_magnum_to_roxie_dct():
        """ Method returning a mapping from MagNum naming convention to ROXIE naming convention.

        :return: a dictionary from MagNum to ROXIE names
        """
        raise NotImplementedError('This method is not implemented for this class')

    @classmethod
    def get_roxie_to_magnum_dct(cls):
        """ Method returning a mapping from ROXIE naming convention to MagNum naming convention. In case there is a
        field not present in ROXIE but present in MagNum, then its default value is None.

        :return: a dictionary from ROXIE to MagNum names
        """
        return {val: key for key, val in cls.get_magnum_to_roxie_dct().items() if val is not None}

    @classmethod
    def reorder_dct(cls, dct: dict) -> dict:
        """ Method reordering an input dictionary to follow ROXIE ordering and magnum naming convention. The reason for
        this is the use of inheritance which does not follow the ROXIE ordering.

        :param dct:
        :return:
        """
        for key in cls.get_magnum_to_roxie_dct().keys():
            dct[key] = dct.pop(key)
        return dct
