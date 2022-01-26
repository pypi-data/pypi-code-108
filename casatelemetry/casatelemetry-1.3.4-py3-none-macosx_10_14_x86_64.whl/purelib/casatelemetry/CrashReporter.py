from .lib import CrashReporter as _CrashReporter
import tempfile
import os
import sys

def init(casalogfile ):
    #posterApp="/Users/vsuorant/casatelemetry/__bin__/casacrashreportposter/CrashReportPoster.app/Contents/MacOS/CrashReportPoster"
    temporaryDirectory = tempfile.gettempdir()
    logfile = casalogfile
    postingUrl='https://casa.nrao.edu/cgi-bin/crash-report.pl'
    if sys.platform == 'darwin':
        posterApp = os.path.dirname(_CrashReporter.__file__) + "/../__bin__/casacrashreportposter/Contents/MacOS/CrashReportPoster"
    else:
        posterApp = os.path.dirname(_CrashReporter.__file__) + "/../__bin__/CrashReportPoster"
    #print ("posterApp: " + posterApp)
    _CrashReporter.CrashReporter_initialize (temporaryDirectory, posterApp, postingUrl, logfile)

def CrashReportHelper():
    return _CrashReporter.CrashReportHelper()
