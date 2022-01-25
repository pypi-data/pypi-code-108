from __future__ import annotations

from dataclasses import field, dataclass
from typing import Iterator, Dict, List, Set, Any
from io import StringIO
import csv

from igi_diskos_reader.spec import Block, DataRow, FileDefinition, ParsedDiskosFile, BlockDefinition, Record, Headers, Sender
from igi_diskos_reader.utils import split_on_last_occurrence
from igi_diskos_reader.validation import validate_code, validate_header_block_def_code

KNOWN_DELIMITER_MAPPINGS: Dict[str, str] = {'COMMA': ',', 'SEMICOLON': ';', 'TAB': '\t'}
COMMENT = '//'
BLOCK_TERMINATOR: str = '-----'
BLOCK_DEF_TEXT = 'DEFINE BLOCK'
NULL_PLACEHOLDERS = {'-91230000000009110000'}  # replace these with empty


def build_reader(file_path: str, quiet_mode: bool = False) -> DiskosReader:
    with open(file_path) as f:
        return DiskosReader(f.read(), quiet_mode)


@dataclass
class DiskosReader:
    file_content: str
    quiet_mode: bool = field(default=False)
    raw_blocks: Iterator[str] = field(init=False)

    def __post_init__(self):
        self.raw_blocks = iter(self.file_content.split(BLOCK_TERMINATOR))

    def parse_file(self) -> ParsedDiskosFile:
        file_def = FileDefinitionBuilder.build(next(self.raw_blocks))
        self._debug(file_def)
        blocks: List[Block] = []

        for raw_header_block in self.raw_blocks:
            # build headers
            if self.is_empty_whitespace_or_comment(raw_header_block):
                continue
            header_data_rows = self.get_data_rows(raw_header_block, file_def.delimiter, for_header=True)
            block_def = BlockDefinitionBuilder.build(header_data_rows)
            self._debug(block_def)

            # build data block
            raw_data_block = next(self.raw_blocks)
            data_rows = self.get_data_rows(raw_data_block, file_def.delimiter, for_header=False)
            block = DataBlockBuilder.build(block_def, data_rows)
            self._debug(f"Built block with {len(block.records)} records.\n")
            blocks.append(block)
        return ParsedDiskosFile(file_def, blocks, raw_data=self.file_content)

    @staticmethod
    def get_data_rows(raw_block: str, delim: str, for_header: bool) -> Iterator[DataRow]:
        cleaned_block = DiskosReader.strip_comments_and_empty_lines(raw_block)
        
        # split fields - can't use simple line.split(delim) because of fields with delims inside ""
        f = StringIO(cleaned_block)  # treat block of text like a csv file
        reader = csv.reader(f, delimiter=delim)

        for line in reader:
            if len(line) < 2:
                raise ValueError(f"Expected to see code followed by values, got: {line}.")

            code, fields = line[0], DiskosReader.replace_null_placeholders(line[1:])
            validate_code(code, for_header)
            yield DataRow(code,  values=[f.strip() for f in fields])

    @staticmethod
    def replace_null_placeholders(fields: List[str]) -> List[str]:
        return [f.strip() if f not in NULL_PLACEHOLDERS else '' for f in fields]

    @staticmethod
    def is_empty_whitespace_or_comment(line: str) -> bool:
        return not line or line.isspace() or line.startswith(COMMENT)

    @staticmethod
    def strip_comments_and_empty_lines(raw_block: str) -> str:
        rows = raw_block.split('\n')
        return '\n'.join([r for r in rows if not DiskosReader.is_empty_whitespace_or_comment(r)])

    def _debug(self, msg: Any) -> None:
        if not self.quiet_mode:
            print(msg)


class FileDefinitionBuilder:

    @staticmethod
    def build(raw_file_def: str) -> FileDefinition:
        lines = raw_file_def.split('\n')
        name_len = 15
        name_to_value: Dict[str, str] = {}
        for line in lines:
            if DiskosReader.is_empty_whitespace_or_comment(line):
                continue
            name = line[:name_len].strip()
            name_to_value[name] = line[name_len:]

        try:
            delim = FileDefinitionBuilder.get_delimiter(delim_desc=name_to_value['Delimiter'])
            version = name_to_value['Version']
            format_code = name_to_value['Format']
            try:
                sender_name = name_to_value['Sender']
                sender = Sender[sender_name]
            except KeyError:
                # mapping to unrecognised rather than excluding because we can at least produce
                # the individual sheets even if we can't merge them.
                sender = Sender.UNRECOGNISED
        except KeyError:
            raise KeyError(f"Expected to find keys for 'Delimiter', 'Version' and 'Format' in dict from text. "
                           f"name_to_value dict: {name_to_value}.")

        return FileDefinition(delimiter=delim, version=version, format=format_code, sender=sender)

    @staticmethod
    def get_delimiter(delim_desc: str) -> str:
        try:
            return KNOWN_DELIMITER_MAPPINGS[delim_desc]
        except KeyError:
            raise KeyError(f"Delimiter description: {delim_desc} not recognised. If this is a valid delimiter "
                           f"it should be added to the 'KNOWN_DELIMITER_MAPPINGS' constant.")


class BlockDefinitionBuilder:

    @staticmethod
    def build(header_rows: Iterator[DataRow]) -> BlockDefinition:
        def_row = next(header_rows)
        validate_header_block_def_code(def_row.code)
        if len(def_row.values) != 3 and def_row.values[0] != BLOCK_DEF_TEXT:
            raise ValueError(f"Expected 3 values in block def row (after '00' code) starting with "
                             f"{BLOCK_DEF_TEXT} but got: {def_row.values}")
        block_no, desc = def_row.values[1], def_row.values[2]
        headers_collection: List[Headers] = []

        # build collection of headers. The code L1-L9 is for the record type, each code gets a separate
        # RecordTypeHeaders collection. Within a type the headers can be delimited on one row or split
        latest_record_type_code = ''
        headers_for_current_code: List[str] = []
        all_block_headers: Set[str] = set()
        for row in header_rows:
            if row.code == latest_record_type_code:
                BlockDefinitionBuilder.add_headers(row, headers_for_current_code, all_block_headers)
            else:
                if len(headers_for_current_code) > 0:  # add record for headers built up so far
                    headers_obj = Headers(latest_record_type_code, headers_for_current_code)
                    headers_collection.append(headers_obj)

                # start new headers list for next header record type e.g. L1 -> L2
                headers_for_current_code = []
                BlockDefinitionBuilder.add_headers(row, headers_for_current_code, all_block_headers)
            
            # setup for next iteration
            latest_record_type_code = row.code

        # push last headers to collection
        if len(headers_for_current_code) > 0:  # add record for headers built up so far
            headers_collection.append(Headers(latest_record_type_code, headers_for_current_code))

        return BlockDefinition(block_no=block_no, description=desc, headers_collection=headers_collection)

    @staticmethod
    def add_headers(row: DataRow, headers_for_current_code: List[str], all_block_headers: Set[str]):
        for val in row.values:
            col = BlockDefinitionBuilder.make_col_name_unique(val, all_block_headers)
            headers_for_current_code.append(col)

    @staticmethod
    def make_col_name_unique(name: str, existing_names: Set[str]) -> str:
        # todo - note merge depends on this convention of _N for dup col names
        if name in existing_names:
            prev_versions = [n for n in existing_names if n.startswith(name)]
            if prev_versions:
                last = sorted(prev_versions)[-1]  # sorting should put highest _N last
                before_, after_ = split_on_last_occurrence(last, '_')
                if not after_: after_ = '1'
                new_name = before_ + '_' + str(int(after_) + 1).zfill(2)
            else:
                new_name = name + '_2'
            existing_names.add(new_name)
            return new_name
        else:
            existing_names.add(name)
            return name


class DataBlockBuilder:

    @staticmethod
    def build(block_def: BlockDefinition, data_rows: Iterator[DataRow]) -> Block:
        records: List[Record] = []
        current_record_rows: List[DataRow] = []

        def is_start_of_new_record(row: DataRow) -> bool:
            # start of a new record (examples I have seen use the block no in place of L1, but will accept either)
            return row.code == block_def.block_no or row.code == 'L1'

        # every row should be for one of these codes (as these were found in the block def)
        # or the block no/L1 (for the first row of a record)
        expected_codes = [h.code for h in block_def.headers_collection[1:]]

        for row in data_rows:
            if is_start_of_new_record(row):
                if len(current_record_rows) > 0:
                    records.append(Record(data_rows=current_record_rows))  # create record for previous rows
                current_record_rows = [row]  # start new record
            else:
                # new row continuing existing record
                if row.code in expected_codes:
                    current_record_rows.append(row)
                else:
                    raise ValueError(f"The expected pattern is that for each header type within a block " 
                                     f"e.g. L1-L9 there will be 1-n rows for each record (e.g sample) "
                                     f"the first row's code should be the block_no: '{block_def.block_no}' ", 
                                     f"optionally followed by rows for the other headers. The current "
                                     f"block registered the following header codes: {expected_codes}. "
                                     f"The code for the current row does not match this: {row}.")

        # ensure final record is added (usually added when a new record begins)
        if len(current_record_rows) > 0:
            records.append(Record(data_rows=current_record_rows))
        
        return Block(block_def, records)
