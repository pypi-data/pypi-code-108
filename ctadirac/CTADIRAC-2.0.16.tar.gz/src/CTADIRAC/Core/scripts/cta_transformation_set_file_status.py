#!/usr/bin/env python

"""
  Expects an input file with a list of lfns with the corresponding transID
  Set transformation files to a new status to the new Status

  Usage:
    cta-transformation-set-file-status <ascii file with a list of (transID, lfn)> <newStatus>
"""

__RCSID__ = "$Id$"

import DIRAC
from DIRAC import gLogger
from DIRAC.Core.Utilities.DIRACScript import DIRACScript as Script
from DIRAC.TransformationSystem.Client.TransformationClient import TransformationClient

def read_inputs(file_path):
  content = open(file_path, 'rt').readlines()
  resList = []
  for line in content:
    transID = line.strip().split(" ")[0]
    lfn = line.strip().split(" ")[1]
    if line != "\n":
      resList.append((transID, lfn))
  return resList

@Script()
def main():
  _, argss = Script.parseCommandLine(ignoreErrors=True)
  if len(argss) != 2:
    Script.showHelp()
      
  infile = argss[0]
  newFileStatus = argss[1]
  resList = read_inputs(infile)

  tc = TransformationClient()

  for (transID, lfn) in resList:
    res = tc.setFileStatusForTransformation(transID, newLFNsStatus=newFileStatus, lfns=[lfn])
    if not res['OK']:
      gLogger.error(res['Message'])
      DIRAC.exit(-1)

if __name__ == "__main__":
  main()