from sonusai import logger


def get_offsets(mixdb: dict, mixid: int) -> (int, int, int):
    required_keys = [
        'mixtures',
        'frame_size',
        'feature_step_samples',
    ]
    for key in required_keys:
        if key not in mixdb.keys():
            logger.error('Missing {} in mixdb'.format(key))
            exit()

    if mixid >= len(mixdb['mixtures']) or mixid < 0:
        logger.error('Invalid mixid: {}'.format(mixid))
        exit()

    i_sample_offset = sum([sub['samples'] for sub in mixdb['mixtures'][:mixid + 1]])
    i_frame_offset = i_sample_offset // mixdb['frame_size']
    o_frame_offset = i_sample_offset // mixdb['feature_step_samples']

    return i_sample_offset, i_frame_offset, o_frame_offset
