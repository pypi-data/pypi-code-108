#!/usr/bin/env python

"""
  Get tasks attached to a transformation for a given TaskStatus
"""

__RCSID__ = "$Id$"

import DIRAC
from DIRAC import gLogger
from DIRAC.Core.Utilities.DIRACScript import DIRACScript as Script
from DIRAC.TransformationSystem.Client.TransformationClient import TransformationClient

@Script()
def main():
  Script.registerSwitch('', 'TransID=', 'transformation ID')
  Script.registerSwitch('', 'Status=', 'task status')
  Script.parseCommandLine()

  transID = None
  status = None

  for switch in Script.getUnprocessedSwitches():
    if switch[0] == 'TransID':
      try:
        transID = int(switch[1])
      except Exception:
        gLogger.fatal('Invalid transID', switch[1])
    elif switch[0] == 'Status':
      status = switch[1].capitalize()

  if not transID:
    Script.showHelp(exitCode=2)

  tc = TransformationClient()

  condDict = {'TransformationID': transID}
  if status:
    condDict.update({'ExternalStatus': status})

  res = tc.getTransformationTasks(condDict)

  if not res['OK']:
    DIRAC.gLogger.error(res['Message'])
    DIRAC.exit(2)

  if len(res['Value']) == 0:
    DIRAC.gLogger.notice("No tasks selected for transformation %s with status %s" % (transID, status))

  for task in res['Value']:
    DIRAC.gLogger.notice(task["TaskID"])

if __name__ == "__main__":
  main()