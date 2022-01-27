#!/usr/bin/env python
'''
Remove a given dataset

Usage:
   cta-prod-remove-dataset <datasetName or ascii file with a list of datasets>
'''

__RCSID__ = "$Id$"

import os
import DIRAC
from DIRAC import gLogger
from DIRAC.Core.Utilities.DIRACScript import DIRACScript as Script
from CTADIRAC.Core.Utilities.tool_box import read_inputs_from_file
from DIRAC.Resources.Catalog.FileCatalogClient import FileCatalogClient

@Script()
def main():
    Script.parseCommandLine(ignoreErrors=True)
    argss = Script.getPositionalArgs()
    fc = FileCatalogClient()
    datasetList = []
    if len(argss) == 1:
      if os.path.isfile(argss[0]):
        gLogger.notice('Reading datasets from input file: %s' % argss[0])
        datasetList = read_inputs_from_file(argss[0])
      else:
        datasetList.append(argss[0])
    else:
      Script.showHelp()

    for dataset in datasetList:
      result = fc.removeDataset(dataset)

      if not result['OK']:
        gLogger.error("Failed to remove %s: %s" % (dataset, result['Message']))
        DIRAC.exit(-1)
      else:
        gLogger.notice("Successfully removed dataset", dataset)

    DIRAC.exit()

####################################################
if __name__ == '__main__':
  main()