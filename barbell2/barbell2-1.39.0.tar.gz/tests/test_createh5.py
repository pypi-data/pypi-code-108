import os
import pytest

from barbell2.createh5 import CreateH5

base_dir = '{}/data/surfdrive/projects/20210203_autosegl3'.format(os.environ['HOME'])


def clean_up():
    if os.path.isfile('train.h5'):
        os.remove('train.h5')
    if os.path.isfile('test.h5'):
        os.remove('test.h5')
    if os.path.isfile('predict.h5'):
        os.remove('predict.h5')


# def test_train_test():
#     """ Both DICOM and TAG files should be collected and the data split up in a training and test set. """
#     clean_up()
#     d = os.path.join(base_dir, 'dicom_and_tag')
#     args = {
#         'data_dir': d,
#         'rows': 512, 'columns': 512,
#         'type': 'train',
#         'test_size': 0.2,
#         'log_dir': '.',
#     }
#     x = CreateH5(args)
#     x.execute()
#     assert os.path.isfile('train.h5')
#     assert os.path.isfile('test.h5')
#     clean_up()


def test_train():
    clean_up()
    # d = os.path.join(base_dir, 'dicom_and_tag')
    d = '/Volumes/USB_SECURE1/data/radiomics/projects/deepseg/data/mega/processed'
    args = {
        'data_dir': d,
        'output_dir': os.path.join(os.environ['HOME'], 'Desktop/h5'),
        'rows': 512, 'columns': 512,
        'type': 'train',
        'test_size': 0.0,
        'log_dir': '.',
    }
    x = CreateH5(args)
    x.execute()
    assert os.path.isfile(os.path.join(args['output_dir'], 'train.h5'))
    clean_up()


# def test_predict():
#     clean_up()
#     d = os.path.join(base_dir, 'dicom')
#     args = {
#         'data_dir': d,
#         'rows': 512, 'columns': 512,
#         'type': 'predict',
#         'test_size': 0.0,
#         'log_dir': '.',
#     }
#     x = CreateH5(args)
#     x.execute()
#     assert os.path.isfile('predict.h5')
#     clean_up()
