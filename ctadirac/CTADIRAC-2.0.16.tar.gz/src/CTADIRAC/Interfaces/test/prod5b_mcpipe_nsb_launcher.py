""" Launcher script to launch a Prod5MCPipeNSBJob
on the WMS or create a Transformation.

    https://forge.in2p3.fr/issues/38939
                    JB, June 2020
"""

import json
from copy import copy

from DIRAC.Core.Base import Script
Script.setUsageMessage('\n'.join([__doc__.split('\n')[1],
                                  'Usage:',
                                  'python %s.py <mode> <site> <particle> <pointing> <zenith> <n showers>' % Script.scriptName,
                                  'Arguments:',
                                  '  mode: WMS for testing, TS for production',
                                  '  site: either Paranal or LaPalma',
                                  '  particle: in gamma, gamma-diffuse, electron, proton',
                                  '  pointing: North or South',
                                  '  zenith: 20, 40 or 60',
                                  '  n shower: 100 for testing',
                                  '\ne.g: python %s.py WMS Paranal gamma North 20 100' % Script.scriptName,
                                  ]))

Script.parseCommandLine()

import DIRAC
from DIRAC.TransformationSystem.Client.Transformation import Transformation
from CTADIRAC.Interfaces.API.Prod5bMCPipeNSBJob import Prod5bMCPipeNSBJob
from DIRAC.Core.Workflow.Parameter import Parameter
from DIRAC.Interfaces.API.Dirac import Dirac


def submit_transformation(job, trans_name):
  """ Create a transformation executing the job workflow
  """
  DIRAC.gLogger.notice('submit_trans : %s' % trans_name)

  # Initialize JOB_ID
  job.workflow.addParameter(Parameter("JOB_ID", "000000", "string", "", "",
                                      True, False, "Temporary fix"))

  trans = Transformation()
  trans.setTransformationName(trans_name)  # this must be unique
  trans.setType("MCSimulation")
  trans.setDescription("Prod5 MC Pipe NSB TS")
  trans.setLongDescription("Prod5 simulation pipeline")  # mandatory
  trans.setBody(job.workflow.toXML())
  result = trans.addTransformation()  # transformation is created here
  if not result['OK']:
    return result
  trans.setStatus("Active")
  trans.setAgentType("Automatic")
  trans_id = trans.getTransformationID()
  return trans_id


def submit_wms(job):
  """ Submit the job to the WMS
  @todo launch job locally
  """
  dirac = Dirac()
  job.setJobGroup('Prod5MCPipeNSBJob')
  result = dirac.submitJob(job)
  if result['OK']:
    Script.gLogger.notice('Submitted job: ', result['Value'])
  return result


def run_simulation(args):
  """ Simple wrapper to create a Prod5MCPipeNSBJob and setup parameters
      from positional arguments given on the command line.

      Parameters:
      args -- mode (trans_name)
  """
  DIRAC.gLogger.notice('run_mc_pipeline')
  # get arguments
  mode = args[0]

  # job setup
  job = Prod5bMCPipeNSBJob()  # to be adjusted!!
  job.version = '2020-06-29b'
  job.compiler = 'gcc83_matchcpu'
  # override for testing
  job.setName('Prod5b_MC_Pipeline_NSB')
  # parameters from command line
  job.set_site(args[1])
  job.set_particle(args[2])
  job.set_pointing_dir(args[3])
  job.zenith_angle = args[4]
  job.n_shower = args[5]

  # output
  job.setOutputSandbox(['*Log.txt'])

  # specific configuration
  if mode == 'WMS':
    # put here your user directory under the Dirac File Catalog
    job.base_path = '/vo.cta.in2p3.fr/user/b/bregeon/prod5b_test_1/'
    # adjust start_run_number and run_number for testing, both can be 0
    job.start_run_number = '0'
    job.run_number = '11'
    job.setupWorkflow(debug=True)
    # submit to the WMS for debug, choose a destination site
    # job.setDestination('LCG.IN2P3-CC.fr')
    job.setDestination('LCG.DESY-ZEUTHEN.de')
    result = submit_wms(job)
  elif mode == 'TS':
    # put here your user directory under the Dirac File Catalog
    job.base_path = '/vo.cta.in2p3.fr/user/b/bregeon/prod5b_JB_test_3'
    job.start_run_number = '0'
    job.run_number = '@{JOB_ID}'  # dynamic
    job.setupWorkflow(debug=False)
    # extra tag in case you have to run different tests, can be empty
    tag = ''
    # Change below the name of transformation, in particular the user name
    # this name must be unique accross the whole system
    trans_name = 'bregeon_Prod5b_Test_%s_%s_%s_%s%s' %\
        (job.cta_site, job.particle, job.pointing_dir, job.zenith_angle, tag)
    result = submit_transformation(job, trans_name)
  else:
    DIRAC.gLogger.error('1st argument should be the job mode: WMS or TS,\n\
                             not %s' % mode)
    return None

  return result


#########################################################
if __name__ == '__main__':

  arguments = Script.getPositionalArgs()
  if len(arguments) != 6:
    Script.showHelp()
  try:
    result = run_simulation(arguments)
    if not result['OK']:
      DIRAC.gLogger.error(result['Message'])
      DIRAC.exit(-1)
    else:
      DIRAC.gLogger.notice('Done')
  except Exception:
    DIRAC.gLogger.exception()
    DIRAC.exit(-1)
