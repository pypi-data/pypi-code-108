"""
SDQC loading file
"""
import os
import warnings
import configparser
from ast import literal_eval
import pysd
from pysd.translation.utils import make_python_identifier, make_coord_dict

from .checks_dict import checks_dict as checks

# keep missing values of external objects
pysd.external.External.missing = "keep"


def load_data(file_name):
    """
    Loads the data.

    Parameters
    ----------
    file_name: str
        File name to load external data from. It must be a Vensim model file
        (.mdl) or python PySD compatible file (.py).

    Returns
    -------
    exts: list
        The list of the PySD External objects used in the model.

    """
    file_extension = os.path.splitext(file_name)[1]

    if file_extension == ".mdl":
        model = pysd.read_vensim(file_name, initialize=False)
    elif file_extension == ".py":
        model = pysd.load(file_name, initialize=False)
    else:
        raise ValueError(
            "Invalid file extension.\n"
            + "The file must be Python file or Vensim's mdl file"
            )

    # Add original Vensim name information to de objects
    exts = model._external_elements
    namespace = model.components._namespace
    for ext in exts:
        ext.original_name = None
        for element in namespace:
            if ext.py_name in ['_ext_data_' + namespace[element],
                               '_ext_constant_' + namespace[element],
                               '_ext_lookup_' + namespace[element],
                               namespace[element]]:
                # original name
                ext.original_name = element
                # short name
                ext.py_short_name = namespace[element]

    return exts


def load_from_dict(elements):
    """
    Loads external outpust from a elements dictionary.

    Parameters
    ----------
    elements: dict
        Dictionary of the elements. Check documentation #TODO add link

    Returns
    -------
    exts: list
        The list of PySD External objects used in the model.

    """
    namespace = {}  # namespace of external objects
    subscript_dict = {}  # subscript dictionary

    for element, data in elements.items():
        if data['type'] == 'SUBSCRIPT':
            # add subscripts to the dict
            subscript_dict[element] = data['values']
        elif data['type'] == 'EXTERNAL':
            # add external variables to the namespace
            make_python_identifier(element, namespace)

    added = {'dataseries': {}, 'constant': {}}

    for element in namespace:
        for excel in elements[element]['excel']:
            # retrieve excel information
            filename = excel.get('filename')
            sheet = excel.get('sheet')
            cell = excel.get('cell')
            # TODO errors for missing filename/sheet/cell
            root = excel.get('root')
            x_row_or_col = excel.get('x_row_or_cols')
            coords = make_coord_dict(
                excel.get('subs') or {}, subscript_dict, terse=False)

            if x_row_or_col:
                # convert series data to pysdexternal Lookup object
                if element in added['dataseries']:
                    # add table to existing object
                    added['dataseries'][element].add(
                        filename, sheet, x_row_or_col, cell, coords)
                else:
                    # create new object
                    obj = pysd.external.ExtLookup(
                        filename, sheet, x_row_or_col, cell, coords,
                        root, '_ext_lookup_' + namespace[element])
                    obj.original_name = element
                    obj.py_short_name = namespace[element]
                    added['dataseries'][element] = obj
            else:
                # convert constant data to pysdexternal Constant object
                if element in added['constant']:
                    # add table to existing object
                    added['constant'][element].add(
                        filename, sheet, cell, coords)
                else:
                    # create new object
                    obj = pysd.external.ExtConstant(
                        filename, sheet, cell, coords,
                        root, '_ext_constant_' + namespace[element])
                    obj.original_name = element
                    obj.py_short_name = namespace[element]
                    added['constant'][element] = obj

    return list(added['dataseries'].values())\
        + list(added['constant'].values())


def load_config(config_file):
    """
    Load default configuration and user configuration if any.

    Parameters
    ----------
    config_file: str
      Path to the user configuration file. If None, no file is loaded.

    Returns
    -------
    config_dict: dict
      Dictionary with the configuration retrieved from the config file

    """
    # dictionary of arguments to load from config file and they type
    config_args = {}
    for check in checks.values():
        config_args[check['flag']] = 'bool'
        if 'args' in check and check['args']:
            for arg, (type, arg_in_func) in check['args'].items():
                config_args[arg] = type

    # TODO let define groups
    # TODO enable checks by dimension/subscript range

    config = configparser.ConfigParser()
    path2lib = os.path.dirname(os.path.abspath(__file__))
    config.read(os.path.join(path2lib, 'default-conf.ini'))
    config_dict = {'all': {}, 'dataseries': {}, 'constant': {}}
    if config_file:
        if not os.path.isfile(config_file):
            raise FileNotFoundError(
                f"No such file or directory: '{config_file}'")
        # read user's config file
        config.read(config_file)
    for section in config.keys():
        sec = section.lower()
        if sec not in config_dict:
            config_dict[sec] = {}
        for key in config[section].keys():
            # convert default values to a dictionary
            if key not in config_args:
                warnings.warn(f"{key} defined in the config file is not"
                              " used in any check")
            elif config_args[key] == 'bool':
                # Boolean value (bool)
                config_dict[sec][key] = config.getboolean(section, key)
            elif config_args[key] == 'float':
                # Numeric value (float)
                config_dict[sec][key] = config.getfloat(section, key)
            elif config_args[key] == 'int':
                # Integer value (int)
                config_dict[sec][key] = config.getint(section, key)
            elif config_args[key] == 'str':
                # Type value (str)
                config_dict[sec][key] = config.get(section, key)
            elif config_args[key] == 'list (float)':
                # Range value (list)
                value = config.get(section, key)
                if value[0] == '[':
                    # literla evaluation of a list
                    config_dict[sec][key] = literal_eval(value)
                else:
                    value = [float(val) for val in value.split()]
                    if all([val.is_integer() for val in value]):
                        # if all are integers convert them to int class
                        value = [int(val) for val in value]

                    config_dict[sec][key] = value
            else:
                raise ValueError(
                    f"Invalid value type definde in checks_dict for {key}")

    return config_dict
