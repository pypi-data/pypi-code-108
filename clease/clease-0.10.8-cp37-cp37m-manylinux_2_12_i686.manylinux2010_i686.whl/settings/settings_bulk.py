"""Definitions of Cluster Expansion settings for bulk.

Cluster Expansion can be peformed on bulk material using either CEBulk
or CECrystal class.
"""
from copy import deepcopy

from ase.build import bulk
from ase.spacegroup import crystal
from clease.tools import wrap_and_sort_by_position
from .concentration import Concentration
from .settings import ClusterExpansionSettings

__all__ = (
    'CEBulk',
    'CECrystal',
)


def CEBulk(concentration: Concentration,
           crystalstructure='sc',
           a=None,
           c=None,
           covera=None,
           u=None,
           **kwargs):
    """
    Specify cluster expansion settings for bulk materials defined based on
    crystal structures.

    Parameters:

        concentration (Union[Concentration, dict]):
            Concentration object or dictionary specifying the basis elements and
            concentration range of constituting species

        crystalstructure (str):
            Must be one of sc, fcc, bcc, hcp, diamond, zincblende, rocksalt,
            cesiumchloride, fluorite or wurtzite.

        a (float):
            Lattice constant.

        c (float):
            Lattice constant.

        covera (float):
            c/a ratio used for hcp.  Default is ideal ratio: sqrt(8/3).

        u (float):
            Internal coordinate for Wurtzite structure.

    For more kwargs, see docstring of :class:`clease.settings.ClusterExpansionSettings`.
    """
    structures = {
        'sc': 1,
        'fcc': 1,
        'bcc': 1,
        'hcp': 1,
        'diamond': 1,
        'zincblende': 2,
        'rocksalt': 2,
        'cesiumchloride': 2,
        'fluorite': 3,
        'wurtzite': 2
    }

    num_basis = len(concentration.orig_basis_elements)
    if num_basis != structures[crystalstructure]:
        msg = f"{crystalstructure} has {structures[crystalstructure]} basis. "
        msg += "The number of basis specified by basis_elements is "
        msg += f"{num_basis}"
        raise ValueError(msg)

    basis_elements = concentration.orig_basis_elements
    name = ''.join(x[0] for x in basis_elements)
    prim = bulk(name=name, crystalstructure=crystalstructure, a=a, c=c, covera=covera, u=u)
    prim = wrap_and_sort_by_position(prim)

    settings = ClusterExpansionSettings(prim, concentration, **kwargs)

    settings.kwargs.update({
        'crystalstructure': crystalstructure,
        'a': a,
        'c': c,
        'covera': covera,
        'u': u,
        'factory': 'CEBulk'
    })
    return settings


def CECrystal(concentration: Concentration,
              spacegroup=1,
              basis=None,
              cell=None,
              cellpar=None,
              ab_normal=(0, 0, 1),
              crystal_kwargs=None,
              **kwargs):
    """Store CE settings on bulk materials defined based on space group.

    Parameters:

        concentration (Union[Concentration, dict]):
            Concentration object or dictionary specifying the basis elements and
            concentration range of constituting species

        spacegroup (int | string | Spacegroup instance):
            Space group given either as its number in International Tables
            or as its Hermann-Mauguin symbol.

        basis (List[float]):
            List of scaled coordinates.
            Positions of the unique sites corresponding to symbols given
            either as scaled positions or through an atoms instance.

        cell (3x3 matrix):
            Unit cell vectors.

        cellpar ([a, b, c, alpha, beta, gamma]):
            Cell parameters with angles in degree. Is not used when `cell`
            is given.

        ab_normal (vector):
            Is used to define the orientation of the unit cell relative
            to the Cartesian system when `cell` is not given. It is the
            normal vector of the plane spanned by a and b.

        crystal_kwargs (dict | None):
            Extra kwargs to be passed into the ase.spacegroup.crystal
            function. Nothing additional is added if None.
            Defaults to None.

    For more kwargs, see docstring of :class:`clease.settings.ClusterExpansionSettings`.
    """

    symbols = []
    num_basis = len(concentration.orig_basis_elements)
    for x in range(num_basis):
        symbols.append(concentration.orig_basis_elements[x][0])

    crystal_kwargs = crystal_kwargs or {}
    prim = crystal(symbols=symbols,
                   basis=basis,
                   spacegroup=spacegroup,
                   cell=cell,
                   cellpar=cellpar,
                   ab_normal=ab_normal,
                   size=[1, 1, 1],
                   primitive_cell=True,
                   **crystal_kwargs)
    prim = wrap_and_sort_by_position(prim)

    settings = ClusterExpansionSettings(prim, concentration, **kwargs)
    settings.kwargs.update({
        'basis': deepcopy(basis),
        'spacegroup': spacegroup,
        'cell': cell,
        'cellpar': cellpar,
        'ab_normal': ab_normal,
        'factory': 'CECrystal'
    })
    return settings
