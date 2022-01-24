# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import List, cast

from sklearn.pipeline import Pipeline

from azureml.automl.core import _codegen_utilities
from azureml.automl.core.shared._diagnostics.contract import Contract
from azureml.automl.runtime.featurizer.transformer.timeseries import TimeSeriesTransformer

from .constants import FunctionNames
from .featurizer_template import AbstractFeaturizerTemplate


class TimeSeriesFeaturizerTemplate(AbstractFeaturizerTemplate):
    def __init__(self, pipeline: Pipeline) -> None:
        Contract.assert_true(
            self.can_handle(pipeline), "A pipeline without TimeSeriesTransformer was provided.", log_safe=True
        )
        self.featurizer = cast(TimeSeriesTransformer, pipeline.steps[0][1])

    @staticmethod
    def can_handle(obj: Pipeline) -> bool:
        return isinstance(obj, Pipeline) and len(obj.steps) > 1 and isinstance(obj.steps[0][1], TimeSeriesTransformer)

    def get_step_name(self) -> str:
        return "tst"

    def generate_featurizer_code(self) -> List[str]:
        output = [f"def {FunctionNames.FEATURIZE_FUNC_NAME}():"]

        imports = set(self.featurizer._get_imports())
        imports.add(("numpy", "nan", float))
        imports.add(_codegen_utilities.get_import(TimeSeriesTransformer))

        output.extend(_codegen_utilities.generate_import_statements(imports))
        output.append("")

        output.append("transformer_list = []")

        assert self.featurizer.pipeline is not None
        for i, step in enumerate(self.featurizer.pipeline.steps):
            i += 1
            transformer = step[1]
            tr_str = f"transformer{i}"
            output.append(f"{tr_str} = {transformer}")
            output.append(f"transformer_list.append(('{step[0]}', {tr_str}))")
            output.append("")

        output.append("pipeline = Pipeline(steps=transformer_list)")

        params = self.featurizer.get_params(deep=False)
        params.pop("pipeline")
        pipeline_type = params.pop("pipeline_type")
        pipeline_type_str = f"{pipeline_type.__class__.__name__}.{pipeline_type.name}"

        tst_repr = _codegen_utilities.generate_repr_str(
            self.featurizer.__class__,
            params,
            pipeline="pipeline",
            pipeline_type=pipeline_type_str,
        )

        output.append(f"tst = {tst_repr}")
        output.append("")
        output.append("return tst")
        output.append("\n")

        output = "\n".join(output).split("\n")
        return _codegen_utilities.indent_function_lines(output)
