# TODO - this file needs to be disected and moved into the correct place
#  a lot of functions are useless once SDK is completly migrated to to use REST

from collections import OrderedDict
from pathlib import Path
from typing import Union

import yaml

DISK_SIZE_ERROR_MSG = "Invalid disk size, should be greater than 100Gb"

SPECIAL_NAME_TO_SKIP_OBJECT_INIT = (
    '486d6d2c206120637572696f7573206465762049207365652e20436865'
    '636b6f75742068747470733a2f2f7777772e6c696e6b6564696e2e636f6'
    'd2f636f6d70616e792f677269642d61692f6a6f62732f20696620796f75'
    '206172652070617373696f6e6174652061626f7574206d616b696e67204d'
    '4c4f707320626f72696e67'
)


def check_run_name_is_valid(value: str):
    """Click callback that checks if a Run contains reserved names."""
    if value is not None:
        fail = False

        #  Check if the input is alphanumeric.
        _run_name = value.replace('-', '')
        if not _run_name.isalnum():
            fail = True

        #  Check if the allowed `-` character is not used
        #  at the end of the string.
        elif value.endswith('-') or value.startswith('-'):
            fail = True

        #  Check that the run name does not contain any
        #  uppercase characters.
        elif any(x.isupper() for x in value):
            fail = True

        if fail:
            raise ValueError(
                f"Invalid Run name: {value} the Run name must be lower case "
                "alphanumeric characters or '-', start with an alphabetic "
                "character, and end with an alphanumeric character (e.g. 'my-name', "
                " or 'abc-123')."
            )

    return value


def _aws_node_to_nickname():
    aws_node_to_nicknames = OrderedDict({
        'p3.16xlarge': '8_v100_16gb',
        'p3dn.24xlarge': '8_v100_32gb',
        'g4dn.metal': '8_t4_16gb',
        'p2.8xlarge': '8_k80_12gb',
        'p3.8xlarge': '4_v100_16gb',
        'g4dn.12xlarge': '4_t4_16gb',
        'g3.16xlarge': '4_m60_8gb',
        'g3.8xlarge': '2_m60_8gb',
        'p3.2xlarge': '1_v100_16gb',
        # 'p4d.24xlarge': '8_a100_40gb',  # currently not supported
        'g4dn.8xlarge': '1_t4_16gb',
        'g4dn.4xlarge': '1_t4_16gb',
        'g4dn.2xlarge': '1_t4_16gb',
        'g4dn.xlarge': '1_t4_16gb',
        'g4dn.16xlarge': '1_t4_16gb',
        'p2.xlarge': '1_k80_12gb',
        'g3s.xlarge': '1_m60_8gb',
        'g3.4xlarge': '1_m60_8gb',
        't2.large': '2_cpu_8gb',
        't2.medium': '2_cpu_4gb'
    })
    return aws_node_to_nicknames


def _nickname_to_aws_nodes():
    aws_node_to_nickname = _aws_node_to_nickname()
    aws_nickname_to_node = {v: k for k, v in aws_node_to_nickname.items()}
    return aws_nickname_to_node


def resolve_instance_type_nickname(value):
    """
    Enables instance type shortcuts like:
    2_cpu_4gb for t2.large
    """
    nickname = value.lower()

    aws_nickname_to_node = _nickname_to_aws_nodes()

    # validate potential options for the node name
    possible_values = list(aws_nickname_to_node.keys()) + list(aws_nickname_to_node.values())
    if nickname not in possible_values:
        possible_options = '\n'.join(list(aws_nickname_to_node.keys()))
        ValueError(f'{nickname} is not an available instance_type\n try one of these:\n{possible_options}')

    instance_type = nickname

    # if the value has _ then it's a nickname
    if '_' in nickname:
        instance_type = aws_nickname_to_node[nickname]
    return instance_type


def _get_instance_types(ctx, args, incomplete):
    # TODO: these should be retrieved from backend
    return list(_aws_node_to_nickname().keys())


def read_config(path: Union[str, Path]) -> dict:
    """
    Parameters
    ----------
    path:
        path to file on disk
    """
    if not isinstance(path, Path):
        path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f'grid config file {path} does not exist')

    #  Loads the YML file as passed by the user.
    try:
        with open(path) as f:
            grid_config = yaml.safe_load(f.read())
        if not isinstance(grid_config, dict):
            raise Exception("Unexpected file structure")
    except Exception as e:
        raise ValueError(f'Could not load your YAML config file: {e}')

    #  Adds required structure to the base YML file, if that structure isn't there.
    if 'compute' not in grid_config:
        grid_config['compute'] = {}
    if 'train' not in grid_config['compute']:
        grid_config['compute']['train'] = {}
    return grid_config


def check_description_isnt_too_long(value: str):
    """Click callback that checks if the description isn't too long."""
    if value is not None and len(value) > 200:
        raise ValueError('Description should have at most ' f'200 characters, yours has {len(value)}.')
    return value
