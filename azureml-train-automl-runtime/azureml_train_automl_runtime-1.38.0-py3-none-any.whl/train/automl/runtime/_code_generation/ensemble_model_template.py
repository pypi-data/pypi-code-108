# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from abc import abstractmethod
from typing import Any, List, Tuple, Union, cast

from sklearn.base import BaseEstimator
from sklearn.pipeline import Pipeline

from azureml.automl.core import _codegen_utilities
from azureml.automl.runtime.stack_ensemble_base import Scorer

from . import utilities
from .constants import FunctionNames
from .model_template import AbstractModelTemplate, NamedModelTemplate
from .template_factory import preprocessor_template_factory


class AbstractEnsembleModelTemplate(AbstractModelTemplate):
    def __init__(self, model: BaseEstimator) -> None:
        self.model = model

    @property
    @abstractmethod
    def _subestimator_pipelines(self) -> List[Tuple[Union[str, int], Pipeline]]:
        raise NotImplementedError

    def _get_imports(self) -> List[Tuple[str, str, Any]]:
        imports = [_codegen_utilities.get_import(self.model.__class__), _codegen_utilities.get_import(Pipeline)]
        if hasattr(self.model, "_get_imports"):
            imports.extend(self.model._get_imports())
        return imports

    def _generate_subestimator_code(self, estimator_pipelines: List[Tuple[Any, Pipeline]]) -> List[str]:
        output = []
        # Generate one pair of functions for each estimator
        for i, pipeline_tuple in enumerate(estimator_pipelines):
            pipeline = pipeline_tuple[1]
            steps = cast(List[Tuple[Any, BaseEstimator]], pipeline.steps)
            preproc_template = preprocessor_template_factory.select_template(pipeline, i)
            model_template = NamedModelTemplate(steps[-1][1], i)
            output += preproc_template.generate_preprocessor_code()
            output += model_template.generate_model_code()
        return output

    def _generate_subestimator_pipelines(
        self, estimator_pipelines: List[Tuple[Any, Pipeline]]
    ) -> Tuple[List[str], str]:
        # Generate one pair of functions for each estimator
        output = []
        for i, estimator in enumerate(estimator_pipelines):
            if utilities.pipeline_has_preprocessor(estimator[1]):
                output.append(
                    "pipeline_{0} = Pipeline(steps=[('preproc', {1}_{0}()), ('model', {2}_{0}())])".format(
                        i, FunctionNames.PREPROC_FUNC_NAME, FunctionNames.MODEL_FUNC_NAME
                    )
                )
            else:
                output.append(
                    "pipeline_{0} = Pipeline(steps=[('model', {1}_{0}())])".format(i, FunctionNames.MODEL_FUNC_NAME)
                )

        estimators_output = [
            "[",
            *_codegen_utilities.indent_lines(
                ["('model_{0}', pipeline_{0}),".format(i) for i in range(len(estimator_pipelines))]
            ),
            "]",
        ]
        estimators_str = "\n".join(estimators_output)
        return output, estimators_str


class EnsembleModelTemplate(AbstractEnsembleModelTemplate):
    @property
    def _subestimator_pipelines(self) -> List[Tuple[Union[str, int], Pipeline]]:
        params = self.model.get_params(deep=False)
        # This cast assumes that all subestimators are pipelines and not standalone estimators.
        return cast(List[Tuple[Union[str, int], Pipeline]], params.pop("estimators"))

    def _get_imports(self) -> List[Tuple[str, str, Any]]:
        imports = [_codegen_utilities.get_import(self.model.__class__), _codegen_utilities.get_import(Pipeline)]
        if hasattr(self.model, "_get_imports"):
            imports.extend(self.model._get_imports())
        return imports

    def _get_support_code(self) -> List[str]:
        output = self._generate_subestimator_code(self._subestimator_pipelines)
        return _codegen_utilities.normalize_lines(output)

    def _get_model_code(self) -> List[str]:
        params = self.model.get_params(deep=False)
        params.pop("estimators")
        output = []

        subestimator_defs, subestimators_list = self._generate_subestimator_pipelines(self._subestimator_pipelines)
        output += subestimator_defs

        repr_str = _codegen_utilities.generate_repr_str(self.model.__class__, params, estimators=subestimators_list)
        output.append(f"algorithm = {repr_str}")
        return output

    def get_step_name(self) -> str:
        return "ensemble"


class StackEnsembleModelTemplate(EnsembleModelTemplate):
    def __init__(self, model: BaseEstimator) -> None:
        super().__init__(model)

    @property
    def _subestimator_pipelines(self) -> List[Tuple[Union[str, int], Pipeline]]:
        params = self.model.get_params(deep=False)
        # This cast assumes that all subestimators are pipelines and not standalone estimators.
        return cast(List[Tuple[Union[str, int], Pipeline]], params.pop("base_learners"))

    @property
    def _meta_learner(self) -> BaseEstimator:
        params = self.model.get_params(deep=False)
        return params.pop("meta_learner")

    def _get_support_code(self) -> List[str]:
        output = self._generate_subestimator_code(self._subestimator_pipelines)
        output += MetaLearnerModelTemplate(self._meta_learner).generate_model_code()

        return _codegen_utilities.normalize_lines(output)

    def _get_model_code(self) -> List[str]:
        params = self.model.get_params(deep=False)
        params.pop("base_learners")
        params.pop("meta_learner")
        output = ["meta_learner = {1}_{0}()".format("meta", FunctionNames.MODEL_FUNC_NAME), ""]

        subestimator_defs, subestimators_list = self._generate_subestimator_pipelines(self._subestimator_pipelines)
        output += subestimator_defs
        meta_estimator_str = "meta_learner"

        repr_str = _codegen_utilities.generate_repr_str(
            self.model.__class__, params, base_learners=subestimators_list, meta_learner=meta_estimator_str
        )
        output.append(f"algorithm = {repr_str}")
        return _codegen_utilities.normalize_lines(output)

    def get_step_name(self) -> str:
        return "stackensemble"


class MetaLearnerModelTemplate(NamedModelTemplate):
    def __init__(self, model: BaseEstimator) -> None:
        super().__init__(model, "meta")

    def _get_imports(self) -> List[Tuple[str, str, Any]]:
        imports = super()._get_imports()
        imports.append(_codegen_utilities.get_import(Scorer))
        return imports

    def get_step_name(self) -> str:
        return "meta_learner"
