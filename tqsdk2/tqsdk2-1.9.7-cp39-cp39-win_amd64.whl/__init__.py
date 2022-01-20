#!/usr/bin/env python
#  -*- coding: utf-8 -*-
name = "tqsdk2"

import os
import ctypes
import platform

this_dir = os.path.abspath(os.path.dirname(__file__))
dll_list = []

if platform.system() == "Windows":
    dll_list = ["lib/WinDataCollect.dll",
                "lib/oes_api.dll", 
                'lib/thosttraderapi.dll',
                'lib/thosttraderapi_se.dll',
                'lib/mfc100.dll',
                'lib/msvcp100.dll',
                'lib/msvcr100.dll',
                'lib/RohonBaseV64.dll',
                'lib/thosttraderapi_rh.dll',
                'lib/zlib1.dll',
                'lib/bz2.dll',
                'lib/lzma.dll',
                'lib/zstd.dll',
                'lib/boost_iostreams-vc142-mt-x64-1_77.dll',                
                'lib/libcurl.dll',
                'lib/sqlite3.dll',
                'lib/uriparser.dll',
                'lib/fclib.dll']
else:
    dll_list = ["lib/libLinuxDataCollect.so",
                "lib/libLinuxDataCollect0.so",
                "lib/libdatafeed64.so",
                "lib/liboes_api.so", 
                "lib/libthosttraderapi.so",
                "lib/libthosttraderapi_se.so",
                "lib/librohonbase.so",
                "lib/librohonbase.so.1.1",
                "lib/libthosttraderapi20200106zip.so",
                "lib/librtq.so",
                "lib/libfclib.so"]

tqsdk2_path = os.path.join(this_dir, 'lib')
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