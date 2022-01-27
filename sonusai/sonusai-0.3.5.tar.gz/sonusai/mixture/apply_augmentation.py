import numpy as np
import sox

from sonusai import logger
from sonusai import mixture


def read_audio(name: str, dither: bool = True) -> np.ndarray:
    try:
        # Read in and convert to desired format
        inp = sox.Transformer()
        inp.set_output_format(rate=mixture.sample_rate, bits=mixture.bit_depth, channels=mixture.channel_count)
        inp.set_globals(dither=dither)
        return inp.build_array(input_filepath=name, sample_rate_in=int(sox.file_info.sample_rate(name)))

    except Exception as e:
        logger.error('Error reading {}: {}'.format(name, e))
        exit()


def apply_augmentation(audio_in: np.ndarray,
                       augmentation: dict,
                       length_common_denominator: int,
                       dither: bool = True) -> np.ndarray:
    try:
        # Apply augmentations
        tfm = sox.Transformer()
        tfm.set_input_format(rate=mixture.sample_rate, bits=mixture.bit_depth, channels=mixture.channel_count)
        tfm.set_output_format(rate=mixture.sample_rate, bits=mixture.bit_depth, channels=mixture.channel_count)
        tfm.set_globals(dither=dither)

        # TODO
        #  Always normalize and remove normalize from list of available augmentations
        #  Normalize to globally set level (should this be a global config parameter,
        #  or hard-coded into the script?)
        if 'normalize' in augmentation:
            tfm.norm(db_level=augmentation['normalize'])

        if 'gain' in augmentation:
            tfm.gain(gain_db=augmentation['gain'], normalize=False, limiter=True)

        if 'pitch' in augmentation:
            tfm.pitch(n_semitones=augmentation['pitch'] / 100)

        if 'tempo' in augmentation:
            factor = augmentation['tempo']
            if abs(factor - 1.0) <= 0.1:
                tfm.stretch(factor=factor)
            else:
                tfm.tempo(factor=factor, audio_type='s')

        if 'eq1' in augmentation:
            tfm.equalizer(frequency=augmentation['eq1'][0], width_q=augmentation['eq1'][1],
                          gain_db=augmentation['eq1'][2])

        if 'eq2' in augmentation:
            tfm.equalizer(frequency=augmentation['eq2'][0], width_q=augmentation['eq2'][1],
                          gain_db=augmentation['eq2'][2])

        if 'eq3' in augmentation:
            tfm.equalizer(frequency=augmentation['eq3'][0], width_q=augmentation['eq3'][1],
                          gain_db=augmentation['eq3'][2])

        if 'lpf' in augmentation:
            tfm.lowpass(frequency=augmentation['lpf'])

        # Create output data
        audio_out = tfm.build_array(input_array=audio_in, sample_rate_in=mixture.sample_rate)

        # make sure length is multiple of length_common_denominator
        audio_len = len(audio_out)
        if audio_len % length_common_denominator:
            pad = length_common_denominator - (audio_len % length_common_denominator)
            audio_out = np.pad(audio_out, pad_width=(0, pad), mode='constant', constant_values=0)

        return audio_out
    except Exception as e:
        logger.error('Error applying {}: {}'.format(augmentation, e))
        exit()
