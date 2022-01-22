import torch.nn as nn
from torch.utils.data import DataLoader

from .cache import CachedDataset
from .datasets import (
    FixedLengthDataset,
    TransformedDataset,
    VariableLengthDataset,
)
from .features import MelSpectrogramExtractor, Resampler, SpectrogramExtractor


class MappedDataLoader(DataLoader):
    def __init__(self, dataset, device=None, **kwargs):
        super().__init__(dataset, **kwargs)

        if device is not None:
            self.to(device)

    def to(self, device):
        self.device = device

    def __iter__(self):
        def _to(data):
            if isinstance(data, (tuple, list)):
                return tuple(_to(item) for item in data)
            return data.to(self.device)

        return map(_to, super().__iter__())


class DataTransformer(MappedDataLoader):
    def __init__(self, dataset, transforms, device=None, **kwargs):
        if not isinstance(transforms, (tuple, list)):
            self.transforms = [transforms]
        else:
            self.transforms = list(transforms)

        # Invoked later because of to()
        super().__init__(dataset, device, **kwargs)

    def to(self, device):
        self.device = device
        for transform in self.transforms:
            if isinstance(transform, nn.Module):
                transform.to(device)

    def transform(self, data):
        is_tuple = isinstance(data, tuple)
        for T in self.transforms:
            if is_tuple:
                output = T(*data)
                if not isinstance(output, tuple):
                    output = (output,)
                data = output + data[len(output):]
            else:
                data = T(data)
                if isinstance(data, tuple):
                    data = data[0]
        return data

    def __iter__(self):
        return map(self.transform, super().__iter__())


class IterationBasedLoader:
    def __init__(self, loader, n_iterations):
        self.loader = loader
        self.n_iterations = n_iterations
        self._iter = loader.__iter__()

    def to(self, device):
        self.loader.to(device)

    def __iter__(self):
        for i in range(self.n_iterations):
            try:
                batch = next(self._iter)
            except StopIteration:
                self._iter = self.loader.__iter__()
                batch = next(self._iter)

            yield batch

    def __len__(self):
        return self.n_iterations


class DataLoaderFactory:
    def __init__(self,
                 sample_rate=None,
                 block_length=None,
                 hop_length=None,
                 features=None,
                 labeler='default',
                 batch_size=1,
                 n_workers=0,
                 cache_features=False,
                 ):
        self.sample_rate = sample_rate
        self.block_length = block_length
        self.hop_length = hop_length
        self.features = features
        self.labeler = labeler
        self.batch_size = batch_size
        self.n_workers = n_workers
        self.cache_features = cache_features

        self._waveform_transforms = []
        self._feature_transforms = []

    def training_data_loader(self, subset):
        return self._data_loader(subset, shuffle=True)

    def validation_data_loader(self, subset):
        return self._data_loader(subset)

    def test_data_loader(self, subset):
        return self._data_loader(subset)

    def feature_extractor(self, subset):
        fv_params = self.features.copy()
        method = fv_params.pop('method')
        if method == 'mel':
            new_sr = self.sample_rate or subset.dataset.sample_rate
            return MelSpectrogramExtractor(new_sr, **fv_params)
        if method == 'spectrogram':
            return SpectrogramExtractor(**fv_params)

        raise ValueError(f"Unknown feature extraction method '{method}'")

    def add_waveform_transform(self, transform, cacheable=False):
        self._waveform_transforms.append((transform, cacheable))

    def add_feature_transform(self, transform, cacheable=False):
        self._feature_transforms.append((transform, cacheable))

    add_tf_transform = add_feature_transform

    def waveform_transforms(self, subset=None):
        cacheable, non_cacheable = self._split(self._waveform_transforms)
        if subset is None:
            return cacheable, non_cacheable

        # Add transform for resampling if applicable
        orig_sr = subset.dataset.sample_rate
        new_sr = self.sample_rate or orig_sr
        if new_sr != orig_sr:
            cacheable.insert(0, Resampler(orig_sr, new_sr))

        return cacheable, non_cacheable

    def feature_transforms(self):
        return self._split(self._feature_transforms)

    tf_transforms = feature_transforms

    def transforms(self, subset):
        cacheable, non_cacheable = self.waveform_transforms(subset)
        if self.features is None:
            return cacheable, non_cacheable

        # Add extractor and subsequent transforms to the correct list(s)
        extractor = self.feature_extractor(subset)
        cacheable_, non_cacheable_ = self.feature_transforms()
        if len(non_cacheable) > 0:
            non_cacheable.append(extractor)
            non_cacheable += cacheable_ + non_cacheable_
        else:
            cacheable.append(extractor)
            cacheable += cacheable_
            non_cacheable += non_cacheable_

        return cacheable, non_cacheable

    def _data_loader(self, subset, **kwargs):
        # Determine which Dataset class to use
        if subset.dataset.clip_duration is None:
            cls = VariableLengthDataset
        else:
            cls = FixedLengthDataset

        # Determine the transforms to be applied (if any)
        cacheable, non_cacheable = self.transforms(subset)
        if self.cache_features:
            loader_transforms = []
        else:
            loader_transforms = cacheable + non_cacheable

        # Instantiate Dataset
        dataset = cls(subset, self.block_length, self.hop_length, self.labeler)
        if self.cache_features:
            if len(cacheable) > 0:
                dataset = CachedDataset(TransformedDataset(dataset, cacheable))
            if len(non_cacheable) > 0:
                dataset = TransformedDataset(dataset, non_cacheable)

        loader = DataTransformer(
            dataset,
            loader_transforms,
            batch_size=self.batch_size,
            num_workers=self.n_workers,
            pin_memory=True,
            **kwargs,
        )
        return loader

    def _split(self, transforms):
        # Determine the cut-off point
        offset = 0
        while offset < len(transforms) and transforms[offset][1]:
            offset += 1

        transforms = next(zip(*transforms), [])
        cacheable = transforms[:offset]
        non_cacheable = transforms[offset:]
        return cacheable, non_cacheable
