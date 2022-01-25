from __future__ import annotations
from typing import Set, Optional
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from dataclasses import dataclass, field
import pandas as pd

from igi_diskos_reader.spec import ParsedDiskosFile
from igi_diskos_reader.sender_specific.merge import try_create_combined_df


@dataclass
class ExcelWriter:
    parsed_diskos_file: ParsedDiskosFile
    dest_file_path: str
    do_merge: bool = field(default=True)
    wb: Workbook = field(default_factory=Workbook)

    def __enter__(self) -> ExcelWriter:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.wb.save(self.dest_file_path)
        self.wb.close()
        print(f"Excel file written to: {self.dest_file_path}")

    def write(self) -> None:
        print("\nWriting Excel file...")
        
        # write raw data to first sheet
        sheet = self.wb.active
        sheet.title = 'raw_data'
        for row_num, line in enumerate(self.parsed_diskos_file.raw_data.split('\n'), start=1):
            sheet[f"A{row_num}"] = line

        # write a sheet for each block
        for block in self.parsed_diskos_file.blocks:

            # unmodified data
            sheet_title = f"{block.block_def.block_no}_{block.block_def.description}"
            self.df_to_sheet(sheet_title, block.as_dataframe)

            # #transformed data (uncomment below to incl indv sheets with each transformation step)
            # transformers = get_transformers(block, self.parsed_diskos_file.file_def.sender)
            # for transformer in transformers:
            #     sheet_title = f"{sheet_title[:15]}_{transformer.__class__.__name__[:15]}"
            #     transformed_df = apply_transformations(block.as_dataframe, transformer)
            #     self.df_to_sheet(sheet_title, transformed_df)

        # merge
        if self.do_merge:
            self._try_create_comb_sheet()

    def df_to_sheet(self, sheet_title: str, df: pd.DataFrame, idx: Optional[int] = None):
        sheet = self.wb.create_sheet(title=ExcelWriter._clean_sheet_name(sheet_title), index=idx)
        rows_with_data = (r for r in dataframe_to_rows(df, index=True, header=True) if r and len(r) > 1)
        for row in rows_with_data:
            sheet.append(row[1:])  #  [1:] to excl row num col

    def _try_create_comb_sheet(self):
        merge_completed, comb_df = try_create_combined_df(self.parsed_diskos_file)
        if merge_completed:
            print("\nWriting combined sheet...")
            self.df_to_sheet('Combined', comb_df, idx=0)

    @staticmethod
    def _clean_sheet_name(orig: str) -> str:
        allowed_chars = ExcelWriter._get_sheet_name_allowed_chars()
        excel_char_limit = 31

        clean_name = ''
        for char in orig:
            if char in allowed_chars:
                clean_name += char
            else:
                clean_name += '_'
        return clean_name[:excel_char_limit]

    @staticmethod
    def _get_sheet_name_allowed_chars() -> Set[str]:
        lower_letters = [chr(n) for n in range(97, 123)]
        upper_letters = [chr(n) for n in range(65, 91)]
        digits = [str(n) for n in range(10)]
        special_chars = [' ', '.', '_']
        return set().union(lower_letters, upper_letters, digits, special_chars)
