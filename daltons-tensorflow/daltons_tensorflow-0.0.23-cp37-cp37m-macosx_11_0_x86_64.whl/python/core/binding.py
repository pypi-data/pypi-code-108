import ctypes

import tensorflow as tf
from tensorflow.python.platform import resource_loader

_daltons_core_path = resource_loader.get_path_to_datafile('_daltons_core.so')
ops = tf.load_op_library(_daltons_core_path)
lib = ctypes.cdll.LoadLibrary(_daltons_core_path)
