# SonusAI mixture utilities

import os
import re

import sonusai

valid_augmentations = ['normalize', 'gain', 'pitch', 'tempo', 'eq1', 'eq2', 'eq3', 'lpf', 'snr', 'count']
rand_pattern = re.compile(r'rand\(([-+]?([0-9]+(\.[0-9]*)?|\.[0-9]+)),\s*([-+]?([0-9]+(\.[0-9]*)?|\.[0-9]+))\)')
sample_rate = 16000
bit_depth = 16
channel_count = 1
sample_bytes = int(bit_depth / 8)
float_bytes = 4
excessive_size = 6 * 1024 * 1024 * 1024

default_noise = os.path.join(sonusai.basedir, 'data', 'whitenoise.wav')
default_config = os.path.join(sonusai.basedir, 'data', 'genmixdb.yml')
default_snr = 80

from sonusai.mixture.apply_augmentation import apply_augmentation  # noqa: E402
from sonusai.mixture.apply_augmentation import read_audio  # noqa: E402
from sonusai.mixture.audio_db import build_noise_audio_db  # noqa: E402
from sonusai.mixture.audio_db import build_target_audio_db  # noqa: E402
from sonusai.mixture.audio_db import get_noise_audio_from_db  # noqa: E402
from sonusai.mixture.audio_db import get_target_audio_from_db  # noqa: E402
from sonusai.mixture.generate_truth import generate_truth  # noqa: E402
from sonusai.mixture.get_class_weights_threshold import get_class_weights_threshold  # noqa: E402
from sonusai.mixture.get_config_from_file import get_config_from_file  # noqa: E402
from sonusai.mixture.get_next_noise import get_next_noise  # noqa: E402
from sonusai.mixture.get_offsets import get_offsets  # noqa: E402
from sonusai.mixture.update_class_count import update_class_count  # noqa: E402
