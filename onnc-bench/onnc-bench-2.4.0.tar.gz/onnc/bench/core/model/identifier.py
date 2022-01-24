from __future__ import annotations

import os
import zipfile
from enum import Enum
import inspect
from pathlib import Path
from typing import List, Any

# from typing import TYPE_CHECKING

# if TYPE_CHECKING:
#     from . import Model

from . import ModelFormat


def _check_object_type(expect_type_str, obj):
    type_str = ""
    try:
        type_str += str(inspect.getmro((obj)))
    except:
        type_str += ""
    type_str += "|"
    type_str += str(type(obj))
    return expect_type_str in type_str


class IdentifierRegistry(type):

    REGISTRY: List = []

    def __new__(cls, name, bases, attrs):
        new_cls = type.__new__(cls, name, bases, attrs)
        cls.REGISTRY.append(new_cls)
        return new_cls


class Identifier(metaclass=IdentifierRegistry):

    FORMAT = ModelFormat.NON_SPECIFIED

    @classmethod
    def is_me(cls, model: Any) -> bool:
        pass


def identifier_selector(model: Any) -> Identifier:
    for identifier in Identifier.REGISTRY:
        if identifier.is_me(model):
            return identifier
    raise NotImplementedError(f"Unalble to identify {model.src}")


def identify(model: Any) -> ModelFormat:
    for identifier in Identifier.REGISTRY:
        if identifier.is_me(model):
            return identifier.FORMAT

    raise NotImplementedError(f"Unalble to identify {model.src}")


class H5(Identifier):
    """
    Use file extension and magic number to identify the file
    """
    FORMAT = ModelFormat.H5

    @classmethod
    def is_me(cls, model: Any) -> bool:
        if model.format == cls.FORMAT:
            return True
        path = model.src

        if not (isinstance(path, Path) and path.exists() and path.is_file()):
            return False
        if str(path).lower().endswith('.h5'):
            return True
        with open(path, 'rb') as f:
            r = f.read(8) == bytes.fromhex('894844460d0a1a0a')
            return r


class ONNX(Identifier):
    """
    Use file extension and magic number to identify the file
    """
    FORMAT = ModelFormat.ONNX

    @classmethod
    def is_me(cls, model: Any):

        if model.format == cls.FORMAT:
            return True

        path = model.src
        if not (isinstance(path, Path) and path.exists() and path.is_file()):
            return False

        if str(path).lower().endswith('.onnx'):
            return True

        # Fixme
        with open(path, 'rb') as f:
            d = f.read(4)
            return d[0] == 8 and d[2:4] in [bytes.fromhex(x) for x in ['1207', '120B']]


class PTH(Identifier):
    """
    Pth archives the model in zip format.

    This identifier determin if the input file is in zip format by magic
    number, then get the file list and check if it match torch strucutre
    """
    FORMAT = ModelFormat.PTH

    @classmethod
    def is_me(cls, model: Any):

        if model.format == cls.FORMAT:
            return True

        path = model.src

        if not (isinstance(path, Path) and path.exists() and path.is_file()):
            return False

        with open(path, 'rb') as f:
            if not f.read(4) == bytes.fromhex('504b0304'):
                return False

        try:
            z = zipfile.ZipFile(path)
            file_names = '|'.join(z.namelist())
            return ('code/__torch__' not in file_names) and \
                   'data.pkl' in file_names and \
                   'data/' in file_names
        except OSError:
            return False


class TorchTraced(Identifier):
    """
    Torchscript archives the model in zip format.

    This identifier determin if the input file is in zip format by magic
    number, then get the file list and check if it match torch strucutre
    """
    FORMAT = ModelFormat.TORCH_TRACED

    @classmethod
    def is_me(cls, model: Any):

        if model.format == cls.FORMAT:
            return True

        path = model.src

        if not (isinstance(path, Path) and path.exists() and path.is_file()):
            return False

        with open(path, 'rb') as f:
            if not f.read(4) == bytes.fromhex('504b0304'):
                return False

        try:
            z = zipfile.ZipFile(path)
            file_names = '|'.join(z.namelist())
            return 'code/__torch__' in file_names and \
                   'data.pkl' in file_names and \
                   'data/' in file_names
        except OSError:
            return False


class PB(Identifier):
    """
    Use file extension and magic number to identify the file
    """

    FORMAT = ModelFormat.PB

    @classmethod
    def is_me(cls, model: Any):

        if model.format == cls.FORMAT:
            return True

        path = model.src

        if not (isinstance(path, Path) and path.exists() and path.is_file()):
            return False

        # I dont find such pattern in:
        # 1. https://github.com/chen0040/java-tensorflow-samples/blob/master/audio-classifier/src/main/resources/tf_models/resnet-v2.pb
        # 2. https://github.com/bugra/putting-tensorflow-2-models-to-production/blob/master/models/resnet/1538687457/saved_model.pb
        # 3. https://github.com/U-t-k-a-r-s-h/Auto-Labeling-tool-using-Tensorflow/blob/master/Mobilenet.pb
        # 4. https://codechina.csdn.net/shy_201992/human-pose-estimation-opencv/-/blob/master/graph_opt.pb
        #
        # with open(path, 'rb') as f:
        #     if f.read(8) == 'PBDEMS2\0':
        #         return True

        # check if 'dtype' exists in the first 1k of the file.
        with open(path, 'rb') as f:
            if bytes.fromhex('0A05647479706512') in f.read(1024):
                return True

        return str(path).lower().endswith('.pb')

class TFLITE(Identifier):
    """
    Use file extension and magic number to identify the file
    """

    FORMAT = ModelFormat.TFLITE

    @classmethod
    def is_me(cls, model: Any):

        if model.format == cls.FORMAT:
            return True

        path = model.src

        if not (isinstance(path, Path) and path.exists() and path.is_file()):
            return False

        with open(path, 'rb') as f:
            if bytes.fromhex('1C00000054464C33') in f.read(8):
                return True

        return False


class SavedModel(Identifier):
    """
    Use directory pattern to identify the file
    """

    FORMAT = ModelFormat.SAVED_MODEL

    @classmethod
    def is_me(cls, model: Any):

        if model.format == cls.FORMAT:
            return True

        path = model.src
        if not (isinstance(path, Path) and path.exists()):
            return False

        if path.is_dir():
            return (os.path.exists(os.path.join(path, 'saved_model.pb')) and
                    os.path.exists(os.path.join(path, 'variables')))
        return False


class ZippedSavedModel(Identifier):
    """
    Use directory pattern to identify the file
    """

    FORMAT = ModelFormat.ZIPPED_SAVED_MODEL

    @classmethod
    def is_me(cls, model: Any) -> bool:

        if model.format == cls.FORMAT:
            return True

        path = model.src
        if not (isinstance(path, Path) and path.exists()):
            return False

        if path.is_file():
            try:
                z = zipfile.ZipFile(path)
                file_names = '|'.join(z.namelist())
                return 'saved_model.pb' in file_names and 'variables' in file_names
            except OSError:
                return False
            except zipfile.BadZipFile:
                return False
        return False


class TFKerasModel(Identifier):
    ''' Use python MRO to check if it contains specific str
    '''

    FORMAT = ModelFormat.TF_KERAS_MODEL

    @classmethod
    def is_me(cls, model: Any):

        if model.format == cls.FORMAT:
            return True

        return _check_object_type('tensorflow.python.keras', model.src)


class TFSession(Identifier):
    ''' Use python MRO to check if it contains specific str
    '''
    FORMAT = ModelFormat.TF_SESSION

    @classmethod
    def is_me(cls, model: Any):

        if model.format == cls.FORMAT:
            return True

        return _check_object_type('tensorflow.python.client.session.Session', model.src)
   

class KerasModel(Identifier):
    '''Use python MRO to check if it contains specific str
    Keras 2.5.0 Serializer
    '''

    FORMAT = ModelFormat.KERAS_MODEL

    @classmethod
    def is_me(cls, model: Any):

        if model.format == cls.FORMAT:
            return True

        return _check_object_type('keras.', model.src)


class PytorchModel(Identifier):
    """Use python MRO to check if it contains specific str"""

    FORMAT = ModelFormat.PT_NN_MODULE

    @classmethod
    def is_me(cls, model: Any):

        if model.format == cls.FORMAT:
            return True

        if _check_object_type('torch.nn.module', model.src):
            return True

        elif _check_object_type('torchvision.models.', model.src):
            return True

        else:
            return False
