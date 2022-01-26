import gzip
from abc import ABC, ABCMeta
from csv import DictWriter, DictReader
from typing import Union, TextIO, BinaryIO, List, Type, Dict

from filedatasource.datafile import DataReader, DataWriter, ReadMode, DataSourceError, Mode, DataFile


def open_file(fname: str, mode: Mode, encoding: str = 'utf-8'):
    """ Method to open a file depending on if it is compress with gzip or not.
    :param fname: The path to the file.
    :param mode: The open mode: Mode.APPEND, Mode.WRITE or Mode.READ.
    :param encoding: The file encoding.
    :return: A stream.
    """
    open_func = gzip.open if fname.lower().endswith('.gz') else open
    return open_func(fname, f'{mode.value}t', encoding=encoding, newline='')


class CsvData(DataFile, ABC):
    """ Abstract class for object that deals with CSV files. """
    __metaclass__ = ABCMeta

    @property
    def encoding(self) -> str:
        """
        :return: The file encoding.
        """
        return self.__encoding

    def __init__(self, file_or_io: [str, TextIO, BinaryIO], mode: Mode, encoding: str = 'utf-8'):
        """ Constructor.

        :param file_or_io: The file path or the file stream.
        :param mode: The open mode: Mode.APPEND, Mode.WRITE or Mode.READ.
        :param encoding: The file encoding.
        """
        DataFile.__init__(self, file_or_io)
        self.__encoding = encoding
        self._file = open_file(file_or_io, mode, self.encoding) if isinstance(file_or_io, str) else file_or_io

    def close(self) -> None:
        """ Close the file stream. """
        self._file.close()


class CsvWriter(CsvData, DataWriter):
    """
    A CSV writer to create a typical CSV file with head. It is very easy to use, only need to

    .. code-block:: python

        fieldnames = ['id', 'name', 'surname', 'address']
        with ConflictsWriter('data.csv', fieldnames) as writer:
            writer.write_row(id=1, name='John', surname='Smith', address='Oxford street')

    Also, if the file ends with .gz, the file will be compressed with gzip automatically.
    """
    @property
    def fieldnames(self) -> List[str]:
        """
        :return: The sequence of field names to use as CSV head.
        """
        return self._fieldnames

    def __init__(self, file_or_io: Union[str, TextIO, BinaryIO], fieldnames: Union[List[str], type, object] = None,
                 mode: Mode = Mode.WRITE, encoding: str = 'utf-8') -> None:
        """ Constructor of this CSV writer.

        :param file_or_io: The file path or an opened stream to use. If it is a file path and it ends in .gz, then
        a compressed file is created using gzip.
        :param fieldnames: The field names of this CSV.
        :param mode: The writing mode: Mode.APPEND or Mode.WRITE. By default Mode.WRITE.
        :param encoding: The encoding (it is only used if the parameter file_or_io is a file path).
        :raises ValueError: If mode is not Mode.WRITE or Mode.APPEND or if file_or_io is a file stream with
          write or append modes but this modes does not correspond to the mode parameter.
        """
        CsvData.__init__(self, file_or_io, mode, encoding)
        DataWriter.__init__(self, file_or_io, mode)
        self._fieldnames = self._parse_fieldnames(fieldnames)

        self._writer = DictWriter(self._file, fieldnames=self.fieldnames)
        if mode == Mode.WRITE:
            self._writer.writeheader()
            self.__num_row = 0
        else:
            self.__num_row = None

    def write_row(self, **row) -> None:
        """ Write a row.

        :param row: The dictionary or parameters to write.
        """
        self._writer.writerow(row)
        if self.__num_row is not None:
            self.__num_row += 1

    def __len__(self) -> int:
        """
        Calculate the number of rows in the file.
        :return: The number of rows in the data source.
        :raises DataFileError: If with this data source is not possible to calculate the number of rows.
          It is not possible to calculate if this comes from a file stream and it is opened as APPEND mode.
        """
        if self.__num_row is None:
            if self.file_name:
                with CsvReader(self.file_name, encoding=self.encoding) as reader:
                    self.__num_row = len(reader)
            else:
                raise DataSourceError(
                    f'The length of the data source cannot be computed if it is defined as a file stream, '
                    f'instead of a file path and this writer is opened in APPEND mode.')
        return self.__num_row


class CsvReader(CsvData, DataReader):
    """
    A CSV reader to read a typical CSV file with head. It is very easy to use. For example, if the file 'data.csv'
    contains:

    .. code-block:: text

        id,name,surname,address
        1,John,Smith,Oxford street
        ---

    It is only necessary to write:

    .. code-block:: python

        with ConflictsWriter('data.csv') as reader:
            for row in reader:
                print(row.id, row.name, row.surname, row.address)

    Also, if the file ends with .gz, the file will be read from a compressed file with gzip automatically.
    """
    @property
    def fieldnames(self) -> List[str]:
        """
        :return: The sequence of field names to use as CSV head.
        """
        return list(self._reader.fieldnames)

    def __init__(self, file_or_io: Union[str, TextIO, BinaryIO], mode: ReadMode = ReadMode.OBJECT,
                 encoding: str = 'utf-8', types: Union[List[Type], Dict[str, Type]] = None):
        """ Constructor of this CSV reader.

        :param file_or_io: The file path or an opened stream to use. If it is a file path and it ends in .gz, then
        the compressed file is read using gzip.
        :param encoding: The encoding (it is only used if the parameter file_or_io is a file path).
        :param mode: The default mode to read the rows. When the reader is iterated,
          it will return objects, dictionaries or lists depending on if the value of this parameter is ReadMode.OBJECT,
          ReadMode.DICTIONARY or ReadMode.LIST, respectively.
        :param types: The type of each field.
        :raises ValueError: If the read mode is not ReadMode.OBJECT, ReadMode.DICT or ReadMode.LIST.
        """
        if mode not in [ReadMode.OBJECT, ReadMode.DICT, ReadMode.LIST]:
            raise ValueError(f'The read mode only can be ReadMode.OBJECT, ReadMode.DICT or ReadMode.LIST, not {mode}.')
        super(CsvReader, self).__init__(file_or_io, Mode.READ, encoding)
        DataReader.__init__(self, file_or_io, mode)
        self._reader = DictReader(self._file)
        self.__length = None
        if types and not isinstance(types, List) and not isinstance(types, Dict):
            raise ValueError('If the parameter types is defined, it must be a list o dict.')
        self.__types = types if types else []

    def read_row(self) -> dict:
        """ Read a row of the CSV file.

        :return: An Python dictionary with fields that represents the information of the file. The name of these fields
        correspond with the name of the CSV head fields.
        """
        d = next(self._reader)
        if not self.__types:
            return d
        if isinstance(self.__types, List):
            return {k: (self.__types[i](v) if i < len(self.__types) else v) for i, (k, v) in enumerate(d.items())}

        return {k: (self.__types[k](v) if k in self.__types else v) for k, v in d.items()}

    def __len__(self) -> int:
        """ Calculate the number of rows. The first time you call this method it read the whole file once and
        it could do the algorithm a little bit slower.

        :return: The number of rows.
        :raises DataFileError: If with this data source is not possible to calculate the number of rows.
          It is not possible to calculate if this comes from a file stream.
        """
        if self.__length:
            return self.__length
        if self.file_name:
            with CsvReader(self.file_name, ReadMode.DICT, self.encoding) as reader:
                self.__length = sum(1 for _ in reader)
                return self.__length
        # return self.__length
        raise DataSourceError(f'The length of the data source cannot be computed if it is defined as a file stream '
                              f'instead of a file path.')
