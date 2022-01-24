# Built-in Modules
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional

# Third Party Modules
import boto3

# Project Specific Modules
from pf_dre_core.utils.loader import load_data

logger = logging.getLogger(__name__)

STATIC_PATH = Path(os.getcwd()).joinpath('static')


def get_secrets(system_name: str, parameter_names: List[str],
                ignore_local: Optional[bool] = False) -> Dict:
    """
    Get a list of parameters from AWS Systems Manager's Parameter Store.
    This function will query Parameter Store for the given names, and return
    their values.

    If there is a file called `local-ssm-values.json` in the project root, then
    it will load the values from here instead of calling AWS, so that the values
    can be easily set and changed during local development.
    :param system_name: The name of the system, project or application we are
    part of. This is used as a prefix to the Parameter Store keys, so all the
    values appear as if they are inside a folder with the name of the system.
    :param parameter_names: An array of the names of the keys to retrieve.
    :return:
    """
    full_param_names = [f"/{system_name}/{p}" for p in parameter_names]
    params_path = STATIC_PATH.joinpath('local-ssm-values.json')
    local_file_content = load_data(params_path)

    params = {}

    for p in full_param_names:
        if not ignore_local and local_file_content and p in local_file_content:
            logger.debug(f"Getting secret [{p}] from local static file.")
            params[p.rsplit('/', 1)[1]] = local_file_content[p]
        else:
            params[p.rsplit('/', 1)[1]] = None

    missing_params = [p for p, v in params.items() if v is None]
    if missing_params:
        full_param_names = [f"/{system_name}/{p}" for p in missing_params]
        logger.debug(f"Getting secrets {full_param_names} from AWS Param store")
        ssm = boto3.client('ssm')
        response = ssm.get_parameters(Names=full_param_names)
        for p in response['Parameters']:
            name = p['Name'].rsplit('/', 1)[1]
            logger.debug("AWS Param {} is in params dict {}"
                         .format(name, name in params))
            params[name] = p['Value']

    return params
