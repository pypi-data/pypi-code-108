#!/usr/bin/env python
"""
  Add files to an existing transformation

  Usage:
    cta-transformation-add-files <transID> <ascii file with lfn list>
"""

__RCSID__ = "$Id$"

import DIRAC
from DIRAC.Core.Utilities.DIRACScript import DIRACScript as Script
from DIRAC.TransformationSystem.Client.TransformationClient import TransformationClient
from CTADIRAC.Core.Utilities.tool_box import read_inputs_from_file

@Script()
def main():
    Script.parseCommandLine()
    args = Script.getPositionalArgs()
    if (len(args) != 2):
      Script.showHelp()

    # get arguments
    transID = args[0]
    infile = args[1]
    infileList = read_inputs_from_file(infile)

    tc = TransformationClient()
    res = tc.addFilesToTransformation(transID, infileList)  # Files added here

    if not res['OK']:
      DIRAC.gLogger.error(res['Message'])
      DIRAC.exit(-1)
    else:
      DIRAC.gLogger.notice("Successfully added %d files to transformation %s" % (len(infileList), transID))
      DIRAC.exit(0)

if __name__ == "__main__":
  main()
