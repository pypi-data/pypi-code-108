#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------
# Author:        sebastian.piec@desy.de
# Last modified: 2017, October 2
# ----------------------------------------------------------------------

"""Errors related functionality
"""

import traceback
import logging

from PyQt5 import QtWidgets

from petra_camera.main_window import APP_NAME

logger = logging.getLogger(APP_NAME)


# ----------------------------------------------------------------------
def report_error(err, parent=None, simplify=False):
    """Send error message to the logging object and show user-friendly
    dialog box.
    """
    logger.exception(err)

    msg = str(err) if simplify else "{}\n\n{}".format(str(err).capitalize(),
                                                          str(traceback.format_exc()))

    QtWidgets.QMessageBox.warning(parent, "Exception", msg, QtWidgets.QMessageBox.Ok)

