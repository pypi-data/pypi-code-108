import re

import pandas as pd

from jaffadata import AudioDataset, DataSubset


LABEL_SET_2020 = [
    'alarm',
    'crying baby',
    'crash',
    'barking dog',
    'running engine',
    'female scream',
    'female speech',
    'burning fire',
    'footsteps',
    'knocking on door',
    'male scream',
    'male speech',
    'ringing phone',
    'piano',
]


LABEL_SET_2021 = [
    'alarm',
    'crying baby',
    'crash',
    'barking dog',
    'female scream',
    'female speech',
    'footsteps',
    'knocking on door',
    'male scream',
    'male speech',
    'ringing phone',
    'piano',
]


class TauNigens2020(AudioDataset):
    def __init__(self, root_dir):
        super().__init__('TAU-NIGENS 2020',
                         root_dir,
                         sample_rate=24000,
                         n_channels=4,
                         bit_depth=16,
                         clip_duration=60,
                         label_set=LABEL_SET_2020,
                         )

        self.n_frames = 600

        # Create DataSubsets for dev set
        dev_tags = read_dev_tags(self.root_dir / 'metadata_dev', ov=True)
        for fmt_name in ['mic_dev', 'foa_dev']:
            audio_dir = self.root_dir / fmt_name
            dataset = DataSubset('all', self, dev_tags, audio_dir)
            self.add_subset(dataset.subset(f'{fmt_name}/training',
                                           dev_tags.fold >= 3))
            self.add_subset(dataset.subset(f'{fmt_name}/validation',
                                           dev_tags.fold == 2))
            self.add_subset(dataset.subset(f'{fmt_name}/test',
                                           dev_tags.fold == 1))

        # Create DataSubsets for eval set
        eval_tags = read_eval_tags(self.root_dir / 'metadata_eval')
        for name in ['mic_eval', 'foa_eval']:
            subset = DataSubset(name, self, eval_tags, self.root_dir / name)
            self.add_subset(subset)

        # Set default training/validation/test sets
        self['training'] = self['mic_dev/training']
        self['validation'] = self['mic_dev/validation']
        self['dev_test'] = self['mic_dev/test']
        self['test'] = self['mic_eval']

    @staticmethod
    def target(subset, index=None):
        return target(subset, index)


class TauNigens2021(AudioDataset):
    def __init__(self, root_dir):
        super().__init__('TAU-NIGENS 2021',
                         root_dir,
                         sample_rate=24000,
                         n_channels=4,
                         bit_depth=16,
                         clip_duration=60,
                         label_set=LABEL_SET_2021,
                         )

        self.n_frames = 600

        # Create DataSubsets for dev set
        mapping = {
            'training': 'train',
            'validation': 'val',
            'test': 'test',
        }
        for fmt_name in ['mic_dev', 'foa_dev']:
            for split, orig in mapping.items():
                name = f'{fmt_name}/{split}'
                metadata_dir = self.root_dir / f'metadata_dev/dev-{orig}'
                tags = read_dev_tags(metadata_dir)
                audio_dir = self.root_dir / fmt_name / 'dev-{orig}'
                subset = DataSubset(name, self, tags, audio_dir)
                self.add_subset(subset)

        # Create DataSubsets for eval set
        eval_tags = read_eval_tags(self.root_dir / 'metadata_eval')
        for name in ['mic_eval', 'foa_eval']:
            audio_dir = self.root_dir / name / 'eval-test'
            subset = DataSubset(name, self, eval_tags, audio_dir)
            self.add_subset(subset)

        # Set default training/validation/test sets
        self['training'] = self['mic_dev/training']
        self['validation'] = self['mic_dev/validation']
        self['dev_test'] = self['mic_dev/test']
        self['test'] = self['mic_eval']

    @staticmethod
    def target(subset, index=None):
        return target(subset, index)


def target(subset, index=None):
    if index is None:
        fnames = subset.tags.index.unique(level=0)
        y = pd.concat([subset.target(idx) for idx in fnames], keys=fnames)
        return y

    n_classes = len(subset.dataset.label_set)
    y_columns = list(range(n_classes))
    y_index = list(range(subset.dataset.n_frames))
    y = subset.tags.loc[index]

    y = binarize(y, y_index, y_columns)
    y.columns = subset.dataset.label_set
    return y


def binarize(y, index, columns):
    y = pd.get_dummies(y.label)
    # Ensure y is not missing any columns
    y = y.T.reindex(columns, fill_value=0).T
    # Merge (OR) labels if they are for the same frame
    y = y.groupby(y.index).max()
    # Insert labels (zeros) for inactive frames
    y = y.reindex(index, fill_value=0)  # (n_frames, n_classes)
    return y


def read_dev_tags(metadata_dir, ov=False):
    pattern_str = r'fold([0-9])_room([0-9])_mix([0-9]{3})'
    if ov:
        pattern_str += '_ov([0-9])'
    pattern = re.compile(pattern_str)

    def _read_df(path):
        columns = ['label', 'track', 'azimuth', 'elevation']
        df = pd.read_csv(path, index_col=0, header=None, names=columns)

        # Extract additional information from file name
        match = pattern.match(str(path.name))
        df['fold'] = int(match[1])
        df['room'] = int(match[2])
        df['mix'] = int(match[3])
        if ov:
            df['ov'] = int(match[4])

        return df

    paths = sorted(metadata_dir.glob('fold*.csv'))
    df = pd.concat([_read_df(path) for path in paths],
                   keys=[path.name.replace('csv', 'wav') for path in paths],
                   names=['fname', 'frame_index'])
    return df


def read_eval_tags(metadata_dir):
    def _read_df(path):
        columns = ['label', 'track', 'azimuth', 'elevation']
        return pd.read_csv(path, index_col=0, header=None, names=columns)

    paths = sorted(metadata_dir.glob('mix*.csv'))
    df = pd.concat([_read_df(path) for path in paths],
                   keys=[path.name.replace('csv', 'wav') for path in paths],
                   names=['fname', 'frame_index'])
    return df
