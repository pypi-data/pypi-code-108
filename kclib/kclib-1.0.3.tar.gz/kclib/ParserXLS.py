#!/usr/bin/env python 
# -*- coding:utf-8 -*-

'''
:Name:	ParserXLS.py
:Author:	Zheng Yabiao
:Usage:	Parse GEO.xls file and return corresponding information.
:Data:	2017.5.23
:Version: v1.0
'''

import sys
from collections import defaultdict
import xlrd


def open_xls(file,  sheet_name = ""):
    """open xls file;
       return the sheet table
    """
    try:
        data = xlrd.open_workbook(file)
        if sheet_name:
            table = data.sheet_by_name(sheet_name)
            return table
    except IOError:
        print(file + " or the " + sheet_name + " sheet doesn't exist!")

def list_index(list, key, start_pos = 0):
    list = [str(i).strip() for i in list]
    try:
        a = list.index(str(key), start_pos)
        return a
    except:
        if key == "":
            return len(list)
        else:
            print("The key of '" + str(key) + "' doesn't exist after the index of %d" %(start_pos))
            sys.exit(1)

def fetch_row(file, key,  sheet_name = ""):
    """Fetch row information in Excel file

    :Args:
        * file (file): input Excel file
        * key (str): the title word for information fields
        * sheet_index (int): the sheet index in file
        * sheet_name (str): the sheet name in file
    :Returns:
        * row_contents (list): list of row information
    """
    table = open_xls(file, sheet_name)
    key_index = list_index(table.col_values(0), key)
    end_index = list_index(table.col_values(0), "END", key_index + 1)
    row_contents = []
    for line in range(key_index + 1, end_index):
        try:
            if table.row_values(line)[0].startswith("#"):
                continue
        except:
            pass
        if table.row_values(line)[0]:
            row_contents.append(table.row_values(line))
    return row_contents

def fetch_col(file, key,  sheet_name = ""):
    """Fetch row information in Excel file

    :Args:
        * file (file): input Excel file
        * key (str): the title word for information fields
        * sheet_index (int): the sheet index in file
        * sheet_name (str): the sheet name in file
    :Returns:
        * col_contents (list): two-layer list. first is header line, second is information.
    """
    table = open_xls(file, sheet_name)
    key_index = list_index(table.col_values(0), key)
    end_index = list_index(table.col_values(0), "END", key_index + 1)
    col_contents = [[],[]]
    for line in range(key_index + 1, end_index):
        if table.row_values(line)[0].startswith("#"):
            continue
        if table.row_values(line)[0]:
            col_contents[0].append(table.row_values(line)[0])
            col_contents[1].append(table.row_values(line)[1])
    return col_contents
