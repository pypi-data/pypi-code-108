import copy
import os
import re
from typing import Dict
from typing import List

import numpy as np


__all__ = [
    'get_tpu_devices',
    'STR_TO_DTYPE',
    'to_raw',
]


def get_tpu_devices() -> List[str]:
    return [os.path.join('/dev', f) for f in os.listdir('/dev') if re.match(r'tpu.', f) and len(f) == 4]


def to_raw(metadata: Dict) -> Dict:
    raw_metadata = copy.copy(metadata)
    for idx, region in raw_metadata['inputs'].items():
        for name, _ in region.items():
            raw_metadata['inputs'][idx][name]['user_shape'] = raw_metadata['inputs'][idx][name]['tpu_shape']
            raw_metadata['inputs'][idx][name]['user_order'] = raw_metadata['inputs'][idx][name]['tpu_order']
            raw_metadata['inputs'][idx][name]['user_dtype'] = raw_metadata['inputs'][idx][name]['tpu_dtype']
            raw_metadata['inputs'][idx][name]['scales'] = [1.0, ]
            raw_metadata['inputs'][idx][name]['padding'] = \
                [[0, 0], ] * len(raw_metadata['inputs'][idx][name]['tpu_shape'])

    for idx, region in raw_metadata['outputs'].items():
        for name, _ in region.items():
            raw_metadata['outputs'][idx][name]['user_shape'] = raw_metadata['outputs'][idx][name]['tpu_shape']
            raw_metadata['outputs'][idx][name]['user_order'] = raw_metadata['outputs'][idx][name]['tpu_order']
            raw_metadata['outputs'][idx][name]['user_dtype'] = raw_metadata['outputs'][idx][name]['tpu_dtype']
            raw_metadata['outputs'][idx][name]['scales'] = [1.0, ]
            raw_metadata['outputs'][idx][name]['padding'] = \
                [[0, 0], ] * len(raw_metadata['outputs'][idx][name]['tpu_shape'])

    return raw_metadata


STR_TO_DTYPE = {
    'int8': np.int8,
    'float16': np.float16,
    'float32': np.float32,
}
