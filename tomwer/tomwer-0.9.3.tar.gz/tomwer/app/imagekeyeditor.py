#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import sys
from silx.gui import qt
import argparse
from tomwer.gui import icons
from tomwer.gui.utils.splashscreen import getMainSplashScreen
from tomwer.core.scan.hdf5scan import HDF5TomoScan
from tomoscan.esrf.hdf5scan import ImageKey
from tomwer.gui.edit.imagekeyeditor import ImageKeyDialog as _ImageKeyDialog
from nxtomomill.utils import change_image_key_control
from tomwer.core.utils.resource import increase_max_number_file
import signal

logging.basicConfig(level=logging.WARNING)
_logger = logging.getLogger(__name__)


class ImageKeyDialog(_ImageKeyDialog):
    def __init__(self, *args, **kwargs):
        _ImageKeyDialog.__init__(self, *args, **kwargs)
        self._scan = None

    def setScan(self, scan):
        if not isinstance(scan, HDF5TomoScan):
            raise TypeError("This only manage HDF5TomoScan")
        self._scan = scan
        _ImageKeyDialog.setScan(self, scan)

    def _validateReleased(self):
        if not self._scan:
            raise ValueError("Scan should be set first")

        modifications = self.getModifications()
        image_keys_set = set(self.getModifications().values())
        image_keys_set = set(
            [ImageKey.from_value(image_key) for image_key in image_keys_set]
        )
        for image_key_type in image_keys_set:
            frame_indexes_dict = dict(
                filter(lambda item: item[1] is image_key_type, modifications.items())
            )
            frame_indexes = tuple(frame_indexes_dict.keys())
            _logger.warning(
                "will modify {} to {}".format(frame_indexes, image_key_type)
            )
            change_image_key_control(
                file_path=self._scan.master_file,
                entry=self._scan.entry,
                frames_indexes=frame_indexes,
                image_key_control_value=image_key_type.value,
                logger=_logger,
            )


def getinputinfo():
    return "tomwer nabu [scan_path]"


def sigintHandler(*args):
    """Handler for the SIGINT signal."""
    qt.QApplication.quit()


def main(argv):
    import os

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scan_path", help="HDF5File to edit")
    parser.add_argument("entry", default=None, help="Entry to treat")
    options = parser.parse_args(argv[1:])

    # image key can only handle HDF5Tomoscan for now
    scan = HDF5TomoScan(scan=options.scan_path, entry=options.entry)
    increase_max_number_file()

    app = qt.QApplication.instance() or qt.QApplication([])

    qt.QLocale.setDefault(qt.QLocale(qt.QLocale.English))
    qt.QLocale.setDefault(qt.QLocale.c())
    signal.signal(signal.SIGINT, sigintHandler)
    sys.excepthook = qt.exceptionHandler
    timer = qt.QTimer()
    timer.start(500)
    # Application have to wake up Python interpreter, else SIGINT is not
    # catch
    timer.timeout.connect(lambda: None)

    splash = getMainSplashScreen()
    options.scan_path = options.scan_path.rstrip(os.path.sep)

    widget = ImageKeyDialog(parent=None)
    widget.setScan(scan)
    widget.setWindowTitle("Image key editor")
    widget.setWindowIcon(icons.getQIcon("tomwer"))
    splash.finish(widget)
    widget.show()
    app.exec_()


if __name__ == "__main__":
    main(sys.argv)
