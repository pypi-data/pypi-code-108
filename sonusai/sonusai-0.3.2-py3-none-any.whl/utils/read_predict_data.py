import h5py
import numpy as np

from sonusai import logger


def read_predict_data(filename: str, expected_frames: int) -> (None, np.ndarray):
    if not filename:
        return None

    logger.info('Reading prediction data from {}'.format(filename))
    with h5py.File(name=filename, mode='r') as f:
        # prediction data is either [frames, num_classes], or [frames, timesteps, num_classes]
        predict = np.array(f['predict'])

        if predict.ndim == 2:
            frames, num_classes = predict.shape

            if frames != expected_frames:
                logger.warning('Ignoring prediction data in {} due to frames mismatch'.format(filename))
                return None
        elif predict.ndim == 3:
            frames, timesteps, num_classes = predict.shape

            if frames * timesteps != expected_frames:
                logger.warning('Ignoring prediction data in {} due to frames mismatch'.format(filename))
                return None

            logger.info('Reshaping prediction data in {} from [{}, {}, {}] to [{}, {}]'.
                        format(filename, frames, timesteps, num_classes, frames * timesteps, num_classes))
            predict = np.reshape(predict, [frames * timesteps, num_classes], order='F')
        else:
            logger.warning('Ignoring prediction data in {} due to invalid dimensions'.format(filename))
            return None

        return predict
