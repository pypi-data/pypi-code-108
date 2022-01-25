"""
Module containing the utilities to parse and properly prepare the configuration
provided by the user

The functions here are testable by calling pytest config_utilities.py
The tests can also be used as a guide on how to use the functions and
what to expect of their behaviour
"""
from pathlib import Path
import os
from copy import deepcopy
from luigi.freezing import FrozenOrderedDict
import yaml


class ConfigPatchError(Exception):
    def __init__(self, message):
        self.message = message


class ConfigFormatError(Exception):
    def __init__(self, message):
        self.message = message


def load_configuration(config_path):
    """
    load the configuration dictionary from a yaml file

    :raises: ConfigFormatError if the input cannot be parsed by the yaml
    parser
    """
    with open(config_path, 'r', encoding='utf-8') as config_file:
        try:
            return yaml.safe_load(config_file.read())
        except yaml.YAMLError as e:
            raise ConfigFormatError from e


def unfreeze(config):
    """
    unfreeze the dictionary that is frozen to serialize it
    and send it from one luigi task to another
    """
    try:
        unfrozen_dict = {}
        for key in config.keys():
            unfrozen_dict[key] = unfreeze(config[key])
        return unfrozen_dict
    except AttributeError:
        try:
            unfrozen_list = []
            if not isinstance(config, str):
                for elem in config:
                    unfrozen_list.append(unfreeze(elem))
                return unfrozen_list
            return config
        except TypeError:
            return config


def update_dict(original: dict, update: dict, offset: bool = False,
                in_place: bool = False):
    """
    update one multi level dictionary with another. If a key does not
    exist in the original, it is created. the updated dictionary is returned

    Arguments:
    original: the unaltered dictionary

    update: the dictionary that will either overwrite or extend the original

    offset: If True, the values in the update dictionary will be interpreted as
            offsets to the values in the original dict. The resulting value wil
            be original + update (this will be string concatenation if both the
            original and update values are strings

    Returns:
    updated_dict: the extended/updated dict where the values that do not appear
                  in the update dict are from the original dict, the keys that
                  do appear in the update dict overwrite/extend the values in
                  the original
    Raises:
    TypeError: If offset is set to true and the types don't match the addition
               of the values will cause a TypeError to be raised

    ConfigPatchError: If lists are updated the length of the lists needs to match
               otherwise a error is raised
    """
    if in_place is True:
        result = original
    else:
        result = dict(deepcopy(original))
    for update_key in update.keys():
        if update_key not in result.keys():
            if in_place is True:
                result[update_key] = update[update_key]
            else:
                result[update_key] = deepcopy(update[update_key])
            continue
        if not isinstance(result[update_key], type(update[update_key])):
            if in_place is True:
                result[update_key] = update[update_key]
            else:
                result[update_key] = deepcopy(update[update_key])
            continue
        if isinstance(result[update_key], dict):
            result[update_key] = update_dict(result[update_key],
                                             update[update_key],
                                             offset=offset,
                                             in_place=in_place)
        elif isinstance(result[update_key], list) or\
             isinstance(result[update_key], tuple):
            if len(result[update_key]) != len(update[update_key]):
                raise ConfigPatchError(
                    'If a list is a value of the dict the list'
                    ' lengths in the original and update need to'
                    ' match')
            patch = []
            for i, (orig_elem, update_elem) in enumerate(
                    zip(result[update_key], update[update_key])):
                if isinstance(orig_elem, dict):
                    patch.append(update_dict(result[update_key][i],
                                             update_elem,
                                             offset=offset,
                                             in_place=in_place))
                else:
                    if in_place is True:
                        patch.append(update_elem)
                    else:
                        patch.append(deepcopy(update_elem))
            if isinstance(result[update_key], tuple):
                patch = tuple(patch)
            result[update_key] = patch
        else:
            if offset is True:
                result[update_key] += update[update_key]
            else:
                if in_place is True:
                    result[update_key] = update[update_key]
                else:
                    result[update_key] = deepcopy(update[update_key])
    return result


def patch_configuration(config: dict, patch: dict):
    """
    currently only a wrapper function, if tests need to be implemented,
    then this is done here. Also the correct part of the cofiguration
    may be selected
    """
    return update_dict(config, patch)


def generate_patch(keys: list, value):
    """
    the Scan task receives a list of keys and values and needs
    to generate a patch from one of the values of the list
    and all the keys. This function does that
    """
    # this is needed to work with luigi as it turns stuffinto
    # tuples
    keys = list(keys)
    keys.reverse()
    current_root = value
    for key in keys:
        level = {}
        if isinstance(key, list) or isinstance(key, tuple):
            for subkey in key:
                level[subkey] = deepcopy(current_root)
        else:
            level[key] = current_root
        current_root = level
    return current_root


def diff_dict(d1: dict, d2: dict) -> dict:
    """
    create the diff of two dictionaries.

    Create a dictionary containing all the keys that differ between
    d1 and d2 or that exist in d2 but not in d1. The value of the
    differing key will be the value found in d2.

    Example:
        With the inputs being
        d1 = {'a': 1, 'b': {'c': 2, 'f': 4}, 'e': 3}
        d2 = {'a': 2, 'b': {'c': 3, 'f': 4}, 'e': 3, 'g': 4}

        the resulting diff will be
        diff = {'a': 2, 'b': {'c':3}, 'g': 4}

        showing that the keys 'a' and 'b:c' are different and that the
        value in the differing d2 is 2 for a and 3 for 'b:c' respectively.
        As there is an entry in d2 that is not in d1 it will appear in the
        diff, however if there is an entry in d1 that is not in d2 it will
        not appear.

    This function is intended to find the patch that where applied on d1 to
    create d2. This may provide some motivation for the way that the function
    handles the different dictionaries
    """
    diff = {}
    for key2, value2 in d2.items():
        if key2 not in d1.keys():
            diff[key2] = value2
        elif isinstance(d1[key2], dict) and isinstance(value2, dict):
            potential_diff = diff_dict(d1[key2], value2)
            if potential_diff is not None:
                diff[key2] = potential_diff
        elif value2 != d1[key2]:
            diff[key2] = value2
    if diff == {}:
        return None
    return diff


def parse_scan_config(scan_config: dict, path: str) -> tuple:
    """
    parse the different entries of the dictionary to create
    the configuration that can be passed to the higher_order_scan function

    The function returns a tuple that contains some of the information that
    needs to be passed to the scan task

    The scan configuration allows it to override the parameters of a default
    daq-system configuration with ones specified in the sever_override and
    client_override section

    Arguments:
        scan_config: Dictionary that is the configuration for a single
                     scan/measurement
        path: Path to the file that contained the scan_config dict in yaml
              format this is needed to be able to find the daq-system default
              configuration
    Returns:
        the tuple of scan parameters, scan_requirement, scan_name and
        daq_system configuration.
    """
    daq_label = scan_config['name']
    scan_config_path = Path(path)
    scan_file_dir = Path(os.path.dirname(scan_config_path))

    # check if any calibrations need to be performed before taking data
    try:
        calibration = scan_config['calibration']
    except KeyError:
        calibration = None

    # parse the daq-system configuration
    # build the path for the default config
    try:
        daq_settings = scan_config['daq_settings']
    except KeyError as err:
        raise ConfigFormatError("A daq Task must specify a 'daq_settings'"
                                " section that at least contains the "
                                "'default' key pointing"
                                " to the default system config used") from err
    try:
        default_daq_settings_path = scan_file_dir / \
            Path(daq_settings['default'])
    except KeyError as err:
        raise ConfigFormatError("A daq Task must specify a 'daq_settings'"
                                " section that at least contains the "
                                "'default' key pointing"
                                " to the default system config used") from err
    # load the default config
    try:
        daq_system_config = load_configuration(
                default_daq_settings_path.resolve())
        daq_system_default_config = daq_system_config
    except FileNotFoundError as err:
        raise ConfigFormatError(f"The path specified for the default config"
                                f"of the daq_settings in {daq_label} does"
                                " not exist") from err
    # apply the override parameters for the server and the client
    for override_prefix in ['server', 'client']:
        override_key = override_prefix+'_override'
        try:
            override_config = daq_settings[override_key]
        except KeyError:
            override_config = None
        if isinstance(override_config, dict):
            override_config = {override_prefix: override_config}
            daq_system_config = update_dict(daq_system_config,
                                            override_config)
        # if the override entry is empty then don't do anything
        elif override_config is not None:
            raise ConfigFormatError(f"The {override_key} section in the daq"
                                    f"task {daq_label} must be a yaml dict")

    # load the power on and initial config for the target
    try:
        target_config = scan_config['target_settings']
    except KeyError as err:
        raise ConfigFormatError(f"The 'target_settings' section in the daq"
                                f" task {daq_label} is missing") from err
    try:
        target_power_on_config_path = target_config['power_on_default']
    except KeyError as err:
        raise ConfigFormatError(f"The 'power_on_default' key in the daq"
                                f" task {daq_label} is missing. It should"
                                "be a path to the power on default config"
                                " of the target") from err
    try:
        pwr_on_path = scan_file_dir /\
                target_power_on_config_path
        target_power_on_config = load_configuration(pwr_on_path)
    except FileNotFoundError as err:
        raise ConfigFormatError(f"The target power on configuration for"
                                f" {daq_label} could not be found") from err
    try:
        initial_config_path = target_config['initial_config']
    except KeyError as err:
        raise ConfigFormatError(f"The 'initial_config' key in the daq"
                                f" task {daq_label} is missing. It should"
                                "be a path to the configuration of the "
                                " target at the beginning of the measure"
                                "ments") from err
    try:
        init_cfg_path = scan_file_dir / initial_config_path
        target_initial_config = load_configuration(init_cfg_path.resolve())
    except FileNotFoundError as err:
        raise ConfigFormatError(f"The initial target config of {daq_label}"
                                " could not be found") from err

    # parse the scan dimensions
    scan_parameters = []
    if 'parameters' not in scan_config.keys():
        raise ConfigFormatError("There needs to be a 'parameters' list"
                                f" in the scan entry {daq_label}")
    for scan_dimension in scan_config['parameters']:
        step = 1
        start = None
        stop = None
        if 'range' not in scan_dimension.keys():
            raise ConfigFormatError("A range must be specified"
                                    " for a scan dimension")
        for key, value in scan_dimension.items():
            if key == 'range':
                for subkey, subval in value.items():
                    if subkey == 'step':
                        step = subval
                    if subkey == 'start':
                        start = subval
                    if subkey == 'stop':
                        stop = subval
        if start is None or stop is None:
            raise ConfigFormatError(f"The Scan configuration {daq_label} is"
                                    " malformed. It misses either the start"
                                    " or stop entry for one of it's "
                                    " dimensions")
        scan_range = list(range(start, stop, step))
        scan_parameters.append((scan_dimension['key'], scan_range))
    return {'parameters': scan_parameters,
            'calibration': calibration,
            'name': daq_label,
            'type': 'daq',
            'target_power_on_default_config': target_power_on_config,
            'target_init_config': target_initial_config,
            'daq_system_config': daq_system_config,
            'daq_system_default_config': daq_system_default_config}


def parse_analysis_config(analysis_config: dict) -> tuple:
    """
    parse the analysis configuration from a dict and return it in the
    same way that the parse_scan_config

    Returns
        Tuple containing the parameters relevant to the analysis given
        by the analysis_label along with the name of the daq task that
        provides the data for the analysis
        analysis_parameters: parameters of the analysis to be performed
        daq: daq task required by the analysis
        analysis_label: name of the analysis
    """
    try:
        analysis_label = analysis_config['name']
    except KeyError as err:
        raise ConfigFormatError("The analysis configuration needs"
                                " a name field") from err
    try:
        analysis_object_name = analysis_config['python_module_name']
    except KeyError as err:
        raise ConfigFormatError("The analysis configuration needs"
                                " a python_module_name field") from err
    # parse the daq that is required for the analysis
    if 'daq' not in analysis_config.keys():
        raise ConfigFormatError("an analysis must specify a daq task")
    daq = analysis_config['daq']

    analysis_parameters = {}
    if 'parameters' in analysis_config.keys():
        if not isinstance(analysis_config['parameters'], dict):
            raise ConfigFormatError("The parameters of an analysis must be"
                                    " a dictionary")
        analysis_parameters = analysis_config['parameters']
    return {'parameters': analysis_parameters,
            'daq': daq,
            'python_module': analysis_object_name,
            'name': analysis_label,
            'type': 'analysis'}


def parse_config_entry(entry: dict, path: str):
    """
    take care of calling the right function for the different configuration
    types calls the parse_scan_config and parse_analysis_config.
    """
    ptype = entry['type']
    if ptype.lower() == 'daq':
        return parse_scan_config(entry, path)
    if ptype.lower() == 'analysis':
        return parse_analysis_config(entry)
    raise ValueError("The type of a procedure must be"
                     " either daq or analysis")


def parse_config_file(config_path: str):
    """
    Parse the root config file and return a list of workflows and
    procedures that are fully parsed so that with them the analyses
    and scan can be properly initialized
    """
    path = Path(config_path).resolve()
    if not path.exists():
        raise FileNotFoundError("The filepath %s given does not exist"%path)
    procedures = []
    workflows = []
    config = load_configuration(path)
    if isinstance(config, dict):
        if 'libraries' in config.keys():
            # resolve the path to the library files taking
            # into account that both relative and absolute
            # paths can be specified in the libraries
            # section
            lib_root_dir = Path(os.path.dirname(path))
            other_paths = config['libraries']
            for lib_path in other_paths:
                if not str(lib_path).startswith('/'):
                    resolved_lib_path = lib_root_dir / lib_path
                else:
                    resolved_lib_path = Path(lib_path).resolve()
                other_procedures, other_workflows = parse_config_file(
                        resolved_lib_path)
                for procedure in other_procedures:
                    procedures.append(procedure)
                for workflow in other_workflows:
                    workflows.append(workflow)
        if 'workflows' in config.keys():
            pass
        # The root configuration file can also specify new
        # procedures, similar to libraries
        if 'procedures' in config.keys():
            if isinstance(config['procedures'], list):
                for procedure in config['procedures']:
                    ptype = procedure['type']
                    if ptype.lower() == 'daq':
                        procedures.append(parse_scan_config(procedure, path))
                    elif ptype.lower() == 'analysis':
                        procedures.append(parse_analysis_config(procedure))
                    else:
                        raise ValueError("The type of a procedure must be"
                                         " either daq or analysis")
            else:
                raise ValueError("procedures must be a list, not a dictionary")
    elif isinstance(config, list):
        for entry in config:
            procedures.append(parse_config_entry(entry, path))
    return procedures, workflows


#### TESTS ####
def test_load_config():
    test_fpath = Path('./tests/configuration/scan_procedures.yaml')
    config = load_configuration(test_fpath)
    assert isinstance(config, list)
    assert isinstance(config[0], dict)


def test_update_dict():
    """
    test the update_dict function
    """
    test_fpath = Path('./examples/daq_procedures.yaml')
    config = load_configuration(test_fpath)
    original = config[0]
    assert 'calibration' in original
    assert original['calibration'] == 'pedestal_calibration'
    update = {'calibration': 'vref_no_inv'}
    updated_dict = update_dict(original, update)
    assert updated_dict['calibration'] == 'vref_no_inv'
    original = {'this': [{'a': 1}, {'b': 2}, {'c': 3}, 3], 'that': 'what'}
    update = {'this': [{'a': 3}, {'b': 3}, {'c': 5}, 5]}
    expected_output = {'this': [{'a': 3}, {'b': 3}, {'c': 5}, 5],
                       'that': 'what'}
    updated_dict = update_dict(original, update)
    assert updated_dict == expected_output
    original = {'this': [{'a': 1}, {'b': 2}, {'c': 3}, 3], 'that': 'what'}
    update = {}
    expected_output = {'this': [{'a': 1}, {'b': 2}, {'c': 3}, 3],
                       'that': 'what'}
    updated_dict = update_dict(original, update)
    assert updated_dict == expected_output


def test_patch_generator():
    """
    test that the generate_patch_dict_from_key_tuple function
    """
    keys = [['k1', 'k2', 'k3'], 'k4', 'k5']
    value = 1
    expected_dict = {'k1': {'k4': {'k5': 1}},
                     'k2': {'k4': {'k5': 1}},
                     'k3': {'k4': {'k5': 1}}}
    patch_dict = generate_patch(keys, value)
    assert patch_dict == expected_dict


def test_diff_dict():
    test_dict_1 = {'a': 1, 'b': {'c': 2, 'f': 4}, 'e': 3}
    test_dict_2 = {'a': 2, 'b': {'c': 3, 'f': 4}, 'e': 3, 'g': 4}
    diff = {'a': 2, 'b': {'c': 3}, 'g': 4}
    result = diff_dict(test_dict_1, test_dict_2)
    assert result == diff
    result = diff_dict(test_dict_2, test_dict_1)
    assert result['b']['c'] == 2
    assert result['a'] == 1


def test_parse_scan_config():
    test_fpath = Path('../../examples/daq_procedures.yaml')
    scan_configs = []
    test_config = load_configuration(test_fpath)
    expected_config_keys = ['parameters', 'name', 'type',
                            'target_power_on_default_config',
                            'target_init_config',
                            'daq_system_config',
                            'calibration']
    for scan in test_config:
        scan_configs.append(parse_scan_config(scan, test_fpath))
    assert len(scan_configs) == 3  # number of different scans
    test_config = scan_configs[0]
    for key in test_config.keys():
        assert key in expected_config_keys
    assert len(test_config.keys()) == len(expected_config_keys)
    assert test_config['name'] == 'injection_scan'
    assert len(test_config['parameters']) == 1
    assert test_config['parameters'][0][0][0] == 'level1_key1'


def test_analysis_config():
    test_fpath = Path('../../examples/analysis_procedures.yaml')
    config = load_configuration(test_fpath)
    parsed_config = parse_analysis_config(config[0])
    assert parsed_config['daq'] == 'pedestal_scan'
    assert isinstance(parsed_config['parameters'], dict)
    assert parsed_config['name'] == 'pedestal_calibration'
    assert parsed_config['type'] == 'analysis'
    ana_params = parsed_config['parameters']
    assert ana_params['p1'] == 346045
    assert ana_params['p2'] == 45346
    assert ana_params['p3'] == 'string option'


def test_parse_config_entry():
    scan_test_config = Path('../../examples/daq_procedures.yaml')
    daq_system_test_config = Path(
            '../../tests/configuration/defaults/daq-system-config.yaml')
    daq_reference_config = load_configuration(daq_system_test_config)
    config = load_configuration(scan_test_config)
    names = ['injection_scan', 'timewalk_scan', 'pedestal_scan']
    lengths = [1, 2, 1]
    expected_diffs = [{'server': {'NEvents': 4000}, 'client': {'hw_type': 'HD'}},
                      {'server': {'port': 7777, 'IdelayStep': 3},
                       'client': {'server_port': 7777}},
                      None]
    for entry, name, length, daq_diff in \
            zip(config, names, lengths, expected_diffs):
        parsed_config = parse_config_entry(entry, scan_test_config)
        assert parsed_config['name'] == name
        assert parsed_config['type'] == 'daq'
        assert len(parsed_config['parameters']) == length
        assert daq_diff == diff_dict(daq_reference_config,
                                    parsed_config['daq_system_config'])

def test_unfreeze():
    input_dict = FrozenOrderedDict({'a': 1, 'b': (1,2,3),
                                    'd': FrozenOrderedDict({'e': 4})})
    expected_dict = {'a': 1, 'b': [1,2,3],
                     'd': {'e': 4}}
    assert expected_dict == unfreeze(input_dict)
