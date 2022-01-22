#!/usr/bin/env python3
"""
Module PYSIDE2.SOCKET -- Python PySide 2 Socket Notifier Objects
Sub-Package UI.TOOLKITS.PYSIDE2 of Package PLIB3 -- Python UI Toolkits
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the PySide 2 UI socket notifier objects.
"""

from PySide2 import QtCore as qtc

from plib.ui.defs import *
from plib.ui.base.app import PSignalBase
from plib.ui.base.socket import PSocketNotifierBase

from .app import PQtSignal


notify_types = {
    NOTIFY_READ: qtc.QSocketNotifier.Read,
    NOTIFY_WRITE: qtc.QSocketNotifier.Write
}


class PSocketNotifier(PQtSignal, qtc.QSocketNotifier, PSignalBase, PSocketNotifierBase):
    
    auto_enable = True
    
    def __init__(self, obj, notify_type, select_fn, notify_fn):
        PSocketNotifierBase.__init__(self, obj, notify_type, select_fn, notify_fn)
        qtc.QSocketNotifier.__init__(self, obj.fileno(),
                                     notify_types[notify_type])
        self.setup_notify(SIGNAL_NOTIFIER, self.handle_notify)
        
        self.is_valid = (
            # Not sure why PySide2 switched to QSocketDescriptor since it has zero information
            # about the actual socket, not even its fileno
            (lambda sock: isinstance(sock, qtc.QSocketDescriptor) and sock.isValid())
            if hasattr(qtc, 'QSocketDescriptor') else
            # This covers older versions of PySide2 where sock was still an int and useful
            (lambda sock: isinstance(sock, int) and (sock == obj.fileno()))
        )
    
    def set_enabled(self, enable):
        self.setEnabled(enable)
    
    # We don't need to override the start or done class methods since Qt's GUI
    # event loop already handles socket events, so just instantiating and enabling
    # the socket notifier is enough
    
    def handle_notify(self, sock):
        self.set_enabled(False)
        if self.is_valid(sock) and self.select_fn():
            self.notify_fn(self._obj)
        if self.auto_enable:
            self.set_enabled(True)
