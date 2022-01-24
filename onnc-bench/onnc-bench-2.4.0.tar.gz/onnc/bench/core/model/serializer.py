from typing import List
from pathlib import Path
from abc import abstractmethod
import shutil
from loguru import logger

from .transformer import ModelTransformer
from .model import Model
from . import ModelFormat
from .identifier import identify
from ..common import get_tmp_path


class SerializerRegistry(type):

    REGISTRY: List = []

    def __new__(cls, name, bases, attrs):


        new_cls = type.__new__(cls, name, bases, attrs)
        cls.REGISTRY.append(new_cls)
        return new_cls


class Serializer(ModelTransformer, metaclass=SerializerRegistry):

    FORMAT = None

    @classmethod
    def is_me(cls, model: Model) -> bool:
        return identify(model) == cls.FORMAT

    @abstractmethod
    def transform(self, model: Model) -> Model:
        raise NotImplementedError("`transform` has to be implemented")

    def serialize(self, model: Model, dest: Path) -> Model:
        self.add_param('dest', dest)   # type: ignore[attr-defined]
        m = self.transform(model)
        return m


def serializer_selector(model: Model) -> Serializer:
    for serializer in Serializer.REGISTRY:
        if serializer.is_me(model):
            return serializer
    raise NotImplementedError(f"Unalble to serialize {model}")


def serialize(model: Model, dest: Path) -> Model:
    for serializer in Serializer.REGISTRY:
        if serializer.is_me(model):
            return serializer().serialize(model, dest)

    raise NotImplementedError(f"Unalble to serialize {model}")


class FileSerializer(Serializer):

    FORMAT: ModelFormat = ModelFormat.NON_SPECIFIED

    def transform(self, model: Model):
        dest = self.get_param('dest')

        if model.src.is_file():
            shutil.copy(model.src, dest)
        else:
            raise Exception(f'src [`{model.src}`] should be a path to a file.')

        return Model(dest)

    def serialize(self, model: Model, dest: Path) -> Model:
        # return super().serialize(model, dest)
        self.add_param('dest', dest)   # type: ignore[attr-defined]
        m = self.transform(model)
        return m

class DirSerializer(Serializer):

    FORMAT: ModelFormat = ModelFormat.NON_SPECIFIED

    def transform(self, model: Model):
        dest = self.get_param('dest')

        if Path(dest).exists() and Path(dest).is_dir():
            raise Exception(f'dest `{dest}` should be a file path.')
        elif not Path(dest).exists:
            if dest[-1] in ['\\', '/']:
                raise Exception(f"dest `{dest}` should file path, not a dir")

        if model.src.is_dir():
            # Zip the dir if the model is in dir form
            tmp_path = Path(get_tmp_path()[:-1])
            shutil.make_archive(str(tmp_path), 'zip', model.src)
            shutil.move(str(tmp_path) + '.zip', dest)
        else:
            raise Exception(f'model source `{model.src}` should be a path to a dir.')

        return Model(dest)

    def serialize(self, model: Model, dest: Path) -> Model:
        # return super().serialize(model, dest)
        self.add_param('dest', dest)   # type: ignore[attr-defined]
        m = self.transform(model)
        return m


class H5(FileSerializer):

    FORMAT = ModelFormat.H5


class ONNX(FileSerializer):

    FORMAT = ModelFormat.ONNX


class PTH(FileSerializer):

    FORMAT = ModelFormat.PTH


class PB(FileSerializer):

    FORMAT = ModelFormat.PB

class TorchTraced(FileSerializer):

    FORMAT = ModelFormat.TORCH_TRACED

class TFLITE(FileSerializer):

    FORMAT = ModelFormat.TFLITE

class SavedModel(DirSerializer):

    FORMAT = ModelFormat.SAVED_MODEL


class ZippedSavedModel(FileSerializer):

    FORMAT = ModelFormat.ZIPPED_SAVED_MODEL



class TFKerasModel(Serializer):
    '''
    '''

    FORMAT = ModelFormat.TF_KERAS_MODEL

    def transform(self, model: Model):
        dest = self.get_param('dest')

        # TF model.save uses file ext to determine the format to
        # be saved. if not specified, SavedModel willl be used.
        model.src.save(dest.with_suffix('.h5'))
        shutil.move(dest.with_suffix('.h5'), dest)
        return Model(dest)


class KerasModel(Serializer):
    '''
    Keras 2.5.0 Serializer
    '''

    FORMAT = ModelFormat.KERAS_MODEL

    def transform(self, model: Model):
        dest = self.get_param('dest')
        model.src.save(dest.with_suffix('.h5'))
        shutil.move(dest.with_suffix('.h5'), dest)
        return Model(dest)


class TF_Session(Serializer):
    '''
    Keras 2.5.0 Serializer
    '''

    FORMAT = ModelFormat.TF_SESSION

    def transform(self, model: Model):
        import tensorflow

        dest = self.get_param('dest')

        saver = tensorflow.train.Saver()

        sess = model.src
        sess.run(tensorflow.initialize_all_variables())

        model.src.save(dest.with_suffix('.h5'))
        shutil.move(dest.with_suffix('.h5'), dest)
        return Model(dest)

class PytorchModel(Serializer):
    """Use python MRO to check if it contains specific str"""

    FORMAT = ModelFormat.PT_NN_MODULE

    def transform(self, model: Model):
        import torch

        dest = self.get_param('dest')

        if not model.inputs:
            raise Exception(
                "PytorchModel requires input shpae, please add an input tensor in the Model")

        for input_tensor in model.inputs:
            try:
                if not all(isinstance(x, int) for x in input_tensor.shape):
                    raise Exception(f"Parameter `shape` must be List[int]")
            except Exception as e:
                raise Exception("Parameter `shape` must be List[int]")

        dummy_inputs = []
        if not len(model.inputs) > 0:
            raise Exception(
                "Pytorch model has to have at least one input tensor")

        for input_tensor in model.inputs:
            shape = list(input_tensor.shape)
            shape[0] = 1
            shape = tuple(shape)
            dummy_inputs.append(torch.rand(*shape))

        # torch.onnx.export(model.src, tuple(dummy_inputs), dest,
        #                   input_names=[x.name for x in model.inputs],
        #                   output_names=[x.name for x in model.outputs])

        try:
            traced_module = torch.jit.trace(model.src, tuple(dummy_inputs))
        except ValueError as ve:
            logger.error("Unable to save the Pytorch model. "
                         "Specify `inputs` in project.add_model() "
                         "may solve this issue.")
            raise ve

        torch.jit.save(traced_module, dest)

        return Model(dest)
