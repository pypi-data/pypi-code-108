"""genmixdb

usage: genmixdb [-hv] CONFIG...

options:
   -h, --help
   -v, --verbose    Be verbose.

Create mixture database data for training and evaluation.

genmixdb creates a database of training and evaluation feature and truth data generation information. It allows
the choice of audio neural-network feature types that are supported by the Aaware real-time front-end and truth
data that is synchronized frame-by-frame with the feature data.

Here are some examples:

#### Adding target data
Suppose you have an audio file which is an example, or target, of what you want to
recognize or detect. Of course, for training a NN you also need truth data for that
file (also called labels). If you don't already have it, genmixdb can create truth using
energy-based sound detection on each frame of the feature data. You can also select
different feature types. Here's an example:

genmixdb target_gfr32ts2.yml

where target_gfr32ts2.yml contains:
---
targets:
  - data/target.wav

feature: gfr32ts2

target_augmentations:
  -
    normalize: -3.5
...

The mixture database is written to a JSON file that inherits the base name of the config file.

#### Target data mix with noise and augmentation

genmixdb mix_gfr32ts2.yml

where mix_gfr32ts2.yml contains:
---
targets:
  - data/target.wav

noises:
  - data/noise.wav

target_count: 5

feature: gfr32ts2

output: data/my_mix.h5

target_augmentations:
  -
    normalize: -3.5
    pitch: [-3, 0, 3]
    tempo: [0.8, 1, 1.2]
    snr: 20

noise_augmentations:
  -
    normalize: -3.5
...

In this example a time-domain mixture is created and feature data is calculated as
specified by 'feature: gfr32ts2'. Various feature types are available which vary in
spectral and temporal resolution (4 ms or higher), and other feature algorithm
parameters. The total feature size, dimension, and #frames for mixture is reported
in the log file (the log file name is derived from the output file base name; in this
case it would be mix_gfr32ts2.log).

Truth (labels) can be automatically created per feature output frame based on sound
energy detection. By default, these are appended to the feature data in a single HDF5
output file. By default, truth/label generation is turned on with default algorithm
and threshold levels (see truth section) and a single class, i.e., detecting a single
type of sound. The truth format is a single float per class representing the
probability of activity/presence, and multi-class truth/labels are possible by
specifying the number of classes and either a scalar index or a vector of indices in
which to put the truth result. For example, 'num_class: 3' and  'truth_index: 2' adds
a 1x3 vector to the feature data with truth put in index 2 (others would be 0) for
data/target.wav being an audio clip from sound type of class 2.

The mixture is created with potential data augmentation functions in the following way:
1. apply noise augmentation rule
2. apply target augmentation rule
3. adjust noise gain for specific SNR
4. add augmented noise to augmented target

The mixture length is the target length by default, and the noise signal is repeated
if it is shorter, or trimmed if longer. If 'target_count: <count>' is specified, then
the target audio is concatenated <count> times for each augmentation rule.
(See the Augmentation section for details on augmentation rules.)

#### Target and noise using path lists

Target and noise audio is specified as a list containing text files, audio files, and
file globs. Text files are processed with items on each line where each item can be a
text file, an audio file, or a file glob. Each item will be searched for audio files
which can be WAV, MP3, FLAC, AIFF, or OGG format with any sample rate, bit depth, or
channel count. All audio files will be converted to 16 kHz, 16-bit, single channel
format before processing. For example,

genmixdb dog-bark.yml

where dog-bark.yml contains:
---
targets:
  - slib/dog-outside/*.wav
  - slib/dog-inside/*.wav

will find all .wav files in the specified directories and process them as targets.

"""
import json
import re
from copy import deepcopy
from glob import glob
from numbers import Number
from os import listdir
from os.path import dirname
from os.path import isabs
from os.path import isdir
from os.path import join
from os.path import splitext
from random import seed
from random import uniform
from time import gmtime
from time import strftime

import numpy as np
import sox
import yaml
from docopt import docopt
from pyaaware import FeatureGenerator
from tqdm import tqdm

import sonusai
from sonusai import create_file_handler
from sonusai import initial_log_messages
from sonusai import logger
from sonusai import update_console_handler
from sonusai.mixture import apply_augmentation
from sonusai.mixture import generate_truth
from sonusai.mixture import get_class_weights_threshold
from sonusai.mixture import get_config_from_file
from sonusai.mixture import get_next_noise
from sonusai.mixture import read_audio
from sonusai.mixture import update_class_count
from sonusai.utils import expandvars
from sonusai.utils import human_readable_size
from sonusai.utils import trim_docstring


def genmixdb(config: dict, show_progress: bool = False) -> dict:
    required_keys = [
        'class_labels',
        'class_weights_threshold',
        'dither',
        'feature',
        'frame_size',
        'noises',
        'noise_augmentations',
        'num_classes',
        'seed',
        'target_augmentations',
        'targets',
        'truth_config',
        'truth_function',
        'truth_index',
        'truth_mode',
        'truth_reduction_function',
    ]
    for key in required_keys:
        if key not in config.keys():
            logger.error('Missing {} in config'.format(key))
            exit()

    seed(config['seed'])

    logger.debug('Seed: {}'.format(config['seed']))
    logger.debug('Configuration:')
    logger.debug(yaml.dump(config))

    targets = get_input_files(config['targets'], cfg={'truth_index':    config['truth_index'],
                                                      'truth_function': config['truth_function'],
                                                      'truth_config':   config['truth_config']})
    if len(targets) == 0:
        logger.error('Canceled due to no targets')
        exit()

    logger.debug('Expanded list of targets:')
    logger.debug(yaml.dump([sub['name'] for sub in targets], default_flow_style=False))

    noises = get_input_files(config['noises'])
    if len(noises) == 0:
        logger.warning('Did not find any noises; using default noise: {}'.format(sonusai.mixture.default_noise))
        noises = get_input_files([sonusai.mixture.default_noise], silent=True)
    logger.debug('Expanded list of noises:')
    logger.debug(yaml.dump([sub['name'] for sub in noises], default_flow_style=False))

    target_augmentations = get_augmentations(config['target_augmentations'], target=True)
    expanded_target_augmentations = ''
    for augmentation in target_augmentations:
        expanded_target_augmentations += '- {}\n'.format(augmentation)
    logger.debug('Expanded list of target augmentations:')
    logger.debug(expanded_target_augmentations)

    noise_augmentations = get_augmentations(config['noise_augmentations'], target=False)
    expanded_noise_augmentations = ''
    for augmentation in noise_augmentations:
        expanded_noise_augmentations += '- {}\n'.format(augmentation)
    logger.debug('Expanded list of noise augmentations:')
    logger.debug(expanded_noise_augmentations)

    total_combinations = len(targets) * len(noises) * len(target_augmentations) * len(noise_augmentations)
    logger.info('')
    logger.info('Found {} combinations to process'.format(total_combinations))

    # TODO: check calculation of estimated duration; this is probably not quite correct
    total_duration = len(noises) * len(noise_augmentations) * sum([sub['duration'] for sub in targets]) * len(
        target_augmentations)

    class_weights_threshold = get_class_weights_threshold(config)

    if config['truth_mode'] not in ['normal', 'mutex']:
        logger.error('invalid truth_mode: {}'.format(config['truth_mode']))
        exit()

    if config['truth_mode'] == 'mutex':
        max_class = config['num_classes'] - 1
        truth_mutex = 1
    else:
        max_class = config['num_classes']
        truth_mutex = 0

    fg = FeatureGenerator(feature_mode=config['feature'],
                          frame_size=config['frame_size'],
                          num_classes=config['num_classes'],
                          truth_mutex=truth_mutex)

    num_bands = fg.num_bands
    stride = fg.stride
    step = fg.step
    decimation = fg.decimation

    transform_frame_ms = float(config['frame_size']) / float(sonusai.mixture.sample_rate / 1000)
    feature_ms = transform_frame_ms * decimation * stride
    feature_step_ms = transform_frame_ms * decimation * step
    feature_samples = config['frame_size'] * decimation * stride
    feature_step_samples = config['frame_size'] * decimation * step
    total_samples = total_duration * sonusai.mixture.sample_rate
    total_features = total_samples / feature_step_samples

    # Feature
    total_size = total_features * num_bands * stride * sonusai.mixture.float_bytes
    # Truth
    total_size += total_features * sonusai.mixture.float_bytes

    logger.info('')
    logger.info('Estimated duration:   {}'.format(strftime('%H:%M:%S', gmtime(total_duration))))
    logger.info('Estimated size:       {}'.format(human_readable_size(total_size, 0)))
    logger.info('Feature shape:        {} x {} ({} total params)'.format(stride, num_bands,
                                                                         stride * num_bands))
    logger.info('Feature samples:      {} samples ({} ms)'.format(feature_samples, feature_ms))
    logger.info('Feature step samples: {} samples ({} ms)'.format(feature_step_samples, feature_step_ms))

    mixdb = {
        'class_count':              [],
        'class_labels':             config['class_labels'],
        'class_weights_threshold':  list(class_weights_threshold),
        'dither':                   config['dither'],
        'feature':                  config['feature'],
        'feature_step_samples':     feature_step_samples,
        'frame_size':               config['frame_size'],
        'mixtures':                 [],
        'noise_augmentations':      noise_augmentations,
        'noises':                   noises,
        'num_classes':              config['num_classes'],
        'target_augmentations':     target_augmentations,
        'targets':                  targets,
        'truth_mutex':              truth_mutex,
        'truth_reduction_function': config['truth_reduction_function'],
    }

    total_class_count = [0] * config['num_classes']
    total_samples = 0
    mixtures = []

    # Read in all audio data beforehand to avoid reading it multiple times in the loop
    raw_noise_audio = []
    for noise in noises:
        raw_noise_audio.append(read_audio(name=noise['name'], dither=config['dither']))

    raw_target_audio = []
    for target in targets:
        raw_target_audio.append(read_audio(name=target['name'], dither=config['dither']))

    with tqdm(desc='Processing', total=total_combinations, disable=(not show_progress)) as progress_bar:
        for noise_index, noise in enumerate(noises):
            for noise_augmentation_index, noise_augmentation in enumerate(noise_augmentations):
                augmented_noise_audio = apply_augmentation(audio_in=raw_noise_audio[noise_index],
                                                           augmentation=noise_augmentation,
                                                           length_common_denominator=1,
                                                           dither=config['dither'])
                noise_offset = 0
                for target_index, target in enumerate(targets):
                    for target_augmentation_index, target_augmentation in enumerate(target_augmentations):
                        if not isinstance(target['truth_index'], list):
                            target['truth_index'] = [target['truth_index']]

                        if any(i > max_class for i in target['truth_index']):
                            logger.error('invalid truth_index')
                            exit()

                        mixture_record = {'target_file_index':         target_index,
                                          'noise_file_index':          noise_index,
                                          'noise_offset':              noise_offset,
                                          'target_augmentation_index': target_augmentation_index,
                                          'noise_augmentation_index':  noise_augmentation_index}

                        augmented_target_audio = apply_augmentation(audio_in=raw_target_audio[target_index],
                                                                    augmentation=target_augmentation,
                                                                    length_common_denominator=feature_step_samples,
                                                                    dither=config['dither'])

                        noise_segment, noise_offset = get_next_noise(offset_in=noise_offset,
                                                                     length=len(augmented_target_audio),
                                                                     audio_in=augmented_noise_audio)

                        # target_gain is the sum of 'gain', noise overflow adjustment, and mixture
                        # overflow adjustment. It is used to return the target audio to its normalized
                        # level when calculating truth (unless target gain is set to zero, in which
                        # case the truth will be all zeros).
                        if 'gain' in target_augmentation:
                            target_gain = 10 ** (target_augmentation['gain'] / 20)
                        else:
                            target_gain = 1

                        if 'snr' in target_augmentation:
                            if target_augmentation['snr'] < -96:
                                # Special case for zeroing out target data
                                mixture_record['target_snr_gain'] = 0
                                mixture_record['noise_snr_gain'] = 1
                                target_gain = 0
                            else:
                                target_energy = np.mean(np.square(np.single(augmented_target_audio)))
                                noise_energy = np.mean(np.square(np.single(noise_segment)))
                                noise_gain = np.sqrt(target_energy / noise_energy) / 10 ** (
                                        target_augmentation['snr'] / 20)

                                # Check for noise_gain > 1 to avoid clipping
                                if noise_gain > 1:
                                    mixture_record['target_snr_gain'] = 1 / noise_gain
                                    mixture_record['noise_snr_gain'] = 1
                                    target_gain = target_gain / noise_gain
                                else:
                                    mixture_record['target_snr_gain'] = 1
                                    mixture_record['noise_snr_gain'] = noise_gain

                        truth_config = deepcopy(target['truth_config'])
                        truth_config['index'] = target['truth_index']
                        truth_config['frame_size'] = config['frame_size']
                        truth_config['num_classes'] = config['num_classes']
                        truth_config['mutex'] = truth_mutex

                        # Check for clipping in mixture
                        mixture_audio = np.single(augmented_target_audio) * mixture_record['target_snr_gain'] + \
                                        np.single(noise_segment) * mixture_record['noise_snr_gain']

                        if any(abs(mixture_audio) >= 32768):
                            # Clipping occurred; lower gains to bring audio within int16 bounds
                            gain_adjustment = 32760 / max(abs(mixture_audio))
                            mixture_record['target_snr_gain'] *= gain_adjustment
                            mixture_record['noise_snr_gain'] *= gain_adjustment
                            target_gain *= gain_adjustment

                        if target_gain == 0:
                            truth = np.zeros((config['num_classes'], len(augmented_target_audio)), dtype=np.int16)
                        else:
                            augmented_target_audio = np.int16(
                                np.single(augmented_target_audio) * mixture_record['target_snr_gain'])
                            truth = generate_truth(
                                audio=np.int16(np.single(augmented_target_audio) / target_gain),
                                function=target['truth_function'],
                                config=truth_config)

                        total_class_count, mixture_record['class_count'] = update_class_count(
                            total_class_count=total_class_count,
                            truth_index=target['truth_index'],
                            truth=truth,
                            class_weights_threshold=class_weights_threshold)

                        target_len = len(augmented_target_audio)
                        total_samples += target_len

                        mixture_record['samples'] = target_len
                        mixture_record['target_gain'] = target_gain
                        mixtures.append(mixture_record)

                        progress_bar.update()

    mixdb['class_count'] = [int(i) for i in total_class_count]
    mixdb['mixtures'] = mixtures

    logger.info('')
    logger.info(
        'Actual duration: {} (HH:MM:SS)'.format(
            strftime('%H:%M:%S', gmtime(total_samples / sonusai.mixture.sample_rate))))
    logger.info('Actual size:     {} (feature and truth_f)'.format(
        human_readable_size(total_samples * sonusai.mixture.bit_depth / 8)))

    return mixdb


def get_input_files(records, cfg=None, silent=False):
    if cfg is None:
        desc = 'noises'
        cfg = {}
    else:
        desc = 'targets'

    if not silent:
        logger.info('Collecting {}'.format(desc))

    files = []
    for record in records:
        append_input_files(files, record, cfg)
    return files


def append_input_files(files: list, in_record, cfg: dict, tokens=None):
    if tokens is None:
        tokens = {}
    in_name = in_record

    if isinstance(in_record, dict):
        if 'target_name' in in_record.keys():
            in_name = in_record['target_name']
        else:
            logger.error('Target list contained record without \'target_name\' key')
            exit()

        if 'truth_index' in in_record.keys():
            cfg['truth_index'] = in_record['truth_index']

        if 'truth_function' in in_record.keys():
            cfg['truth_function'] = in_record['truth_function']

        if 'truth_config' in in_record.keys():
            cfg['truth_config'] = in_record['truth_config']

    (in_name, new_tokens) = expandvars(in_name)
    tokens.update(new_tokens)
    names = glob(in_name)
    if not names:
        logger.warning('Could not find {}. Make sure path exists'.format(in_name))
    for name in names:
        ext = splitext(name)[1].lower()
        dir_name = dirname(name)
        if isdir(name):
            for file in listdir(name):
                child = file
                if not isabs(child):
                    child = join(dir_name, child)
                append_input_files(files, child, cfg, tokens)
        else:
            try:
                if ext == '.txt':
                    with open(name, mode='r') as txt_file:
                        for line in txt_file:
                            # strip comments
                            child = line.partition('#')[0]
                            child = child.rstrip()
                            if child:
                                (child, new_tokens) = expandvars(child)
                                tokens.update(new_tokens)
                                if not isabs(child):
                                    child = join(dir_name, child)
                                append_input_files(files, child, cfg, tokens)
                elif ext == '.yml':
                    try:
                        with open(name, mode='r') as yml_file:
                            yml_config = yaml.safe_load(yml_file)

                        if 'targets' in yml_config:
                            for record in yml_config['targets']:
                                append_input_files(files, record, cfg, tokens)
                    except Exception as e:
                        logger.error('Error processing {}: {}'.format(name, e))
                        exit()
                else:
                    sox.file_info.validate_input_file(name)
                    duration = sox.file_info.duration(name)
                    original_name = name
                    for key, value in tokens.items():
                        original_name = original_name.replace(value, '${}'.format(key))
                    entry = {'name': name, 'duration': duration, 'original_name': original_name}
                    entry.update(cfg)
                    files.append(entry)
            except Exception as e:
                logger.error('Error processing {}: {}'.format(name, e))
                exit()


def get_augmentations(rules: list, target: bool) -> list:
    if target:
        desc = 'target augmentations'
    else:
        desc = 'noise augmentations'
    logger.info('Collecting {}'.format(desc))
    augmentations = []
    for rule in rules:
        expand_augmentations(augmentations, rule, target)

    augmentations = rand_augmentations(augmentations)
    return augmentations


def expand_augmentations(augmentations: list, rule: dict, target: bool):
    # replace old 'eq' rule with new 'eq1' rule to allow both for backward compatibility
    rule = {'eq1' if key == 'eq' else key: value for key, value in rule.items()}

    for key in rule:
        if key not in sonusai.mixture.valid_augmentations:
            logger.error('Invalid augmentation: {}'.format(key))
            exit()

        if key in ['eq1', 'eq2', 'eq3']:
            # eq must be a list of length 3 or a list of length 3 lists
            valid = True
            multiple = False
            if isinstance(rule[key], list):
                if any(isinstance(el, list) for el in rule[key]):
                    multiple = True
                    for value in rule[key]:
                        if not isinstance(value, list) or len(value) != 3:
                            valid = False
                else:
                    if len(rule[key]) != 3:
                        valid = False
            else:
                valid = False

            if not valid:
                logger.error('Invalid augmentation value for {}: {}'.format(key, rule[key]))
                exit()

            if multiple:
                for value in rule[key]:
                    expanded_rule = deepcopy(rule)
                    expanded_rule[key] = deepcopy(value)
                    expand_augmentations(augmentations, expanded_rule, target)
                return

        elif key == 'count':
            pass

        else:
            if isinstance(rule[key], list):
                for value in rule[key]:
                    if isinstance(value, list):
                        logger.error('Invalid augmentation value for {}: {}'.format(key, rule[key]))
                        exit()
                    expanded_rule = deepcopy(rule)
                    expanded_rule[key] = deepcopy(value)
                    expand_augmentations(augmentations, expanded_rule, target)
                return
            elif not isinstance(rule[key], Number):
                if not rule[key].startswith('rand'):
                    logger.error('Invalid augmentation value for {}: {}'.format(key, rule[key]))
                    exit()

    # Set default snr for target if needed
    if target and 'snr' not in rule:
        rule['snr'] = sonusai.mixture.default_snr

    # Remove snr rule from noise if needed
    if not target and 'snr' in rule:
        del rule['snr']

    augmentations.append(rule)


def rand_repl(m):
    return '{:.2f}'.format(uniform(float(m.group(1)), float(m.group(4))))


def rand_augmentations(in_rules):
    out_rules = []
    for rule in in_rules:
        # do any keys contain rand?
        has_rand = False
        for key in rule:
            if 'rand' in str(rule[key]):
                has_rand = True
                break

        if has_rand:
            count = 1
            if rule['count'] is not None:
                count = rule['count']
                del rule['count']
            for i in range(count):
                new_rule = deepcopy(rule)
                for key in new_rule:
                    new_rule[key] = eval(re.sub(sonusai.mixture.rand_pattern, rand_repl, str(new_rule[key])))

                    # convert eq values from strings to numbers
                    if key in ['eq1', 'eq2', 'eq3']:
                        for n in range(3):
                            if isinstance(new_rule[key][n], str):
                                new_rule[key][n] = eval(new_rule[key][n])
                out_rules.append(new_rule)
        else:
            out_rules.append(rule)
    return out_rules


def get_base_name(config: dict, config_name: str) -> str:
    try:
        config_base = splitext(config_name)[0]
        name = str(splitext(config['output'])[0])
        name = name.replace('${config}', config_base)
        return name
    except Exception as e:
        logger.error('Error getting genmixdb base name: {}'.format(e))
        exit()


def main():
    try:
        args = docopt(trim_docstring(__doc__), version=sonusai.version(), options_first=True)

        verbose = args['--verbose']

        for config_file in args['CONFIG']:
            logger.info('Creating mixture database for {}'.format(config_file))
            config = get_config_from_file(config_file)

            base_name = get_base_name(config, config_file)
            output_name = base_name + '.json'

            log_name = base_name + '.log'
            create_file_handler(log_name)
            update_console_handler(verbose)
            initial_log_messages('genmixdb')

            mixdb = genmixdb(config=config, show_progress=True)

            with open(output_name, mode='w') as file:
                json.dump(mixdb, file, indent=2)
                logger.info('Wrote mixture database for {} to {}'.format(config_file, output_name))

    except KeyboardInterrupt:
        logger.info('Canceled due to keyboard interrupt')
        exit()


if __name__ == '__main__':
    main()
