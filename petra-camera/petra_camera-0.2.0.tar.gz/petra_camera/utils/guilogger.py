#!/usr/bin/env python

# ----------------------------------------------------------------------
# Author:        Sebastian Piec <sebastian.piec@desy.de>
# Last modified: 2017, April 4
# ----------------------------------------------------------------------

"""Logger propagating log records to the LoggingWidget.
"""

import logging

# ----------------------------------------------------------------------
class GuiLogger(logging.Handler):

    # ----------------------------------------------------------------------
    def __init__(self):
        super(GuiLogger, self).__init__()

        self._widget = None

    # ----------------------------------------------------------------------
    def setWidget(self, widget):
        self._widget = widget

    # ----------------------------------------------------------------------
    def emit(self, record):
        if self._widget:
            self._widget.append(record)
