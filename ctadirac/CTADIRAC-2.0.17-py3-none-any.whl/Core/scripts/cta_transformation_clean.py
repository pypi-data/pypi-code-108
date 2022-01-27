#!/usr/bin/env python

"""
  Clean an existing transformation

  Usage:
    cta-transformation-clean <transID>
"""

__RCSID__ = "$Id$"

import DIRAC
from DIRAC.Core.Utilities.DIRACScript import DIRACScript as Script
from DIRAC.TransformationSystem.Client.TransformationClient import TransformationClient

@Script()
def main():
    Script.parseCommandLine()
    args = Script.getPositionalArgs()
    if (len(args) != 1):
      Script.showHelp()

    # get arguments
    transID = args[0]

    tc = TransformationClient()
    res = tc.cleanTransformation(transID)

    if not res['OK']:
      DIRAC.gLogger.error(res['Message'])
      DIRAC.exit(-1)
    else:
      DIRAC.gLogger.notice("Successfully cleaned transformation %s" % transID)
      DIRAC.exit(0)

if __name__ == "__main__":
  main()