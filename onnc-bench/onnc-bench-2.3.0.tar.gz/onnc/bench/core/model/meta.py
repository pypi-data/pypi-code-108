from typing import List
from pathlib import Path
from abc import abstractmethod
import shutil
from dataclasses import dataclass
import zipfile    


from loguru import logger

from .transformer import ModelTransformer
from .model import Model, Tensor
from . import ModelFormat, ModelDataType
from .identifier import identify
from ..common import get_tmp_path


class MetadataRetriverRegistry(type):

    REGISTRY: List = []

    def __new__(cls, name, bases, attrs):
        new_cls = type.__new__(cls, name, bases, attrs)
        cls.REGISTRY.append(new_cls)
        return new_cls


class ModelMeta:
    def __init__(self, inputs: List[Tensor], outputs: List[Tensor]):
        self.inputs = inputs
        self.outputs = outputs


class MetadataRetriver(metaclass=MetadataRetriverRegistry):

    FORMAT: ModelFormat = ModelFormat.NON_SPECIFIED

    @classmethod
    def is_me(cls, model: Model) -> bool:
        return identify(model) == cls.FORMAT

    @abstractmethod
    def retrive_inputs(self, model: Model) -> List[Tensor]:
        raise NotImplementedError("`retrive_inputs` has to be implemented")

    @abstractmethod
    def retrive_outputs(self, model: Model) -> List[Tensor]:
        raise NotImplementedError("`retrive_outputs` has to be implemented")

    def retrive(self, model: Model) -> ModelMeta:
        inputs = self.retrive_inputs(model)
        logger.info(f"Inputs of {model.name}: {inputs}")
        outputs = self.retrive_outputs(model)
        logger.info(f"Outputs of {model.name}: {outputs}")
        return ModelMeta(inputs=inputs,
                         outputs=outputs)


def metadataretriver_selector(model: Model) -> MetadataRetriver:
    for metadataretriver in MetadataRetriver.REGISTRY:
        if metadataretriver.is_me(model):
            return metadataretriver
    raise NotImplementedError(f"Unalble to retrive metadata from {model}")


def retrive_model_metadata(model: Model) -> ModelMeta:
    for metadataretriver in MetadataRetriver.REGISTRY:
        if metadataretriver.is_me(model):
            return metadataretriver().retrive(model)

    raise NotImplementedError(f"Unalble to retrive metadata of {model.format}")


# class FileSerializer(MetadataRetriver):

#     FORMAT: ModelFormat = ModelFormat.NON_SPECIFIED

#     def transform(self, model: Model):
#         dest = self.get_param('dest')

#         if model.src.is_file():
#             shutil.move(model.src, dest)

#         elif model.src.is_dir():
#             # Zip the dir if the model is in dir form
#             tmp_path = Path(get_tmp_path())
#             shutil.make_archive(tmp_path, 'zip', model.src)
#             shutil.move(tmp_path / '.zip', dest)

#         return Model(dest)


class H5(MetadataRetriver):

    FORMAT = ModelFormat.H5

    def retrive_inputs(self, model: Model) -> List[Tensor]:
        from tensorflow import keras  # type: ignore[import]
        _model = keras.models.load_model(model.src)

        return [Tensor(name=x.name, shape=tuple(x.shape.as_list()),
                       dtype=x.dtype) for x in _model.inputs]

    def retrive_outputs(self, model: Model) -> List[Tensor]:
        # from tensorflow import keras
        # model = keras.models.load_model(model.src)
        # outputs = {}
        # for x in model.outputs:
        #     inputs[x.name] = Tensor(name=x.name,
        #                             shape=tuple(x.shape.as_list()),
        #                             dtype=x.dtype)
        from tensorflow import keras  # type: ignore[import]
        _model = keras.models.load_model(model.src)

        return [Tensor(name=x.name, shape=tuple(x.shape.as_list()),
                       dtype=x.dtype) for x in _model.outputs]


class ONNX(MetadataRetriver):

    FORMAT = ModelFormat.ONNX
    def retrive_inputs(self, model: Model) -> List[Tensor]:
        import onnx
        onnx_model = onnx.load(model.src)

        input_all = [node.name for node in onnx_model.graph.input]
        input_initializer =  [node.name for node in onnx_model.graph.initializer]
        net_feed_input = list(set(input_all)  - set(input_initializer))

        return [Tensor(x, tuple(), ModelDataType.NON_SPECIFIED) for x in net_feed_input]

    def retrive_outputs(self, model: Model) -> List[Tensor]:
        import onnx
        model = onnx.load(model.src)
        output =[node.name for node in model.graph.output]

        return [Tensor(x, tuple(), ModelDataType.NON_SPECIFIED) for x in output]



class PTH(MetadataRetriver):

    FORMAT = ModelFormat.PTH

    def retrive_inputs(self, model: Model) -> List[Tensor]:
        import torch
        _model = torch.jit.load(model.src)
        tensor = list(_model.parameters())[  # type: ignore[union-attr]
            0].detach()
        t_name = "input" if tensor.name == None else tensor.name
        tensor = tensor.numpy()
        return [Tensor(t_name, tensor.shape, tensor.dtype)]

    def retrive_outputs(self, model: Model) -> List[Tensor]:
        import torch
        _model = torch.jit.load(model.src)

        # type: ignore[union-attr]
        tensor = list(_model.parameters())[-1].detach()
        t_name = "output" if tensor.name == None else tensor.name
        tensor = tensor.numpy()
        return [Tensor(t_name, tensor.shape, tensor.dtype)]


class PB(MetadataRetriver):

    FORMAT = ModelFormat.PB

    # https://stackoverflow.com/questions/43517959/given-a-tensor-flow-model-graph-how-to-find-the-input-node-and-output-node-name
    def _load_graph(self, frozen_graph_filename):
        import tensorflow as tf
        with tf.io.gfile.GFile(frozen_graph_filename, "rb") as f:
            graph_def = tf.compat.v1.GraphDef()
            graph_def.ParseFromString(f.read())
        with tf.Graph().as_default() as graph:
            tf.import_graph_def(graph_def)

        ops = graph.get_operations()
        return ops

    def analyze_inputs_outputs(graph):

        inputs = []
        for op in ops:
            if len(op.inputs) == 0 and op.type != 'Const':
                inputs.append(op)
            else:
                for input_tensor in op.inputs:
                    if input_tensor.op in outputs_set:
                        outputs_set.remove(input_tensor.op)
        outputs = list(outputs_set)
        return (inputs, outputs)

    def retrive_inputs(self, model: Model) -> List[Tensor]:
        import tensorflow as tf
        ops = self._load_graph(model.src)
        inputs = []
        for op in ops:
            if len(op.inputs) == 0 and op.type != 'Const':
                inputs.append(op)

        return [Tensor(name=x.name, shape=tuple(x.outputs[0].shape.as_list()),
                       dtype=x.outputs[0].dtype) for x in inputs]
        """
        >>> [x.size for x in graph_def.node[0].attr['shape'].shape.dim]
        [-1, 96, 96, 3]
        """
    def retrive_outputs(self, model: Model) -> List[Tensor]:
        import tensorflow as tf
        ops = self._load_graph(model.src)
        inputs = []
        outputs_set = set(ops)

        for op in ops:
            if len(op.inputs) == 0 and op.type != 'Const':
                inputs.append(op)
            else:
                for input_tensor in op.inputs:
                    if input_tensor.op in outputs_set:
                        outputs_set.remove(input_tensor.op)

        outputs = list(outputs_set)

        return [Tensor(name=x.name, shape=tuple(x.outputs[0].shape.as_list()),
                       dtype=x.outputs[0].dtype) for x in outputs]


class SavedModel(MetadataRetriver):

    FORMAT = ModelFormat.SAVED_MODEL

    def retrive_inputs(self, model: Model) -> List[Tensor]:
        from tensorflow import keras  # type: ignore[import]
        _model = keras.models.load_model(model.src)

        return [Tensor(name=x.name, shape=tuple(x.shape.as_list()),
                       dtype=x.dtype) for x in _model.inputs]

    def retrive_outputs(self, model: Model) -> List[Tensor]:
        # from tensorflow import keras
        # model = keras.models.load_model(model.src)
        # outputs = {}
        # for x in model.outputs:
        #     inputs[x.name] = Tensor(name=x.name,
        #                             shape=tuple(x.shape.as_list()),
        #                             dtype=x.dtype)
        from tensorflow import keras  # type: ignore[import]
        _model = keras.models.load_model(model.src)

        return [Tensor(name=x.name, shape=tuple(x.shape.as_list()),
                       dtype=x.dtype) for x in _model.outputs]


class ZippedSavedModel(MetadataRetriver):

    FORMAT = ModelFormat.ZIPPED_SAVED_MODEL

    def retrive_inputs(self, model: Model) -> List[Tensor]:
        from tensorflow import keras  # type: ignore[import]

        temp = get_tmp_path()

        with zipfile.ZipFile(model.src, 'r') as zip_ref:  # type: ignore[arg-type]
            zip_ref.extractall(temp)


        _model = keras.models.load_model(temp)

        return [Tensor(name=x.name, shape=tuple(x.shape.as_list()),
                       dtype=x.dtype) for x in _model.inputs]

    def retrive_outputs(self, model: Model) -> List[Tensor]:
        from tensorflow import keras  # type: ignore[import]

        temp = get_tmp_path()

        with zipfile.ZipFile(model.src, 'r') as zip_ref:  # type: ignore[arg-type]
            zip_ref.extractall(temp)


        _model = keras.models.load_model(temp)

        return [Tensor(name=x.name, shape=tuple(x.shape.as_list()),
                       dtype=x.dtype) for x in _model.outputs]


class TFKerasModel(MetadataRetriver):

    FORMAT = ModelFormat.TF_KERAS_MODEL

    def retrive_inputs(self, model: Model) -> List[Tensor]:
        return [Tensor(name=x.name, shape=tuple(x.shape.as_list()),
                       dtype=x.dtype) for x in model.src.inputs]

    def retrive_outputs(self, model: Model) -> List[Tensor]:
        return [Tensor(name=x.name, shape=tuple(x.shape.as_list()),
                       dtype=x.dtype) for x in model.src.outputs]


class KerasModel(MetadataRetriver):
    '''
    Keras 2.5.0 Serializer
    '''

    FORMAT = ModelFormat.KERAS_MODEL

    def retrive_inputs(self, model: Model) -> List[Tensor]:
        return [Tensor(name=x.name, shape=tuple(x.shape.as_list()),
                       dtype=x.dtype) for x in model.src.inputs]   # type: ignore[union-attr]

    def retrive_outputs(self, model: Model) -> List[Tensor]:
        return [Tensor(name=x.name, shape=tuple(x.shape.as_list()),
                       dtype=x.dtype) for x in model.src.outputs]  # type: ignore[union-attr]


class PytorchModel(MetadataRetriver):
    """Use python MRO to check if it contains specific str"""

    FORMAT = ModelFormat.PT_NN_MODULE

    def retrive_inputs(self, model: Model) -> List[Tensor]:
        _model = model.src
        tensor = list(_model.parameters())[  # type: ignore[union-attr]
            0].detach()
        t_name = "input" if tensor.name == None else tensor.name
        tensor = tensor.numpy()
        return [Tensor(t_name, tensor.shape, tensor.dtype)]

    def retrive_outputs(self, model: Model) -> List[Tensor]:
        _model = model.src

        # type: ignore[union-attr]
        tensor = list(_model.parameters())[-1].detach()
        t_name = "output" if tensor.name == None else tensor.name
        tensor = tensor.numpy()
        return [Tensor(t_name, tensor.shape, tensor.dtype)]


class TorchTracedModel(MetadataRetriver):

    FORMAT = ModelFormat.TORCH_TRACED

    def retrive_inputs(self, model: Model) -> List[Tensor]:
        import torch
        _model = torch.jit.load(model.src)
        tensor = list(_model.parameters())[  # type: ignore[union-attr]
            0].detach()
        t_name = "input" if tensor.name == None else tensor.name
        tensor = tensor.numpy()
        return [Tensor(t_name, tensor.shape, tensor.dtype)]

    def retrive_outputs(self, model: Model) -> List[Tensor]:
        import torch
        _model = torch.jit.load(model.src)

        # type: ignore[union-attr]
        tensor = list(_model.parameters())[-1].detach()
        t_name = "output" if tensor.name == None else tensor.name
        tensor = tensor.numpy()
        return [Tensor(t_name, tensor.shape, tensor.dtype)]


class TFLiteModel(MetadataRetriver):
    """Use python MRO to check if it contains specific str"""

    FORMAT = ModelFormat.TFLITE

    def retrive_inputs(self, model: Model) -> List[Tensor]:
        try:
            import tflite_runtime.interpreter as tflite
            interpreter = tflite.Interpreter(model_path=model.src)
        except ModuleNotFoundError:
            import tensorflow as tf
            interpreter = tf.lite.Interpreter(model_path=model.src)

        return [[i["name"], i["shape"].tolist(), i['dtype']] for i in interpreter.get_input_details()]


    def retrive_outputs(self, model: Model) -> List[Tensor]:
        try:
            import tflite_runtime.interpreter as tflite
            interpreter = tflite.Interpreter(model_path=model.src)
        except ModuleNotFoundError:
            import tensorflow as tf
            interpreter = tf.lite.Interpreter(model_path=model.src)

        return [[i["name"], i["shape"].tolist(), i['dtype']] for i in interpreter.get_output_details()]
