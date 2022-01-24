# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from abc import abstractmethod
from typing import Any, List, Union, cast

from sklearn.base import TransformerMixin
from sklearn.pipeline import Pipeline

from azureml.automl.core import _codegen_utilities
from azureml.automl.core.shared._diagnostics.contract import Contract

from . import utilities
from .constants import FunctionNames
from .pipeline_step_template import NoOpTemplate, PipelineStepTemplate


class AbstractPreprocessorTemplate(PipelineStepTemplate):
    @abstractmethod
    def get_function_name(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_step_name(self) -> str:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def can_handle(obj: Any) -> bool:
        raise NotImplementedError

    @abstractmethod
    def generate_preprocessor_code(self) -> List[str]:
        """
        Generate code for this preprocessor using this template.

        May return an empty list.

        :return: a list containing generated code
        """
        raise NotImplementedError


class PreprocessorTemplate(AbstractPreprocessorTemplate):
    def __init__(self, pipeline: Pipeline) -> None:
        Contract.assert_true(self.can_handle(pipeline), "A pipeline without preprocessor was provided.", log_safe=True)
        self.preprocessor = pipeline.steps[-2][1]

    def get_function_name(self) -> str:
        return FunctionNames.PREPROC_FUNC_NAME

    def get_step_name(self) -> str:
        return "preproc"

    @staticmethod
    def can_handle(obj: Any) -> bool:
        return isinstance(obj, Pipeline) and utilities.pipeline_has_preprocessor(obj)

    def generate_preprocessor_code(self) -> List[str]:
        output = [f"def {self.get_function_name()}():"]

        imports = [_codegen_utilities.get_import(self.preprocessor.__class__)]
        if hasattr(self.preprocessor, "_get_imports"):
            imports.extend(self.preprocessor._get_imports())

        output.extend(_codegen_utilities.generate_import_statements(imports))
        output.append("")

        output.append(f"preproc = {self.preprocessor}")
        output.append("")
        output.append("return preproc")
        output.append("\n")
        return _codegen_utilities.indent_function_lines(output)


class NamedPreprocessorTemplate(PreprocessorTemplate):
    def __init__(self, pipeline: Pipeline, preprocessor_name: Union[str, int]) -> None:
        super().__init__(pipeline)
        self.preprocessor_name = preprocessor_name

    def get_function_name(self):
        return f"{super().get_function_name()}_{self.preprocessor_name}"

    def get_step_name(self) -> str:
        return f"preproc_{self.preprocessor_name}"


class NoPreprocessorTemplate(NoOpTemplate, AbstractPreprocessorTemplate):
    @staticmethod
    def can_handle(obj: Any) -> bool:
        return isinstance(obj, Pipeline) and not utilities.pipeline_has_preprocessor(obj)

    def generate_preprocessor_code(self) -> List[str]:
        return []
