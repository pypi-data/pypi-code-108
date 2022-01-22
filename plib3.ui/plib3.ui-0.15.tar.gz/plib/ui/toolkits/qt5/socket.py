#!/usr/bin/env python3
"""
Module QT5.SOCKET -- Python Qt 5 Socket Notifier Objects
Sub-Package UI.TOOLKITS.QT5 of Package PLIB3 -- Python UI Toolkits
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the Qt 5 UI socket notifier objects.
"""

from PyQt5 import QtCore as qtc

from plib.ui.defs import *
from plib.ui.base.app import PSignalBase
from plib.ui.base.socket import PSocketNotifierBase

from .app import PQtSignalBase


notify_types = {
    NOTIFY_READ: qtc.QSocketNotifier.Read,
    NOTIFY_WRITE: qtc.QSocketNotifier.Write
}


class PSocketNotifier(qtc.QSocketNotifier, PQtSignalBase, PSignalBase, PSocketNotifierBase):
    
    auto_enable = True
    
    def __init__(self, obj, notify_type, select_fn, notify_fn):
        PSocketNotifierBase.__init__(self, obj, notify_type, select_fn, notify_fn)
        qtc.QSocketNotifier.__init__(self, obj.fileno(),
                                     notify_types[notify_type])
        self.setup_notify(SIGNAL_NOTIFIER, self.handle_notify)
    
    def set_enabled(self, enable):
        self.setEnabled(enable)
    
    # We don't need to override the start or done class methods since Qt's GUI
    # event loop already handles socket events, so just instantiating and enabling
    # the socket notifier is enough
    
    def handle_notify(self, sock):
        self.set_enabled(False)
        if (sock == self._obj.fileno()) and self.select_fn():
            self.notify_fn(self._obj)
        if self.auto_enable:
            self.set_enabled(True)
