"""genft

usage: genft [-hv] (-i INPUT) [-o OUTPUT]

options:
    -h, --help
    -v, --verbose                   Be verbose.
    -i INPUT, --input INPUT         A SonusAI mixture HDF5 file.
    -o OUTPUT, --output OUTPUT      Output HDF5 file.

Generate a SonusAI feature file from a SonusAI mixture.

Inputs:
    INPUT       A SonusAI mixture HDF5 file (containing 'mixdb', 'mixture', and 'truth_t' datasets).

Outputs:
    OUTPUT.h5   A SonusAI feature HDF5 file (containing 'feature' and 'truth_f' datasets).
    genft.log

"""

import json
from os.path import exists
from os.path import splitext

import h5py
import numpy as np
from docopt import docopt
from pyaaware import FeatureGenerator
from pyaaware import ForwardTransform
from tqdm import tqdm

import sonusai
from sonusai import create_file_handler
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
          mixture: np.ndarray,
          truth_t: np.ndarray,
          verbose: bool = False,
          show_progress: bool = False) -> (np.ndarray, np.ndarray):
    update_console_handler(verbose)
    initial_log_messages('genft')

    total_samples = len(mixture)
    if total_samples % mixdb['frame_size'] != 0:
        logger.error('Number of samples in mixture is not a multiple of {}'.format(mixdb['frame_size']))
        exit()

    fft = ForwardTransform(N=mixdb['frame_size'] * 4, R=mixdb['frame_size'])
    fg = FeatureGenerator(frame_size=mixdb['frame_size'],
                          feature_mode=mixdb['feature'],
                          num_classes=mixdb['num_classes'],
                          truth_mutex=mixdb['truth_mutex'])

    transform_frames = total_samples // mixdb['frame_size']
    feature_frames = transform_frames // (fg.step * fg.decimation)

    feature = np.empty((feature_frames, fg.stride, fg.num_bands), dtype=np.single)
    truth_f = np.empty((feature_frames, fg.num_classes), dtype=np.single)

    feature_frame = 0
    for mixture_record in (tqdm(mixdb['mixtures'], desc='Processing') if show_progress else mixdb['mixtures']):
        offsets = range(mixture_record['i_sample_offset'],
                        mixture_record['i_sample_offset'] + mixture_record['samples'],
                        mixdb['frame_size'])
        for offset in offsets:
            mixture_fd = fft.execute(np.single(mixture[offset:offset + mixdb['frame_size']]) / 32768)
            fg.execute(mixture_fd,
                       truth_reduction(truth_t[:, offset:offset + mixdb['frame_size']],
                                       mixdb['truth_reduction_function']))
            if fg.eof():
                feature[feature_frame, :, :] = np.reshape(fg.feature(), (fg.stride, fg.num_bands))
                truth_f[feature_frame, :] = fg.truth()
                feature_frame += 1

        fft.reset()
        fg.reset()

    return feature, truth_f


def main():
    try:
        args = docopt(trim_docstring(__doc__), version=sonusai.version(), options_first=True)

        verbose = args['--verbose']
        input_name = args['--input']
        output_name = args['--output']

        if not output_name:
            output_name = splitext(input_name)[0] + '_ft.h5'

        log_name = 'genft.log'
        create_file_handler(log_name)

        if not exists(input_name):
            logger.error('{} does not exist'.format(input_name))
            exit()

        with h5py.File(input_name, 'r') as f:
            mixdb = json.loads(f.attrs['mixdb'])
            mixture = np.array(f['/mixture'])
            truth_t = np.array(f['/truth_t'])

        feature, truth_f = genft(mixdb=mixdb,
                                 mixture=mixture,
                                 truth_t=truth_t,
                                 verbose=verbose,
                                 show_progress=True)

        with h5py.File(output_name, 'w') as f:
            f.attrs['mixdb'] = json.dumps(mixdb)
            f.create_dataset(name='feature', data=feature)
            f.create_dataset(name='truth_f', data=truth_f)
            logger.info('Wrote {}'.format(output_name))

    except KeyboardInterrupt:
        logger.info('Canceled due to keyboard interrupt')
        exit()


if __name__ == '__main__':
    main()
