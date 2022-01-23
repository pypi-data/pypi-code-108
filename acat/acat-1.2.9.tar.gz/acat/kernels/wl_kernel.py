from acat.utilities import (neighbor_shell_list, 
                            get_adj_matrix, 
                            hash_composition)
from multiprocessing import Pool
from itertools import chain, combinations
from functools import partial
import networkx as nx
import numpy as np
import os


class WL(object):

    def __init__(self,
                 hp={'length': np.array([.75, .25]), 't': 2},
                 normalize=False,
                 connect_nn=False,
                 n_jobs=os.cpu_count()):
        self.hp = hp
        self.set_hyperparams(hp)
        self.normalize = normalize
        self.connect_nn = connect_nn
        self.n_jobs = n_jobs

    def set_hyperparams(self, new_params):
        """Set or update the hyperparameters for the Kernel.

        Parameters
        ----------
        new_params: dictionary
            A dictionary of hyperparameters that are added or updated.
        """
        self.hp.update(new_params)
#        if 'alpha' not in self.hp:
#            self.hp['alpha'] = np.array([.75])
        if 'length' not in self.hp:
            self.hp['length'] = np.array([200.])

        # Lower and upper machine precision
        eps_mach_lower = np.sqrt(1.01 * np.finfo(float).eps)
        eps_mach_upper = 1 / eps_mach_lower
        self.hp['length'] = np.abs(self.hp['length']).reshape(-1)
#        self.hp['alpha'] = np.abs(self.hp['alpha']).reshape(-1)
        self.hp['length'] = np.where(self.hp['length'] < eps_mach_upper, 
                                     np.where(self.hp['length'] > eps_mach_lower, 
                                              self.hp['length'], eps_mach_lower), 
                                     eps_mach_upper)
#        self.hp['alpha'] = np.where(self.hp['alpha'] < eps_mach_upper, 
#                                    np.where(self.hp['alpha'] > eps_mach_lower, 
#                                             self.hp['alpha'], eps_mach_lower), 
#                                    eps_mach_upper)
        return self.hp

    def dist_m(self, train_images, test_images=None):
        dists = self.__call__(train_images, test_images, get_dists=True)

        return dists

    def __call__(self, train_images, test_images=None, get_derivatives=False, 
                 get_dists=False, dists=None):
        if test_images is None:
            images = list(train_images)
        else:
            images = list(train_images) + list(test_images)
        if dists is None:                                      
            pool = Pool(self.n_jobs)
            dicts = pool.map(self.get_dict, images)
#            for d in dicts:
#                all_keys = set(chain.from_iterable(dicts))   
#                old_keys = d.keys()
#                d.update((k, 0) for k in all_keys - old_keys)
            dicts = np.asarray(dicts, dtype=object)
            if get_dists:
                t = self.hp['t']                                                    
                Kdts = [np.zeros(shape=(len(dicts), len(dicts)))] * t
                idx0dt, idx1dt = np.triu_indices_from(Kdts[0])
                for idt in range(len(idx0dt)):
                    i0, i1 = idx0dt[idt], idx1dt[idt]
                    for k in set(dicts[i0]).intersection(set(dicts[i1])):
                        maxrep = count = 0
                        current = ''
                        for c in k:
                            if c == current == ':':
                                count += 1
                            else:
                                count = 1
                                current = c
                            maxrep = max(count, maxrep)
                        Kdts[maxrep-1][i0,i1] += 1
                for j, Kdt in enumerate(Kdts):                   
                    Kdts[j] = Kdt + Kdt.T - np.diag(np.diag(Kdt))
                Kdts = np.asarray(Kdts)
                if t == 1:
                    Kdts = Kdts[0]
                dists = (dicts, Kdts)
                return dists
        else:
            dicts = dists[0]
#            print('length: {}'.format(self.hp['length']))
#            print('alpha: {}'.format(self.hp['alpha']))
#            print('noise: {}'.format(self.hp['noise']))

        # Initialize the similarity kernel
        K = np.zeros(shape=(len(images), len(images)))
        # Iterate through upper triangular matrix indices
        idx0, idx1 = np.triu_indices_from(K)
        # Perform similarity calculations in parallel.
        pool = Pool(self.n_jobs)
        po = partial(self.pairwise_operation)
        sims = pool.starmap(po, zip(dicts[idx0], dicts[idx1]))

        # Insert it into K[i,j] and K[j,i]
        for i, sim in enumerate(sims):
            K[idx0[i],idx1[i]] = sim
        # Symmetrize
        K = K + K.T - np.diag(np.diag(K))
        # Normalize
        if self.normalize:
            d = np.diag(K)**-0.5
            K = np.einsum("i,ij,j->ij", d, K, d)
        # Take the upper right rectangle if there are test images
        if test_images is not None:
            K = K[:len(train_images),len(train_images):len(images)] 

        return K

    def get_hyperparameters(self):
        "Get all the hyperparameters"
        return self.hp 

    def get_dict(self, atoms):
        d = {} 
        numbers = atoms.numbers
        nblist = neighbor_shell_list(atoms, dx=0.3, neighbor_number=1, 
                                     mic=(True in atoms.pbc))
        A = get_adj_matrix(nblist)
        G = nx.from_numpy_matrix(A) 
        if 't' in self.hp:
            t = self.hp['t']
        else:
            t = 2

        nnlabs, neighbors, lpd = {}, {}, {}
        isolates = []
        for i in range(len(A)):
            lab0 = str(numbers[i])
            if lab0 in d:
                d[lab0] += 1.
            else:
                d[lab0] = 1.

            if t > 0:
                nnd = nx.single_source_shortest_path_length(G, i, cutoff=1)
                nns = [j for j, v in nnd.items() if v == 1]
                neighbors[i] = nns
                if len(nns) == 0:
                    isolates.append(i)
                    continue
                if self.connect_nn:
                    nnhood = np.asarray([i] + nns)
                    An = A[nnhood,:][:,nnhood]
                    Gn = nx.from_numpy_matrix(An)
                    # An algorithm to find the lexicographically minimum 
                    # longest path starts from node and ends at a neighbor
                    maxlen = 0
                    longest_paths = []
  
                    for ani, anj in combinations(range(len(An)), 2):
                        paths = nx.all_simple_paths(Gn, source=ani, target=anj)
                        for path in paths:
                            length = len(path)
                            if length > maxlen:
                                longest_paths = [path]
                                maxlen = length
                            elif length == maxlen:
                                longest_paths.append(path)
                    mint = min(((idx, hash_composition(numbers[nnhood[lp]])) for idx, lp 
                                in enumerate(longest_paths)), key=lambda x: x[1])
                    longest_path = longest_paths[mint[0]]
                    sorted_numbers = mint[1]
                    lpd[i] = longest_path
                else:
                    sorted_numbers = sorted(numbers[nns])
                lab1 = lab0 + ':' + ','.join(map(str, sorted_numbers))
                nnlabs[i] = lab1
                if lab1 in d:
                    d[lab1] += self.hp['length'][0] 
                else:
                    d[lab1] = self.hp['length'][0]
#            print(sorted(d.keys()))

        if t > 1: 
            for k in range(1, t):
                nnnlabs = {}
                for i in range(len(A)):
                    if i in isolates:
                        continue
                    nnlab = nnlabs[i]
                    if self.connect_nn:
                        nnnlab = ','.join([nnlabs[nn] for nn in lpd[i]])
                    else:
                        nnnlab = ','.join(sorted(nnlabs[nn] for nn in neighbors[i]))
                    lab = nnlab + ':' * (k + 1) + nnnlab
                    nnnlabs[i] = lab
                    if lab in d:
                        d[lab] += self.hp['length'][k]
                    else:
                        d[lab] = self.hp['length'][k]
                nnlabs = nnnlabs 
#                print(sorted(d.keys()))

        return d

    def get_derivatives(self, train_images, hp, KXX=None, dists=None):                 
        """Get the derivatives of the kernel matrix in respect to the 
        hyperparameters.

        Parameters
        ----------
        train_images : list of ase.Atoms
            N training images.
        hp : list
            A list with hyperparameters to calculate derivatives.
        KXX : (N,N) array (optional)
            The kernel matrix of training data.
        dists : (N,N) array (optional)
            Can be given the distance matrix to avoid recaulcating it. 
        """
        assert not self.normalize
        hp_deriv = {}
        if 'length' in hp:
            if dists is None:                                      
                pool = Pool(self.n_jobs)
                dicts = pool.map(self.get_dict, train_images)
                dicts = np.asarray(dicts, dtype=object)
                t = self.hp['t']                                                     
                Kdts = [np.zeros(shape=(len(dicts), len(dicts)))] * t
                idx0dt, idx1dt = np.triu_indices_from(Kdt)
                for idt in range(len(idx0dt)):
                    i0, i1 = idx0dt[idt], idx1dt[idt]
                    for k in set(dicts[i0]).intersection(set(dicts[i1])):
                        maxrep = count = 0
                        current = ''
                        for c in k:
                            if c == current == ':':
                                count += 1
                            else:
                                count = 1
                                current = c
                            maxrep = max(count, maxrep)
                        Kdts[maxrep-1][i0,i1] += 1
                for j, Kdt in enumerate(Kdts):                   
                    Kdts[j] = Kdt + Kdt.T - np.diag(np.diag(Kdt))
                Kdts = np.asarray(Kdts)
                if t == 1:
                    Kdts = Kdts[0]
            else:
                Kdts = dists[1]
        hp_deriv['length'] = Kdts

        return hp_deriv

    def pairwise_operation(self, dx, dy):
        """Compute pairwise similarity between every two dicts."""

        dxy = {k: [d[k] if k in d else 0 for d in (dx, dy)] 
               for k in set(dx.keys()) | set(dy.keys())}
        X = np.asarray(list(dxy.values()))
 
       # Inner product
        k = X[:,0] @ X[:,1].T

        # Exponential
#        k = np.exp(-np.linalg.norm(X[:,0] - X[:,1]) / self.hp['length'][0]**2)

        # Square exponential
#        k = np.exp(-np.sum((X[:,0] - X[:,1])**2) / (2 * self.hp['length'][0]**2))

        return k

    def diag(self, test_images, get_derivatives=False):
        """Get the diagonal kernel vector.

        Parameters
        ----------
        test_images : (N,N) array
            Test images with N structures.
        """

        if self.normalize:
            return np.ones(len(test_images))

        K = self.__call__(train_images=test_images)
        return np.diag(K)

    def __repr__(self):
        return 'WL(hp={})'.format(self.hp)
