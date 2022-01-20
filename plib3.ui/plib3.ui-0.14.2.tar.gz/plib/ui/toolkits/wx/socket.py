#!/usr/bin/env python3
"""
Module WX.SOCKET -- Python Wx Socket Notifier Objects
Sub-Package UI.TOOLKITS.WX of Package PLIB3 -- Python UI Toolkits
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the Qt 5 UI socket notifier objects.
"""

import select

from plib.stdlib.classtools import Singleton

from plib.ui.defs import *
from plib.ui.base.socket import PSocketNotifierBase

from .app import PApplication


# NOTE: We don't use the higher-level selectors module here
# because we want separate registration of readers and writers,
# even if both are for the same underlying socket object

class PWxSocketManager(Singleton):
    
    timeout = 0.1
    
    def _init(self):
        self.readers = []
        self.writers = []
        self.exit_loop = False
    
    @property
    def app(self):
        return PApplication.Get()
    
    def add_reader(self, reader):
        self.readers.append(reader)
    
    def add_writer(self, writer):
        self.writers.append(writer)
    
    def remove_reader(self, reader):
        self.readers.remove(reader)
    
    def remove_writer(self, writer):
        self.writers.remove(writer)
    
    def run_select_loop(self,
                        select=select.select):
        
        self.exit_loop = False
        timeout = self.timeout
        e = []  # no socket exception handlers
        while (not self.exit_loop) and (self.readers or self.writers):
            r, w, e = select(self.readers, self.writers, e, timeout)
            for reader in r:
                reader.process_read()
            for writer in w:
                writer.process_write()
            # This is a kludge, but wx gives us no way to have its own event loop
            # process socket events, so it's the best we can do
            self.app.process_events()
    
    @classmethod
    def get_instance(cls):
        return cls.__dict__.get("__inst__")


class PSocketNotifier(PSocketNotifierBase):
    
    manager = PWxSocketManager()
    
    notify_map = {
        NOTIFY_READ: 'add_reader',
        NOTIFY_WRITE: 'add_writer',
    }
    
    disable_map = {
        NOTIFY_READ: 'remove_reader',
        NOTIFY_WRITE: 'remove_writer',
    }
    
    def __init__(self, obj, notify_type, select_fn, notify_fn):
        PSocketNotifierBase.__init__(self, obj, notify_type, select_fn, notify_fn)
        
        process_fn = self.process_fn
        null_fn = (lambda: None)
        self.process_read = process_fn if (notify_type == NOTIFY_READ) else null_fn
        self.process_write = process_fn if (notify_type == NOTIFY_WRITE) else null_fn
        
        self.set_enabled(True)
    
    def fileno(self):
        # We need this so select will recognize us as a file-like object
        return self._obj.fileno()
    
    def process_fn(self):
        if self.select_fn():
            self.notify_fn(self._obj)
    
    def set_enabled(self, enable):
        method_map = (self.disable_map, self.notify_map)[enable]
        method = getattr(self.manager, method_map[self._notify_type])
        method(self)
    
    @classmethod
    def start(cls):
        inst = cls.manager.get_instance()
        inst.run_select_loop()
    
    @classmethod
    def done(cls):
        inst = cls.manager.get_instance()
        inst.exit_loop = True
