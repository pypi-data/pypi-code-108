#!/usr/bin/env python
#  -*- coding: utf-8 -*-


import logging
import os
import unittest

import lz4.frame
from shinny_structlog import JSONFormatter

from tqsdk.channel import TqChan
from tqsdk.test.helper import MockInsServer


TqChan._level = 10


class TQBaseTestcase(unittest.TestCase):

    def setUp(self, md_url="wss://api.shinnytech.com/t/nfmd/front/mobile"):
        self.ins = MockInsServer()
        os.environ["TQ_INS_URL"] = f"http://127.0.0.1:{self.ins.port}/t/md/symbols/2020-09-15.json"
        os.environ["TQ_AUTH_URL"] = f"http://127.0.0.1:{self.ins.port}"
        os.environ["TQ_CONT_TABLE_URL"] = f"http://127.0.0.1:{self.ins.port}/continuous_table.json"
        os.environ["TQ_CHINESE_HOLIDAY_URL"] = f"http://127.0.0.1:{self.ins.port}/shinny_chinese_holiday.json"

        # 清空 logger handler
        logger = logging.getLogger("TqApi")
        while logger.handlers:
            logger.removeHandler(logger.handlers[0])
        log_file_name = f"./log_archive/{self._testMethodName}.log.lz4"
        fp = lz4.frame.open(log_file_name, mode='wt')
        sh = logging.StreamHandler(fp)
        sh.setFormatter(JSONFormatter())
        sh.setLevel(logging.DEBUG)
        logger.addHandler(sh)

    def tearDown(self) -> None:
        self.ins.close()
