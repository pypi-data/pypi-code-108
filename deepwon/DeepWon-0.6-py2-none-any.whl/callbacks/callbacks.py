__env__ = '''Envs]
    Python 3.9.7 64-bit(conda 4.11.0)
    macOS 12.1
'''
__version__ = '''Version]
    version 0.01(beta)
'''
__doc__ = '''\
This module contains various keras callbacks.
'''+ __env__+__version__

import tensorflow as tf
from tensorflow import keras
import numpy as np
import matplotlib.pyplot as plt

class CheckReconstrunction(keras.callbacks.Callback):
    def __init__(self, image, patch_size):
        super().__init__() 
        self.image = image
        self.img_shape = image.shape
        self.patch_size = patch_size

    def on_epoch_end(self, epoch, logs={}):
        # Reconstruct the image
        img = self.model.predict(self.image)
       
        patches = [np.reshape(arr, (-1, self.patch_size, self.patch_size, 3)) \
                  for arr in np.split(img, img.shape[1], axis=1)]

        # n_row, n_col should be interger
        n_row = self.img_shape[1] // self.patch_size
        n_col = self.img_shape[2] // self.patch_size
        
        rows = []
        for row in range(n_row):
            cols = []
            for col in range(n_col):
                cols.append(patches[row*n_col + col])
            col_t = np.concatenate(cols, axis=2)  
            rows.append(col_t)
        img = np.concatenate(rows, axis=1).reshape(self.img_shape[1], self.img_shape[2], 3)

        image = self.image.reshape(self.image.shape[1], self.image.shape[2], 3)
        fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(10, 5))
        ax[0].imshow(image)
        ax[0].set_title(f"Original: {epoch:03d}")

        ax[1].imshow((img*255).astype(np.uint8))
        ax[1].set_title(f"Resonstructed: {epoch:03d}")

        plt.show()
        plt.close()
    
    def get_config(self):
        config = {
          'image':self.image,
          'patch_size': self.patch_size,
        }
        return config

class ReconstructImage(keras.callbacks.Callback):
    def __init__(self, img_tag, log_dir, image, patch_size):
        super().__init__() 
        self.tag = img_tag
        self.image = image
        self.log_dir = log_dir
        self.img_shape = image.shape
        self.patch_size = patch_size

    def on_epoch_begin(self, epoch, logs={}):
        # Reconstruct the image
        img = self.model.predict(self.image)
       
        patches = [np.reshape(arr, (-1, self.patch_size, self.patch_size, 3)) \
                  for arr in np.split(img, img.shape[1], axis=1)]

        # n_row, n_col should be interger
        n_row = self.img_shape[1] // self.patch_size
        n_col = self.img_shape[2] // self.patch_size
        
        rows = []
        for row in range(n_row):
            cols = []
            for col in range(n_col):
                cols.append(patches[row*n_col + col])
            col_t = np.concatenate(cols, axis=2)  
            rows.append(col_t)
        img = np.concatenate(rows, axis=1)

        writer = tf.summary.create_file_writer(self.log_dir)
        with writer.as_default():
          tf.summary.image("reconstructed", img, step=epoch)

        return
    
    def get_config(self):
        config = {
          'img_tag': self.tag,
          'log_dir': self.log_dir,
          'image':self.image,
          'patch_size': self.patch_size,
        }
        return config