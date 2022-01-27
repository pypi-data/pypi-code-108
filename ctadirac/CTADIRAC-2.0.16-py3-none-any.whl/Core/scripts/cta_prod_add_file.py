#!/usr/bin/env python

__RCSID__ = "$Id$"

# generic imports
import os
from multiprocessing import Pool

# DIRAC imports
from DIRAC import gLogger
from CTADIRAC.Core.Utilities.tool_box import read_inputs_from_file
from DIRAC.Core.Utilities.DIRACScript import DIRACScript as Script

Script.setUsageMessage("""
Bulk upload of a list of local files from the current directory to a Storage Element
Usage:
   cta-prod-add-file <ascii file with lfn list> <SE>
""")

Script.parseCommandLine(ignoreErrors=True)

args = Script.getPositionalArgs()
if len(args) > 1:
  infile = args[0]
  SE = args[1]
else:
  Script.showHelp()

# Import of Dirac must comes after parseCommandLine
from DIRAC.Interfaces.API.Dirac import Dirac

@Script()
def main():
  infileList = read_inputs_from_file(infile)
  p = Pool(10)
  p.map(addfile, infileList)

def addfile(lfn):
  dirac = Dirac()
  res = dirac.addFile(lfn, os.path.basename(lfn), SE)
  if not res['OK']:
    gLogger.error('Error uploading file', lfn)
    return res['Message']

if __name__ == '__main__':
  main()
