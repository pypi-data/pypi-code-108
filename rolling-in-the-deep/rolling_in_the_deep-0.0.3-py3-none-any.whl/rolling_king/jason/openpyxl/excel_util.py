#!/usr/bin/python3
# -*- coding: UTF-8 -*-

"""
Excel操作
"""

from openpyxl import Workbook, load_workbook
from openpyxl.styles import *
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')  # logging.basicConfig函数对日志的输出格式及方式做相关配置

logger = logging.getLogger("excel_util")


class ExcelUtil(object):

    def __init__(self, excel_path=None, excel_sheet=None):
        if excel_path is None:
            self.wb = Workbook(write_only=False)
            logger.info("默认创建一个空workbook。")
            self.ws = self.wb.active
            logger.info("默认worksheet={0}。".format(self.ws))
        else:
            self.wb = load_workbook(excel_path)
            self.ws = self.wb[excel_sheet]
            logger.info("加载{0}文件的{1}表单。".format(excel_path, excel_sheet))

    @property
    def rows(self):
        return self.ws.max_row

    @property
    def cell(self, cell_name):
        self.cell = self.ws[cell_name]
        return self.cell

    @property
    def cell(self, row, col):
        self.cell = self.ws.cell(row, col)
        return self.cell

    def set_cell_value(self, content):
        self.cell.value = content

    def set_cell_value(self, cell_name, content):
        self.ws[cell_name] = content

    def set_cell_value(self, row, col, content):
        self.ws.cell(row, col).value = content

    def get_cell_value(self, cell_name):
        return self.ws[cell_name].value

    def get_cell_value(self, row, col):
        return self.ws.cell(row, col).value

    def change_active_sheet(self, index):
        self.wb._active_sheet_index = index

    def save(self, save_path):
        self.wb.save(save_path)


if __name__ == '__main__':

    excelOperator = ExcelUtil(excel_path="../crawler/Temp.xlsx", excel_sheet="Records")
    logger.info(excelOperator.rows)



