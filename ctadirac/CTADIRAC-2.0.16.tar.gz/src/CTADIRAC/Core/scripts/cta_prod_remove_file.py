#!/usr/bin/env python

__RCSID__ = "$Id$"

# generic imports
from multiprocessing import Pool

# DIRAC imports
from DIRAC import gLogger
from CTADIRAC.Core.Utilities.tool_box import read_inputs_from_file
from DIRAC.Core.Utilities.DIRACScript import DIRACScript as Script

Script.setUsageMessage("""
Bulk removal of a list of files
Usage:
   cta-prod-remove-file [options] <ascii file with lfn list>
""")

Script.parseCommandLine(ignoreErrors=True)

from DIRAC.Resources.Catalog.FileCatalog import FileCatalog
fc = FileCatalog()

def removeFile(lfn):
  res = fc.removeFile(lfn)
  if not res['OK']:
    gLogger.error('Error removing file', lfn)
    return res['Message']

@Script()
def main():
  args = Script.getPositionalArgs()
  if len(args) > 0:
    infile = args[0]
  else:
    Script.showHelp()

  infileList = read_inputs_from_file(infile)
  p = Pool(10)
  p.map(removeFile, infileList)

if __name__ == '__main__':
  main()
