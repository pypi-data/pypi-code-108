#!/usr/bin/env python

__RCSID__ = "$Id$"

# DIRAC imports
import DIRAC
from DIRAC import gLogger
from DIRAC.Core.Utilities.DIRACScript import DIRACScript as Script
from DIRAC.TransformationSystem.Client.TransformationClient import TransformationClient

Script.setUsageMessage("""
Treat problematic transfers for files with No replicas
Unregister files from the catalog and set transformation files to Processed

Usage:
   cta-prod-treat-problematic-transfers <ascii file with list of (transID lfn)>

Arguments:
  <ascii file with list of (transID lfn)> : input file with (transID lfn) to treat
""")

Script.parseCommandLine(ignoreErrors=True)
# Must comes after parseCommandLine
from DIRAC.Resources.Catalog.FileCatalog import FileCatalog
fc = FileCatalog()

def read_inputs(file_path):
  content = open(file_path, 'rt').readlines()
  resList = []
  for line in content:
    transID = line.strip().split(" ")[0]
    lfn = line.strip().split(" ")[1]
    if line != "\n":
      resList.append((transID, lfn))
  return resList

def unregisterFile(lfn):
  res = fc.removeFile(lfn)
  if res['OK']:
    if 'Failed' in res['Value']:
      if lfn in res['Value']['Failed']:
        gLogger.error(res['Value']['Failed'][lfn])
      elif lfn in res['Value']['Successful']:
        gLogger.notice("Successfully removed from the catalog", lfn)
      else:
        gLogger.error("Unexpected error result", res['Value'])
    else:
      gLogger.notice("Successfully removed from the catalog", lfn)
  else:
    gLogger.error("Failed to remove file from the catalog:", res['Message'])

  if not res['OK']:
    gLogger.error(res['Message'])

  return DIRAC.S_OK()

@Script()
def main():

  args = Script.getPositionalArgs()
  if len(args) != 1:
    Script.showHelp()

  infile = args[0]
  resList = read_inputs(infile)

  # Initialize the transDict with the transID keys
  transDict = {}
  for (transID, lfn) in resList:
    transDict.update({transID:[]})

  # Unregister file from the catalog and update the transDict with values
  for (transID, lfn) in resList:
    res = unregisterFile(lfn)
    if not res['OK']:
      gLogger.error(res['Message'])
      DIRAC.exit(-1)
    transDict[transID].append(lfn)

  tc = TransformationClient()

  for transID in transDict:
    res = tc.setFileStatusForTransformation(transID, newLFNsStatus='Processed', lfns=transDict[transID])
    if not res['OK']:
      gLogger.error(res['Message'])
      DIRAC.exit(-1)

if __name__ == '__main__':
  main()
