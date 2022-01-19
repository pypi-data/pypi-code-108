# -*- coding: utf-8 -*-
"""
Functions to register datasets for multiclass image classification.
Expects folder structure ./<classname>/[images]
"""
from dataclasses import dataclass
from itertools import combinations, permutations
from copy import deepcopy
from typing import Callable, Iterable, Union, Tuple, Dict, Set
import numpy as np
from scipy.spatial.distance import pdist
from scipy.stats import skewnorm
import torch
from torch import nn
from functools import lru_cache

class TripletGenerator:
    """Class to generate (anchor, positive_example, negative_example) triplets.

    This class supports various ways to generate triplets usable for learning with triplet loss.
    """

    @dataclass
    class Subset:
        """Class representing a subset of TripletGenerator.data.

        Normally instances of the class are generate through TripletGenerator.sample_subset(...).

        Attributes
        ----------
        base_set: TripletGenerator
            The TripletGenerator from which the subset was sampled.
        indeices: np.array of ints
            Indices of the subset examples
        example_vectors: np.array or None, optional, default=None
            Feature vectors of the examples
        """


        base_set: "TripletGenerator"
        indices: np.ndarray
        example_vectors: np.ndarray = None

        def build_maxmin_triplets(self, metric: Union[str, Callable]='euclidean', **kwargs) -> Tuple['np.array', 'np.array', 'np.array']:
            """Build the hardest triplet in the dataset.

            For the hardest triplets the distance between anchor and the positive example
            is maximized and the distance between anchor and the negative example is minized.
            To calculate the distance scipy.distance.pdist is used. See its documentation for details.

            Parameters
            ----------
            metric: str or callable
                Metric used for the pdist call.
                Check scipy.distance.pdist documentation
            **kwargs
                All keywords are passed to pdist call.

            Returns
            -------
            np.array
                Anchor indices
            np.array
                Positive example indices
            np.array
                Negative example indices
            """
            if self.example_vectors is None:
                raise ValueError('Please provide example_vectors through the \'set_example_vectors\' functions!')
            dist_matrix = pdist(self.example_vectors, metric=metric, **kwargs)
            pos, neg, pos_masks = [], [], {}
            class_ids_set = self.class_ids
            for idx in range(len(self.indices)):
                indices_pos, indices_feat_pos = _get_indices_pdist_matrix_condensed(class_ids_set, idx, pos_masks, same_class=True, use_torch=False)
                pos.append(self.indices[indices_feat_pos[np.argmax(dist_matrix[indices_pos])]])
                indices_neg, indices_feat_neg = _get_indices_pdist_matrix_condensed(class_ids_set, idx, pos_masks, same_class=False, use_torch=False)
                neg.append(self.indices[indices_feat_neg[np.argmin(dist_matrix[indices_neg])]])
            return self.indices, np.array(pos), np.array(neg)

        @property
        def class_ids(self) -> 'np.array':
            return self.base_set.class_ids[self.indices]

        def build_all_possible_triplets(self, anchor_pos_combinations_unique=False) -> Tuple['np.array', 'np.array', 'np.array']:
            """Build all possible triplets.

            Parameters
            ----------
            anchor_pos_combinations_unique: bool, optional, default=False
                If anchor, pos pairs should be unique.
                If True, (1, 2, 3) and (2, 1, 3) are returned.
                If False, only (1, 2, 3) will returned.

            Returns
            -------
            np.array
                Anchor indices
            np.array
                Positive example indices
            np.array
                Negative example indices
            """
            class_ids_set = self.class_ids
            class_ids_unique = np.unique(class_ids_set)

            triplets = []
            for class_id in class_ids_unique:
                mask = class_ids_set == class_id
                indices_of_class = np.where(mask)[0]
                indices_of_not_class = np.where(np.logical_not(mask))[0]
                if anchor_pos_combinations_unique:
                    ap_pairs = combinations(indices_of_class, 2)
                else:
                    ap_pairs = permutations(indices_of_class, 2)
                triplets.extend([(*pair, idx_neg) for pair in ap_pairs for idx_neg in indices_of_not_class])
            triplets = np.array(triplets)
            return self.indices[triplets[:, 0]], self.indices[triplets[:, 1]], self.indices[triplets[:, 2]]

        def build_random_triplets(self, size, replace=False) -> Tuple['np.array', 'np.array', 'np.array']:
            """Build uniform random triplets

            Parameters
            ----------
            size: int
                Number of triplets.
            replace: bool, optional, default=False
                Sample anchors with replacement.

            Returns
            -------
            np.array
                Anchor indices
            np.array
                Positive example indices
            np.array
                Negative example indices
            """
            class_ids_set = self.class_ids
            anchors, pos, neg = self.base_set.build_random_triplets_for_ids(
                class_ids_set,
                excludes=self.base_set.excludes,
                size=size,
                rng=self.base_set.rng,
                replace=replace)
            return self.indices[anchors], self.indices[pos], self.indices[neg]

        def build_triplets_accourding_to_strategy(self, strategy, dist_norm=2.) -> Tuple['np.array', 'np.array', 'np.array']:
            """Build using 'create_triplets_from_pk_sample'.

            This function is also used inside of the TripletDistanceLearner and supports different
            strategy. Check documentation for the function for more details.

            Parameters
            ----------
            strategy: length 2 tuple of strs or floats between 0. and 1.
                Tuple of strategies (pos_strategy, neg_strategy) used for sampling the positive and
                negative examples. Supported strategies are '*', 'rand', 'min', 'max' or floats
                between 0. and 1.
            dist_norm: float, optional, default=2
                Norm used to calculate the distance.
                Check torch.nn.functional.pdist for details.

            Returns
            -------
            np.array
                Anchor indices
            np.array
                Positive example indices
            np.array
                Negative example indices
            """
            strategy = build_triplet_strategy(strategy)
            triplets = create_triplets_from_pk_sample(torch.from_numpy(self.example_vectors),
                                                     torch.from_numpy(self.class_ids),
                                                     *strategy,
                                                     dist_norm=dist_norm)
            triplets = [i.numpy() for i in triplets]
            return self.indices[triplets[0]], self.indices[triplets[1]], self.indices[triplets[2]]

        def set_example_vectors(self, example_vectors):
            if example_vectors is not None and len(example_vectors) != len(self.indices):
                raise ValueError('The provided example_vectors is not of the same length as the image vector in the subset!')
            self.example_vectors = example_vectors


    def __init__(self,
                 class_ids: Iterable[int],
                 excludes: Union[None, Dict[int, Set]]=None,
                 rng: Union[None, int, 'np.random.Generator']=None,
                 example_vectors: Union[None, 'np.array']=None,
                 global_indices: Union[None, Iterable[int]]=None,
                 ignore_class_weights=False):
        """Create instance of TripletGenerator.

        Parameters
        ----------
        class_ids: Iterable of ints castable to np.array
            Class ids
        excludes: None or dict, optional, default=None
            Triplet exclude dict passed to sampler, if sampler supports it.
            Check sap_computer_vision.data.samplers for more details on the different samplers.
            This parameters is meant for distance metric learning.
        rng: None or int or np.random.Generator, optinal, default=None
            Seed for the np.random.Generator or a np.random.Generator.
            Check https://numpy.org/doc/stable/reference/random/generator.html
            for more infos
        example_vectors: None or np.array, optional, default=None
            Features vectors for all examples. Has to be of same length as
            class_ids.
        global_indices: None or np., optional, default=None
            Indices mappping.
            If None set the first entry of class_ids is returnd as index 0 etc.
            Has to be of same length as class_ids.
        """
        self.class_ids = np.asarray(class_ids)
        self.classes, self.class_counts = np.unique(class_ids, return_counts=True)

        self.ignore_class_weights = ignore_class_weights

        self.use_excludes = excludes is not None
        self.excludes, self.pos_masks_classes, self.pos_example_mask = self._prepare_excludes(class_ids, excludes=excludes)
        self.neg_masks_classes = {}

        if global_indices is not None:
            global_indices = np.asarray(global_indices)
        self.global_indices = global_indices

        if example_vectors is not None:
            example_vectors = np.asarray(example_vectors)
        self.example_vectors = example_vectors
        if not isinstance(rng, np.random.Generator):
            if isinstance(rng, int) and rng < 0:
                rng = None
            rng = np.random.default_rng(seed=rng)
        self.rng = rng

    def _adjust_class_weights(self, new_class, class_weights=None):
        if class_weights is None:
            class_weights = self.class_counts.copy()
        excluded_classes = self.excludes.get(new_class, set()).union(set([new_class]))
        class_weights_mask = [c_i in excluded_classes for c_i in self.classes]
        w_excluded = np.sum(class_weights[class_weights_mask])
        if w_excluded == np.sum(class_weights):
            raise ValueError('Excludes led to 0 remaining classes! Please relax the excludes!')
        class_weights[class_weights_mask] = 0.
        class_weights /= (1 - w_excluded)
        return class_weights


    def sample_subset(self, p: int, k: int, ignore_class_weights: bool=False) -> 'TripletGenerator.Subset':
        """Sample a subset containing p classes with k examples each.

        Parameters
        ----------
        p: int
            Number of classes in the subset.
        k: int
            Number of examples in the subset.
        ignore_class_weights: bool, optinal, default=False
            Whether class_weights should be ignored when sampling the subset.

        Returns
        -------
        TripletGenerator.Subset
            Subset containing p classes with k examples each.
        """
        if ignore_class_weights:
            class_weights = np.ones_like(self.class_counts).astype(np.float32)
        else:
            class_weights = self.class_counts.copy().astype(np.float32)
        class_weights[class_weights < k] = 0
        class_weights /= np.sum(class_weights)
        if not self.use_excludes:
            selected_classes = self.rng.choice(self.classes, size=p, p=class_weights, replace=False)
        else:
            selected_classes = [self.rng.choice(self.classes, p=class_weights, replace=False)]
            for i in range(p-1):
                class_weights = self._adjust_class_weights(new_class=selected_classes[-1], class_weights=class_weights)
                selected_classes.append(self.rng.choice(self.classes, p=class_weights, replace=False))
        image_idx = [self.rng.choice(list(self.pos_masks_classes.setdefault(class_id, _create_pos_mask(class_id, self.class_ids))), size=k, replace=False) for class_id in selected_classes]
        indices = np.array([i for image_l in image_idx for i in image_l])
        return TripletGenerator.Subset(base_set=self,
                                       indices=self.global_indices[indices] if self.global_indices is not None else indices,
                                       example_vectors=self.example_vectors[indices] if self.example_vectors is not None else None)

    def build_random_triplets(self, size: int, replace: bool=False) -> Tuple['np.array', 'np.array', 'np.array']:
        """Sample uniform random triplets

        Parameters
        ----------
        size: int
            Number of triplets.
        replace: bool, optional, default=False
            Sample anchors with replacement.

        Returns
        -------
        np.array
            Anchor indices
        np.array
            Positive example indices
        np.array
            Negative example indices
        """
        a, p, n = self._build_random_triplets_for_ids(
            class_ids=self.class_ids,
            examples_mask=self.pos_example_mask,
            excludes=self.excludes,
            size=size,
            rng=self.rng,
            replace=replace,
            pos_masks=self.pos_masks_classes,
            neg_masks=self.neg_masks_classes)
        if self.global_indices is None:
            return a, p, n
        else:
            return self.global_indices[a], self.global_indices[p], self.global_indices[n]

    @staticmethod
    def _prepare_excludes(class_ids, excludes=None, pos_masks=None, force_bidirectional_excludes=True):
        if excludes is None:
            excludes = {}
        else:
            excludes = deepcopy(excludes)
        if pos_masks is None:
            pos_masks = {}

        examples_mask = np.ones_like(class_ids, dtype=bool)
        for c_i, count in zip(*np.unique(class_ids, return_counts=True)):
            try:
                e_i = excludes[c_i]
            except KeyError:
                e_i = set([c_i])
            else:
                e_i = set(e_i).union(set([c_i]))
            excludes[c_i] = e_i
            if force_bidirectional_excludes:
                for c_ij in excludes[c_i]:
                    if c_ij != c_i:
                        try:
                            e_j = excludes[c_ij]
                        except KeyError:
                            e_j = set([c_i])
                        else:
                            e_j = set(e_j).union(set([c_i]))
                        excludes[c_ij] = e_j
            if count == 1:
                pos_mask = pos_masks.setdefault(c_i, _create_pos_mask(c_i, class_ids))
                examples_mask[list(pos_mask)] = False
        return excludes, pos_masks, examples_mask

    @staticmethod
    def build_random_triplets_for_ids(class_ids, excludes=None, size=1, rng=None, replace=True):
        """Static function to generate uniform random triplets.

        Parameters
        ----------
        class_ids: Iterable of ints castable to np.array
            Class ids
        excludes: None or dict, optional, default=None
            Triplet exclude dict passed to sampler, if sampler supports it.
            Check sap_computer_vision.data.samplers for more details on the different samplers.
            This parameters is meant for distance metric learning.
        rng: None or int or np.random.Generator, optinal, default=None
            Seed for the np.random.Generator or a np.random.Generator.
            Check https://numpy.org/doc/stable/reference/random/generator.html
            for more infos
        size: int
            Number of triplets.
        replace: bool, optional, default=False
            Sample anchors with replacement.

        Returns
        -------
        np.array
            Anchor indices
        np.array
            Positive example indices
        np.array
            Negative example indices
        """
        excludes, pos_masks, examples_mask= TripletGenerator._prepare_excludes(class_ids=class_ids, excludes=excludes)
        neg_masks = {}
        if not isinstance(rng, np.random.Generator):
            rng = np.random.default_rng(seed=rng)
        return TripletGenerator._build_random_triplets_for_ids(class_ids=class_ids,
                                                               examples_mask=examples_mask,
                                                               excludes=excludes,
                                                               size=size,
                                                               rng=rng,
                                                               replace=replace,
                                                               pos_masks=pos_masks,
                                                               neg_masks=neg_masks)

    @staticmethod
    def _build_random_triplets_for_ids(class_ids, examples_mask, excludes, size, rng, replace, pos_masks, neg_masks):
        try:
            selected_idx = rng.choice(np.where(examples_mask)[0], size=size, replace=replace)
        except ValueError:
            if not replace:
                raise ValueError(f'Tried to sample {size} triplets without replacement, but there are only '
                                 f'{np.sum(examples_mask)} images from classes with at least 2 images!')
        idx = set(range(len(class_ids)))
        anchors, pos, neg = [], [], []
        for idx_anchor, c_i in zip(selected_idx, class_ids[selected_idx]):
            pos_mask = pos_masks.setdefault(c_i, _create_pos_mask(c_i, class_ids))
            neg_mask = neg_masks.setdefault(c_i, _create_neg_mask(excludes[c_i], class_ids, pos_masks))
            idx_pos = rng.choice(list(pos_mask.difference(set([idx_anchor]))))
            try:
                idx_neg = rng.choice(list(idx.difference(neg_mask)))
            except ValueError:
                raise ValueError('Tried to sample a negative example from an empty list. This is most likely to rigorous excludes. '
                                 'Please to try relax the excludes or remove classes with strong excludes from the input')
            anchors.append(idx_anchor)
            pos.append(idx_pos)
            neg.append(idx_neg)

        return np.array(anchors), np.array(pos), np.array(neg)


def _index_f_squared_to_condense_torch(n, i, j):
    return n * i + j - torch.div(((i + 2) * (i + 1)), 2, rounding_mode='trunc')


def _index_f_squared_to_condense_numpy(n, i, j):
    return n * i + j - ((i + 2) * (i + 1)) // 2


def _get_indices_pdist_matrix_condensed(labels, idx, pos_masks=None, same_class=True, use_torch=False):
    """Helper function to get indices form a condensed pdist matrix."""
    pos_masks = {} if pos_masks is None else pos_masks
    if use_torch:
        j = torch.arange(len(labels), device=labels.device)
        j_original = j.clone()
        i = torch.ones_like(j) * int(idx)
    else:
        j = np.arange(len(labels))
        i = np.ones_like(j) * int(idx)
    mask = i > j
    i[mask], j[mask] = j[mask], i[mask]
    pos_mask = pos_masks.setdefault(labels[idx], labels == labels[idx])
    if use_torch:
        if same_class:
            value_mask = pos_mask.clone()
            value_mask[idx] = False
        else:
            value_mask = torch.logical_not(pos_mask)
    else:
        if same_class:
            value_mask = pos_mask.copy()
            value_mask[idx] = False
        else:
            value_mask = np.logical_not(pos_mask)
    if use_torch:
        return _index_f_squared_to_condense_torch(len(labels), i[value_mask], j[value_mask]), j_original[value_mask]
    else:
        return _index_f_squared_to_condense_numpy(len(labels), i[value_mask], j[value_mask]), np.where(value_mask)[0]


def _create_pos_mask(c_i, classes):
    return set(np.where(classes == c_i)[0])


def _create_neg_mask(excluded_classes, classes, pos_masks):
    ignore_idx = set()
    for c_i in excluded_classes:
        idx_c_i = pos_masks.setdefault(c_i, _create_pos_mask(c_i, classes))
        ignore_idx = ignore_idx.union(idx_c_i)
    return ignore_idx


def create_triplets_from_pk_sample(feature_vectors: 'torch.Tensor',
                                  labels: 'torch.Tensor',
                                  strategy_pos: Union[None, str, Callable]=None,
                                  strategy_neg: Union[None, str, Callable]=None,
                                  dist_norm: float =2.,
                                  anchor_pos_combinations_unique: bool=False) -> Tuple['torch.Tensor', 'torch.Tensor', 'torch.Tensor']:
    """Sample triplets from a subset containing p classes and k examples per class according to a given strategy.

    This function is meant to be used internally. For example this function is called
    by the TripletDistanceLearner or the TripletReservoirSampler.

    Parameters
    ----------
    example_vectors: torch.Tensor
        Features vectors for all examples. Has to be of same length as
        class_ids.
    labels: torch.Tensor
        Labels ids
    strategy_pos: None, str or callable, optinal, default=None
        Strategy used to determine the positive example.
        Supported strategies are 'min', 'max', 'rand' or '*'/'all'.
        If '*' or 'all' strategy_neg is ignored and all possible triplets
        are returned. 'min'/'max' selects the example with the mininmal/
        maximal distance. 'rand' selects a uniform random example.
        If None the default strategy 'rand' is used.
        Alternativly a callable can be passed as a stategy.
        The callable has to return an index as Torch.Tensor and is called
        with max_index and the device of the result. The returned index
        used to access the potential positive examples ordered by their
        distance to the anchor (ascending).
        The intended use is to used custom distribution instead of uniform
        random sampling. Check SkewedNormalSampler as an example.
    strategy_neg: None, str or callable, optinal, default=None
        Strategy used to determine the negative example.
        Identical to 'strategy_pos'.
    dist_norm: float, optional, default=2
        Norm used to calculate the distance.
        Check torch.nn.functional.pdist for details.
    anchor_pos_combinations_unique: bool, optional, default=False
        This option only is only relevant when using '*'/'all' as the strategy.
        The option controls if anchor, pos pairs should be unique.
        If True, (1, 2, 3) and (2, 1, 3) are returned.
        If False, only (1, 2, 3) will returned.

    Returns
    -------
    torch.Tensor
        Anchor indices
    torch.Tensor
        Positive example indices
    torch.Tensor
        Negative example indices
    """
    indices = torch.arange(len(labels), device=labels.device)
    if strategy_pos in ['all', '*'] or strategy_neg in ['all', '*']:
        positive_matrix = labels.unsqueeze(1) == labels.unsqueeze(0)
        negative_matrix = positive_matrix.logical_not()
        if anchor_pos_combinations_unique:
            positive_matrix = positive_matrix.triu(diagonal=1)
        else:
            positive_matrix = positive_matrix.logical_and(torch.eye(*positive_matrix.size(), dtype=bool).logical_not())
        anchor, pos, neg = [], [], []
        for i, a in enumerate(indices):
            for p in indices[positive_matrix[i, :]]:
                for n in indices[negative_matrix[i, :]]:
                    anchor.append(a)
                    pos.append(p)
                    neg.append(n)
        anchor_idx, pos_idx, neg_idx = torch.stack(anchor), torch.stack(pos), torch.stack(neg)
    else:
        with torch.no_grad():
            pos, neg = [], []
            pos_masks = {}
            if any([strat in ['min', 'max'] for strat in (strategy_pos, strategy_neg)]) or any([callable(strat) for strat in (strategy_pos, strategy_neg)]):
                if isinstance(dist_norm, float) or isinstance(dist_norm, int):
                    pdist = nn.functional.pdist(feature_vectors, p=float(dist_norm))
                else:
                    raise NotImplementedError
            else:
                pdist = None
            for idx in range(len(feature_vectors)):
                if strategy_pos == 'rand':
                    pos_mask = pos_masks.setdefault(labels[idx], labels == labels[idx])
                    indices_pos = indices[pos_mask]
                    selected_idx = torch.randint(0, len(indices_pos), size=(1, ), device=labels.device)[0]
                    selected_pos = indices_pos[selected_idx]
                    if selected_pos == idx:
                        selected_pos = indices_pos[(selected_idx + 1) % len(indices_pos)]
                    pos.append(selected_pos)
                elif strategy_pos in ('min', 'max') or callable(strategy_pos):
                    indices_pos, indices_feat_pos = _get_indices_pdist_matrix_condensed(labels,
                                                                                        idx,
                                                                                        None,#pos_masks,
                                                                                        same_class=True,
                                                                                        use_torch=True)
                    if callable(strategy_pos):
                        distance_order = torch.argsort(pdist[indices_pos])
                        idx_ = strategy_pos(len(distance_order), labels.device)
                        pos.append(indices_feat_pos[distance_order[idx_]])
                    else:
                        pos.append(indices_feat_pos[torch.argmin(pdist[indices_pos])
                                                    if strategy_pos == 'min' else
                                                    torch.argmax(pdist[indices_pos])])
                else:
                    raise ValueError(f'`{strategy_pos}` is not a valid strategy to sample positive examples')
                if strategy_neg == 'rand':
                    neg_mask = torch.logical_not(pos_masks.setdefault(labels[idx], labels == labels[idx]))
                    indices_neg = indices[neg_mask]
                    selected_idx = torch.randint(0, len(indices_neg), size=(1, ), device=labels.device)[0]
                    neg.append(indices_neg[selected_idx])
                elif strategy_neg in ('min', 'max') or callable(strategy_neg):
                    indices_neg, indices_feat_neg = _get_indices_pdist_matrix_condensed(labels,
                                                                                        idx,
                                                                                        None,#pos_masks,
                                                                                        same_class=False,
                                                                                        use_torch=True)
                    if callable(strategy_neg):
                        distance_order = torch.argsort(pdist[indices_neg])
                        idx_ = strategy_neg(len(distance_order), labels.device)
                        neg.append(indices_feat_neg[distance_order[idx_]])
                    else:
                        neg.append(indices_feat_neg[torch.argmin(pdist[indices_neg])
                                                    if strategy_neg == 'min' else
                                                    torch.argmax(pdist[indices_neg])])
                else:
                    raise ValueError(f'`{strategy_neg}` is not a valid strategy to sample positive examples')
                anchor_idx, pos_idx, neg_idx = indices, torch.stack(pos), torch.stack(neg)
    return anchor_idx, pos_idx, neg_idx


class SkewedNormalSampler:
    """Class providng samples indices based on a moved and scaled skewed normal distribution.

    The basic idea is to squeeze a skewed normal distribution in the range between 0 and 1
    and skew the distribution "to the right" if the modus is > 0.5 and "to the left" if the mode
    is < 0.5. The skewness is linearly increased to its max value when moving the mode to the
    side.

    The distribution is used to have control on the difficulty of sampled triplets. It can be
    seen as a relaxation of max min triplets. The class is used when using a float as triplet
    sampling strategy.
    """
    def __init__(self, loc: float, power: float=1., min_weight: Union[None, float]=None, max_skew: float=10.):
        """Create callable instance to random sample an index according to a
        moved and scaled skewed normal distribution.

        Parameters
        ----------
        loc: float
            Position of the mode. Has to be between 0 and 1.
        power: float, optional, defaul=1.
            Exponent x (dist**x).
            Can be used to make the distribution "sharper".
        min_weight: None or float, optinal, default=None
            Minimum weight when sampling the index.
            dist*(x) = max(dist(x), min_weight).
        max_skew: float, optional, default=10.
            Maximal skewness value
        """
        self._cache = {}
        self.loc = loc
        self.power = power
        self.min_weight = min_weight
        self.max_skew = max_skew

    def __repr__(self):
        return str(self)

    def __str__(self):
        return f'SkewedNormalSampler(loc={self.loc}, power={self.power} min_weight={self.min_weight}, max_skew={self.max_skew})'

    @staticmethod
    def _get_scaled_moved_skewed_normal_distribution(a, max_a=10., power=1.):
        used_a = (0.5-a)/0.5 * max_a
        scaling = skewnorm.ppf(1-0.01, used_a) - skewnorm.ppf(0.01, used_a)

        if used_a == 0:
            mode = 0
        else:
            delta = used_a / np.sqrt(1 + used_a**2)
            mu_z = np.sqrt(2 / np.pi) * delta
            sigma_z = np.sqrt(1-mu_z**2)
            skew = (4-np.pi) / 2 * (delta * np.sqrt(2/np.pi))**3 / (1 - 2*delta**2/np.pi)**(1.5)
            mode = mu_z - skew * sigma_z / 2. - np.sign(used_a) / 2. * np.exp(-2*np.pi/np.absolute(used_a))
        amplitude = skewnorm.pdf(mode, used_a)

        def f_(x):
            x = ((x-a)* scaling + mode)
            weights = np.power(skewnorm.pdf(x, used_a) / amplitude, power)
            return weights

        return f_

    @staticmethod
    def _get_sample_weights_skewed_norm_dist(n_entries, loc, power=1, min_weight=None, max_skew=10.):
        loc = np.clip(loc, 0., 1.)
        f_ = SkewedNormalSampler._get_scaled_moved_skewed_normal_distribution(loc, power=power, max_a=max_skew)
        x = np.linspace(0., 1, n_entries)
        weights = np.ones(1, dtype=np.float32) if n_entries == 1 else f_(np.linspace(0., 1, n_entries))
        if min_weight is not None:
            weights = np.clip = np.clip(weights, min_weight, None)
        weights /= np.sum(weights)
        return weights


    def __call__(self, n_entries, device):
        try:
            cumsum = self._cache[n_entries]
        except KeyError:
            weights = self._get_sample_weights_skewed_norm_dist(n_entries, loc=self.loc, power=self.power, min_weight=self.min_weight, max_skew=self.max_skew)
            cumsum = np.cumsum(weights)
            cumsum /= cumsum[-1]
            cumsum = torch.from_numpy(cumsum).float().to(device)
            self._cache[n_entries] = cumsum
        val = torch.rand(1, device=device, requires_grad=False)
        return int(sum(cumsum < val))


def build_triplet_strategy(strategy: Union[str, float]=None, skewed_pow=3) -> Tuple[Union[str, Callable]]:
    """Function to check strategy and create SkewedNormalSampler when strategy is float.

    This function is used by the TripletDistanceLearner and the TripletReservoirSampler.

    Parameters
    ----------
    strategy: str or float, optional, defaul=None
        Strategies used to sample positve example (strategy[0])
        and negative example (strategy[1]).
        Options are 'rand'/'min'/'max' or a float between 0 and 1.
        - rand: random
        - min: minimal distance to the anchor
        - max: maximal distance to the anchor
        - all/*: All possible triplets
        - float: loc of SkedNormalSampler

    Returns
    -------
    tuple(str/Callable, str/Callable)
        Tiplet
    """
    if (isinstance(strategy, str) and strategy.lower() == 'none') or strategy is None:
        strategy = ('rand', 'rand')
    if not isinstance(strategy, tuple) and len(strategy) != 2:
        raise ValueError('`strategy` for triplet sampling when using the PKsampler/TripletReservoirSampler has be a tuple (pos_strat, neg_strat).')
    pos, neg = strategy
    if isinstance(pos, float):
        pos = SkewedNormalSampler(pos, power=skewed_pow)
    elif isinstance(pos, str):
        pos = pos.lower()
    if isinstance(neg, float):
        neg = SkewedNormalSampler(neg, power=skewed_pow)
    elif isinstance(neg, str):
        neg = neg.lower()
    return (pos, neg)
