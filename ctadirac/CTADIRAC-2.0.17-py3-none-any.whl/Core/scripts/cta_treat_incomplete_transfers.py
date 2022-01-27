#!/usr/bin/env python

__RCSID__ = "$Id$"

# DIRAC imports
import DIRAC
from DIRAC import gLogger
from DIRAC.Core.Utilities.DIRACScript import DIRACScript as Script
from DIRAC.TransformationSystem.Client.TransformationClient import TransformationClient

Script.setUsageMessage("""
Treat the incomplete transfers by removing the replicas at source SEs but not at the destination SE

Usage:
   cta-prod-treat-incomplete-transfers <ascii file with list of (transID lfn)> <destSE>

Arguments:
  <ascii file with list of (transID lfn)> : input file with (transID lfn) to treat
  <destSE>                                : destination SE at which the Replica must be kept
""")

Script.parseCommandLine(ignoreErrors=True)

from DIRAC.DataManagementSystem.Client.DataManager import DataManager

def read_inputs(file_path):
  content = open(file_path, 'rt').readlines()
  resList = []
  for line in content:
    transID = line.strip().split(" ")[0]
    lfn = line.strip().split(" ")[1]
    if line != "\n":
      resList.append((transID, lfn))
  return resList

def removeSourceReplica(sourceSEs, lfn):
  dm = DataManager()
  for SE in sourceSEs:
    res = dm.removeReplica(SE, lfn)
    if not res['OK']:
      gLogger.error('Error removing source replicas for:', lfn)
      return res['Message']
  return DIRAC.S_OK()

@Script()
def main():
  args = Script.getPositionalArgs()

  if len(args) != 2:
    Script.showHelp()

  infile = args[0]
  destSE = args[1]
  resList = read_inputs(infile)
  tc = TransformationClient()

  sourceSEs = ['DESY-ZN-Disk', 'LPNHE-Disk', 'CNAF-Disk', 'CYF-STORM-Disk', 'LAPP-Disk', 'CEA-Disk', 'CC-IN2P3-Disk',
               'POLGRID-Disk', 'LANCASTER-Disk','CC-IN2P3-Tape','CNAF-Tape','DESY-ZN-Tape']

  if destSE in sourceSEs:
    sourceSEs.remove(destSE)

  # To do: improve by passing a list with all lfns to setFileStatusForTransformation
  for (transID, lfn) in resList:
    res = removeSourceReplica(sourceSEs, lfn)
    if not res['OK']:
      gLogger.error(res['Message'])
      DIRAC.exit(-1)
    res = tc.setFileStatusForTransformation(transID, newLFNsStatus='Processed', lfns=[lfn])
    if not res['OK']:
      gLogger.error(res['Message'])
      DIRAC.exit(-1)


if __name__ == '__main__':
  main()
