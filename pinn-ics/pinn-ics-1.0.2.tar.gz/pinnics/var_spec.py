import tensorflow as tf
from tensorflow.random import uniform, normal


class VarSpec:
    """
        Variable object, which will pass into model

        Parameter
        ---------
            character: str 
                The indicated character of the variable 

            limit: tuple
                The range of variable
    """
    def __init__(self, character='x', limit=(0, 1)):
        self._character = character
        self._limit = limit

    @property
    def character(self):
        return self._character

    def random_uniform(self, num):
        min_val, max_val = self._limit
        return uniform([num, 1], minval=min_val, maxval=max_val)

    def random_normal(self, num, **kwargs):
        min_val, max_val = self._limit
        data = normal([num, 1], **kwargs)
        data = tf.where(data > max_val, max_val, data)
        data = tf.where(data < min_val, min_val, data)
        return data

    def initial_float(self, num, value):
        data = tf.ones([num, 1], dtype=tf.float32)
        data = tf.multiply(data, tf.constant(value, dtype=tf.float32))
        return data

    def random(self, num, random_type='uniform', **kwargs):
        """
            Random data with special features.
            
            Parameter
            ---------
                num: int
                    The number of data 
                
                random_type: "uniform", "normal" or float 
                    The type of data that be randomed by this function,
                        if you choose float -> generate all float value.
        """
        if random_type == "uniform":
            return self.random_uniform(num)
        elif random_type == "normal":
            return self.random_normal(num, **kwargs)
        elif isinstance(random_type, float):
            return self.initial_float(num, random_type)
        else:
            raise ValueError(f"random_type must be uniform or normal.")
