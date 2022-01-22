from pathlib import Path

import pandas as pd

import jaffadata as jd
from jaffadata import AudioDataset, DataSubset


class _Arca23K(AudioDataset):
    def __init__(self, name, root_dir, data_dirs,
                 train_gt_dir, test_gt_dir=None):
        super().__init__(name,
                         root_dir,
                         sample_rate=44100,
                         n_channels=1,
                         bit_depth=16,
                         clip_duration=None,
                         )

        if test_gt_dir is None:
            test_gt_dir = train_gt_dir

        # Read metadata from file
        train_tags = read_tags(train_gt_dir / 'train.csv')
        val_tags = read_tags(test_gt_dir / 'val.csv')
        test_tags = read_tags(test_gt_dir / 'test.csv')

        # Add DataSubsets for training, validation, and test sets
        self.add_subset(DataSubset('training', self, train_tags,
                                   data_dirs['training']))
        self.add_subset(DataSubset('validation', self, val_tags,
                                   data_dirs['validation']))
        self.add_subset(DataSubset('test', self, test_tags,
                                   data_dirs['test']))

        self.label_set = sorted(train_tags.label.unique())

    @staticmethod
    def target(subset, index=None):
        return jd.binarize(subset, 'label', index)


class Arca23K(_Arca23K):
    def __init__(self, root_dir, fsd50k_dir):
        root_dir = Path(root_dir)
        fsd50k_dir = Path(fsd50k_dir)

        super().__init__('ARCA23K',
                         root_dir,
                         {'training': root_dir / 'ARCA23K.audio',
                          'validation': fsd50k_dir / 'FSD50K.dev_audio',
                          'test': fsd50k_dir / 'FSD50K.eval_audio',
                          },
                         root_dir / 'ARCA23K.ground_truth',
                         root_dir / 'ARCA23K-FSD.ground_truth',
                         )


class Arca23K_FSD(_Arca23K):
    def __init__(self, root_dir, fsd50k_dir):
        root_dir = Path(root_dir)
        fsd50k_dir = Path(fsd50k_dir)

        super().__init__('ARCA23K-FSD',
                         root_dir,
                         {'training': fsd50k_dir / 'FSD50K.dev_audio',
                          'validation': fsd50k_dir / 'FSD50K.dev_audio',
                          'test': fsd50k_dir / 'FSD50K.eval_audio',
                          },
                         root_dir / 'ARCA23K-FSD.ground_truth',
                         )


def read_tags(path):
    df = pd.read_csv(path, index_col=0, dtype={'label': 'category'})
    # Add missing file extension to file names
    fnames = [f'{name}.wav' for name in df.index]
    df.index = pd.Index(fnames, name=df.index.name)
    return df
