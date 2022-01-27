#!/usr/bin/env python
"""
  Check if files exist in the Catalog
  and dump the list of Found and Not Found files

  Usage:
  cta-dms-check-lfn [options] <ascii file with lfn list>
"""

__RCSID__ = "$Id$"

import DIRAC
from DIRAC.Core.Utilities.DIRACScript import DIRACScript as Script
from DIRAC import gLogger
from DIRAC.Resources.Catalog.FileCatalogClient import FileCatalogClient
from CTADIRAC.Core.Utilities.tool_box import read_inputs_from_file

@Script()
def main():
  Script.parseCommandLine(ignoreErrors=True)
  args = Script.getPositionalArgs()
  if len(args) > 0:
    infile = args[0]
  else:
    Script.showHelp()

  lfns = read_inputs_from_file(infile)
  lfnsFound = []
  lfnsNotFound = []

  fc = FileCatalogClient()

  for lfn in lfns:
    res = fc.exists(lfn)
    if not res['OK']:
      gLogger.error(res['Message'])

    if res['Value']['Successful'][lfn]:
      gLogger.debug('%s found in Catalog' % lfn)
      lfnsFound.append(lfn)
    else:
      gLogger.debug('%s not found in Catalog' % lfn)
      lfnsNotFound.append(lfn)

  fname = infile + '_Found.list'
  f = open(fname, 'w')
  for lfn in lfnsFound:
    f.write(lfn + '\n')
  f.close()
  gLogger.notice('%d files have been dumped in %s' % (len(lfnsFound), fname))

  fname = infile + '_NotFound.list'
  f = open(fname, 'w')
  for lfn in lfnsNotFound:
    f.write(lfn + '\n')
  f.close()
  gLogger.notice('%d files have been dumped in %s' % (len(lfnsNotFound), fname))
  DIRAC.exit()

####################################################
if __name__ == '__main__':
  main()