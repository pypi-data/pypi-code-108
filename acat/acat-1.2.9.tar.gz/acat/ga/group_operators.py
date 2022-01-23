"""Procreation operators meant to be used in symmetry-constrained
genetic algorithm (SCGA)."""
from ..settings import adsorbate_elements, site_heights
from ..utilities import is_list_or_tuple, get_depth
from ..adsorption_sites import (ClusterAdsorptionSites,    
                                SlabAdsorptionSites)
from ..adsorbate_coverage import (ClusterAdsorbateCoverage,
                                  SlabAdsorbateCoverage)
from ..build.action import (add_adsorbate_to_site, 
                            remove_adsorbates_from_sites)
from ase.ga.offspring_creator import OffspringCreator
from collections import defaultdict
from operator import attrgetter
import warnings
import random


class Mutation(OffspringCreator):
    """Base class for all particle mutation type operators.
    Do not call this class directly."""

    def __init__(self, num_muts=1):
        OffspringCreator.__init__(self, num_muts=num_muts)
        self.descriptor = 'Mutation'
        self.min_inputs = 1


class GroupSubstitute(Mutation):
    """Substitute all the atoms in a group with a different element. 
    The elemental composition cannot be fixed.

    Parameters
    ----------
    groups : list of lists or list of list of lists, default None
        The atom indices in each user-divided group. Can be obtained 
        by `acat.build.ordering.SymmetricClusterOrderingGenerator` 
        or `acat.build.ordering.SymmetricSlabOrderingGenerator`.
        You can also mix structures with different groupings in one 
        GA run by providing all possible groups in a list of list of 
        lists, so that the algorithm will randomly assign a grouping
        to the structure, where for each grouping the atoms in each 
        group are of the same type. If not provided here, please 
        provide the groups in atoms.info['data']['groups'] in all 
        intial structures. 

    elements : list of strs, default None
        Only take into account the elements specified in this list. 
        Default is to take all elements into account.

    num_muts : int, default 1
        The number of times to perform this operation.

    """

    def __init__(self, groups=None, 
                 elements=None,
                 num_muts=1):
        Mutation.__init__(self, num_muts=num_muts)

        self.descriptor = 'GroupSubstitute'
        self.elements = elements
        self.groups = groups

    def substitute(self, atoms):
        """Does the actual substitution"""

        atoms = atoms.copy() 
        if self.groups is None:
            groups = atoms.info['data']['groups']
        else:
            depth = get_depth(self.groups)
            if depth > 2:
                random.shuffle(self.groups)
                found = False
                for gs in self.groups:  
                    if all(len(set([atoms[i].symbol for i in g])) == 1 for g in gs):
                        groups = gs
                        found = True
                        break
                assert found, 'Some structures have broken the symmetry' +\
                              ' so that no groups can be assigned.'                  
            else:
                groups = self.groups
        if self.elements is None:
            e = list(set(atoms.get_chemical_symbols()))
        else:
            e = self.elements

        sorted_elems = sorted(set(atoms.get_chemical_symbols()))
        if e is not None and sorted(e) != sorted_elems:
            for group in groups:
                torem = []
                for i in group:
                    if atoms[i].symbol not in e:
                        torem.append(i)
                for i in torem:
                    group.remove(i)

        itbms = random.sample(range(len(groups)), self.num_muts)
        
        for itbm in itbms:
            mut_group = groups[itbm]
            other_elements = [e for e in self.elements if 
                              e != atoms[mut_group[0]].symbol]
            to_element = random.choice(other_elements)
            atoms.symbols[mut_group] = len(mut_group) * to_element

        return atoms

    def get_new_individual(self, parents):
        f = parents[0]

        indi = self.substitute(f)
        indi = self.initialize_individual(f, indi)
        if 'groups' in f.info['data']:
            indi.info['data']['groups'] = f.info['data']['groups']
        indi.info['data']['parents'] = [f.info['confid']]

        return (self.finalize_individual(indi),
                self.descriptor + ':Parent {0}'.format(f.info['confid']))


class GroupPermutation(Mutation):
    """Permutes the elements in two random groups. The elemental 
    composition can be fixed.

    Parameters
    ----------
    groups : list of lists or list of list of lists, default None
        The atom indices in each user-divided group. Can be obtained 
        by `acat.build.ordering.SymmetricClusterOrderingGenerator` 
        or `acat.build.ordering.SymmetricSlabOrderingGenerator`.
        You can also mix structures with different groupings in one 
        GA run by providing all possible groups in a list of list of
        lists, so that the algorithm will randomly assign a grouping
        to the structure, where for each grouping the atoms in each 
        group are of the same type. If not provided here, please 
        provide the groups in atoms.info['data']['groups'] in all 
        intial structures. 

    elements : list of strs, default None
        Only take into account the elements specified in this list. 
        Default is to take all elements into account.

    keep_composition : bool, defulat False
        Whether the elemental composition should be the same as in
        the parents.

    num_muts : int, default 1
        The number of times to perform this operation.

    """

    def __init__(self, groups=None,
                 elements=None,
                 keep_composition=False, 
                 num_muts=1):
        Mutation.__init__(self, num_muts=num_muts)

        self.descriptor = 'GroupPermutation'
        self.elements = elements
        self.keep_composition = keep_composition
        self.groups = groups

    def get_new_individual(self, parents):

        f = parents[0].copy()
        diffatoms = len(set(f.numbers))

        # Return None if there is only one atomic type
        if diffatoms == 1:
            return None, '{1} not possible in {0}'.format(f.info['confid'],
                                                          self.descriptor)
        indi = self.initialize_individual(f)
        indi.info['data']['parents'] = [f.info['confid']]
        if self.groups is None:
            groups = f.info['data']['groups']
            indi.info['data']['groups'] = groups
        else:
            depth = get_depth(self.groups)
            if depth > 2:
                random.shuffle(self.groups)
                found = False
                for gs in self.groups:  
                    if all(len(set([f[i].symbol for i in g])) == 1 for g in gs):
                        groups = gs
                        found = True
                        break
                assert found, 'Some structures have broken the symmetry' +\
                              ' so that no groups can be assigned.'                 
            else:
                groups = self.groups
            if 'groups' in f.info['data']:
                indi.info['data']['groups'] = f.info['data']['groups']
        for _ in range(self.num_muts):
            GroupPermutation.mutate(f, groups, self.elements,
                                    self.keep_composition)
        for atom in f:
            indi.append(atom)

        return (self.finalize_individual(indi),
                self.descriptor + ':Parent {0}'.format(f.info['confid']))

    @classmethod
    def mutate(cls, atoms, groups, elements=None, keep_composition=False):
        """Do the actual permutation."""

        if elements is None:
            e = list(set(atoms.get_chemical_symbols()))
        else:
            e = elements

        sorted_elems = sorted(set(atoms.get_chemical_symbols()))
        if e is not None and sorted(e) != sorted_elems:
            for group in groups:
                torem = []
                for i in group:
                    if atoms[i].symbol not in e:
                        torem.append(i)
                for i in torem:
                    group.remove(i)

        if keep_composition:
            dd = defaultdict(list)
            for gi, group in enumerate(groups):
                dd[len(group)].append(gi)
            items = list(dd.items())
            random.shuffle(items)
            mut_gis = None
            for k, v in items:
                if len(v) > 1:
                    mut_gis = v
                    break
            if mut_gis is None:
                return
            random.shuffle(mut_gis)
            i1 = mut_gis[0]
            mut_group1 = groups[i1]           
            options = [i for i in mut_gis[1:] if atoms[mut_group1[0]].symbol 
                       != atoms[groups[i][0]].symbol]

        else:
            i1 = random.randint(0, len(groups) - 1)
            mut_group1 = groups[i1]
            options = [i for i in range(0, len(groups)) if atoms[mut_group1[0]].symbol 
                       != atoms[groups[i][0]].symbol]
        if not options:
            return

        i2 = random.choice(options)
        mut_group2 = groups[i2]
        atoms.symbols[mut_group1+mut_group2] = len(mut_group1) * atoms[
        mut_group2[0]].symbol + len(mut_group2) * atoms[mut_group1[0]].symbol            


class AdsorbateGroupSubstitute(Mutation):
    """Substitute all the adsorbates (or vacancies) in a site group 
    with a different element.

    Parameters
    ----------
    adsorbate_species : str or list of strs 
        A list of possible adsorbate species to be added to the surface.

    site_groups : list of lists or list of list of lists, default None
        The site indices in each user-divided group. Can be obtained 
        by `acat.build.ordering.SymmetricPatternGenerator`.
        You can also mix structures with different groupings in one 
        GA run by providing all possible groups in a list of list of
        lists, so that the algorithm will randomly assign a grouping
        to the structure, where for each grouping the adsorbate / 
        vacancy occupations in each site group are of the same type. 
        If not provided here, please provide the groups in 
        atoms.info['data']['groups'] in all intial structures. 

    max_species : int, default None
        The maximum allowed adsorbate species (excluding vacancies) for a
        single structure. Allow all adsorbatae species if not specified.

    heights : dict, default acat.settings.site_heights                
        A dictionary that contains the adsorbate height for each site 
        type. Use the default height settings if the height for a site
        type is not specified.

    adsorption_sites : acat.adsorption_sites.ClusterAdsorptionSites object 
        or acat.adsorption_sites.SlabAdsorptionSites object, default None
        Provide the built-in adsorption sites class to accelerate the 
        pattern generation. Make sure all the structures have the same 
        periodicity and atom indexing. If composition_effect=True, you 
        should only provide adsorption_sites when the surface composition 
        is fixed. If this is not provided, the arguments for identifying
        adsorption sites can still be passed in by **kwargs.

    remove_neighbor_sites : bool, default True
        Whether to remove the neighboring sites around each occupied site. 

    remove_neighbor_number : int, default 1
        The neighbor shell number within which the neighbors should be
        removed. Only relevant when remove_neighbor_sites=True.       

    num_muts : int, default 1
        The number of times to perform this operation.

    dmax : float, default 3.
        The maximum bond length (in Angstrom) between the site and the 
        bonding atom  that should be considered as an adsorbate.

    """

    def __init__(self, adsorbate_species,
                 site_groups=None, 
                 max_species=None,
                 heights=site_heights,
                 adsorption_sites=None,
                 remove_neighbor_sites=True,
                 remove_neighbor_number=1,
                 num_muts=1, dmax=3., **kwargs):
        Mutation.__init__(self, num_muts=num_muts)

        self.descriptor = 'AdsorbateGroupSubstitute'
        self.adsorbate_species = adsorbate_species if is_list_or_tuple(
                                 adsorbate_species) else [adsorbate_species]
        self.site_groups = site_groups
        self.max_species = max_species
        self.heights = heights
        self.adsorption_sites = adsorption_sites
        self.remove_neighbor_sites = remove_neighbor_sites
        self.remove_neighbor_number = remove_neighbor_number
        self.dmax = dmax

        self.kwargs = {'allow_6fold': False, 'composition_effect': False, 
                       'ignore_bridge_sites': True, 'label_sites': False}
        self.kwargs.update(kwargs)
        if self.adsorption_sites is not None:
            for k in self.kwargs.keys():             
                self.kwargs[k] = attrgetter(k)(self.adsorption_sites)
        self.__dict__.update(self.kwargs)                                  

    def substitute(self, atoms):
        """Does the actual substitution of the adsorbates"""

        atoms = atoms.copy() 
        if True in atoms.pbc:                                          
            if self.adsorption_sites is not None:
                sas = self.adsorption_sites
                sas.update(atoms)
            else:
                sas = SlabAdsorptionSites(atoms, **self.kwargs)
            sac = SlabAdsorbateCoverage(atoms, sas, dmax=self.dmax)
        else:
            if self.adsorption_sites is not None:
                sas = self.adsorption_sites
                sas.update(atoms)
            else:
                sas = ClusterAdsorptionSites(atoms, **self.kwargs)
            sac = ClusterAdsorbateCoverage(atoms, sas, dmax=self.dmax) 

        hsl = sac.hetero_site_list
        if self.site_groups is None:
            groups = atoms.info['data']['groups']
        else:
            depth = get_depth(self.site_groups)
            if depth > 2:
                random.shuffle(self.site_groups)
                found = False
                for gs in self.site_groups:  
                    if all(len(set([hsl[i]['fragment'] for i in g])) == 1 for g in gs):
                        groups = gs
                        found = True
                        break
                assert found, 'Some structures have broken the symmetry' +\
                              ' so that no groups can be assigned.'                     
            else:
                groups = self.site_groups

        ngroups = len(groups)
        indices = list(range(ngroups))
        if self.remove_neighbor_sites:
            nsl = sas.get_neighbor_site_list(neighbor_number=self.remove_neighbor_number)
            indexes = indices.copy()
            random.shuffle(indexes)
            itbms = set()
            for j in range(len(indexes)):
                itbms.add(j)
                if hsl[groups[j][0]]['occupied']:
                    inset = {ni for i in groups[j] for ni in nsl[i]}
                    ings = [nj for nj in indexes if not set(groups[nj]).isdisjoint(inset)]
                    itbms = set(itbms) - set(ings)
                if len(itbms) == self.num_muts:
                    break
            itbms = list(itbms) 
        else:
            itbms = random.sample(indices, self.num_muts)
        not_mut = [j for j in indices if j not in itbms]
        random.shuffle(not_mut)
        if self.max_species is None:                      
            options = self.adsorbate_species + ['vacancy']
        else:
            not_mut_specs = {hsl[groups[j][0]]['fragment'] for j in not_mut
                             if hsl[groups[j][0]]['occupied']}
            diff = self.max_species - len(not_mut_specs)
            if diff > 0:
                others = [sp for sp in self.adsorbate_species if sp not in not_mut_specs]
                options = list(not_mut_specs) + random.sample(others, diff) + ['vacancy'] 
            elif diff == 0:
                options = list(not_mut_specs) + ['vacancy']
            else:
                options = list(not_mut_specs) + ['vacancy']
                warnings.warn('The number of adsorbate species exceeds ' +
                              'the maximum allowed number.')

        changes = [None] * ngroups                                 
        newvs = set()
        indices = itbms + not_mut
        for idx in indices:
            group = groups[idx]
            st0 = hsl[group[0]]
            if not set(group).isdisjoint(newvs):
                if st0['occupied']:
                    changes[idx] = 'vacancy'
            elif idx in itbms:
                if st0['occupied']:
                    spec = st0['fragment']
                else:
                    spec = 'vacancy'     
                other_specs = [sp for sp in options if sp != spec]
                to_spec = random.choice(other_specs)
                changes[idx] = to_spec
                if to_spec == 'vacancy':
                    newvs.update(group)
                elif self.remove_neighbor_sites:
                    newvs.update([i for k in group for i in nsl[k]])

        rmsites = [hsl[j] for idx, to_spec in enumerate(changes) 
                   if to_spec is not None for j in groups[idx]]
        remove_adsorbates_from_sites(atoms, sites=rmsites, remove_fragments=True)
        for idx, to_spec in enumerate(changes):
            if to_spec not in [None, 'vacancy']:
                for j in groups[idx]:
                    st = hsl[j]
                    height = self.heights[st['site']]
                    add_adsorbate_to_site(atoms, to_spec, st, height)

        if True in atoms.pbc:
            nsac = SlabAdsorbateCoverage(atoms, sas, dmax=self.dmax)
        else:
            nsac = ClusterAdsorbateCoverage(atoms, sas, dmax=self.dmax)
        atoms.info['data']['adsorbates'] = [t[0] for t in 
            nsac.get_adsorbates(self.adsorbate_species)]

        return atoms

    def get_new_individual(self, parents):
        f = parents[0]

        indi = self.substitute(f)
        indi = self.initialize_individual(f, indi) 
        if 'groups' in f.info['data']:
            indi.info['data']['groups'] = f.info['data']['groups']
        indi.info['data']['parents'] = [f.info['confid']] 

        return (self.finalize_individual(indi),
                self.descriptor + ':Parent {0}'.format(f.info['confid']))


class AdsorbateGroupPermutation(Mutation):
    """Permutes the elements in two random site groups.

    Parameters
    ----------
    adsorbate_species : str or list of strs 
        A list of possible adsorbate species to be added to the surface.

    site_groups : list of lists or list of list of lists, default None
        The site indices in each user-divided group. Can be obtained 
        by `acat.build.ordering.SymmetricPatternGenerator`.
        You can also mix structures with different groupings in one 
        GA run by providing all possible groups in a list of list of
        lists, so that the algorithm will randomly assign a grouping
        to the structure, where for each grouping the adsorbate / 
        vacancy occupations in each site group are of the same type.
        If not provided here, please provide the groups in 
        atoms.info['data']['groups'] in all intial structures. 

    heights : dict, default acat.settings.site_heights                
        A dictionary that contains the adsorbate height for each site 
        type. Use the default height settings if the height for a site
        type is not specified.

    adsorption_sites : acat.adsorption_sites.ClusterAdsorptionSites object 
        or acat.adsorption_sites.SlabAdsorptionSites object, default None
        Provide the built-in adsorption sites class to accelerate the 
        pattern generation. Make sure all the structures have the same 
        periodicity and atom indexing. If composition_effect=True, you 
        should only provide adsorption_sites when the surface composition 
        is fixed. If this is not provided, the arguments for identifying
        adsorption sites can still be passed in by **kwargs.

    remove_neighbor_sites : bool, default True
        Whether to remove the neighboring sites around each occupied site. 

    remove_neighbor_number : int, default 1
        The neighbor shell number within which the neighbors should be
        removed. Only relevant when remove_neighbor_sites=True.       

    num_muts : int, default 1
        The number of times to perform this operation.

    dmax : float, default 3.
        The maximum bond length (in Angstrom) between the site and the 
        bonding atom  that should be considered as an adsorbate.

    """

    def __init__(self, adsorbate_species, 
                 site_groups=None,
                 heights=site_heights,
                 adsorption_sites=None,
                 remove_neighbor_sites=True,
                 remove_neighbor_number=1,
                 num_muts=1, dmax=3., **kwargs):
        Mutation.__init__(self, num_muts=num_muts)

        self.descriptor = 'AdsorbateGroupPermutation'
        self.adsorbate_species = adsorbate_species if is_list_or_tuple(       
                                 adsorbate_species) else [adsorbate_species]
        self.site_groups = site_groups
        self.heights = heights
        self.adsorption_sites = adsorption_sites
        self.remove_neighbor_sites = remove_neighbor_sites
        self.remove_neighbor_number = remove_neighbor_number
        self.dmax = dmax

        self.kwargs = {'allow_6fold': False, 'composition_effect': False, 
                       'ignore_bridge_sites': True, 'label_sites': False}
        self.kwargs.update(kwargs)
        if self.adsorption_sites is not None:
            for k in self.kwargs.keys():             
                self.kwargs[k] = attrgetter(k)(self.adsorption_sites)
        self.__dict__.update(self.kwargs)                                  

    def get_new_individual(self, parents):

        f = parents[0].copy()
        
        indi = self.initialize_individual(f)
        indi.info['data']['parents'] = [f.info['confid']]

        if True in f.pbc:                                          
            if self.adsorption_sites is not None:
                sas = self.adsorption_sites
                sas.update(f)
            else:
                sas = SlabAdsorptionSites(f, **self.kwargs)
            sac = SlabAdsorbateCoverage(f, sas, dmax=self.dmax)
        else:
            if self.adsorption_sites is not None:
                sas = self.adsorption_sites
                sas.update(f)
            else:
                sas = ClusterAdsorptionSites(f, **self.kwargs)
            sac = ClusterAdsorbateCoverage(f, sas, dmax=self.dmax) 
        hsl = sac.hetero_site_list

        if self.site_groups is None:
            site_groups = f.info['data']['groups']
            indi.info['data']['groups'] = site_groups
        else:
            depth = get_depth(self.site_groups)
            if depth > 2:
                random.shuffle(self.site_groups)
                found = False
                for gs in self.site_groups:  
                    if all(len(set([hsl[i]['fragment'] for i in g])) == 1 for g in gs):
                        site_groups = gs
                        found = True
                        break
                assert found, 'Some structures have broken the symmetry' +\
                              ' so that no groups can be assigned.'                     
            else:
                site_groups = self.site_groups
            if 'groups' in f.info['data']:
                indi.info['data']['groups'] = f.info['data']['groups']

        # Return None if there is only one adsorbate (vacancy) type
        if set([hsl[g[0]]['fragment'] for g in site_groups]) == 1:
            return None, '{1} not possible in {0}'.format(f.info['confid'],
                                                          self.descriptor)
        for _ in range(self.num_muts):
            AdsorbateGroupPermutation.mutate(f, site_groups, self.heights, sas, 
                                             hsl, self.remove_neighbor_sites, 
                                             self.remove_neighbor_number)
            if True in indi.pbc:
                nsac = SlabAdsorbateCoverage(f, sas, dmax=self.dmax)
            else:
                nsac = ClusterAdsorbateCoverage(f, sas, dmax=self.dmax)
            hsl = nsac.hetero_site_list

        for atom in f:
            indi.append(atom)
        
        indi.info['data']['adsorbates'] = [t[0] for t in 
            nsac.get_adsorbates(self.adsorbate_species)]

        return (self.finalize_individual(indi),
                self.descriptor + ':Parent {0}'.format(f.info['confid']))

    @classmethod
    def mutate(cls, atoms, groups, heights, adsorption_sites, hetero_site_list, 
               remove_neighbor_sites, remove_neighbor_number):
        """Do the actual permutation of the adsorbates."""

        sas, hsl = adsorption_sites, hetero_site_list
        ngroups = len(groups)
        indices = list(range(ngroups))
        i1 = random.randint(0, ngroups - 1)
        st01 = hsl[groups[i1][0]]
        ings = []
        if remove_neighbor_sites:                                                   
            nsl = sas.get_neighbor_site_list(neighbor_number=remove_neighbor_number)
            if st01['occupied']:
                ings += [nj for nj in indices if not set(groups[nj]).isdisjoint(nsl[i1])]
        options = [j for j in range(ngroups) if (j not in ings) and 
                   (st01['fragment'] != hsl[groups[j][0]]['fragment'])]
        if not options:
            return
        i2 = random.choice(options)
        st02 = hsl[groups[i2][0]]
        if st01['occupied']:
            to_spec2 = st01['fragment']
        else: 
            to_spec2 = 'vacancy'
        if st02['occupied']:
            to_spec1 = st02['fragment']
        else:
            to_spec1 = 'vacancy'
        not_mut = [j for j in indices if j not in [i1, i2]]
        random.shuffle(not_mut)

        changes = [None] * ngroups 
        newvs = set()
        indices = [i1, i2] + not_mut
        for idx in indices:
            group = groups[idx]
            st0 = hsl[group[0]]
            if not set(group).isdisjoint(newvs): 
                if st0['occupied']:
                    changes[idx] = 'vacancy'
            elif idx == i1:
                changes[idx] = to_spec1
                if to_spec1 == 'vacancy':
                    newvs.update(group)
                elif remove_neighbor_sites:
                    newvs.update([i for k in group for i in nsl[k]])
            elif idx == i2:
                changes[idx] = to_spec2
                if to_spec2 == 'vacancy':
                    newvs.update(group)
                elif remove_neighbor_sites:
                    newvs.update([i for k in group for i in nsl[k]])

        rmsites = [hsl[j] for idx, to_spec in enumerate(changes) 
                   if to_spec is not None for j in groups[idx]]
        remove_adsorbates_from_sites(atoms, sites=rmsites, remove_fragments=True)
        for idx, to_spec in enumerate(changes):
            if to_spec not in [None, 'vacancy']:
                for j in groups[idx]:
                    st = hsl[j]
                    height = heights[st['site']]
                    add_adsorbate_to_site(atoms, to_spec, st, height)


class Crossover(OffspringCreator):
    """Base class for all particle crossovers.
    Do not call this class directly."""
    def __init__(self):
        OffspringCreator.__init__(self)
        self.descriptor = 'Crossover'
        self.min_inputs = 2


class GroupCrossover(Crossover):
    """Merge the elemental distributions in two half groups from 
    different structures together. The elemental composition can be 
    fixed.

    Parameters
    ----------
    groups : list of lists or list of list of lists, default None
        The atom indices in each user-divided group. Can be obtained 
        by `acat.build.ordering.SymmetricClusterOrderingGenerator` 
        or `acat.build.ordering.SymmetricSlabOrderingGenerator`.
        You can also mix structures with different groupings in one 
        GA run by providing all possible groups in a list of list of
        lists, so that the algorithm will randomly assign a grouping
        to the structure, where for each grouping the atoms in each 
        group are of the same type. If not provided here, please 
        provide the groups in atoms.info['data']['groups'] in all 
        intial structures. 

    elements : list of strs, default None
        Only take into account the elements specified in this list. 
        Default is to take all elements into account.

    keep_composition : bool, defulat False
        Whether the elemental composition should be the same as in
        the parents.

    """

    def __init__(self, groups=None, elements=None, keep_composition=False):
        Crossover.__init__(self)
        self.groups = groups
        self.elements = elements
        self.keep_composition = keep_composition
        self.descriptor = 'GroupCrossover'
        
    def get_new_individual(self, parents):

        f, m = parents
        indi = f.copy()
        if self.groups is None:
            assert f.info['data']['groups'] == m.info['data']['groups']
            groups = indi.info['data']['groups']
        else:
            depth = get_depth(self.groups)
            if depth > 2:
                random.shuffle(self.groups)
                found = False
                for gs in self.groups:  
                    if all(len(set([atoms[i].symbol for i in g])) == 1 for g in gs):
                        groups = gs
                        found = True
                        break
                assert found, 'Some structures have broken the symmetry' +\
                              ' so that no groups can be assigned.'                 
            else:
                groups = self.groups.copy()
        if self.elements is None:
            e = list(set(f.get_chemical_symbols()))
        else:
            e = self.elements

        sorted_elems = sorted(set(f.get_chemical_symbols()))
        if e is not None and sorted(e) != sorted_elems:
            for group in groups:
                torem = []
                for i in group:
                    if f[i].symbol not in e:
                        torem.append(i)
                for i in torem:
                    group.remove(i)
        random.shuffle(groups)

        if self.keep_composition:
            def fix_composition_swaps(groups1, groups2):
                indices = sorted([i for j in groups1 for i in j])                                
                zipped = list(map(list, zip(groups1, groups2)))
                gids = [i for i, (groups1, groups2) in enumerate(zipped) 
                        if groups1 != groups2]

                # If solution not found in 1000 iterations, we say there
                # is no possible solution at all
                gids_list = []
                for j in range(1000):        
                    random.shuffle(gids)
                    if gids in gids_list:
                        continue
                    gids_list.append(gids.copy())

                    for n, i in enumerate(gids):
                        zipped[i].reverse()
                        if indices == sorted(idx for groups1, _ in zipped 
                        for idx in groups1):
                            return gids[:n+1]
                    zipped = list(map(list, zip(groups1, groups2)))
                return []

            fsyms = [list(f.symbols[g]) for g in groups]
            msyms = [list(m.symbols[g]) for g in groups]
            swap_ids = fix_composition_swaps(fsyms, msyms)
            mids = [i for j in swap_ids for i in groups[j]] 

        else:
            mgroups = groups[len(groups)//2:]
            mids = [i for group in mgroups for i in group]

        indi.symbols[mids] = m.symbols[mids]
        indi = self.initialize_individual(f, indi)
        if 'groups' in f.info['data']:
            indi.info['data']['groups'] = f.info['data']['groups']
        indi.info['data']['parents'] = [i.info['confid'] for i in parents] 
        indi.info['data']['operation'] = 'crossover'
        parent_message = ':Parents {0} {1}'.format(f.info['confid'],
                                                   m.info['confid']) 

        return (self.finalize_individual(indi),
                self.descriptor + parent_message)
