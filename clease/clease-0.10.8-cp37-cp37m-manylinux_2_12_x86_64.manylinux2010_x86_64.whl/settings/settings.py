"""Definition of ClusterExpansionSettings Class.

This module defines the base-class for storing the settings for performing
Cluster Expansion in different conditions.
"""
import logging
from copy import deepcopy
from typing import List, Dict, Optional, Union, Sequence, Set, Any
from packaging.version import Version, parse

from deprecated import deprecated
import numpy as np
from ase.db import connect
from ase import Atoms

from clease.version import __version__
from clease.jsonio import jsonable
from clease.tools import wrap_and_sort_by_position
from clease.basis_function import BasisFunction
from clease.cluster import ClusterManager
from clease.basis_function import Polynomial, Trigonometric, BinaryLinear
from .concentration import Concentration
from .template_filters import ValidConcentrationFilter
from .template_atoms import TemplateAtoms
from .atoms_manager import AtomsManager

__all__ = ('ClusterExpansionSettings',)

logger = logging.getLogger(__name__)


@jsonable('ce_settings')
class ClusterExpansionSettings:
    """Base class for all Cluster Expansion settings.

    Args:
        prim (Atoms): The primitive atoms object.

        concentration (Union[Concentration, dict]): Concentration object or
            dictionary specifying the basis elements and
            concentration range of constituting species.

        size (List[int] | None, optional): Size of the supercell
            (e.g., [2, 2, 2] for 2x2x2 cell).
            ``supercell_factor`` is ignored if both ``size`` and ``supercell_factor``
            are specified. Defaults to None.

        supercell_factor (int, optional): Maximum multipilicity factor for
            limiting the size of supercell created from the primitive cell.
            ``supercell_factor`` is ignored if
            both `size` and `supercell_factor` are specified. Defaults to 27.

        db_name (str, optional): Name of the database file. Defaults to ``'clease.db'``.

        max_cluster_size (int | None, optional): Deprecated. Specifies the maximum cluster
            body size. Defaults to None. A DeprecationWarning will be raised,
            if this value is not None.

        max_cluster_dia (Sequence[float], optional): A list of int or float containing the
            maximum diameter of clusters (in Å). Defaults to ``(5., 5., 5.)``, i.e.
            a 5 Å cutoff for 2-, 3-, and 4-body clusters.

        include_background_atoms (bool, optional): Whether background elements are to
            be included. An element is considered to be a background element,
            if there is only 1 possible species which be ever be placed in a given basis.
            Defaults to False.

        basis_func_type (str, optional): Type of basis function to use. Defaults to 'polynomial'.
    """
    # pylint: disable=too-many-instance-attributes, too-many-public-methods

    # Keys which are important for saving/loading
    ARG_KEYS = ('prim_cell', 'concentration')
    KWARG_KEYS = ('size', 'supercell_factor', 'db_name', 'max_cluster_dia',
                  'include_background_atoms', 'basis_func_type')

    # Other keys we want to input back into the loaded object, but after initialization
    OTHER_KEYS = (
        'skew_threshold',
        # kwargs is a bookkeeping variable, for compatibility.
        # Just contains information about how the factory functions were called.
        'kwargs')

    def __init__(
            self,
            prim: Atoms,
            concentration: Union[Concentration, dict],
            size: Optional[List[int]] = None,
            supercell_factor: int = 27,
            db_name: str = 'clease.db',
            # max_cluster_size is only here for deprecation purposes
            # if it is not None, the user has manually specified a value
            max_cluster_size=None,
            max_cluster_dia: Sequence[float] = (5., 5., 5.),
            include_background_atoms=False,
            basis_func_type='polynomial') -> None:

        self._include_background_atoms = None
        self._cluster_mng = None
        self._trans_matrix = None
        self._cluster_list = None
        self.concentration = _get_concentration(concentration)

        self.basis_elements = deepcopy(self.concentration.basis_elements)
        self._check_first_elements()
        self.db_name = db_name
        self.size = to_3x3_matrix(size)
        self.supercell_factor = supercell_factor

        self.prim_cell = prim.copy()
        self._order_and_tag_prim_cell()
        self._store_prim_cell()

        prim_mng = AtomsManager(prim)
        prim_ind_by_basis = prim_mng.index_by_symbol([x[0] for x in self.basis_elements])
        conc_filter = ValidConcentrationFilter(concentration, prim_ind_by_basis)

        self.template_atoms = TemplateAtoms(self.prim_cell,
                                            supercell_factor=supercell_factor,
                                            size=self.size,
                                            skew_threshold=40,
                                            filters=[conc_filter])

        self.atoms_mng = AtomsManager(None)

        self.max_cluster_dia = _format_max_cluster_dia(max_cluster_dia,
                                                       max_cluster_size=max_cluster_size)

        self.set_active_template(atoms=self.template_atoms.weighted_random_template())

        self.basis_func_type = basis_func_type
        self.include_background_atoms = include_background_atoms

        if len(self.basis_elements) != self.num_basis:
            raise ValueError("list of elements is needed for each basis")

        # For storing the settings from the CLEASE factories.
        # Just for bookkeeping
        self.kwargs = {}

    @property
    def atoms(self) -> Atoms:
        return self.atoms_mng.atoms

    @property
    def max_cluster_size(self):
        return len(self.max_cluster_dia) + 1

    @property
    def all_elements(self) -> List[str]:
        return sorted([item for row in self.basis_elements for item in row])

    @property
    def num_elements(self) -> int:
        return len(self.all_elements)

    @property
    def unique_elements(self) -> List[str]:
        return sorted(list(set(deepcopy(self.all_elements))))

    @property
    def num_unique_elements(self) -> int:
        return len(self.unique_elements)

    @property
    def ref_index_trans_symm(self) -> List[int]:
        return [i[0] for i in self.index_by_sublattice]

    @property
    def skew_threshold(self):
        return self.template_atoms.skew_threshold

    @skew_threshold.setter
    def skew_threshold(self, threshold: int) -> None:
        '''
        Maximum acceptable skew level (ratio of max and min diagonal of the
        Niggli reduced cell)
        '''
        self.template_atoms.skew_threshold = threshold

    @property
    def background_indices(self) -> List[int]:
        """Get indices of the background atoms."""
        # check if any basis consists of only one element type
        basis = [i for i, b in enumerate(self.basis_elements) if len(b) == 1]

        bkg_indices = []
        for b_indx in basis:
            bkg_indices += self.index_by_basis[b_indx]
        return bkg_indices

    @property
    def cluster_mng(self):
        if self._cluster_mng is None:
            kwargs = {}
            if not self.include_background_atoms:
                kwargs['background_syms'] = self.get_bg_syms()
            self._cluster_mng = ClusterManager(self.prim_cell, **kwargs)
        return self._cluster_mng

    @property
    def include_background_atoms(self) -> bool:
        return self._include_background_atoms

    @include_background_atoms.setter
    def include_background_atoms(self, value: bool) -> None:
        if value == self._include_background_atoms:
            return
        self._include_background_atoms = value
        # We need to reset cluster manager
        self._cluster_mng = None

        self.clear_cache()
        self.basis_func_type.unique_elements = \
            self.unique_element_without_background()

    @property
    def spin_dict(self) -> Dict[str, float]:
        return self.basis_func_type.spin_dict

    @property
    def basis_functions(self):
        return self.basis_func_type.basis_functions

    @property
    def ignore_background_atoms(self) -> bool:
        return not self.include_background_atoms

    @property
    def multiplicity_factor(self) -> Dict[str, float]:
        """Return the multiplicity factor of each cluster."""
        num_sites_in_group = [len(x) for x in self.index_by_sublattice]
        return self.cluster_list.multiplicity_factors(num_sites_in_group)

    @property
    def all_cf_names(self) -> List[str]:
        num_bf = len(self.basis_functions)
        return self.cluster_list.get_all_cf_names(num_bf)

    @property
    def num_cf(self) -> int:
        """Return the number of correlation functions."""
        return len(self.all_cf_names)

    @property
    def index_by_basis(self) -> List[List[int]]:
        first_symb_in_basis = [x[0] for x in self.basis_elements]
        return self.atoms_mng.index_by_symbol(first_symb_in_basis)

    @property
    def index_by_sublattice(self) -> List[List[int]]:
        return self.atoms_mng.index_by_tag()

    @property
    def num_basis(self) -> int:
        return len(self.basis_elements)

    @property
    def basis_func_type(self):
        return self._basis_func_type

    def get_sublattice_site_ratios(self) -> np.ndarray:
        """Return the ratios of number of sites per (grouped) sublattice"""
        # Number of sites per sublattice
        sites_per_basis = np.array([len(basis) for basis in self.index_by_basis])
        num_sites = sites_per_basis.sum()
        return sites_per_basis / num_sites

    @property
    def num_active_sublattices(self) -> int:
        """Number of active sublattices"""
        return sum(self.get_active_sublattices())

    def get_active_sublattices(self) -> List[bool]:
        """List of booleans indicating if a (grouped) sublattice is active"""
        unique_no_bkg = self.unique_element_without_background()

        return [basis[0] in unique_no_bkg for basis in self.concentration.basis_elements]

    @property
    def ignored_species_and_conc(self) -> Dict[str, float]:
        """
        Return the ignored species and their concentrations normalised to the total number
        of atoms.
        """
        unique_no_bkg = self.unique_element_without_background()
        # Find the concentration within grouped sublattices
        orig_basis = self.concentration.basis_elements
        # Concentration of sites within each sublattice
        ratios = self.get_sublattice_site_ratios()
        assert len(orig_basis) == len(ratios)
        ignored = {}
        for ratio, basis in zip(ratios, orig_basis):
            elem = basis[0]
            if elem not in unique_no_bkg:
                if len(basis) != 1:
                    raise ValueError(("Ignored sublattice contains multiple elements -"
                                      "this does not make any sense"))
                if elem not in ignored:
                    ignored[elem] = ratio
                else:
                    # This element is already on one of the ignored background here we
                    # accumulate the concentration
                    ignored[elem] += ratio
        return ignored

    @property
    def atomic_concentration_ratio(self) -> float:
        """
        Ratio between true concentration (normalised to atoms) and the internal concentration used.
        For example, if one of the two basis is fully occupied, and hence ignored internally, the
        internal concentration is half of the actual atomic concentration.
        """
        ratios = self.get_sublattice_site_ratios()
        # We only want to include active sublattices
        active_sublatt = self.get_active_sublattices()
        # Add up all ratios for the active sublattices
        return ratios[active_sublatt].sum()

    @basis_func_type.setter
    def basis_func_type(self, bf_type):
        """
        Type of basis function to use.
        It should be one of "polynomial", "trigonometric" or "binary_linear"
        """
        unique_element = self.unique_element_without_background()

        if isinstance(bf_type, BasisFunction):
            if bf_type.unique_elements != sorted(unique_element):
                raise ValueError("Unique elements in BasisFunction instance "
                                 "is different from the one in settings")
            self._basis_func_type = bf_type
        elif isinstance(bf_type, str):
            if bf_type.lower() == 'polynomial':
                self._basis_func_type = Polynomial(unique_element)
            elif bf_type.lower() == 'trigonometric':
                self._basis_func_type = Trigonometric(unique_element)
            elif bf_type.lower() == "binary_linear":
                self._basis_func_type = BinaryLinear(unique_element)
            else:
                msg = f"basis function type {bf_type} is not supported."
                raise ValueError(msg)
        else:
            raise ValueError("basis_function has to be an instance of BasisFunction or a string")

    def get_bg_syms(self) -> Set[str]:
        """
        Return the symbols in the basis where there is only one element
        """
        return set(x[0] for x in self.basis_elements if len(x) == 1)

    def unique_element_without_background(self):
        """Remove background elements."""
        if self.include_background_atoms:
            bg_sym = set()
        else:
            bg_sym = self.get_bg_syms()

            # Remove bg_syms that are also present in basis with more than one
            # element
            for elems in self.basis_elements:
                if len(elems) == 1:
                    continue
                to_be_removed = set()
                for s in bg_sym:
                    if s in elems:
                        to_be_removed.add(s)

                bg_sym -= to_be_removed

        unique_elem = set()
        for x in self.basis_elements:
            unique_elem.update(x)
        return list(unique_elem - bg_sym)

    def prepare_new_active_template(self, template):
        """Prepare necessary data structures when setting new template."""
        logger.debug('Preparing new template in settings')
        self.atoms_mng.atoms = template
        self.clear_cache()

    def set_active_template(self, atoms=None):
        """Set a new template atoms object."""
        if atoms is not None:
            template = self.template_atoms.get_template_matching_atoms(atoms=atoms)
        else:
            template = self.template_atoms.weighted_random_template()

        template = wrap_and_sort_by_position(template)

        if atoms is not None:
            # Check that the positions of the generated template
            # matches the ones in the passed object
            atoms = wrap_and_sort_by_position(atoms)
            if not np.allclose(template.get_positions(), atoms.get_positions()):
                raise ValueError(f"Inconsistent positions. Passed object\n"
                                 f"{atoms.get_positions()}\nGenerated template"
                                 f"\n{template.get_positions()}")
        self.prepare_new_active_template(template)

    def _order_and_tag_prim_cell(self):
        """
        Add a tag to all the atoms in the unit cell to track the sublattice.
        Tags are added such that that the lowest tags corresponds to "active"
        sites, while the highest tags corresponds to background sites. An
        example is a system having three sublattices that can be occupied by
        more than one species, and two sublattices that can be occupied by
        only one species. The tags 0, 1, 2 will then be assigned to the three
        sublattices that can be occupied by more than one species, and the two
        remaining lattices will get the tag 3, 4.

        Re-orders the primitive cell in accordance to the order of the tags.
        """
        bg_sym = self.get_bg_syms()
        tag = 0

        # Tag non-background elements first
        for atom in self.prim_cell:
            if atom.symbol not in bg_sym:
                atom.tag = tag
                tag += 1

        # Tag background elements
        for atom in self.prim_cell:
            if atom.symbol in bg_sym:
                atom.tag = tag
                tag += 1

        # Rearange primitive cell in order of the tags.
        sorted_indx = np.argsort([atom.tag for atom in self.prim_cell])
        self.prim_cell = self.prim_cell[sorted_indx]

    def _store_prim_cell(self):
        """Store unit cell to the database. Returns the id of primitive cell in the database"""
        with connect(self.db_name) as db:
            shape = self.prim_cell.cell.cellpar()
            for row in db.select(name='primitive_cell'):
                uc_shape = row.toatoms().cell.cellpar()
                if np.allclose(shape, uc_shape):
                    return row.id

            uid = db.write(self.prim_cell, name='primitive_cell')
        return uid  # Ensure connection is closed before returning

    def _get_prim_cell(self):
        raise NotImplementedError("This function has to be implemented in in derived classes.")

    @property
    def trans_matrix(self):
        """Get the translation matrix, will be created upon request"""
        self.ensure_clusters_exist()
        return self._trans_matrix

    @property
    def cluster_list(self):
        """Get the cluster list, will be created upon request"""
        self.ensure_clusters_exist()
        return self._cluster_list

    def clear_cache(self) -> None:
        """Clear the cached objects, due to a change e.g. in the template atoms"""
        logger.debug('Clearing the cache')
        self._trans_matrix = None
        self._cluster_list = None

    def create_cluster_list_and_trans_matrix(self):
        """Prepares the internal cache objects by calculating cluster related properties"""
        logger.debug('Creating translation matrix and cluster list')
        at_cpy = self.atoms.copy()
        self.cluster_mng.build(self.max_cluster_dia)
        self._cluster_list = self.cluster_mng.info_for_template(at_cpy)
        self._trans_matrix = self.cluster_mng.translation_matrix(at_cpy)

    def view_clusters(self) -> None:
        """Display all clusters along with their names."""
        # pylint: disable=import-outside-toplevel
        from ase.gui.gui import GUI
        from ase.gui.images import Images
        figures = self.get_all_figures_as_atoms()
        images = Images()
        images.initialize(figures)
        gui = GUI(images, expr='')
        gui.show_name = True
        gui.run()

    def get_all_figures_as_atoms(self) -> List[Atoms]:
        """Get the list of all possible figures, in their
        ASE Atoms representation."""
        self.ensure_clusters_exist()
        return self.cluster_mng.get_figures()

    def ensure_clusters_exist(self) -> None:
        """Ensure the cluster list and trans matrix has been populated.
        They are not calculated upon creaton of the settings instance,
        for performance reasons. They will be constructed if required.
        Nothing is done if the cache exists."""
        if self._cluster_list is None or self._trans_matrix is None:
            logger.debug('Triggered construction of clusters')
            self.create_cluster_list_and_trans_matrix()
            # It should not be possible for them to be None after this call.
            assert self._cluster_list is not None
            assert self._trans_matrix is not None

    def get_all_templates(self):
        """
        Return a list with all template atoms
        """
        return self.template_atoms.get_all_templates()

    def view_templates(self):
        """
        Display all templates in the ASE GUi
        """
        # pylint: disable=import-outside-toplevel
        from ase.visualize import view
        view(self.get_all_templates())

    def _check_first_elements(self):
        basis_elements = self.basis_elements
        num_basis = self.num_basis
        # This condition can be relaxed in the future
        first_elements = []
        for elements in basis_elements:
            first_elements.append(elements[0])
        if len(set(first_elements)) != num_basis:
            raise ValueError("First element of different basis should not be the same.")

    def todict(self) -> Dict:
        """Return a dictionary representation of the settings class.

        Example:

            >>> from clease.settings import CEBulk, Concentration
            >>> conc = Concentration([['Au', 'Cu']])
            >>> settings = CEBulk(conc, crystalstructure='fcc', a=4.1)
            >>> dct = settings.todict()  # Get the dictionary representation
        """
        vars_to_save = self.ARG_KEYS + self.KWARG_KEYS + self.OTHER_KEYS
        dct = {'clease_version': str(__version__)}
        for key in vars_to_save:
            val = getattr(self, key)
            dct[key] = val
        return dct

    @classmethod
    def from_dict(cls, dct: Dict[str, Any]) -> 'ClusterExpansionSettings':
        """Load a new ClusterExpansionSettings class from a dictionary representation.

        Example:

            >>> from clease.settings import CEBulk, Concentration, ClusterExpansionSettings
            >>> conc = Concentration([['Au', 'Cu']])
            >>> settings = CEBulk(conc, crystalstructure='fcc', a=4.1)
            >>> dct = settings.todict()  # Get the dictionary representation
            >>> # Remove the existing settings, perhaps due to being in a new environment
            >>> del settings
            >>> # Load in the settins from the dictionary representation
            >>> settings = ClusterExpansionSettings.from_dict(dct)
        """
        dct = deepcopy(dct)
        version = dct.pop('clease_version', None)
        if version is None or parse(version) < Version('0.10.2'):
            # For backwards compatibility
            # pylint: disable=import-outside-toplevel, cyclic-import
            from .utils import old_settings_from_json
            return old_settings_from_json(dct)

        # Get the args and kwargs we expect in our function signature
        args = [dct.pop(key) for key in cls.ARG_KEYS]

        # Should we allow for missing kwargs keys?
        kwargs = {key: dct.pop(key) for key in cls.KWARG_KEYS}

        if 'max_cluster_size' in dct:
            # For compatibility, since it's no longer in KWARG_KEYS
            kwargs['max_cluster_size'] = dct.pop('max_cluster_size')

        settings = cls(*args, **kwargs)

        for key in cls.OTHER_KEYS:
            # Populate "other" keys, which aren't *args or **kwargs
            value = dct.pop(key)
            setattr(settings, key, value)

        if dct:
            # We have some unexpected left-overs
            logger.warning('Unused items from dictionary: %s', dct)
        return settings

    def clusters_table(self) -> str:
        """String with information about the clusters"""
        mult_dict = self.multiplicity_factor

        columns = ['Index', 'Cluster Name', 'Size', 'Group', 'Radius', 'Figures', 'Multiplicity']

        fmt = '| {:<5} | {:<12} | {:<4} | {:<5} | {:<6} | {:<7} | {:<12} |'
        header = fmt.format(*columns)
        rule = '-' * len(header)  # Horizontal line of -----
        lines = [rule, header, rule]

        for ii, cluster in enumerate(self.cluster_list.clusters):
            name = cluster.name
            size = f'{cluster.size:d}'.center(4, ' ')
            mult = f'{int(mult_dict[name]):d}'.center(12, ' ')
            radius = f'{cluster.diameter / 2:2.4f}'
            n_figures = f'{len(cluster.figures)}'.center(7)
            group = f'{cluster.group:d}'.center(5)
            index_s = f'{ii:d}'.center(5)

            s = fmt.format(index_s, name, size, group, radius, n_figures, mult)
            lines.append(s)

        lines.append(rule)

        return '\n'.join(lines)


def to_3x3_matrix(size):
    if size is None:
        return None
    if isinstance(size, np.ndarray):
        size = size.tolist()

    # Is already a matrix
    if np.array(size).shape == (3, 3):
        return size

    if np.array(size).shape == (3,):
        return np.diag(size).tolist()

    raise ValueError(f"Cannot convert passed array {size} to 3x3 matrix")


def _get_concentration(concentration: Union[Concentration, dict]) -> Concentration:
    """Helper function to format the concentration"""
    if isinstance(concentration, Concentration):
        conc = concentration
    elif isinstance(concentration, dict):
        conc = Concentration.from_dict(concentration)
    else:
        raise TypeError("concentration has to be either dict or instance of Concentration")
    return conc


def _format_max_cluster_dia(max_cluster_dia, max_cluster_size=None):
    """Formatter of max_cluster_dia."""
    if max_cluster_size is None and not isinstance(max_cluster_dia, (int, float)):
        # Assume max_cluster_dia is sequence[float], and user didn't specify any
        # (now deprecated) max_cluster sizes.
        return np.array(max_cluster_dia)
    return _old_format_max_cluster_dia(max_cluster_dia, max_cluster_size)


def _old_format_max_cluster_dia(max_cluster_dia, max_cluster_size):

    # User specified an old version of MCS and MCD
    dep_msg = f"""
    max_cluser_size should no longer be specfied explicitly,
    and max_cluster_dia should no longer be an int or float.

    Specify cluster sizes with max_cluster_dia as an array-like instead.
    Got max_cluster_size '{max_cluster_size}' and max_cluster_dia '{max_cluster_dia}'.
    Try instead to use max_cluster_dia as an array, e.g. max_cluster_dia=[5., 5., 5.]
    for 2-, 3- and 4-body clusters of cutoff 5 Å.
    """

    @deprecated(version='0.10.6', reason=dep_msg)
    def _formatter():
        # max_cluster_dia is list or array
        if isinstance(max_cluster_dia, (list, np.ndarray, tuple)):
            # Length should be either max_cluster_size+1 or max_cluster_size-1
            mcd = np.array(max_cluster_dia, dtype=float)
            if len(max_cluster_dia) == max_cluster_size + 1:
                # Remove the first two entries, assume they are 0- and 1-body diameters
                mcd = mcd[2:]
            elif len(max_cluster_dia) == max_cluster_size - 1:
                # Assume max_cluster_dia contains 2+ body clusters
                pass
            else:
                raise ValueError("Invalid length for max_cluster_dia.")
        elif isinstance(max_cluster_dia, (int, float)):
            if max_cluster_size is None:
                raise ValueError('Received no max_cluster_size, but a float for max_cluster_dia')
            mcd = np.ones(max_cluster_size - 1, dtype=float) * max_cluster_dia
        # Case for *None* or something else
        else:
            raise TypeError(f"max_cluster_dia is of wrong type, got: {type(max_cluster_dia)}")
        return mcd.round(decimals=3)

    return _formatter()
