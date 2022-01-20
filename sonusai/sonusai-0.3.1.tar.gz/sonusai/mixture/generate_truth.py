import numpy as np
from pyaaware import ForwardTransform
from pyaaware import SED

from sonusai import logger


def strictly_decreasing(list_to_check: list) -> bool:
    return all(x > y for x, y in zip(list_to_check, list_to_check[1:]))


def generate_truth(audio: np.ndarray, function: str, config: dict) -> np.ndarray:
    required_parameters = ['index', 'frame_size', 'num_classes', 'mutex']
    for parameter in required_parameters:
        if parameter not in config.keys():
            logger.error('Truth function config missing required parameter: {}'.format(parameter))
            exit()

    index = config['index']
    frame_size = config['frame_size']
    num_classes = config['num_classes']
    mutex = config['mutex']

    if function == 'sed':
        if len(audio) % frame_size != 0:
            logger.error('Number of samples in audio is not a multiple of {}'.format(frame_size))
            exit()

        if 'thresholds' in config.keys():
            thresholds = config['thresholds']
            if not isinstance(thresholds, list) or len(thresholds) != 3:
                logger.error('Truth function SED thresholds does not contain 3 entries: {}'.format(thresholds))
                exit()
            if not strictly_decreasing(thresholds):
                logger.error('Truth function SED thresholds are not strictly decreasing: {}'.format(thresholds))
                exit()
        else:
            thresholds = None

        fft = ForwardTransform(N=frame_size * 4, R=frame_size)
        sed = SED(thresholds=thresholds,
                  index=index,
                  frame_size=frame_size,
                  num_classes=num_classes,
                  mutex=mutex)

        truth = np.empty((num_classes, 0), dtype=np.single)
        for offset in range(0, len(audio), frame_size):
            new_truth = sed.execute(fft.energy((audio[offset:offset + frame_size]).astype(np.single) / 32768))
            truth = np.hstack((truth, np.reshape(new_truth, (len(new_truth), 1))))

        # This repeats each sample and not the whole sequence
        truth = truth.repeat(frame_size, axis=1)
        return truth

    logger.error('Unsupported truth function: {}'.format(function))
    exit()
