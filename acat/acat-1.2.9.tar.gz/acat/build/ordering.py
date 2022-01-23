from ..utilities import (bipartitions, get_mic,
                         partitions_into_totals, 
                         numbers_from_ratios, 
                         is_list_or_tuple)
from ase.geometry import get_distances, find_mic, get_layers
from ase.io import Trajectory, read, write
from asap3.analysis import FullCNA 
from asap3 import EMT as asapEMT
from asap3.Internal.BuiltinPotentials import Gupta
from collections import defaultdict
from itertools import product, combinations
from networkx.algorithms.components.connected import connected_components
import networkx as nx
import numpy as np
import random
import math


class SymmetricClusterOrderingGenerator(object):
    """`SymmetricClusterOrderingGenerator` is a class for generating 
    symmetric chemical orderings for a **nanoalloy**. There is no 
    limitation of the number of metal components. Please always align 
    the z direction to the symmetry axis of the nanocluster.
 
    Parameters
    ----------
    atoms : ase.Atoms object
        The nanoparticle to use as a template to generate symmetric
        chemical orderings. Accept any ase.Atoms object. No need to be 
        built-in.

    elements : list of strs 
        The metal elements of the nanoalloy.

    symmetry : str, default 'spherical'
        Support 9 symmetries: 

        **'spherical'**: spherical symmetry (groups defined by the 
        distances to the geometric center);

        **'cylindrical'**: cylindrical symmetry around z axis (groups 
        defined by the distances to the z axis);

        **'planar'**: planar symmetry around z axis (groups defined by 
        the z coordinates), common for phase-separated nanoalloys;

        **'mirror_planar'**: mirror planar symmetry around both
        z and xy plane (groups defined by the absolute z coordinate), 
        high symmetry subset of 'planar';
        'circular' = ring symmetry around z axis (groups defined by
        both z coordinate and distance to z axis);

        **'mirror_circular'**: mirror ring symmetry around both
        z and xy plane (groups defined by both absolute z coordinate 
        and distance to z axis);

        **'chemical'**: symmetry w.r.t chemical environment (groups 
        defined by the atomic energies given by a Gupta potential)

        **'geometrical'**: symmetry w.r.t geometrical environment (groups 
        defined by vertex / edge / fcc111 / fcc100 / bulk identified
        by CNA analysis);

        **'concentric'**: conventional definition of the concentric 
        shells (surface / subsurface, subsubsurface, ..., core).

    cutoff : float, default 1.0
        Maximum thickness (in Angstrom) of a single group. The thickness
        is calculated as the difference between the "distances" of the 
        closest-to-center atoms in two neighbor groups. Note that the
        criterion of "distance" depends on the symmetry. This parameter 
        works differently if the symmetry is 'chemical', 'geometrical' or 
        'concentric'. For 'chemical' it is defined as the maximum atomic
        energy difference (in eV) of a single group predicted by a Gupta
        potential. For 'geometrical' and 'concentric' it is defined as 
        the cutoff radius (in Angstrom) for CNA, and a reasonable cutoff 
        based on the lattice constant of the material will automatically 
        be used if cutoff <= 1. Use a larger cutoff if the structure is 
        distorted. 

    secondary_symmetry : str, default None
        Add a secondary symmetry check to define groups hierarchically. 
        For example, even if two atoms are classifed in the same group
        defined by the primary symmetry, they can still end up in 
        different groups if they fall into two different groups defined 
        by the secondary symmetry. Support 7 symmetries: 'spherical',
        'cylindrical', 'planar', 'mirror_planar', 'chemical', 'geometrical' 
        and 'concentric'. Note that secondary symmetry has the same 
        importance as the primary symmetry, so you can set either of the 
        two symmetries of interest as the secondary symmetry. Useful for 
        combining symmetries of different types (e.g. circular + chemical) 
        or combining symmetries with different cutoffs.

    secondary_cutoff : float, default 1.0
        Same as cutoff, except that it is for the secondary symmetry.

    composition : dict, default None
        Generate symmetric orderings only at a certain composition.
        The dictionary contains the metal elements as keys and their 
        concentrations as values. Generate orderings at all compositions 
        if not specified. 

    groups : list of lists, default None
        Provide the user defined symmetry equivalent groups as a list of 
        lists of atom indices. Useful for generating structures with
        symmetries that are not supported.

    save_groups : bool, default False
        Whether to save the site groups in atoms.info['data']['groups'] 
        for each generated structure.

    trajectory : str, default 'orderings.traj'
        The name of the output ase trajectory file.

    append_trajectory : bool, default False
        Whether to append structures to the existing trajectory. 

    """

    def __init__(self, atoms, elements,
                 symmetry='spherical',
                 cutoff=1.,       
                 secondary_symmetry=None,
                 secondary_cutoff=1.,
                 composition=None,
                 groups=None,
                 save_groups=False,
                 trajectory='orderings.traj',
                 append_trajectory=False):

        self.atoms = atoms
        self.elements = elements
        self.symmetry = symmetry
        self.cutoff = cutoff
        assert secondary_symmetry not in ['circular', 'mirror_circular']
        self.secondary_symmetry = secondary_symmetry
        self.secondary_cutoff = secondary_cutoff

        self.composition = composition
        if self.composition is not None:
            ks = list(self.composition.keys())
            assert set(ks) == set(self.elements)
        self.save_groups = save_groups
 
        if isinstance(trajectory, str):
            self.trajectory = trajectory                        
        self.append_trajectory = append_trajectory

        if groups is None:
            self.groups = self.get_groups()
        else:
            self.groups = groups

    def get_sorted_indices(self, symmetry):                               
        """Returns the indices sorted by the metric that defines different 
        groups, together with the corresponding vlues, given a specific 
        symmetry. Returns the indices sorted by geometrical environment if 
        symmetry='geometrical'. Returns the indices sorted by surface, 
        subsurface, subsubsurface, ..., core if symmetry='concentric'.

        Parameters
        ----------
        symmetry : str
            Support 7 symmetries: spherical, cylindrical, planar, 
            mirror_planar, chemical, geometrical, concentric.

        """

        atoms = self.atoms.copy()
        atoms.center()
        geo_mid = [(atoms.cell/2.)[0][0], (atoms.cell/2.)[1][1], 
                   (atoms.cell/2.)[2][2]]
        if symmetry == 'spherical':
            dists = get_distances(atoms.positions, [geo_mid])[1][:,0]

        elif symmetry == 'cylindrical':
            dists = np.asarray([math.sqrt((a.position[0] - geo_mid[0])**2 + 
                               (a.position[1] - geo_mid[1])**2) for a in atoms])

        elif symmetry == 'planar':
            dists = atoms.positions[:, 2]

        elif symmetry == 'mirror_planar':
            dists = abs(atoms.positions[:, 2] - geo_mid[2])

        elif symmetry == 'chemical':
            gupta_parameters = {'Cu': [10.960, 2.2780, 0.0855, 1.224, 2.556]}
            calc = Gupta(gupta_parameters, cutoff=1000, debug=False)
            for a in atoms:
                a.symbol = 'Cu'
            atoms.center(vacuum=5.)
            atoms.calc = calc
            dists = atoms.get_potential_energies()
            atoms.calc = None

        elif symmetry == 'geometrical':
            if self.symmetry == 'geometrical':
                rCut = None if self.cutoff <= 1. else self.cutoff
            elif self.secondary_symmetry == 'geometrical':
                rCut = None if self.secondary_cutoff <= 1. else self.secondary_cutoff
            atoms.center(vacuum=5.)
            fcna = FullCNA(atoms, rCut=rCut).get_normal_cna()
            d = defaultdict(list)
            for i, x in enumerate(fcna):
                if sum(x.values()) < 12:
                    d[str(x)].append(i)
                else:
                    d['bulk'].append(i)
            return list(d.values()), None

        elif symmetry == 'concentric':
            if self.symmetry == 'concentric':
                rCut = None if self.cutoff <= 1. else self.cutoff
            elif self.secondary_symmetry == 'concentric':
                rCut = None if self.secondary_cutoff <= 1. else self.secondary_cutoff

            def view1D(a, b): # a, b are arrays
                a = np.ascontiguousarray(a)
                b = np.ascontiguousarray(b)
                void_dt = np.dtype((np.void, a.dtype.itemsize * a.shape[1]))
                return a.view(void_dt).ravel(),  b.view(void_dt).ravel()

            def argwhere_nd_searchsorted(a,b):
                A,B = view1D(a,b)
                sidxB = B.argsort()
                mask = np.isin(A,B)
                cm = A[mask]
                idx0 = np.flatnonzero(mask)
                idx1 = sidxB[np.searchsorted(B,cm, sorter=sidxB)]
                return idx0, idx1 # idx0 : indices in A, idx1 : indices in B

            def get_surf_ids(a):
                fcna = FullCNA(a, rCut=rCut).get_normal_cna() 
                surf_ids, bulk_ids = [], []
                for i in range(len(a)):
                    if sum(fcna[i].values()) < 12:
                        surf_ids.append(i)
                    else:
                        bulk_ids.append(i)
                group_ids = list(argwhere_nd_searchsorted(atoms.positions, 
                                 a.positions[surf_ids])[0])
                conv_groups.append(group_ids)
                if not bulk_ids:
                    return 
                get_surf_ids(a[bulk_ids])

            conv_groups = []
            atoms.center(vacuum=5.)
            get_surf_ids(atoms)
            return conv_groups, None

        else:
            raise NotImplementedError("Symmetry '{}' is not supported".format(symmetry))

        sorted_indices = np.argsort(np.ravel(dists))
        return sorted_indices, dists[sorted_indices]    
    
    def get_groups(self):
        """Get the groups (a list of lists of atom indices) of all
        symmetry-equivalent atoms."""

        if self.symmetry == 'circular':
            symmetry = 'planar'
        elif self.symmetry == 'mirror_circular':
            symmetry = 'mirror_planar'
        else:
            symmetry = self.symmetry
        indices, dists = self.get_sorted_indices(symmetry=symmetry) 

        if self.symmetry in ['geometrical', 'concentric']:
            groups = indices
        else:
            groups = []
            old_dist = -10.
            for i, dist in zip(indices, dists):
                if abs(dist - old_dist) > self.cutoff:
                    groups.append([i])
                    old_dist = dist
                else:
                    groups[-1].append(i)

        if self.symmetry in ['circular', 'mirror_circular']:
            indices0, dists0 = self.get_sorted_indices(symmetry='cylindrical')
            groups0 = []
            old_dist0 = -10.
            for j, dist0 in zip(indices0, dists0):
                if abs(dist0 - old_dist0) > self.cutoff:
                    groups0.append([j])
                    old_dist0 = dist0
                else:
                    groups0[-1].append(j)

            res = []
            for group in groups:
                res0 = []
                for group0 in groups0:
                    match = [i for i in group if i in group0]
                    if match:
                        res0.append(match)
                res += res0
            groups = res

        if self.secondary_symmetry is not None:
            indices2, dists2 = self.get_sorted_indices(symmetry=
                                                       self.secondary_symmetry)
            if self.secondary_symmetry in ['geometrical', 'concentric']:
                groups2 = indices2
            else:
                groups2 = []
                old_dist2 = -10.
                for j, dist2 in zip(indices2, dists2):
                    if abs(dist2 - old_dist2) > self.secondary_cutoff:
                        groups2.append([j])
                        old_dist2 = dist2
                    else:
                        groups2[-1].append(j)

            res = []
            for group in groups:
                res2 = []
                for group2 in groups2:
                    match = [i for i in group if i in group2]
                    if match:
                        res2.append(match)
                res += res2
            groups = res
 
        return groups

    def run(self, max_gen=None, mode='systematic', eps=0.01, verbose=False):
        """Run the chemical ordering generator.

        Parameters
        ----------
        max_gen : int, default None
            Maximum number of chemical orderings to generate. Running
            forever (until exhaustive for systematic search) if not 
            specified. 

        mode : str, default 'systematic'
            **'systematic'**: enumerate all possible unique chemical 
            orderings. Recommended when there are not many groups. Switch
            to stochastic mode automatically if the number of groups is
            more than 20 (30 if composition is fixed since there are much
            fewer structures).

            **'stochastic'**: sample chemical orderings stochastically.
            Duplicate structures can be generated. Recommended when there 
            are many groups. A greedy algorithm is employed if the 
            composition is fixed, which might result in slightly different
            compositions. This can be controled by eps.

        eps : float, default 0.01
            The tolerance of the concentration for each element (the target 
            concentration range is [c-eps, c+eps]). Only relevant for 
            generating fixed-composition symmetric nanoalloys using 
            'stochastic' mode. Set to a small value, e.g. 0.005, if you 
            want the exact composition accurate to one atom. Please use a 
            larger eps if the concentrations you specified in compositions 
            are not accurate enough.

        verbose : bool, default False 
            Whether to print out information about number of groups and
            number of generated structures.

        """

        traj_mode = 'a' if self.append_trajectory else 'w'
        traj = Trajectory(self.trajectory, mode=traj_mode)
        atoms = self.atoms.copy()
        groups = self.groups
        ngroups = len(groups)
        n_write = 0
        if verbose:
            print('{} symmetry-equivalent groups classified'.format(ngroups))

        if self.composition is not None:
            natoms = len(atoms)
            keys = list(self.composition.keys())
            ratios = list(self.composition.values())

            if mode == 'systematic':
                if ngroups > 30:
                    if verbose:
                        print('{} groups is infeasible for systematic'.format(ngroups), 
                              'generator. Use stochastic generator instead')
                    mode = 'stochastic'

                else:
                    totals = numbers_from_ratios(natoms, ratios) 
                    if max_gen is None:
                        max_gen = -1               

                    for part in partitions_into_totals(groups, totals):
                        for j in range(len(totals)):
                            ids = [i for group in part[j] for i in group] 
                            atoms.symbols[ids] = len(ids) * keys[j]
                        if self.save_groups:
                            if 'data' not in atoms.info:
                                atoms.info['data'] = {}
                            atoms.info['data']['groups'] = groups
                        traj.write(atoms)
                        n_write += 1
                        if n_write == max_gen:
                            break

            if mode == 'stochastic':
                if max_gen is None:
                    max_gen = math.inf
                nele = len(ratios)
                sor = sum(ratios)

                while n_write < max_gen:
                    # get a new random permutation
                    lst = groups.copy()
                    random.shuffle(lst)
                    partition = []                    
                    # starting index (in the permutation) of the current sublist
                    lo = 0
                    # permutation partial sum
                    s = 0
                    # index of sublist we are currently generating (i.e. what ratio we are on)
                    k = 0
                    # ratio partial sum
                    rs = ratios[k]
                    
                    for i in range(ngroups):
                        s += len(lst[i])
                        
                        # if ratio of permutation partial sum exceeds ratio of ratio partial sum,
                        # the current sublist is "complete"
                        if s / natoms >= rs / sor - eps:
                            partition.append(lst[lo:i+1])
                            # start creating new sublist from next element
                            lo = i + 1
                            k += 1
                            if k == nele:
                                # done with partition
                                # remaining elements will always all be zeroes 
                                partition[-1].extend(lst[i+1:])
                                break
                            rs += ratios[k]
                    
                    # continue if there is any empty subset
                    if len(partition) != nele:
                        continue
                    partition = [[i for p in part for i in p] for part in partition]

                    if all(math.isclose(ratios[i] / sor, len(part) / natoms, abs_tol=eps) 
                    for i, part in enumerate(partition)):
                        for j in range(nele):
                            ids = partition[j]
                            atoms.symbols[ids] = len(ids) * keys[j]
                        if self.save_groups:
                            if 'data' not in atoms.info:
                                atoms.info['data'] = {}
                            atoms.info['data']['groups'] = groups
                        traj.write(atoms)
                        n_write += 1

        else: 
            # When the number of groups is too large (> 20), systematic enumeration 
            # is not feasible. Stochastic sampling is the only option
            if mode == 'systematic':
                if ngroups > 20:
                    if verbose:
                        print('{} groups is infeasible for systematic'.format(ngroups), 
                              'generator. Use stochastic generator instead')
                    mode = 'stochastic'
                else:    
                    combos = list(product(self.elements, repeat=ngroups))
                    random.shuffle(combos)
                    for combo in combos:
                        for j, spec in enumerate(combo):
                            atoms.symbols[groups[j]] = spec
                        if self.save_groups:
                            if 'data' not in atoms.info:
                                atoms.info['data'] = {}
                            atoms.info['data']['groups'] = groups
                        traj.write(atoms)
                        n_write += 1
                        if max_gen is not None:
                            if n_write == max_gen:
                                break
 
            if mode == 'stochastic':
                combos = set()
                too_few = (2**ngroups * 0.95 <= max_gen)
                if too_few and verbose:
                    print('Too few groups. Will generate duplicate images.')
                while True:
                    combo = tuple(np.random.choice(self.elements, size=ngroups))
                    if combo not in combos or too_few: 
                        combos.add(combo)
                        for j, spec in enumerate(combo):
                            atoms.symbols[groups[j]] = spec
                        if self.save_groups:                      
                            if 'data' not in atoms.info:
                                atoms.info['data'] = {}
                            atoms.info['data']['groups'] = groups
                        traj.write(atoms)
                        n_write += 1
                        if max_gen is not None:
                            if n_write == max_gen:
                                break
        if verbose:
            print('{} symmetric chemical orderings generated'.format(n_write))


class SymmetricSlabOrderingGenerator(object):
    """`SymmetricSlabOrderingGenerator` is a class for generating 
    symmetric chemical orderings for a **alloy surface slab**. 
    There is no limitation of the number of metal components.
 
    Parameters
    ----------
    atoms : ase.Atoms object
        The surface slab to use as a template to generate symmetric 
        chemical orderings. Accept any ase.Atoms object. No need to 
        be built-in.

    elements : list of strs 
        The metal elements of the alloy catalyst.

    symmetry : str, default 'rotational'
        Support 4 symmetries: 

        **'rotational'**: rotational symmetry with symmetry
        equivalent groups depending on the symmetry_axis.

        **'translational'**: translational symmetry with symmetry 
        equivalent groups depending on repeating_size.

        **'inversion'**: centrosymmetry with symmetry equivalent 
        groups depending on the distance to the geometric center.
        Only works for certain number of slab layers (e.g. 5) and 
        orthogonal cell.

        **'mirror'**: mirror plane symmetry with symmetry equivalent
        groups depeneding on the xy plane bisecting the slab. Only
        works for certain number of slab layers (e.g. 5) and orthogonal 
        cell.

    symmetry_axis : numpy.array or list, default None
        The symmetry axis (3d vector) to form symmetric ordering 
        around. Only relevant for rotational symmetry.

    repeating_size : list of ints or tuple of ints, default (1, 1)
        The multiples that describe the size of the repeating pattern
        on the surface. Symmetry-equivalent atoms are grouped by 
        the multiples in the x and y directions. The x or y length of 
        the cell must be this multiple of the distance between each 
        pair of symmetry-equivalent atoms. Larger reducing size 
        generates fewer structures. For translational symmetry please
        change repeating_size to larger numbers.

    composition : dict, default None
        Generate symmetric orderings only at a certain composition. 
        The dictionary contains the metal elements as keys and their 
        concentrations as values. Generate orderings at all compositions 
        if not specified. 

    groups : list of lists, default None
        Provide the user defined symmetry equivalent groups as a list of 
        lists of atom indices. Useful for generating structures with
        symmetries that are not supported.

    save_groups : bool, default False
        Whether to save the site groups in atoms.info['data']['groups'] 
        for each generated structure.

    dtol : float, default 0.01
        The distance tolerance (in Angstrom) when comparing distances. 
        Use a larger value if the structure is distorted.

    ztol : float, default 0.1
        The tolerance (in Angstrom) when comparing z values. Use a 
        larger ztol if the structure is distorted.

    trajectory : str, default 'orderings.traj'
        The name of the output ase trajectory file.

    append_trajectory : bool, default False
        Whether to append structures to the existing trajectory. 

    """

    def __init__(self, atoms, elements,
                 symmetry='rotational',
                 symmetry_axis=None,
                 repeating_size=(1, 1),
                 composition=None,
                 groups=None,
                 save_groups=False,
                 dtol=0.01,
                 ztol=0.1,
                 trajectory='orderings.traj',
                 append_trajectory=False):

        self.atoms = atoms
        self.elements = elements
        self.symmetry = symmetry
        self.symmetry_axis = symmetry_axis
        if self.symmetry_axis is not None:
            self.symmetry_axis = np.asarray(self.symmetry_axis)

        assert is_list_or_tuple(repeating_size) 
        assert len(repeating_size) == 2
        self.repeating_size = repeating_size
        self.save_groups = save_groups
        self.dtol = dtol
        self.ztol = ztol

        self.composition = composition
        if self.composition is not None:
            ks = list(self.composition.keys())
            assert set(ks) == set(self.elements)

        if isinstance(trajectory, str):
            self.trajectory = trajectory                        
        self.append_trajectory = append_trajectory

        if groups is None:                  
            self.groups = self.get_groups()
        else:
            self.groups = groups

    def get_symmetric_pairs(self, atoms):                               
        sa = self.symmetry_axis
        layers = get_layers(atoms, (0, 0, 1), tolerance=self.ztol)[0]
        dd = defaultdict(list)
        for i, layer in enumerate(layers): 
            dd[layer].append(i)
        positions = atoms.positions
        natoms = len(positions)
        indices, sym_pts = [], []
        for idxs in dd.values():
            geo_mid = np.mean(positions[idxs], axis=0)
            sa2 = sa @ sa
            projs = np.sum((positions[idxs] - geo_mid) * sa, 
                            axis=1).reshape((-1,1)) * sa / sa2
            norms = positions[idxs] - geo_mid - projs
            indices += idxs
            sym_pts += (positions[idxs] - 2 * norms).tolist()
        sym_pts = np.asarray([pt for _, pt in sorted(zip(indices, sym_pts))])
        new_indices = np.asarray(list(product(range(natoms), range(natoms))))
        p1 = atoms.positions[new_indices[:,0]]
        p2 = sym_pts[new_indices[:,1]]
        _, ds = find_mic(p1 - p2, atoms.cell, pbc=True)

        pairs = []
        for i in range(0, len(ds), natoms):
            idx1 = [int(i / natoms)]
            idx2 = []
            for j, d in enumerate(ds[i:i+natoms]):
                if i == j:
                    continue
                if np.isclose(0, d, rtol=0., atol=self.dtol):
                    idx2.append(j)
                    break
            pairs.append(sorted(idx1 + idx2))
        return pairs

    def get_x_y_identical_pairs(self, atoms):
        xy_atoms = atoms.copy()
        xy_atoms.positions[:,2] = 1
        ds = xy_atoms.get_all_distances(mic=True)
        return np.column_stack(np.where(ds < self.dtol)).tolist() 

    def get_lx_ly_identical_pairs(self, atoms):
        ds = atoms.get_all_distances(mic=True)
        cell = atoms.cell
        x_cell = np.linalg.norm(cell[0])
        y_cell = np.linalg.norm(cell[1])
                                                                              
        ref_x_dist = x_cell / self.repeating_size[0]
        ref_y_dist = y_cell / self.repeating_size[1]
        x_pairs = np.column_stack(np.where(abs(ds - ref_x_dist) < self.dtol))
        y_pairs = np.column_stack(np.where(abs(ds - ref_y_dist) < self.dtol))
        return x_pairs.tolist() + y_pairs.tolist()

    def get_collinear_pairs(self, atoms):
        atoms.center()
        geo_mid = [(atoms.cell/2.)[0][0], (atoms.cell/2.)[1][1],                
                   (atoms.cell/2.)[2][2]]
        vecs, _ = find_mic(atoms.positions - np.asarray([geo_mid]), 
                           atoms.cell, pbc=True)
        # Generate the i, j indices
        rows, cols = np.triu_indices(len(vecs), 1)
        # Find the cross products using numpy indexing on vecs
        cross = np.cross(vecs[rows], vecs[cols])
        # Find the values that are close 
        arg = np.argwhere(np.isclose(0, (cross * cross).sum(axis=1)**0.5, 
                          rtol=0, atol=self.dtol))
        # Get the i, j indices where is close to 0
        return np.hstack([rows[arg], cols[arg]]).tolist(), geo_mid            

    def get_groups(self):
        """Get the groups (a list of lists of atom indices) of all
        symmetry-equivalent atoms."""

        atoms = self.atoms.copy()
        if self.symmetry == 'rotational':
            assert self.symmetry_axis is not None
            pairs = self.get_symmetric_pairs(atoms)

        elif self.symmetry == 'translational':
            if self.repeating_size[0] * self.repeating_size[1] == 1:
                raise ValueError('Please set repeating_size larger than (1, 1) ' + 
                                 'for translational symmetry') 
            pairs = self.get_lx_ly_identical_pairs(atoms)  
            z_positions = atoms.positions[:,2]
            pairs = [p for p in pairs if abs(z_positions[p[0]] -
                     z_positions[p[1]]) < self.ztol]

        elif self.symmetry == 'inversion':
            pairs, geo_mid = self.get_collinear_pairs(atoms)
            atoms.center()
            positions = atoms.positions
            cell = atoms.cell
            pairs = [p for p in pairs if abs(get_mic(positions[p[0]], geo_mid, cell, 
                     return_squared_distance=True)**0.5 - get_mic(positions[p[1]], 
                     geo_mid, cell, return_squared_distance=True)**0.5) < self.dtol]

        elif self.symmetry == 'mirror':
            pairs = self.get_x_y_identical_pairs(atoms)
            atoms.center()
            z_positions = atoms.positions[:,2]
            mid_z = (atoms.cell/2.)[2][2]
            pairs = [p for p in pairs if abs(abs(z_positions[p[0]] - mid_z) - 
                     abs(z_positions[p[1]] - mid_z)) < self.ztol]
            
        def to_edges(lst):
            it = iter(lst)
            last = next(it) 
            for current in it:
                yield last, current
                last = current    
        G = nx.Graph()
        for p in pairs:
            G.add_nodes_from(p)
            G.add_edges_from(to_edges(p))
        groups = [list(cc) for cc in list(connected_components(G))]
        uni = {i for group in groups for i in group}
        addition = [[i] for i in set(range(len(atoms))) - uni]
        groups += addition

        return groups

    def run(self, max_gen=None, mode='systematic', eps=0.01, verbose=False):
        """Run the chemical ordering generator.

        Parameters
        ----------
        max_gen : int, default None
            Maximum number of chemical orderings to generate. Running
            forever (until exhaustive for systematic search) if not 
            specified. 

        mode : str, default 'systematic'
            **'systematic'**: enumerate all possible unique chemical 
            orderings. Recommended when there are not many groups. Switch
            to stochastic mode automatically if the number of groups is
            more than 20 (30 if composition is fixed since there are much
            fewer structures).

            **'stochastic'**: sample chemical orderings stochastically.
            Duplicate structures can be generated. Recommended when there 
            are many groups. A greedy algorithm is employed if the 
            composition is fixed, which might result in slightly different
            compositions. This can be controled by eps.

        eps : float, default 0.01
            The tolerance of the concentration for each element (the target 
            concentration range is [c-eps, c+eps]). Only relevant for 
            generating fixed-composition symmetric nanoalloys using 
            'stochastic' mode. Set to a small value, e.g. 0.005, if you 
            want the exact composition accurate to one atom. Please use a 
            larger eps if the concentrations you specified in compositions 
            are not accurate enough.

        verbose : bool, default False 
            Whether to print out information about number of groups and
            number of generated structures.

        """

        traj_mode = 'a' if self.append_trajectory else 'w'
        traj = Trajectory(self.trajectory, mode=traj_mode)
        atoms = self.atoms.copy()
        groups = self.groups
        ngroups = len(groups)
        n_write = 0
        if verbose:
            print('{} symmetry-equivalent groups classified'.format(ngroups))

        if self.composition is not None:
            natoms = len(atoms)
            keys = list(self.composition.keys())
            ratios = list(self.composition.values())

            if mode == 'systematic':
                if ngroups > 30:
                    if verbose:
                        print('{} groups is infeasible for systematic'.format(ngroups), 
                              'generator. Use stochastic generator instead')
                    mode = 'stochastic'
                else:
                    totals = numbers_from_ratios(natoms, ratios)
                    if max_gen is None:
                        max_gen = -1             
   
                    for part in partitions_into_totals(groups, totals):
                        for j in range(len(totals)):
                            ids = [i for group in part[j] for i in group] 
                            atoms.symbols[ids] = len(ids) * keys[j]
                        if self.save_groups:
                            if 'data' not in atoms.info:
                                atoms.info['data'] = {}
                            atoms.info['data']['groups'] = groups
                        traj.write(atoms)
                        n_write += 1
                        if n_write == max_gen:
                            break

            if mode == 'stochastic':
                if max_gen is None:
                    max_gen = math.inf
                nele = len(ratios)
                sor = sum(ratios)

                while n_write < max_gen:
                    # get a new random permutation
                    lst = groups.copy()
                    random.shuffle(lst)
                    partition = []                    
                    # starting index (in the permutation) of the current sublist
                    lo = 0
                    # permutation partial sum
                    s = 0
                    # index of sublist we are currently generating (i.e. what ratio we are on)
                    k = 0
                    # ratio partial sum
                    rs = ratios[k]
                    
                    for i in range(ngroups):
                        s += len(lst[i])
                        
                        # if ratio of permutation partial sum exceeds ratio of ratio partial sum,
                        # the current sublist is "complete"
                        if s / natoms >= rs / sor - eps:
                            partition.append(lst[lo:i+1])
                            # start creating new sublist from next element
                            lo = i + 1
                            k += 1
                            if k == nele:
                                # done with partition
                                # remaining elements will always all be zeroes 
                                partition[-1].extend(lst[i+1:])
                                break
                            rs += ratios[k]
                    
                    # continue if there is any empty subset
                    if len(partition) != nele:
                        continue
                    partition = [[i for p in part for i in p] for part in partition]

                    if all(math.isclose(ratios[i] / sor, len(part) / natoms, abs_tol=eps) 
                    for i, part in enumerate(partition)):
                        for j in range(nele):
                            ids = partition[j]
                            atoms.symbols[ids] = len(ids) * keys[j]
                        if self.save_groups:
                            if 'data' not in atoms.info:
                                atoms.info['data'] = {}
                            atoms.info['data']['groups'] = groups
                        traj.write(atoms)
                        n_write += 1

        else: 
            # When the number of groups is too large (> 20), systematic enumeration 
            # is not feasible. Stochastic sampling is the only option
            if mode == 'systematic':
                if ngroups > 20:
                    if verbose:
                        print('{} groups is infeasible for systematic'.format(ngroups), 
                              'generator. Use stochastic generator instead')
                    mode = 'stochastic'
                else:    
                    combos = list(product(self.elements, repeat=ngroups))
                    random.shuffle(combos)
                    for combo in combos:
                        for j, spec in enumerate(combo):
                            atoms.symbols[groups[j]] = spec
                        if self.save_groups:
                            if 'data' not in atoms.info:
                                atoms.info['data'] = {}
                            atoms.info['data']['groups'] = groups
                        traj.write(atoms)
                        n_write += 1
                        if max_gen is not None:
                            if n_write == max_gen:
                                break
 
            if mode == 'stochastic':
                combos = set()
                too_few = (2**ngroups * 0.95 <= max_gen)
                if too_few and verbose:
                    print('Too few groups. Will generate duplicate images.')
                while True:
                    combo = tuple(np.random.choice(self.elements, size=ngroups))
                    if combo not in combos or too_few: 
                        combos.add(combo)
                        for j, spec in enumerate(combo):
                            atoms.symbols[groups[j]] = spec
                        if self.save_groups:
                            if 'data' not in atoms.info:
                                atoms.info['data'] = {}
                            atoms.info['data']['groups'] = groups
                        traj.write(atoms)
                        n_write += 1
                        if max_gen is not None:
                            if n_write == max_gen:
                                break
        if verbose:
            print('{} symmetric chemical orderings generated'.format(n_write))


class RandomOrderingGenerator(object):
    """`RandomOrderingGenerator` is a class for generating random 
    chemical orderings for an alloy catalyst. The function is 
    generalized for both periodic and non-periodic systems, and 
    there is no limitation of the number of metal components.
 
    Parameters
    ----------
    atoms : ase.Atoms object
        The nanoparticle or surface slab to use as a template to
        generate random chemical orderings. Accept any ase.Atoms 
        object. No need to be built-in.

    elements : list of strs 
        The metal elements of the alloy catalyst.

    composition : dict, default None
        Generate random orderings only at a certain composition.
        The dictionary contains the metal elements as keys and 
        their concentrations as values. Generate orderings at all 
        compositions if not specified.

    trajectory : str, default 'orderings.traj'
        The name of the output ase trajectory file.

    append_trajectory : bool, default False
        Whether to append structures to the existing trajectory. 

    """

    def __init__(self, atoms, elements,
                 composition=None,
                 trajectory='orderings.traj',
                 append_trajectory=False):

        self.atoms = atoms
        self.elements = elements
        self.composition = composition
        if self.composition is not None:
            ks = list(self.composition.keys())
            assert set(ks) == set(self.elements)
            vs = list(self.composition.values())
            nums = numbers_from_ratios(len(self.atoms), vs)
            self.num_dict = {ks[i]: nums[i] for i in range(len(ks))}

        if isinstance(trajectory, str):
            self.trajectory = trajectory                        
        self.append_trajectory = append_trajectory

    def randint_with_sum(self):
        """Return a randomly chosen list of N positive integers i
        summing to the number of atoms. N is the number of elements.
        Each such list is equally likely to occur."""

        N = len(self.elements)
        total = len(self.atoms)
        dividers = sorted(random.sample(range(1, total), N - 1))
        return [a - b for a, b in zip(dividers + [total], [0] + dividers)]

    def random_split_indices(self):
        """Generate random chunks of indices given sizes of each 
        chunk."""

        indices = list(range(len(self.atoms)))
        random.shuffle(indices)
        res = {}
        pointer = 0
        for k, v in self.num_dict.items():
            res[k] = indices[pointer:pointer+v]
            pointer += v

        return res

    def run(self, num_gen):
        """Run the chemical ordering generator.

        Parameters
        ----------
        num_gen : int
            Number of chemical orderings to generate.

        """

        traj_mode = 'a' if self.append_trajectory else 'w'
        traj = Trajectory(self.trajectory, mode=traj_mode)
        atoms = self.atoms
        natoms = len(atoms)

        for _ in range(num_gen):
            if self.composition is None:
                rands = self.randint_with_sum()
                self.num_dict = {e: rands[i] for i, e in 
                                 enumerate(self.elements)}
            chunks = self.random_split_indices()    
            indi = atoms.copy()
            for e, ids in chunks.items():
                indi.symbols[ids] = e
            traj.write(indi)
