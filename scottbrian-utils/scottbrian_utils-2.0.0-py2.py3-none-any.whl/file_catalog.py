"""Module file_catalog.

============
file_catalog
============

With **file_catalog**, you can set up a mapping of file names to their
paths. An application can then use the catalog to retrieve the paths
based on the file name. By keeping different catalogs with the same file
names but different paths, different runs of the application can use
each of the different catalogs as appropriate. For example, one catalog
could be used for testing purposes and another for normal production.

:Example: instantiate production and test catalogs for one file

>>> from scottbrian_utils.file_catalog import FileCatalog
>>> prod_cat = FileCatalog({'file1': Path('/prod_files/file1.csv')})
>>> print(prod_cat.get_path('file1'))
/prod_files/file1.csv

>>> test_cat = FileCatalog(
...     {'file1': Path('/test_files/test_file1.csv')})
>>> print(test_cat.get_path('file1'))
/test_files/test_file1.csv


:Example: instantiate a catalog for two files:

>>> a_cat = FileCatalog({'sales': Path('/home/T/files/file1.csv'),
...                      'inventory': Path('/home/T/files/file2.csv')})
>>> print(a_cat)
FileCatalog({'sales': Path('/home/T/files/file1.csv'),
             'inventory': Path('/home/T/files/file2.csv')})

>>> print(a_cat.get_path('inventory'))
/home/T/files/file2.csv

>>> from os import fspath
>>> print(fspath(a_cat.get_path('sales')))
/home/T/files/file1.csv


The file_catalog module contains:

    1) FileCatalog class with add_paths, del_paths,  get_path,
       save_catalog, and load_catalog methods
    2) FileSpec, FileSpecs type aliases that you can use for type hints
    3) Error exception classes:

       a. FileNameNotFound
       b. FileSpecIncorrect
       c. IllegalAddAttempt
       d. IllegalDelAtempt

"""
import csv
from pathlib import Path
from typing import Dict, List, Optional, Type, TYPE_CHECKING

FileSpecs = Dict[str, Path]


class FileCatalogError(Exception):
    """Base class for exceptions in this module."""
    pass


class FileNameNotFound(FileCatalogError):
    """FileNameNotFound when the file name is not in the catalog."""
    pass


class FileSpecIncorrect(FileCatalogError):
    """FileCatalog incorrect file_specs specification."""
    pass


class IllegalAddAttempt(FileCatalogError):
    """FileCatalog attempted add of existing but different path."""
    pass


class IllegalDelAttempt(FileCatalogError):
    """FileCatalog attempted del of existing but different path."""
    pass


class FileCatalog:
    """Provides a mapping of file names to paths.

    This is useful for cases where an application is to be used in
    various environments with files that are in different places.
    Another use is where one set of files is used for normal processing
    and another set is used for testing purposes.
    """

    def __init__(self,
                 file_specs: Optional[FileSpecs] = None
                 ) -> None:
        """Store the input file specs to a data frame.

        Args:
            file_specs: A dictionary of one or more entries. The key is
                          the file name and the value is the path. The
                          file name must be a sting and the path must be
                          a pathlib Path.

        :Example: instantiate a catalog with two files

        >>> from scottbrian_utils.file_catalog import FileCatalog
        >>> a_catalog = FileCatalog(
        ...     {'file_1': Path('/run/media/file1.csv'),
        ...      'file_2': Path('/run/media/file2.pdf')})
        >>> print(a_catalog.get_path('file_2'))
        /run/media/file2.pdf

        """
        self.catalog: Dict[str, Path] = {}
        if file_specs is not None:
            self.add_paths(file_specs)

    def __len__(self) -> int:
        """Return the number of items in the catalog.

        Returns:
            The number of entries in the catalog as an integer

        :Example: instantiate a catalog with three files

        >>> from scottbrian_utils.file_catalog import FileCatalog
        >>> a_catalog = FileCatalog(
        ...     {'file1': Path('/run/media/file1.csv'),
        ...      'file2': Path('/run/media/file2.pdf'),
        ...      'file5': Path('/run/media/file5.csv')})
        >>> len(a_catalog)
        3

        """
        return len(self.catalog)

    def __repr__(self) -> str:
        """Return a representation of the class.

        Returns:
            The representation as how the class is instantiated

        :Example: instantiate a catalog with three files and print it

        >>> from scottbrian_utils.file_catalog import FileCatalog
        >>> a_catalog = FileCatalog(
        ...     {'file1': Path('/run/media/file1.csv'),
        ...      'file2': Path('/run/media/file2.pdf'),
        ...      'file5': Path('/run/media/file5.csv')})
        >>> print(a_catalog)
        FileCatalog({'file1': Path('/run/media/file1.csv'),
                     'file2': Path('/run/media/file2.pdf'),
                     'file5': Path('/run/media/file5.csv')})

        """
        if TYPE_CHECKING:
            __class__: Type[FileCatalog]
        classname = self.__class__.__name__
        indent_spaces = ''  # start with no indent for first entry
        num_entries = len(self)
        num_start_entries = 2
        parms = ''

        for i, (file_name, path) in enumerate(self.catalog.items()):
            # we will do only a few entries at the top, then an ellipse,
            # and finish with the last entry
            if (num_entries <= 4) \
                    or (i < num_start_entries) \
                    or (i == num_entries-1):
                parms = parms + indent_spaces + "'" + file_name \
                         + "': " + "Path(" + "'" + str(path.as_posix()) \
                         + "'),\n"

            # put in the ellipse
            if num_entries > 4:
                if (i == num_start_entries) and (i != num_entries-1):
                    parms = parms + indent_spaces + '...\n'

            # for entries after the first, we need to indent
            indent_spaces = ' ' * (len(classname) + len('({'))

        if parms:  # if we have entries, strip the final comma and newline
            parms = '{' + parms[:-2] + '}'

        return f'{classname}({parms})'

    def get_path(self, file_name: str) -> Path:
        """Obtain a path given a file name.

        Args:
            file_name: The name of the file whose path is needed

        Returns:
            A pathlib Path object for the input file name

        Raises:
            FileNameNotFound: The input file name is not in the catalog

        :Example: instantiate a catalog with two files and get their
                  paths

        >>> from scottbrian_utils.file_catalog import FileCatalog
        >>> a_catalog = FileCatalog(
        ...    {'file1': Path('/run/media/file1.csv'),
        ...     'file2': Path('/run/media/file2.pdf')})
        >>> path1 = a_catalog.get_path('file1')
        >>> print(path1)
        /run/media/file1.csv

        >>> from os import fspath
        >>> fspath(a_catalog.get_path('file2'))
        '/run/media/file2.pdf'

        """
        try:
            return self.catalog[file_name]
        except KeyError:
            raise FileNameNotFound('Catalog does not have an entry for'
                                   f'file name: {file_name}')

    def add_paths(self, file_specs: FileSpecs) -> None:
        """Add one or more paths to the catalog.

        Args:
            file_specs: A dictionary of one or more entries. The key is
                          the file name and the value is the path. The
                          file name must be a sting and the path must be
                          a pathlib Path.

        Raises:
            FileSpecIncorrect: The input path is not a string
            IllegalAddAttempt: Entry already exists with different path

        The entries to be added are specified in the file_specs
        argument. For each file_spec, the specified file name is used to
        determine whether the entry already exists in the catalog. If
        the entry already exists, the specified path is compared against
        the found entry. If they do not match, an IllegalAddAttempt
        exception is raised and no entries for the add_paths request
        will be added. Otherwise, if the path matches, there is no need
        to add it again so processing continues with the next file_spec.
        If no errors are detected for any of the file_specs, any file
        names that do not yet exist in the catalog are added.

        :Example: add some paths to the catalog

        >>> from scottbrian_utils.file_catalog import FileCatalog
        >>> from pathlib import Path
        >>> a_catalog = FileCatalog()
        >>> a_catalog.add_paths({'file1': Path('/run/media/file1.csv')})
        >>> print(a_catalog)
        FileCatalog({'file1': Path('/run/media/file1.csv')})
        >>> a_catalog.add_paths({'file2': Path('/run/media/file2.csv'),
        ...                      'file3': Path('path3')})
        >>> print(a_catalog)
        FileCatalog({'file1': Path('/run/media/file1.csv'),
                     'file2': Path('/run/media/file2.csv'),
                     'file3': Path('path3')})

        """
        if not isinstance(file_specs, dict):
            raise FileSpecIncorrect('Specified file_specs', file_specs,
                                    'is not a dictionary')
        for file_name, path in file_specs.items():
            if not isinstance(file_name, str):
                raise FileSpecIncorrect('Specified file name', file_name,
                                        'is not a string')
            if not isinstance(path, Path):
                raise FileSpecIncorrect(f'Specified path {path} is not a Path')
            if ((file_name in self.catalog) and
                    (self.catalog[file_name] != path)):
                raise IllegalAddAttempt(
                    'Attempting to add file name', file_name,
                    ' with path', path, 'to existing entry with '
                    'path', self.catalog[file_name])
        self.catalog.update(file_specs)

    def del_paths(self,
                  file_specs: FileSpecs) -> None:
        """Delete one or more paths from the catalog.

        Args:
            file_specs: A dictionary of one or more entries. The key is
                          the file name and the value is the path. The
                          file name must be a sting and the path must be
                          a pathlib Path.

        Raises:
            FileSpecIncorrect: The input path is not a string
            IllegalDelAttempt: Attempt to delete entry with different
                path

        The entries to be deleted are specified in the file_specs
        argument. For each file_spec, the specified file name is used to
        find the entry in the catalog. If not found, processing
        continues with the next file_spec. Otherwise, if the entry is
        found, the specified path from the file_spec is compared against
        the path in the found entry. If not equal, an IllegalDelAttempt
        exception is raised and no entries for the del_paths request
        will be deleted. Otherwise, if the path matches, the entry will
        be deleted provided no errors are detected for any of the
        preceeding or remaining file_specs.

        :Example: add and then delete paths from the catalog

        >>> from scottbrian_utils.file_catalog import FileCatalog
        >>> a_catalog = FileCatalog()
        >>> a_catalog.add_paths({'file1': Path('/run/media/file1.csv'),
        ...                      'file2': Path('/run/media/file2.csv'),
        ...                      'file3': Path('path3'),
        ...                      'file4': Path('path4')})
        >>> print(a_catalog)
        FileCatalog({'file1': Path('/run/media/file1.csv'),
                     'file2': Path('/run/media/file2.csv'),
                     'file3': Path('path3'),
                     'file4': Path('path4')})

        >>> a_catalog.del_paths({'file1': Path('/run/media/file1.csv'),
        ...                      'file3': Path('path3')})
        >>> print(a_catalog)
        FileCatalog({'file2': Path('/run/media/file2.csv'),
                     'file4': Path('path4')})

        """
        if not isinstance(file_specs, dict):
            raise FileSpecIncorrect('Specified file_specs', file_specs,
                                    'is not a dictionary')
        del_index: List[str] = []
        for file_name, path in file_specs.items():
            if not isinstance(file_name, str):
                raise FileSpecIncorrect('Specified file name ',
                                        file_name, 'is not a string')
            if not isinstance(path, Path):
                raise FileSpecIncorrect('Specified path', path,
                                        'is not a pathlib Path')
            if file_name in self.catalog:
                if self.catalog[file_name] != path:
                    raise IllegalDelAttempt(
                        'Attempting to delete file name', file_name,
                        ' with path', path, 'from to existing entry with path',
                        self.catalog[file_name])
                # if here then no exception and we can delete this path
                del_index.append(file_name)

        # remove the requested entries
        for file_name in del_index:
            del self.catalog[file_name]

    def save_catalog(self, saved_cat_path: Path) -> None:
        """Save catalog as a csv file.

        Args:
            saved_cat_path: The path to where the catalog is to be saved


        """
        # save catalog
        fieldnames = self.catalog.keys()

        with open(saved_cat_path, 'w', newline='') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerow(self.catalog)

    @classmethod
    def load_catalog(cls, saved_cat_path: Path) -> "FileCatalog":
        """Load catalog from a csv file.

        Args:
            saved_cat_path: The path from where the catalog is to be
                              loaded

        Returns:
            A FileCatalog instance

        """
        new_catalog: Dict[str, Path] = {}
        with open(saved_cat_path, newline='') as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                catalog = row

        for file_name, path in catalog.items():
            new_catalog[file_name] = Path(path)
        return cls(new_catalog)
