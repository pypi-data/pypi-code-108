# coding: utf-8
# /*##########################################################################
#
# Copyright (c) 2017 European Synchrotron Radiation Facility
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# ###########################################################################*/

__authors__ = ["H. Payno"]
__license__ = "MIT"
__date__ = "20/04/2020"


import os
import threading

from contextlib import AbstractContextManager
from tomwer.core.utils.Singleton import singleton


@singleton
class FileLockerManager:
    """Insure that for each file we will provide at most one locker"""

    def __init__(self):
        self.__lockers = {}

    def get_locker(self, file_):
        file_ = os.path.abspath(file_)
        if file_ not in self.__lockers:
            self.__lockers[file_] = threading.RLock()
        return self.__lockers[file_]

    def clear_locker(self, file_):
        if file_ in self.__lockers:
            del self.__lockers[file_]


class FileLockerContext(AbstractContextManager):
    """provide a context manager for a FileLocker"""

    def __init__(self, lock):
        self.__lock = lock

    def __enter__(self):
        self.__lock.acquire()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__lock.release()
