"""genft

usage: genft [-hv] (-d MIXDB) [-i MIXID] [-o OUTPUT]

options:
    -h, --help
    -v, --verbose                   Be verbose.
    -d MIXDB, --mixdb MIXDB         Mixture database JSON file.
    -i MIXID, --mixid MIXID         Mixtures to include (using Python slice notation). [default: :].
    -o OUTPUT, --output OUTPUT      Output HDF5 file.

Generate a SonusAI feature/truth file from a SonusAI mixture database.

Inputs:
    MIXDB       A SonusAI mixture database JSON file.
    MIXID       Mixtures to include (uses Python slice notation, i.e., start:stop:step).

Outputs:
    OUTPUT.h5   A SonusAI feature HDF5 file (containing 'feature' and 'truth_f' datasets).
    genft.log

"""

import json
from os.path import exists
from os.path import splitext
from typing import List
from typing import Union

import h5py
import numpy as np
from docopt import docopt
from pyaaware import FeatureGenerator
from pyaaware import ForwardTransform
from tqdm import tqdm

import sonusai
from sonusai import create_file_handler
from sonusai import genmix
from sonusai import initial_log_messages
from sonusai import logger
from sonusai import update_console_handler
from sonusai.utils import trim_docstring


def truth_reduction(x: np.ndarray, func: str) -> np.ndarray:
    if func == 'max':
        return np.max(x, axis=1)

    if func == 'mean':
        return np.mean(x, axis=1)

    logger.error('Invalid truth reduction function: {}'.format(func))
    exit()


def genft(mixdb: dict,
          mixid: Union[str, List[int]],
          show_progress: bool = False) -> (np.ndarray, np.ndarray, dict):
    logger.info('')
    logger.info('Generating mixtures')

    mixture, truth_t, _, _, _, mixdb_out = genmix(mixdb=mixdb,
                                                  mixid=mixid,
                                                  compute_segsnr=False,
                                                  show_progress=show_progress)

    total_samples = len(mixture)
    if total_samples % mixdb_out['frame_size'] != 0:
        logger.error('Number of samples in mixture is not a multiple of {}'.format(mixdb_out['frame_size']))
        exit()

    fft = ForwardTransform(N=mixdb_out['frame_size'] * 4, R=mixdb_out['frame_size'])
    fg = FeatureGenerator(frame_size=mixdb_out['frame_size'],
                          feature_mode=mixdb_out['feature'],
                          num_classes=mixdb_out['num_classes'],
                          truth_mutex=mixdb_out['truth_mutex'])

    transform_frames = total_samples // mixdb_out['frame_size']
    feature_frames = transform_frames // (fg.step * fg.decimation)

    feature = np.empty((feature_frames, fg.stride, fg.num_bands), dtype=np.single)
    truth_f = np.empty((feature_frames, fg.num_classes), dtype=np.single)

    logger.info('')
    logger.info('Generating {} feature frames'.format(feature_frames))
    feature_frame = 0
    for mixture_record in (tqdm(mixdb_out['mixtures'], desc='Processing') if show_progress else mixdb_out['mixtures']):
        offsets = range(mixture_record['i_sample_offset'],
                        mixture_record['i_sample_offset'] + mixture_record['samples'],
                        mixdb_out['frame_size'])
        for offset in offsets:
            mixture_fd = fft.execute(np.single(mixture[offset:offset + mixdb_out['frame_size']]) / 32768)
            fg.execute(mixture_fd,
                       truth_reduction(truth_t[:, offset:offset + mixdb_out['frame_size']],
                                       mixdb_out['truth_reduction_function']))
            if fg.eof():
                feature[feature_frame, :, :] = np.reshape(fg.feature(), (fg.stride, fg.num_bands))
                truth_f[feature_frame, :] = fg.truth()
                feature_frame += 1

        fft.reset()
        fg.reset()

    return feature, truth_f, mixdb_out


def main():
    try:
        args = docopt(trim_docstring(__doc__), version=sonusai.version(), options_first=True)

        verbose = args['--verbose']
        mixdb_name = args['--mixdb']
        mixid = args['--mixid']
        output_name = args['--output']

        if not output_name:
            output_name = splitext(mixdb_name)[0] + '.h5'

        log_name = 'genft.log'
        create_file_handler(log_name)
        update_console_handler(verbose)
        initial_log_messages('genft')

        if not exists(mixdb_name):
            logger.error('{} does not exist'.format(mixdb_name))
            exit()

        with open(mixdb_name, encoding='utf-8') as f:
            mixdb = json.load(f)

        feature, truth_f, mixdb_out = genft(mixdb=mixdb,
                                            mixid=mixid,
                                            show_progress=True)

        with h5py.File(output_name, 'w') as f:
            f.attrs['mixdb'] = json.dumps(mixdb_out)
            f.create_dataset(name='feature', data=feature)
            f.create_dataset(name='truth_f', data=truth_f)
            logger.info('Wrote {}'.format(output_name))

    except KeyboardInterrupt:
        logger.info('Canceled due to keyboard interrupt')
        exit()


if __name__ == '__main__':
    main()
