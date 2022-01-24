import numpy as np

from tensorflow.compat.v1.keras import backend as K


def infer_batch_size(model, k=2.338, max_mem=10000 * 1024 * 1024):
    shapes_mem_count = 0
    for l in model.layers:
        single_layer_mem = 1
        for s in l.output_shape:
            if s is None:
                continue
            if isinstance(s, tuple):
                s = s[1]

            single_layer_mem *= s
        shapes_mem_count += single_layer_mem

    trainable_count = np.sum([K.count_params(p) for p in set(model.trainable_weights)])
    non_trainable_count = np.sum([K.count_params(p) for p in set(model.non_trainable_weights)])

    number_size = 4.0
    if K.floatx() == 'float16':
        number_size = 2.0
    if K.floatx() == 'float64':
        number_size = 8.0

    # total_memory_bytes = number_size*(batch_size*shapes_mem_count*k + trainable_count + non_trainable_count)
    # gbytes = np.round(total_memory_bytes / (1024.0 ** 3), 3)
    # mbytes = np.round(total_memory_bytes / (1024.0 ** 2), 3)

    max_batch_size = int((max_mem / number_size - trainable_count - non_trainable_count) / (shapes_mem_count * k))

    return max_batch_size
