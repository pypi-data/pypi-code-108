#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import shutil
from typing import List

from xlwings.utils import rgb_to_int

from .error import Error
import xlwings as xw


def sheet_with_name(err: Error, wb: xw.Book, name='sheet name'):
    if err.has_error():
        return None
    for sht in wb.sheets:
        if sht.name == name:
            return sht

    err.append('excel file({}) has no sheet named "{}"'.format(wb.fullname, name))
    return None


def count_of_continue_none_cells(items: List[any] = None):
    if items is None:
        items = []
    i = len(items) - 1
    count = 0
    while i >= 0:
        if items[i] is None:
            count += 1
        else:
            break
        i -= 1
    return count


def row_items(err: Error, sht: xw.Sheet, row=1, first_column='A', last_column='ZZ'):
    if err.has_error():
        return None
    range_str = '{}{}:{}{}'.format(first_column, row, last_column, row)
    r = sht.range(range_str)
    cells = r.value

    count = count_of_continue_none_cells(cells)
    return cells[0:len(cells) - count]


def row_items_with_column(err: Error, sht: xw.Sheet, row=1, first_column='A', last_column='ZZ'):
    items = row_items(err, sht, row, first_column, last_column)
    results = []
    i = 0
    for item in items:
        results.append((add_column(first_column, i), item))
        i += 1

    return results


def row_items_filtered(err: Error, sht: xw.Sheet, tester=lambda x: True, row=1, first_column='A', last_column='ZZ'):
    items = row_items_with_column(err, sht, row, first_column, last_column)
    if tester is None:
        return items

    results = filter(lambda x: tester(x[1]), items)
    return list(results)


def column_items_sub(err: Error, sht: xw.Sheet, column='A', start_row=1, steps=100):
    if err.has_error():
        return []
    end_row = start_row + steps - 1
    if type(column) == str:
        range_str = '{}{}:{}{}'.format(column, start_row, column, end_row)
        return sht.range(range_str).value
    else:
        return sht.range((start_row, column), (end_row, column)).value


def column_items(err: Error, sht: xw.Sheet, column='A', start_row=1, steps=100):
    if err.has_error():
        return []

    items = []
    start_row_sub = start_row
    count = count_of_continue_none_cells(items)
    while count < 20:
        items = items + column_items_sub(err, sht, column, start_row_sub, steps)
        start_row_sub += steps
        count = count_of_continue_none_cells(items)

    return items[0:len(items) - count]


def column_items_with_row(err: Error, sht: xw.Sheet, column='A', start_row=1, steps=100):
    items = column_items(err, sht, column, start_row, steps)
    results = []
    i = 0
    for item in items:
        results.append((start_row + i, item))
        i += 1

    return results


def column_items_filtered(err: Error, sht: xw.Sheet, tester=lambda x: True, column='A', start_row=1, steps=100):
    items = column_items_with_row(err, sht, column, start_row, steps)
    if tester is None:
        return items

    results = filter(lambda x: tester(x[1]), items)
    return list(results)


def num_to_column(num: int):
    if num < 0:
        s = 'column number({}) is less than 0'.format(num)
        raise Exception(s)
    elif num == 0:
        return ""
    elif num <= 26:
        return chr(65 - 1 + num)

    right = num % 26
    if right == 0:
        right = 26
    left = int((num - right) / 26)
    return num_to_column(left) + num_to_column(right)


def column_to_num(column: str):
    length = len(column)
    if length == 0:
        return 0
    elif length == 1:
        num = ord(column.upper()) - ord('A') + 1
        if num < 1 or num > 26:
            s = 'column char({}) is not in a~z, or A~Z'.format(column)
            raise Exception(s)
        return num
    else:
        return 26 * column_to_num(column[0:length - 1]) + column_to_num(column[length - 1:])


def add_column(column: str, add_num: int):
    num = column_to_num(column)
    return num_to_column(num + add_num)


def close_wb(wb: xw.Book):
    if wb is not None:
        wb.close()


def quit_app(app: xw.App):
    if app is not None:
        app.quit()


def orange_red():
    return rgb_to_int((255, 69, 0))


def banana_yellow():
    return rgb_to_int((227, 207, 87))


def sky_blue():
    return rgb_to_int((135, 206, 235))


def green():
    return rgb_to_int((0, 255, 0))


def is_excel_file_opened(file_path: str):
    (file_folder, file_name) = os.path.split(file_path)

    locked_file = file_folder + '\\~$' + file_name
    return os.path.exists(locked_file)


def append_sht_to_another(err: Error, source_wb: xw.Book, target_wb: xw.Book,
                          source_sheet: str = 'Sheet1',
                          target_sheet: str = 'Sheet1',
                          skip_if_no_source_sheet: bool = False,
                          empty_rows: int = 1,
                          source_ref_column: str = 'A',
                          target_ref_column: str = 'A'):
    if err.has_error():
        return
    source_sht = sheet_with_name(err, source_wb, source_sheet)
    if err.has_error():
        if skip_if_no_source_sheet:
            print('[Info] skip to copy sheet "{}", because it is not exists'.format(source_sheet))
            err.clear()
            return
        return

    source_row_count = len(column_items(err, source_sht, source_ref_column))
    if err.has_error():
        return

    if source_row_count == 0:
        return

    target_sht = sheet_with_name(err, target_wb, target_sheet)
    if err.has_error():
        return
    target_row_count = len(column_items(err, target_sht, target_ref_column))
    if err.has_error():
        return

    source_range = source_sht.range('A1:ZZ{}'.format(source_row_count))
    split_row_count = 0 if target_row_count == 0 else empty_rows
    target_range = target_sht.range('A{}:ZZ{}'.format(target_row_count + 1 + split_row_count,
                                                      target_row_count + source_row_count + split_row_count))
    source_range.copy(target_range)
    return True


def upload_data_to_another_file(err: Error,
                                app: xw.App,
                                source_file_path: str,
                                target_file_path: str,
                                source_sheet: str = 'Sheet1',
                                target_sheet: str = 'Sheet1',
                                empty_rows: int = 1,
                                source_ref_column: str = 'A',
                                target_ref_column: str = 'A'
                                ):
    if err.has_error():
        return

    # check target folder is exists
    target_folder = os.path.dirname(target_file_path)
    if not os.path.exists(target_folder):
        err.append('try to upload data to shared file {}, but its folder {} is not exists'
                   .format(target_file_path, target_folder))
        return

    # check file opening
    opened = is_excel_file_opened(target_file_path)
    if opened:
        err.append('try to upload data to shared file {}, but it is opened now'.format(target_file_path))
        return

    # copy file if target is not exists
    if not os.path.exists(target_file_path):
        try:
            shutil.copy(source_file_path, target_file_path)
            target_wb: xw.Book = app.books.open(target_file_path)

            # rename sheet if should
            if source_sheet != target_sheet:
                target_sht = sheet_with_name(err, target_wb, source_sheet)
                if err.has_error():
                    close_wb(target_wb)
                    return
                target_sht.name = target_sheet
                target_wb.save()

            # remove useless sheets
            has_useless_sheets = False
            for sht in target_wb.sheets:
                if sht.name != target_sheet:
                    has_useless_sheets = True
                    sht.delete()
            if has_useless_sheets:
                target_wb.save()

            close_wb(target_wb)

        except Exception as e:
            err.append(
                'copy file {} to file {} failed with error {}'.format(source_file_path, target_file_path, e))
        return

    # uploading
    source_wb = app.books.open(source_file_path)
    target_wb = app.books.open(target_file_path)

    uploaded = append_sht_to_another(err, source_wb, target_wb,
                                     source_sheet,
                                     target_sheet,
                                     False,
                                     empty_rows,
                                     source_ref_column,
                                     target_ref_column)

    if uploaded is not None and uploaded:
        target_wb.save()

    close_wb(source_wb)
    close_wb(target_wb)
