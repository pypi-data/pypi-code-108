# /*##########################################################################
# Copyright (C) 2016-2017 European Synchrotron Radiation Facility
#
# This file is part of the PyMca X-ray Fluorescence Toolkit developed at
# the ESRF by the Software group.
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

__author__ = ["H. Payno"]
__license__ = "MIT"
__date__ = "02/06/2017"

from silx.gui import qt
import numpy.lib.npyio
import os
import tomwer.resources
import logging
from tomwer.io.utils import get_slice_data

logger = logging.getLogger(__name__)


class ImageLoaderThread(qt.QThread):
    """Thread used to load an image"""

    IMG_NOT_FOUND = numpy.load(
        tomwer.resources._resource_filename(
            "%s.%s" % ("imageNotFound", "npy"),
            default_directory=os.path.join("gui", "icons"),
        )
    )

    def __init__(self, url):
        """

        :param index: index of the image on the stackplot
        :param filePath: filePath is the file to load on stackplot reference.
                         It can be an .edf file or a .vol file. If this is a
                         vol file then the name is given with the slice z index
                         to be loaded.
        """
        super(qt.QThread, self).__init__()
        self.data = None
        self.url = url

    def getData(self):
        if hasattr(self, "data"):
            return self.data
        else:
            return None

    def run(self):
        if os.path.exists(self.url.file_path()) and os.path.isfile(
            self.url.file_path()
        ):
            self.data = get_slice_data(self.url)
        else:
            logger.warning("file %s not longer exists or is empty" % self.url)
            self.data = self.IMG_NOT_FOUND
