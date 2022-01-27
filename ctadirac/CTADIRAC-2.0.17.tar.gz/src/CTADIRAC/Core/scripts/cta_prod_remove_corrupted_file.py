#!/usr/bin/env python

"""
Remove files downloaded as job InputData having a Bad checksum
"""

__RCSID__ = "$Id$"

# Generic imports
import os

# DIRAC imports
import DIRAC
from DIRAC.Core.Base import Script
Script.parseCommandLine()

# Specific DIRAC imports
from DIRAC.DataManagementSystem.Client.DataManager import DataManager
from DIRAC.Interfaces.API.Dirac import Dirac

def main():
  if 'JOBID' in os.environ:
    jobID = os.environ['JOBID']
    dirac = Dirac()
    res = dirac.getJobJDL(jobID)
    if 'InputData' in res['Value']:
      lfn = res['Value']['InputData']

  dm = DataManager(['DIRACFileCatalog'])
  DIRAC.gLogger.notice('Check file: %s' % lfn)

  res = dm.getFile(lfn)

  if lfn in res['Value']['Failed']:
    if 'Bad checksum' in res['Value']['Failed'][lfn]:
      DIRAC.gLogger.notice('Bad checksum. Removing: %s' % lfn)
      res = dm.removeFile(lfn)
      if res['OK']:
        DIRAC.gLogger.notice('Successfully removed: %s' % lfn)
      else:
        DIRAC.gLogger.error(res['Message'])
        DIRAC.exit(-1)
  else:
    DIRAC.gLogger.notice('Good checksum for: %s' % lfn)
    DIRAC.exit()

####################################################
if __name__ == '__main__':
  main()