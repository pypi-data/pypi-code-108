from itertools import product
from typing import Any, Dict, Iterator, Protocol, Optional, Tuple

from holeysheet.parser import Parser
from holeysheet.schema import Config, Region, Cell
import pylightxl


class ExcelReader(Protocol):
    """
    Functions that an excel reader should have.
    """

    def select_worksheet(self, sheet: str):
        """
        Select the worksheet to be used from now on.

        :param sheet: Name of the worksheet in the excel file.
        """
        ...

    def index(self, row: int, col: int) -> Any:
        """
        Get the value of the cell at the given index.
        :param row: Row number, starting at 1.
        :param col: Column number, starting at 1.
        :return: Value in the cell.
        """
        ...

    def address(self, address: Cell) -> Any:
        """
        Get the value of the cell at the given address.
        :param address: Excel address of the targeted cell.
        :return: Value in the cell.
        """
        ...


class PylightExcelReader:
    """
    Excel reader which uses pylightxl
    """

    _db: pylightxl.Database = None
    _ws: pylightxl.pylightxl.Worksheet = None
    selected_worksheet: str = None

    def __init__(self, filename):
        self.filename = filename

    @property
    def db(self) -> pylightxl.Database:
        if self._db is None:
            self._db = pylightxl.readxl(self.filename)
        return self._db

    @property
    def ws(self) -> pylightxl.pylightxl.Worksheet:
        if self._ws is None:
            raise RuntimeError(
                "No worksheet selected. Use the `select_worksheet` function."
            )
        return self._ws

    def select_worksheet(self, sheet: str) -> None:
        if self.selected_worksheet != sheet:
            self._ws = self.db.ws(sheet)
            self.selected_worksheet = sheet

    def index(self, row: int, col: int) -> Any:
        return self.ws.index(row=row, col=col)

    def address(self, address: Cell) -> Any:
        return self.ws.address(address=address)


class ExcelParser(Parser):
    """
    Excel parser using an excel reader and a config object.
    """

    def __init__(self, excel_reader: ExcelReader, config: Config):
        """
        :param excel_reader: Excel reader interface
        :param config: Configuration object
        """
        self.reader = excel_reader
        self.config = config

    def parse(self) -> Iterator[Dict[str, Any]]:
        """
        Parse the excel reader using the config object.
        :return: Iterator over all the rows found in the excel.
        """
        for region in self.config.flatten_regions():
            yield from ExcelRegionParser(
                excel_reader=self.reader, region=region
            ).parse()


class ExcelRegionParser(Parser):
    """
    Parser that parses a single region to an excel reader
    """

    def __init__(self, excel_reader: ExcelReader, region: Region):
        """
        :param excel_reader: Excel reader interface
        :param region: Region object
        """
        self.reader = excel_reader
        self.region = region

    def get_value(self, row: int, col: int) -> Any:
        """
        Get the cell value in the given row, col
        :param row: Row number, starting from 1
        :param col: Column number, starting from 1
        :return: Value in the cell
        """
        return self.reader.index(row=row, col=col)

    def parse(self) -> Iterator[Dict[str, Any]]:
        """
        Parse the excel reader using the region object.
        :return: Iterator over all the rows found in the excel.
        """
        self.reader.select_worksheet(self.region.sheet)
        header_column = None
        if self.region.header.column!="index":
            header_column = addr2index(f"{self.region.header.column}1")[1]
        header_row = self.region.header.row
        from_row, from_col = addr2index(self.region.range.start)
        to_row, to_col = addr2index(self.region.range.end)
        literals = self.get_literals()
        # Get all possible row, col combinations in the given range.
        for (row, col) in product(
            range(from_row, to_row + 1), range(from_col, to_col + 1)
        ):
            val = self.get_value(row=row, col=col)
            column_header = None
            if header_column is None:
                column_header = str(row)
            if val:
                d = {
                    "column_header": column_header or self.get_value(row=row, col=header_column),
                    "row_header": self.get_value(row=header_row, col=col),
                    "value": val,
                    **literals,
                }
                yield d

    def get_literals(self) -> Dict[str, Any]:
        """
        Get the literals for the given region.
        :return: Dict of literals
        """
        d = {}
        for literal in self.region.literals:
            if literal.value:
                d[literal.name] = literal.value
            elif literal.cell:
                d[literal.name] = self.reader.address(literal.cell)
        return d


def addr2index(address: Cell) -> Tuple[int, int]:
    """
    Convert an excel address to a row, column index.
    :param address: excel address
    :return: row, column index starting from 1.
    """
    return pylightxl.pylightxl.utility_address2index(address)
