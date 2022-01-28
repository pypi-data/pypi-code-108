"""Importer template"""
import gzip
import io
import logging
from abc import ABC, abstractmethod
from collections import OrderedDict
from inspect import isabstract
from pathlib import Path
from re import match
from typing import (
    IO,
    Any,
    BinaryIO,
    Callable,
    Dict,
    Iterator,
    List,
    Optional,
    TextIO,
    Tuple,
    Union,
    cast,
)

from openqlab._typing import FilepathOrBuffer
from openqlab.io.data_container import DataContainer
from openqlab.io.importers import utils

try:
    import pyvisa
except ImportError:
    pyvisa = None


abstract_class_attribute = property(abstractmethod(lambda *args: None))

log = logging.getLogger(__name__)


class BaseImporter(ABC):
    NAME = cast(str, abstract_class_attribute)
    AUTOIMPORTER = cast(bool, abstract_class_attribute)
    PRIORITY = 0

    @abstractmethod
    def read(self) -> DataContainer:
        pass

    @classmethod
    def get_subclasses(cls) -> Iterator[Any]:
        for subclass in cls.__subclasses__():
            yield from subclass.get_subclasses()
            yield subclass

    @classmethod
    def importers(cls) -> Dict[str, "BaseImporter"]:
        importer_dict: dict = {
            importer.NAME: importer
            for importer in BaseImporter.get_subclasses()
            if not isabstract(importer)
        }
        return importer_dict

    @classmethod
    def auto_importers(cls) -> Dict[str, "BaseImporter"]:
        auto_importers = {
            name: importer
            for name, importer in cls.importers().items()
            if importer.AUTOIMPORTER
        }
        return auto_importers


class VisaImporter(BaseImporter, ABC):
    """VisaImporter template."""

    IDN_STARTS_WITH = cast(str, abstract_class_attribute)
    IDN_STARTS_WITH.__doc__ = "Start of the device IDN"
    ADDRESS_REGEX: str = r"tcpip[0-9]?::"

    def __init__(self, data: FilepathOrBuffer, inst: None = None):
        if pyvisa is None:
            raise utils.UnknownFileType(
                f"{self.NAME}: pyvisa is not installed. Skipping VISA importers."
            )
        if not isinstance(data, str):
            raise utils.UnknownFileType(f"{self.NAME}: not a string: {data}")
        if not match(self.ADDRESS_REGEX, data.lower()):
            raise utils.UnknownFileType(f"{self.NAME}: not a Visa address: {data}")

        rm = pyvisa.ResourceManager("@py")
        if inst is None:
            self._inst = rm.open_resource(data)
        else:
            self._inst = inst

        self._check_connection()

    @property
    def idn(self) -> str:
        return self.query("*IDN?").strip()

    def query(self, query: str) -> str:
        return self._inst.query(query)  # type: ignore

    def write(self, command: str) -> None:
        self._inst.write(command)  # type: ignore

    def _check_connection(self) -> None:
        try:
            assert self.idn.startswith(self.IDN_STARTS_WITH)
        except (AssertionError, pyvisa.errors.VisaIOError):
            raise utils.UnknownFileType(
                f"{self.NAME}: cannot open connection"
            ) from None


class StreamImporter(BaseImporter, ABC):
    """StreamImporter template.

    Incoming streams are not closed.
    """

    STARTING_LINES = cast(Union[List[str], List[bytes]], abstract_class_attribute)
    STARTING_LINES.__doc__ = "List of strings with a regex to match the first lines."
    HEADER_MAP: Dict[str, Tuple[Callable, Optional[str]]] = NotImplemented

    ENCODING: str = "utf-8"
    BINARY: bool = False
    HEADER_SPLIT: str = ","

    def __init__(self, data: FilepathOrBuffer) -> None:
        self._header: Dict = OrderedDict()
        self._opened_file = False
        self._open_stream(data)
        self._header_lines: List = self._check_header()
        self._stream: IO

    def __del__(self) -> None:
        if self._opened_file:
            try:
                self._stream.close()
            except AttributeError:
                pass

    # @no_type_check
    def _open_stream(self, data: FilepathOrBuffer) -> None:
        if isinstance(data, Path):
            data = str(data)
        if isinstance(data, str):
            self._opened_file = True

            # use gzip if it is a gzip file
            opener = gzip.open if data.endswith(".gz") else io.open

            if self.BINARY:
                self._stream = cast(BinaryIO, opener(data, "rb"))
            else:
                self._stream = cast(
                    TextIO,
                    opener(
                        data, "rt", encoding=self.ENCODING, newline=""
                    ),  # newline="" automatically uses the corrent line ending for the OS
                )
        else:
            self._stream = cast(IO, data)
        self._stream.seek(0, 0)

    def _check_header(self) -> List:
        lines: List = []  # save the header lines to reuse them if necessary
        log.debug(f"starting lines: {self.STARTING_LINES}")
        try:
            for i, start in enumerate(self.STARTING_LINES, 1):
                line = self._stream.readline()
                lines.append(line)
                log.debug("regex: %s, line: %s", start, line)
                if not isinstance(start, type(line)) or not match(start, line):
                    raise utils.UnknownFileType(
                        f'{self.NAME}: line {i} of file must start with "{start}"'
                    )
        except UnicodeDecodeError as e:
            log.info(f"error: {e}")
            raise utils.UnknownFileType(f"{self.NAME}: cannot open file")
        return lines

    def _get_key(self, keyword: str) -> str:
        try:
            key = self.HEADER_MAP[keyword][1]
            if key:
                return key
        except KeyError:
            pass
        return keyword

    def _read_line(self, line: str) -> None:
        split = line.strip().split(self.HEADER_SPLIT)
        keyword, *values = split

        if keyword not in self.HEADER_MAP:
            return

        as_type = self.HEADER_MAP[keyword][0]
        keyword = self._get_key(keyword)

        value = values[0]
        self._insert_header_line(keyword, value, as_type)

        if len(values) > 1 and values[1]:
            unit = values[1]
            keyword = self._get_key(keyword + "-unit")
            self._insert_header_line(keyword, unit, str)

    def _insert_header_line(
        self, key: str, value: str, as_type: Union[type, Callable]
    ) -> None:
        if key in self._header:
            return

        # if isinstance(as_type, type):
        self._header[key] = as_type(value)
        # else:
        #     as_type = cast(Callable, as_type)
        #     as_type(key, value)
