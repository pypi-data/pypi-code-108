"""
SDQC tools file
"""
from pysd import external as pysdexternal


def _add_config_to_ext(exts, config):
    """
    Add config information to each External object.

    Parameters
    ----------
    exts: list
        The list of pysd.external.External objects used in the model.

    Returns
    -------
    None

    """
    for ext in exts:
        # TODO enable checks by dimension/subscript range
        # Include parameters for All
        extconfig = config['all'].copy()

        # Check if the object is Constant or Data and include specific params
        if isinstance(ext, pysdexternal.ExtConstant):
            extconfig.update(config['constant'])
            extconfig['_type'] = 'constant'
        elif isinstance(ext, (pysdexternal.ExtData, pysdexternal.ExtLookup)):
            extconfig.update(config['dataseries'])
            extconfig['_type'] = 'dataseries'

        # TODO add group option with level between object name and type

        # Find if the object is in the dictionary
        if ext.original_name.lower() in config:
            extconfig.update(config[ext.original_name.lower()])
        elif ext.py_name.lower() in config:
            extconfig.update(config[ext.py_name.lower()])
        elif ext.py_short_name.lower() in config:
            extconfig.update(config[ext.py_short_name.lower()])

        # set the attribute
        ext.check_config = extconfig
