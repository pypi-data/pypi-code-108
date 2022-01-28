import logging
import warnings
from io import StringIO
from pathlib import Path
from typing import BinaryIO, List, Optional, TextIO, Union, cast

from typeguard import typechecked

from openqlab.io.data_container import DataContainer, DataContainerSeries

from .data_container import DataContainer
from .importers import utils
from .importers.ascii_header import ASCII_Header

from .base_importer import BaseImporter, StreamImporter  # isort:skip

log = logging.getLogger(__name__)


class UndefinedImporter(Exception):
    pass


def list_formats() -> None:
    print(
        "The below formats are currently understood by the importer.\n"
        'To import one of these formats, use io.read("filename", importer="<Importer>"),\n'
        "where <Importer> needs to be replaced by one of the following:\n"
    )
    for i in BaseImporter.importers().keys():
        print("\t", i)
    print(
        "\nThe following formats can be automatically detected and thus the\n"
        "type keyword can be omitted during import:\n"
    )
    for i in BaseImporter.auto_importers().keys():
        print("\t", i)


def _import(
    stream: BinaryIO, selected_importers: List[BaseImporter], **kwargs
) -> DataContainer:
    for imp in sorted(
        selected_importers, key=lambda importer: importer.PRIORITY, reverse=True
    ):
        try:
            i = imp(stream, **kwargs)  # type: ignore
            return i.read()
        except (utils.UnknownFileType, UnicodeDecodeError, TypeError):
            pass

    raise UndefinedImporter(
        "AutoImporter: unable to find importer for {0}".format(stream)
    )


@typechecked
def read(
    files: Union[str, TextIO, Path, List[Union[str, TextIO, Path]]],
    append: bool = False,
    importer: str = None,
    type: str = None,
    as_list: bool = False,
    **kwargs,
) -> Union[DataContainer, List[DataContainer]]:
    """
    Import data from lab instruments.

    Automatically imports lab instrument data data_files. Several importers
    are available, and will be used to try and import the data. Note that the
    same importer will be used for all data_files. The data will be returned as a
    Pandas :obj:`DataFrame`.

    Args:
        data_files : a filename or list of file names to import
        **kwargs : optional argument list that is passed on to the importer.
            Use the `type` keyword to explicitly specify an importer.

    Returns:
        openqlab.io.DataContainer:
        a DataContainer containing the imported data with header information if available.
        The index of the data frame will be set to a natural x-axis, e.g. frequency or
        time.

    Examples:
        Read traces from an oscilloscope data file::

            >>> data = io.read('scope.bin')
            >>> data.head()
                        Channel 0  Channel 1
            Time (s)
            -0.005000  -0.019347    5.22613
            -0.004995  -0.019347    5.22613
            ...

        Read multiple data_files containing spectral data::

            >>> data = io.read(['vac.txt', 'dark.txt', 'sqz.txt'])

    Raises:
        UndefinedImporter: The file type cannot be recognized and cannot be
            imported automatically, or the given importer type does not exist
            (if `type` was specified).

    :param files: a filename or list of file names to import.
    :param append: If True, multiple data_files will be appended row wise. If False, column wise.
    :param kwargs: optional argument list that is passed on to the importer.
    :return: DataContainer with imported data_files or empty DataContainer.
    """
    if type:
        warnings.warn(
            'Argument "type" is deprecated. Use argument "importer" instead.',
            DeprecationWarning,
        )
        if not importer:
            importer = type
    if isinstance(files, list):
        files_list: List = cast(list, files)
    else:
        files_list = [files]

    log.debug("file list in io.read: %s", files_list)

    importers = BaseImporter.importers()

    if importer:
        if importer not in importers.keys():
            raise UndefinedImporter(f"No importer defined for {importer}")
        selected_importers: List[BaseImporter] = [importers[importer]]
    else:
        selected_importers = list(BaseImporter.auto_importers().values())

    data: List[DataContainer] = [
        _import(data_file, selected_importers, **kwargs) for data_file in files_list
    ]

    if append is True:
        axis = 0
    else:
        axis = 1

    if as_list:
        return data
    return DataContainer.concat(data, axis=axis)


@typechecked
def reads(data: str, **kwargs) -> Union[DataContainer, List[DataContainer]]:
    stream = StringIO(data)
    stream.name = "StringIO"
    log.debug("type of data: %s", type(stream))
    return read(stream, **kwargs)
