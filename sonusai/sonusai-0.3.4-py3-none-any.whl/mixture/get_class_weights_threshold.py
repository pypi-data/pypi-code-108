import numpy as np

from sonusai import logger


def get_class_weights_threshold(mixdb: dict) -> list:
    class_weights_threshold = mixdb['class_weights_threshold']
    if not isinstance(class_weights_threshold, list):
        class_weights_threshold = np.repeat(class_weights_threshold, mixdb['num_classes'])
    if len(class_weights_threshold) != mixdb['num_classes']:
        logger.error('invalid class_weights_threshold length: {}'.format(len(class_weights_threshold)))
        exit()
    return class_weights_threshold
