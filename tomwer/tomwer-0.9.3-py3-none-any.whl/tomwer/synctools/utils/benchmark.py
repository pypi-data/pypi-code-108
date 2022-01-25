# coding: utf-8
# /*##########################################################################
# Copyright (C) 2016 European Synchrotron Radiation Facility
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
#############################################################################*/

"""
This module is containing benchmarks for rsync
"""

__authors__ = ["H.Payno"]
__license__ = "MIT"
__date__ = "07/06/2017"


import os
import shutil
import tempfile
import time

from tomwer.synctools.rsyncmanager import RSyncManager


class BenchRSyncClass(object):
    ORI_FOLDER = "/home/payno/testRSync/data/"

    def __init__(self):
        """ """
        self.folder1Path = tempfile.mkdtemp()
        print(self.folder1Path)
        self.folder2Path = tempfile.mkdtemp()

        assert os.path.isdir(self.folder1Path)
        assert os.path.isdir(self.folder2Path)
        # assert (os.path.isdir(BenchRSyncClass.ORI_FOLDER))
        # copy from original to folder 1
        # shutil.copytree(src=BenchRSyncClass.ORI_FOLDER,
        #                dst=os.path.join(self.folder1Path, 'test'))

    def __del__(self):
        if os.path.isdir(self.folder1Path):
            shutil.rmtree(self.folder1Path)

        if os.path.isdir(self.folder2Path):
            shutil.rmtree(self.folder2Path)

    def testCopy(self, options, parallel=False, nbIter=3):

        startTime = time.time()

        for it in range(nbIter):
            # copy from folder 1 to folder 2
            RSyncManager().syncFolderRaw(
                source=self.folder1Path,
                target=self.folder2Path,
                options=options,
                parallel=parallel,
                block=True,
            )

            # copy from folder 2 to folder 1
            RSyncManager().syncFolderRaw(
                source=self.folder2Path,
                target=self.folder1Path,
                options=options,
                parallel=parallel,
                block=True,
            )

        # check data integrity ?
        return (time.time() - startTime) / nbIter

    def testCopyFolders(self, f1, f2, options, parallel=False, nbIter=1):

        fullTime = 0

        for it in range(nbIter):
            startTime = time.time()

            # copy from folder 1 to folder 2
            RSyncManager().syncFolderRaw(
                source=f1, target=f2, options=options, parallel=parallel, block=True
            )

            fullTime += time.time() - startTime

            # copy from folder 2 to folder 1
            RSyncManager().syncFolderRaw(
                source=f2, target=f1, options=options, parallel=parallel, block=True
            )

        return fullTime / nbIter

    def testCopyTree(self, parallel=True):

        startTime = time.time()

        # copy from original to folder 1
        shutil.copytree(
            src=self.folder1Path, dst=os.path.join(self.folder2Path, "test")
        )

        shutil.rmtree(os.path.join(self.folder1Path, "test"))
        # copy from original to folder 1
        shutil.copytree(
            src=self.folder2Path, dst=os.path.join(self.folder1Path, "test")
        )

        # check data integrity ?
        return time.time() - startTime


def benchemark_rsync():
    benchmark = BenchRSyncClass()

    options = []
    options.append(["-a"])
    options.append(["-r"])

    f1 = "/lbsram/data/visitor/mi1226/bm05/nemoz/test1_"
    f2 = "/data/visitor/mi1226/bm05/nemoz/test1_"

    print("----- not using parallel ------")

    for opt in options:
        print("options are : ")
        print(opt)
        print(benchmark.testCopyFolders(f1, f2, opt, parallel=False))

    #    print('----- using parallel ------')

    #    for opt in options:
    #        print('options are : ')
    #        print(opt)
    #        print(l.testCopyFolders(f1, f2, opt, parallel=True))

    print("----- default shutil ------")
    print(benchmark.testCopyTree())


if __name__ == "__main__":
    benchemark_rsync()
