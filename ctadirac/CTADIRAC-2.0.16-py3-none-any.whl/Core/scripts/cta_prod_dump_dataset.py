#!/usr/bin/env python
"""
Dump in a file the list of files for a given dataset

Usage:
   cta-prod-dump-dataset <datasetName>
"""

__RCSID__ = "$Id$"

import DIRAC
from DIRAC import gLogger
from DIRAC.Core.Utilities.DIRACScript import DIRACScript as Script
from DIRAC.Resources.Catalog.FileCatalogClient import FileCatalogClient

@Script()
def main():
  Script.parseCommandLine(ignoreErrors=True)
  argss = Script.getPositionalArgs()
  fc = FileCatalogClient()

  if len(argss) > 0:
    datasetName = argss[0]
  else:
    Script.showHelp()

  result = fc.getDatasetFiles(datasetName)

  if not result['OK']:
    gLogger.error("Failed to get files for dataset:", result['Message'])
    DIRAC.exit(-1)
  else:
    lfnList = result['Value']['Successful'][datasetName]

    f = open(datasetName + '.list', 'w')
    for lfn in lfnList:
      f.write(lfn + '\n')
    f.close()
    gLogger.notice('%d files have been put in %s.list' % (len(lfnList), datasetName))
    DIRAC.exit()

####################################################
if __name__ == '__main__':
  main()