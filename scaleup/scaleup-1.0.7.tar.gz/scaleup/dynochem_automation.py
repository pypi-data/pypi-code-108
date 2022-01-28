#
# DynochemAuto.py
#
# Helpers routines for COM automation of Dynochem Runtime scripting
#
#
#

import pythoncom 
from win32com.client import VARIANT

from scaleup.dynochem_automation_defs import *
from scaleup.script_utils import *

# Creates a script parameters class, adding the standard params
#   targetType of 1 is Excel 
#   targetType of 2 is Reaction Lab

def create_script_parameters(name : str , file_name : str, options : str = '', dataSheets = None):

	target_type = get_run_type(file_name)

	if target_type == 0:
		raise ValueError('{} is not of a supported model type'.format(file_name))

	parameters = create_script_parameters_w32()
	parameters.Name = name
	parameters.TargetType = target_type
	parameters.ModelDetails = file_name
	parameters.Options = options
	if(dataSheets != None):
		set_datasheets(parameters, dataSheets)
	return parameters


def create_simulation_step(scenarios = [], writeProfiles : bool = False, returnProfiles : bool = False) -> pythoncom.VT_DISPATCH:
	step = create_script_step_w32("SIMULATION")
	stepParameters = create_simulation_parameters_w32()
	
	stepParameters.Scenarios = scenarios
	
	stepParameters.RunType = 1 if len(scenarios) == 0 else 3
	stepParameters.writeProfiles = writeProfiles
	stepParameters.ReturnProfiles = returnProfiles
	step.StepParameters = stepParameters
	return step

def create_fitting_step(scenarios, parameters , fitEachScenario : bool, updateToSource : bool = False ) -> pythoncom.VT_DISPATCH:
	step = create_script_step_w32("FITTING")
	stepParameters = create_fitting_parameters_w32()
	
	stepParameters.Scenarios = scenarios
	stepParameters.Parameters = parameters
	stepParameters.FitEachScenario = fitEachScenario
	stepParameters.UpdateToSource = updateToSource
	
	step.StepParameters = stepParameters
	return step
	
	
def create_verification_step(scenarios = [], verificationType : int = 1 ) -> pythoncom.VT_DISPATCH:
	step = create_script_step_w32("VERIFICATION")
	stepParameters = create_verification_parameters_w32()
	stepParameters.Scenarios = scenarios
	stepParameters.RunType = 1 if len(scenarios) == 0 else 3
	stepParameters.VerificationType = verificationType
	
	step.StepParameters = stepParameters
	return step
	
	
def create_optimization_step(scenarioName : str, factors, responses, updateToSource : bool = False) -> pythoncom.VT_DISPATCH:
	step = create_script_step_w32("OPTIMIZATION")
	stepParameters = create_optimization_parameters_w32()
	stepParameters.ScenarioName = scenarioName
	stepParameters.Factors = factors
	stepParameters.Responses = responses
	stepParameters.UpdateToSource = updateToSource
	
	step.StepParameters = stepParameters
	return step	

def set_datasheets(script, datasheets):
	datasheets_variant = VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_VARIANT, datasheets)
	script.DataSheets = datasheets_variant

#=================================================================================================
# ScriptType generated from filename
	
def run_script(file_name : str, script_name : str, steps, options : str = '', dataSheets = None):
	
	parameters = create_script_parameters(script_name, file_name, options, dataSheets)
	parameters.Steps = steps

	runner = create_model_automate_w32()
	result = runner.RunScript(file_name,
								parameters)

	return result
	

