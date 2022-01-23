from ..settings import (adsorbate_elements, site_heights,  
                        adsorbate_list, adsorbate_molecule)
from ..adsorption_sites import enumerate_adsorption_sites 
from ..adsorbate_coverage import (ClusterAdsorbateCoverage, 
                                  SlabAdsorbateCoverage)
from ..utilities import (is_list_or_tuple, 
                         get_close_atoms, 
                         get_rodrigues_rotation_matrix,
                         get_angle_between, 
                         get_rejection_between)
from ..labels import (get_cluster_signature_from_label, 
                      get_slab_signature_from_label)
from ase.data import atomic_numbers
from ase.formula import Formula
from ase import Atoms, Atom
import numpy as np
import warnings
import re


def add_adsorbate(atoms, adsorbate, site=None, surface=None, 
                  morphology=None, indices=None, height=None, 
                  composition=None, orientation=None, 
                  tilt_angle=0., subsurf_element=None, 
                  all_sites=None, **kwargs):
    """A general function for adding one adsorbate to the surface.
    Note that this function adds one adsorbate to a random site
    that meets the specified condition regardless of it is already 
    occupied or not. The function is generalized for both periodic 
    and non-periodic systems (distinguished by atoms.pbc).

    Parameters
    ----------
    atoms : ase.Atoms object
        Accept any ase.Atoms object. No need to be built-in.

    adsorbate : str or ase.Atom object or ase.Atoms object
        The adsorbate species to be added onto the surface.

    site : str, default None
        The site type that the adsorbate should be added to.

    surface : str, default None
        The surface type (crystal structure + Miller indices)
        If the structure is a periodic surface slab, this is required.
        If the structure is a nanoparticle, the function enumerates
        only the sites on the specified surface.

    morphology : str, default None
        The morphology type that the adsorbate should be added to. 
        Only available for surface slabs.

    indices : list or tuple
        The indices of the atoms that contribute to the site that
        you want to add adsorbate to. This has the highest priority.

    height : float, default None
        The height of the added adsorbate from the surface.
        Use the default settings if not specified.

    composition : str, default None
        The elemental of the site that should be added to.

    orientation : list or numpy.array, default None
        The vector that the multidentate adsorbate is aligned to.

    tilt_angle: float, default 0.
        Tilt the adsorbate with an angle (in degress) relative to
        the surface normal.

    subsurf_element : str, default None
        The subsurface element of the hcp or 4fold hollow site that 
        should be added to.

    all_sites : list of dicts, default None
        The list of all sites. Provide this to make the function
        much faster. Useful when the function is called many times.

    """
    
    composition_effect = any(v is not None for v in 
                             [composition, subsurf_element])

    if composition:
        if '-' in composition or len(list(Formula(composition))) == 6:
            scomp = composition
        else:
            comp = re.findall('[A-Z][^A-Z]*', composition)
            if len(comp) != 4:
                scomp = ''.join(sorted(comp, key=lambda x: 
                                       atomic_numbers[x]))
            else:
                if comp[0] != comp[2]:
                    scomp = ''.join(sorted(comp, key=lambda x: 
                                           atomic_numbers[x]))
                else:
                    if atomic_numbers[comp[0]] > atomic_numbers[comp[1]]:
                        scomp = comp[1]+comp[0]+comp[3]+comp[2]
                    else:
                        scomp = ''.join(comp)
    else:
        scomp = None

    if all_sites is None:
        all_sites = enumerate_adsorption_sites(atoms, surface, morphology, 
                        composition_effect=composition_effect, **kwargs)

    if indices is not None:
        indices = indices if is_list_or_tuple(indices) else [indices]
        indices = tuple(sorted(indices))
        st = next((s for s in all_sites if 
                   s['indices'] == indices), None)
    
    elif subsurf_element is None:
        st = next((s for s in all_sites if 
                   s['site'] == site and
                   s['composition'] == scomp), None)
    else:
        st = next((s for s in all_sites if
                   s['site'] == site and
                   s['composition'] == scomp and
                   s['subsurf_element']
                   == subsurf_element), None)

    if not st:
        print('No such site can be found')            
    else:
        if height is None:
            height = site_heights[st['site']]
        add_adsorbate_to_site(atoms, adsorbate, st, height, 
                              orientation, tilt_angle)


def add_adsorbate_to_site(atoms, adsorbate, site, height=None, 
                          orientation=None, tilt_angle=0.):            
    """The base function for adding one adsorbate to a site.
    Site must include information of 'normal' and 'position'.
    Useful for adding adsorbate to multiple sites or adding 
    multidentate adsorbates.

    Parameters
    ----------
    atoms : ase.Atoms object
        Accept any ase.Atoms object. No need to be built-in.

    adsorbate : str or ase.Atom object or ase.Atoms object
        The adsorbate species to be added onto the surface.

    site : dict 
        The site that the adsorbate should be added to.
        Must contain information of the position and the
        normal vector of the site.

    height : float, default None
        The height of the added adsorbate from the surface.
        Use the default settings if not specified.

    orientation : list or numpy.array, default None
        The vector that the multidentate adsorbate is aligned to.

    tilt_angle: float, default None
        Tilt the adsorbate with an angle (in degress) relative to
        the surface normal.

    """
 
    if height is None:
        height = site_heights[site['site']]

    # Make the correct position
    normal = site['normal']
    pos = site['position'] + normal * height

    # Convert the adsorbate to an Atoms object
    if isinstance(adsorbate, Atoms):
        ads = adsorbate
    elif isinstance(adsorbate, Atom):
        ads = Atoms([adsorbate])

    # Or assume it is a string representing a molecule
    else:
        ads = adsorbate_molecule(adsorbate)
        if not ads:
            print('Nothing is added.')
            return 

    bondpos = ads[0].position
    ads.translate(-bondpos)
    z = -1. if adsorbate in ['CH','NH','OH','SH'] else 1.
    ads.rotate(np.asarray([0., 0., z]) - bondpos, normal)
    if tilt_angle > 0.:
        pvec = np.cross(np.random.rand(3) - ads[0].position, normal)
        ads.rotate(tilt_angle, pvec, center=ads[0].position)

    if adsorbate not in adsorbate_list:
        # Always sort the indices the same order as the input symbol.
        # This is a naive sorting which might cause H in wrong order.
        # Please sort your own adsorbate atoms by reindexing as has
        # been done in the adsorbate_molecule function in acat.settings.
        symout = list(Formula(adsorbate))
        symin = list(ads.symbols)
        newids = []
        for elt in symout:
            idx = symin.index(elt)
            newids.append(idx)
            symin[idx] = None
        ads = ads[newids]

    if orientation is not None:
        orientation = np.asarray(orientation)
        oripos = next((a.position for a in ads[1:] if 
                       a.symbol != 'H'), ads[1].position)

        v1 = get_rejection_between(oripos - bondpos, normal)
        v2 = get_rejection_between(orientation, normal)
        theta = get_angle_between(v1, v2)

        # Flip the sign of the angle if the result is not the closest
        rm_p = get_rodrigues_rotation_matrix(axis=normal, angle=theta)
        rm_n = get_rodrigues_rotation_matrix(axis=normal, angle=-theta)        
        npos_p, npos_n = rm_p @ oripos, rm_n @ oripos
        nbpos_p = npos_p + pos - bondpos
        nbpos_n = npos_n + pos - bondpos
        d_p = np.linalg.norm(nbpos_p - pos - orientation)
        d_n = np.linalg.norm(nbpos_n - pos - orientation)
        if d_p <= d_n:
            for a in ads:
                a.position = rm_p @ a.position
        else:
            for a in ads:
                a.position = rm_n @ a.position

    ads.translate(pos - bondpos)
    atoms += ads


def add_adsorbate_to_label(atoms, adsorbate, label, 
                           surface=None, height=None,
                           orientation=None, 
                           tilt_angle=0.,
                           composition_effect=False,
                           all_sites=None, **kwargs):
    """Same as add_adsorbate function, except that the site type is 
    represented by a numerical label. The function is generalized for 
    both periodic and non-periodic systems (distinguished by atoms.pbc).

    Parameters
    ----------
    atoms : ase.Atoms object
        Accept any ase.Atoms object. No need to be built-in.

    adsorbate : str or ase.Atom object or ase.Atoms object
        The adsorbate species to be added onto the surface.

    label : int or str
        The label of the site that the adsorbate should be added to.

    surface : str, default None
        The surface type (crystal structure + Miller indices)
        If the structure is a periodic surface slab, this is required.
        If the structure is a nanoparticle, the function enumerates
        only the sites on the specified surface.

    height : float, default None
        The height of the added adsorbate from the surface.
        Use the default settings if not specified.

    orientation : list or numpy.array, default None
        The vector that the multidentate adsorbate is aligned to.

    tilt_angle: float, default 0.
        Tilt the adsorbate with an angle (in degress) relative to
        the surface normal.

    composition_effect : bool, default False
        Whether the label is defined in bimetallic labels or not.

    all_sites : list of dicts, default None
        The list of all sites. Provide this to make the function
        much faster. Useful when the function is called many times.

    """

    if composition_effect:
        slab = atoms[[a.index for a in atoms if a.symbol
                      not in adsorbate_elements]]
        metals = sorted(list(set(slab.symbols)),
                        key=lambda x: atomic_numbers[x])
        assert len(metals) in [1, 2], \
        'only support labelling of monometallics and bimetallics'
    else:
        metals = None

    if True in atoms.pbc:
        signature = get_slab_signature_from_label(label, surface,
                                                  composition_effect,
                                                  metals)
    else:
        signature = get_cluster_signature_from_label(label,
                                                     composition_effect,
                                                     metals)
    sigs = signature.split('|')
    morphology, composition = None, None
    if not composition_effect:
        if True in atoms.pbc:
            site, morphology = sigs[0], sigs[1]
        else:
            site, surface = sigs[0], sigs[1]
    else:
        if True in atoms.pbc:
            site, morphology, composition = sigs[0], sigs[1], sigs[2]
        else:
            site, surface, composition = sigs[0], sigs[1], sigs[2]

    add_adsorbate(atoms, adsorbate, site, surface, 
                  morphology, height=height,
                  composition=composition, 
                  orientation=orientation, 
                  all_sites=all_sites, **kwargs)


def remove_adsorbate_from_site(atoms, site, remove_fragment=False):
    """The base function for removing one adsorbate from an
    occupied site. The site must include information of 
    'adsorbate_indices' or 'fragment_indices'. Note that if
    you want to remove adsorbates from multiple sites, call
    this function multiple times will return the wrong result.
    Please use remove_adsorbates_from_sites instead.

    Parameters
    ----------
    atoms : ase.Atoms object
        Accept any ase.Atoms object. No need to be built-in.

    site : dict 
        The site that the adsorbate should be removed from.
        Must contain information of the adsorbate indices.

    remove_fragment : bool, default False
        Remove the fragment of a multidentate adsorbate instead 
        of the whole adsorbate.

    """

    if site['occupied']:
        if not remove_fragment:
            si = list(site['adsorbate_indices'])
        else:
            si = list(site['fragment_indices'])
        del atoms[si]
    else:
        warnings.warn('This site is not occupied.')


def remove_adsorbates_from_sites(atoms, sites, remove_fragments=False):
    """The base function for removing multiple adsorbates from
    an occupied site. The sites must include information of 
    'adsorbate_indices' or 'fragment_indices'.

    Parameters
    ----------
    atoms : ase.Atoms object
        Accept any ase.Atoms object. No need to be built-in.

    sites : list of dicts 
        The site that the adsorbate should be removed from.
        Must contain information of the adsorbate indices.

    remove_fragments : bool, default False
        Remove the fragment of a multidentate adsorbate instead 
        of the whole adsorbate.

    """

    if not remove_fragments:
        si = [i for s in sites if s['occupied'] for 
              i in s['adsorbate_indices']]
    else:
        si = [i for s in sites if s['occupied'] for 
              i in s['fragment_indices']]
    del atoms[si]


def remove_adsorbates_too_close(atoms, adsorbate_coverage=None,
                                surface=None, 
                                min_adsorbate_distance=0.5):
    """Find adsorbates that are too close, remove one set of them.
    The function is intended to remove atoms that are unphysically 
    close. Please do not use a min_adsorbate_distace larger than 2.
    The function is generalized for both periodic and non-periodic 
    systems (distinguished by atoms.pbc).


    Parameters
    ----------
    atoms : ase.Atoms object
        The nanoparticle or surface slab onto which the adsorbates are
        added. Accept any ase.Atoms object. No need to be built-in.

    adsorbate_coverage : acat.adsorbate_coverage.ClusterAdsorbateCoverage \
        object or acat.adsorbate_coverage.SlabAdsorbateCoverage object, \
        default None
        The built-in adsorbate coverage class.

    surface : str, default None
        The surface type (crystal structure + Miller indices). 
        If the structure is a periodic surface slab, this is required. 
        If the structure is a nanoparticle, the function only add 
        adsorbates to the sites on the specified surface. 

    min_adsorbate_distance : float, default 0.
        The minimum distance between two atoms that is not considered to
        be to close. This distance has to be small.
    
    """

    if adsorbate_coverage is not None:
        sac = adsorbate_coverage
    else:
        if True not in atoms.pbc:
            sac = ClusterAdsorbateCoverage(atoms)
        else:
            sac = SlabAdsorbateCoverage(atoms, surface)                  
    dups = get_close_atoms(atoms, cutoff=min_adsorbate_distance,
                           mic=(True in atoms.pbc))
    if dups.size == 0:
        return
    
    hsl = sac.hetero_site_list
    # Make sure it's not the bond length within a fragment being too close
    bond_rows, frag_id_list = [], []
    for st in hsl:
        if st['occupied']:
            frag_ids = list(st['fragment_indices'])
            frag_id_list.append(frag_ids)
            w = np.where((dups == x).all() for x in frag_ids)[0]
            if w:
                bond_rows.append(w[0])

    dups = dups[[i for i in range(len(dups)) if i not in bond_rows]]
    del_ids = set(dups[:,0])
    rm_ids = [i for lst in frag_id_list for i in lst if 
              del_ids.intersection(set(lst))]
    rm_ids = list(set(rm_ids))

    del atoms[rm_ids]
