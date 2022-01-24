# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import hashlib
import itertools
import re
from collections import defaultdict
from typing import Any, DefaultDict, Dict, List, Mapping, Tuple, Type, Union, cast

from sklearn.base import BaseEstimator
from sklearn.pipeline import FeatureUnion, Pipeline
from sklearn_pandas import DataFrameMapper, gen_features

from azureml.automl.core import _codegen_utilities
from azureml.automl.core.shared._diagnostics.contract import Contract
from azureml.automl.runtime.featurization import DataTransformer

from .constants import FunctionNames
from .featurizer_template import AbstractFeaturizerTemplate

ColumnNameType = Union[str, List[str]]
FeaturizerType = Union[List[BaseEstimator], BaseEstimator, Pipeline]
FeatureType = Tuple[ColumnNameType, FeaturizerType, Mapping[str, object]]


def get_object_repr(obj: Any) -> str:
    return re.sub(r"\s+", "", repr(obj))


def get_object_hash(obj: Any) -> str:
    obj_repr = get_object_repr(obj)
    return get_repr_hash(obj_repr)


def get_repr_hash(repr_str: str) -> str:
    hash_object = hashlib.sha256(repr_str.encode())
    return hash_object.hexdigest()


class IndividualFeaturizerTemplate(AbstractFeaturizerTemplate):
    instance_cache: Dict[str, "IndividualFeaturizerTemplate"] = {}

    def __init__(self, featurizer: FeaturizerType) -> None:
        if isinstance(featurizer, list):
            self.featurizers = featurizer
        else:
            self.featurizers = (
                [featurizer] if not isinstance(featurizer, Pipeline) else [step[1] for step in featurizer.steps]
            )
        self._repr = get_object_repr(featurizer)

    @classmethod
    def get_instance(
        cls: "Type[IndividualFeaturizerTemplate]", featurizer: FeaturizerType
    ) -> "IndividualFeaturizerTemplate":
        key = get_object_repr(featurizer)
        if key not in cls.instance_cache:
            cls.instance_cache[key] = cls(featurizer)
        return cls.instance_cache[key]

    def get_step_name(self) -> str:
        return f"mapper_{self.get_hash()[:6]}"

    def get_hash(self) -> str:
        return get_repr_hash(self._repr)

    def get_function_name(self) -> str:
        return f"get_{self.get_step_name()}"

    def __repr__(self) -> str:
        return self.get_function_name()

    def __hash__(self) -> int:
        return hash(self._repr)

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, self.__class__) and self._repr == other._repr

    @staticmethod
    def _featurizer_to_def(transformer: BaseEstimator) -> List[str]:
        with _codegen_utilities.use_custom_repr():
            # FIXME: We basically take the string representation and then create a new dictionary from that.
            # This is because each class may have some parameters that might need custom handling, so let the
            # class deal with that.
            # We should make this less brittle somehow
            output = ["{", f"    'class': {transformer.__class__.__name__},"]
            repr_str = repr(transformer)
            param_lines = repr_str.split("\n")[1:-1]
            for line in param_lines:
                # With our custom repr, we're expecting a format like
                # Estimator(
                #     param1=value1,
                #     param2=value2
                # )
                # So we match according to this format.
                match = re.fullmatch(r" {4}(.*?)=(.*?),?", line)
                assert match is not None
                key, value = match.group(1, 2)
                output.append(f"    '{key}': {value},")
            output.append("}")

        return output

    @staticmethod
    def can_handle(obj: Any) -> bool:
        return isinstance(obj, BaseEstimator)

    def generate_featurizer_code(self) -> List[str]:
        imports = set(_codegen_utilities.get_recursive_imports(self.featurizers))
        for featurizer in self.featurizers:
            imports.update(_codegen_utilities.get_recursive_imports(featurizer.get_params()))
        imports.add(_codegen_utilities.get_import(gen_features))
        imports.add(_codegen_utilities.get_import(DataFrameMapper))

        # Workaround for CountVectorizer
        if "DataTransformer._wrap_in_lst" in repr(self.featurizers):
            imports.add(_codegen_utilities.get_import(DataTransformer))

        output = [f"def {self.get_function_name()}(column_names):"]
        output.extend(_codegen_utilities.generate_import_statements(imports))
        output.append("")
        output.append("definition = gen_features(")
        output.append("    columns=column_names,")
        output.append("    classes=[")
        for featurizer in self.featurizers:
            featurizer_def = self._featurizer_to_def(featurizer)
            indented_lines = _codegen_utilities.indent_lines(featurizer_def, 8)
            featurizer_str = "\n".join(indented_lines)
            output.append(f"{featurizer_str},")
        output.append("    ]")
        output.append(")")
        output.append("mapper = DataFrameMapper(features=definition, input_df=True, sparse=True)")
        output.append("")
        output.append("return mapper")
        output.append("\n")
        return _codegen_utilities.indent_function_lines(output)


class DataFeaturizerTemplate(AbstractFeaturizerTemplate):
    def __init__(self, pipeline: Pipeline, task_type: str) -> None:
        Contract.assert_true(
            self.can_handle(pipeline), "A pipeline without DataTransformer was provided.", log_safe=True
        )
        self.featurizer = cast(DataTransformer, pipeline.steps[0][1])
        self.task_type = task_type

    @staticmethod
    def can_handle(obj: Pipeline) -> bool:
        return isinstance(obj, Pipeline) and len(obj.steps) > 1 and isinstance(obj.steps[0][1], DataTransformer)

    def get_step_name(self) -> str:
        return "featurization"

    def generate_featurizer_code(self) -> List[str]:
        transformer_and_mapper_list = self.featurizer.transformer_and_mapper_list
        output = [f"def {FunctionNames.FEATURIZE_FUNC_NAME}():"]

        imports = {
            _codegen_utilities.get_import(FeatureUnion),
        }

        output.extend(_codegen_utilities.generate_import_statements(imports))
        output.append("")

        assert transformer_and_mapper_list is not None

        # Group columns based on which columns are using identical transformers
        column_mappings: DefaultDict[IndividualFeaturizerTemplate, List[ColumnNameType]] = defaultdict(list)
        for trm in transformer_and_mapper_list:
            for feature in cast(List[FeatureType], trm.mapper.features):
                template = IndividualFeaturizerTemplate.get_instance(feature[1])
                if isinstance(feature[0], str):
                    # Just wrap it in a list so we can pass it into list.extend().
                    # The transformers that this column will be passed into expect pd.Series.
                    # TODO: Pass DataFrame into transformers and then wrap ones that only allow pd.Series
                    column_mappings[template].extend([feature[0]])
                else:
                    # Each individual column must be wrapped in its own list, or else we will get a pd.Series instead
                    # of a pd.DataFrame in the corresponding transformers.
                    # This applies even if there is only one column inside the list.
                    # The transformers that these columns will be passed into expect pd.DataFrame.
                    column_mappings[template].extend([[f] for f in feature[0]])

        column_groups = set([repr(mapping) for mapping in column_mappings.values()])
        column_group_names = {}
        for i, column_group_str in enumerate(column_groups):
            column_group_names[column_group_str] = f"column_group_{i+1}"

        for column_group_str in column_groups:
            output.append(f"{column_group_names[column_group_str]} = {column_group_str}")
            output.append("")

        if len(column_mappings) > 1:
            # FeatureUnion acts as a functional replacement for DataTransformer
            output.append("feature_union = FeatureUnion([")
            for template, column_group in column_mappings.items():
                column_group_str = repr(column_group)
                column_group_name = column_group_names[column_group_str]
                output.append(
                    f"    ('{template.get_step_name()}', {template.get_function_name()}({column_group_name})),"
                )
            output.append("])")
            output.append("return feature_union")
        else:
            # We only have one template. Generate the mapper directly.
            # TODO: Remove the function call and place the mapper directly into this function body
            template, column_group = next(iter(column_mappings.items()))
            column_group_str = repr(column_group)
            output.append(f"mapper = {template.get_function_name()}({column_group_names[column_group_str]})")
            output.append("return mapper")

        output.append("\n")
        output = "\n".join(output).split("\n")
        output = _codegen_utilities.indent_function_lines(output)

        # Generate code for each featurizer, then flatten it and prepend it to the output
        featurizer_funcs = [template.generate_featurizer_code() for template in column_mappings.keys()]
        return list(itertools.chain.from_iterable([*featurizer_funcs, output]))
