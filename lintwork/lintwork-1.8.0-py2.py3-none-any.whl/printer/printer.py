# -*- coding: utf-8 -*-

import json
import openpyxl
import os
import time

from lintwork.proto.proto import Format
from openpyxl.styles import Alignment, Font

LINT_NAME = "lintwork"

head = {
    "A": Format.FILE,
    "B": Format.LINE,
    "C": Format.TYPE,
    "D": Format.DETAILS,
}


class PrinterException(Exception):
    def __init__(self, info):
        super().__init__(self)
        self._info = info

    def __str__(self):
        return self._info


class Printer(object):
    _format = [".json", ".txt", ".xlsx"]

    def __init__(self, config=None):
        if config is None:
            pass

    @staticmethod
    def format():
        return Printer._format

    def _json(self, data, name):
        with open(name, "w", encoding="utf-8") as f:
            f.write(json.dumps(data, ensure_ascii=False, indent=2))

    def _txt(self, data, name):
        def _txt_helper(data, out):
            global head
            for key in sorted(head.keys()):
                out.write(u"%s: %s\n" % (head[key], data[head[key]]))

        with open(name, "w", encoding="utf8") as f:
            f.write("")
            for key, val in data.items():
                for v in val:
                    f.write(u"%s\n" % key)
                    _txt_helper(v, f)
                    f.write("\n")

    def _xlsx(self, data, name):
        def _styling_head(sheet):
            for item in head.keys():
                sheet[item + "1"].alignment = Alignment(
                    horizontal="center", shrink_to_fit=True, vertical="center"
                )
                sheet[item + "1"].font = Font(bold=True, name="Calibri")
            sheet.freeze_panes = sheet["A2"]

        def _styling_data(sheet, rows):
            for key in head.keys():
                for row in range(rows):
                    sheet[key + str(row + 2)].alignment = Alignment(
                        horizontal="center", vertical="center"
                    )
                    sheet[key + str(row + 2)].font = Font(bold=False, name="Calibri")

        wb = openpyxl.Workbook()
        wb.remove(wb.active)
        for key, val in data.items():
            ws = wb.create_sheet()
            ws.append([head[key].upper() for key in sorted(head.keys())])
            ws.title = "%s %s" % (
                key.upper(),
                time.strftime("%Y-%m-%d", time.localtime(time.time())),
            )
            for v in val:
                ws.append([v[head[key]] for key in sorted(head.keys())])
            _styling_head(ws)
            _styling_data(ws, len(val))
        wb.save(filename=name)

    def run(self, data, name, append=True):
        if append is True:
            raise PrinterException("append not supported")
        func = Printer.__dict__.get(os.path.splitext(name)[1].replace(".", "_"), None)
        if func is not None:
            func(self, {LINT_NAME: data}, name)
