from ..settings import (adsorbate_elements, site_heights, 
                        monodentate_adsorbate_list, 
                        multidentate_adsorbate_list)
from ..adsorption_sites import (ClusterAdsorptionSites, 
                                SlabAdsorptionSites, 
                                group_sites_by_facet)
from ..adsorbate_coverage import (ClusterAdsorbateCoverage, 
                                  SlabAdsorbateCoverage)
from ..utilities import (get_mic, atoms_too_close_after_addition, 
                         is_list_or_tuple, numbers_from_ratios)
from ..labels import (get_cluster_signature_from_label, 
                      get_slab_signature_from_label)
from .action import (add_adsorbate_to_site, 
                     remove_adsorbate_from_site)
from ase.io import read, write, Trajectory
from ase.formula import Formula
from ase.geometry import find_mic
from operator import attrgetter
from copy import deepcopy
import networkx.algorithms.isomorphism as iso
import networkx as nx
from scipy.spatial import distance_matrix
import numpy as np
import warnings
import random


class StochasticPatternGenerator(object):
    """`StochasticPatternGenerator` is a class for generating 
    adsorbate overlayer patterns stochastically. Graph isomorphism
    is implemented to identify identical adlayer patterns. 4 
    adsorbate actions are supported: add, remove, move, replace. 
    The class is generalized for both periodic and non-periodic 
    systems (distinguished by atoms.pbc). 

    Parameters
    ----------
    images : ase.Atoms object or list of ase.Atoms objects
        The structure to perform the adsorbate actions on. 
        If a list of structures is provided, perform one 
        adsorbate action on one of the structures in each step. 
        Accept any ase.Atoms object. No need to be built-in.

    adsorbate_species : str or list of strs 
        A list of adsorbate species to be randomly added to the surface.

    image_probabilities : listt, default None
        A list of the probabilities of selecting each structure.
        Selecting structure with equal probability if not specified.

    species_probabilities : dict, default None
        A dictionary that contains keys of each adsorbate species and 
        values of their probabilities of adding onto the surface.
        Adding adsorbate species with equal probability if not specified.

    min_adsorbate_distance : float, default 1.5
        The minimum distance constraint between two atoms that belongs 
        to two adsorbates.

    adsorption_sites : acat.adsorption_sites.ClusterAdsorptionSites object \
        or acat.adsorption_sites.SlabAdsorptionSites object, default None
        Provide the built-in adsorption sites class to accelerate the 
        pattern generation. Make sure all the structures have the same 
        periodicity and atom indexing. If composition_effect=True, you 
        should only provide adsorption_sites when the surface composition 
        is fixed. If this is not provided, the arguments for identifying
        adsorption sites can still be passed in by **kwargs.

    heights : dict, default acat.settings.site_heights
        A dictionary that contains the adsorbate height for each site 
        type. Use the default height settings if the height for a site 
        type is not specified.

    dmax : float, default 3.
        The maximum bond length (in Angstrom) between the site and the 
        bonding atom that should be considered as an adsorbate.

    species_forbidden_sites : dict, default None                       
        A dictionary that contains keys of each adsorbate species and 
        values of the site (can be one or multiple site types) that the 
        speices is not allowed to add to. All sites are availabe for a
        species if not specified. Note that this does not differentiate
        sites with different compositions.

    species_forbidden_labels : dict, default None
        Same as species_forbidden_sites except that the adsorption sites
        are written as numerical labels according to acat.labels. Useful
        when you need to differentiate sites with different compositions.

    fragmentation : bool, default True                                  
        Whether to cut multidentate species into fragments. This ensures 
        that multidentate species with different orientations are
        considered as different adlayer patterns.

    trajectory : str, default 'patterns.traj'
        The name of the output ase trajectory file.

    append_trajectory : bool, default False
        Whether to append structures to the existing trajectory. 
        If only unique patterns are accepted, the code will also check 
        graph isomorphism for the existing structures in the trajectory.
        This is also useful when you want to generate adlayer patterns 
        stochastically but for all images systematically, e.g. generating
        10 stochastic adlayer patterns for each image:

        >>> from acat.build.adlayer import StochasticPatternGenerator as SPG
        >>> for atoms in images:
        ...    spg = SPG(atoms, ..., append_trajectory=True)
        ...    spg.run(num_gen = 10)

    logfile : str, default 'patterns.log'
        The name of the log file.

    """

    def __init__(self, images,                                                       
                 adsorbate_species,
                 image_probabilities=None,
                 species_probabilities=None,
                 min_adsorbate_distance=1.5,
                 adsorption_sites=None,
                 heights=site_heights,
                 dmax=3.,                 
                 species_forbidden_sites=None,    
                 species_forbidden_labels=None,
                 fragmentation=True,
                 trajectory='patterns.traj',
                 append_trajectory=False,
                 logfile='patterns.log', 
                 **kwargs):

        self.images = images if is_list_or_tuple(images) else [images]                     
        self.adsorbate_species = adsorbate_species if is_list_or_tuple(
                                 adsorbate_species) else [adsorbate_species]
        self.monodentate_adsorbates = [s for s in self.adsorbate_species if s in 
                                       monodentate_adsorbate_list]
        self.multidentate_adsorbates = [s for s in self.adsorbate_species if s in
                                        multidentate_adsorbate_list]
        if len(self.adsorbate_species) != len(self.monodentate_adsorbates +
        self.multidentate_adsorbates):
            diff = list(set(self.adsorbate_species) - 
                        set(self.monodentate_adsorbates +
                            self.multidentate_adsorbates))
            raise ValueError('species {} are not defined '.format(diff) +
                             'in adsorbate_list in acat.settings')             

        self.image_probabilities = image_probabilities
        if self.image_probabilities is not None:
            assert len(self.image_probabilities) == len(self.images)
        self.species_probabilities = species_probabilities
        if self.species_probabilities is not None:
            assert len(self.species_probabilities.keys()) == len(self.adsorbate_species)
            self.species_probability_list = [self.species_probabilities[a] for 
                                             a in self.adsorbate_species]               
         
        self.min_adsorbate_distance = min_adsorbate_distance
        self.adsorption_sites = adsorption_sites
        self.heights = site_heights 
        for k, v in heights.items():
            self.heights[k] = v
        self.dmax = dmax
        self.kwargs = {'allow_6fold': False, 'composition_effect': False,
                       'ignore_bridge_sites': False, 'label_sites': False} 
        self.kwargs.update(kwargs)
        if self.adsorption_sites is not None:
            for k in self.kwargs.keys():             
                self.kwargs[k] = attrgetter(k)(self.adsorption_sites)
        self.__dict__.update(self.kwargs)
        self.species_forbidden_sites = species_forbidden_sites
        self.species_forbidden_labels = species_forbidden_labels

        if self.species_forbidden_labels is not None:
            self.species_forbidden_labels = {k: v if is_list_or_tuple(v) else [v] for
                                             k, v in self.species_forbidden_labels.items()}
        if self.species_forbidden_sites is not None:
            self.species_forbidden_sites = {k: v if is_list_or_tuple(v) else [v] for
                                            k, v in self.species_forbidden_sites.items()}  
        self.fragmentation = fragmentation
        if isinstance(trajectory, str):            
            self.trajectory = trajectory 
        self.append_trajectory = append_trajectory
        if isinstance(logfile, str):
            self.logfile = open(logfile, 'a')      
 
        if self.adsorption_sites is not None:
            if self.multidentate_adsorbates:
                self.bidentate_nblist = \
                self.adsorption_sites.get_neighbor_site_list(neighbor_number=1)
            self.site_nblist = \
            self.adsorption_sites.get_neighbor_site_list(neighbor_number=2)

    def _add_adsorbate(self, adsorption_sites):
        sas = adsorption_sites
        if self.adsorption_sites is not None:                               
            site_nblist = self.site_nblist
        else:
            site_nblist = sas.get_neighbor_site_list(neighbor_number=2)     
         
        if self.clean_slab:
            hsl = sas.site_list
            nbstids = set()
            neighbor_site_indices = []
        else:
            if True in self.atoms.pbc:
                sac = SlabAdsorbateCoverage(self.atoms, sas, dmax=self.dmax,
                                            label_occupied_sites=self.unique) 
            else: 
                sac = ClusterAdsorbateCoverage(self.atoms, sas, dmax=self.dmax, 
                                               label_occupied_sites=self.unique)                                                
            hsl = sac.hetero_site_list
            nbstids, selfids = [], []
            for j, st in enumerate(hsl):
                if st['occupied']:
                    nbstids += site_nblist[j]
                    selfids.append(j)
            nbstids = set(nbstids)
            neighbor_site_indices = [v for v in nbstids if v not in selfids]            
                                                                                             
        # Select adsorbate with probability 
        if self.add_species_composition is not None:
            adsorbate = self.adsorbates_to_add.pop(random.randint(0, len(
                                                   self.adsorbates_to_add)-1))
        else:
            if self.species_probabilities is None:
                adsorbate = random.choice(self.adsorbate_species)
            else: 
                adsorbate = random.choices(k=1, population=self.adsorbate_species,
                                           weights=self.species_probability_list)[0]    
                                                                                             
        # Only add one adsorabte to a site at least 2 shells 
        # away from currently occupied sites
        nsids = [i for i, s in enumerate(hsl) if i not in nbstids]

        if self.species_forbidden_labels is not None:
            if adsorbate in self.species_forbidden_labels:
                forb_labs = self.species_forbidden_labels[adsorbate]
                if True in self.atoms.pbc:
                    def get_label(site):
                        if sas.composition_effect:
                            signature = [site['site'], site['morphology'], 
                                         site['composition']]
                        else:
                            signature = [site['site'], site['morphology']]
                        return sas.label_dict['|'.join(signature)]                        
                else:
                    def get_label(site):
                        if sas.composition_effect:
                            signature = [site['site'], site['surface'], 
                                         site['composition']]
                        else:
                            signature = [site['site'], site['surface']]
                        return sas.label_dict['|'.join(signature)]                   

                nsids = [i for i in nsids if get_label(hsl[i]) not in forb_labs]    

        elif self.species_forbidden_sites is not None:
            if adsorbate in self.species_forbidden_sites:
                nsids = [i for i in nsids if hsl[i]['site'] not in 
                         self.species_forbidden_sites[adsorbate]] 
        if not nsids:                                                             
            if self.logfile is not None:                                          
                self.logfile.write('Not enough space to add {} '.format(adsorbate)
                                   + 'to any site. Addition failed!\n')
                self.logfile.flush()
            return
                                                                                             
        # Prohibit adsorbates with more than 1 atom from entering subsurf 6-fold sites
        subsurf_site = True
        nsi = None
        while subsurf_site: 
            nsi = random.choice(nsids)
            if self.allow_6fold:
                subsurf_site = (len(adsorbate) > 1 and hsl[nsi]['site'] == '6fold')
            else:
                subsurf_site = (hsl[nsi]['site'] == '6fold')
                                                                                             
        nst = hsl[nsi]            
        if adsorbate in self.multidentate_adsorbates:                                                   
            if self.adsorption_sites is not None:                               
                bidentate_nblist = self.bidentate_nblist
            else:
                bidentate_nblist = sas.get_neighbor_site_list(neighbor_number=1)

            binbs = bidentate_nblist[nsi]                    
            binbids = [n for n in binbs if n not in nbstids]
            if not binbids and nst['site'] != '6fold':
                if self.logfile is not None:                                          
                    self.logfile.write('Not enough space to add {} '.format(adsorbate) 
                                       + 'to any site. Addition failed!\n')
                    self.logfile.flush()
                return            
                                                                                             
            # Rotate a bidentate adsorbate to the direction of a randomly 
            # choosed neighbor site
            nbst = hsl[random.choice(binbids)]
            pos = nst['position'] 
            nbpos = nbst['position'] 
            orientation = get_mic(nbpos, pos, self.atoms.cell)
            add_adsorbate_to_site(self.atoms, adsorbate, nst, 
                                  height=self.heights[nst['site']],
                                  orientation=orientation)                                 
        else:
            add_adsorbate_to_site(self.atoms, adsorbate, nst, 
                                  height=self.heights[nst['site']])                            

        if True in self.atoms.pbc:
            nsac = SlabAdsorbateCoverage(self.atoms, sas, dmax=self.dmax,
                                         label_occupied_sites=self.unique) 
        else:
            nsac = ClusterAdsorbateCoverage(self.atoms, sas, dmax=self.dmax, 
                                            label_occupied_sites=self.unique)
        nhsl = nsac.hetero_site_list
                                                                           
        # Make sure there is no new site too close to previous sites after 
        # the action. Useful when adding large molecules
        if any(s for i, s in enumerate(nhsl) if (s['occupied'])
        and (i in neighbor_site_indices)):
            if self.logfile is not None:
                self.logfile.write('The added {} is too close '.format(adsorbate)
                                   + 'to another adsorbate. Addition failed!\n')
                self.logfile.flush()
            return
        ads_atoms = self.atoms[[a.index for a in self.atoms if                   
                                a.symbol in adsorbate_elements]]
        if atoms_too_close_after_addition(ads_atoms, len(list(Formula(adsorbate))), 
        self.min_adsorbate_distance, mic=(True in self.atoms.pbc)):        
            if self.logfile is not None:
                self.logfile.write('The added {} is too close '.format(adsorbate)
                                   + 'to another adsorbate. Addition failed!\n')
                self.logfile.flush()
            return

        return nsac                                                                

    def _remove_adsorbate(self, adsorption_sites):
        sas = adsorption_sites 
        if True in self.atoms.pbc:                    
            sac = SlabAdsorbateCoverage(self.atoms, sas, dmax=self.dmax,
                                        label_occupied_sites=self.unique) 
        else: 
            sac = ClusterAdsorbateCoverage(self.atoms, sas, dmax=self.dmax,
                                           label_occupied_sites=self.unique)
        hsl = sac.hetero_site_list
        occupied = [s for s in hsl if s['occupied']]
        if not occupied:
            if self.logfile is not None:
                self.logfile.write('There is no occupied site. Removal failed!\n')
                self.logfile.flush()
            return
        rmst = random.choice(occupied)
        rm_frag = rmst['fragment'] in self.adsorbate_species 
        remove_adsorbate_from_site(self.atoms, rmst, remove_fragment=rm_frag)

        ads_remain = [a for a in self.atoms if a.symbol in adsorbate_elements]
        if not ads_remain:
            if self.logfile is not None:
                self.logfile.write('Last adsorbate has been removed ' + 
                                   'from image {}\n'.format(self.n_image))
                self.logfile.flush()
            return

        if True in self.atoms.pbc:
            nsac = SlabAdsorbateCoverage(self.atoms, sas, dmax=self.dmax,
                                         label_occupied_sites=self.unique) 
        else:
            nsac = ClusterAdsorbateCoverage(self.atoms, sas, dmax=self.dmax,
                                            label_occupied_sites=self.unique)                      
        return nsac 

    def _move_adsorbate(self, adsorption_sites):           
        sas = adsorption_sites
        if self.adsorption_sites is not None:
            site_nblist = self.site_nblist
        else:
            site_nblist = sas.get_neighbor_site_list(neighbor_number=2) 

        if True in self.atoms.pbc:                                                                         
            sac = SlabAdsorbateCoverage(self.atoms, sas, dmax=self.dmax,
                                        label_occupied_sites=self.unique) 
        else: 
            sac = ClusterAdsorbateCoverage(self.atoms, sas, dmax=self.dmax,
                                           label_occupied_sites=self.unique)
        hsl = sac.hetero_site_list
        occupied = [s for s in hsl if s['occupied']]                         
        if not occupied:
            if self.logfile is not None:
                self.logfile.write('There is no occupied site. Move failed!\n')
                self.logfile.flush()
            return
        rmst = random.choice(occupied)
        adsorbate = rmst['adsorbate']
        rm_frag = rmst['fragment'] in self.adsorbate_species 
        remove_adsorbate_from_site(self.atoms, rmst, remove_fragment=rm_frag)

        nbstids, selfids = [], []
        for j, st in enumerate(hsl):
            if st['occupied']:
                nbstids += site_nblist[j]
                selfids.append(j)
        nbstids = set(nbstids)
        neighbor_site_indices = [v for v in nbstids if v not in selfids]
                                                                                        
        # Only add one adsorabte to a site at least 2 shells 
        # away from currently occupied sites
        nsids = [i for i, s in enumerate(hsl) if i not in nbstids]

        if self.species_forbidden_labels is not None:
            if adsorbate in self.species_forbidden_labels:
                forb_labs = self.species_forbidden_labels[adsorbate]
                if True in self.atoms.pbc:
                    def get_label(site):
                        if sas.composition_effect:
                            signature = [site['site'], site['morphology'], 
                                         site['composition']]
                        else:
                            signature = [site['site'], site['morphology']]
                        return sas.label_dict['|'.join(signature)]                        
                else:
                    def get_label(site):
                        if sas.composition_effect:
                            signature = [site['site'], site['surface'], 
                                         site['composition']]
                        else:
                            signature = [site['site'], site['surface']]
                        return sas.label_dict['|'.join(signature)]                   
                                                                                             
                nsids = [i for i in nsids if get_label(hsl[i]) not in forb_labs]   

        elif self.species_forbidden_sites is not None:
            if adsorbate in self.species_forbidden_sites:
                nsids = [i for i in nsids if hsl[i]['site'] not in 
                         self.species_forbidden_sites[adsorbate]] 
        if not nsids:                                                             
            if self.logfile is not None:                                          
                self.logfile.write('Not enough space to place {} '.format(adsorbate)
                                   + 'on any other site. Move failed!\n')
                self.logfile.flush()
            return
                                                                                        
        # Prohibit adsorbates with more than 1 atom from entering subsurf 6-fold sites
        subsurf_site = True
        nsi = None
        while subsurf_site: 
            nsi = random.choice(nsids)
            if self.allow_6fold:
                subsurf_site = (len(adsorbate) > 1 and hsl[nsi]['site'] == '6fold')
            else:
                subsurf_site = (hsl[nsi]['site'] == '6fold')
                                                                                        
        nst = hsl[nsi]            
        if adsorbate in self.multidentate_adsorbates:                                   
            if self.adsorption_sites is not None:
                bidentate_nblist = self.bidentate_nblist
            else:
                bidentate_nblist = sas.get_neighbor_site_list(neighbor_number=1)

            binbs = bidentate_nblist[nsi]                    
            binbids = [n for n in binbs if n not in nbstids]
            if not binbids:
                if self.logfile is not None:
                    self.logfile.write('Not enough space to place {} '.format(adsorbate) 
                                       + 'on any other site. Move failed!\n')
                    self.logfile.flush()
                return
                                                                                        
            # Rotate a bidentate adsorbate to the direction of a randomly 
            # choosed neighbor site
            nbst = hsl[random.choice(binbids)]
            pos = nst['position'] 
            nbpos = nbst['position'] 
            orientation = get_mic(nbpos, pos, self.atoms.cell)
            add_adsorbate_to_site(self.atoms, adsorbate, nst, 
                                  height=self.heights[nst['site']], 
                                  orientation=orientation)    
        else:
            add_adsorbate_to_site(self.atoms, adsorbate, nst,
                                  height=self.heights[nst['site']])                          

        if True in self.atoms.pbc:
            nsac = SlabAdsorbateCoverage(self.atoms, sas, dmax=self.dmax,
                                         label_occupied_sites=self.unique) 
        else: 
            nsac = ClusterAdsorbateCoverage(self.atoms, sas, dmax=self.dmax,
                                            label_occupied_sites=self.unique)
        nhsl = nsac.hetero_site_list
                                                                           
        # Make sure there is no new site too close to previous sites after 
        # the action. Useful when adding large molecules
        if any(s for i, s in enumerate(nhsl) if s['occupied'] and (i in 
        neighbor_site_indices)):
            if self.logfile is not None:
                self.logfile.write('The new position of {} is too '.format(adsorbate)
                                   + 'close to another adsorbate. Move failed!\n')
                self.logfile.flush()
            return
        ads_atoms = self.atoms[[a.index for a in self.atoms if                   
                                a.symbol in adsorbate_elements]]
        if atoms_too_close_after_addition(ads_atoms, len(list(Formula(adsorbate))), 
        self.min_adsorbate_distance, mic=(True in self.atoms.pbc)):
            if self.logfile is not None:
                self.logfile.write('The new position of {} is too '.format(adsorbate)
                                   + 'close to another adsorbate. Move failed!\n')
                self.logfile.flush()
            return
 
        return nsac                                                                 

    def _replace_adsorbate(self, adsorption_sites):
        sas = adsorption_sites                     
        if True in self.atoms.pbc:                                      
            sac = SlabAdsorbateCoverage(self.atoms, sas, dmax=self.dmax,
                                        label_occupied_sites=self.unique) 
        else: 
            sac = ClusterAdsorbateCoverage(self.atoms, sas, dmax=self.dmax,
                                           label_occupied_sites=self.unique)
        hsl = sac.hetero_site_list
        occupied_stids = [i for i in range(len(hsl)) if hsl[i]['occupied']]
        if not occupied_stids:
            if self.logfile is not None:
                self.logfile.write('There is no occupied site. Replacement failed!\n')
                self.logfile.flush()
            return

        rpsti = random.choice(occupied_stids)
        rpst = hsl[rpsti]
        rm_frag = rpst['fragment'] in self.adsorbate_species 
        remove_adsorbate_from_site(self.atoms, rpst, remove_fragment=rm_frag)

        # Select a different adsorbate with probability 
        old_adsorbate = rpst['adsorbate']
        new_options = [a for a in self.adsorbate_species if a != old_adsorbate]

        if self.species_forbidden_labels is not None:
            _new_options = []
            for o in new_options:
                if o in self.species_forbidden_labels: 
                    if True in self.atoms.pbc:
                        if sas.composition_effect:
                            signature = [rpst['site'], rpst['morphology'], 
                                         rpst['composition']]
                        else:
                            signature = [rpst['site'], rpst['morphology']]
                        lab = sas.label_dict['|'.join(signature)]                        
                                                                                                 
                    else:
                        if sas.composition_effect:
                            signature = [rpst['site'], rpst['surface'], 
                                         rpst['composition']]
                        else:
                            signature = [rpst['site'], rpst['surface']]
                        lab = sas.label_dict['|'.join(signature)]                                                                                            
                    if lab not in self.species_forbidden_labels[o]:
                        _new_options.append(o)
            new_options = _new_options                                                       

        elif self.species_forbidden_sites is not None:                      
            _new_options = []
            for o in new_options: 
                if o in self.species_forbidden_sites:
                    if rpst['site'] not in self.species_forbidden_sites[o]:
                        _new_options.append(o)
            new_options = _new_options

        # Prohibit adsorbates with more than 1 atom from entering subsurf 6-fold sites
        if self.allow_6fold and rpst['site'] == '6fold':
            new_options = [o for o in new_options if len(o) == 1]

        if self.species_probabilities is None:
            adsorbate = random.choice(new_options)
        else:
            new_probabilities = [self.species_probabilities[a] for a in new_options]
            adsorbate = random.choices(k=1, population=self.adsorbate_species,
                                       weights=new_probabilities)[0] 
        if self.adsorption_sites is not None:
            site_nblist = self.site_nblist
        else:
            site_nblist = sas.get_neighbor_site_list(neighbor_number=2)

        nbstids, selfids = [], []
        for j, st in enumerate(hsl):
            if st['occupied']:
                nbstids += site_nblist[j]
                selfids.append(j)
        nbstids = set(nbstids)
        neighbor_site_indices = [v for v in nbstids if v not in selfids]

        if adsorbate in self.multidentate_adsorbates:
            if self.adsorption_sites is not None:                                      
                bidentate_nblist = self.bidentate_nblist
            else:
                bidentate_nblist = sas.get_neighbor_site_list(neighbor_number=1)
            
            binbs = bidentate_nblist[rpsti]                    
            binbids = [n for n in binbs if n not in nbstids]
            if not binbids:
                if self.logfile is not None:
                    self.logfile.write('Not enough space to add {} '.format(adsorbate)  
                                       + 'to any site. Replacement failed!\n')
                    self.logfile.flush()
                return
                                                                                            
            # Rotate a bidentate adsorbate to the direction of a randomly 
            # choosed neighbor site
            nbst = hsl[random.choice(binbids)]
            pos = rpst['position'] 
            nbpos = nbst['position'] 
            orientation = get_mic(nbpos, pos, self.atoms.cell)
            add_adsorbate_to_site(self.atoms, adsorbate, rpst, 
                                  height=self.heights[rpst['site']],
                                  orientation=orientation)                     
        else:
            add_adsorbate_to_site(self.atoms, adsorbate, rpst,
                                  height=self.heights[rpst['site']])                 
 
        if True in self.atoms.pbc:   
            nsac = SlabAdsorbateCoverage(self.atoms, sas, dmax=self.dmax,
                                         label_occupied_sites=self.unique) 
        else: 
            nsac = ClusterAdsorbateCoverage(self.atoms, sas, dmax=self.dmax,
                                            label_occupied_sites=self.unique)         
        nhsl = nsac.hetero_site_list                            
                                                                           
        # Make sure there is no new site too close to previous sites after 
        # the action. Useful when adding large molecules
        if any(s for i, s in enumerate(nhsl) if s['occupied'] and (i in 
        neighbor_site_indices)):
            if self.logfile is not None:
                self.logfile.write('The added {} is too close '.format(adsorbate)
                                   + 'to another adsorbate. Replacement failed!\n')
                self.logfile.flush()
            return
        ads_atoms = self.atoms[[a.index for a in self.atoms if                   
                                a.symbol in adsorbate_elements]]
        if atoms_too_close_after_addition(ads_atoms, len(list(Formula(adsorbate))), 
        self.min_adsorbate_distance, mic=(True in self.atoms.pbc)):
            if self.logfile is not None:
                self.logfile.write('The added {} is too close '.format(adsorbate)
                                   + 'to another adsorbate. Replacement failed!\n')
                self.logfile.flush()
            return

        return nsac                        
 
    def run(self, num_gen, 
            action='add', 
            action_probabilities=None,
            num_act=1,
            add_species_composition=None,
            unique=True,
            site_preference=None,
            subsurf_effect=False):
        """Run the pattern generator.

        Parameters
        ----------
        num_gen : int
            Number of patterns to generate.

        action : str or list of strs, default 'add'
            Action(s) to perform. If a list of actions is provided, select
            actions from the list randomly or with probabilities.

        action_probabilities : dict, default None
            A dictionary that contains keys of each action and values of the 
            corresponding probabilities. Select actions with equal probability 
            if not specified.

        num_act : int, default 1
            Number of times performed for each action. Useful for operating
            more than one adsorbates at a time. This becomes extremely slow
            when adding many adsorbates to generate high coverage patterns. 
            The recommended ways to generate high coverage patterns are:
            1) adding one adsorbate at a time from low to high coverage if 
            you want to control the exact number of adsorbates;
            2) use `acat.build.adlayer.random_coverage_pattern` if you want
            to control the minimum adsorbate distance. This is the fastest
            way, but the number of adsorbates is not guaranteed to be fixed.

        add_species_composition : dict, default None
            A dictionary that contains keys of each adsorbate species and 
            values of the species composition to be added onto the surface.
            Adding adsorbate species according to species_probabilities if 
            not specified. Please only use this if the action is 'add'.

        unique : bool, default True 
            Whether to discard duplicate patterns based on graph isomorphism.

        site_preference : str of list of strs, defualt None
            The site type(s) that has higher priority to attach adsorbates.

        subsurf_effect : bool, default False
            Whether to take subsurface atoms into consideration when checking 
            uniqueness. Could be important for surfaces like fcc100.

        """
 
        mode = 'a' if self.append_trajectory else 'w'
        self.traj = Trajectory(self.trajectory, mode=mode)
        actions = action if is_list_or_tuple(action) else [action]
        if action_probabilities is not None:
            all_action_probabilities = [action_probabilities[a] for a in actions]
        self.num_act = num_act
        if add_species_composition is not None:
            ks = list(add_species_composition.keys())
            ratios = list(add_species_composition.values())
            nums = numbers_from_ratios(num_act, ratios)
            adsorbates_to_add = [ads for k, n in zip(ks, nums) for ads in [k]*n] 
        self.add_species_composition = add_species_composition

        self.labels_list, self.graph_list = [], []
        self.unique = unique
        self.subsurf_effect = subsurf_effect
        if len(self.traj) > 0 and self.unique and self.append_trajectory:                                 
            if self.logfile is not None:                             
                self.logfile.write('Loading graphs for existing structures in ' +
                                   '{}. This might take a while.\n'.format(self.trajectory))
                self.logfile.flush()

            prev_images = read(self.trajectory, index=':')
            for patoms in prev_images:
                if self.adsorption_sites is not None:
                    psas = self.adsorption_sites
                elif True in patoms.pbc:
                    if self.surface is None:
                        raise ValueError('please specify the surface type')
                    psas = SlabAdsorptionSites(patoms, **self.kwargs)
                else:
                    psas = ClusterAdsorptionSites(patoms, **self.kwargs) 
                if True in patoms.pbc:
                    psac = SlabAdsorbateCoverage(patoms, psas, dmax=self.dmax,
                                                 label_occupied_sites=self.unique)           
                else:
                    psac = ClusterAdsorbateCoverage(patoms, psas, dmax=self.dmax,
                                                    label_occupied_sites=self.unique)        

                plabs = psac.get_occupied_labels(fragmentation=self.fragmentation)
                pG = psac.get_graph(fragmentation=self.fragmentation,
                                    subsurf_effect=self.subsurf_effect)
                self.labels_list.append(plabs)
                self.graph_list.append(pG)

        n_new = 0
        n_old = 0
        # Start the iteration
        while n_new < num_gen:
            if self.add_species_composition is not None:
                self.adsorbates_to_add = adsorbates_to_add.copy()

            if n_old == n_new:
                if self.logfile is not None:                                    
                    self.logfile.write('Generating pattern {}\n'.format(n_new))
                    self.logfile.flush()
                n_old += 1
            # Select image with probability 
            if self.species_probabilities is None:
                self.atoms = random.choice(self.images).copy()
            else: 
                self.atoms = random.choices(k=1, population=self.images, 
                                            weights=self.image_probabilities)[0].copy()
            self.n_image = n_new 

            if self.adsorption_sites is not None:
                sas = self.adsorption_sites
            elif True in self.atoms.pbc:
                if self.surface is None:
                    raise ValueError('please specify the surface type')
                sas = SlabAdsorptionSites(self.atoms, **self.kwargs)
            else:
                sas = ClusterAdsorptionSites(self.atoms, **self.kwargs)      
            if site_preference is not None:                                              
                if not is_list_or_tuple(site_preference):
                    site_preference = [site_preference]
                sas.site_list.sort(key=lambda x: x['site'] in site_preference, reverse=True)

            # Choose an action 
            self.clean_slab = False
            n_slab = len(sas.indices) 
            if n_slab == len(self.atoms):
                if 'add' not in actions:                                                             
                    warnings.warn("There is no adsorbate in image {}. ".format(n_new)
                                  + "The only available action is 'add'")
                    continue 
                else:
                    action = 'add'
                    self.clean_slab = True
            else:
                if not action_probabilities:
                    action = random.choice(actions)
                else:
                    assert len(action_probabilities.keys()) == len(actions)
                    action = random.choices(k=1, population=actions, 
                                            weights=all_action_probabilities)[0] 
            if self.logfile is not None:                                    
                self.logfile.write('Action: {0} x {1}\n'.format(action, self.num_act))
                self.logfile.flush()

            if action == 'add':
                for _ in range(self.num_act):             
                    nsac = self._add_adsorbate(sas)
                    if not nsac:
                        break
            elif action == 'remove':
                for _ in range(self.num_act):             
                    nsac = self._remove_adsorbate(sas)
                    if not nsac:
                        break
            elif action == 'move':
                for _ in range(self.num_act):             
                    nsac = self._move_adsorbate(sas)
                    if not nsac:
                        break
            elif action == 'replace':
                for _ in range(self.num_act):             
                    nsac = self._replace_adsorbate(sas)
                    if not nsac:
                        break
            if not nsac:
                continue

            labs = nsac.get_occupied_labels(fragmentation=self.fragmentation)
            if self.unique: 
                if labs in self.labels_list: 
                    G = nsac.get_graph(fragmentation=self.fragmentation,
                                       subsurf_effect=self.subsurf_effect)
                    if self.graph_list:
                        # Skip duplicates based on isomorphism 
                        nm = iso.categorical_node_match('symbol', 'X')
                        potential_graphs = [g for i, g in enumerate(self.graph_list) 
                                            if self.labels_list[i] == labs]
                        # If the surface slab is clean, the potentially isomorphic
                        # graphs are all isomorphic. However, when considering subsurf
                        # effect, graph isomorphism should still be checked.
                        if self.clean_slab and potential_graphs and self.num_act == 1 \
                        and not self.subsurf_effect:
                            if self.logfile is not None:                              
                                self.logfile.write('Duplicate found by label match. '
                                                   + 'Discarded!\n')
                                self.logfile.flush()
                            continue
                        if any(H for H in potential_graphs if 
                        nx.isomorphism.is_isomorphic(G, H, node_match=nm)):
                            if self.logfile is not None:                             
                                self.logfile.write('Duplicate found by isomorphism. '
                                                   + 'Discarded!\n')
                                self.logfile.flush()
                            continue
                    self.graph_list.append(G)                                          
                self.labels_list.append(labs)                

            if self.logfile is not None:
                self.logfile.write('Succeed! Pattern generated: {}\n\n'.format(labs))
                self.logfile.flush()
            if 'data' not in self.atoms.info:
                self.atoms.info['data'] = {}
            self.atoms.info['data']['labels'] = labs
            self.traj.write(self.atoms)            
            n_new += 1


class SystematicPatternGenerator(object):
    """`SystematicPatternGenerator` is a class for generating 
    adsorbate overlayer patterns systematically. This is useful to 
    enumerate all unique patterns at low coverage, but explodes at
    higher coverages. Graph isomorphism is implemented to identify 
    identical adlayer patterns. 4 adsorbate actions are supported: 
    add, remove, move, replace. The class is generalized for both
    periodic and non-periodic systems (distinguished by atoms.pbc). 

    Parameters
    ----------
    images : ase.Atoms object or list of ase.Atoms objects

        The structure to perform the adsorbate actions on. 
        If a list of structures is provided, perform one 
        adsorbate action on one of the structures in each step. 
        Accept any ase.Atoms object. No need to be built-in.

    adsorbate_species : str or list of strs 
        A list of adsorbate species to be randomly added to the surface.

    min_adsorbate_distance : float, default 1.5
        The minimum distance constraint between two atoms that belongs 
        to two adsorbates.

    adsorption_sites : acat.adsorption_sites.ClusterAdsorptionSites object \
        or acat.adsorption_sites.SlabAdsorptionSites object, default None
        Provide the built-in adsorption sites class to accelerate the 
        pattern generation. Make sure all the structures have the same 
        periodicity and atom indexing. If composition_effect=True, you 
        should only provide adsorption_sites when the surface composition 
        is fixed. If this is not provided, the arguments for identifying
        adsorption sites can still be passed in by **kwargs.

    heights : dict, default acat.settings.site_heights
        A dictionary that contains the adsorbate height for each site 
        type. Use the default height settings if the height for a site 
        type is not specified.

    dmax : float, default 3.
        The maximum bond length (in Angstrom) between the site and the 
        bonding atom that should be considered as an adsorbate.       

    species_forbidden_sites : dict, default None
        A dictionary that contains keys of each adsorbate species and 
        values of the site (can be one or multiple site types) that the 
        speices is not allowed to add to. All sites are availabe for a
        species if not specified. Note that this does not differentiate
        sites with different compositions.

    species_forbidden_labels : dict, default None
        Same as species_forbidden_sites except that the adsorption sites
        are written as numerical labels according to acat.labels. Useful
        when you need to differentiate sites with different compositions.

    enumerate_orientations: bool, default True
        Whether to enumerate all orientations of multidentate species.
        This ensures that multidentate species with different orientations 
        are all enumerated.

    trajectory : str, default 'patterns.traj'
        The name of the output ase trajectory file.

    append_trajectory : bool, default False
        Whether to append structures to the existing trajectory. 
        If only unique patterns are accepted, the code will also check 
        graph isomorphism for the existing structures in the trajectory.

    logfile : str, default 'patterns.log'
        The name of the log file.

    """

    def __init__(self, images,                                                     
                 adsorbate_species,
                 min_adsorbate_distance=1.5,
                 adsorption_sites=None,
                 heights=site_heights,
                 dmax=3.,
                 species_forbidden_sites=None,
                 species_forbidden_labels=None,
                 enumerate_orientations=True,
                 trajectory='patterns.traj',
                 append_trajectory=False,
                 logfile='patterns.log', 
                 **kwargs):

        self.images = images if is_list_or_tuple(images) else [images]                     
        self.adsorbate_species = adsorbate_species if is_list_or_tuple(
                                 adsorbate_species) else [adsorbate_species]
        self.monodentate_adsorbates = [s for s in self.adsorbate_species if s in 
                                       monodentate_adsorbate_list]
        self.multidentate_adsorbates = [s for s in self.adsorbate_species if s in
                                        multidentate_adsorbate_list]
        if len(self.adsorbate_species) != len(self.monodentate_adsorbates +
        self.multidentate_adsorbates):
            diff = list(set(self.adsorbate_species) - 
                        set(self.monodentate_adsorbates +
                            self.multidentate_adsorbates))
            raise ValueError('species {} is not defined '.format(diff) +
                             'in adsorbate_list in acat.settings')             

        self.min_adsorbate_distance = min_adsorbate_distance
        self.adsorption_sites = adsorption_sites
        self.heights = site_heights 
        for k, v in heights.items():
            self.heights[k] = v
        self.dmax = dmax
        self.kwargs = {'allow_6fold': False, 'composition_effect': False,
                       'ignore_bridge_sites': False, 'label_sites': False} 
        self.kwargs.update(kwargs)
        if self.adsorption_sites is not None:
            for k in self.kwargs.keys():             
                self.kwargs[k] = attrgetter(k)(self.adsorption_sites)
        self.__dict__.update(self.kwargs)
        self.species_forbidden_sites = species_forbidden_sites
        self.species_forbidden_labels = species_forbidden_labels
                                                                                           
        if self.species_forbidden_labels is not None:
            self.species_forbidden_labels = {k: v if is_list_or_tuple(v) else [v] for
                                             k, v in self.species_forbidden_labels.items()}
        if self.species_forbidden_sites is not None:
            self.species_forbidden_sites = {k: v if is_list_or_tuple(v) else [v] for
                                            k, v in self.species_forbidden_sites.items()}
        self.enumerate_orientations = enumerate_orientations
        if isinstance(trajectory, str):
            self.trajectory = trajectory                        
        self.append_trajectory = append_trajectory
        if isinstance(logfile, str):
            self.logfile = open(logfile, 'a')                 
 
        if self.adsorption_sites is not None:
            if self.multidentate_adsorbates:
                self.bidentate_nblist = \
                self.adsorption_sites.get_neighbor_site_list(neighbor_number=1)
            self.site_nblist = \
            self.adsorption_sites.get_neighbor_site_list(neighbor_number=2)

    def _exhaustive_add_adsorbate(self, atoms, adsorption_sites):
        if self.add_species_composition is not None:
            adsorbate_species = [self.adsorbates_to_add[self.act_count]]
        else:
            adsorbate_species = self.adsorbate_species

        self.n_duplicate = 0        
        sas = adsorption_sites
        if self.adsorption_sites is not None:                                         
            site_nblist = self.site_nblist
        else:
            site_nblist = sas.get_neighbor_site_list(neighbor_number=2) 
       
        # Take care of clean surface slab
        if self.clean_slab:
            hsl = sas.site_list
            nbstids = set()    
            neighbor_site_indices = []        
        else:
            if True in atoms.pbc: 
                sac = SlabAdsorbateCoverage(atoms, sas, dmax=self.dmax,
                                            label_occupied_sites=self.unique) 
            else: 
                sac = ClusterAdsorbateCoverage(atoms, sas, dmax=self.dmax,
                                               label_occupied_sites=self.unique)
            hsl = sac.hetero_site_list
            nbstids, selfids = [], []
            for j, st in enumerate(hsl):
                if st['occupied']:
                    nbstids += site_nblist[j]
                    selfids.append(j)
            nbstids = set(nbstids)
            neighbor_site_indices = [v for v in nbstids if v not in selfids]

        if self.multidentate_adsorbates:
            if self.adsorption_sites is not None:
                bidentate_nblist = self.bidentate_nblist
            else:
                bidentate_nblist = sas.get_neighbor_site_list(neighbor_number=1)

        # Only add one adsorbate to a site at least 2 shells away from
        # currently occupied sites
        newsites, binbids = [], []
        for i, s in enumerate(hsl):
            if i not in nbstids:
                if self.multidentate_adsorbates:
                    binbs = bidentate_nblist[i]
                    binbis = [n for n in binbs if n not in nbstids]
                    if not binbis and s['site'] != '6fold':
                        continue 
                    binbids.append(binbis)
                newsites.append(s)

        for k, nst in enumerate(newsites):
            for adsorbate in adsorbate_species:
                if self.species_forbidden_labels is not None:
                    if adsorbate in self.species_forbidden_labels: 
                        if True in atoms.pbc:
                            if sas.composition_effect:
                                signature = [nst['site'], nst['morphology'], 
                                             nst['composition']]
                            else:
                                signature = [nst['site'], nst['morphology']]
                            lab = sas.label_dict['|'.join(signature)]                        
                        else:
                            if sas.composition_effect:
                                signature = [nst['site'], nst['surface'], 
                                             nst['composition']]
                            else:
                                signature = [nst['site'], nst['surface']]
                            lab = sas.label_dict['|'.join(signature)]
                        if lab in self.species_forbidden_labels[adsorbate]:
                            continue                                                                             
                                                                                                     
                elif self.species_forbidden_sites is not None:                          
                    if adsorbate in self.species_forbidden_sites:
                        if nst['site'] in self.species_forbidden_sites[adsorbate]:
                            continue

                if adsorbate in self.multidentate_adsorbates:                                     
                    nis = binbids[k]
                    if not self.enumerate_orientations:
                        nis = [random.choice(nis)]
                else:
                    nis = [0]
                for ni in nis:
                    # Prohibit adsorbates with more than 1 atom from entering subsurf sites
                    if len(adsorbate) > 1 and nst['site'] == '6fold':
                        continue
 
                    final_atoms = atoms.copy()
                    if adsorbate in self.multidentate_adsorbates:
                        # Rotate a multidentate adsorbate to all possible directions of
                        # a neighbor site
                        nbst = hsl[ni]
                        pos = nst['position'] 
                        nbpos = nbst['position'] 
                        orientation = get_mic(nbpos, pos, final_atoms.cell)
                        add_adsorbate_to_site(final_atoms, adsorbate, nst, 
                                              height=self.heights[nst['site']],
                                              orientation=orientation)        
  
                    else:
                        add_adsorbate_to_site(final_atoms, adsorbate, nst,
                                              height=self.heights[nst['site']])        
 
                    if True in final_atoms.pbc:
                        nsac = SlabAdsorbateCoverage(final_atoms, sas, dmax=self.dmax,
                                                     label_occupied_sites=self.unique) 
                    else: 
                        nsac = ClusterAdsorbateCoverage(final_atoms, sas, dmax=self.dmax,
                                                        label_occupied_sites=self.unique)
                    nhsl = nsac.hetero_site_list
  
                    # Make sure there is no new site too close to previous sites after 
                    # adding the adsorbate. Useful when adding large molecules
                    if any(s for i, s in enumerate(nhsl) if s['occupied'] and (i in 
                    neighbor_site_indices)):
                        continue
                    ads_atoms = final_atoms[[a.index for a in final_atoms if                   
                                             a.symbol in adsorbate_elements]]
                    if atoms_too_close_after_addition(ads_atoms, len(list(Formula(
                    adsorbate))), self.min_adsorbate_distance, mic=(True in final_atoms.pbc)):
                        continue

                    self.act_count += 1
                    if self.act_count < self.num_act:                        
                        self._exhaustive_add_adsorbate(final_atoms, sas)
                    self.act_count -= 1
                    if self.exit:
                        return

                    labs = nsac.get_occupied_labels(fragmentation=self.enumerate_orientations)
                    if self.unique:                                        
                        if labs in self.labels_list: 
                            G = nsac.get_graph(fragmentation=self.enumerate_orientations,
                                               subsurf_effect=self.subsurf_effect)
                            if self.graph_list:
                                # Skip duplicates based on isomorphism 
                                potential_graphs = [g for i, g in enumerate(self.graph_list)
                                                    if self.labels_list[i] == labs]
                                # If the surface slab is clean, the potentially isomorphic
                                # graphs are all isomorphic. However, when considering subsurf
                                # effect, graph isomorphism should still be checked.
                                if self.clean_slab and potential_graphs and self.num_act == 1 \
                                and not self.subsurf_effect:
                                    self.n_duplicate += 1
                                    continue
                                nm = iso.categorical_node_match('symbol', 'X')
                                if any(H for H in potential_graphs if 
                                nx.isomorphism.is_isomorphic(G, H, node_match=nm)):
                                    self.n_duplicate += 1
                                    continue

                            self.graph_list.append(G)                                       
                        self.labels_list.append(labs)

                    if self.logfile is not None:                                
                        self.logfile.write('Succeed! Pattern {} '.format(self.n_write)
                                           + 'generated: {}\n'.format(labs))
                        self.logfile.flush()
                    if 'data' not in final_atoms.info:
                        final_atoms.info['data'] = {}
                    final_atoms.info['data']['labels'] = labs
                    self.traj.write(final_atoms)
                    self.n_write += 1
                    self.n_write_per_image += 1
                    if self.max_gen_per_image is not None:
                        if self.n_write_per_image == self.max_gen_per_image:
                            self.exit = True
                            return 

    def _exhaustive_remove_adsorbate(self, atoms, adsorption_sites):
        self.n_duplicate = 0                                                           
        sas = adsorption_sites
        if True in atoms.pbc:
            sac = SlabAdsorbateCoverage(atoms, sas, dmax=self.dmax,
                                        label_occupied_sites=self.unique) 
        else: 
            sac = ClusterAdsorbateCoverage(atoms, sas, dmax=self.dmax,
                                           label_occupied_sites=self.unique)
        hsl = sac.hetero_site_list
        occupied = [s for s in hsl if s['occupied']]
        if not occupied:
            if self.logfile is not None:
                self.logfile.write('There is no occupied site. Removal failed!\n')
                self.logfile.flush()
            return

        rm_ids = set()
        for rmst in occupied:
            ads_ids = set(rmst['adsorbate_indices'])
            # Make sure the same adsorbate is not removed twice
            if ads_ids.issubset(rm_ids):
                continue
            rm_ids.update(ads_ids)                
            final_atoms = atoms.copy()
            rm_frag = rmst['fragment'] in self.adsorbate_species 
            remove_adsorbate_from_site(final_atoms, rmst, remove_fragment=rm_frag)

            ads_remain = [a for a in final_atoms if a.symbol in adsorbate_elements]
            if not ads_remain:
                if self.logfile is not None:
                    self.logfile.write('Last adsorbate has been removed ' + 
                                       'from image {}\n'.format(self.n_image))
                    self.logfile.flush()
                if 'data' not in final_atoms.info:
                    final_atoms.info['data'] = {}
                final_atoms.info['data']['labels'] = []
                self.trajectory.write(final_atoms)
                return

            self.act_count += 1
            if self.act_count < self.num_act:
                self._exhaustive_remove_adsorbate(final_atoms, sas)
            self.act_count -= 1
            if self.exit:
                return
                                                      
            if True in final_atoms.pbc:                                
                nsac = SlabAdsorbateCoverage(final_atoms, sas, dmax=self.dmax,
                                             label_occupied_sites=self.unique) 
            else: 
                nsac = ClusterAdsorbateCoverage(final_atoms, sas, dmax=self.dmax,
                                                label_occupied_sites=self.unique)

            labs = nsac.get_occupied_labels(fragmentation=self.enumerate_orientations)
            if self.unique:                                        
                if labs in self.labels_list: 
                    G = nsac.get_graph(fragmentation=self.enumerate_orientations,
                                       subsurf_effect=self.subsurf_effect)
                    if self.graph_list:
                        # Skip duplicates based on isomorphism 
                        potential_graphs = [g for i, g in enumerate(self.graph_list)
                                            if self.labels_list[i] == labs]
                        nm = iso.categorical_node_match('symbol', 'X')
                        if any(H for H in potential_graphs if 
                        nx.isomorphism.is_isomorphic(G, H, node_match=nm)):
                            self.n_duplicate += 1
                            continue            

                    self.graph_list.append(G)                                       
                self.labels_list.append(labs)

            if self.logfile is not None:                                
                self.logfile.write('Succeed! Pattern {} '.format(self.n_write)
                                   + 'generated: {}\n'.format(labs))
                self.logfile.flush()
            if 'data' not in final_atoms.info:
                final_atoms.info['data'] = {}
            final_atoms.info['data']['labels'] = labs
            self.traj.write(final_atoms)
            self.n_write += 1
            self.n_write_per_image += 1
            if self.max_gen_per_image is not None:
                if self.n_write_per_image == self.max_gen_per_image:
                    self.exit = True
                    return

    def _exhaustive_move_adsorbate(self, atoms, adsorption_sites): 
        self.n_duplicate = 0                                                           
        sas = adsorption_sites                      
        if self.adsorption_sites is not None:                            
            site_nblist = self.site_nblist
        else:
            site_nblist = sas.get_neighbor_site_list(neighbor_number=2) 

        if True in atoms.pbc:  
            sac = SlabAdsorbateCoverage(atoms, sas, dmax=self.dmax,
                                        label_occupied_sites=self.unique) 
        else: 
            sac = ClusterAdsorbateCoverage(atoms, sas, dmax=self.dmax,
                                           label_occupied_sites=self.unique)
        hsl = sac.hetero_site_list
        nbstids, selfids, occupied = [], [], []
        for j, st in enumerate(hsl):
            if st['occupied']:
                nbstids += site_nblist[j]
                selfids.append(j)
                occupied.append(st)
        if not occupied:                                                       
            if self.logfile is not None:
                self.logfile.write('There is no occupied site. Move failed!\n')
                self.logfile.flush()
            return
        nbstids = set(nbstids)
        neighbor_site_indices = [v for v in nbstids if v not in selfids]

        rm_ids = set()
        for st in occupied:
            ads_ids = set(st['adsorbate_indices'])
            # Make sure the same adsorbate is not removed twice
            if ads_ids.issubset(rm_ids):
                continue
            rm_ids.update(ads_ids)                              
            test_atoms = atoms.copy()
            rm_frag = st['fragment'] in self.adsorbate_species
            remove_adsorbate_from_site(test_atoms, st, remove_fragment=rm_frag)

            adsorbate = st['adsorbate']
            if adsorbate in self.multidentate_adsorbates:
                if self.adsorption_sites is not None:
                    bidentate_nblist = self.bidentate_nblist
                else:
                    bidentate_nblist = sas.get_neighbor_site_list(neighbor_number=1)
 
            # Only add one adsorabte to a site at least 2 shells away from
            # currently occupied sites
            newsites, binbids = [], []
            for i, s in enumerate(hsl):
                if i not in nbstids:
                    if adsorbate in self.multidentate_adsorbates:
                        binbs = bidentate_nblist[i]
                        binbis = [n for n in binbs if n not in nbstids]
                        if not binbis and s['site'] != '6fold':
                            continue 
                        binbids.append(binbis)
                    newsites.append(s)
 
            for k, nst in enumerate(newsites):
                if self.species_forbidden_labels is not None:
                    if adsorbate in self.species_forbidden_labels: 
                        if True in test_atoms.pbc:
                            if sas.composition_effect:
                                signature = [nst['site'], nst['morphology'], 
                                             nst['composition']]
                            else:
                                signature = [nst['site'], nst['morphology']]
                            lab = sas.label_dict['|'.join(signature)]                        
                        else:
                            if sas.composition_effect:
                                signature = [nst['site'], nst['surface'], 
                                             nst['composition']]
                            else:
                                signature = [nst['site'], nst['surface']]
                            lab = sas.label_dict['|'.join(signature)]
                        if lab in self.species_forbidden_labels[adsorbate]:
                            continue                                                          

                elif self.species_forbidden_sites is not None:                          
                    if adsorbate in self.species_forbidden_sites:
                        if nst['site'] in self.species_forbidden_sites[adsorbate]:
                            continue

                if adsorbate in self.multidentate_adsorbates:
                    nis = binbids[k]
                    if not self.enumerate_orientations:
                        nis = [random.choice(nis)]
                else:
                    nis = [0]
                for ni in nis:
                    # Prohibit adsorbates with more than 1 atom from entering subsurf 
                    if len(adsorbate) > 1 and nst['site'] == '6fold':
                        continue

                    final_atoms = test_atoms.copy()  
                    if adsorbate in self.multidentate_adsorbates:                     
                        # Rotate a multidentate adsorbate to all possible directions of
                        # a neighbor site
                        nbst = hsl[ni]
                        pos = nst['position'] 
                        nbpos = nbst['position'] 
                        orientation = get_mic(nbpos, pos, final_atoms.cell)
                        add_adsorbate_to_site(final_atoms, adsorbate, nst, 
                                              height=self.heights[nst['site']],
                                              orientation=orientation)        
      
                    else:
                        add_adsorbate_to_site(final_atoms, adsorbate, nst,
                                              height=self.heights[nst['site']])       

                    if True in final_atoms.pbc:   
                        nsac = SlabAdsorbateCoverage(final_atoms, sas, dmax=self.dmax,
                                                     label_occupied_sites=self.unique) 
                    else: 
                        nsac = ClusterAdsorbateCoverage(final_atoms, sas, dmax=self.dmax,
                                                        label_occupied_sites=self.unique)
                    nhsl = nsac.hetero_site_list
      
                    # Make sure there is no new site too close to previous sites after 
                    # adding the adsorbate. Useful when adding large molecules
                    if any(s for i, s in enumerate(nhsl) if s['occupied'] and (i in 
                    neighbor_site_indices)):
                        continue
                    ads_atoms = final_atoms[[a.index for a in final_atoms if                   
                                             a.symbol in adsorbate_elements]]
                    if atoms_too_close_after_addition(ads_atoms, len(list(Formula(adsorbate))),
                    self.min_adsorbate_distance, mic=(True in final_atoms.pbc)):
                        continue                                                                                   

                    self.act_count += 1
                    if self.act_count < self.num_act:
                        self._exhaustive_move_adsorbate(final_atoms, sas)
                    self.act_count -= 1
                    if self.exit:
                        return

                    if True in final_atoms.pbc:
                        nsac = SlabAdsorbateCoverage(final_atoms, sas, dmax=self.dmax,
                                                     label_occupied_sites=self.unique) 
                    else: 
                        nsac = ClusterAdsorbateCoverage(final_atoms, sas, dmax=self.dmax,
                                                        label_occupied_sites=self.unique)                      
      
                    labs = nsac.get_occupied_labels(fragmentation=self.enumerate_orientations)
                    if self.unique:                                        
                        if labs in self.labels_list: 
                            G = nsac.get_graph(fragmentation=self.enumerate_orientations,
                                               subsurf_effect=self.subsurf_effect)
                            if self.graph_list:
                                # Skip duplicates based on isomorphism 
                                potential_graphs = [g for i, g in enumerate(self.graph_list)
                                                    if self.labels_list[i] == labs]
                                nm = iso.categorical_node_match('symbol', 'X')
                                if any(H for H in potential_graphs if 
                                nx.isomorphism.is_isomorphic(G, H, node_match=nm)):
                                    self.n_duplicate += 1
                                    continue            

                            self.graph_list.append(G)                                       
                        self.labels_list.append(labs)
                                                                                             
                    if self.logfile is not None:                                
                        self.logfile.write('Succeed! Pattern {} '.format(self.n_write)
                                           + 'generated: {}\n'.format(labs))
                        self.logfile.flush()
                    if 'data' not in final_atoms.info:
                        final_atoms.info['data'] = {}
                    final_atoms.info['data']['labels'] = labs
                    self.traj.write(final_atoms)
                    self.n_write += 1
                    self.n_write_per_image += 1
                    if self.max_gen_per_image is not None:
                        if self.n_write_per_image == self.max_gen_per_image:
                            self.exit = True
                            return

    def _exhaustive_replace_adsorbate(self, atoms, adsorption_sites):
        sas = adsorption_sites
        if True in atoms.pbc:                                                           
            sac = SlabAdsorbateCoverage(atoms, sas, dmax=self.dmax,
                                        label_occupied_sites=self.unique)
        else: 
            sac = ClusterAdsorbateCoverage(atoms, sas, dmax=self.dmax,
                                           label_occupied_sites=self.unique)
        hsl = sac.hetero_site_list
        occupied_stids = [i for i in range(len(hsl)) if hsl[i]['occupied']]
        if not occupied_stids:
            if self.logfile is not None:
                self.logfile.write('There is no occupied site. Replacement failed!\n')
                self.logfile.flush()
            return
                                
        rm_ids = set()
        for rpsti in occupied_stids:                                                         
            rpst = hsl[rpsti]
            ads_ids = set(rpst['adsorbate_indices'])
            # Make sure the same adsorbate is not removed twice
            if ads_ids.issubset(rm_ids):
                continue
            rm_ids.update(ads_ids)                             
            test_atoms = atoms.copy()
            rm_frag = rpst['fragment'] in self.adsorbate_species  
            remove_adsorbate_from_site(test_atoms, rpst, remove_fragment=rm_frag)
                                                                                             
            # Select a different adsorbate with probability 
            old_adsorbate = rpst['adsorbate']
            new_options = [a for a in self.adsorbate_species if a != old_adsorbate]

            if self.species_forbidden_labels is not None:
                _new_options = []
                for o in new_options:
                    if o in self.species_forbidden_labels: 
                        if True in test_atoms.pbc:
                            if sas.composition_effect:
                                signature = [rpst['site'], rpst['morphology'], 
                                             rpst['composition']]
                            else:
                                signature = [rpst['site'], rpst['morphology']]
                            lab = sas.label_dict['|'.join(signature)]                        
                                                                                                 
                        else:
                            if sas.composition_effect:
                                signature = [rpst['site'], rpst['surface'], 
                                             rpst['composition']]
                            else:
                                signature = [rpst['site'], rpst['surface']]
                            lab = sas.label_dict['|'.join(signature)]                            
                        if lab not in self.species_forbidden_labels[o] :
                            _new_options.append(o)
                new_options = _new_options                                                       

            elif self.species_forbidden_sites is not None:                      
                _new_options = []
                for o in new_options: 
                    if o in self.species_forbidden_sites:
                        if rpst['site'] not in self.species_forbidden_sites[o]:
                            _new_options.append(o)
                new_options = _new_options
                                                                                             
            # Prohibit adsorbates with more than 1 atom from entering subsurf 6-fold sites
            if self.allow_6fold and rpst['site'] == '6fold':
                new_options = [o for o in new_options if len(o) == 1]
                                                                                             
            for adsorbate in new_options:
                if self.adsorption_sites is not None:
                    site_nblist = self.site_nblist
                else:
                    site_nblist = sas.get_neighbor_site_list(neighbor_number=2)
                                                                                                 
                nbstids, selfids = [], []
                for j, st in enumerate(hsl):
                    if st['occupied']:
                        nbstids += site_nblist[j]
                        selfids.append(j)
                nbstids = set(nbstids)
                neighbor_site_indices = [v for v in nbstids if v not in selfids]
                                                                                                 
                if adsorbate in self.multidentate_adsorbates:                                     
                    if self.adsorption_sites is not None:                                      
                        bidentate_nblist = self.bidentate_nblist
                    else:
                        bidentate_nblist = sas.get_neighbor_site_list(neighbor_number=1)
                    
                    binbs = bidentate_nblist[rpsti]                    
                    binbids = [n for n in binbs if n not in nbstids]
                    if not binbids:
                        continue
                    nis = binbids[k]
                    if not self.enumerate_orientations:
                        nis = [random.choice(nis)]
                else:
                    nis = [0]
                for ni in nis:                                                                                  
                    final_atoms = test_atoms.copy()
                    if adsorbate in self.multidentate_adsorbates:
                        # Rotate a multidentate adsorbate to all possible directions of
                        # a neighbor site
                        nbst = hsl[ni]
                        pos = rpst['position'] 
                        nbpos = nbst['position'] 
                        orientation = get_mic(nbpos, pos, final_atoms.cell)
                        add_adsorbate_to_site(final_atoms, adsorbate, rpst, 
                                              height=self.heights[rpst['site']],
                                              orientation=orientation)        
                                                                                                  
                    else:
                        add_adsorbate_to_site(final_atoms, adsorbate, rpst,
                                              height=self.heights[rpst['site']])        

                    if True in final_atoms.pbc:                                                                              
                        nsac = SlabAdsorbateCoverage(final_atoms, sas, dmax=self.dmax,
                                                     label_occupied_sites=self.unique)
                    else: 
                        nsac = ClusterAdsorbateCoverage(final_atoms, sas, dmax=self.dmax,
                                                        label_occupied_sites=self.unique)
                    nhsl = nsac.hetero_site_list
                                                                                                  
                    # Make sure there is no new site too close to previous sites after 
                    # adding the adsorbate. Useful when adding large molecules
                    if any(s for i, s in enumerate(nhsl) if s['occupied'] and (i in 
                    neighbor_site_indices)):
                        continue
                    ads_atoms = final_atoms[[a.index for a in final_atoms if                   
                                             a.symbol in adsorbate_elements]]
                    if atoms_too_close_after_addition(ads_atoms, len(list(Formula(adsorbate))),  
                    self.min_adsorbate_distance, mic=(True in final_atoms.pbc)):
                        continue

                    self.act_count += 1
                    if self.act_count < self.num_act:
                        self._exhaustive_replace_adsorbate(final_atoms, sas)
                    self.act_count -= 1
                    if self.exit:
                        return

                    if True in final_atoms.pbc:
                        nsac = SlabAdsorbateCoverage(final_atoms, sas, dmax=self.dmax,
                                                     label_occupied_sites=self.unique) 
                    else: 
                        nsac = ClusterAdsorbateCoverage(final_atoms, sas, dmax=self.dmax,
                                                        label_occupied_sites=self.unique)                     
      
                    labs = nsac.get_occupied_labels(fragmentation=self.enumerate_orientations)                                                   
                    if self.unique:                                        
                        if labs in self.labels_list: 
                            G = nsac.get_graph(fragmentation=self.enumerate_orientations,
                                               subsurf_effect=self.subsurf_effect)
                            if self.graph_list:
                                # Skip duplicates based on isomorphism 
                                potential_graphs = [g for i, g in enumerate(self.graph_list)
                                                    if self.labels_list[i] == labs]
                                nm = iso.categorical_node_match('symbol', 'X')
                                if any(H for H in potential_graphs if 
                                nx.isomorphism.is_isomorphic(G, H, node_match=nm)):
                                    self.n_duplicate += 1
                                    continue            

                            self.graph_list.append(G)                                       
                        self.labels_list.append(labs)
                                                                                             
                    if self.logfile is not None:                                
                        self.logfile.write('Succeed! Pattern {} '.format(self.n_write)
                                           + 'generated: {}\n'.format(labs))
                        self.logfile.flush()
                    if 'data' not in final_atoms.info:
                        final_atoms.info['data'] = {}
                    final_atoms.info['data']['labels'] = labs
                    self.traj.write(final_atoms)
                    self.n_write += 1
                    self.n_write_per_image += 1
                    if self.max_gen_per_image is not None:
                        if self.n_write_per_image == self.max_gen_per_image:
                            self.exit = True
                            return

    def run(self, max_gen_per_image=None, 
            action='add',
            num_act=1, 
            add_species_composition=None,
            unique=True, 
            site_preference=None,
            subsurf_effect=False):
        """Run the pattern generator.

        Parameters
        ----------
        max_gen_per_image : int, default None
            Maximum number of patterns to generate for each image. Enumerate
            all possible patterns if not specified.

        action : str, defualt 'add'
            Action to perform.

        num_act : int, default 1
            Number of times performed for the action. Useful for operating
            more than one adsorbates at a time. This becomes extremely slow
            when adding many adsorbates to generate high coverage patterns. 
            The recommended way to generate high coverage patterns is to add 
            one adsorbate at a time from low to high coverage if you want to 
            control the exact number of adsorbates.

        add_species_composition : dict, default None
            A dictionary that contains keys of each adsorbate species and 
            values of the species composition to be added onto the surface.
            Adding all possible adsorbate species if not specified. Please 
            only use this if the action is 'add'.

        unique : bool, default True 
            Whether to discard duplicate patterns based on graph isomorphism.

        site_preference : str of list of strs, defualt None
            The site type(s) that has higher priority to attach adsorbates.

        subsurf_effect : bool, default False
            Whether to take subsurface atoms into consideration when checking 
            uniqueness. Could be important for surfaces like fcc100.

        """

        mode = 'a' if self.append_trajectory else 'w'
        self.traj = Trajectory(self.trajectory, mode=mode)          
        self.max_gen_per_image = max_gen_per_image
        self.num_act = num_act
        if add_species_composition is not None:
            ks = list(add_species_composition.keys())
            ratios = list(add_species_composition.values())
            nums = numbers_from_ratios(num_act, ratios)
            self.adsorbates_to_add = [ads for k, n in zip(ks, nums) for ads in [k]*n] 
        self.add_species_composition = add_species_composition        

        self.act_count = 0
        self.n_write = 0
        self.n_duplicate = 0
        self.exit = False

        self.labels_list, self.graph_list = [], []
        self.unique = unique
        self.subsurf_effect = subsurf_effect
        if len(self.traj) > 0 and self.unique and self.append_trajectory:                                 
            if self.logfile is not None:                             
                self.logfile.write('Loading graphs for existing structures in ' +
                                   '{}. This might take a while.\n'.format(self.trajectory))
                self.logfile.flush()
                                                                                   
            prev_images = read(self.trajectory, index=':')
            for patoms in prev_images:
                if self.adsorption_sites is not None:
                    psas = self.adsorption_sites
                elif True in patoms.pbc:
                    if self.surface is None:
                        raise ValueError('please specify the surface type')
                    psas = SlabAdsorptionSites(patoms, **self.kwargs)
                else:
                    psas = ClusterAdsorptionSites(patoms, **self.kwargs)      
                if True in patoms.pbc:
                    psac = SlabAdsorbateCoverage(patoms, psas, dmax=self.dmax,
                                                 label_occupied_sites=self.unique)      
                else:
                    psac = ClusterAdsorbateCoverage(patoms, psas, dmax=self.dmax,
                                                    label_occupied_sites=self.unique)        
                                                                                   
                plabs = psac.get_occupied_labels(fragmentation=self.enumerate_orientations)
                pG = psac.get_graph(fragmentation=self.enumerate_orientations,
                                    subsurf_effect=self.subsurf_effect)
                self.labels_list.append(plabs)
                self.graph_list.append(pG)

        for n, atoms in enumerate(self.images):
            self.n_write_per_image = 0
            if self.logfile is not None:                                   
                self.logfile.write('Generating all possible patterns '
                                   + 'for image {}\n'.format(n))
                self.logfile.flush()
            self.n_image = n
            self.atoms = atoms

            if self.adsorption_sites is not None:
                sas = self.adsorption_sites
            elif True in atoms.pbc:
                if self.surface is None:
                    raise ValueError('please specify the surface type')
                sas = SlabAdsorptionSites(atoms, **self.kwargs)
            else:
                sas = ClusterAdsorptionSites(atoms, **self.kwargs)     
            if site_preference is not None:                                              
                if not is_list_or_tuple(site_preference):
                    site_preference = [site_preference]
                sas.site_list.sort(key=lambda x: x['site'] in site_preference, reverse=True)

            self.clean_slab = False
            self.n_slab = len(sas.indices)
            if self.n_slab == len(atoms):
                if action != 'add':
                    warnings.warn("There is no adsorbate in image {}. ".format(n) 
                                  + "The only available action is 'add'")        
                    continue
                self.clean_slab = True

            if self.logfile is not None:                                    
                self.logfile.write('Action: {0} x {1}\n'.format(action, self.num_act))
                self.logfile.flush()

            if action == 'add':            
                self._exhaustive_add_adsorbate(atoms, sas)
            elif action == 'remove':
                self._exhaustive_remove_adsorbate(atoms, sas)
            elif action == 'move':
                self._exhaustive_move_adsorbate(atoms, sas)
            elif action == 'replace':
                self._exhaustive_replace_adsorbate(atoms, sas)            

            if self.logfile is not None:
                method = 'label match' if self.clean_slab else 'isomorphism'
                self.logfile.write('All possible patterns were generated '
                                   + 'for image {}\n'.format(n) +
                                   '{} patterns were '.format(self.n_duplicate)
                                   + 'discarded by {}\n\n'.format(method))
                self.logfile.flush()


class OrderedPatternGenerator(object):
    """`OrderedPatternGenerator` is a class for generating 
    adsorbate overlayer patterns stochastically. Graph isomorphism
    is implemented to identify identical adlayer patterns. 4 
    adsorbate actions are supported: add, remove, move, replace. 
    The class is generalized for both periodic and non-periodic 
    systems (distinguished by atoms.pbc). 

    Parameters
    ----------
    images : ase.Atoms object or list of ase.Atoms objects
        The structure to perform the adsorbate actions on. 
        If a list of structures is provided, perform one 
        adsorbate action on one of the structures in each step. 
        Accept any ase.Atoms object. No need to be built-in.

    adsorbate_species : str or list of strs 
        A list of possible adsorbate species to be added to the surface.

    repeating_distance : float
        The pairwise distance (in Angstrom) between two symmetry-equivalent 
        adsorption sites.

    species_probabilities : dict, default None
        A dictionary that contains keys of each adsorbate species and 
        values of their probabilities of adding onto the surface.

    max_species : int, default None
        The maximum allowed adsorbate species (excluding vacancies) for a 
        single structure. Allow all adsorbatae species if not specified.

    sorting_axis : numpy.array, default numpy.array([1, 0, 0])
        The vector to sort the sites based on the distance from the site 
        to that vector before grouping. Use the x-axis by default. Recommend
        using default or the diagonal vector.

    adsorption_sites : acat.adsorption_sites.ClusterAdsorptionSites object \
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
        The neighbor shell number within which the neighbor sites should be 
        removed. Only relevant when remove_neighbor_sites=True.       

    populate_isolated_sites : bool, default False
        Whether to add adsorbates to low-symmetry sites that are not grouped 
        with any other sites.

    allow_odd : bool, default False
        Whether to allow odd number of adsorbates. This is done by singling
        out one site for each symmetry-inequivalent site.

    heights : dict, default acat.settings.site_heights
        A dictionary that contains the adsorbate height for each site 
        type. Use the default height settings if the height for a site 
        type is not specified.

    site_groups : list of lists, default None                                 
        Provide the user defined symmetry equivalent site groups as a list 
        of lists of site indices (of the site list). Useful for generating 
        structures with symmetries that are not supported.

    save_groups : bool, default False
        Whether to save the site groups in atoms.info['data']['groups'] for
        each generated structure. If there is groups present (e.g. the groups 
        of the slab atoms), append the site groups to it.

    fragmentation : bool, default True                                  
        Whether to cut multidentate species into fragments. This ensures
        that multidentate species with different orientations are
        considered as different adlayer patterns.

    dmax : float, default 3.
        The maximum bond length (in Angstrom) between the site and the
        bonding atom that should be considered as an adsorbate.       

    dtol : float, default 0.3
        The tolerance (in Angstrom) when calculating the repeating distance.

    trajectory : str, default 'patterns.traj'
        The name of the output ase trajectory file.

    append_trajectory : bool, default False
        Whether to append structures to the existing trajectory. 
        If only unique patterns are accepted, the code will also check 
        graph isomorphism for the existing structures in the trajectory.

    """
    def __init__(self, images, 
                 adsorbate_species, 
                 repeating_distance,
                 species_probabilities=None,
                 max_species=None,
                 sorting_axis=np.array([1, 0, 0]), 
                 adsorption_sites=None,
                 remove_neighbor_sites=True,
                 remove_neighbor_number=1,
                 populate_isolated_sites=False,
                 allow_odd=False,
                 heights=site_heights, 
                 site_groups=None,
                 save_groups=False,
                 fragmentation=True,
                 dmax=3.,
                 dtol=.3,
                 trajectory='patterns.traj',
                 append_trajectory=False, 
                 **kwargs):

        self.images = images if is_list_or_tuple(images) else [images]                     
        self.adsorbate_species = adsorbate_species if is_list_or_tuple(
                                 adsorbate_species) else [adsorbate_species]
        self.repeating_distance = repeating_distance
        self.species_probabilities = species_probabilities
        if self.species_probabilities is not None:
            assert len(self.species_probabilities.keys()) == len(self.adsorbate_species)
            self.species_probability_list = [self.species_probabilities[a] for 
                                             a in self.adsorbate_species]               

        self.kwargs = {'allow_6fold': False, 'composition_effect': False,
                       'ignore_bridge_sites': True, 'label_sites': False} 
        self.kwargs.update(kwargs)
        if adsorption_sites is None:
            if True in self.images[0].pbc:
                self.adsorption_sites = SlabAdsorptionSites(self.images[0],
                                                            **self.kwargs)
            else: 
                self.adsorption_sites = ClusterAdsorptionSites(self.images[0], 
                                                               **self.kwargs)
        else:
            self.adsorption_sites = adsorption_sites
            for k in self.kwargs.keys():             
                self.kwargs[k] = attrgetter(k)(self.adsorption_sites)
        self.__dict__.update(self.kwargs)

        self.sorting_axis = sorting_axis
        self.remove_neighbor_sites = remove_neighbor_sites
        self.remove_neighbor_number = remove_neighbor_number
        self.populate_isolated_sites = populate_isolated_sites
        self.allow_odd = allow_odd
        self.heights = site_heights 
        for k, v in heights.items():
            self.heights[k] = v
        self.save_groups = save_groups
        self.fragmentation = fragmentation
        self.dmax = dmax
        self.dtol = dtol

        if max_species is None:
            self.max_species = len(set(self.adsorbate_species)) 
        else: 
            self.max_species = max_species
        if isinstance(trajectory, str):            
            self.trajectory = trajectory 
        self.append_trajectory = append_trajectory

        self.site_list = self.adsorption_sites.site_list
        if site_groups is None:                  
            self.site_groups = self.get_site_groups()
        else:
            self.site_groups = site_groups

    def get_site_groups(self, return_all_site_groups=False):
        """Get the groups (a list of lists of site indices) of all
        pairs of symmetry-equivalent sites.

        Parameters
        ----------
        return_all_site_groups : bool, default False
            Whether to return all possible high-symmetry groupings of 
            the adsorption sites.

        """

        atoms = self.images[0].copy()
        u = self.sorting_axis
        sl = self.site_list
        if self.allow_odd:
            seen_labs = set()
            odd_site_indices = set()
            for i, st in enumerate(sl):
                lab = (st['morphology'], st['site'])
                if lab not in seen_labs:
                    odd_site_indices.add(i)
                    seen_labs.add(lab)
        pts = np.asarray([s['position'] for s in sl])
        pt0 = np.mean(pts, axis=0)

        def get_signed_distance(pt):
            v = get_mic(pt, pt0, cell=atoms.cell, pbc=atoms.pbc)[:2]
            cross = u[0] * v[1] - u[1] * v[0]
            dist = abs(cross) / np.linalg.norm(u[:2])
            sign = (cross > 0).astype(np.float32) - (cross < 0).astype(np.float32)
            return sign * dist

        sorted_indices = sorted(range(len(sl)), key=lambda x: 
                                get_signed_distance(sl[x]['position']))
        i1 = 0
        for i in sorted_indices:
            st = sl[i]
            pt1 = st['position']
            tup = find_mic(pts - pt1, cell=atoms.cell, 
                           pbc=(True in atoms.pbc))
            i2a = np.argwhere(np.abs(tup[1] - self.repeating_distance) 
                              < self.dtol).ravel().tolist()
            if i2a:
                i1 = i
                break

        all_groups = set()
        for i2 in i2a:
            pt2 = sl[i2]['position']
            vec = tup[0][i2]
            seen = {i1, i2}
            groups = [[i1, i2]]
            for i in sorted_indices:
                if (i in [i1, i2]) or (i in seen):
                    continue
                st = sl[i]
                pt = st['position']
                repeat_pt = pt + vec
                ja = np.argwhere(find_mic(pts - repeat_pt, cell=atoms.cell,
                                 pbc=(True in atoms.pbc))[1] < self.dtol)
                if ja.size == 0:
                    if self.populate_isolated_sites:
                        seen.add(i)
                        groups.append([i])
                    continue
                j = np.min(ja)
                if j in seen:
                    continue
                res = sorted([i, j])
                seen.update(res)
                groups.append(res)

            if len(groups) == len(sl) / 2:
                if self.allow_odd:
                    new_groups = []
                    for g in groups:
                        if not set(g).isdisjoint(odd_site_indices):
                            new_groups += [[g[0]], [g[1]]]
                        else:
                            new_groups.append(g)
                    groups = new_groups
                groups.sort()
                if return_all_site_groups:
                    groups = tuple(tuple(g) for g in groups)
                    all_groups.add(groups)
                else:
                    return groups

        all_sorted_groups = []
        for groups in all_groups:
            sorted_groups = [list(g) for g in groups]
            all_sorted_groups.append(sorted_groups)
 
        return sorted(all_sorted_groups)
 
    def run(self, max_gen=None, unique=True):
        """Run the ordered pattern generator.

        Parameters
        ----------
        max_gen : int, default None
            Maximum number of chemical orderings to generate. Running
            forever (until exhaustive for systematic search) if not 
            specified. 

        unique : bool, default True 
            Whether to discard duplicate patterns based on graph isomorphism.

        """

        traj_mode = 'a' if self.append_trajectory else 'w'
        traj = Trajectory(self.trajectory, mode=traj_mode)
        sas = self.adsorption_sites
        sl = self.site_list
        groups = self.site_groups
        if self.remove_neighbor_sites:
            nsl = sas.get_neighbor_site_list(neighbor_number=self.remove_neighbor_number)
        ngroups = len(groups)
        labels_list, graph_list = [], []
        if len(traj) > 0 and unique and self.append_trajectory:                                
            prev_images = read(self.trajectory, index=':')
            for patoms in prev_images:
                psac = SlabAdsorbateCoverage(patoms, sas, dmax=self.dmax)
                plabs = psac.get_occupied_labels(fragmentation=self.fragmentation)
                pG = psac.get_graph(fragmentation=self.fragmentation)
                labels_list.append(plabs)
                graph_list.append(pG)

        n_write = 0
        combos = set()
        too_few = (2**ngroups * 0.95 <= max_gen)
        while True:
            if self.species_probabilities is None:
                specs = random.sample(self.adsorbate_species, self.max_species) + ['vacancy']
            else:
                specs = random.choices(k=self.max_species, population=self.adsorbate_species,                  
                                       weights=self.species_probability_list) + ['vacancy']
            combo = [None] * ngroups                                 
            indices = list(range(ngroups))
            random.shuffle(indices)
            newvs = set()
            for idx in indices:
                group = groups[idx]
                if not set(group).isdisjoint(newvs):
                    spec = 'vacancy'
                else:
                    spec = random.choice(specs)
                    if self.remove_neighbor_sites:
                        newvs.update([i for k in group for i in nsl[k]])
                combo[idx] = spec
            combo = tuple(combo)
            if not all(sp == 'vacancy' for sp in combo):
                if combo not in combos or too_few:
                    atoms = random.choice(self.images).copy()
                    dup = False
                    for j, spec in enumerate(combo):
                        if spec == 'vacancy':
                            continue
                        sites = [sl[si] for si in groups[j]]
                        for st in sites:
                            height = self.heights[st['site']]
                            add_adsorbate_to_site(atoms, spec, st, height)
                        if unique:
                            nsac = SlabAdsorbateCoverage(atoms, sas, dmax=self.dmax) 
                            labs = nsac.get_occupied_labels(fragmentation=self.fragmentation)
                            if labs in labels_list:
                                G = nsac.get_graph(fragmentation=self.fragmentation)
                                if graph_list:
                                    # Skip duplicates based on isomorphism 
                                    nm = iso.categorical_node_match('symbol', 'X')
                                    potential_graphs = [g for i, g in enumerate(graph_list) 
                                                        if labels_list[i] == labs]
                                    if any(H for H in potential_graphs if 
                                    nx.isomorphism.is_isomorphic(G, H, node_match=nm)):
                                        dup = True
                                        break
                                graph_list.append(G)
                            labels_list.append(labs)
                    if dup:
                        continue                   
                    combos.add(combo)
                    if self.save_groups:
                        if 'data' not in atoms.info:
                            atoms.info['data'] = {}
                        if 'groups' in atoms.info['data']:
                            atoms.info['data']['groups'] += groups
                        else:
                            atoms.info['data']['groups'] = groups
                    traj.write(atoms)
                    n_write += 1
                    if max_gen is not None:
                        if n_write == max_gen:
                            break


def special_coverage_pattern(atoms, adsorbate_species, 
                             coverage=1., 
                             species_probabilities=None,
                             adsorption_sites=None,
                             surface=None, 
                             height=None, 
                             min_adsorbate_distance=0., 
                             **kwargs):
    """A function for generating representative ordered adsorbate 
    overlayer patterns. The function is generalized for both periodic 
    and non-periodic systems (distinguished by atoms.pbc).

    Parameters
    ----------
    atoms : ase.Atoms object
        The nanoparticle or surface slab onto which the adsorbates are
        added. Accept any ase.Atoms object. No need to be built-in.

    adsorbate_species : str or list of strs 
        A list of adsorbate species to be added to the surface.

    coverage : float, default 1. 
        The coverage (ML) of the adsorbate (N_adsorbate / N_surf_atoms). 
        Support 4 adlayer patterns (
        0.25 for p(2x2) pattern; 
        0.5 for c(2x2) pattern on fcc100 or honeycomb pattern on fcc111; 
        0.75 for (2x2) pattern on fcc100 or Kagome pattern on fcc111; 
        1. for p(1x1) pattern; 
        2. for ontop+4fold pattern on fcc100 or fcc+hcp pattern on fcc111.
        Note that for small nanoparticles, the function might give 
        results that do not correspond to the coverage. This is normal 
        since the surface area can be too small to encompass the 
        adlayer pattern properly. We expect this function to work 
        well on large nanoparticles and surface slabs.                  

    species_probabilities : dict, default None
        A dictionary that contains keys of each adsorbate species and 
        values of their probabilities of adding onto the surface.

    adsorption_sites : acat.adsorption_sites.ClusterAdsorptionSites object \
        or acat.adsorption_sites.SlabAdsorptionSites object, default None
        Provide the built-in adsorption sites class to accelerate the 
        pattern generation. If this is not provided, the arguments for 
        identifying adsorption sites can still be passed in by **kwargs.

    surface : str, default None
        The surface type (crystal structure + Miller indices).
        For now only support 2 common surfaces: fcc100 and fcc111. 
        If the structure is a periodic surface slab, this is required when
        adsorption_sites is not provided. 
        If the structure is a nanoparticle, the function only add 
        adsorbates to the sites on the specified surface. 

    height : float, default None
        The height of the added adsorbate from the surface.
        Use the default settings if not specified.

    min_adsorbate_distance : float, default 0.
        The minimum distance between two atoms that belongs to two 
        adsorbates.

    """

    assert coverage in [0.25, 0.5, 0.75, 1., 2.], 'coverage not supported' 

    adsorbate_species = adsorbate_species if is_list_or_tuple(                                     
                        adsorbate_species) else [adsorbate_species]
    if species_probabilities is not None:
        assert len(species_probabilities.keys()) == len(adsorbate_species)
        probability_list = [species_probabilities[a] for a in adsorbate_species]

    if True not in atoms.pbc:                            
        if surface is None:
            surface = ['fcc100', 'fcc111'] 
        if adsorption_sites is None:       
            sas = ClusterAdsorptionSites(atoms, **kwargs)
        else:
            sas = adsorption_sites
        site_list = sas.site_list
    else:
        if adsorption_sites is None:
            sas = SlabAdsorptionSites(atoms, surface=surface, **kwargs)
        else:
            sas = adsorption_sites
        site_list = sas.site_list
        if 'both_sides' in kwargs:
            if kwargs['both_sides']:
                bot_site_list = site_list[len(site_list)//2:]
                site_list = site_list[:len(site_list)//2]

    if not isinstance(surface, list):
        surface = [surface] 

    #TODO: implement Woods' notation
    def find_ordered_sites(site_list):
        final_sites = []
        if 'fcc111' in surface: 
            # fcc+hcp pattern
            if coverage == 2:
                fold3_sites = [s for s in site_list if s['site'] in ['fcc', 'hcp']]
                if fold3_sites:
                    final_sites += fold3_sites

            # p(1x1) pattern
            if coverage == 1:
                fcc_sites = [s for s in site_list if s['site'] == 'fcc']
                if fcc_sites:
                    final_sites += fcc_sites
 
            # Kagome pattern
            elif coverage == 3/4:
                fcc_sites = [s for s in site_list if s['site'] == 'fcc']
                if True not in atoms.pbc:                                
                    grouped_sites = group_sites_by_facet(atoms, fcc_sites, site_list)
                else:
                    grouped_sites = {'pbc_sites': fcc_sites}

                for sites in grouped_sites.values():
                    if sites:
                        sites_to_remove = [sites[0]]
                        for sitei in sites_to_remove:
                            common_site_indices = []
                            non_common_sites = []
                            for sitej in sites:
                                if sitej['indices'] == sitei['indices']:
                                    continue
                                if set(sitej['indices']) & set(sitei['indices']):
                                    common_site_indices += list(sitej['indices'])
                                else:
                                    non_common_sites.append(sitej)
                            for sitej in non_common_sites:
                                overlap = sum([common_site_indices.count(i) 
                                               for i in sitej['indices']])
                                if overlap == 1 and sitej['indices'] not in [
                                s['indices'] for s in sites_to_remove]:
                                    sites_to_remove.append(sitej)
                        if True in atoms.pbc:
                            if len(sites_to_remove) != len(fcc_sites) * 1/4:
                                sorted_sites = sorted(sites, key=lambda x: get_mic(                
                                                      x['position'], sites[0]['position'], 
                                                      atoms.cell, return_squared_distance=True))
                                sites_to_remove = [sites[0]] + sorted_sites[
                                                   1-int(len(fcc_sites)*1/4):]
                        for s in sites:
                            if s['indices'] not in [st['indices'] for st in sites_to_remove]:
                                final_sites.append(s)
 
            # Honeycomb pattern
            elif coverage == 2/4:
                fcc_sites = [s for s in site_list if s['site'] == 'fcc']
                hcp_sites = [s for s in site_list if s['site'] == 'hcp']
                all_sites = fcc_sites + hcp_sites
                if True not in atoms.pbc:    
                    grouped_sites = group_sites_by_facet(atoms, all_sites, site_list)
                else:
                    grouped_sites = {'pbc_sites': all_sites}
                for sites in grouped_sites.values():
                    if sites:                    
                        sites_to_keep = [sites[0]]
                        for sitei in sites_to_keep:
                            for sitej in sites:
                                if sitej['indices'] == sitei['indices']:
                                    continue
                                if len(set(sitej['indices']) & \
                                set(sitei['indices'])) == 1 \
                                and sitej['site'] != sitei['site'] \
                                and sitej['indices'] not in [s['indices'] 
                                for s in sites_to_keep]:
                                    sites_to_keep.append(sitej)
                        if True in atoms.pbc:
                            if len(sites_to_keep) != len(fcc_sites) * 1/2:
                                sorted_sites = sorted(all_sites, key=lambda x: get_mic(                
                                                      x['position'], all_sites[0]['position'], 
                                                      atoms.cell, return_squared_distance=True))
                                sites_to_keep = [all_sites[0]] + sorted_sites[
                                                 1-int(len(fcc_sites)*1/2):]
                        final_sites += sites_to_keep                                          
                if True not in atoms.pbc:                                                                       
                    bad_sites = []
                    for sti in final_sites:
                        if sti['site'] == 'hcp':
                            count = 0
                            for stj in final_sites:
                                if stj['site'] == 'fcc':
                                    if len(set(stj['indices']) & set(sti['indices'])) == 2:
                                        count += 1
                            if count != 0:
                                bad_sites.append(sti)
                    final_sites = [s for s in final_sites if s['indices'] not in 
                                   [st['indices'] for st in bad_sites]]
 
            # p(2x2) pattern
            elif coverage == 1/4:
                fcc_sites = [s for s in site_list if s['site'] == 'fcc']                                                                 
                if True not in atoms.pbc:                                
                    grouped_sites = group_sites_by_facet(atoms, fcc_sites, site_list)
                else:
                    grouped_sites = {'pbc_sites': fcc_sites}
 
                for sites in grouped_sites.values():
                    if sites:
                        sites_to_keep = [sites[0]]
                        for sitei in sites_to_keep:
                            common_site_indices = []
                            non_common_sites = []
                            for sitej in sites:
                                if sitej['indices'] == sitei['indices']:
                                    continue
                                if set(sitej['indices']) & set(sitei['indices']):
                                    common_site_indices += list(sitej['indices'])
                                else:
                                    non_common_sites.append(sitej)
                            for sitej in non_common_sites:
                                overlap = sum([common_site_indices.count(i) 
                                              for i in sitej['indices']])
                                if overlap == 1 and sitej['indices'] not in [
                                s['indices'] for s in sites_to_keep]:
                                    sites_to_keep.append(sitej)               
                        if True in atoms.pbc:
                            if len(sites_to_keep) != len(fcc_sites) * 1/4:
                                sorted_sites = sorted(sites, key=lambda x: get_mic(                
                                                      x['position'], sites[0]['position'], 
                                                      atoms.cell, return_squared_distance=True))
                                sites_to_keep = [sites[0]] + sorted_sites[
                                                 1-int(len(fcc_sites)*1/4):]
                        final_sites += sites_to_keep
 
        if 'fcc100' in surface:
            # ontop+4fold pattern
            if coverage == 2:
                fold14_sites = [s for s in site_list if s['site'] in ['ontop', '4fold']]
                if fold14_sites:
                    final_sites += fold14_sites

            # p(1x1) pattern
            if coverage == 1:
                fold4_sites = [s for s in site_list if s['site'] == '4fold']
                if fold4_sites:
                    final_sites += fold4_sites
 
            # (2x2) pattern 
            elif coverage == 3/4:
                fold4_sites = [s for s in site_list if s['site'] == '4fold']
                if True not in atoms.pbc:                                           
                    grouped_sites = group_sites_by_facet(atoms, fold4_sites, site_list)
                else:
                    grouped_sites = {'pbc_sites': fold4_sites}
                for sites in grouped_sites.values():
                    if sites:
                        sites_to_remove = [sites[0]]
                        for sitei in sites_to_remove:
                            common_site_indices = []
                            non_common_sites = []
                            for sitej in sites:
                                if sitej['indices'] == sitei['indices']:
                                    continue
                                if set(sitej['indices']) & set(sitei['indices']):
                                    common_site_indices += list(sitej['indices'])
                                else:
                                    non_common_sites.append(sitej)
                            for sitej in non_common_sites:                        
                                overlap = sum([common_site_indices.count(i) 
                                              for i in sitej['indices']])                        
                                if overlap in [1, 4] and sitej['indices'] not in [
                                s['indices'] for s in sites_to_remove]:  
                                    sites_to_remove.append(sitej)
                        if True in atoms.pbc:
                            if len(sites_to_remove) != len(fold4_sites) * 1/4:
                                sorted_sites = sorted(sites, key=lambda x: get_mic(                
                                                      x['position'], sites[0]['position'], 
                                                      atoms.cell, return_squared_distance=True))
                                sites_to_remove = [sites[0]] + [sorted_sites[-1]] + sorted_sites[
                                                   1-2*int(len(fold4_sites)*1/4):
                                                   -int(len(fold4_sites)*1/4)-1]
                        for s in sites:
                            if s['indices'] not in [st['indices'] for st in sites_to_remove]:
                                final_sites.append(s)
 
            # c(2x2) pattern
            elif coverage == 2/4:
                fold4_sites = [s for s in site_list if s['site'] == '4fold']
                original_sites = deepcopy(fold4_sites)
                if True not in atoms.pbc:
                    grouped_sites = group_sites_by_facet(atoms, fold4_sites, site_list)
                else:
                    grouped_sites = {'pbc_sites': fold4_sites}
                for sites in grouped_sites.values():
                    if sites:
                        sites_to_keep = [sites[0]]
                        for sitei in sites_to_keep:
                            for sitej in sites:
                                if (len(set(sitej['indices']) & \
                                set(sitei['indices'])) == 1) and \
                                (sitej['indices'] not in [s['indices'] 
                                for s in sites_to_keep]):
                                    sites_to_keep.append(sitej)
                        if True in atoms.pbc:
                            if len(sites_to_keep) != len(fold4_sites) * 1/2:
                                sorted_sites = sorted(sites, key=lambda x: get_mic(                
                                                      x['position'], sites[0]['position'], 
                                                      atoms.cell, return_squared_distance=True))
                                sites_to_keep = [sites[0]] + [sorted_sites[-1]] + sorted_sites[
                                                 1-2*int(len(fold4_sites)*1/2):
                                                 -int(len(fold4_sites)*1/2)-1]
                        for s in original_sites:
                            if s['indices'] in [st['indices'] for st in sites_to_keep]:
                                final_sites.append(s)
 
            # p(2x2) pattern
            elif coverage == 1/4:
                fold4_sites = [s for s in site_list if s['site'] == '4fold']
                if True not in atoms.pbc:                                           
                    grouped_sites = group_sites_by_facet(atoms, fold4_sites, site_list)
                else:
                    grouped_sites = {'pbc_sites': fold4_sites}

                for sites in grouped_sites.values():
                    if sites:
                        sites_to_keep = [sites[0]]
                        for sitei in sites_to_keep:
                            common_site_indices = []
                            non_common_sites = []
                            for idx, sitej in enumerate(sites):
                                if sitej['indices'] == sitei['indices']:
                                    continue
                                if set(sitej['indices']) & set(sitei['indices']):
                                    common_site_indices += list(sitej['indices'])
                                else:
                                    non_common_sites.append(sitej)
                            for sitej in non_common_sites:
                                overlap = sum([common_site_indices.count(i) 
                                              for i in sitej['indices']])
                                if overlap in [1, 4] and sitej['indices'] not in [
                                s['indices'] for s in sites_to_keep]:  
                                    sites_to_keep.append(sitej)
                        if True in atoms.pbc:
                            print(sites[0]['indices'])
                            if len(sites_to_keep) != len(fold4_sites) * 1/4:
                                sorted_sites = sorted(sites, key=lambda x: get_mic(                
                                                      x['position'], sites[0]['position'], 
                                                      atoms.cell, return_squared_distance=True))
                                sites_to_keep = [sites[0]] + [sorted_sites[-1]] + sorted_sites[
                                                 1-2*int(len(fold4_sites)*1/4):
                                                 -int(len(fold4_sites)*1/4)-1]
                        final_sites += sites_to_keep
        return final_sites

    final_sites = find_ordered_sites(site_list)
    if True in atoms.pbc:
        if 'both_sides' in kwargs:
            if kwargs['both_sides']:
                final_sites += find_ordered_sites(bot_site_list)
    # Add edge coverage for nanoparticles
    else:
        if coverage in [1, 2]:
            edge_sites = [s for s in site_list if 
                          s['site'] == 'bridge' and 
                          s['surface'] == 'edge']
            vertex_indices = [s['indices'][0] for 
                              s in site_list if 
                              s['site'] == 'ontop' and 
                              s['surface'] == 'vertex']
            ve_common_indices = set()
            for esite in edge_sites:
                if set(esite['indices']) & set(vertex_indices):
                    for i in esite['indices']:
                        if i not in vertex_indices:
                            ve_common_indices.add(i)
            for esite in edge_sites:
                if not set(esite['indices']).issubset(
                ve_common_indices):
                    final_sites.append(esite)

        if coverage == 3/4:
            occupied_sites = final_sites.copy()
            hcp_sites = [s for s in site_list if 
                         s['site'] == 'hcp' and
                         s['surface'] == 'fcc111']
            edge_sites = [s for s in site_list if 
                          s['site'] == 'bridge' and
                          s['surface'] == 'edge']
            vertex_indices = [s['indices'][0] for 
                              s in site_list if
                              s['site'] == 'ontop' and 
                              s['surface'] == 'vertex']
            ve_common_indices = set()
            for esite in edge_sites:
                if set(esite['indices']) & set(vertex_indices):
                    for i in esite['indices']:
                        if i not in vertex_indices:
                            ve_common_indices.add(i)                
            for esite in edge_sites:
                if not set(esite['indices']).issubset(
                ve_common_indices):
                    intermediate_indices = []
                    for hsite in hcp_sites:
                        if len(set(esite['indices']) & set(hsite['indices'])) == 2:
                            intermediate_indices.append(min(
                            set(esite['indices']) ^ set(hsite['indices'])))
                    too_close = 0
                    for s in occupied_sites:
                        if len(set(esite['indices']) & set(s['indices'])) == 2:
                            too_close += 1
                    share = [0]
                    for interi in intermediate_indices:
                        share.append(len([s for s in occupied_sites if
                                          interi in s['indices']]))
                    if max(share) <= 2 and too_close == 0:
                        final_sites.append(esite)

        if coverage == 2/4:            
            occupied_sites = final_sites.copy()
            hcp_sites = [s for s in site_list if 
                         s['site'] == 'hcp' and
                         s['surface'] == 'fcc111']
            edge_sites = [s for s in site_list if 
                          s['site'] == 'bridge' and
                          s['surface'] == 'edge']
            vertex_indices = [s['indices'][0] for 
                              s in site_list if
                              s['site'] == 'ontop' and 
                              s['surface'] == 'vertex']
            ve_common_indices = set()
            for esite in edge_sites:
                if set(esite['indices']) & set(vertex_indices):
                    for i in esite['indices']:
                        if i not in vertex_indices:
                            ve_common_indices.add(i)                
            for esite in edge_sites:
                if not set(esite['indices']).issubset(
                ve_common_indices):
                    intermediate_indices = []
                    for hsite in hcp_sites:
                        if len(set(esite['indices']) & set(hsite['indices'])) == 2:
                            intermediate_indices.append(min(
                            set(esite['indices']) ^ set(hsite['indices'])))
                    share = [0]
                    for interi in intermediate_indices:
                        share.append(len([s for s in occupied_sites if
                                          interi in s['indices']]))
                    too_close = 0
                    for s in occupied_sites:
                        if len(set(esite['indices']) & set(s['indices'])) == 2:
                            too_close += 1
                    if max(share) <= 1 and too_close == 0:
                        final_sites.append(esite)

        if coverage == 1/4:
            occupied_sites = final_sites.copy()
            hcp_sites = [s for s in site_list if 
                         s['site'] == 'hcp' and
                         s['surface'] == 'fcc111']
            edge_sites = [s for s in site_list if 
                          s['site'] == 'bridge' and
                          s['surface'] == 'edge']
            vertex_indices = [s['indices'][0] for 
                              s in site_list if
                              s['site'] == 'ontop' and 
                              s['surface'] == 'vertex'] 
            ve_common_indices = set()
            for esite in edge_sites:
                if set(esite['indices']) & set(vertex_indices):
                    for i in esite['indices']:
                        if i not in vertex_indices:
                            ve_common_indices.add(i)                
            for esite in edge_sites:
                if not set(esite['indices']).issubset(
                ve_common_indices):
                    intermediate_indices = []
                    for hsite in hcp_sites:
                        if len(set(esite['indices']) & set(hsite['indices'])) == 2:
                            intermediate_indices.append(min(
                            set(esite['indices']) ^ set(hsite['indices'])))
                    share = [0]
                    for interi in intermediate_indices:
                        share.append(len([s for s in occupied_sites if
                                          interi in s['indices']]))
                    too_close = 0
                    for s in occupied_sites:
                        if len(set(esite['indices']) &
                        set(s['indices'])) > 0:
                            too_close += 1
                    if max(share) == 0 and too_close == 0:
                        final_sites.append(esite)

    natoms = len(atoms)
    nads_dict = {ads: len(list(Formula(ads))) for ads in adsorbate_species}

    for site in final_sites:
        # Select adsorbate with probability 
        if not species_probabilities:
            adsorbate = random.choice(adsorbate_species)
        else: 
            adsorbate = random.choices(k=1, population=adsorbate_species,
                                       weights=probability_list)[0]        
        nads = nads_dict[adsorbate] 

        if height is None:
            height = site_heights[site['site']]
        add_adsorbate_to_site(atoms, adsorbate, site, height)       
        if min_adsorbate_distance > 0:
            if atoms_too_close_after_addition(atoms[natoms:], nads,
            min_adsorbate_distance, mic=(True in atoms.pbc)): 
                atoms = atoms[:-nads]

    return atoms


def max_dist_coverage_pattern(atoms, adsorbate_species, 
                              coverage, site_types=None, 
                              species_probabilities=None,
                              adsorption_sites=None,
                              surface=None,
                              heights=site_heights,
                              **kwargs):
    """A function for generating random adlayer patterns with 
    a certain surface adsorbate coverage (i.e. fixed number of 
    adsorbates N) and trying to even the adsorbate density. The 
    function samples N sites from all given sites using K-medoids 
    clustering to maximize the minimum distance between sites and 
    add N adsorbates to these sites. The function is generalized 
    for both periodic and non-periodic systems (distinguished by 
    atoms.pbc). pyclustering is required.

    Parameters
    ----------
    atoms : ase.Atoms object
        The nanoparticle or surface slab onto which the adsorbates are
        added. Accept any ase.Atoms object. No need to be built-in.

    adsorbate_species : str or list of strs 
        A list of adsorbate species to be added to the surface.

    coverage : float
        The surface coverage calculated by (number of adsorbates /
        number of surface atoms). Subsurface sites are not considered.

    site_types : str or list of strs, default None
        The site type(s) that the adsorbates should be added to.
        Consider all sites if not specified.

    species_probabilities : dict, default None
        A dictionary that contains keys of each adsorbate species and 
        values of their probabilities of adding onto the surface.

    adsorption_sites : acat.adsorption_sites.ClusterAdsorptionSites object \
        or acat.adsorption_sites.SlabAdsorptionSites object, default None
        Provide the built-in adsorption sites class to accelerate the 
        pattern generation. If this is not provided, the arguments for 
        identifying adsorption sites can still be passed in by **kwargs.

    surface : str, default None
        The surface type (crystal structure + Miller indices). 
        If the structure is a periodic surface slab, this is required when
        adsorption_sites is not provided. 
        If the structure is a nanoparticle, the function only add 
        adsorbates to the sites on the specified surface. 

    heights : dict, default acat.settings.site_heights
        A dictionary that contains the adsorbate height for each site 
        type. Use the default height settings if the height for a site 
        type is not specified.

    """
    from pyclustering.cluster.kmedoids import kmedoids

    adsorbate_species = adsorbate_species if is_list_or_tuple(
                        adsorbate_species) else [adsorbate_species]
    if site_types is not None:
        site_types = site_types if is_list_or_tuple(site_types) else [site_types]
    if species_probabilities is not None:
        assert len(species_probabilities.keys()) == len(adsorbate_species)
        probability_list = [species_probabilities[a] for a in adsorbate_species]               
    
    _heights = site_heights
    for k, v in heights.items():
        _heights[k] = v
    heights = _heights
 
    if True not in atoms.pbc:                                
        if adsorption_sites is None:
            sas = ClusterAdsorptionSites(atoms, **kwargs)
        else:
            sas = adsorption_sites
        site_list = sas.site_list
        if surface is not None:
            site_list = [s for s in site_list if s['surface'] == surface]
    else:
        if adsorption_sites is None:
            sas = SlabAdsorptionSites(atoms, surface=surface, **kwargs)
        else:
            sas = adsorption_sites
        site_list = sas.site_list
    if site_types is None:
        site_list = [s for s in site_list if s['site'] != '6fold']
    else:
        site_list = [s for s in site_list if s['site'] in site_types 
                     and s['site'] != '6fold']

    nads = int(len(sas.surf_ids) * coverage)
    points = np.asarray([s['position'] for s in site_list])
    if True in atoms.pbc:
        D = np.asarray([find_mic(points - np.tile(points[i], (len(points),1)), 
                        cell=atoms.cell, pbc=True)[1] for i in range(len(points))])
    else:
        D = distance_matrix(points, points)

    # K-medoids clustering (PAM algorithm)
    medoids_init = random.sample(range(len(points)), nads)
    pam = kmedoids(D, medoids_init, data_type='distance_matrix')
    pam.process()
    sampled_indices = pam.get_medoids()

    final_sites = [site_list[j] for j in sampled_indices]
    for st in final_sites:
        # Select adsorbate with probability 
        if not species_probabilities:
            adsorbate = random.choice(adsorbate_species)
        else: 
            adsorbate = random.choices(k=1, population=adsorbate_species,
                                       weights=probability_list)[0]        
        height = heights[st['site']]
        add_adsorbate_to_site(atoms, adsorbate, st, height)       

    return atoms


def min_dist_coverage_pattern(atoms, adsorbate_species, 
                              species_probabilities=None,
                              adsorption_sites=None,
                              surface=None, 
                              min_adsorbate_distance=1.5, 
                              site_types=None,
                              heights=site_heights,
                              site_preference=None,
                              **kwargs):
    """A function for generating random adlayer patterns with a 
    minimum distance constraint and trying to maximize the adsorbate
    density. The function is generalized for both periodic and 
    non-periodic systems (distinguished by atoms.pbc). Especially 
    useful for generating high coverage patterns.

    Parameters
    ----------
    atoms : ase.Atoms object
        The nanoparticle or surface slab onto which the adsorbates are
        added. Accept any ase.Atoms object. No need to be built-in.

    adsorbate_species : str or list of strs 
        A list of adsorbate species to be randomly added to the surface.

    species_probabilities : dict, default None
        A dictionary that contains keys of each adsorbate species and 
        values of their probabilities of adding onto the surface.

    adsorption_sites : acat.adsorption_sites.ClusterAdsorptionSites object \
        or acat.adsorption_sites.SlabAdsorptionSites object, default None
        Provide the built-in adsorption sites class to accelerate the 
        pattern generation. If this is not provided, the arguments for 
        identifying adsorption sites can still be passed in by **kwargs.

    surface : str, default None
        The surface type (crystal structure + Miller indices).
        If the structure is a periodic surface slab, this is required when
        adsorption_sites is not provided. 
        If the structure is a nanoparticle, the function only add 
        adsorbates to the sites on the specified surface. 

    min_adsorbate_distance : float, default 1.5
        The minimum distance constraint between two atoms that belongs 
        to two adsorbates.

    site_types : str or list of strs, default None
        The site type(s) that the adsorbates should be added to.
        Consider all sites if not specified.

    heights : dict, default acat.settings.site_heights
        A dictionary that contains the adsorbate height for each site 
        type. Use the default height settings if the height for a site 
        type is not specified.

    site_preference : str of list of strs, defualt None
        The site type(s) that has higher priority to attach adsorbates.
    
    """
    adsorbate_species = adsorbate_species if is_list_or_tuple(
                        adsorbate_species) else [adsorbate_species]
    if site_types is not None:
        site_types = site_types if is_list_or_tuple(site_types) else [site_types]
    if species_probabilities is not None:
        assert len(species_probabilities.keys()) == len(adsorbate_species)
        probability_list = [species_probabilities[a] for a in adsorbate_species]               
    
    _heights = site_heights
    for k, v in heights.items():
        _heights[k] = v
    heights = _heights
 
    if True not in atoms.pbc:                                
        if adsorption_sites is None:
            sas = ClusterAdsorptionSites(atoms, **kwargs)
        else:
            sas = adsorption_sites
        site_list = sas.site_list
        if surface is not None:
            site_list = [s for s in site_list if s['surface'] == surface]
    else:
        if adsorption_sites is None:                           
            sas = SlabAdsorptionSites(atoms, surface=surface, **kwargs)
        else:
            sas = adsorption_sites
        site_list = sas.site_list
    if site_types is not None:
        site_list = [s for s in site_list if s['site'] in site_types]

    random.shuffle(site_list)
    natoms = len(atoms)
    nads_dict = {ads: len(list(Formula(ads))) for ads in adsorbate_species}

    if site_preference is not None:
        if not is_list_or_tuple(site_preference):
            site_preference = [site_preference]
        site_list.sort(key=lambda x: x['site'] in site_preference, reverse=True)

    for st in site_list:
        # Select adsorbate with probability 
        if not species_probabilities:
            adsorbate = random.choice(adsorbate_species)
        else: 
            adsorbate = random.choices(k=1, population=adsorbate_species,
                                       weights=probability_list)[0] 

        if st['site'] == '6fold':
            if len(adsorbate) != 1:
                continue
        nads = nads_dict[adsorbate] 
        height = heights[st['site']]
        add_adsorbate_to_site(atoms, adsorbate, st, height)       
        if min_adsorbate_distance > 0:
            if atoms_too_close_after_addition(atoms[natoms:], nads,
            min_adsorbate_distance, mic=(True in atoms.pbc)):
                atoms = atoms[:-nads]                               

    return atoms
