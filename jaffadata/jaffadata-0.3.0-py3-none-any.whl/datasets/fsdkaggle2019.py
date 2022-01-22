import pandas as pd

import jaffadata as jd
from jaffadata import AudioDataset, DataSubset


class FSDKaggle2019(AudioDataset):
    def __init__(self, root_dir):
        super().__init__('FSDKaggle2019',
                         root_dir,
                         sample_rate=44100,
                         n_channels=1,
                         bit_depth=16,
                         clip_duration=None,
                         )

        # Read metadata from file
        metadata_dir = self.root_dir / 'FSDKaggle2019.meta'
        curated_path = metadata_dir / 'train_curated_post_competition.csv'
        noisy_path = metadata_dir / 'train_noisy_post_competition.csv'
        test_path = metadata_dir / 'test_post_competition.csv'
        curated_tags = read_tags(curated_path)
        noisy_tags = read_tags(noisy_path)
        test_tags = read_tags(test_path)

        # Add training sets
        curated_dir = self.root_dir / 'FSDKaggle2019.audio_train_curated'
        noisy_dir = self.root_dir / 'FSDKaggle2019.audio_train_noisy'
        curated = DataSubset('train/curated', self, curated_tags, curated_dir)
        noisy = DataSubset('train/noisy', self, noisy_tags, noisy_dir)
        combined = jd.concat([curated, noisy], 'train')
        self.add_subset(curated)
        self.add_subset(noisy)
        self.add_subset(combined)

        # Add test sets based on Public/Private split
        mask = test_tags.usage == 'Public'
        test_dir = self.root_dir / 'FSDKaggle2019.audio_test'
        public = DataSubset('test/public', self, test_tags[mask], test_dir)
        private = DataSubset('test/private', self, test_tags[mask], test_dir)
        combined = jd.concat([public, private], 'test')
        self.add_subset(public)
        self.add_subset(private)
        self.add_subset(combined)

        # Create aliases
        self['training'] = self['train']
        self['training/curated'] = self['train/curated']
        self['training/noisy'] = self['train/noisy']

        # Determine label set
        vocab_path = metadata_dir / 'vocabulary.csv'
        vocab = pd.read_csv(vocab_path, index_col=0, header=None)
        self.label_set = sorted(vocab[1])

    @staticmethod
    def target(subset, index=None):
        return jd.binarize(subset, 'labels', index)


def read_tags(path):
    df = pd.read_csv(path, index_col=0)
    df['labels'] = df['labels'].str.split(',')
    return df
