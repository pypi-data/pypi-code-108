import numpy as np
import pytest
from nabu.misc.binning import *

@pytest.fixture(scope='class')
def bootstrap(request):
    cls = request.cls
    cls.data = np.arange(100*99, dtype=np.uint16).reshape(100, 99)
    cls.tol = 1e-5

#
# Alternate implementation of binning
# TODO do we have off-the shelf binning in scipy or skimage ?
#

def binning2_ref(img):
    return img.reshape(img.shape[0] //2, 2, img.shape[1]//2, 2).mean(axis=-1).mean(axis=1)

def binning2_horiz_ref(img):
    return img.reshape(img.shape[0], img.shape[1]//2, 2).mean(axis=-1)

def binning2_vertic_ref(img):
    return img.reshape(img.shape[0] //2, 2, img.shape[1]).mean(axis=1)

def binning3_ref(img):
    return img.reshape(img.shape[0] //3, 3, img.shape[1]//3, 3).mean(axis=-1).mean(axis=1)

def binning3_horiz_ref(img):
    return img.reshape(img.shape[0], img.shape[1]//3, 3).mean(axis=-1)

def binning3_vertic_ref(img):
    return img.reshape(img.shape[0]//3, 3, img.shape[1]).mean(axis=1)


@pytest.mark.usefixtures('bootstrap')
class TestUnsharp:

    def checkResult(self, res, ref, name):
        mae = np.max(np.abs(res - ref))
        assert mae < self.tol, "%s: max error is too high (%.2e > %.2e)" % (name, mae, self.tol)


    def testBinning2(self):
        data = self.data
        res = binning2(data)
        ref = binning2_ref(data[:, :-1])
        self.checkResult(res, ref, "binning 2x2")

        res = binning2_horiz(data)
        ref = binning2_horiz_ref(data[:, :-1])
        self.checkResult(res, ref, "horizontal 2-binning")

        res = binning2_vertic(data)
        ref = binning2_vertic_ref(data)
        self.checkResult(res, ref, "horizontal 2-binning")


    def testBinning3(self):
        data = self.data
        res = binning3(data)
        ref = binning3_ref(data[:-1, :])
        self.checkResult(res, ref, "binning 3x3")

        res = binning3_horiz(data)
        ref = binning3_horiz_ref(data)
        self.checkResult(res, ref, "horizontal 3-binning")

        res = binning3_vertic(data)
        ref = binning3_vertic_ref(data[:-1, :])
        self.checkResult(res, ref, "horizontal 3-binning")

