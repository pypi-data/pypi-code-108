# Following requirements are needed:
# 1) Install pylint from pip
# 2) Install graphviz (https://graphviz.org/)
#       Important: Add graphviz to PATH variable!
#       First time you run graphviz you need to run 'dot -c' as admin!
#       Maybe you have to restart your PC in between.
# Within pylint the tool pyreverse exist. For any help call 'pyreverse -h'.
# With pyreverse you are able to generate graphs from your code.
import os
from os.path import basename, dirname
from subprocess import check_call

from simses import main
from simses.analysis.evaluation.economic.revenue_stream import abstract_revenue_stream
from simses.analysis.evaluation.technical import technical_evaluation
from simses.commons import config, state
from simses.commons.state import parameters
from simses.logic.energy_management.strategy import operation_strategy, operation_priority
from simses.system.auxiliary import auxiliary
from simses.system.auxiliary.heating_ventilation_air_conditioning import fix_cop_hvac_pid_control
from simses.system.housing import abstract_housing
from simses.system.power_electronics.acdc_converter import abstract_acdc_converter
from simses.system.power_electronics.dcdc_converter import abstract_dcdc_converter
from simses.system.test import test_fix_cop_hvac, test_acdc_converter, test_location_ambient_temperature, \
    test_constant_ambient_temperature
from simses.system.thermal.ambient import ambient_thermal_model
from simses.system.thermal.model import system_thermal_model
from simses.technology.lithium_ion.cell import type
from simses.technology.lithium_ion.degradation import degradation_model
from simses.technology.lithium_ion.test import test_cell_type


class Filter:
    PUB_ONLY: str = 'PUB_ONLY'
    ALL: str = 'ALL'
    SPECIAL: str = 'SPECIAL'
    OTHER: str = 'OTHER'


class Output:
    PDF: str = 'pdf'
    PNG: str = 'png'
    DOT: str = 'dot'


def is_output(file: str) -> bool:
    return file.endswith(Output.PDF) or \
           file.endswith(Output.PNG) or \
           file.endswith(Output.DOT)


def create_ignore_list() -> str:
    ignore: [str] = list()
    ignore.append(test_acdc_converter)
    ignore.append(operation_priority)
    ignore.append(test_cell_type)
    ignore.append(parameters)
    ignore.append(test_constant_ambient_temperature)
    ignore.append(test_location_ambient_temperature)
    ignore.append(test_fix_cop_hvac)
    ignore.append(fix_cop_hvac_pid_control)
    res: str = ''
    for module in ignore:
        res += basename(module.__file__) + ','
    return res


def create_call_for(package: str, ignore: str, cls: str = None) -> [str]:
    call: [str] = list()
    call.append('pyreverse')
    call.append('-o' + Output.PDF)
    call.append('-f' + Filter.PUB_ONLY)
    call.append('-mn')  # do not use module name for classes, my for yes
    call.append('-k')  # show only classnames
    call.append('--ignore=' + ignore)  # files not to be parsed
    if cls is not None:
        call.append('-c' + cls)  # create a class diagram
        # call.append('-s 1')  # depth of associated classes
        # call.append('-a 1')  # depth of ancestors
    call.append('-p' + basename(package))  # name output of basename from package
    call.append(package)
    return call


def create_graph_for(file: str, ignore: str, cls: str = None) -> None:
    print('Creating graph for ' + file)
    call: [str] = create_call_for(file, ignore, cls)
    check_call(call, cwd=dirname(__file__))


def remove_all_graphs() -> None:
    print('Removing old graphs...')
    directory: str = dirname(__file__)
    for item in os.listdir(directory):
        file = os.path.join(directory, item)
        if os.path.isfile(file) and is_output(file):
            os.remove(file)


packages: [str] = list()
packages.append(abstract_dcdc_converter)
packages.append(abstract_acdc_converter)
packages.append(ambient_thermal_model)
packages.append(operation_strategy)
packages.append(type)
packages.append(config)
packages.append(state)
packages.append(abstract_revenue_stream)
packages.append(technical_evaluation)
packages.append(auxiliary)
packages.append(system_thermal_model)
packages.append(degradation_model)
packages.append(abstract_housing)
packages.append(main)

modules: dict = dict()
# modules.update({degradation_model: DegradationModel})

remove_all_graphs()

ignore: str = create_ignore_list()

for package in packages:
    create_graph_for(dirname(package.__file__), ignore)

for module, cls in modules.items():
    create_graph_for(module.__file__, ignore, cls.__name__)

# Conversion from dot files to pdf
# from graphviz import render
# render(Output.DOT, Output.PDF, 'classes.dot')
# render(Output.DOT, Output.PDF, 'packages.dot')
