import pandas as pd

import jaffadata as jd
from jaffadata import AudioDataset, DataSubset


class FSDnoisy18k(AudioDataset):
    def __init__(self, root_dir):
        super().__init__('FSDnoisy18k',
                         root_dir,
                         sample_rate=44100,
                         n_channels=1,
                         bit_depth=16,
                         clip_duration=None,
                         )

        # Read metadata from file
        metadata_dir = self.root_dir / 'FSDnoisy18k.meta'
        train_tags = pd.read_csv(metadata_dir / 'train.csv', index_col=0)
        test_tags = pd.read_csv(metadata_dir / 'test.csv', index_col=0)

        # Add training set
        train_dir = self.root_dir / 'FSDnoisy18k.audio_train'
        self.add_subset(DataSubset('train', self, train_tags, train_dir))

        # Add test set
        test_dir = self.root_dir / 'FSDnoisy18k.audio_test'
        self.add_subset(DataSubset('test', self, test_tags, test_dir))

        # Create alias
        self['training'] = self['train']

        self.label_set = sorted(train_tags.label.unique())

    @staticmethod
    def target(subset, index=None):
        return jd.binarize(subset, 'label', index)
