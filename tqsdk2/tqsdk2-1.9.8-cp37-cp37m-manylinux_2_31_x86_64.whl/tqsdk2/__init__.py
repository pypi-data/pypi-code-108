#!/usr/bin/env python
#  -*- coding: utf-8 -*-
name = "tqsdk2"

import os
import ctypes
import platform

this_dir = os.path.abspath(os.path.dirname(__file__))
dll_list = ["libfclib.so"] if platform.system() == "Linux" else []

tqsdk2_path = os.path.join(this_dir)
os.environ['PATH'] += ';' + tqsdk2_path
os.environ['TQSDK2_WEB_PATH'] = os.path.join(this_dir, 'web')

for name in dll_list:
    try:
        ctypes.cdll.LoadLibrary(os.path.join(this_dir, name))
    except Exception as e:
        raise Exception(e.strerror + "模块名:" + name)

from tqsdk2.tqsdk2 import TqApi
from tqsdk2.tqsdk2 import TqAuth
from tqsdk2.tqsdk2 import TqAccount, TqCtp, TqSim, TqKq, TqRohon, TqKqStock
from tqsdk2.tqsdk2 import TargetPosTask, TqBacktest, BacktestFinished
from tqsdk2.tqsdk2 import TqMarketMaker

from tqsdk2.tqsdk2 import ta