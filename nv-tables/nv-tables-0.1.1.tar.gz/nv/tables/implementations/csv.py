from collections import defaultdict
from collections.abc import Mapping
from dataclasses import asdict, is_dataclass
from contextlib import ExitStack
from csv import DictWriter, DictReader
from pathlib import Path
from typing import Collection, Any, TextIO, Type, Tuple, Iterator

from nv.utils.collections.structures import normalize_row

from ..core import Serializer
from ..typing import DataTable, DataStructure, ParsedDataRow, ParsedDataStructure, ParsedDataTable


__ALL__ = ['CSVSerializer', 'csv', ]


class CSVSerializer(Serializer):
    DEFAULT_EXTENSION = 'csv'
    DEFAULT_NAMING_PATTERN = f'{{table_name}}.{DEFAULT_EXTENSION}'
    DEFAULT_LOAD_PATTERN = f'*.{DEFAULT_EXTENSION}'
    DEFAULT_EMPTY_ON_READ = None
    DEFAULT_EMPTY_ON_WRITE = ''
    DEFAULT_ENCODING = 'utf-8'

    def __init__(self, encoding: str = DEFAULT_ENCODING, **fmtparams):
        self.encoding = encoding
        self.fmtparams = fmtparams
        super().__init__()

    def write_table(self, table: DataTable, fp: Path | str | TextIO, headers: Collection[str] = None,
                    default: Any = DEFAULT_EMPTY_ON_WRITE, encoding: str = None, **serializer_kwargs) -> None:

        if not table:
            raise ValueError(f"unable to write an empty table to '{fp}'")

        with ExitStack() as stack:
            if isinstance(fp, str | Path):
                fp = stack.enter_context(Path(fp).open('w', encoding=self._get_encoding(fp, encoding)))

            self._write_table(table, fp, headers, default, **serializer_kwargs)

    def append_table(self, table: DataTable, fp: Path | str | TextIO, headers: Collection[str] = None,
                     default: Any = DEFAULT_EMPTY_ON_WRITE, encoding: str = None, **serializer_kwargs) -> None:
        if not table:
            raise ValueError(f"unable to append an empty table to '{fp}'")

        with ExitStack() as stack:
            if isinstance(fp, str | Path):
                fp = stack.enter_context(Path(fp).open('a', encoding=self._get_encoding(fp, encoding)))

            self._write_table(table, fp, headers, default, append=True, **serializer_kwargs)

    def dump(self, structure: DataStructure, fp: Path | str | TextIO, schema: Mapping[Collection[str]] = None,
             pattern=DEFAULT_NAMING_PATTERN, default: Any = DEFAULT_EMPTY_ON_WRITE, encoding: str = None,
             **serializer_kwargs) -> None:
        if not structure:
            raise ValueError(f"unable to append an empty structure to '{fp}'")

        schema = schema or dict()

        fp = Path(fp)
        fp.mkdir(parents=True, exist_ok=True)
        if not fp.is_dir():
            raise ValueError(f'{fp} must be a directory')

        if isinstance(structure, Mapping):
            structure = structure.items()

        for table_name, table in structure:
            if schema and table_name not in schema:
                continue

            table_path = fp / Path(pattern.format(table_name=table_name))
            self.write_table(table, table_path, headers=schema.get(table_name, None),
                             default=default, encoding=encoding, **serializer_kwargs)

    def iter_table(self, fp: Path | str | TextIO, constructor: Type = None, default: Any = DEFAULT_EMPTY_ON_READ,
                   encoding: str = None, **parser_kwargs) -> Iterator[ParsedDataRow]:

        with ExitStack() as stack:
            if isinstance(fp, str | Path):
                fp = stack.enter_context(Path(fp).open('r', encoding=self._get_encoding(fp, encoding)))

            dict_reader = DictReader(fp, **(self.fmtparams | parser_kwargs))

            headers = dict_reader.fieldnames

            for row in dict_reader:
                yield constructor(**row) if constructor else normalize_row(row, headers=headers, default=default)

    def iter_structure(self, fp: Path | str, pattern=DEFAULT_LOAD_PATTERN, constructor: Type = None,
                       default: Any = DEFAULT_EMPTY_ON_READ, encoding: str = None,
                       **parser_kwargs) -> Iterator[Tuple[str, ParsedDataRow]]:

        for f in self._iter_tables(fp, pattern):
            for row in self.iter_table(f, constructor=constructor, default=default, encoding=encoding, **parser_kwargs):
                table_name, _ = self._parse_table_name(f)
                yield table_name, row

    def read_table(self, fp: Path | str | TextIO, constructor: Type = None, default: Any = DEFAULT_EMPTY_ON_READ,
                   encoding: str = None, **parser_kwargs) -> ParsedDataTable:
        return list(self.iter_table(fp, constructor=constructor, default=default, encoding=encoding, **parser_kwargs))

    def load(self, fp: Path | str, pattern=DEFAULT_LOAD_PATTERN, constructor: Type = None,
             default: Any = DEFAULT_EMPTY_ON_READ, encoding: str = None, **parser_kwargs) -> ParsedDataStructure:

        structure = defaultdict(list)
        for table_name, row in self.iter_structure(fp, pattern=pattern, constructor=constructor, default=default,
                                                   encoding=encoding, **parser_kwargs):
            structure[table_name].append(row)
        return structure

    def read_headers(self, fp: Path | str | TextIO, encoding: str = None, **parser_kwargs) -> Collection[str]:
        with ExitStack() as stack:
            if isinstance(fp, str | Path):
                fp = stack.enter_context(Path(fp).open('r', encoding=self._get_encoding(fp, encoding)))

            dict_reader = DictReader(fp, **(self.fmtparams | parser_kwargs))
            return dict_reader.fieldnames

    def read_schema(self, fp: Path | str, pattern=DEFAULT_LOAD_PATTERN, encoding: str = None,
                    **parser_kwargs) -> Mapping[Collection[str]]:

        schema = dict()
        for f in self._iter_tables(fp, pattern):
            table_name, _ = self._parse_table_name(f)
            schema[table_name] = self.read_headers(f, encoding=encoding, **parser_kwargs)
        return schema

    @staticmethod
    def _parse_table_name(fp: Path | str) -> Tuple[str, int | None]:
        return fp.stem, None

    def _write_table(self, table: DataTable, fp: TextIO, headers: Collection[str] = None,
                     default: Any = DEFAULT_EMPTY_ON_READ, append=False, **serializer_kwargs) -> None:

        dict_writer = None

        for row in table:
            row = asdict(row) if is_dataclass(row) else row

            # Capture headers if None, presumes data is normalized though
            if not headers:
                headers = (asdict(row) if is_dataclass(row) else row).keys()

            # Write headers
            if dict_writer is None:
                if not headers:
                    # Guards against any empty data
                    raise ValueError('no headers found in data (or no data to write).')

                dict_writer = DictWriter(fp, headers, **(self.fmtparams | serializer_kwargs))

                if not append:
                    dict_writer.writeheader()

            dict_writer.writerow(normalize_row(row, headers=headers, default=default))

    @staticmethod
    def _iter_tables(fp: Path | str, pattern='*.csv') -> Iterator[Path]:
        fp = Path(fp)
        if not fp.is_dir():
            raise ValueError(f'{fp} is not a directory.')

        for f in fp.glob(pattern):
            if f.is_file():
                yield f

    def _get_encoding(self, fp: Path | str, encoding: str = None) -> str:
        encoding = encoding or self.encoding or self.DEFAULT_ENCODING
        if callable(encoding):
            encoding = encoding(fp)
        return encoding


# Default implementation
csv = CSVSerializer()
