import numpy as np

from sonusai import logger
from sonusai.mixture import apply_augmentation
from sonusai.mixture import read_audio


def build_noise_audio_db(mixdb: dict) -> list:
    db = []
    for file_index in sorted(list(set([sub['noise_file_index'] for sub in mixdb['mixtures']]))):
        audio_in = read_audio(name=mixdb['noises'][file_index]['name'], dither=mixdb['dither'])
        for augmentation_index in sorted(list(set([sub['noise_augmentation_index'] for sub in mixdb['mixtures']]))):
            db.append({
                'file':         file_index,
                'augmentation': augmentation_index,
                'audio':        apply_augmentation(audio_in=audio_in,
                                                   augmentation=mixdb['noise_augmentations'][augmentation_index],
                                                   length_common_denominator=1,
                                                   dither=mixdb['dither'])
            })
    return db


def get_noise_audio_from_db(db: list, file_index: int, augmentation_index: int) -> np.ndarray:
    for record in db:
        if record['file'] == file_index and record['augmentation'] == augmentation_index:
            return record['audio']

    logger.error(
        'Could not find noise_file_index {} and noise_augmentation_index {} in noise database'.format(file_index,
                                                                                                      augmentation_index))
    exit()


def build_target_audio_db(mixdb: dict) -> list:
    db = []
    for file_index in sorted(list(set([sub['target_file_index'] for sub in mixdb['mixtures']]))):
        db.append({
            'file':  file_index,
            'audio': read_audio(name=mixdb['targets'][file_index]['name'], dither=mixdb['dither'])
        })
    return db


def get_target_audio_from_db(db: list, file_index: int) -> np.ndarray:
    for record in db:
        if record['file'] == file_index:
            return record['audio']

    logger.error('Could not find target_file_index {} in target database'.format(file_index))
    exit()
