#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import List, Optional, Dict
from .csv import load_form_from_csv_file
from .excel import num_to_column, column_to_num
from .formatter_and_parser import is_none_or_empty, string_of, parse_value
from .error import Error

from .form import Form
from .utils import get_value_or_exception


class EasyForm:
    def __init__(self, err: Error, form: Form, must_has_content: bool = True):
        self.err = err

        self.__raw_form = form
        self.__all_fields: List[str] = list(map(lambda x: string_of(x), self.__raw_form.title_row.cells))
        self.___row_num_to_index_dict: Optional[Dict[int, int]] = self.__init_row_num_to_index_dict()
        self.__field_to_index_dict: Dict[str, int] = {}

        self.row_num_list: List[int] = list(map(lambda x: x.row_num, self.__raw_form.data_rows))
        if not self.err.has_error() and must_has_content and len(self.__raw_form.data_rows) == 0:
            msg = 'form is no data'
            self.err.append(msg)

    def __init_row_num_to_index_dict(self):
        if self.err.has_error():
            return
        result_dict: Dict[int, int] = {}

        index = 0
        for row in self.__raw_form.data_rows:
            result_dict[row.row_num] = index
            index += 1

        return result_dict

    def register_field(self, field: str, must_not_none=True):
        if self.err.has_error():
            return

        if field in self.__field_to_index_dict:
            return

        # get col index
        if field not in self.__all_fields:
            msg = 'cannot find field "{}" in title row'.format(field)
            self.err.append(msg)
            return

        index = self.__all_fields.index(field)

        # verify field data
        if must_not_none:
            for row in self.__raw_form.data_rows:
                val = row.cell(index, self.err)
                row_num = row.row_num
                if is_none_or_empty(val):
                    msg = 'empty cell found at row {}, field {}'.format(row_num, field)
                    self.err.append(msg)
                    return

        # register
        self.__field_to_index_dict[field] = index

    def register_multi_fields(self, fields: List[str], must_not_none=True):
        for field in fields:
            self.register_field(field, must_not_none)
            if self.err.has_error():
                return

    def __verify_field(self, field: str):
        if self.err.has_error():
            return

        if field not in self.__field_to_index_dict:
            msg = 'field "{}" is not register, or not exists in title row'.format(field)
            self.err.append(msg)

    def __verify_row_num(self, row_num: int):
        if self.err.has_error():
            return

        if row_num not in self.___row_num_to_index_dict:
            msg = 'row "{}" is out of range'.format(row_num)
            self.err.append(msg)

    def cell(self, field: str, row_num: int):
        self.__verify_field(field)
        self.__verify_row_num(row_num)
        if self.err.has_error():
            return

        field_index = self.__field_to_index_dict[field]
        row_index = self.___row_num_to_index_dict[row_num]

        return self.__raw_form.data_rows[row_index].cell(field_index, self.err)

    def excel_cell_range(self, field: str, row_num: int, start_column_name: str = 'A'):
        self.__verify_field(field)
        if self.err.has_error():
            return

        field_index = self.__field_to_index_dict[field]
        column_name = num_to_column(column_to_num(start_column_name) + field_index)
        return '{}{}'.format(column_name, row_num)

    def check_values_of_field(self, field: str, expected_value: any):
        self.__verify_field(field)
        if self.err.has_error():
            return

        row_count = len(self.__raw_form.data_rows)
        if row_count < 1:
            return

        field_index = self.__field_to_index_dict[field]
        for row_num in self.___row_num_to_index_dict:
            row_index = self.___row_num_to_index_dict[row_num]
            row_cell_value = self.__raw_form.data_rows[row_index].cell(field_index, self.err)

            if row_cell_value != expected_value:
                msg = 'column "{}" have unexpected value: {} at row {}, expected value: {}' \
                    .format(field, row_cell_value, row_num, expected_value)
                self.err.append(msg)
                return

    def format_cell_values(self, field: str, formatter=lambda x: x):
        self.__verify_field(field)
        if self.err.has_error():
            return

        field_index = self.__field_to_index_dict[field]
        for row in self.__raw_form.data_rows:
            val = row.cell(field_index, self.err)
            row.cells[field_index] = formatter(val)

    def find_row_num_list(self, field: str, val, data_type: str = "自动", must_have: bool = False,
                          must_only_one: bool = False):
        self.__verify_field(field)
        if self.err.has_error():
            return

        field_index = self.__field_to_index_dict[field]
        row_num_list: List[int] = []
        for row_num in self.___row_num_to_index_dict:
            row_index = self.___row_num_to_index_dict[row_num]
            row_cell_val = self.__raw_form.data_rows[row_index].cell(field_index, self.err)
            row_cell_val = get_value_or_exception(self.err, parse_value(row_cell_val, data_type=data_type))
            if self.err.has_error():
                return
            if val == row_cell_val:
                row_num_list.append(row_num)

        if self.err.has_error():
            return

        count = len(row_num_list)
        if count == 0 and must_have:
            msg = 'cannot find any row with value \'{}\' in field \'{}\''.format(val, field)
            self.err.append(msg)
            return

        if count > 1 and must_only_one:
            msg = 'find too many rows \'{}\' with same value \'{}\' in field \'{}\''.format(row_num_list, val, field)
            self.err.append(msg)
            return

        return row_num_list

    def find_first_row_num(self, field: str, val, data_type: str = "自动", must_have: bool = True,
                           must_only_one: bool = True):
        row_num_list = self.find_row_num_list(field, val, data_type=data_type, must_have=must_have,
                                              must_only_one=must_only_one)
        if self.err.has_error():
            return

        return row_num_list[0]


def build_easyform_from_csv_file(err: Error, csv_file_path: str):
    if err.has_error():
        return None

    form = load_form_from_csv_file(err, csv_file_path)
    if err.has_error():
        return None

    easy_form = EasyForm(err, form)
    if err.has_error():
        msg = 'last error occurred when read file {}'.format(csv_file_path)
        err.append(msg)
        return
    return easy_form
