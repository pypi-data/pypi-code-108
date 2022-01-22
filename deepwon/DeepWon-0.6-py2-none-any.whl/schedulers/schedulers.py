__env__ = '''Envs]
    Python 3.9.7 64-bit(conda 4.11.0)
    macOS 12.1
'''
__version__ = '''Version]
    version 0.01(beta)
'''
__doc__ = '''\
This module contains various schedulers for optimizing.
''' + __env__+__version__

import tensorflow as tf
from tensorflow import keras
import numpy as np

# warm-up cosine
class WarmUpCosine(keras.optimizers.schedules.LearningRateSchedule):
    def __init__(
        self, learning_rate_base, total_steps, warmup_learning_rate, warmup_steps
    ):
        '''
            Learning rate linearly increases from 'learning_rate_base' to 'warm_up_learning_rate',
            and then decreases.

            learning_rate_base: base learning rate
            total_steps: total steps for optimizer to work on.
            warm_up_learning_rate: maximum learning rate
            warm_up_steps: warm up steps

        '''
        super(WarmUpCosine, self).__init__()

        self.learning_rate_base = learning_rate_base
        self.total_steps = total_steps
        self.warmup_learning_rate = warmup_learning_rate
        self.warmup_steps = warmup_steps
        self.pi = tf.constant(np.pi)

    def __call__(self, step):
        if self.total_steps < self.warmup_steps:
            raise ValueError("Total_steps must be larger or equal to warmup_steps.")

        cos_annealed_lr = tf.cos(
            self.pi
            * (tf.cast(step, tf.float32) - self.warmup_steps)
            / float(self.total_steps - self.warmup_steps)
        )
        learning_rate = 0.5 * self.learning_rate_base * (1 + cos_annealed_lr)

        if self.warmup_steps > 0:
            if self.learning_rate_base < self.warmup_learning_rate:
                raise ValueError(
                    "Learning_rate_base must be larger or equal to "
                    "warmup_learning_rate."
                )
            slope = (
                self.learning_rate_base - self.warmup_learning_rate
            ) / self.warmup_steps
            warmup_rate = slope * tf.cast(step, tf.float32) + self.warmup_learning_rate
            learning_rate = tf.where(
                step < self.warmup_steps, warmup_rate, learning_rate
            )
        return tf.where(
            step > self.total_steps, 0.0, learning_rate, name="learning_rate"
        )
    
    def get_config(self):
        config = {
          'learning_rate_base': self.learning_rate_base,
          'total_steps': self.total_steps,
          'warmup_learning_rate':self.warmup_learning_rate,
          'warmup_steps': self.warmup_steps,
        
        }
        return config

