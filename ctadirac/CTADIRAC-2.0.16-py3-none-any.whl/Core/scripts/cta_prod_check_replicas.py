#!/usr/bin/env python

__RCSID__ = "$Id$"


# DIRAC imports
import DIRAC
from DIRAC import gLogger
from DIRAC.Core.Utilities.DIRACScript import DIRACScript as Script

Script.setUsageMessage("""
Check replica location against the a given SE
Usage:
   cta-check-get-replicas <ascii file with lfn list> <destSE>
""")

Script.parseCommandLine(ignoreErrors=True)

from DIRAC.Resources.Catalog.FileCatalog import FileCatalog
fc = FileCatalog()

args = Script.getPositionalArgs()
if len(args) > 0:
  infile = args[0]
  destSE = args[1]
else:
  Script.showHelp()

f0 = open("%s_NoReplicas.lfns" % (infile), "w")
f1 = open("%s_SingleReplica_%s.lfns" % (infile, destSE), "w")
f2 = open("%s_MultipleReplicas_%s.lfns" % (infile, destSE), "w")
f3 = open("%s_MissingReplica_%s.lfns" % (infile, destSE), "w")

@Script()
def main():
  resList = read_inputs(infile)
  for (transID, lfn) in resList:
    checkReplicas(transID, lfn)
  gLogger.notice('Files dumped: check %s_*.lfns' % (infile))

def read_inputs(file_path):
  content = open(file_path, 'rt').readlines()
  resList = []
  for line in content:
    transID = line.strip().split(" ")[0]
    lfn = line.strip().split(" ")[1]
    if line != "\n":
      resList.append((transID, lfn))
  return resList

def checkReplicas(transID, lfn):
  res = fc.getReplicas(lfn)
  if not res['OK']:
    gLogger.notice('Failed to get replicas for lfn', lfn)
    return res['Message']
  if lfn in res['Value']['Successful']:
    resDict = res['Value']['Successful'][lfn]
    nReplicas = len(resDict)
    if destSE in resDict:
      if nReplicas == 1:
        f1.write("%s %s\n" % (transID, lfn))
      else:
        f2.write("%s %s\n" % (transID, lfn))
    else:
      if nReplicas == 0:
        f0.write("%s %s\n" % (transID, lfn))
      else:
        f3.write("%s %s\n" % (transID, lfn))
  else:
    res = DIRAC.S_ERROR('Failed to get replicas for lfn %s' % lfn)
    gLogger.notice(res['Message'])
    return res

if __name__ == '__main__':
  main()
