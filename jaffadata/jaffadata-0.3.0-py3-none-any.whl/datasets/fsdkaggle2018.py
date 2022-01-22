import pandas as pd

import jaffadata as jd
from jaffadata import AudioDataset, DataSubset


class FSDKaggle2018(AudioDataset):
    def __init__(self, root_dir):
        super().__init__('FSDKaggle2018',
                         root_dir,
                         sample_rate=44100,
                         n_channels=1,
                         bit_depth=16,
                         clip_duration=None,
                         )

        # Read metadata from file
        metadata_dir = self.root_dir / 'FSDKaggle2018.meta'
        train_path = metadata_dir / 'train_post_competition.csv'
        test_path = metadata_dir / 'test_post_competition_scoring_clips.csv'
        train_tags = read_tags(train_path)
        test_tags = read_tags(test_path)

        # Add training set
        train_dir = self.root_dir / 'FSDKaggle2018.audio_train'
        self.add_subset(DataSubset('train', self, train_tags, train_dir))

        # Add test sets based on Public/Private split
        mask = test_tags.usage == 'Public'
        test_dir = self.root_dir / 'FSDKaggle2018.audio_test'
        public = DataSubset('test/public', self, test_tags[mask], test_dir)
        private = DataSubset('test/private', self, test_tags[mask], test_dir)
        combined = jd.concat([public, private], 'test')
        self.add_subset(public)
        self.add_subset(private)
        self.add_subset(combined)

        # Create alias
        self['training'] = self['train']

        self.label_set = sorted(train_tags.label.unique())

    @staticmethod
    def target(subset, index=None):
        return jd.binarize(subset, 'label', index)


def read_tags(path):
    return pd.read_csv(path, index_col=0, dtype={'label': 'category'})
