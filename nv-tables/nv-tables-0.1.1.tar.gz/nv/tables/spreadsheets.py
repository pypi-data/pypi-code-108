from abc import abstractmethod
from collections import defaultdict
from collections.abc import Mapping
from dataclasses import asdict, is_dataclass
from enum import IntEnum
from fnmatch import fnmatchcase
from operator import itemgetter
from pathlib import Path
from typing import Collection, Any, Iterable, Type, Tuple, Iterator, Callable, Dict, List, TypeVar

from .core import Serializer
from .typing import DataTable, DataStructure, DataRow, ParsedDataRow, ParsedDataStructure, ParsedDataTable


Workbook = TypeVar('Workbook')
Worksheet = TypeVar('Worksheet')
Cell = TypeVar('Cell')


class SpreadsheetSerializer(Serializer):
    DEFAULT_NAMING_PATTERN = f'{{table_name}}_{{table_series}}'
    DEFAULT_LOAD_PATTERN = '*'
    DEFAULT_EMPTY_ON_READ = None
    DEFAULT_EMPTY_ON_WRITE = ''
    DEFAULT_TABLE_NAME = 'data'

    MAX_LINES = NotImplemented
    MAX_COLS = NotImplemented

    class CellError:
        class Behaviour(IntEnum):
            IGNORE = 0
            WRAP = 1
            RAISE = 255

        class CellErrorWrapper:
            def __init__(self, value: Any):
                self.value = value

        @classmethod
        def match_behaviour(cls,
                            behaviour: Behaviour,
                            value: Any,
                            default: Any = None,
                            wrapper: Callable = CellErrorWrapper,
                            ) -> Any:
            match behaviour:
                case cls.Behaviour.IGNORE:
                    return default
                case cls.Behaviour.WRAP:
                    return wrapper(value)
                case cls.Behaviour.RAISE:
                    raise ValueError(f'cell error found: {value}')
                case _:
                    raise ValueError(f'unknown behaviour: {behaviour}')

    def __init__(self, cell_error: CellError.Behaviour = CellError.Behaviour.WRAP):
        super().__init__()
        self.cell_error = cell_error

    # Generic XLS/XLSX implementation
    def write_table(self, table: DataTable, fp: Path | str, table_name: str = DEFAULT_TABLE_NAME,
                    headers: Collection[str] = None, default: Any = DEFAULT_EMPTY_ON_WRITE, **serializer_kwargs):

        if not table:
            raise ValueError(f"unable to write an empty table to '{fp}'")

        workbook = self._get_new_workbook()
        self._add_table(workbook, table_name=table_name, table=table, default=default, headers=headers)
        self._save_workbook(workbook, fp)

    def append_table(self, table: DataTable, fp: Path | str, table_name: str = DEFAULT_TABLE_NAME,
                     headers: Collection[str] = None, default: Any = DEFAULT_EMPTY_ON_WRITE, **serializer_kwargs):
        if not table:
            raise ValueError(f"unable to append an empty table to '{fp}'")

        workbook = self._open_workbook(fp, for_append=True)
        self._add_table(workbook, table_name, table, default=default, headers=headers)
        self._save_workbook(workbook, fp)

    def dump(self, structure: DataStructure, fp: Path | str, schema: Mapping[Collection[str]] = None,
             default: Any = DEFAULT_EMPTY_ON_WRITE, **serializer_kwargs) -> None:
        if not structure:
            raise ValueError(f"unable to dump an empty structure to '{fp}'")

        schema = schema or dict()
        if isinstance(structure, Mapping):
            structure = structure.items()

        workbook = self._get_new_workbook()
        for table_name, table in structure:
            if schema and table_name not in schema:
                continue

            self._add_table(workbook, table_name, table, default=default, headers=schema.get(table_name, None))
        self._save_workbook(workbook, fp)

    def load(self, fp: Path | str, pattern=DEFAULT_LOAD_PATTERN, constructor: Type = None,
             default: Any = DEFAULT_EMPTY_ON_READ, **open_kwargs) -> ParsedDataStructure:

        structure = defaultdict(list)
        for table_name, row in self.iter_structure(fp, pattern=pattern, constructor=constructor,
                                                   default=default, **open_kwargs):
            structure[table_name].append(row)
        return structure

    def read_table(self, fp: Path | str, table_name: str = DEFAULT_TABLE_NAME, constructor: Type = None,
                   default: Any = DEFAULT_EMPTY_ON_READ, **open_kwargs) -> ParsedDataTable:
        return list(self.iter_table(fp, table_name=table_name, constructor=constructor,
                                    default=default, **open_kwargs))

    def read_headers(self, fp: Path | str, table_name: str = DEFAULT_TABLE_NAME, constructor: Type = None,
                     default: Any = DEFAULT_EMPTY_ON_READ, **open_kwargs) -> ParsedDataTable:
        first_row = next(self.iter_table(fp, table_name=table_name, constructor=constructor,
                                         default=default, **open_kwargs))
        return first_row.keys()

    def read_schema(self, fp: Path | str, pattern=DEFAULT_LOAD_PATTERN, **open_kwargs) -> Mapping[Collection[str]]:
        workbook = self._open_workbook(fp, **open_kwargs)
        return dict(self._iter_schema(workbook, pattern=pattern))

    def iter_table(self, fp: Path | str, table_name: str = None, constructor: Type = None,
                   default: Any = DEFAULT_EMPTY_ON_READ, **open_kwargs) -> Iterator[ParsedDataRow]:
        workbook = self._open_workbook(fp, **open_kwargs)
        table_name = table_name or self.DEFAULT_TABLE_NAME
        yield from self._iter_table(table_name, workbook, constructor, default)

    def iter_structure(self, fp: Path | str, pattern=DEFAULT_LOAD_PATTERN, constructor: Type = None,
                       default: Any = DEFAULT_EMPTY_ON_READ, **open_kwargs) -> Iterator[Tuple[str, ParsedDataRow]]:
        workbook = self._open_workbook(fp, **open_kwargs)
        yield from self._iter_structure(workbook, pattern, constructor, default)

    @staticmethod
    def _parse_table_name(s: str) -> Tuple[str, int | None]:
        table_name, *table_series = s.rsplit('_', 1)
        try:
            return table_name, int(table_series[0])
        except (IndexError, ValueError):
            return s, None

    def _add_table(self,
                   workbook,
                   table_name: str,
                   table: Iterable[DataRow],
                   default: Any = DEFAULT_EMPTY_ON_WRITE,
                   headers: Collection[str] = None,
                   ):
        max_lines = self.MAX_LINES
        max_cols = self.MAX_COLS
        naming_pattern = self.DEFAULT_NAMING_PATTERN

        table_series = 1
        sheet = None
        top_row = 0

        for row_num, row in enumerate(table):
            row = asdict(row) if is_dataclass(row) else row

            # Capture headers if None, presumes data is normalized though
            if not headers:
                headers = row.keys()

                if len(headers) > max_cols:
                    raise ValueError(f'too many columns for XLS: {len(headers)} > {max_cols} (max supported)')

            # handles new sheet
            if not sheet or (row_num - top_row + 1) >= max_lines:
                sheet_name = naming_pattern.format(table_name=table_name, table_series=table_series)
                sheet = self._add_sheet(workbook, sheet_name)

                self._write_headers(sheet, headers)
                self._freeze_headers(sheet)

                table_series += 1
                top_row = row_num

            # write data
            self._write_row(sheet, headers, row_num - top_row + 1, row, default=default)

    def _find_tables(self, workbook, pattern='*') -> Dict[str, List[Any]]:
        tables = defaultdict(list)

        for sheet in self._get_all_sheets(workbook):
            if pattern == '*' or fnmatchcase(sheet.name, pattern):
                sheet_name = self._get_sheet_name(sheet)
                table_name, table_series = self._parse_table_name(sheet_name)
                tables[table_name].append(((-1 if table_series is None else table_series), sheet))

        # Sort and clean-up serials
        for table_name, table_sheets in tables.items():
            table_sheets.sort(key=itemgetter(0))
            tables[table_name] = [sheet for _, sheet in table_sheets]

        return tables

    def _find_table_sheets(self, table_name, workbook) -> List[Worksheet]:
        table_sheets = list()

        for sheet in self._get_all_sheets(workbook):
            this_name, this_series = self._parse_table_name(self._get_sheet_name(sheet))
            if table_name == this_name:
                table_sheets.append(((-1 if this_series is None else this_series), sheet))

        table_sheets.sort(key=itemgetter(0))
        return [sheet for _, sheet in table_sheets]

    def _iter_structure(self,
                        workbook,
                        pattern: str = '*',
                        constructor: Type = None,
                        default: Any = DEFAULT_EMPTY_ON_READ,
                        ) -> Iterator[Tuple[str, Iterable[DataRow]]]:

        tables = self._find_tables(workbook, pattern=pattern)

        for table_name, table_sheets in tables.items():
            for table_sheet in table_sheets:
                for row in self._iter_through_sheet(table_sheet, workbook, constructor, default):
                    yield table_name, row

    def _iter_table(self,
                    table_name: str,
                    workbook,
                    constructor: Type = None,
                    default: Any = DEFAULT_EMPTY_ON_READ,
                    ) -> Iterator[Dict[str, Any]]:

        for sheet in self._find_table_sheets(table_name, workbook):
            yield from self._iter_through_sheet(sheet, workbook, constructor, default)

    def _iter_schema(self,
                     workbook: Workbook,
                     pattern: str = '*',
                     ) -> Iterator[Tuple[str, Collection[str]]]:

        tables = self._find_tables(workbook, pattern=pattern)

        for table_name, table_sheets in tables.items():
            for table_sheet in table_sheets:
                first_row = next(self._iter_through_sheet(table_sheet, workbook))
                yield table_name, list(first_row.keys())

    # Abstract methods to be adapted by xls/xlsx implementations
    @abstractmethod
    def _add_sheet(self, workbook: Workbook, sheet_name: str) -> Worksheet:
        pass

    @abstractmethod
    def _write_headers(self, sheet: Worksheet, headers: Collection[str]):
        pass

    @abstractmethod
    def _write_row(self, sheet: Worksheet, headers: Collection[str], row_num: int, row_data: ParsedDataRow,
                   default: Any = DEFAULT_EMPTY_ON_WRITE):
        pass

    @abstractmethod
    def _freeze_headers(self, sheet: Worksheet):
        pass

    @abstractmethod
    def _get_new_workbook(self, **new_kwargs) -> Workbook:
        pass

    @abstractmethod
    def _save_workbook(self, workbook: Workbook, fp: Path | str):
        pass

    @abstractmethod
    def _iter_through_sheet(self,
                            sheet: Worksheet,
                            workbook: Workbook,
                            constructor: Type = None,
                            default: Any = DEFAULT_EMPTY_ON_READ,
                            ) -> Iterator[ParsedDataRow]:
        pass

    @abstractmethod
    def _get_sheet_name(self, sheet: Worksheet) -> str:
        pass

    @abstractmethod
    def _get_all_sheets(self, book: Workbook) -> List[Any]:
        pass

    @abstractmethod
    def _open_workbook(self, fp: Path | str, for_append=False, **kwargs) -> Workbook:
        pass
