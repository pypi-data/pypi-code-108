from __future__ import absolute_import
import sys
import os as __os

for flag in sys.argv:
    if flag == '--app-path':
        from .private.config import app_path
        print(app_path)
    if flag == '--app':
        from .private.config import app_path
        if __os.fork( ) == 0:
            __os.execvp(app_path, [app_path] if len(sys.argv) <= 2 else [app_path] + sys.argv[2:])
            __os.exit(1)
        else:
            sys.exit(0)
    if flag == '--help':
        print("--app\t\t\tstart casaviewer and pass along any parameters")
        print("--app-path\t\tpath to casaviewer app")
