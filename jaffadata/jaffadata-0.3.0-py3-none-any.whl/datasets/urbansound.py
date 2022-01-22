import pandas as pd

import jaffadata as jd
from jaffadata import AudioDataset, DataSubset


class UrbanSound8K(AudioDataset):
    def __init__(self, root_dir, sample_rate=44100,
                 n_channels=1, bit_depth=16):
        super().__init__('UrbanSound8K',
                         root_dir,
                         sample_rate,
                         n_channels,
                         bit_depth,
                         clip_duration=4,
                         )

        # Read metadata from file
        metadata_path = self.root_dir / 'metadata/UrbanSound8K.csv'
        tags = pd.read_csv(metadata_path, index_col=0,
                           dtype={'class': 'category'})

        # Add DataSubet for whole dataset
        folds = [DataSubset('', self, tags[tags.fold == fold],
                            self.root_dir / f'audio/fold{fold}')
                 for fold in range(1, 11)]
        self.add_subset(jd.concat(folds, 'root'))

        self.label_set = sorted(tags['class'].unique())

    def split(self, fold):
        root = self['root']
        mask = root.tags.fold == fold
        train_set = root[~mask]
        test_set = root[mask]
        return train_set, test_set

    @staticmethod
    def target(subset, index=None):
        return jd.binarize(subset, 'class', index)
