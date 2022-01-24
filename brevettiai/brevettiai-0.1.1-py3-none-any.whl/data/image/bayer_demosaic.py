import tensorflow as tf
from tensorflow.keras.layers import Conv2D
import numpy as np


def get_kernels():
    kern = np.zeros((4, 4, 3), dtype=np.float)
    for ii in range(0, 3, 2):
        for jj in range(0, 3, 2):
            kern[ii, jj, 0] = .25

        kern[ii, 1, 1] = .25
        kern[1, ii, 1] = .25

    kern[1, 1, 2] = 1.0
    return {"bgr": kern[:, :, ::-1],
            "rgb": kern}


kernels = get_kernels()


def bayer_demosaic_layer(mode="rgb"):
    kernel = kernels[mode.lower()]
    return Conv2D(3, kernel.shape[:2],
                  use_bias=False,
                  strides=2,
                  weights=[kernel[:,:,None,:]],
                  trainable=False,
                  padding='same')


def tf_bayer_demosaic(x, mode="rgb"):
    return tf.nn.conv2d(x, kernels[mode][:, :, None, :], strides=[1, 2, 2, 1], padding='SAME', name="bayer_demosaic")