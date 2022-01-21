"""
SDQC main file
"""
import warnings
import numpy as np
import pandas as pd

from .loading import load_data, load_config, load_from_dict
from .tools import _add_config_to_ext
from .checks_dict import checks_dict as checks


def check(source, config_file=None, output='dataframe',
          verbose=False):
    """
    Main function to run the check.

    Parameters
    ----------
    source: str or dict
        File name or dictionary to load external data from.
        If a file name is given, it must be a Vensim model file
        (.mdl) or python PySD compatible file (.py). If a dict is
        given it should be compatible with loading.load_from_dict
        function (see #TODO link to documentation).

    config_file: str (optional)
        Path to the config file.

    output: str (optional)
        Options...

    verbose: bool (optional)
        If True the output from all checks is saved. If False (default)
        only the output from not passed checks will be saved.

    Returns
    -------
    out:

    """

    if isinstance(source, str):
        # load external objects from .mdl/PySD model in Python
        exts = load_data(source)
    elif isinstance(source, dict):
        # load data from a dictionary
        exts = load_from_dict(source)
    else:
        raise ValueError("Source must be a file_name or a dictionary.")

    # load configuration
    config = load_config(config_file)

    # add config information to each external object
    _add_config_to_ext(exts, config)

    # iterate over External objects to run the checks
    out = []
    for ext in exts:
        if ext.check_config['_type'] == 'constant':
            check_constant(ext, out, verbose)
        elif ext.check_config['_type'] == 'dataseries':
            check_dataseries(ext, out, verbose)

    # TODO add report output
    if output == "dataframe":
        return pd.DataFrame(out)
    else:
        return out


def check_constant(ext, out, verbose):
    """
    Run the checks in a ExtConstant type object.

    Parameters
    ----------
    ext: pysd.external.ExtConstant
        The object to pass the check. I must have the py_short_name,
        original_name and config attributes, setted previously.
    out: list
        The list to append the results of the checks.
    verbose: bool
        If True the output from all checks is saved. If False only the
        output from not passed checks will be saved.

    Returns
    -------
    None

    """
    # TODO enable checks by dimension/subscript range

    info = {
       'py_name': ext.py_name,
       'py_short_name': ext.py_short_name,
       'original_name': ext.original_name,
       'file': ext.files,
       'sheet': ext.sheets,
       'transposed': None,
       'cell': ext.cells,
       'coords': ext.coordss
       }

    try:
        ext.initialize()
    except Exception as err:
        warnings.warn(
            err.args[0]
            + f"\n\nNot able to initialize the following object:\n{info}"
            + "\nFind error details above.\n")
        return

    if ext.coordss[0]:
        constant = ext().values
    else:
        # if constant value is 0-D (float) no test can be passed
        return

    # Start checks
    for chk in checks:
        # Is check activated and for constant?
        if 'constant' in checks[chk]['targets']\
          and ext.check_config[checks[chk]['flag']]:
            new_info = _run_check([constant], chk, ext.check_config,
                                  'constant', info, verbose)
            if new_info:
                out.append(new_info)


def check_dataseries(ext, out, verbose):
    """
    Run the checks in a ExtData or ExtLookup type object.

    Parameters
    ----------
    ext: pysd.external.ExtData or pysd.external.ExtLookup
        The object to pass the check. I must have the py_short_name,
        original_name and config attributes, setted previously.
    out: list
        The list to append the results of the checks.
    verbose: bool
        If True the output from all checks is saved. If False only the
        output from not passed checks will be saved.

    Returns
    -------
    None

    """
    # TODO enable checks by dimension/subscript range

    info = {
       'py_name': ext.py_name,
       'py_short_name': ext.py_short_name,
       'original_name': ext.original_name,
       'file': ext.files,
       'sheet': ext.sheets,
       'transposed': None,
       'cell': ext.cells,
       'coords': ext.coordss
       }

    if hasattr(ext, 'time_row_or_cols'):
        # ExtLookup
        info['x_row_or_coll'] = ext.time_row_or_cols
    else:
        # ExtData
        info['x_row_or_coll'] = ext.x_row_or_cols

    try:
        ext.initialize()
    except Exception as err:
        warnings.warn(
            err.args[0]
            + f"\n\nNot able to initialize the following object:\n{info}"
            + "\nFind error details above.\n")
        return

    data = ext.data.values
    series = ext.data.coords[ext.data.dims[0]].values

    # Always check first for missing values in the series as we need
    # to remove them before starting
    new_info = info.copy()
    new_info['check_name'] = 'missing_values_series'
    new_info['check_description'] = checks['missing_values']['descr']
    new_info['check_target'] = 'series'
    new_info['check_arg'] = {}
    new_info['check_pass'], new_info['check_out'] =\
        checks['missing_values']['func'](series)

    # Remove missing values from series
    data = data[~np.isnan(series)]
    series = series[~np.isnan(series)]
    if verbose or not new_info['check_pass']:
        out.append(new_info)

    # Start checks
    for chk in checks:
        # Is check activated?
        new_info = None
        if ext.check_config[checks[chk]['flag']]:
            if 'series' in checks[chk]['targets']:
                # Check for series
                new_info = _run_check([series], chk, ext.check_config,
                                      'series', info, verbose)
            elif 'data' in checks[chk]['targets']:
                # Check for data
                new_info = _run_check([data], chk, ext.check_config,
                                      'data', info, verbose)
            elif 'dataseries' in checks[chk]['targets']:
                # Check for data + series
                new_info = _run_check([data, series], chk, ext.check_config,
                                      'dataseries', info, verbose)
            if new_info:
                out.append(new_info)


def _run_check(args, check_name, econfig, target, info, verbose):
    """
    Run a check with the given arguments.

    Parameters
    ----------
    args: list
        List of arguments to run a check, could be data, series,
        constant or data and series.
    check_name: str
        Name of the check to be passed.
    econfig: dict
        Configuration dictionary of the object. Needed to find extra
        arguments for the function.
    target: str
        The target of the check, must match the arguments passed in args.
    info: dict
        General info for the current reading block.
    verbose: bool
        If True the output from all checks is saved. If False only the
        output from not passed checks will be saved.

    Returns
    -------
    None

    """
    # create a new dictionary to sabe
    new_info = info.copy()

    # save name, description and target
    new_info['check_name'] = check_name
    new_info['check_description'] = checks[check_name]['descr']
    new_info['check_target'] = target

    if 'args' in checks[check_name] and checks[check_name]['args']:
        # read the arguments and save the info
        new_info['check_arg'] = {
            checks[check_name]['args'][arg][1]: econfig[arg]
            for arg in checks[check_name]['args']}
    else:
        # no arguments
        new_info['check_arg'] = {}

    # run the check
    new_info['check_pass'], new_info['check_out'] =\
        checks[check_name]['func'](*args, **new_info['check_arg'])

    # save the result if the check has not passed or verbose is True
    if not new_info['check_pass'] or verbose:
        return new_info
