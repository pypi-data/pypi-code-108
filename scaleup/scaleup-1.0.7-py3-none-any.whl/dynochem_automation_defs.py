import win32com.client as w32c

#==================================================================================================

def create_model_automate_w32():
	automate = w32c.Dispatch("ModelAutomation.ModelAutomate")
	return automate

def create_script_parameters_w32():
	parameters = w32c.Dispatch("ModelAutomation.ScriptParameters")
	return parameters
	
def create_script_step_w32(stepType : str):
	step = w32c.Dispatch("ModelAutomation.ScriptStep")
	step.StepType = stepType
	return step
	
def create_simulation_parameters_w32():
	stepParams = w32c.Dispatch("ModelAutomation.SimulationAutomationParameters")
	return stepParams
	
def create_verification_parameters_w32():
	stepParams = w32c.Dispatch("ModelAutomation.VerificationAutomationParameters")
	return stepParams	
	
def create_fitting_parameters_w32():
	stepParams = w32c.Dispatch("ModelAutomation.FittingAutomationParameters")
	return stepParams	

def create_optimization_parameters_w32():
	stepParams = w32c.Dispatch("ModelAutomation.OptimizationAutomationParameters")
	return stepParams	
