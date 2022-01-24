from typing import Dict, List, Union, Type, Iterable, Any, Tuple
from pathlib import Path

from loguru import logger

from .model.model import Model, Tensor
from .model.meta import retrive_model_metadata
from .model.transformer import ModelTransformer
from .dataset.dataset import Dataset
from .dataset.transformer import DatasetTransformer
from .evaluator import Evaluator
from .evaluator import Metric
from .model import identifier as model_identifier
from .dataset import identifier as dataset_identifier
from .model import serializer as model_serializer
from .dataset import serializer as dataset_serializer

from .dataset.dataset import Dataset
from .model import ModelFormat, ModelDataType
from .dataset import DatasetFormat
from .common import get_tmp_path


class ModelPackage:
    """Contain all data and controllers

    Data include: model and dataset
    Controllers include: evaluators, model_transformer and dataset_transformer

    """

    def __init__(
            self,
            model: Union[object, str, Path, Model],
            dataset: Union[object, str, Path, Dataset],
            model_format: ModelFormat = ModelFormat.NON_SPECIFIED,
            sample_format: DatasetFormat = DatasetFormat.NON_SPECIFIED,
            #  [name: str, shape:Tuple, dtype:ModelDataType]
            model_inputs: List[Union[List, Tuple, Tensor]] = [],
            #  [name: str, shape:Tuple, dtype:ModelDataType]
            model_outputs: List[Union[List, Tuple, Tensor]] = []):

        self._src_model = model
        self._src_dataset = dataset
        self.evaluators: List[Evaluator] = []
        self.model_transformers: List[ModelTransformer] = []
        self.dataset_transformers: List[DatasetTransformer] = []

        self.__encapsulate_model(model_format, model_inputs, model_outputs)
        self.__encapsulate_dataset(sample_format)

    def __encapsulate_model(self, model_format, model_inputs, model_outputs):
        # Convert to a Model object if it is not
        if isinstance(self._src_model, Model):
            self.model = self._src_model
        elif isinstance(self._src_model, str):
            self.model = Model(Path(self._src_model))
        else:
            self.model = Model(self._src_model)

        # Retrive inputs
        # if the input name is not specified, retrive automatically
        meta = retrive_model_metadata(self.model)

        if len(model_inputs) == 0:
            for tensor in meta.inputs:
                self.model.add_input(tensor)
        else:
            meta_input_names = set([x.name for x in meta.inputs])
            logger.info(f"meta_input_names: {meta_input_names}")

            for idx, i in enumerate(model_inputs):
                if isinstance(i, list) or isinstance(i, tuple):
                    assert len(i) > 0
                    name = i[0]
                    shape = i[1] if len(i) >= 2 else tuple()
                    dtype = i[2] if len(i) >= 3 else ModelDataType.NON_SPECIFIED
                    tensor = Tensor(name, shape, dtype)
                elif isinstance(i, Tensor):
                    tensor = i

                self.model.add_input(tensor)
                if tensor.name not in meta_input_names:
                    logger.warning(f"It seems input tenosr({tensor.name})"
                                   f" does not match with model input schema"
                                   f"({meta_input_names}).")

        # Retrive outputs
        # if the _output name is not specified, retrive automatically
        if len(model_inputs) == 0 and len(model_outputs) == 0:
            for tensor in meta.outputs:
                self.model.add_output(tensor)
        elif len(model_outputs) == 0:
            for tensor in meta.outputs:
                self.model.add_output(tensor)
        else:
            meta_output_names = set([x.name for x in meta.outputs])

            for idx, i in enumerate(model_outputs):
                if isinstance(i, list) or isinstance(i, tuple):
                    assert len(i) > 0
                    name = i[0]
                    shape = i[1] if len(i) >= 2 else tuple()
                    dtype = i[2] if len(i) >= 3 else ModelDataType.NON_SPECIFIED
                    tensor = Tensor(name, shape, dtype)
                elif isinstance(i, Tensor):
                    tensor = i

                self.model.add_output(tensor)

                if tensor.name not in meta_output_names:
                    logger.warning(f"It seems output tenosr({tensor.name})"
                                   f" does not match with model output schema"
                                   f"({meta_output_names}).")

        # Assign or identify model format
        if not model_format == ModelFormat.NON_SPECIFIED:
            self.model.format = model_format
        else:
            self.model.format = model_identifier.identify(self.model)

        logger.debug(self.model.format.name)

    def __encapsulate_dataset(self, dataset_format: DatasetFormat):
        # Convert to a Dataset object if it is not
        if isinstance(self._src_dataset, Dataset):
            self.dataset = self._src_dataset
        elif isinstance(self._src_dataset, str):
            self.dataset = Dataset(Path(self._src_dataset))
        else:
            self.dataset = Dataset(self._src_dataset)

        # specify model format or identify it automatically
        if not dataset_format == DatasetFormat.NON_SPECIFIED:
            self.dataset.format = dataset_format
        else:
            self.dataset.format = dataset_identifier.identify(self.dataset)

    def transform_model(self) -> Type[Model]:
        model = self.model
        for mt in self.model_transformers:
            model = mt.transform(model)
        return model

    def transform_dataset(self) -> Type[Dataset]:
        dataset = self.dataset
        for dt in self.dataset_transformers:
            dataset = dt.transform(dataset)
        return dataset

    def evaluate(self, model, dataset) -> List[Metric]:
        return [e.evaluate(model, dataset) for e in self.evaluators]

    def add_model_transformer(self, model_transformer: ModelTransformer):
        self.model_transformers.append(model_transformer)

    def add_dataset_transformer(self, ds_transformer: DatasetTransformer):
        self.dataset_transformers.append(ds_transformer)

    def add_evaluator(self, evaluator: Evaluator):
        self.evaluators.append(evaluator)

    def serialize(self,
                  model_path: Union[str, Path, None] = None,
                  dataset_path: Union[str, Path, None] = None):

        if model_path is None:
            model_path = get_tmp_path()
        if dataset_path is None:
            dataset_path = get_tmp_path()

        orig_inputs = self.model.inputs
        orig_outputs = self.model.outputs

        self._src_model = model_serializer.serialize(self.model,
                                                     Path(model_path))

        self._src_dataset = dataset_serializer.serialize(
            self.dataset, Path(dataset_path))

        # we need to get the meta again after serialization
        self.__encapsulate_model(ModelFormat.NON_SPECIFIED, orig_inputs,
                                 orig_outputs)
        self.__encapsulate_dataset(DatasetFormat.NON_SPECIFIED)

    def dump(self) -> Dict:
        data = {
            "model":
                self.model.dump(),
            "dataset":
                self.dataset.dump(),
            "evaluators": [x.dump() for x in self.evaluators],
            "model_transformers": [x.dump() for x in self.model_transformers],
            "dataset_transformers": [
                x.dump() for x in self.dataset_transformers
            ]
        }
        return data

    def load(self, data: Dict):
        pass
