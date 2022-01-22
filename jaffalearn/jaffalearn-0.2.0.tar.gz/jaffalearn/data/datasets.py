import numpy as np

import torch
import torch.nn.functional as F
from torch.utils.data import Dataset

import torchaudio


class _AudioDataset(Dataset):
    def __init__(self,
                 subset,
                 block_length=None,
                 hop_length=None,
                 labeler='default',
                 pad_fn=None,
                 ):
        if block_length is None and subset.dataset.clip_duration is None:
            raise ValueError('Block length undetermined (block_length=None '
                             f'and {subset.dataset.name} is variable-length)')

        self.subset = subset
        self.block_length = block_length or subset.dataset.clip_duration
        self.hop_length = hop_length or self.block_length

        # Use canonical labeling method if 'default' is specified
        if labeler == 'default':
            labeler = subset.dataset.target
        self.labeler = labeler

        self.pad_fn = pad_fn or zero_pad

    def load_audio(self, file_index, block_index):
        path = self.subset.audio_paths[file_index]
        sample_rate = self.subset.dataset.sample_rate
        num_frames = int(self.block_length * sample_rate)
        offset = block_index * int(self.hop_length * sample_rate)
        x, _ = torchaudio.load(path, offset, num_frames)

        # Pad data to block length if necessary
        remainder = int(sample_rate * self.block_length) - x.shape[1]
        if remainder > 0:
            x = self.pad_fn(x, remainder)

        return x

    def target(self, file_index):
        if self.labeler is None:
            return None

        y = self.labeler(self.subset, self.subset.audio_paths[file_index].name)
        if y is not None:
            return torch.as_tensor(y.values, dtype=torch.float32)


class FixedLengthDataset(_AudioDataset):
    def __init__(self,
                 subset,
                 block_length=None,
                 hop_length=None,
                 labeler='default',
                 pad_fn=None,
                 ):
        super().__init__(subset, block_length, hop_length, labeler, pad_fn)

        # Calculate number of blocks per clip
        if subset.dataset.clip_duration is not None:
            numerator = subset.dataset.clip_duration - self.block_length
            self.n_blocks = int(numerator / self.hop_length) + 1
        else:
            self.n_blocks = 1

    def __getitem__(self, index):
        file_index, block_index = divmod(index, self.n_blocks)
        x = self.load_audio(file_index, block_index)
        y = self.target(file_index)

        if y is None:
            return x
        return x, y

    def __len__(self):
        return len(self.subset.audio_paths) * self.n_blocks


class VariableLengthDataset(_AudioDataset):
    def __init__(self,
                 subset,
                 block_length=1,
                 hop_length=None,
                 labeler='default',
                 length_fn=None,
                 pad_fn=None,
                 ):
        super().__init__(subset, block_length, hop_length, labeler, pad_fn)

        # Create mapping between block indexes and clip indexes
        # See __getitem__() below for usage of self.index_map
        self.index_map = []
        length_fn = length_fn or padded_length
        lengths = np.array([length_fn(length, self.block_length)
                            for length in audio_lengths(subset)])
        n_blocks = (lengths - self.block_length) / self.hop_length
        n_blocks = n_blocks.astype(int) + 1
        for i, n in enumerate(n_blocks):
            self.index_map += list(zip([i] * n, range(n)))

    def __getitem__(self, index):
        file_index, block_index = self.index_map[index]
        x = self.load_audio(file_index, block_index)
        y = self.target(file_index)

        if y is None:
            return x, file_index
        return x, y, file_index

    def __len__(self):
        return len(self.index_map)


class TransformedDataset(Dataset):
    def __init__(self, dataset, transforms):
        self.dataset = dataset
        if not isinstance(transforms, (tuple, list)):
            self.transforms = [transforms]
        else:
            self.transforms = list(transforms)

    def __getitem__(self, index):
        data = self.dataset[index]
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

    def __len__(self):
        return len(self.dataset)


def audio_lengths(subset):
    # Note that 44 is assumed to be the WAV header size
    bytes_per_sample = subset.dataset.bit_depth / 8
    bytes_per_second = subset.dataset.sample_rate * bytes_per_sample
    lengths = [(path.stat().st_size - 44) / bytes_per_second
               for path in subset.audio_paths]
    return lengths


def padded_length(raw_length, block_length, margin=0.1):
    q, r = divmod(raw_length, block_length)
    if q == 0:
        factor = int(r > 0)
    elif r > block_length * margin:
        factor = q + 1
    else:
        factor = q

    return factor * block_length


def zero_pad(x, padding):
    return F.pad(x, (0, padding))
