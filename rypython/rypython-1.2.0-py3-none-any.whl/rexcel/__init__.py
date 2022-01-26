from pathlib import Path

import pandas as pd
import xlsxwriter


class RexelWorkbook:
    COLS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

    def __init__(
            self,
            output_file: Path
    ) -> None:
        self.worksheets = []
        self.output_file = output_file

    def __enter__(self):
        self.workbook = xlsxwriter.Workbook(self.output_file)
        return self

    def __exit__(self, type, value, traceback):
        self.workbook.close()

    def add_worksheet_by_dataframe(
            self,
            df: pd.DataFrame,
            worksheet_name: str,
            column_widths: list
    ):
        df = df.where(pd.notnull(df), '')
        wks = self.workbook.add_worksheet(name=worksheet_name)
        bold = self.workbook.add_format({'bold': 1})
        if column_widths:
            for first, last, width in column_widths:
                wks.set_column(first, last, width)
        for j, header in enumerate(df.columns):
            wks.write(
                f"{self.COLS[j]}1",
                header,
                bold
            )
        rows = df.values.tolist()
        row_number = 1
        col_number = 0
        write_funcs = {
            str: wks.write_string,
            bool: wks.write_boolean,
            int: wks.write_number
        }
        for row in rows:
            offset = 0
            for j, cell in enumerate(row):
                if type(cell) not in write_funcs:
                    cell = str(cell)
                write_func = write_funcs.get(type(cell))
                write_func(
                    row_number,
                    col_number + offset,
                    cell
                )
                offset += 1
            row_number += 1
        self.worksheets.append(wks)
