#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import sys
import os
from silx.gui import qt
import argparse
from tomwer.gui.utils.splashscreen import getMainSplashScreen
from tomwer.gui.stacks import SliceStack
from tomwer.gui import icons
from tomwer.core.utils.resource import increase_max_number_file
import signal

logging.basicConfig(level=logging.WARNING)
_logger = logging.getLogger(__name__)


def getinputinfo():
    return "tomwer slicestack [scanDir]"


def sigintHandler(*args):
    """Handler for the SIGINT signal."""
    qt.QApplication.quit()


def addFolderAndSubFolder(stack, path):
    stack.addLeafScan(path)
    for f in os.listdir(path):
        _path = os.path.join(path, f)
        if os.path.isdir(_path) is True:
            addFolderAndSubFolder(stack, _path)


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "root_dir", help="Root dir to browse and to extract all slices files under it."
    )
    parser.add_argument(
        "--debug",
        dest="debug",
        action="store_true",
        default=False,
        help="Set logging system in debug mode",
    )

    options = parser.parse_args(argv[1:])

    increase_max_number_file()

    global app  # QApplication must be global to avoid seg fault on quit
    app = qt.QApplication.instance() or qt.QApplication([])

    qt.QLocale.setDefault(qt.QLocale(qt.QLocale.English))
    qt.QLocale.setDefault(qt.QLocale.c())
    signal.signal(signal.SIGINT, sigintHandler)
    sys.excepthook = qt.exceptionHandler
    timer = qt.QTimer()
    timer.start(500)
    # Application have to wake up Python interpreter, else SIGINT is not
    # catched
    timer.timeout.connect(lambda: None)

    splash = getMainSplashScreen()
    widget = SliceStack()
    widget.setWindowIcon(icons.getQIcon("tomwer"))
    options.root_dir = options.root_dir.rstrip(os.path.sep)
    addFolderAndSubFolder(stack=widget, path=options.root_dir)

    splash.finish(widget)
    widget.show()
    app.exec_()


if __name__ == "__main__":
    main(sys.argv)
