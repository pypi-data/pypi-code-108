import json

import h5py
import numpy as np


def read_feature_data(filename: str) -> dict:
    with h5py.File(name=filename, mode='r') as f:
        feature_data = {'config':               json.loads(f.attrs['config']),
                        'feature':              np.array(f['feature']),
                        'feature_samples':      np.array(f['feature_samples']),
                        'mixture_database':     json.loads(f.attrs['mixture_database']),
                        'noise_augmentations':  json.loads(f.attrs['noise_augmentations']),
                        'noise_files':          json.loads(f.attrs['noise_files']),
                        'segsnr':               np.array(f['segsnr']),
                        'target_augmentations': json.loads(f.attrs['target_augmentations']),
                        'target_files':         json.loads(f.attrs['target_files']),
                        'truth':                np.array(f['truth'])
                        }

        if 'mixture' in f.keys():
            feature_data['mixture'] = np.array(f['mixture'])

        if 'target' in f.keys():
            feature_data['target'] = np.array(f['target'])

        if 'noise' in f.keys():
            feature_data['noise'] = np.array(f['noise'])

        return feature_data
