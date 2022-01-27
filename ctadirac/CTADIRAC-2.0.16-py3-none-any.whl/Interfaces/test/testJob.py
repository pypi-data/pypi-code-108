"""
    Launcher script for a simple job example
"""

__RCSID__ = "$Id$"

from DIRAC.Core.Base import Script
Script.parseCommandLine()
from DIRAC.Interfaces.API.Job import Job
from DIRAC import gLogger
from DIRAC.Interfaces.API.Dirac import Dirac

dirac = Dirac()
j = Job()
j.setCPUTime(500)
j.setExecutable('ls')
j.setName('testjob')
res = dirac.submitJob(j)
gLogger.notice('Submission Result:', res['Value'])
