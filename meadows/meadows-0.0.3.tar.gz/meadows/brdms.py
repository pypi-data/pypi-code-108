from collections import Counter
from copy import deepcopy
import numpy as np
from scipy.spatial.distance import squareform
from meadows.align import _mean, _align
from pyrsa.rdm.rdms import RDMs


class BehavioralRDMs(RDMs):
    """Behavioral RDMs class

    Args:
        dissimilarities (numpy.ndarray):
            either a 2d np-array (n_rdm x vectorform of dissimilarities)
            or a 3d np-array (n_rdm x n_cond x n_cond)
        dissimilarity_measure (String):
            a description of the dissimilarity measure (e.g. 'Euclidean')
        descriptors (dict):
            descriptors with 1 value per RDMs object
        rdm_descriptors (dict):
            descriptors with 1 value per RDM
        pattern_descriptors (dict):
            descriptors with 1 value per RDM column

    Attributes:
        n_rdm(int): number of rdms
        n_cond(int): number of patterns
    """

    def reorder(self, new_order):
        """Reorder the patterns according to the index in new_order

        Args:
            new_order (numpy.ndarray): new order of patterns,
                vector of length equal to the number of patterns
        """
        matrices = self.get_matrices()
        matrices = matrices[(slice(None),) + np.ix_(new_order, new_order)]
        self.dissimilarities = batch_to_vectors(matrices)[0]
        for dname, descriptors in self.pattern_descriptors.items():
            self.pattern_descriptors[dname] = descriptors[new_order]

    def sort_by(self, **kwargs):
        """Reorder the patterns by sorting a descriptor

        Pass keyword arguments that correspond to descriptors,
        with value 'alpha'. 

        Example:
            Sorts the condition descriptor alphabetically:

            `rdms.sort(condition='alpha')`

        Raises:
            ValueError: Raised if the method chosen is not implemented
        """
        for dname, method in kwargs.items():
            if method == 'alpha':
                descriptor = self.pattern_descriptors[dname]
                self.reorder(np.argsort(descriptor))
            else:
                raise ValueError(f'Unknown sorting method: {method}')

    @classmethod
    def expand(cls, list_of_rdms, all_patterns=None, descriptor='conds'):
        """Make larger RDMs with missing values where needed

        Any object-level descriptors will be turned into rdm_descriptors
        if they do not match across objects.

        Args:
            list_of_rdms (list): List of RDMs objects
            all_patterns (list, optional): The full list of pattern
                descriptors. Defaults to None, in which case the full
                list is the union of all input rdms' values for the
                pattern descriptor chosen.
            descriptor (str, optional): The pattern descriptor on the basis
                of which to expand. Defaults to 'conds'.

        Returns:
            RDMs: Object containing all input rdms on the larger scale,
                with missing values where required
        """

        def pdescs(rdms, descriptor):
            return list(rdms.pattern_descriptors.get(descriptor, []))

        if all_patterns is None:
            all_patterns = []
            for rdms in list_of_rdms:
                all_patterns += pdescs(rdms, descriptor)
            all_patterns = list(dict.fromkeys(all_patterns).keys())

        n_rdm_objs = len(list_of_rdms)
        n_rdms = sum([rdms.n_rdm for rdms in list_of_rdms])
        n_patterns = len(all_patterns)

        desc_tuples = []
        rdm_desc_names = []
        for rdms in list_of_rdms:
            desc_tuples += list(rdms.descriptors.items())
            rdm_desc_names += list(rdms.rdm_descriptors.keys())
        descriptors = dict(
            [d for d, c in Counter(desc_tuples).items() if c == n_rdm_objs]
        )
        desc_diff_names = set(
            [d[0] for d, c in Counter(desc_tuples).items() if c != n_rdm_objs]
        )
        rdm_desc_names = set(rdm_desc_names + list(desc_diff_names))
        rdm_descriptors = dict([(n, [None]*n_rdms) for n in rdm_desc_names])

        measure = None
        vector_len = int(n_patterns * (n_patterns-1) / 2)
        vectors = np.full((n_rdms, vector_len), np.nan)
        rdm_id = 0
        for rdms in list_of_rdms:
            measure = rdms.dissimilarity_measure
            pidx = [all_patterns.index(i) for i in pdescs(rdms, descriptor)]
            for rdm_local_id, utv in enumerate(rdms.dissimilarities):
                rdm = np.full((len(all_patterns), len(all_patterns)), np.nan)
                rdm[np.ix_(pidx, pidx)] = squareform(utv, checks=False)
                vectors[rdm_id, :] = squareform(rdm, checks=False)
                for name in rdm_descriptors.keys():
                    if name in rdms.rdm_descriptors:
                        val = rdms.rdm_descriptors[name][rdm_local_id]
                        rdm_descriptors[name][rdm_id] = val
                    elif name in rdms.descriptors:
                        rdm_descriptors[name][rdm_id] = rdms.descriptors[name]
                rdm_id += 1

        return RDMs(
            dissimilarities=vectors,
            dissimilarity_measure=measure,
            descriptors=descriptors,
            rdm_descriptors=rdm_descriptors,
            pattern_descriptors=dict([(descriptor, all_patterns)])
        )

    def align(self, method='evidence'):
        """Bring RDMs closer together

        Iteratively scales RDMs based on pairs in-common.
        Also adds an RDM descriptor with the weights used.

        Args:
            method (str, optional): One of 'evidence', 'setsize' or
                'simple'. Defaults to 'evidence'.

        Returns:
            RDMs: RDMs object with the aligned RDMs
        """
        aligned, weights = _align(self.dissimilarities, method)
        rdm_descriptors = deepcopy(self.rdm_descriptors)
        if weights is not None:
            rdm_descriptors['weights'] = weights
        return RDMs(
            dissimilarities=aligned,
            dissimilarity_measure=self.dissimilarity_measure,
            descriptors=deepcopy(self.descriptors),
            rdm_descriptors=rdm_descriptors,
            pattern_descriptors=deepcopy(self.pattern_descriptors)
        )

    def mean(self, weights='stored'):
        """Average rdm of all rdms contained

        Args:
            weights (str or ndarray, optional): One of:
                'stored': Use the weights contained in `rdm_descriptor` "weights"
                ndarray: Weights array of the shape of RDMs.dissimilarities
                None: No weighting applied

        Returns:
            `pyrsa.rdm.rdms.RDMs`: New RDMs object with one vector
        """
        if weights == 'stored':
            weights = self.rdm_descriptors.get('weights')
        new_descriptors = dict(
            [(k, v) for (k, v) in self.descriptors.items() if k != 'weights']
        )
        return RDMs(
            dissimilarities=np.array([_mean(self.dissimilarities, weights)]),
            dissimilarity_measure=self.dissimilarity_measure,
            descriptors=new_descriptors,
            pattern_descriptors=deepcopy(self.pattern_descriptors)
        )
