#!/usr/bin/env python

"""
  Delete a transformation or a list of transformations

  Usage:
    cta-transformation-delete <list of transID comma separated OR ascii file containing a list of transID (comma-separated on each line)>
"""

__RCSID__ = "$Id$"

import os

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
    transIDs = []
    for arg in args[0].split(','):
      if os.path.exists(arg):
        lines = open(arg, 'rt').readlines()
        for line in lines:
          for transID in line.split(','):
            transIDs += [int(transID.strip())]
      else:
        transIDs.append(int(arg))

    tc = TransformationClient()

    for transID in transIDs:
      res = tc.deleteTransformation(transID)
      if not res['OK']:
        DIRAC.gLogger.error('Failed to delete transformation %s: %s' % (transID, res['Message']))
        continue
      else:
        DIRAC.gLogger.notice("Successfully deleted transformation %s" % transID)

    DIRAC.exit(0)

if __name__ == "__main__":
  main()