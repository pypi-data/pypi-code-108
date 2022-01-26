#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import List
from .excel import row_items, num_to_column, column_to_num, column_items
from .formatter_and_parser import is_none_or_empty
from .error import Error
import xlwings as xw
from .form import Form


def remove_unfilled_rows(err: Error, form: Form, must_not_empty_fields: List[str]):
    if err.has_error():
        return

    field_indexes: List[int] = list(map(lambda x: form.column_index_with_title(x), must_not_empty_fields))
    if err.has_error():
        return

    unfilled_row_indexes: List[int] = []
    for row_index in range(len(form.data_rows)):
        row = form.data_rows[row_index]
        for field_index in field_indexes:
            cell_val = row.cell(field_index, err)
            if is_none_or_empty(cell_val):
                unfilled_row_indexes.insert(0, row_index)
                break

    for row_index in unfilled_row_indexes:
        form.data_rows.pop(row_index)


def read_sht(err: Error, sht: xw.Sheet, ref_col: str = 'A', header_row: int = 1, start_col: str = 'A'):
    cells_row = row_items(err, sht, header_row, start_col)
    if err.has_error():
        return

    if len(cells_row) == 0:
        return
    end_col = num_to_column(column_to_num(start_col) + len(cells_row) - 1)

    form = Form(err)
    form.set_title_row(header_row, cells_row)
    cells_col = column_items(err, sht, ref_col, header_row + 1)
    for i in range(len(cells_col)):
        row_num = header_row + 1 + i
        cells = sht.range("{}{}:{}{}".format(start_col, row_num, end_col, row_num)).value
        form.append_data_row(row_num, cells)

    return form
