"""
    Launcher script to launch a production with 2 steps
    simulation Step: Prod5bMCPipeNSBJob
    calibimgreco Step: EvnDispProd5SingJob
"""

__RCSID__ = "$Id$"

import json
from copy import copy

from DIRAC.Core.Base import Script
Script.parseCommandLine()
import DIRAC

from DIRAC.ProductionSystem.Client.ProductionClient import ProductionClient
from DIRAC.ProductionSystem.Client.ProductionStep import ProductionStep
from CTADIRAC.Interfaces.API.Prod5bMCPipeNSBJob import Prod5bMCPipeNSBJob
from CTADIRAC.Interfaces.API.EvnDispProd5SingJob import EvnDispProd5SingJob
from CTADIRAC.Core.Utilities.tool_box import get_dataset_MQ
from DIRAC.Core.Workflow.Parameter import Parameter


def build_simulation_step(DL0_data_set, name_tag=''):
  ''' Setup Corsika + sim_telarray step

  Note that there is no InputQuery,
  since jobs created by this steps don't require any InputData

  @return ProductionStep object
  '''
  # Note that there is no InputQuery,
  # since jobs created by this steps don't require any InputData
  prod_step_1 = ProductionStep()
  prod_step_1.Name = 'Simulation_%s' % DL0_data_set.replace('AdvancedBaseline_NSB1x_', '')
  prod_step_1.Name += '%s' % name_tag
  DIRAC.gLogger.notice('\tBuilding MC Production step: %s' % prod_step_1.Name)
  prod_step_1.Type = 'MCSimulation'
  prod_step_1.Outputquery = get_dataset_MQ(DL0_data_set)
  prod_step_1.Outputquery['nsb'] = {'in': [1, 5]}

  # get meta data to be passed to simulation job
  site = prod_step_1.Outputquery['site']
  particle = prod_step_1.Outputquery['particle']
  if prod_step_1.Outputquery['phiP']['='] == 180:
    pointing_dir = 'North'
  elif prod_step_1.Outputquery['phiP']['='] == 0:
    pointing_dir = 'South'
  zenith_angle = prod_step_1.Outputquery['thetaP']['=']

  # Here define the job description (i.e. Name, Executable, etc.)
  # to be associated to the first ProductionStep, as done when using the TS
  job1 = Prod5bMCPipeNSBJob()
  job1.version = '2020-06-29b'
  job1.compiler = 'gcc83_matchcpu'
  # Initialize JOB_ID
  job1.workflow.addParameter(Parameter("JOB_ID", "000000", "string", "", "",
                                       True, False, "Temporary fix"))
  # configuration
  job1.setName('Prod5b_MC_Pipeline_NSB')
  job1.set_site(site)
  job1.set_particle(particle)
  job1.set_pointing_dir(pointing_dir)
  job1.zenith_angle = zenith_angle
  job1.n_shower = 50000
  if particle == 'gamma':
    job1.n_shower = 20000

  job1.setOutputSandbox(['*Log.txt'])
  job1.start_run_number = '0'
  job1.run_number = '@{JOB_ID}'  # dynamic
  job1.output_file_size = 100000  # 200 MB
  job1.setupWorkflow(debug=False)
  # Add the job description to the first ProductionStep
  prod_step_1.Body = job1.workflow.toXML()
  # return ProductionStep object
  return prod_step_1


def build_evndisp_step(DL0_data_set, nsb=1, name_tag=''):
  ''' Define a new EventDisplay analysis production step

  @return ProductionStep object
  '''
  if nsb == 1:
    DL0_data_set_NSB = DL0_data_set
  elif nsb == 5:
    DL0_data_set_NSB = DL0_data_set.replace('NSB1x', 'NSB5x')

  prod_step_2 = ProductionStep()
  prod_step_2.Name = 'Analysis_' + DL0_data_set_NSB.replace('AdvancedBaseline_', '').replace('DL0', 'DL1')
  prod_step_2.Name += '%s' % name_tag
  DIRAC.gLogger.notice('\tBuilding Analysis Production step: %s' % prod_step_2.Name)
  prod_step_2.Type = 'DataReprocessing'  # This corresponds to the Transformation Type
  prod_step_2.Inputquery = get_dataset_MQ(DL0_data_set_NSB)
  prod_step_2.Outputquery = get_dataset_MQ(DL0_data_set_NSB.replace('DL0', 'DL1'))

  # Here define the job description to be associated to the second ProductionStep
  job2 = EvnDispProd5SingJob(cpuTime=259200.)
  job2.version = 'eventdisplay-cta-dl1-prod5.v04'
  job2.setName('Prod5b_EvnDisp_Singularity')
  # output
  job2.setOutputSandbox(['*Log.txt'])
  # refine output meta data if needed
  output_meta_data = copy(prod_step_2.Outputquery)
  job2.set_meta_data(output_meta_data)
  job2.set_file_meta_data(nsb=output_meta_data['nsb']['='])

  job2.ts_task_id = '@{JOB_ID}'  # dynamic
  job2.group_size = 5   # for the input files verification
  job2.setupWorkflow(debug=False)
  job2.setType('EvnDisp3')  # mandatory *here*
  prod_step_2.Body = job2.workflow.toXML()
  prod_step_2.GroupSize = 5  # have to match the above group size?
  # return ProductionStep object
  return prod_step_2


#########################################################
if __name__ == '__main__':
  # get arguments
  tag = ''
  args = Script.getPositionalArgs()
  if len(args) < 1:
    DIRAC.gLogger.error('At least 1 argument required: DL0_data_set_name')
    DIRAC.exit(-1)
  DL0_data_set = args[0]
  if len(args) == 2:
    tag = args[1]
  prod_name = DL0_data_set.replace('AdvancedBaseline_NSB1x_', '') + '_DL1'
  if tag != '':
    prod_name += '-%s' % tag

  ##################################
  # Create the production
  DIRAC.gLogger.notice('Building new production: %s' % prod_name)
  prod_sys_client = ProductionClient()

  ##################################
  # Define the first ProductionStep (Corsika+sim_telarray)
  prod_step_1 = build_simulation_step(DL0_data_set, name_tag=tag)
  # Add the step to the production
  prod_sys_client.addProductionStep(prod_step_1)

  ##################################
  # Define EventDisplay analysis steps and add them to the production
  # dark nsb = 1
  prod_step_2 = build_evndisp_step(DL0_data_set, nsb=1, name_tag=tag)
  prod_step_2.ParentStep = prod_step_1
  prod_sys_client.addProductionStep(prod_step_2)
  # moon nsb = 5
  prod_step_3 = build_evndisp_step(DL0_data_set, nsb=5, name_tag=tag)
  prod_step_3.ParentStep = prod_step_1
  prod_sys_client.addProductionStep(prod_step_3)

  ##################################
  # Get the production description
  prod_description = prod_sys_client.prodDescription

  # Create the production
  DIRAC.gLogger.notice('Creating production.')
  res = prod_sys_client.addProduction(prod_name, json.dumps(prod_description))
  if not res['OK']:
    DIRAC.gLogger.error(res['Message'])
    DIRAC.exit(-1)

  # Start the production, i.e. instantiate the transformation steps
  res = prod_sys_client.startProduction(prod_name)

  if not res['OK']:
    DIRAC.gLogger.error(res['Message'])
    DIRAC.exit(-1)

  DIRAC.gLogger.notice('Production %s successfully created' % prod_name)
