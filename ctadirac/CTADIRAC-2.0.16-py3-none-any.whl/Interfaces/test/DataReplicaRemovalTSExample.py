#!/usr/bin/env python
"""
  Create a Transformation for bulk data removal
"""

from DIRAC.Core.Base import Script

Script.setUsageMessage('\n'.join([__doc__.split('\n')[1],
                                  'Usage:',
                                  '  %s [option|cfgfile] ... [File List] ...' % Script.scriptName,
                                  'Arguments:',
                                  '  List of Files to remove']))

Script.parseCommandLine()

from DIRAC.TransformationSystem.Client.Transformation import Transformation
from DIRAC.TransformationSystem.Client.TransformationClient import TransformationClient
from CTADIRAC.Core.Utilities.tool_box import read_inputs_from_file

def DataReplicaRemovalTSExample(args=None):

  if (len(args) != 1):
    Script.gLogger.notice('Wrong number of arguments')
    Script.showHelp()

  infile = args[0]
  infileList = read_inputs_from_file(infile)

  t = Transformation()
  tc = TransformationClient()

  t.setType("Removal")

  t.setPlugin("Broadcast")  # Mandatory for ReplicaRemoval
  t.setSourceSE(['CC-IN2P3-Tape'])  # A list of SE where at least 1 SE is the valid one
  # A list of SE where at least 1 SE is the valid one
  t.setTargetSE(['CEA-Disk', 'LAPP-Disk', 'DESY-ZN-Disk', 'CC-IN2P3-Disk', 'CYF-STORM-Disk'])
  t.setDescription("AarProd2 ReplicaRemoval")
  t.setLongDescription("AarProd2 ReplicaRemoval")  # Mandatory

  t.setGroupSize(100)  # Here you specify how many files should be grouped within the same request, e.g. 100
  t.setBody("Removal;RemoveReplica")  # Mandatory (the default is a ReplicateAndRegister operation)

  t.addTransformation()  # Transformation is created here
  t.setStatus("Active")
  t.setAgentType("Automatic")

  transID = t.getTransformationID()
  tc.addFilesToTransformation(transID['Value'], infileList)  # Files are added here


if __name__ == '__main__':

  args = Script.getPositionalArgs()

  try:
    DataReplicaRemovalTSExample(args)
  except Exception:
    Script.gLogger.exception()
