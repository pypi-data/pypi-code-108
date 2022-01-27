"""
    Launcher script to launch EvnDisp processing on Prod3b SCT with Alpha Array
    submit to WMS or create a Transformation
    https://forge.in2p3.fr/issues/46540
    https://forge.in2p3.fr/issues/47784
"""

__RCSID__ = "$Id$"

from copy import copy

from DIRAC.Core.Base import Script
Script.setUsageMessage(
    '\n'.join(
        [
            __doc__.split('\n')[1],
            'Usage:',
            '  %s TS trans_name input_dataset_name group_size' %
            Script.scriptName,
            '  %s WMS' %
            Script.scriptName,
            'Arguments:',
            '  mode: WMS for testing, TS for production',
            '  trans_name: (with mode=TS) name of the transformation',
            '  input_dataset_name: (with mode=TS) name of the input dataset',
            '  group_size: (with mode=TS) n files per job',
            '\ne.g: python %s.py TS MyNewTrans Prod4-Paranal-gamma-North-DL-3 5' %
            Script.scriptName,
        ]))

Script.parseCommandLine()

import DIRAC
from DIRAC.TransformationSystem.Client.Transformation import Transformation
from CTADIRAC.Interfaces.API.EvnDispProd3SCTMergeSingJob import EvnDispProd3SCTMergeSingJob
from DIRAC.Core.Workflow.Parameter import Parameter
from DIRAC.Interfaces.API.Dirac import Dirac
from CTADIRAC.Core.Utilities.tool_box import get_dataset_MQ


def submit_trans(job, trans_name, input_meta_query, group_size):
  """ Create a transformation executing the job workflow
  """
  DIRAC.gLogger.notice('submit_trans : %s' % trans_name)

  # Initialize JOB_ID
  job.workflow.addParameter(Parameter("JOB_ID", "000000", "string", "", "",
                                      True, False, "Temporary fix"))

  trans = Transformation()
  trans.setTransformationName(trans_name)  # this must be unique
  trans.setType("DataReprocessing")
  trans.setDescription("Prod3b-sct-merge EventDisplay TS")
  trans.setLongDescription("Prod3b-sct-merge EventDisplay processing")  # mandatory
  trans.setBody(job.workflow.toXML())
  trans.setGroupSize(group_size)
  trans.setInputMetaQuery(input_meta_query)
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
  # prod3b sct input file
  base_path = '/vo.cta.in2p3.fr/MC/PROD3/scratch/Paranal/gamma/simtel/954/Data/000xxx'
  input_data = ['%s/gamma_20deg_0deg_run100___cta-prod3-sct_desert-2150m-Paranal-SCT.simtel.gz' % base_path]

  job.setInputData(input_data)
  job.setJobGroup('EvnDispProd3bSCT-merge')
  result = dirac.submitJob(job)
  if result['OK']:
    Script.gLogger.notice('Submitted job: ', result['Value'])
  return result


def launch_job(args):
  """ Simple launcher to instanciate a Job and setup parameters
      from positional arguments given on the command line.

      Parameters:
      args -- mode (trans_name dataset_name group_size)
  """
  DIRAC.gLogger.notice('Running EventDisplay jobs')
  # get arguments
  mode = args[0]

  if mode == 'TS':
    trans_name = args[1]
    dataset_name = args[2]
    group_size = int(args[3])

  # job setup - 72 hours
  job = EvnDispProd3SCTMergeSingJob(cpuTime=259200.)
  job.version = 'eventdisplay-cta-dl1-prod3b-sct-merge.v02'
  # For SCT Alpha 156 tel use
  #job.version = 'eventdisplay-cta-dl1-prod3b-sct-156tel-merge.v01'
  # override for testing
  job.setName('Prod3b-sct-merge_EvnDisp')
  # output
  job.setOutputSandbox(['*Log.txt'])

  # specific configuration
  if mode == 'WMS':
    job.base_path = '/vo.cta.in2p3.fr/user/a/arrabito'
    job.ts_task_id = '62'
    simtel_meta_data = {'array_layout': 'SCTAlpha', 'site': 'Paranal',
                        'particle': 'gamma', 'phiP': 180.0, 'thetaP': 20.0}
    # For SCT Alpha 156 tel use
    simtel_meta_data = {'array_layout': 'SCTAlpha-156tel', 'site': 'Paranal',
                        'particle': 'gamma', 'phiP': 180.0, 'thetaP': 20.0}
    job.set_meta_data(simtel_meta_data)
    job.set_file_meta_data(nsb=1)
    job.setupWorkflow(debug=True)
    # submit to the WMS for debug
    # job.setDestination('LCG.IN2P3-CC.fr')
    result = submit_wms(job)
  elif mode == 'TS':
    input_meta_query = get_dataset_MQ(dataset_name)
    # refine output meta data if needed
    output_meta_data = copy(input_meta_query)
    job.set_meta_data(output_meta_data)
    job.set_file_meta_data(nsb=1)
    # adjust calibration file
    job.ts_task_id = '@{JOB_ID}'  # dynamic
    job.group_size = group_size   # for the input files verification
    job.setupWorkflow(debug=False)
    job.setType('EvnDisp3')  # mandatory *here*
    result = submit_trans(job, trans_name, input_meta_query, group_size)
  else:
    DIRAC.gLogger.error('1st argument should be the job mode: WMS or TS,\n\
                             not %s' % mode)
    return None

  return result


#########################################################
if __name__ == '__main__':

  arguments = Script.getPositionalArgs()
  if len(arguments) not in [1, 4]:
    Script.showHelp()
  try:
    result = launch_job(arguments)
    if not result['OK']:
      DIRAC.gLogger.error(result['Message'])
      DIRAC.exit(-1)
    else:
      DIRAC.gLogger.notice('Done')
  except Exception:
    DIRAC.gLogger.exception()
    DIRAC.exit(-1)
