"""mkwav

usage: mkwav [-hvn] FILE...

options:
   -h, --help
   -v, --verbose        Be verbose.
   -n, --dry-run        Don't actually create files, just show what will be done.

The mkwav command creates WAV files from audio data contained in genft .h5 files.
Specifically, it looks for these datasets: target, noise, and mixture.

"""
import wave
from os.path import splitext

import h5py
import numpy as np
from docopt import docopt

import sonusai
from sonusai import create_file_handler
from sonusai import initial_log_messages
from sonusai import logger
from sonusai import mixture
from sonusai import update_console_handler
from sonusai.utils import trim_docstring


def mkwav(files: list, dry_run: bool = False, verbose: bool = False):
    update_console_handler(verbose)
    initial_log_messages('mkwav')

    audio_names = ['target', 'noise', 'mixture']

    if dry_run:
        logger.info('Dry run')

    for file in files:
        base_name = splitext(file)[0]
        if verbose:
            logger.info('Processing {}'.format(file))
        try:
            with h5py.File(file, 'r') as f:
                keys = f.keys()
                for audio_name in audio_names:
                    if audio_name in keys:
                        out_name = base_name + '_' + audio_name + '.wav'
                        audio = np.array(f['/' + audio_name])
                        if verbose:
                            logger.info(' writing {} samples to {}'.format(len(audio), out_name))
                        if not dry_run:
                            with wave.open(out_name, 'w') as w:
                                w.setnchannels(mixture.channel_count)
                                w.setsampwidth(mixture.sample_bytes)
                                w.setframerate(mixture.sample_rate)
                                w.writeframesraw(audio)
        except Exception as e:
            logger.error('Error processing {}: {}'.format(file, e))


def main():
    try:
        args = docopt(trim_docstring(__doc__), version=sonusai.version(), options_first=True)

        log_name = 'mkwav.log'
        create_file_handler(log_name)

        files = args['FILE']
        if not isinstance(files, list):
            files = [files]

        mkwav(files=files, dry_run=args['--dry-run'], verbose=args['--verbose'])

    except KeyboardInterrupt:
        logger.info('Canceled due to keyboard interrupt')
        exit()


if __name__ == '__main__':
    main()
