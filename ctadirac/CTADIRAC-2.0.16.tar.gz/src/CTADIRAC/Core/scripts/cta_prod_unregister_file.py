#!/usr/bin/env python

__RCSID__ = "$Id$"

# generic imports
from multiprocessing import Pool

# DIRAC imports
from DIRAC import gLogger
from CTADIRAC.Core.Utilities.tool_box import read_inputs_from_file
from DIRAC.Core.Utilities.DIRACScript import DIRACScript as Script

Script.setUsageMessage("""
Bulk removal of a list of files from the catalog
Usage:
   cta-prod-unregister-file <ascii file with lfn list>
""")

Script.parseCommandLine(ignoreErrors=True)
# Must comes after parseCommandLine
from DIRAC.Resources.Catalog.FileCatalog import FileCatalog
fc = FileCatalog()

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

@Script()
def main():
  args = Script.getPositionalArgs()
  if len(args) > 0:
    infile = args[0]
  else:
    Script.showHelp()

  infileList = read_inputs_from_file(infile)
  p = Pool(10)
  p.map(unregisterFile, infileList)

if __name__ == '__main__':
  main()