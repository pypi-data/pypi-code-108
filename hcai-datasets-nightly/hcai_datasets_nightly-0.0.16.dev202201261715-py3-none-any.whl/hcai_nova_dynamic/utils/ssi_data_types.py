from enum import Enum
import numpy as np
import tensorflow as tf

class FileTypes(Enum):
        UNDEF = 0
        BINARY = 1
        ASCII = 2
        BIN_LZ4 = 3

class NPDataTypes(Enum):
    UNDEF = 0
    #CHAR = 1
    #UCHAR = 2
    SHORT = np.int16
    USHORT = np.uint16
    INT = np.int32
    UINT = np.uint32
    LONG = np.int64
    ULONG = np.uint64
    FLOAT = np.float32
    DOUBLE = np.float64
    LDOUBLE = np.float64
    #STRUCT = 12
    #IMAGE = 13
    BOOL = np.bool_

class TFDataTypes(Enum):
  UNDEF = 0
  SHORT = tf.int16
  USHORT = tf.uint16
  INT = tf.int32
  UINT = tf.uint32
  LONG = tf.int64
  ULONG = tf.uint64
  FLOAT = tf.float32
  DOUBLE = tf.float64
  LDOUBLE = tf.float64
  BOOL = tf.bool

'''Helper'''
def string_to_enum(enum, string):
    for e in enum:
        if e.name == string:
            return e
    raise ValueError('{} not part of enumeration  {}'.format(string, enum))
