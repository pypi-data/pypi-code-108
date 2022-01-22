import pandas as pd

import jaffadata as jd
from jaffadata import AudioDataset, DataSubset


class _ESC(AudioDataset):
    def __init__(self, name, root_dir, mask=None):
        super().__init__(name,
                         root_dir,
                         sample_rate=44100,
                         n_channels=1,
                         bit_depth=16,
                         clip_duration=5,
                         )

        # Read metadata from file
        tags = pd.read_csv(self.root_dir / 'meta/esc50.csv', index_col=0,
                           dtype={'category': 'category'})
        if mask is not None:
            tags = mask(tags)

        # Add DataSubet for whole dataset
        audio_dir = self.root_dir / 'audio'
        self.add_subset(DataSubset('root', self, tags, audio_dir))

        self.label_set = sorted(tags.category.unique())

    def split(self, fold):
        root = self['root']
        mask = root.tags.fold == fold
        train_set = root[~mask]
        test_set = root[mask]
        return train_set, test_set

    @staticmethod
    def target(subset, index=None):
        return jd.binarize(subset, 'category', index)


class ESC10(_ESC):
    def __init__(self, root_dir):
        super().__init__('ESC-10', root_dir, lambda tags: tags[tags.esc10])


class ESC50(_ESC):
    def __init__(self, root_dir):
        super().__init__('ESC-50', root_dir)
