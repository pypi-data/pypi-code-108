import os

from .PetraSimulationAdapter import PetraSimulationAdapter
from .PetraMachineAdapter import PetraMachineAdapter

import argparse


def set_service_by_env_values():
    name = os.environ.get('SERVICE_NAME')
    mode = os.environ.get('SERVICE_MODE')
    if name == None:
        raise Exception('Environment SERVICE_NAME is not set.')
    adapter = None
    if mode == 'sim':
        adapter = PetraSimulationAdapter()
    elif mode == 'prod':
        adapter = PetraMachineAdapter()
    else:
        raise Exception('Environment SERVICE_MODE have to set to "sim" or "prod".')
    return name, adapter, mode


def set_adapter_by_arg_parser():
    parser = argparse.ArgumentParser(description='Short sample app')
    parser.add_argument('--mode', help="mode can be 'prod' or 'sim'")
    options = parser.parse_args()
    adapter = None

    if options.mode == 'sim':
        adapter = PetraSimulationAdapter()
    elif options.mode == 'prod':
        adapter = PetraMachineAdapter()
    else:
        raise Exception("Argument --mode isn't set. Possible values are 'prod' for production or 'sim' for simulation")
    return adapter, options.mode
