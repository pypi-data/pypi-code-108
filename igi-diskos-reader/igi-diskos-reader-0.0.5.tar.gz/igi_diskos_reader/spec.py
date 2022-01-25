from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Sequence, Optional
import itertools as it
import pandas as pd

KNOWN_FORMATS_TO_KNOWN_VERSIONS: Dict[str, Sequence[str]] = {'GC-NPD-95': ['2.0']}
SUPPRESS_WARNINGS = False


class Sender(Enum):
    """
    We need to recognise the sender as they assign ids differently, which leads
    to a different merge process.
    """
    APT = 1
    STATOIL = 2
    UNRECOGNISED = 99


class BlockType(Enum):
    Site = 1
    Sample = 2
    Fraction = 3
    Analysis = 4
    Observations = 5  # observation data in sheets 5+


@dataclass
class ParsedDiskosFile:
    file_def: FileDefinition
    blocks: Sequence[Block]
    raw_data: str

    def get_identity_block(self, type: BlockType) -> Optional[Block]:
        return next((b for b in self.blocks if b.block_type == type and type != BlockType.Observations),
                    default=None)

    def get_block(self, block_no: str) -> Block:
        return next((b for b in self.blocks if b.block_def.block_no == block_no))


@dataclass
class FileDefinition:
    delimiter: str
    version: str
    format: str
    sender: Sender

    def __post_init__(self):
        supported_formats = KNOWN_FORMATS_TO_KNOWN_VERSIONS.keys()
        if self.format not in supported_formats:
            raise KeyError(f"The format detected for this file is unsupported. "
                           f"Detected: {self.format}, supported formats: {supported_formats}")

        supported_versions = KNOWN_FORMATS_TO_KNOWN_VERSIONS[self.format]
        if self.version not in supported_versions:
            raise ValueError(f"The version detected for this file (format: {self.format}) is unsupported. "
                             f"Detected version: {self.version}, supported versions: {supported_versions}")


@dataclass
class DataRow:
    """
    Every row in the diskos file that is not a comment or block separator fits the pattern of
    a delimited str with the first value as the code (incl the block definitions).
    """
    code: str
    values: Sequence[str]


@dataclass
class Record:
    """
    Multiple value rows in a single block can be associated with a single record e.g. if 
    there is more than one type of headers (L1 - L9).
    """
    data_rows: Sequence[DataRow]

    def get_all_values(self, block_def: BlockDefinition) -> Sequence[str]:
        return concatenate_values_in_record(self, block_def)


@dataclass
class Headers:
    """
    A block can contain more than one format of record. A set of headers is
    given for each starting with a code L1 - L9. Note, the headings for a
    record type e.g. L1 can be delimited on a single row or split over
    multiple rows.
    """
    code: str
    headers: Sequence[str]


@dataclass
class BlockDefinition:
    block_no: str
    description: str
    headers_collection: Sequence[Headers]


@dataclass
class Block:
    block_def: BlockDefinition
    records: Sequence[Record]
    block_type: BlockType = field(init=False)
    _df: Optional[pd.DataFrame] = field(init=False, default=None)

    def __post_init__(self):
        code = int(self.block_def.block_no)
        self.block_type = BlockType(code) if code <=5 else BlockType(5)  # 5+ obs, 1 = site, 2 = sam etc

    def get_headers(self) -> Sequence[str]:
        """
        Flatten out the headers for all record types in this block into a single collection.
        """
        return list(it.chain.from_iterable([h.headers for h in self.block_def.headers_collection]))

    @property
    def as_dataframe(self) -> pd.DataFrame:
        if self._df is None:
            data = [r.get_all_values(self.block_def) for r in self.records]
            self._df = pd.DataFrame(data, columns=self.get_headers())
        return self._df


def concatenate_values_in_record(record: Record, block_def: BlockDefinition) -> Sequence[str]:
    """
    Uses block def to ensure that spaces are included for header records that we do
    not have data for.
    """
    code_to_row = {row.code: row for row in record.data_rows}
    # main headers row keyed from both L1 and block_no, supporting either (I would expect
    # the data from this row to use L1 as the code from the general pattern), but it seems 
    # to use the block no from example data I have seen.
    code_to_row['L1'] = code_to_row.get(block_def.block_no)
    combined_values = []
    for headers in block_def.headers_collection:
        if headers.code in code_to_row:  # a record may not have data for every header collection
            row = code_to_row[headers.code]
            combined_values += row.values

            n_heads, n_values = len(headers.headers), len(row.values)

            # you would think this would be an error condition, but this happens in the
            # example files I have been given (fewer values that headers), so just warning.
            if n_heads != n_values:

                # add empty cells to pad values
                for i in range(n_heads - n_values):
                    combined_values.append("")

                if not SUPPRESS_WARNINGS:
                    print(f"** WARNING: The number of headers do not match the number of values:\n"
                          f"  headers: {headers.headers}\n  values: {row.values}.\n"
                          "   empty cells will be added to make up the row.\n")

        else:
            combined_values += ['' for _ in headers.headers]
    return combined_values
