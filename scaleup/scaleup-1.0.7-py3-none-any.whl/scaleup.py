from scaleup.script_utils import *
from scaleup.dynochem_automation import *



def run_simulation(file_name, scenarios = [], showUi = True, altReader = True):
    options = create_script_option_string(showUi, altReader)
    step = create_simulation_step(scenarios)
    result = run_script(file_name, "Simulation Automation", [step], options)
    return result


def run_verification(file_name, scenarios = [], verificationType : int = 1, showUi = True, altReader = True):
    options = create_script_option_string(showUi, altReader)
    step = create_verification_step(scenarios, verificationType)
    result = run_script(file_name, "Verification Automation", [step], options)

    return result

def run_fitting(file_name, scenarios, parameters, fitToEach : bool = False, showUi : bool = True, altReader : bool = True, updateToSource : bool = False):

    if(updateToSource):
        xl=w32c.Dispatch("Excel.Application")
        xl.Visible = True #Update to Source requires this
        wb=xl.Workbooks.Open(file_name)
        xl.WindowState = 2

    try:

        options = create_script_option_string(showUi, altReader)
        step = create_fitting_step(scenarios, parameters, fitToEach, updateToSource)
        result = run_script(file_name, "Fitting Automation", [step], options)
    finally:
        if(updateToSource):
            wb.Close(True)
            xl.Quit()

    return result

def run_optimization(file_name : str, scenario, factors, responses, showUi : bool = True, altReader : bool = True, updateToSource : bool = False):

    if(updateToSource):
        xl=w32c.Dispatch("Excel.Application")
        xl.Visible = True #Update to Source requires this
        wb=xl.Workbooks.Open(file_name)
        xl.WindowState = 2

    try:
        options = create_script_option_string(showUi, altReader)
        step = create_optimization_step(scenario, factors, responses, updateToSource)
        result = run_script(file_name, "Optimization Automation", [step], options)
    finally:
        if(updateToSource):
            wb.Close(True)
            xl.Quit()

    return result

def run_multiple_steps(file_name : str, steps, showUi : bool = True, altReader : bool = True, updateToSource : bool = False):

    if(updateToSource):
        xl=w32c.Dispatch("Excel.Application")
        xl.Visible = True #Update to Source requires this
        wb=xl.Workbooks.Open(file_name)
        xl.WindowState = 2

    try:
        options = create_script_option_string(showUi, altReader)
        result = run_script(file_name, "Multi-step Automation", steps, options)
    finally:
        if(updateToSource):
            wb.Close(True)
            xl.Quit()

    return result
