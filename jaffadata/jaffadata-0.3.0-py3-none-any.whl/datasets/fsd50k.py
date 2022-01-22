import pandas as pd

import jaffadata as jd
from jaffadata import AudioDataset, DataSubset


class FSD50K(AudioDataset):
    def __init__(self, root_dir):
        super().__init__('FSD50K',
                         root_dir,
                         sample_rate=44100,
                         n_channels=1,
                         bit_depth=16,
                         clip_duration=None,
                         )

        # Read metadata from file
        gt_dir = self.root_dir / 'FSD50K.ground_truth'
        dev_tags = read_tags(gt_dir / 'dev.csv')
        eval_tags = read_tags(gt_dir / 'eval.csv')

        # Create DataSubset for dev set
        dev_dir = self.root_dir / 'FSD50K.dev_audio'
        dev_set = DataSubset('dev', self, dev_tags, dev_dir)
        # Split into training and validation sets
        self.add_subset(dev_set.subset('train', dev_tags.split == 'train'))
        self.add_subset(dev_set.subset('val', dev_tags.split == 'val'))

        # Create DataSubset for eval set
        eval_dir = self.root_dir / 'FSD50K.eval_audio'
        self.add_subset(DataSubset('eval', self, eval_tags, eval_dir))

        # Create aliases
        self['training'] = self['train']
        self['validation'] = self['val']
        self['test'] = self['eval']

        # Determine label set
        vocab_path = gt_dir / 'vocabulary.csv'
        vocab = pd.read_csv(vocab_path, index_col=0, header=None)
        self.label_set = sorted(vocab[1])

    @staticmethod
    def target(subset, index=None):
        return jd.binarize(subset, 'labels', index)


def read_tags(path):
    df = pd.read_csv(path, index_col=0)
    # Add missing file extension to file names
    fnames = [f'{name}.wav' for name in df.index]
    df.index = pd.Index(fnames, name=df.index.name)
    df['labels'] = df['labels'].str.split(',')
    df['mids'] = df['mids'].str.split(',')
    return df
