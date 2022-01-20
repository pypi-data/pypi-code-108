# @Author: chunyang.xu
# @Email:  398745129@qq.com
# @Date:   2020-06-08 11:55:54
# @Last Modified time: 2021-08-29 13:30:07
# @github: https://github.com/longfengpili

# !/usr/bin/env python3
# -*- coding:utf-8 -*-

import os
import time

from .base import DBbase
from pydbapi.sql import SqlFileParse

import logging
dblogger = logging.getLogger(__name__)


class DBFileExec(DBbase):

    def __init__(self):
        super(DBFileExec, self).__init__()

    def get_filesqls(self, filepath, **kw):
        sqlfileparser = SqlFileParse(filepath)
        arguments, sqls = sqlfileparser.get_filesqls(**kw)
        return arguments, sqls

    def file_exec(self, filepath, ehandling=None, verbose=0, **kw):
        st = time.time()
        results = {}
        filename = os.path.basename(filepath)
        dblogger.info(f"Start Job 【{filename}】".center(80, '='))
        arguments, sqls = self.get_filesqls(filepath, **kw)
        for desc, sql in sqls.items():
            dblogger.info(f">>> START {desc}")
            sqlverbose = verbose or (2 if 'verbose2' in desc else 1
                                     if 'verbose1' in desc or filename.startswith('test')
                                     else 0)
            sqlehandling = ehandling or ('pass' if 'epass' in desc else 'raise')
            rows, action, result = self.execute(sql, ehandling=sqlehandling, verbose=sqlverbose)
            results[desc] = result
            # dblogger.info(f"End {desc}")
        et = time.time()
        dblogger.info(f"End Job 【{filename}】, cost {et - st:.2f} seconds".center(80, '='))
        return results
