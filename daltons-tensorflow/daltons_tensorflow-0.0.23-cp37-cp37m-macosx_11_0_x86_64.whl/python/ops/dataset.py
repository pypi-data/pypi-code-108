
"""Daltons Dataset."""

import tensorflow as tf
from tensorflow import dtypes
from tensorflow.compat.v1 import data

import daltons_tensorflow.python.core.binding as binding

class DaltonsDataset(data.Dataset):
    """A Daltons Dataset that consumes messages from a daltons dataset source
    """

    def __init__(self,
            url,
            action_id_field="action_id",
            reward_field="reward",
            probability_field="probability",
            descending_reward=False,
            preload=1):

        self._url = tf.convert_to_tensor(
            url, dtype=dtypes.string, name="url")

        self._action_id_field = tf.convert_to_tensor(
            action_id_field, dtype=dtypes.string, name="action_id")

        self._reward_field = tf.convert_to_tensor(
            reward_field, dtype=dtypes.string, name="reward_field")
        
        self._probability_field = tf.convert_to_tensor(
            probability_field, dtype=dtypes.string, name="probability_field")
        
        self._descending_reward = tf.convert_to_tensor(
            descending_reward, dtype=dtypes.bool, name="descending_reward")

        self._preload = tf.convert_to_tensor(
            preload, dtype=dtypes.int64, name="preload")

        super().__init__()

    def _inputs(self):
        return []

    def _as_variant_tensor(self):
        return binding.ops.daltons_dataset(self._url, 
                                           self._action_id_field, 
                                           self._reward_field, 
                                           self._probability_field, 
                                           self._descending_reward, 
                                           self._preload)

    @property
    def output_classes(self):
        return tf.Tensor

    @property
    def output_shapes(self):
        return tf.TensorShape([])

    @property
    def output_types(self):
        return dtypes.string

class DaltonsTrainerDataset(data.Dataset):
    """A Daltons Trainer Dataset that consumes daltons examples directly from a trainer process
    """

    def __init__(self,
            url,
            listen=False,
            max_retries=100,
            retry_timeout=5000,
            eos_on_close=True):

        self._url = tf.convert_to_tensor(
            url, dtype=dtypes.string, name="url")

        self._listen = tf.convert_to_tensor(
            listen, dtype=dtypes.bool, name="listen")

        self._max_retries = tf.convert_to_tensor(
            max_retries, dtype=dtypes.int64, name="max_retries")

        self._eos_on_close = tf.convert_to_tensor(
            eos_on_close, dtype=dtypes.bool, name="eos_on_close")

        self._retry_timeout = tf.convert_to_tensor(
            retry_timeout, dtype=dtypes.int64, name="retry_timeout")

        super().__init__()

    def _inputs(self):
        return []

    def _as_variant_tensor(self):
        return binding.ops.daltons_trainer_dataset(
            self._url, 
            self._listen, 
            self._max_retries, 
            self._eos_on_close, 
            self._retry_timeout)

    @property
    def output_classes(self):
        return tf.Tensor

    @property
    def output_shapes(self):
        return tf.TensorShape([])

    @property
    def output_types(self):
        return dtypes.string
