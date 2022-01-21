
import json
import os
import tempfile
import fibre.libfibre
import odrive
from odrive.utils import OperationAbortedException, yes_no_prompt

def _property_paths(prefix, obj):
    for k in dir(obj):
        v = getattr(obj, k)
        if k.startswith('_') and k.endswith('_property'):
            yield '.'.join(prefix + [k[1:-9]]), v
        elif not k.startswith('_') and isinstance(v, fibre.libfibre.RemoteObject):
            yield from _property_paths(prefix + [k], v)

def _get_dict(obj, is_config_object, prop_dict):
    result = {}

    for k in dir(obj):
        v = getattr(obj, k)
        if k.startswith('_') and k.endswith('_property') and is_config_object:
            v = v.read()
            if isinstance(v, fibre.libfibre.RemoteObject):
                v = prop_dict[v]
                print("path:", v)
            result[k[1:-9]] = v
        elif not k.startswith('_') and isinstance(v, fibre.libfibre.RemoteObject):
            sub_dict = _get_dict(v, (k == 'config') or is_config_object, prop_dict)
            if sub_dict != {}:
                result[k] = sub_dict

    return result

def _set_dict(obj, path, config_dict, prop_dict):
    errors = []
    for (k,v) in config_dict.items():
        name = ".".join(path + [k])
        if not k in dir(obj):
            errors.append("Could not restore {}: property not found on device".format(name))
            continue
        if isinstance(v, dict):
            errors += _set_dict(getattr(obj, k), path + [k], v, prop_dict)
        else:
            try:
                remote_attribute = getattr(obj, '_' + k + '_property')
                if isinstance(v, str) and hasattr(type(remote_attribute), 'exchange') and type(remote_attribute).exchange._inputs[1][1] == 'object_ref':
                    v = prop_dict[v]
                remote_attribute.exchange(v)
            except Exception as ex:
                errors.append("Could not restore {}: {}".format(name, str(ex)))
    return errors

def get_temp_config_filename(device):
    serial_number = odrive.get_serial_number_str_sync(device)
    safe_serial_number = ''.join(filter(str.isalnum, serial_number))
    return os.path.join(tempfile.gettempdir(), 'odrive-config-{}.json'.format(safe_serial_number))

def backup_config(device, filename, logger):
    """
    Exports the configuration of an ODrive to a JSON file.
    If no file name is provided, the file is placed into a
    temporary directory.
    """

    if filename is None:
        filename = get_temp_config_filename(device)

    logger.info("Saving configuration to {}...".format(filename))

    if os.path.exists(filename):
        if not yes_no_prompt("The file {} already exists. Do you want to override it?".format(filename), True):
            raise OperationAbortedException()

    prop_dict = list(_property_paths([], device))
    print([k for k, v in prop_dict])
    data = _get_dict(device, False, {v: k for k, v in prop_dict})
    with open(filename, 'w') as file:
        json.dump(data, file)
    logger.info("Configuration saved.")

def restore_config(device, filename, logger):
    """
    Restores the configuration stored in a file 
    """

    if filename is None:
        filename = get_temp_config_filename(device)

    with open(filename) as file:
        data = json.load(file)

    logger.info("Restoring configuration from {}...".format(filename))
    prop_dict = list(_property_paths([], device))
    errors = _set_dict(device, [], data, {k: v for k, v in prop_dict})

    for error in errors:
        logger.info(error)
    if errors:
        logger.warn("Some of the configuration could not be restored.")
    
    try:
        device.save_configuration()
    except fibre.libfibre.ObjectLostError:
        pass # Saving configuration makes the device reboot
    logger.info("Configuration restored.")
