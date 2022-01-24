# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from abc import ABC, abstractmethod
from typing import List


class PipelineStepTemplate(ABC):
    @abstractmethod
    def get_function_name(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_step_name(self) -> str:
        raise NotImplementedError

    def generate_pipeline_step(self) -> List[str]:
        """
        Generate the pipeline step corresponding to this template.

        May return an empty list.

        :return: a list containing the pipeline step code
        """
        return [f"('{self.get_step_name()}', {self.get_function_name()}()),"]


class NoOpTemplate(PipelineStepTemplate):
    def get_function_name(self) -> str:
        return ""

    def get_step_name(self) -> str:
        return ""

    def generate_pipeline_step(self) -> List[str]:
        return []
