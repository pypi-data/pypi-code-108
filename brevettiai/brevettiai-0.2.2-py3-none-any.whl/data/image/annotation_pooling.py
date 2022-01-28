import tensorflow as tf

import brevettiai.interfaces.vue_schema_utils as vue


class AnnotationPooling(vue.VueSettingsModule):
    """Vue enabled module for average pooling"""
    def __init__(self, pooling_method: str = "max",
                 input_key: str = "segmentation",
                 output_key: str = None,
                 pool_size=None):
        self.pooling_method = pooling_method
        self.input_key = input_key
        self.output_key = output_key or input_key
        self.pool_size = pool_size

        self.pooling_algorithms = {"max": tf.keras.layers.MaxPool2D,
                                   "avg": tf.keras.layers.AveragePooling2D,
                                   "average": tf.keras.layers.AveragePooling2D}

    def __call__(self, x, *args, **kwargs):
        inp = x[self.input_key]
        x[self.output_key] = self.pooling_algorithms[self.pooling_method](
            pool_size=self.pool_size)(inp)
        return x
