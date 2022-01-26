'''
Dataset loading utilities, mainly relying on the `tensorflow_datasets <https://www.tensorflow.org/datasets/api_docs/python/tfds>`_ module.

Datasets:

- MNIST

'''


import tensorflow as tf
import tensorflow_datasets as tfds

def load_mnist(batch_size=50):
    """Load the MNIST train and test dataset

    :param batch_size: minibatch size, defaults to 50
    :type batch_size: int, optional
    :return: mnist dataset
    :rtype: tf.Dataset
    """
    
    def preprocess(image, label): 
        return (tf.reshape(tf.cast(image, tf.float32), [784, 1]) / 255.,
                tf.cast(tf.expand_dims(tf.one_hot(label, 10), -1), tf.float32))
        
    ds = tfds.load('mnist', split='train', as_supervised=True)
    ds = ds.map(preprocess, num_parallel_calls=tf.data.AUTOTUNE)
    ds = ds.cache()
    ds = ds.batch(batch_size)
    ds = ds.prefetch(tf.data.experimental.AUTOTUNE)
    tds = tfds.load('mnist', split='test', as_supervised=True)
    tds = tds.map(preprocess, num_parallel_calls=tf.data.AUTOTUNE)
    tds = tds.cache()
    tds = tds.batch(10000)
    tds = tds.prefetch(tf.data.experimental.AUTOTUNE)
    
    return ds, tds


    
