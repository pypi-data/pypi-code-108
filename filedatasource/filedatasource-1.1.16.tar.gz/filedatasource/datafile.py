from abc import ABC, ABCMeta, abstractmethod
from enum import Enum, unique, auto
from typing import List, Union, TextIO, BinaryIO, Any, Dict, Sequence, Callable

from filedatasource.utils import dict2obj, attributes2list, attributes2dict, dict2list, dict_keys2list


@unique
class Mode(Enum):
    """ The file open mode. """
    APPEND = 'a'  # To append at the end of the file.
    WRITE = 'w'  # To start a new file, this will destroy the previous one with the same name.
    READ = 'r'  # To read the file.


@unique
class ReadMode(Enum):
    """ Modes which DataReader will return the rows. """
    OBJECT = auto()  # Return each row as object with attributes
    DICT = auto()  # Return each row as dictionary
    LIST = auto()  # Return each row as list of values


class DataSourceError(Exception):
    pass


class DataFile(ABC):
    """
    Abstract class for object that deals with data files.
    """
    __metaclass__ = ABCMeta

    @property
    @abstractmethod
    def fieldnames(self) -> List[str]:
        """ :return: The sequence of field names to use as CSV head. """
        pass

    @property
    def file_name(self) -> str:
        """ :return: The file name. """
        return self._fname

    def __init__(self, file_or_io: Union[str, TextIO, BinaryIO]) -> None:
        """ Constructor.
        :param file_or_io: The file path to the Data file.
        """
        self._fname = file_or_io if isinstance(file_or_io, str) else None
        self._file_stream = file_or_io if not isinstance(file_or_io, str) else None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    @abstractmethod
    def close(self) -> None:
        """ This method is called when finishes with this object, usually to close the file. """
        pass


class DataWriter(DataFile, ABC):
    __metaclass__ = ABCMeta

    @property
    def mode(self) -> Mode:
        return self.__mode

    def __init__(self, file_or_io: Union[str, TextIO, BinaryIO], mode: Mode):
        super(DataWriter, self).__init__(file_or_io)
        self.__check_mode(mode)
        self.__mode = mode

    def __check_mode(self, mode):
        if mode not in [Mode.WRITE, Mode.APPEND]:
            raise ValueError(f'The {type(self).__name__} only allows modes {Mode.WRITE} or {Mode.APPEND}, not {mode}')
        f_mode = self._file_stream.mode.strip() if self._file_stream and hasattr(self._file_stream, 'mode') else None
        if f_mode and mode == Mode.WRITE and f_mode[0] != 'w':
            raise ValueError(f'The reader is in mode {mode} but the file stream is in not in write mode ("{f_mode}").')
        if f_mode and mode == Mode.APPEND and f_mode[0] != 'a':
            raise ValueError(f'The reader is in mode {mode} but the file stream is in not in append mode ("{f_mode}").')

    @staticmethod
    def _parse_fieldnames(fieldnames: Union[List[str], Dict, object]) -> List[str]:
        """ Convert the fieldnames if their are defined as a dict or an object with attributes or properties in
        a list of fieldnames without values.
        If this argument is already a list, then return it without any modification.

        :param fieldnames: A list, dictionary or object.
        :return: A list of strings that represent the fieldnames.
        """
        if isinstance(fieldnames, List):
            return fieldnames
        if isinstance(fieldnames, dict):
            return dict_keys2list(fieldnames)
        if isinstance(fieldnames, object):
            return attributes2list(fieldnames)
        return []

    def write(self, o: Union[List, dict, object]) -> None:
        """ Write a row.

        :param o: A list, a dictionary or an object with the values of the row to store.
        """
        if isinstance(o, List):
            self.write_list(o)
        elif isinstance(o, dict):
            self.write_dict(o)
        else:
            self.write_object(o)

    @abstractmethod
    def write_row(self, **row) -> None:
        """ Write a row.

        :param row: The dictionary or parameters to write.
        """
        pass

    def write_dict(self, row: dict) -> None:
        """ Write a dictionary as a row.

        :param row: A dictionary with the fieldnames as a key and the row data as the dictionary values.
        """
        self.write_row(**row)

    def write_dicts(self, rows: Sequence[dict]) -> None:
        """ Write a list of dictionaries.

        :param rows:  The list of dictionaries. Each dictionary has to contain as keys the fieldnames and as value
        the row data to store.
        """
        for row in rows:
            self.write_dict(row)

    def write_object(self, o: object) -> None:
        """ Write an objects.

        :param o: The objects to write with public attributes or properties.
        """
        self.write_row(**attributes2dict(o))

    def write_objects(self, objects: Sequence[object]) -> None:
        """ Write a sequence of objects.

        :param objects: The sequence of objects to write with public attributes or properties.
        """
        for o in objects:
            self.write(o)

    def write_list(self, lst: list) -> None:
        """ Write a list of values.

        :param lst: The list of values. It is going to store in the same order than the fieldnames.
        """
        self.write_dict({field: lst[i] for i, field in enumerate(self.fieldnames) if i < len(lst)})

    def write_lists(self, lists: Sequence[list]) -> None:
        """ Write a sequences of lists as a sequence of rows

        :param lists: The sequence of rows as lists.
        """
        for lst in lists:
            self.write_list(lst)

    def import_reader(self, reader: 'DataReader') -> None:
        """ Import the content of a reader in this writer.

        :param reader: The reader to import.
        """
        for obj in reader:
            self.write(obj)


class DataReader(DataFile, ABC):
    """ A data reader to read very easy a file with data, usually, the typical CSV or Excel files. """
    __metaclass__ = ABCMeta

    def __init__(self, file_or_io: Union[str, TextIO, BinaryIO], mode: ReadMode = ReadMode.OBJECT) -> None:
        """ Constructor.

        :param file_or_io: The file or the IO stream to read.
        :param mode: The default mode to read the rows. When the reader is iterated,
        it will return objects, dictionaries or lists depending on if the value of this parameter is ReadMode.OBJECT,
        ReadMode.DICTIONARY or ReadMode.LIST, respectively.
        """
        super(DataReader, self).__init__(file_or_io)
        if mode not in [elem for elem in ReadMode]:
            ValueError(f'The mode argument must be ReadMode.OBJECT, ReadMode.DICT or ReadMode.LIST instead of {mode}.')
        self.__mode = mode

    def __iter__(self):
        return self

    def __next__(self):
        return self.read()

    def read(self) -> object:
        """ Read a row of the CSV file.

        :return: An Python object with fields that represents the information of the file. The name of these fields
        correspond with the name of the CSV head fields.
        """
        if self.__mode == ReadMode.DICT:
            return self.read_row()
        elif self.__mode == ReadMode.OBJECT:
            return self.read_object()
        return self.read_list()

    @abstractmethod
    def read_row(self) -> dict:
        """ Read a row of the file as a dict.

        :return: It must to return a dictionary where the keys are the fieldnames, and their values the row values.
        """
        pass

    def read_rows(self) -> List[dict]:
        """ Read the whole file and return a list of dictionaries with each one of the file rows.

        :return: A list of dictionaries that represents the list of file rows.
        """
        return self.__read_lists(self.read_row)

    def read_list(self) -> list:
        """ Read a row of the CSV file as a list.

        :return: A list of values with the data of each column of the file row.
        """
        return dict2list(self.read_row())

    def read_lists(self) -> List[list]:
        """ Read the whole file and return a list of lists with each one of the file rows.

        :return: A list of lists that represents the list of file rows.
        """
        return self.__read_lists(self.read_list)

    def read_object(self) -> object:
        """ Read a row of the CSV file as a Python object.

        :return: A list of object with the fieldnames as object attributes and of each column value as their values.
        If there is any character that cannot be represented as a Python identifier, it is changed by underscore '_'.
        If the name of the column starts with number, then a 'n' character is added.
        """
        return dict2obj(self.read_row())

    def read_objects(self) -> List[object]:
        """ Read the whole file and return a list of Python objects with each one of the file rows.

        :return: A list of objects that represents the list of file rows. See read_object() method for further
        information.
        """
        return self.__read_lists(self.read_object)

    @staticmethod
    def __read_lists(func: Callable) -> List[Any]:
        """ Call the function until it returns a StopIteration exception. Then, this method returns a list with
        the results of the each function call.

        :param func: The function to call.
        :return: A list of results.
        """
        lst = []
        try:
            while True:
                result = func()
                lst.append(result)
        except StopIteration:
            return lst
