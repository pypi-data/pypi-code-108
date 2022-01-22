#!/usr/bin/env python3
"""
Sub-Package UI.TOOLKITS of Package PLIB3 -- Python UI Toolkits
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This sub-package contains sub-sub-packages for each of the supported
UI toolkits.
"""

import sys
import os
import tempfile

from plib.stdlib.builtins import first
from plib.stdlib.proc import process_call


class ToolkitError(Exception):
    pass


DETECT_TEMPLATE = """# Toolkit detection temporary script

import sys

try:
    import {import_name}
except ImportError:
    sys.exit(1)
else:
    sys.exit(0)
"""


class _ToolkitManager(object):
    
    supported_toolkits = (
        'pyside2',
        'qt5',
        'wx',
    )
    
    def __init__(self):
        # We don't auto-initialize because we don't want to go through the
        # auto-detection process unless we have to; the application can call
        # set_toolkit before any other plib.ui modules are imported to avoid
        # triggering the auto-detection machinery
        
        self.available_toolkits = []
        self.toolkit = None
        
        env_var = os.getenv('UI_TOOLKIT')
        if env_var is not None:
            self.set_toolkit(env_var)
    
    def init_toolkit(self):
        self.available_toolkits[:] = self.detect_toolkits()
        self.toolkit = first(t for t in self.supported_toolkits if t in self.available_toolkits)
    
    import_map = {
        'pyside2': "PySide2",
        'qt5': "PyQt5",
    }
    
    script_template = DETECT_TEMPLATE
    script_filename = "toolkit_detect.py"
    
    script_dir = None
    
    def is_detected(self, toolkit):
        import_name = self.import_map.get(toolkit, toolkit)
        script_data = self.script_template.format(**locals())
        filename = os.path.join(self.script_dir, self.script_filename)
        
        exitcode = -1
        try:
            with open(filename, 'w') as f:
                f.write(script_data)
            exitcode, _ = process_call([sys.executable, filename])
        finally:
            if os.path.isfile(filename):
                os.remove(filename)
        
        return (exitcode == 0)
    
    def detect_toolkits(self):
        # We have to go through all this because having multiple toolkit modules
        # imported in the same interpreter process can cause errors, so we have
        # to test for each of them in a separate process. This makes the detection
        # machinery somewhat heavyweight, which is why we avoid using it unless we
        # have to.
        
        detected = []
        
        self.script_dir = tempfile.mkdtemp()
        try:
            for toolkit in self.supported_toolkits:
                if self.is_detected(toolkit):
                    detected.append(toolkit)
        finally:
            os.rmdir(self.script_dir)
            del self.script_dir
        
        return detected
    
    def get_toolkit(self):
        if not self.toolkit:
            print("Need to initialize toolkits")
            self.init_toolkit()
        return self.toolkit
    
    def set_toolkit(self, toolkit):
        if toolkit not in self.supported_toolkits:
            raise ToolkitError("Toolkit not supported: {}".format(toolkit))
        # We don't check for availability here, the caller is responsible for
        # handling any errors if the specified toolkit is not available
        print("Setting toolkit to", toolkit)
        self.toolkit = toolkit


_manager = _ToolkitManager()

supported_toolkits = _manager.supported_toolkits
available_toolkits = _manager.available_toolkits

get_toolkit = _manager.get_toolkit
set_toolkit = _manager.set_toolkit
