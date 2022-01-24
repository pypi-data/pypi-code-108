import json

from deprecated import deprecated
from ase import Atoms
from clease import basis_function as bf
from .concentration import Concentration
from .settings import ClusterExpansionSettings
from .settings_bulk import CEBulk, CECrystal
from .settings_slab import CESlab

__all__ = ('settings_from_json', 'settingsFromJSON')


def settings_from_json(fname):
    """Initialize settings from JSON.

    Exists due to compatibility. You should instead use
    `ClusterExpansionSettings.load(fname)`

    Parameters:

    fname: str
        JSON file where settings are stored
    """
    return ClusterExpansionSettings.load(fname)  # pylint: disable=no-member


def old_settings_from_json(fname):
    """
    Initialise settings from JSON file.
    Used for reading old json files from versions < 0.10.2

    Parameters:

    fname: str
        JSON file where settings are stored
    """
    with open(fname, 'r') as infile:
        data = json.load(infile)

    factory = data['kwargs'].pop('factory')
    kwargs = data['kwargs']
    conc = Concentration.from_dict(kwargs['concentration'])
    kwargs['concentration'] = conc
    if factory == 'CEBulk':
        settings = CEBulk(**kwargs)
    elif factory == 'CECrystal':
        settings = CECrystal(**kwargs)
    elif factory == 'CESlab':
        cnv_cell_dict = kwargs.pop('conventional_cell')
        cnv_cell = Atoms.fromdict(cnv_cell_dict)
        kwargs['conventional_cell'] = cnv_cell
        settings = CESlab(**kwargs)
    else:
        raise ValueError(f"Unknown factory {factory}")
    settings.include_background_atoms = data['include_background_atoms']
    settings.skew_threshold = data['skew_threshold']
    bf_dict = data['basis_func_type']
    name = bf_dict.pop('name')

    if name == 'polynmial':
        settings.basis_func_type = bf.Polynomial(**bf_dict)
    elif name == 'trigonometric':
        settings.basis_func_type = bf.Trigonometric(**bf_dict)
    elif name == 'binary_linear':
        settings.basis_func_type = bf.BinaryLinear(**bf_dict)
    return settings


@deprecated(version='0.10.0', reason='You should use "settings_from_json" instead')
def settingsFromJSON(fname):
    return settings_from_json(fname)
