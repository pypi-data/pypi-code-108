import numpy as np

import torch
from torch.distributions.categorical import Categorical
from torch.utils.data import (
    BatchSampler,
    Dataset,
    Sampler,
    SubsetRandomSampler,
)

from .cache import CachedDataset
from .datasets import (
    audio_lengths,
    FixedLengthDataset,
    TransformedDataset,
)
from .loader import DataLoaderFactory, DataTransformer


class SubsetSampler(Sampler):
    def __init__(self, indexes):
        self.indexes = indexes

    def __iter__(self):
        yield from self.indexes

    def __len__(self):
        return len(self.indexes)


class MixedBatchSampler(Sampler):
    def __init__(self,
                 index_list,
                 batch_sizes,
                 drop_last=False,
                 shuffle=False,
                 ):
        sampler_class = SubsetRandomSampler if shuffle else SubsetSampler
        self.batch_samplers = [BatchSampler(sampler_class(indexes),
                                            batch_sizes[i], drop_last)
                               for i, indexes in enumerate(index_list)]
        lengths = torch.Tensor([len(indexes) for indexes in index_list])
        self.distribution = Categorical(logits=lengths.log())

    def __iter__(self):
        iterators = [iter(sampler) for sampler in self.batch_samplers]
        n_batches = [len(sampler) for sampler in self.batch_samplers]
        while sum(n_batches) > 0:
            index = self.distribution.sample()
            if n_batches[index] == 0:
                continue

            yield next(iterators[index])
            n_batches[index] -= 1

    def __len__(self):
        return sum(len(sampler) for sampler in self.batch_samplers)


class MixedDataset(Dataset):
    def __init__(self, datasets, indexes):
        self.datasets = datasets
        self.indexes = indexes
        self.cumulative_lengths = np.cumsum(
            [len(dataset) for dataset in datasets])

    def __getitem__(self, index):
        dataset_index = np.where(index < self.cumulative_lengths)[0][0]
        offset = self.cumulative_lengths[dataset_index]
        dataset = self.datasets[dataset_index]
        entry = dataset[index - offset]  # x or (x, y)

        # Return (x, indexes) or (x, y, indexes) accordingly
        if isinstance(entry, tuple):
            return entry + (self.indexes[index],)
        return entry, self.indexes[index]

    def __len__(self):
        return self.cumulative_lengths[-1]


class MixedDataLoaderFactory(DataLoaderFactory):
    def __init__(self, block_lengths, batch_sizes, **kwargs):
        super().__init__(block_length=None, hop_length=None,
                         batch_size=None, **kwargs)
        self.block_lengths = block_lengths
        self.batch_sizes = batch_sizes

    def training_data_loader(self, subset):
        return self._data_loader(subset, shuffle=True)

    def validation_data_loader(self, subset):
        return self._data_loader(subset)

    def test_data_loader(self, subset):
        return self._data_loader(subset)

    def _data_loader(self, subset, shuffle=False):
        # Determine the transforms to be applied (if any)
        cacheable, non_cacheable = self.transforms(subset)
        if self.cache_features:
            loader_transforms = []
        else:
            loader_transforms = cacheable + non_cacheable

        # Instantiate Dataset
        subsets, indexes = _split_subset(subset, self.block_lengths)
        datasets = [self._create_dataset(subset, self.block_lengths[i],
                                         cacheable, non_cacheable)
                    for i, subset in enumerate(subsets)]
        dataset = MixedDataset(datasets, indexes)

        batch_sampler = self._create_batch_sampler(datasets, shuffle)
        loader = DataTransformer(
            dataset,
            loader_transforms,
            batch_sampler=batch_sampler,
            num_workers=self.n_workers,
            pin_memory=True,
        )
        return loader

    def _create_dataset(self, subset, block_length, cacheable, non_cacheable):
        dataset = FixedLengthDataset(subset, block_length,
                                     labeler=self.labeler)
        if self.cache_features:
            if len(cacheable) > 0:
                dataset = CachedDataset(TransformedDataset(dataset, cacheable))
            if len(non_cacheable) > 0:
                dataset = TransformedDataset(dataset, non_cacheable)
        return dataset

    def _create_batch_sampler(self, datasets, shuffle):
        index_list = []
        start_index = 0
        for dataset in datasets:
            end_index = start_index + len(dataset)
            index_list.append(range(start_index, end_index))
            start_index = end_index
        return MixedBatchSampler(index_list, self.batch_sizes, shuffle=shuffle)


def _split_subset(subset, block_lengths):
    lengths = audio_lengths(subset)

    subsets = []
    all_indexes = []
    block_lengths = [0] + block_lengths[:-1] + [9999]
    for i, block_length in enumerate(block_lengths[1:]):
        indexes = [j for j, length in enumerate(lengths)
                   if length > block_lengths[i]
                   and length <= block_length]
        all_indexes += indexes

        subsets.append(subset.subset_iloc(subset.name, indexes))

    return subsets, all_indexes
