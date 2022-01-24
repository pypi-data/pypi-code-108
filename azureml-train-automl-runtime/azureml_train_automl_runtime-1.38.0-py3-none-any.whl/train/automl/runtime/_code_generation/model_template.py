# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from abc import abstractmethod
from typing import Any, List, Tuple, Union, cast

from sklearn.base import BaseEstimator

from azureml.automl.core import _codegen_utilities
from azureml.automl.runtime.shared.model_wrappers import CalibratedModel, _AbstractModelWrapper

from .constants import FunctionNames
from .pipeline_step_template import PipelineStepTemplate


class AbstractModelTemplate(PipelineStepTemplate):
    @abstractmethod
    def _get_imports(self) -> List[Tuple[str, str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def _get_model_code(self) -> List[str]:
        raise NotImplementedError

    @abstractmethod
    def _get_support_code(self) -> List[str]:
        raise NotImplementedError

    def get_function_name(self) -> str:
        return FunctionNames.MODEL_FUNC_NAME

    def get_step_name(self) -> str:
        return "model"

    def generate_pipeline_step(self) -> List[str]:
        return [f"('{self.get_step_name()}', {self.get_function_name()}()),"]

    def generate_model_code(self) -> List[str]:
        support_code = self._get_support_code()
        output = [f"def {self.get_function_name()}():"]
        output.extend(_codegen_utilities.generate_import_statements(self._get_imports()))
        output.append("")
        output.extend(self._get_model_code())
        output.append("")
        output.append("return algorithm")
        output.append("\n")
        return support_code + _codegen_utilities.indent_function_lines(output)


class SingleModelTemplate(AbstractModelTemplate):
    def __init__(self, model: Union[BaseEstimator, _AbstractModelWrapper]) -> None:
        while isinstance(model, _AbstractModelWrapper):
            if isinstance(model, CalibratedModel):
                break
            underlying_model = model.get_model()
            if isinstance(underlying_model, BaseEstimator) and underlying_model is not model:
                model = underlying_model
            else:
                break
        self.model = cast(BaseEstimator, model)

    def _get_imports(self) -> List[Tuple[str, str, Any]]:
        imports = [_codegen_utilities.get_import(self.model.__class__)]
        if hasattr(self.model, "_get_imports"):
            imports.extend(self.model._get_imports())
        return imports

    def _get_model_code(self) -> List[str]:
        return [f"algorithm = {self.model}"]

    def _get_support_code(self) -> List[str]:
        return []


class NamedModelTemplate(SingleModelTemplate):
    def __init__(self, model: BaseEstimator, model_name: Union[str, int]) -> None:
        super().__init__(model)
        self.model_name = model_name

    def get_step_name(self) -> str:
        return f"model_{self.model_name}"

    def get_function_name(self) -> str:
        return f"{super().get_function_name()}_{self.model_name}"

    def _get_support_code(self) -> List[str]:
        return []

    def generate_pipeline_step(self) -> List[str]:
        # TODO: This code isn't really standalone because it assumes pipeline_0, etc has already been defined.
        #  Should this be changed?
        return [f"('{self.get_step_name()}', pipeline_{self.model_name}),"]
