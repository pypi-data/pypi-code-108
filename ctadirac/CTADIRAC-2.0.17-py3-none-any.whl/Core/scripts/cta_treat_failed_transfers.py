#!/usr/bin/env python

__RCSID__ = "$Id$"

# DIRAC imports
import DIRAC
from DIRAC import gLogger
from DIRAC.Core.Utilities.DIRACScript import DIRACScript as Script
from DIRAC.TransformationSystem.Client.TransformationClient import TransformationClient

Script.setUsageMessage("""
Treat failed transfers by setting the transformation file status to Unused

Usage:
   cta-prod-treat-failed-transfers <ascii file with list of (transID lfn)>

Arguments:
  <ascii file with list of (transID lfn)> : input file with (transID lfn) to treat
""")

Script.parseCommandLine(ignoreErrors=True)

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
  if len(argss) != 1:
    Script.showHelp()

  infile = argss[0]
  resList = read_inputs(infile)

  # Initialize the transDict with all transID keys
  transDict = {}
  for (transID, lfn) in resList:
    transDict.update({transID:[]})

  # Update the transDict with values
  for (transID, lfn) in resList:
    transDict[transID].append(lfn)

  tc = TransformationClient()

  for transID in transDict:
    res = tc.setFileStatusForTransformation(transID, newLFNsStatus='Unused', lfns=transDict[transID])
    if not res['OK']:
      gLogger.error(res['Message'])
      DIRAC.exit(-1)

if __name__ == '__main__':
  main()
