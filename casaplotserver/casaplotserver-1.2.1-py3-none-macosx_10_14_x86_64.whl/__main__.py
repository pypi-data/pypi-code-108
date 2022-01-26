from __future__ import absolute_import
import sys
import os as __os

for flag in sys.argv:
    if flag == '--app-path':
        from .private.config import app_path
        print(app_path)
    if flag == '--help':
        print("--app-path\t\tpath to casaviewer app")
