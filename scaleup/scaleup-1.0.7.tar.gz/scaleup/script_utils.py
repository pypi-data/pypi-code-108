"""Various utilities for using with scripts

"""

import os
from enum import Enum

string_delim = '~'
opt_string_delim = '\t'
delim_escape = '&TLD;'

class OptTarget(Enum):
	Target  = 1,
	Min = 2,
	Max = 3


#=============================================================================================================
# recurrently used methods


def get_file_path(file_name : str, folder_name : str = None):
	"""Returns the path of a file relative to the current folder

	Args:
		file_name (str): the name of the file
		folder_name (str, optional): sub-folder in which the file can be found. Defaults to None.

	Returns:
		(str): full path to the file
	"""

	folder = os.getcwd()
	eff_folder = '' if folder_name == None else folder_name
	ret = os.path.join(folder, eff_folder, file_name)
	return ret


#Creates the simulation scenario escaping any tildes in the scenario name
def escape_name(scenName):
	"""
	Escapes a name containing tilde (~) characters, replacing each ~ with &TLD;  This is
	used when generating tilde delimited strings to safely send names which contains tildes.

	Args:
		scenName (str): name to be escaped

	Returns:
		str: escaped version of the input string
	"""
	ret = scenName.replace(string_delim, delim_escape)
	return ret

def create_simulation_scenario(scen_name : str, ds_name : str, values = []):
	"""Creates a simulation scenario for use with Simulation and Verification steps.

	Args:
		scen_name (str): scenario name
		ds_name (str): dataset name

	Returns:
		values ([]): parameter values for the scenario
	"""
	scen = string_delim.join([escape_name(scen_name), ds_name])
	scen = scen if len(values) == 0 else (scen + string_delim + string_delim.join(str(v) for v in values))
	return scen


# creates the option string
def create_script_option_string(showInUi : bool = True, altReader : bool = False):
	"""Generates the script option string

	Args:
		showInUi (bool, optional): Show the Automation UI when running. Defaults to True.
		altReader (bool, optional): Use the alternate file reader for Excel models (i.e. not Excel Interop). Defaults to False.

	Returns:
		Nothing
	"""
	ret = ''
	if(showInUi):
		ret += 'SHOWUI:TRUE'
		if (altReader):
			ret += '~'
	if (altReader):
			ret += 'ALTREADER:TRUE'	
	return ret



# creates a fitting parameter

def create_fitting_parameter(parameter_name : str, unit : str, initial_value, max_value, min_value, fit_to_log : bool = False):
	"""Create a fitting parameter

	Args:
		parameter_name (str): name of the parameter
		unit (str): unit of measure for the parameter
		initial_value (float): initial value
		max_value (float): minimum value
		min_value (float): maximum value
		fit_to_log (bool, optional): Fit to the log of the value. Defaults to False.

	Returns:
		parameter_string (str): formatted parameter details for use with fitting step
	"""
	ret = string_delim.join([parameter_name, unit, str(initial_value), str(max_value), str(min_value), str(fit_to_log)])
	return ret


# creates an optimization factor
def create_optimization_factor(name : str, unit : str, initial_value , min = None, max = None):
	"""Create optimization Factor

	Args:
		name (str): name of factor
		unit (str): unit of factor
		initial_value (float): initial value
		min ([type], optional): min value for factor. Defaults to half of the initial value
		max ([type], optional): max value for factor. Defaults to twice the initial value

	Returns:
		factor_string (str): formatted factor for use in optimization step
	"""
	ret = opt_string_delim.join([name, str(initial_value), unit, str(min if min != None else initial_value / 2.0 ), str(max if max != None else initial_value * 2.0)])
	return ret

# creates an optimization response
def create_min_optimization_response(name, weighting = 1.0):
	"""Creates a 'Minimize' target for a response

	Args:
		name (str): name of the response to minimize
		weighting (float, optional): Weighting for this parameter. Defaults to 1.0.

	Returns:
		response_string (str): formatted response for use in optimization step
	"""
	return create_optimization_response(name, OptTarget.Min, 0, weighting)

def create_max_optimization_response(name, weighting = 1.0):
	"""Create a 'Maximize' target for a response

	Args:
		name (str): name of the response to maximize
		weighting (float, optional): Weighting for this parameter. Defaults to 1.0.

	Returns:
		response_string (str): formatted response for use in optimization step
	"""
	return create_optimization_response(name, OptTarget.Max, 0, weighting)

def create_target_optimization_response(name, value, weighting = 1.0):
	"""Creates a 'Target' target for a response 

	Args:
		name (str): name of the response
		value (float): Target value to attempt to achieve
		weighting (float, optional): Weighting for this parameter. Defaults to 1.0.

	Returns:
		response_string (str): formatted response for use in optimization step
	"""
	return create_optimization_response(name, OptTarget.Target, value, weighting)

def create_optimization_response(name : str, target : OptTarget, value = 0, weighting = 1):
	"""Create a response for the optimization step

	Args:
		name (str): name of the response
		target (OptTarget): The goal; Max|Min|Taerget
		value (float): Target value to attempt to achieve
		weighting (float, optional): Weighting for this parameter. Defaults to 1.0.

	Returns:
		response_string (str): formatted response for use in optimization step
	"""
	ret = opt_string_delim.join([name, str(value), str(weighting), target.name])
	return ret			



# Checks the result to see if there is an error message. if there is, it displays it,
# if not, it displays the pages of results 

def write_result(result, writer = None, separator : str = ','):
	"""
	Write the contents of a script result.
	A script result contain have an error message or an array of step results.
	If it contains an error message, then this is written
	If it contains step results, each result (each of which may contain multiple pages) is written as
	lines of values separated by the passed in separator or a comma.

	If no 'writer' method is passed in, then we print to console.

	Args:
		result (COM object): Script Result from RunScript()
		writer (method, optional): Method which takes in a string. Defaults to 'print'
	"""

	if writer == None:
		writer = print

	if(result.ErrorMessage != None and len(result.ErrorMessage) > 0):
		writer(result.ErrorMessage)
	else:
		stepNumber = 1
		for stepResult in result.Results:
			writer('Step : {}\n'.format(stepNumber))
			for values in stepResult.Entries[0].Values:
				output = ''
				for row in values:
					output += separator.join(["" if v == None else str(v) for v in row]) + '\n'
				writer(output + '==\n')



def write_result_to_file(result, file_name : str, append : bool = True):
	"""
	Writes the result to a file

	Args:
		result (COM Object): Script Result
		file_name (str): name of file
		append (bool): Append the output to the file (or overwrite). Default is True (append)
	
	"""

	try:
		file_path = get_file_path(file_name)
		mode = "a" if append else "w"
		f=open(file_path, mode)
		write_result(result, f.write)
	finally:
		f.flush()
		f.close()



# Gets the RunType (1 for excel, 2 for rxm) from a filename
# returns 0 on not recognized

def get_run_type(file_name : str):
	"""
	Ascertains the run type of a file based on the extension.
	Excel models "*.xls(?)" are 1.
	Reaction Lab Models "*.rxm" are 2
	
	Not suppoted return 0

	Args:
		file_name (str): name of the file

	Returns:
		int: 0|1|2, depending on the file extension
	"""
	file_ext = os.path.splitext(file_name)[1]
	ret = 0
	if file_ext.lower().startswith('.xls'):
		ret = 1
	if file_ext.lower().startswith('.rxm'):
		ret = 2
	return ret

