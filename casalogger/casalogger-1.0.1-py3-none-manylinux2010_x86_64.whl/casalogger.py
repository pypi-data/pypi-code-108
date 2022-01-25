import os
import subprocess
import argparse
import atexit
import platform

from casatasks import casalog

def casalogger(logfile="", terminal=False):
    app_name = ""
    if platform.system() == "Darwin":
        app_name = "casalogger/__bin__/casalogger.app/Contents/MacOS/casalogger"
    elif platform.system() == "Linux":
        app_name = "casalogger/__bin__/casalogger-x86_64.AppImage"
    else:
        raise Exception("Unsupported platform")
    
    if not logfile:
        logfile = casalog.logfile()

    app_path = os.path.join(
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..")),
        app_name,
    )
    
    try:
        if terminal is False:
            p = subprocess.Popen([app_path, logfile])

            @atexit.register
            def stop_logger():
                p.kill()
        else:
            subprocess.Popen([app_path, logfile])
            
    except KeyboardInterrupt:
        print('\n...Exiting casalogger, goodbye.')
