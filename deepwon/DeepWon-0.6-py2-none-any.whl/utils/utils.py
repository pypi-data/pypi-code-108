__env__ = '''Envs]
    Python 3.9.7 64-bit(conda 4.11.0)
    macOS 12.1
'''
__version__ = '''Version]
    version 0.01(beta)
'''
__doc__ = '''\
This module contains various utilities.
'''+ __env__+__version__
import tensorflow as tf


# print tabular data
def print_table(col_names, *cols, tab_width=50, just='right'):
    '''Make and print a table that consists of multiple columns.
    
    The length of 'col_names' should be the same as of 'cols'.

    Params]
        col_names: A list of column names
        cols: Vector like 1D variables, each of which will be a column of the table sequentially
        tab_width (optional): An width of a table. default = 50
        just (optional): Justification option. 'center' and 'right' are acceptible. default = 'right'
    '''
    # Assume that len(col_names) == len(cols) holds.
    if len(col_names) != len(cols):
        raise ValueError('Length of col_names and cols should be same')
    # Column names
    print("="*tab_width)
    cols_str = ''.join([str(name).center(int((tab_width//len(col_names))*0.95)) 
                        for name in col_names])
    print(cols_str)
    print('-'*tab_width)
    
    # get the maximum length of contents, respect to each column
    max_data_len = []
    for col in cols:
        max_len = 0
        for i in range(len(col)):
            if max_len < len(str(col[i])):
                max_len = len(str(col[i]))
        max_data_len.append(max_len)

    # print data row by row, propotionally indented to the length of each column
    for row in range(len(cols[0])):
        # right justification
        if just =='right':
            row_str = ''.join([str(data[row]).rjust(max_data_len[i]).center(tab_width // len(cols))
                          for i, data in enumerate(cols)])
        # center justification
        elif just =='center':
            row_str = ''.join([str(data[row]).center(max_data_len[i]).center(tab_width // len(cols))
                          for i, data in enumerate(cols)])
        print(row_str)
    
    print('='*tab_width)

# decode image file from path and resize
def decode_img(img, IMG_HEIGHT, IMG_WIDTH):
  img = tf.image.decode_jpeg(img, channels=3)
  img = tf.image.resize(img, [IMG_HEIGHT, IMG_WIDTH])
  img = tf.cast(img, tf.float32)
  
  return img


def config_for_performance(ds, batchsize=512, cache=True):
  if cache:
    if isinstance(cache, str):
        ds = ds.cache(cache)
    else:
        ds = ds.cache()
  
  AUTOTUNE = tf.data.experimental.AUTOTUNE
  ds = ds.shuffle(buffer_size=1000)
  ds = ds.repeat()
  ds = ds.batch(batchsize)
  ds = ds.prefetch(buffer_size=AUTOTUNE)
  return ds


def train_test_split_ds(ds, ratio=0.2):
  val_size = int(len(ds) * ratio)
  train_ds = ds.skip(val_size)
  val_ds = ds.take(val_size)

  return train_ds, val_ds



# Get model size
# https://stackoverflow.com/questions/43137288/how-to-determine-needed-memory-of-keras-model
def get_model_memory_usage(batch_size, model):
    import numpy as np
    try:
        from keras import backend as K
    except:
        from tensorflow.keras import backend as K

    shapes_mem_count = 0
    internal_model_mem_count = 0
    for l in model.layers:
        layer_type = l.__class__.__name__
        if layer_type == 'Model':
            internal_model_mem_count += get_model_memory_usage(batch_size, l)
        single_layer_mem = 1
        out_shape = l.output_shape
        if type(out_shape) is list:
            out_shape = out_shape[0]
        for s in out_shape:
            if s is None:
                continue
            single_layer_mem *= s
        shapes_mem_count += single_layer_mem

    trainable_count = np.sum([K.count_params(p) for p in model.trainable_weights])
    non_trainable_count = np.sum([K.count_params(p) for p in model.non_trainable_weights])

    number_size = 4.0
    if K.floatx() == 'float16':
        number_size = 2.0
    if K.floatx() == 'float64':
        number_size = 8.0

    total_memory = number_size * (batch_size * shapes_mem_count + trainable_count + non_trainable_count)
    gbytes = np.round(total_memory / (1024.0 ** 3), 3) + internal_model_mem_count
    return gbytes