# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from abc import abstractmethod
from typing import Any, List

from sklearn.pipeline import Pipeline

from . import utilities
from .constants import FunctionNames
from .pipeline_step_template import NoOpTemplate, PipelineStepTemplate


class AbstractFeaturizerTemplate(PipelineStepTemplate):
    @staticmethod
    @abstractmethod
    def can_handle(obj: Any) -> bool:
        """
        Check whether this template can support this object.

        :param obj: the object to check
        :return: True if this template can handle this object, False otherwise
        """
        raise NotImplementedError

    def get_function_name(self) -> str:
        return FunctionNames.FEATURIZE_FUNC_NAME

    @abstractmethod
    def generate_featurizer_code(self) -> List[str]:
        """
        Generate code for this featurizer using this template.

        May return an empty list.

        :return: a list containing generated code
        """
        raise NotImplementedError


class NoFeaturizerTemplate(AbstractFeaturizerTemplate, NoOpTemplate):
    @staticmethod
    def can_handle(obj: Any) -> bool:
        return isinstance(obj, Pipeline) and not utilities.pipeline_has_featurizer(obj)

    def generate_featurizer_code(self) -> List[str]:
        return []
