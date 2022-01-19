"""This file contains various batch samplers and matching collate functions

The sampler are are intended to do distance metric learning.
"""
import logging
from contextlib import ExitStack
from itertools import count
from collections.abc import Iterable as IsIterable
from typing import Callable, Iterator, Dict, List, Set, Union, Tuple, Any

import numpy as np
import torch
from torch import nn
from torch.utils.data.dataloader import DataLoader
from torch.utils.data.sampler import Sampler
from torch.utils.data import IterableDataset
from detectron2.engine.train_loop import HookBase
from detectron2.evaluation.evaluator import inference_context
from detectron2.data.build import trivial_batch_collator, build_batch_data_loader

from .triplet_sampling_utils import TripletGenerator, create_triplets_from_pk_sample, build_triplet_strategy


logger = logging.getLogger(__name__)


class PKTripletSampler(Sampler):
    """"This sampler returns batches containing p classes and k examples per class.

    This sampler can return batches of indices:
        [(c1, c1, c5, c5, c4, c4), ..., (c5, c5, c2, c2, c3, c3) ]
    or single indices (Make sure to do correct batching later on the
    preserve the pk batches):
        [c1, c1, c5, c5, c4, c4, ..., c5, c5, c2, c2, c3, c3]

    The idea for such a sampler is taken from: https://arxiv.org/pdf/1703.07737.pdf

    Attributes
    ----------
    batch_size: int
        Effective batch size: p*k
    p: int
        Number of classes in a batch.
    k: int
        Number of examples per class.
    """
    def __init__(self,
                 p: int,
                 k: int,
                 class_ids: Union['np.array', List[int]],
                 n_batches: Union[None, int]=None,
                 excludes: Union[None, Dict[int, Set[int]]]=None,
                 ignore_class_weights: bool=True,
                 rng: Union[None, int, 'np.random.Generator']=None,
                 return_batch: bool=False,
                 infinite_stream: bool=False):
        """"Create a sampler.

        Parameters
        ----------
        p: int
            Number of classes in a batch.
        k: int
            Number of examples per class.
        class_ids: np.array or list of ints
            Class ids of the examples in the dataset.
        n_batches: None or int, optional, default=None
            If None len of the iterator is will be len(class_ids.
        excludes: None or dict(int, set(int)), optional, default=None
            To exclude classes from being sampled together with other classes.
            Provide a dict with int as key and a set of class ids of the
            excluded classes. The prevents all classes from the set form
            being sampled if the class used as key for the set is in the batch.
        ignore_class_weights: bool, optional, default=False
            If True the p classes are sampled according to their ratio in the dataset.
            If False all classes are uniformly sampled.
        rng: None or int or np.random.Generator, optinal, default=None
            Seed for the np.random.Generator or a np.random.Generator.
            Check https://numpy.org/doc/stable/reference/random/generator.html
            for more infos
        return_batch: bool, optional, default=False
            Whether the Sampler should return batches indices or single indices of the
            examples.
        infinite_strem: bool, optional, default=False
            If set to True the sampler returns an infinite stream of bachtes/single
            indices.

        """
        assert p >= 2 and isinstance(p, int), "`p` must be int >= 2."
        assert k >= 2 and isinstance(p, int), "`k` must be int >= 2."
        self.p = p
        self.k = k
        self._generator = TripletGenerator(class_ids=class_ids, excludes=excludes, rng=rng, ignore_class_weights=ignore_class_weights)
        self.return_batch = return_batch
        # Setup sampling
        if n_batches is None:
            n_batches = len(class_ids)
        self.n_batches = n_batches
        self.infinite_stream = infinite_stream

    def __len__(self) -> int:
        if self.infinite_stream:
            raise TypeError('Sampler is set to produce an infinite stream of samples, so length is not definied!')
        else:
            if self.return_batch:
                return self.n_batches
            else:
                return self.n_batches * self.batch_size

    @property
    def batch_size(self):
        return self.p * self.k

    def __iter__(self) -> Iterator[int]:
        iterator = count(0) if self.infinite_stream else range(self.n_batches)
        for _ in iterator:
            subset = self._generator.sample_subset(p=self.p, k=self.k)
            if self.return_batch:
                yield subset.indices
            else:
                for i in subset.indices:
                    yield i


class TripletTrainSampler(Sampler):
    """This sampler returns uniform random sampled triplets.

    The shape of the output can be controlled with the attributes
    'flatten' 'and return_batch':
        - (batch_size=2, flatten=False, return_batch=True):
            [((t1_anchor, t1_pos, t1_neg), (t2_anchor, t2_pos, t2_neg)), ...]
        - (batch_size=2, flatten=True, return_batch=True):
            [(t1_anchor, t1_pos, t1_neg, t2_anchor, t2_pos, t2_neg), ...]
        - (batch_size=2, flatten=Flase, return_batch=False):
            [t1_anchor, t1_pos, t1_neg, t2_anchor, t2_pos, t2_neg, ...]

    Attributes
    ----------
    batch_size: int
        Effective batch size: n_triplets_per_batch*3 (flatten=True) or
        simply n_triplets_per_batch (flatten=False)
    sampler_n_batches_at_once: int, default=10
        This parameter is only to optimize the performace a little bit.
        The time it takes to generate triplets is linear with the number of triplets.
        But there is also a significant overhead for every call (check TripletGenerator
        implementation details). So calling it for every batch is slower. Creating
        a lot of unused triplets is also not ideal. Normally you can simply ignore this
        parameter and use the default values.
    """
    sampler_n_batches_at_once = 10

    def __init__(self,
                 class_ids,
                 n_triplets_per_batch,
                 n_batches=None,
                 excludes=None,
                 rng: Union[None, int, 'np.random.Generator']=None,
                 return_batch: bool=False,
                 flatten: bool=True,
                 infinite_stream: bool=False):
        """"Create a sampler.

        Parameters
        ----------
        class_ids: np.array or list of ints
            Class ids of the examples in the dataset.
        n_triplets_per_batch: int
            Number of triplets per batch.
        n_batches: None or int, optional, default=None
            If None len of the iterator is will be len(class_ids.
        excludes: None or dict(int, set(int)), optional, default=None
            To exclude classes from being sampled together with other classes.
            Provide a dict with int as key and a set of class ids of the
            excluded classes. The prevents all classes from the set form
            being sampled if the class used as key for the set is in the batch.
        rng: None or int or np.random.Generator, optinal, default=None
            Seed for the np.random.Generator or a np.random.Generator.
            Check https://numpy.org/doc/stable/reference/random/generator.html
            for more infos
        return_batch: bool, optional, default=False
            Whether the Sampler should return batches indices or single indices of the
            examples.
        flatten: bool, optional, default=True
            If True the batch shape is (n_triplets_per_batch*3, ).
            If False the batch shape is (n_triplets_per_batch, 3).
        infinite_strem: bool, optional, default=False
            If set to True the sampler returns an infinite stream of bachtes/single
            indices.
        """
        self.generator = TripletGenerator(class_ids=class_ids, excludes=excludes, rng=rng)
        self.return_batch = return_batch
        self.flatten = True if not return_batch else flatten
        self.infinite_stream = infinite_stream
        # Setup sampling
        if n_batches is None:
            self.n_batches = len(class_ids)
        self.n_triplets_per_batch = n_triplets_per_batch

    def __len__(self) -> int:
        if self.infinite_stream:
            raise TypeError('Sampler is set to produce an infinite stream of samples, so length is not definied!')
        else:
            if self.return_batch:
                return self.n_batches
            else:
                return self.n_batches * self.batch_size

    @property
    def batch_size(self) -> int:
        if self.flatten:
            return self.n_triplets_per_batch * 3
        else:
            return self.n_triplets_per_batch

    def __iter__(self) -> Iterator[int]:
        iterator = count(0) if self.infinite_stream else range(self.n_batches)
        batches_returned = 0
        for _ in iterator:
            new_batches = min(self.sampler_n_batches_at_once,
                              self.n_batches - batches_returned if self.n_batches > 0 else self.sampler_n_batches_at_once)
            size = self.n_triplets_per_batch * new_batches
            triplet_array = np.vstack(self.generator.build_random_triplets(size=size, replace=True)).T
            for data in _iter_triplet_data(triplet_array,
                                           self.n_triplets_per_batch,
                                           flatten=self.flatten,
                                           return_batch=self.return_batch):
                yield data
            batches_returned += new_batches
            if self.n_batches > 0 and batches_returned >= self.n_batches:
                return



class TripletReservoirSampler(Sampler):
    """This sampler creates triplets similar to TripletSampler
    but creates the triplets based on the distance/similarities of the
    examples. The batches of triplets are sampled from a reservoir.
    The reservoirs contain p classes with k examples each.
    """
    def __init__(self,
                 class_ids: Union['np.array', List[int]],
                 n_triplets_per_batch: int,
                 k_examples_per_class: int,
                 strategy: Tuple[Union[str, float]]=('max', 'min'),
                 reservoir_of_n_batches: int=10,
                 n_random_batches_start: int=10,
                 refresh_after_n_batches: Union[int, None]=None,
                 n_batches: Union[None, int]=None,
                 example_vectors: Union[None, 'np.array']=None,
                 example_vectors_func: Union[None, Callable]=None,
                 excludes: Union[None, Dict[int, Set[int]]]=None,
                 rng: Union[None, int, 'np.random.Generator']=None,
                 return_batch: bool=False,
                 flatten: bool=True,
                 infinite_stream: bool=False):
        """"Create a sampler.

        Parameters
        ----------
        class_ids: np.array or list of ints
            Class ids of the examples in the dataset.
        n_triplets_per_batch: int
            Number of triplets per batch.
        k_examples_per_class: int
            Number of examples per class
        strategy: str or float, optional, defaul=('max', 'min')
            Strategy used to sample positve example (strategy[0])
            and negative example (strategy[1]).
            Options are 'rand'/'min'/'max' or a float between 0 and 1.
            - rand: random
            - min: minimal distance to the anchor
            - max: maximal distance to the anchor
            - float: loc of triplet_sampling_utils.SkedNormalSampler
        reservoir_of_n_batches: int, optional, default=10
            Number of batches sampled from each reservoir.
        n_random_batches_start: int, optional, default=0
            Number of uniform random triplets to warmup the classifier.
        refresh_after_n_batches: None or int, optional, default=None
            Number of batches sampled from a single reservoir.
            If None refresh_after_n_batches = reservoir_of_n_batches
        n_batches: None or int, optional, default=None
            If None len of the iterator is will be len(class_ids.
        example_vectors: None or np.array, optional, default=None
            Features vectors for all examples. Has to be of same length as
            class_ids. To calculate the feature vectors dynamically for each
            batch set sampler.example_vectors_func.
        example_vectors_func: None or callable, optional, default=None
            Callable calculating the feature vectors of the examples in the
            reservoir. The callable is called with the reservoir.
            Check sap_computer_vision.data.triplet_sampling_utils.TripletGenerator.Subset
            for details.
        excludes: None or dict(int, set(int)), optional, default=None
            To exclude classes from being sampled together with other classes.
            Provide a dict with int as key and a set of class ids of the
            excluded classes. The prevents all classes from the set form
            being sampled if the class used as key for the set is in the batch.
        rng: None or int or np.random.Generator, optinal, default=None
            Seed for the np.random.Generator or a np.random.Generator.
            Check https://numpy.org/doc/stable/reference/random/generator.html
            for more infos
        return_batch: bool, optional, default=False
            Whether the Sampler should return batches indices or single indices of the
            examples.
        flatten: bool, optional, default=True
            If True the batch shape is (n_triplets_per_batch*3, ).
            If False the batch shape is (n_triplets_per_batch, 3).
        infinite_strem: bool, optional, default=False
            If set to True the sampler returns an infinite stream of bachtes/single
            indices.
        """
        self._generator = TripletGenerator(class_ids=class_ids, excludes=excludes, rng=rng, example_vectors=example_vectors)
        self.return_batch = return_batch
        self.refresh_after_n_batches = refresh_after_n_batches if refresh_after_n_batches is not None else reservoir_of_n_batches
        self.n_triplets_per_batch = n_triplets_per_batch
        self.reservoir_of_n_batches = reservoir_of_n_batches
        self.k_examples_per_class = k_examples_per_class
        self.n_random_batches_start = n_random_batches_start
        self._random_triplets = n_random_batches_start > 0
        self.triplet_strategy = build_triplet_strategy(strategy)

        self.example_vectors_func = example_vectors_func

        self.return_batch = return_batch
        self.flatten = True if not return_batch else flatten
        self.infinite_stream = infinite_stream
        if n_batches is None:
            self.n_batches = len(class_ids)

    @property
    def p_classes_in_reservoir(self):
        return int(np.ceil((self.n_triplets_per_batch * self.reservoir_of_n_batches) // self.k_examples_per_class))

    def __len__(self) -> int:
        if self.infinite_stream:
            raise TypeError('Sampler is set to produce an infinite stream of samples, so length is not definied!')
        else:
            if self.return_batch:
                return self.n_batches
            else:
                return self.n_batches * self.batch_size

    @property
    def batch_size(self):
        if self.flatten:
            return self.n_triplets_per_batch * 3
        else:
            return self.n_triplets_per_batch

    def get_reservoir(self):
        reservoir = self._generator.sample_subset(
            p=self.p_classes_in_reservoir,
            k=self.k_examples_per_class)
        if self.example_vectors_func is not None:
            reservoir.set_example_vectors(self.example_vectors_func(reservoir))
        return reservoir

    def __iter__(self) -> Iterator[int]:
        iterator = count(0) if self.infinite_stream else range(self.n_batches)
        batches_returned = 0
        for _ in iterator:
            if self._random_triplets:
                new_batches = min(self.n_random_batches_start, self.n_batches)
                size = self.n_triplets_per_batch * new_batches
                triplet_array = np.vstack(self._generator.build_random_triplets(size=size, replace=True)).T
                self._random_triplets = False
            else:
                reservoir = self.get_reservoir()
                triplet_array = reservoir.build_triplets_accourding_to_strategy((self.triplet_strategy[0],
                                                                                 self.triplet_strategy[1]))
                triplet_array = np.array(triplet_array).T
                self._generator.rng.shuffle(triplet_array)
                new_batches = min(self.refresh_after_n_batches,
                                  self.n_batches - batches_returned if self.n_batches > 0 else self.refresh_after_n_batches)
                triplet_array = triplet_array[:new_batches*self.n_triplets_per_batch]
            for data in _iter_triplet_data(triplet_array,
                                           self.n_triplets_per_batch,
                                           flatten=self.flatten,
                                           return_batch=self.return_batch):
                yield data
            batches_returned += new_batches
            if self.n_batches > 0 and batches_returned >= self.n_batches:
                return


class PredictReservoirHook(HookBase):
    """Detectron trainer hook to calculate feature vectors of the reservoir examples.

    The tricky part is to create a dataloader for the reservoir."""
    def __init__(self, sampler):
        self.sampler = sampler

    def before_train(self):
        """Function executed before the training.
        Assign the 'calculate_example_vectors' of the hook as the example_vectors_func
        callable of the sampler.
        """
        self.sampler.example_vectors_func = self.calculate_example_vectors

    @staticmethod
    def _predict_reservoir(cfg, reservoir_data, model, collate_fn=trivial_batch_collator):
        with ExitStack() as stack:
            if isinstance(model, nn.Module):
                stack.enter_context(inference_context(model))
            stack.enter_context(torch.no_grad())
            batch_size = cfg.SOLVER.get('IMS_PER_BATCH_EVAL', cfg.SOLVER.IMS_PER_BATCH)
            data_loader = DataLoader(
                dataset=reservoir_data,
                batch_size=batch_size,
                drop_last=False,
                collate_fn=collate_fn)
            outputs = []
            with torch.no_grad():
                model.eval()
                for batch_inputs in data_loader:
                    outputs.append(model(batch_inputs).cpu().detach().numpy())
                model.train()
            return np.vstack(outputs)

    def calculate_example_vectors(self, reservoir: 'TripletGenerator.Subset') -> 'np.array':
        """Function calculating the feature vectors of a reservoir.

        This functions is used as the example_vectors_func callable
        of the TripletReservoirSampler.

        Parameters
        ----------
        reservoir: TripletGenerator.Subset
            Reservoir for which the feature vectors should be calculated.
        Returns
        -------
        np.array
            Feature vectors of the reservoir
        """
        if reservoir.example_vectors is None:
            dataset = self.trainer.data_loader.dataset
            if isinstance(dataset, IterableDataset):
                raise ValueError('TripletReservoirSampler can not be used for `IterableDataset`s.')
            reservoir_data = [dataset[idx] for idx in reservoir.indices]
            example_vectors = self._predict_reservoir(cfg=self.trainer.cfg,
                                                     reservoir_data=reservoir_data,
                                                     model=self.trainer.model)
            return example_vectors


def triplet_collator_fn(batch: List[Dict[str, Any]]) -> List[Dict[str, Dict[str, Any]]]:
    """Collate function for torch.data.DataLoader to output list of dicts of triplets.
    [{'anchor': example_dict, 'pos': example_dict, 'neg': example_dict}...]

    Parameters
    ----------
    batch: list of dicts
        List of dicts returned form the DatasetMapper.

    Returns
    ----------
    list of dicts
        List of dicts. Each list entry is a dict
        {'anchor': example_dict, 'pos': example_dict, 'neg': example_dict}
    """
    assert len(batch) % 3 == 0
    return [{'anchor': a, 'pos': p, 'neg': n} for a, p, n in zip(batch[::3], batch[1::3], batch[2::3])]


def _iter_triplet_data(data, n_triplets_per_batch, flatten, return_batch):
    assert len(data.shape) == 2
    assert data.shape[1] == 3
    _position = 0
    while _position < len(data):
        start = _position
        end = start + n_triplets_per_batch
        end = None if end > len(data) else end
        s_ = slice(start, end)
        current_batch = data[s_, ].flatten()  if flatten else data[s_, ]
        if return_batch:
            yield current_batch
        else:
            for entry in current_batch:
                yield entry
        _position += n_triplets_per_batch


class PKTripletStrategySwitcher(HookBase):
    """This sampler returns batches containing p classes and k examples per class.

    This sampler can return batches of indices (p=3, k=2):
        [(c1, c1, c5, c5, c4, c4), ..., (c5, c5, c2, c2, c3, c3) ]
    or single indices (Make sure to do correct batching later on the
    preserve the pk batches):
        [c1, c1, c5, c5, c4, c4, ..., c5, c5, c2, c2, c3, c3]

    The idea for such a sampler is taken from: https://arxiv.org/pdf/1703.07737.pdf

    Attributes
    ----------
    next_strat_and_step: (step, (pos_strat, net_strat))
        Property to retrieve the next strategy switch:
        step (int) and tuple (pos_strat, neg_strat)
    """
    def __init__(self, strategies, target):
        """Create a hook with list of strategies.
        The hook instance can be registered with a detectron2 trainer.
        If using the TripletDistanceTrain from this package the
        hook is automatically registered when strategies switches are
        defined in the config and the PKSampler is selected.

        Parameters
        ----------
        strategies: list of tuples [(step, (pos_strat, neg_start)), ...]
            Strategies are provided as a list of tuples.
            The tuples consist of a step and a tuple with the strategy
            for the positive example and the strategy for the negative
            example. Check sap_computer_vision.modelling.TripletDistanceLearner
            documentation for details about different strategies.
        """
        self.strategies = self.check_strategies(strategies)
        self.target = target
        self._pointer = 0

    @property
    def next_strat_and_step(self) -> Tuple[int, Union[None, Tuple[Union[str, float], Union[str, float]]]]:
        """Property returning the next stragety and the switch step.

        Returns
        -------
        int
            Step for the next switch. -1 if no switch is scheduled.
        tuple or None
            Tuple (pos_strat, neg_strat) or None if no switch is scheduled."""
        try:
            return self.strategies[self._pointer]
        except IndexError:
            return -1, None


    @staticmethod
    def check_strategies(strategies) -> List[Tuple[int, Union[None, Tuple[Union[str, float], Union[str, float]]]]]:
        """Functions to perform sanity checks of list of strategies.
        Invalid tuples are ignored and are logged as warnings.

        Parameters
        ----------
        strategies: list of tuples [(step, (pos_strat, neg_start)), ...]
            Strategies are provided as a list of tuples.
            The tuples consist of a step and a tuple with the strategy
            for the positive example and the strategy for the negative
            example. Check sap_computer_vision.modelling.TripletDistanceLearner
            documentation for details about different strategies.
        Returns
        -------
        list of strategy tuples
            Cleaned list of tuples [(step, (pos_strat, neg_start)), ...]
        """
        if not isinstance(strategies, IsIterable):
            logger.warning('Strategies for switches have to provided as a list of tuples (step, strategie). Strategies will not be switched!')
            return []
        else:
            checked_strategies = []
            for i in range(len(strategies)):
                try:
                    step, strat = strategies[i]
                except ValueError:
                    logger.warning(f'Strategies for switches have to provided as a list of tuples (step, strategie). Switch defined as `{strategies[i]}` will be ignored!')
                else:
                    checked_strategies.append((step, strat))
        return checked_strategies

    def before_train(self):
        """Function executed before the training.
        This functions is only logging the first strategy switch.
        """
        msg = f'Starting with `{self.target.triplet_strategy}`'
        switch_step, next_strat = self.next_strat_and_step
        if next_strat is not None:
            msg += f'; first strategy switch iter: {switch_step} to `{next_strat}`'
        else:
            msg += '; no strategy switch sheduled'
        logger.info(msg)

    def after_step(self):
        """Function executed after every training step.
        After every training step this functions check if the strategy has to be switched.
        Every switch is logged and the next switch is announced.
        """
        switch_step, next_strat = self.next_strat_and_step
        if self.trainer.iter == switch_step:
            try:
                new_strat = build_triplet_strategy(next_strat)
            except ValueError:
                msg = f'Switching to {next_strat} failed, because it is not a valid strategy'
            else:
                msg = f'Switching to `{new_strat}` iter: {self.trainer.iter}'
                self.target.triplet_strategy = new_strat
                self._pointer += 1
                switch_step, next_strat = self.next_strat_and_step
            if next_strat is not None:
                msg += f'; next strategy iter: {switch_step} to `{next_strat}`'
            else:
                msg += '; no more strategy switches sheduled'
            logger.info(msg)
