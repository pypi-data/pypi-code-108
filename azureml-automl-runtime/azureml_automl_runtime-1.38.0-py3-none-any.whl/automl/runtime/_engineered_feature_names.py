# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Classes and methods for generating engineered feature names for features extracted using pre-processing."""
from typing import Any, cast, Dict, List, Optional, Set, Union
import re
from collections import defaultdict

from sklearn.base import TransformerMixin
from sklearn.cluster import MiniBatchKMeans
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MaxAbsScaler

from azureml.automl.core.shared._diagnostics.contract import Contract
from azureml.automl.core.shared._diagnostics.validation import Validation
from azureml.automl.core.constants import (
    FeatureType,
    FEATURIZERS_NOT_TO_BE_SHOWN_IN_ENGG_FEAT_NAMES,
    SupportedTransformersInternal)
from azureml.automl.core.shared.reference_codes import ReferenceCodes

from azureml.automl.runtime.shared.types import FeaturizationSummaryType
from azureml.automl.core.shared.transformer_runtime_exceptions import (
    EngineeredFeatureNamesEmptyJsonException, EngineeredFeatureNamesNoRawFeatureTypeException,
    EngineeredFeatureNamesTransformerNamesNotFoundException,
    EngineeredFeatureNamesNoTransformationsInJsonException,
    EngineeredFeatureNamesUnsupportedIndexException, EngineeredFeatureNamesNotSupportedFeatureTypeException,
    UnrecognizedRawFeatureAliasNameException, UnrecognizedTransformedFeatureNameException)


class _GenerateEngineeredFeatureNames:
    """
    Transforms the transformed raw feature names into engineered feature names.

    The following schema design is followed for storing the engineered names:-

    {
        "FinalTransformerName": string,
        "Transformations": {
            "Transformer1":
            {
                    "Input": [
                                {"InputFeatureName":string},
                                {"InputFeatureName":string}
                            ]
                    "TransformationFunction": string.
                    "Operator": string
                    "FeatureType": string,
                    "ShouldOutput": bool,
                    "Transformer_Params": Dict[string, Any]
            },
            "Transformer2":
            {
                    "Input": [
                                {"InputFeatureName":string},
                                {"InputFeatureName":string}
                            ]
                    "TransformationFunction": string.
                    "Operator": string
                    "FeatureType": string,
                    "ShouldOutput": bool
                    "Transformer_Params": None
            },
            .
            .
            .
            "TransformerN":
            {
                    "Input": [
                                {"InputFeatureName":string},
                                {"InputFeatureName":string}
                            ]
                    "TransformationFunction": string
                    "Operator": string
                    "FeatureType": string,
                    "ShouldOutput": bool
                    "Transformer_Params": Dict[string, Any]
            }
        },

        "Value": string
    }
    """

    def __init__(self, blacklisted_column_aliases: Optional[Set[str]] = None):
        """Initialize this feature name transformer."""
        # Maintain mapping between alias raw feature name and transformation
        # json objects
        self.alias_raw_feature_name_transformation_mapping = {}  # type: Dict[str, _FeatureTransformersAsJSONObject]
        # Maintain a list of string version of engineered feature names
        # Set of blacklisted / prohibited raw feature column aliases
        self._blacklisted_raw_feature_aliases = blacklisted_column_aliases
        self._engineered_feature_names = []     # type: List[str]
        # Maintain a dictionary of JSON objects for engineered feature names
        self._engineered_feature_name_json_objects = {}  # type: Dict[str, Dict[str, Any]]
        # Counter used in determining the next raw feature column alias
        self._raw_feature_alias_counter = 0

    def are_engineered_feature_names_available(self) -> bool:
        """
        Return 'True' if engineered feature names have already been created; 'False' otherwise.

        :return: bool
        """
        return len(self._engineered_feature_names) != 0

    def get_raw_feature_alias_name(self, transformation_json_obj: Any) -> str:
        """
        Take a list of transformations needed for a raw feature and return the resulting alias name.

        :param transformation_json_obj:
        :return: A number represented as string
        """
        # Get a new, unique alias for the incoming feature
        raw_feature_alias = self._generate_next_raw_feature_alias()

        # Add the json string for transformations into a dictionary which
        # maps the alias name to the json string
        self.alias_raw_feature_name_transformation_mapping[raw_feature_alias] = transformation_json_obj

        # Return the alias name for the raw feature
        return raw_feature_alias

    def get_raw_features_featurization_summary(self, is_user_friendly: bool = True) -> FeaturizationSummaryType:
        """
        Return the featurization summary for all the input features seen by this class.

        :return: List of featurization summary for each input feature.
        """
        entire_featurization_summary = _RawFeatureFeaturizationInfo.get_coalesced_raw_feature_featurization_mapping(
            self.alias_raw_feature_name_transformation_mapping, self._engineered_feature_name_json_objects)
        user_friendly_verion = []
        for featurization_summary in entire_featurization_summary:
            user_friendly_verion.append(featurization_summary.to_user_friendly_repr(
                include_transformation_params=not is_user_friendly))
        return user_friendly_verion

    def parse_raw_feature_names(
            self,
            transformed_raw_feature_names: List[str],
            regex_for_parsing_raw_feature_names: Optional[str] = None) -> None:
        """
        Parse transformed raw feature names, compose engineered feature names and store as JSON for later use.

        :param transformed_raw_feature_names:
            A list of string which are the transformed feature names from sklearn transformations
        :param regex_for_parsing_raw_feature_names: Regular expression to be used when parsing a raw feature name.
        """
        # Get the regex for transformed feature names
        if regex_for_parsing_raw_feature_names is None:
            regex_for_parsing_raw_feature_names = FeatureNamesHelper.get_regular_exp_for_parsing_raw_feature_names()

        for raw_feature_name in transformed_raw_feature_names:
            # Parse transformed feature name with the regex
            transformed_feature_match_obj = re.match(
                regex_for_parsing_raw_feature_names, raw_feature_name)

            if transformed_feature_match_obj:
                # If there is a match, then extract the values out of
                # the match object
                raw_feature_alias = transformed_feature_match_obj.group(1)
                value_str = transformed_feature_match_obj.group(3)
            else:
                # If the transformed feature names doesn't match the
                # regular expression, then raise exception
                raise UnrecognizedTransformedFeatureNameException(
                    "Unrecognized transformed feature name passed",
                    reference_code=ReferenceCodes._ENGINEERED_FEATURE_PARSE_RAW_NAMES_TRANSFORMED,
                    has_pii=False)

            # Get JSON transformation data for the raw feature alias name
            if raw_feature_alias not in self.alias_raw_feature_name_transformation_mapping:
                raise UnrecognizedRawFeatureAliasNameException(
                    "Unrecognized raw feature alias name passed",
                    reference_code=ReferenceCodes._ENGINEERED_FEATURE_PARSE_RAW_NAMES_RAW,
                    has_pii=False)

            transformation_json_data_obj = self.alias_raw_feature_name_transformation_mapping[
                raw_feature_alias]

            # Get the raw feature type from the transformations
            feature_type = transformation_json_data_obj.get_raw_feature_type()

            # Clone the dictionary holding the transformation json data
            transformation_json_data = dict(
                transformation_json_data_obj._entire_transformation_json_data)

            if feature_type == FeatureType.DateTime:
                # If the raw feature type is Datetime, then get the
                # sub-feature and store it
                transformation_json_data[_FeatureNameJSONTag.Value] = \
                    DateTimeHelper.get_datetime_transformation_name(
                        int(value_str))
            elif feature_type == FeatureType.Categorical or \
                feature_type == FeatureType.Text or \
                feature_type == FeatureType.Numeric or \
                    feature_type == FeatureType.CategoricalHash:
                # If the raw feature type is Text or Categorical or
                # Categorical Hash, then set the value_str in the JSON
                # If it is numeric we would still want to do this for
                # many to many transformers
                if value_str != '':
                    transformation_json_data[
                        _FeatureNameJSONTag.Value] = value_str

            # Create the string for the engineered feature
            engineered_feature_str = \
                _FeatureTransformersAsJSONObject.\
                get_engineered_feature_name_from_json(transformation_json_data)

            # Add engineered feature name into the list
            self._engineered_feature_names.append(engineered_feature_str)

            # Add the JSON object for the engineered feature name into
            # the dictionary
            self._engineered_feature_name_json_objects[
                engineered_feature_str] = transformation_json_data

    def get_json_object_for_engineered_feature_name(self,
                                                    engineered_feature_name: str) -> Optional[Dict[str, Any]]:
        """
        Fetch the JSON object for the given engineered feature name.

        :param engineered_feature_name: Engineered feature name for whom JSON string is required
        :return: JSON object for engineered feature name
        """
        # Look up the dictionary to see if the engineered
        # feature name exists.
        if engineered_feature_name not in \
                self._engineered_feature_name_json_objects:
            return None

        # Get the JSON object from the dictionary and return it
        return self._engineered_feature_name_json_objects[
            engineered_feature_name]

    def _generate_next_raw_feature_alias(self) -> str:
        """Generate a new, unique raw feature alias."""
        self._raw_feature_alias_counter += 1
        if self._blacklisted_raw_feature_aliases is not None:
            while str(self._raw_feature_alias_counter) in self._blacklisted_raw_feature_aliases:
                self._raw_feature_alias_counter += 1
        return str(self._raw_feature_alias_counter)

    def _record_metadata_and_create_alias(self,
                                          columns: Union[str, List[str]],
                                          transformers: Union[TransformerMixin, List[TransformerMixin], Pipeline],
                                          column_purpose: str) -> str:
        """
        Given a column or a list of columns (K-means cluster distance), list of transformers that are determined to
        be applied on them, their column purpose (we assume that if a list of columns is provided as input, all of
        them belong to the same column purpose), this method is going to record that metadata and create an alias
        prefix for the newly generated columns.

        :param columns: Column or list of columns.
        :param transformers: A list of transformers that are going to be applied on the column(s).
        :param column_purpose: The column purpose or feature type.
        :return: A number casted to a string representing the prefix that will be added to the columns in the
        featurized data from this list of transformers.
        """
        Contract.assert_type(value=columns, name='columns', expected_types=(type(str), List),
                             reference_code=ReferenceCodes._ENGINEERED_FEATURE_INVALID_TYPE_FOR_COLUMNS)
        Contract.assert_type(value=transformers, name='transformers', expected_types=(TransformerMixin,
                                                                                      List,
                                                                                      Pipeline),
                             reference_code=ReferenceCodes._ENGINEERED_FEATURE_INVALID_TYPE_FOR_TRANSFORMERS)
        Contract.assert_value(value=column_purpose, name='column_purpose', valid_values=list(FeatureType.FULL_SET),
                              reference_code=ReferenceCodes._ENGINEERED_FEATURE_INVALID_COLUMN_PURPOSE)

        columns = [columns] if isinstance(columns, str) else columns
        if isinstance(transformers, Pipeline):
            transformers = [step[1] for step in transformers.steps]

        engg_featname_transformers = []  # type: List[_Transformer]
        for index, transformer in enumerate(transformers):
            if hasattr(transformer, '_transformer_name'):
                transformer_name = transformer._transformer_name
            else:
                # For backwards compatibility.
                transformer_name = transformer.__class__.__name__
                if transformer_name == 'TfidfTransformer':
                    transformer_name = SupportedTransformersInternal.TfIdf

            op_key = 'operator_name'
            if hasattr(transformer, op_key) and not callable(getattr(transformer, op_key)):
                operator = getattr(transformer, op_key)
            else:
                operator = None

            parent_feature_list = columns if index == 0 else [index]  # type: ignore
            show_output = transformer_name not in FEATURIZERS_NOT_TO_BE_SHOWN_IN_ENGG_FEAT_NAMES
            transformer_params = _TransformerParamsHelper.to_dict(transformer)
            tr = _Transformer(parent_feature_list,
                              transformer_name,
                              operator,
                              column_purpose if index == 0 else None,
                              show_output,
                              transformer_params)
            engg_featname_transformers.append(tr)

        if not engg_featname_transformers:
            return ""

        feature_transformers = _FeatureTransformers(engg_featname_transformers)
        json_obj = feature_transformers.encode_transformations_from_list()
        alias_column_name = self.get_raw_feature_alias_name(json_obj)
        return alias_column_name


class FeatureNamesHelper:
    """Helper class for feature names."""

    @classmethod
    def get_regular_exp_for_parsing_raw_feature_names(cls) -> str:
        """
        Return the regular expression required for parsing the transformed feature names.

        :return: regex as string
        """
        return r"(\d+)(_?)(.*)"

    @classmethod
    def get_regular_exp_for_parsing_raw_feature_names_streaming(cls) -> str:
        """
        Return the regular expression for parsing transformed streaming feature names.

        :return: regex as string
        """
        return r"(\d+)(\.?)(.*)"

    @classmethod
    def get_transformer_name(cls, transformer_number: int) -> str:
        """
        Return a string for transformer name which is added in the json representation of the transformations.

        :param transformer_number:
        :return: string
        """
        Validation.validate_value(transformer_number, "transformer_number",
                                  reference_code=ReferenceCodes._ENGINEERED_FEATURE_GET_TRANSFORMER_NONE)
        Validation.validate_type(transformer_number, "transformer_number", expected_types=int,
                                 reference_code=ReferenceCodes._ENGINEERED_FEATURE_GET_TRANSFORMER_NOT_INT)

        return _MiscConstants.Transformer + str(transformer_number)


class _FeatureTransformersAsJSONObject:
    """Class to hold the JSON representation of the engineered feature name."""

    AllTransformationsType = Dict[str, Union[str, List[str]]]
    EntireTransformationType = Dict[str, Dict[str, Union[str, List[str]]]]

    def __init__(self):
        self._entire_transformation_json_data = {
            _FeatureNameJSONTag.FinalTransformerName: None,
            _FeatureNameJSONTag.Transformations: None,
            _FeatureNameJSONTag.Value: None
        }   # type: Dict[str, Optional[Any]]

        self._number_transformers = 0
        self._transformer_as_json = {}  # type: Dict[str, Optional[Any]]

    def _set_value_tag(self, value: str) -> None:
        """
        Set value in the feature transformer JSON object.

        :param value: Value to be set inside the feature transformer JSON object.
        :type value: str
        """
        self._entire_transformation_json_data[_FeatureNameJSONTag.Value] = value

    def _add_transformer_to_json(self, parent_feature_list=None,
                                 transformation_fnc=None,
                                 operator=None, feature_type=None,
                                 should_output=None, transformer_params=None):
        """
        Add a transformer to the JSON object.

        :param parent_feature_list:
        :param transformation_fnc:
        :param operator:
        :param feature_type:
        :param should_output:
        :param transformer_params:
        :return:
        """
        self._number_transformers += 1

        # Get the name for the current transformer
        current_transformer_name = FeatureNamesHelper.get_transformer_name(
            self._number_transformers)

        # Form the dictionary for the transformation details
        transformer_json_data = {
            _FeatureNameJSONTag.Input: parent_feature_list,
            _FeatureNameJSONTag.TransformationFunction: transformation_fnc,
            _FeatureNameJSONTag.Operator: operator,
            _FeatureNameJSONTag.FeatureType: feature_type,
            _FeatureNameJSONTag.ShouldOutput: should_output,
            _FeatureNameJSONTag.TransformationParams: transformer_params
        }

        self._transformer_as_json[current_transformer_name] = \
            transformer_json_data

    def _compose_feature_transformers_as_json_obj(self):
        """Compose the JSON object from all the known transformations."""
        self._entire_transformation_json_data[
            _FeatureNameJSONTag.FinalTransformerName] = \
            FeatureNamesHelper.get_transformer_name(
                self._number_transformers)

        self._entire_transformation_json_data[
            _FeatureNameJSONTag.Transformations] = \
            self._transformer_as_json

    def __str__(self):
        """Return an engineered feature name string for the feature."""
        return _FeatureTransformersAsJSONObject.get_engineered_feature_name_from_json(
            self._entire_transformation_json_data)

    @classmethod
    def get_engineered_feature_name_from_json(cls, entire_transformation_json_data):
        """
        Return the '_' separated string representation of the engineered feature.

        :return: string having '_' separated engineered feature name
        """
        # Call helper fucntion to get the engineered feature name with the
        # final transformer name
        complete_engineered_feature_name = \
            cls._get_engineered_feature_name_from_json_internal(
                entire_transformation_json_data,
                entire_transformation_json_data[
                    _FeatureNameJSONTag.FinalTransformerName])

        # If there is value present in the json object, then append
        # it to the engineered feature name
        if entire_transformation_json_data[
                _FeatureNameJSONTag.Value] is not None:
            complete_engineered_feature_name += \
                '_' + entire_transformation_json_data[
                    _FeatureNameJSONTag.Value]

        # Return the complete string representation
        return complete_engineered_feature_name

    @classmethod
    def _get_engineered_feature_name_from_json_internal(
            cls, json_data, current_transformer_name):
        """
        Form the '_' separated string representation of the engineered feature recursively.

        :param json_data: json object for the engineered feature name
        :current_transformer_name: The current transformer name which needs to be
                                   added to the engineered feature name
        :return: string having '_' separated engineered feature name
        """
        if current_transformer_name not in json_data[
                _FeatureNameJSONTag.Transformations]:
            # The base case is when the raw feature name happens to be the
            # current transformer name. Return the current transformer name
            # as is.
            return current_transformer_name
        else:
            # Read the current transformer from the json object
            current_transformer = json_data[
                _FeatureNameJSONTag.Transformations][
                    current_transformer_name]

            input_engineered_feature_name_list = []
            for feature_name in current_transformer[_FeatureNameJSONTag.Input]:
                if feature_name is not None:
                    # Recursively get engineered feature name for this input feature
                    input_engineered_feature_name = \
                        cls._get_engineered_feature_name_from_json_internal(
                            json_data,
                            feature_name)
                    input_engineered_feature_name_list.append(
                        input_engineered_feature_name)
            engineered_feature_name = '_'.join(input_engineered_feature_name_list)

            if current_transformer[_FeatureNameJSONTag.ShouldOutput]:
                # If this transformer's transformation functions and operators
                # need to be added into the engineered feature, then
                # append them to the engineered feature name
                engineered_feature_name += '_'

                if current_transformer[
                        _FeatureNameJSONTag.Operator] is not None:
                    engineered_feature_name += \
                        current_transformer[_FeatureNameJSONTag.Operator]

                engineered_feature_name += \
                    current_transformer[
                        _FeatureNameJSONTag.TransformationFunction]

            # Return the engineered feature name
            return engineered_feature_name

    def _validate_transformation_json_object(self) -> None:
        """Validate if the JSON object has a valid schema."""
        # If the json object is None, then throw an exception
        if self._entire_transformation_json_data is None:
            raise EngineeredFeatureNamesEmptyJsonException(
                "No json object having transformations provided",
                reference_code=ReferenceCodes._ENGINEERED_FEATURE_VALIDATE_JSON_NONE_JSON,
                has_pii=False)

        # If there is no transformations key in the json object then
        # throw an exception
        if _FeatureNameJSONTag.Transformations not in \
                self._entire_transformation_json_data:
            raise EngineeredFeatureNamesNoTransformationsInJsonException(
                "No transformations found in the json object",
                reference_code=ReferenceCodes._ENGINEERED_FEATURE_VALIDATE_JSON_INVALID_TAG,
                has_pii=False)

    def is_feature_dropped(self) -> bool:
        """
        Return 'True' if a raw feature was dropped and not featurized otherwise 'False'.

        return: bool
        """
        # Check if the raw feature type is in dropped list
        return self.get_raw_feature_type() in FeatureType.DROP_SET

    def get_transformation_input_feature_name(self) -> Optional[str]:
        """
        Get the raw feature name from the JSON object.

        If the input feature list is set of input features, then concatenate them and return.
        return: str
        """
        # Validate the JSON object
        self._validate_transformation_json_object()

        # Create the first transformer name
        first_transformer_name = FeatureNamesHelper.get_transformer_name(1)
        transformations = cast(_FeatureTransformersAsJSONObject.EntireTransformationType,
                               self._entire_transformation_json_data[_FeatureNameJSONTag.Transformations])
        if first_transformer_name in transformations:
            # Join and return all the input feature names
            raw_feature_name_list = transformations[first_transformer_name][_FeatureNameJSONTag.Input]
            return '-'.join(raw_feature_name_list)
        else:
            # If there is no first transformer present return None
            return None

    def get_all_transformations_as_str(self) -> str:
        """
        Aggregate all the transformers as a '-' separated string.

        return: str
        """
        all_transformer_list = []  # type: List[str]
        for index in range(1, self._number_transformers + 1):
            # Get the name for the current transformer
            current_transformer_name = FeatureNamesHelper.get_transformer_name(
                index)
            transformations = cast(_FeatureTransformersAsJSONObject.AllTransformationsType,
                                   self._entire_transformation_json_data[_FeatureNameJSONTag.Transformations])
            if current_transformer_name in transformations:
                current_transformer = cast(_FeatureTransformersAsJSONObject.AllTransformationsType,
                                           transformations[current_transformer_name])
                transformation_function = cast(str, current_transformer[
                                               _FeatureNameJSONTag.TransformationFunction])
                operator = cast(
                    str, current_transformer[_FeatureNameJSONTag.Operator])

                if current_transformer[_FeatureNameJSONTag.Operator] is None:
                    transformer_str = transformation_function
                else:
                    transformer_str = operator + transformation_function

                # Add the current transformer name to the list
                all_transformer_list.append(transformer_str)

        # Join all transformer names and return
        return '-'.join(all_transformer_list)

    def get_raw_feature_type(self) -> str:
        """
        Return a string for the type of raw feature inside the JSON object.

        :return: A string having the raw feature name (numeric, categorical etc.)
        """
        self._validate_transformation_json_object()

        # Iterate over all the transformations to find the feature type of
        # the raw feature
        transformations = cast(_FeatureTransformersAsJSONObject.EntireTransformationType,
                               self._entire_transformation_json_data[
                                   _FeatureNameJSONTag.Transformations])
        for transformer_key in transformations:
            transformer = transformations[transformer_key]

            if transformer[_FeatureNameJSONTag.FeatureType] is not None:
                if transformer[_FeatureNameJSONTag.FeatureType] not in \
                        list(FeatureType.FULL_SET):
                    # If the raw feature type is found but it is not a
                    # recognized raw feature type, then raise exception
                    raise EngineeredFeatureNamesNotSupportedFeatureTypeException(
                        cast(str, transformer[_FeatureNameJSONTag.FeatureType])
                        + " is not a supported feature type",
                        reference_code=ReferenceCodes._ENGINEERED_FEATURE_GET_RAW_FEATURETYPE_NOT_FOUND,
                        has_pii=False)

                # Return the raw feature type
                return cast(str, transformer[_FeatureNameJSONTag.FeatureType])

        # If no raw feature was found, then throw an exception
        raise EngineeredFeatureNamesNoRawFeatureTypeException(
            "No raw feature type was found in transformations json object",
            reference_code=ReferenceCodes._ENGINEERED_FEATURE_GET_RAW_FEATURETYPE_EMPTY,
            has_pii=False)


class _FeatureTransformers:
    """This class forms a JSON object from the graph of transformers."""

    def __init__(self, graph_of_transformers):
        """
        Initialize this graph serializer.

        :param graph_of_transformers:
        """
        self._graph_of_transformers = graph_of_transformers
        self._feature_as_json = _FeatureTransformersAsJSONObject()

    def encode_transformations_from_list(self) -> _FeatureTransformersAsJSONObject:
        """
        Create a JSON object from the graph of transformers.

        :return: list
        """
        # The starting transformer number
        transformer_number = 1

        # Dictionary to know parent transformer name
        transformer_name_dict = {}  # type: Dict[str, str]

        # Iterate over all the transformers in the list
        for transformer in self._graph_of_transformers:

            # Input list for inputs to the current transformer
            input_list = []
            for parent_feature in transformer._parent_feature_list:

                if isinstance(parent_feature, int):
                    # It parent feature is a number, then get the transformer
                    # name from the dictionary. This means that the transformer
                    # depends on the previous transformer.
                    transformer_name = \
                        FeatureNamesHelper.get_transformer_name(
                            int(parent_feature))

                    if transformer_name not in transformer_name_dict:
                        raise EngineeredFeatureNamesTransformerNamesNotFoundException(
                            "The transformer name " + transformer_name
                            + " not found",
                            reference_code=ReferenceCodes._ENGINEERED_FEATURE_ENCODE_TRANSFOREMER_NOT_FOUND,
                            has_pii=False)

                    # Add the input transformer name in the list
                    input_list.append(transformer_name)
                else:
                    # This is the case for raw feature name
                    input_list.append(parent_feature)

            self._feature_as_json._add_transformer_to_json(
                input_list, transformer._transformation_function,
                transformer._operator, transformer._feature_type,
                transformer._should_output, transformer._transformer_params)

            # Get the name for the current transformer
            current_transformer_name = \
                FeatureNamesHelper.get_transformer_name(
                    transformer_number)

            # Add the current transformer name
            transformer_name_dict[current_transformer_name] = \
                current_transformer_name

            # Increment the transformer number
            transformer_number += 1

        self._feature_as_json._compose_feature_transformers_as_json_obj()
        return self._feature_as_json


class _Transformer:
    """Concrete class to keep track of transformer details and operators."""

    def __init__(self, parent_feature_list=None, transformation_fnc=None,
                 operator=None, feature_type=None, should_output=None, transformer_params=None):
        self._parent_feature_list = parent_feature_list
        self._transformation_function = transformation_fnc
        self._transformer_params = transformer_params
        self._operator = operator
        self._feature_type = feature_type
        self._should_output = should_output


class DateTimeHelper:
    """Helper class for Datetime engineered feature transformations."""

    # List of all date time sub-feature names
    _datetime_sub_feature_names = ['Year',
                                   'Month',
                                   'Day',
                                   'DayOfWeek',
                                   'DayOfYear',
                                   'QuarterOfYear',
                                   'WeekOfMonth',
                                   'Hour',
                                   'Minute',
                                   'Second']

    @classmethod
    def get_datetime_transformation_name(cls, index):
        """
        Return the date time sub-feature given an index value.

        param index: An index value which can reference the list elements of
                     _datetime_sub_feature_names
        return: string for the date time sub-feature
        """
        if index < 0 or index >= len(cls._datetime_sub_feature_names):
            raise EngineeredFeatureNamesUnsupportedIndexException(
                "Unsupported index passed for datetime sub-featuere",
                reference_code=ReferenceCodes._ENGINEERED_FEATURE_DATETIME_UNSUPPORTED_INDEX,
                has_pii=False)

        return cls._datetime_sub_feature_names[index]


class _TransformerParamsHelper:
    """Helper class to get params for transformers."""

    @staticmethod
    def _imputer_to_dict(imputer: SimpleImputer) -> Dict[str, Any]:
        dct = imputer.get_params()  # type: Dict[str, Any]
        return dct

    @staticmethod
    def _minibatchkmeans_to_dict(minibatchkmeans: MiniBatchKMeans) -> Dict[str, Any]:
        dct = minibatchkmeans.get_params()  # type: Dict[str, Any]
        dct.pop('init')
        return dct

    @staticmethod
    def _maxabsscaler_to_dict(maxabsscaler: MaxAbsScaler) -> Dict[str, Any]:
        dct = maxabsscaler.get_params()  # type: Dict[str, Any]
        return dct

    @staticmethod
    def _count_vectorizer_to_dict(count_vectorizer: CountVectorizer) -> Dict[str, Any]:
        dct = count_vectorizer.get_params()  # type: Dict[str, Any]
        if not isinstance(dct['analyzer'], str):
            dct.pop('analyzer')
        dct.pop('preprocessor')
        dct.pop('tokenizer')
        dct.pop('dtype')
        return dct

    @staticmethod
    def _tfidf_vectorizer_to_dict(tfidf_vectorizer: TfidfVectorizer) -> Dict[str, Any]:
        dct = tfidf_vectorizer.get_params()  # type: Dict[str, Any]
        if not isinstance(dct['analyzer'], str):
            dct.pop('analyzer')
        dct.pop('preprocessor')
        dct.pop('tokenizer')
        dct.pop('dtype')
        return dct

    @classmethod
    def to_dict(cls, transformer):
        """
        Convert transformer to a serializable dict.

        :param cls:
        :param transformer: A transformer object.
        :return: a dict of transformer.
        """
        transformer_function_dict = {
            SimpleImputer.__name__: cls._imputer_to_dict,
            MiniBatchKMeans.__name__: cls._minibatchkmeans_to_dict,
            MaxAbsScaler.__name__: cls._maxabsscaler_to_dict,
            CountVectorizer.__name__: cls._count_vectorizer_to_dict,
            TfidfVectorizer.__name__: cls._tfidf_vectorizer_to_dict
        }

        if transformer.__class__.__name__ in transformer_function_dict:
            return transformer_function_dict[transformer.__class__.__name__](transformer)
        elif hasattr(transformer, '_to_dict'):
            try:
                return transformer._to_dict()['kwargs']
            except Exception:
                return None
        else:
            return None


class _FeatureNameJSONTag:
    """Class for JSON tags for engineered feature names."""

    Input = 'Input'
    TransformationFunction = 'TransformationFunction'
    Transformations = 'Transformations'
    Operator = 'Operator'
    FeatureType = 'FeatureType'
    ShouldOutput = 'ShouldOutput'
    Value = 'Value'
    FinalTransformerName = 'FinalTransformerName'
    TransformationParams = 'TransformationParams'

    FULL_SET = {Input,
                TransformationFunction,
                Transformations,
                Operator, FeatureType, ShouldOutput,
                Value, FinalTransformerName}


class _MiscConstants:
    """Class for storing the miscellaneous constants."""

    Transformer = 'Transformer'


class _RawFeatureSummaryConstants:
    """Class for storing raw feature summary constants."""

    # Contants
    Transformations = 'Transformations'
    EngineeredFeatureCount = 'EngineeredFeatureCount'
    RawFeatureName = 'RawFeatureName'
    TypeDetected = 'TypeDetected'
    Dropped = 'Dropped'
    TransformationParams = 'TransformationParams'


class _RawFeatureSummary:
    """
    Class to capture the featurization summary for a raw feature.

    This captures the following:-
        - Raw feature name
        - Number of engineered features formed out of this raw feature
        - Type detected
        - If feature was dropped
        - List of feature transformations for the raw feature
    """

    def __init__(self, raw_feature_name: str, type_detected: FeatureType, if_dropped: bool) -> None:
        self._raw_feature_name = raw_feature_name
        self._type_detected = type_detected
        self._if_dropped = if_dropped
        self._num_engineered_features = 0
        self._transformations = []  # type: List[str]
        self._transformation_params = None  # type: Optional[Dict[str, Any]]

    def set_num_engineered_features(self, num_engineered_features: int) -> None:
        self._num_engineered_features = num_engineered_features

    def set_transformation_params(self, transformation_params: Optional[Dict[str, Any]] = None) -> None:
        self._transformation_params = transformation_params

    def inc_num_engineered_features(self) -> None:
        self._num_engineered_features += 1

    def append_transformation(self, transformation: str) -> None:
        self._transformations.append(transformation)

    def to_user_friendly_repr(self, include_transformation_params: bool = False) -> Dict[str, Optional[Any]]:
        raw_feature_summary_dict = {
            _RawFeatureSummaryConstants.RawFeatureName: self._raw_feature_name,
            _RawFeatureSummaryConstants.TypeDetected: self._type_detected,
            _RawFeatureSummaryConstants.Dropped: 'Yes' if self._if_dropped else 'No',
            _RawFeatureSummaryConstants.EngineeredFeatureCount: self._num_engineered_features,
            _RawFeatureSummaryConstants.Transformations: self._transformations}
        if include_transformation_params:
            raw_feature_summary_dict[_RawFeatureSummaryConstants.TransformationParams] = self._transformation_params
        return raw_feature_summary_dict


class _RawFeatureFeaturizationInfo:
    """
    Expose the following information for white-boxing AutoML featurization.

    - Raw feature name
    - Number of engineered features formed out of this raw feature
    - Type detected
    - If feature was dropped
    - List of feature transformations for the raw feature

    The following schema design is used for storing information to white-box featurization:-
    {
        "FeatureName": string,
        "TypeDetected": string,
        'EngineeredFeatureCount': integer,
        "Dropped": string,
        "Transformations": List of transformations as string
    }
    """

    @classmethod
    def get_coalesced_raw_feature_featurization_mapping(
            cls, raw_feature_featurization_dict: Dict[str, Any],
            engineered_feature_name_json_dict: Optional[Any] = None) -> List[_RawFeatureSummary]:
        """
        Return a summary for raw feature names as per the class description.

        :param raw_feature_featurization_dict: Execution plan for individual raw features as JSON object
        :param engineered_feature_name_json_dict: Engineered feature names as JSON objects
        :return: Featurization summary for the input features
        """
        coalesced_raw_feature_featurization_dict = \
            cls.get_coalesced_raw_feature_featurization_mapping_internal(
                raw_feature_featurization_dict,
                engineered_feature_name_json_dict)

        coalesced_raw_feature_featurization_list = []
        for coalesced_raw_feature_summary in coalesced_raw_feature_featurization_dict.values():
            coalesced_raw_feature_featurization_list.append(coalesced_raw_feature_summary)

        return cast(List[_RawFeatureSummary], coalesced_raw_feature_featurization_list)

    @classmethod
    def get_coalesced_raw_feature_featurization_mapping_internal(
            cls, raw_feature_featurization_dict: Dict[str, Any],
            engineered_feature_name_json_dict: Optional[Any] = None) -> Dict[str, Optional[Any]]:
        """
        Return a summary for raw feature names as per the class description.

        :param raw_feature_featurization_dict: Execution plan for individual raw features as JSON object
        :param engineered_feature_name_json_dict: Engineered feature names as JSON objects
        :return: Featurization summary for the input features
        """
        temp_summary = dict()  # type: Dict[str, Optional[Any]]
        num_engineered_feature_per_raw_feature = None

        # If engineered feature names as JSON objects are available, create the summary of number
        # of engineered features per raw feature
        if engineered_feature_name_json_dict is not None:
            num_engineered_feature_per_raw_feature = cls.create_raw_features_num_engineered_features_mapping(
                engineered_feature_name_json_dict)

        # Walk all the execution plan for the raw features
        for raw_feature_transformation_info in raw_feature_featurization_dict.values():

            # Get the raw feature name
            raw_feature_name = raw_feature_transformation_info.get_transformation_input_feature_name()

            if raw_feature_name is None:
                continue

            if raw_feature_name in temp_summary:
                # If raw feature is already seen, then add the transformation summary
                coalesced_raw_feature_featurization_mapping = cast(_RawFeatureSummary,
                                                                   temp_summary[raw_feature_name])

                # Get the transformation summary
                coalesced_raw_feature_featurization_mapping.append_transformation(
                    raw_feature_transformation_info.get_all_transformations_as_str())

                if num_engineered_feature_per_raw_feature is None:
                    # If engineered names aren't available like in case of time series, update the
                    # count of number of engineered features seen for this raw feature
                    coalesced_raw_feature_featurization_mapping.inc_num_engineered_features()
            else:
                # Create a new dictionary entry and populate it
                coalesced_raw_feature_featurization_mapping = _RawFeatureSummary(
                    raw_feature_name, raw_feature_transformation_info.get_raw_feature_type(),
                    raw_feature_transformation_info.is_feature_dropped())

                num_engineered_features = 0
                if num_engineered_feature_per_raw_feature is not None:
                    # If the engineered names are available, then look up the number engineered feature from
                    # the pre-computed stats
                    if num_engineered_feature_per_raw_feature.get(raw_feature_name) is not None:
                        num_engineered_features = num_engineered_feature_per_raw_feature.get(
                            raw_feature_name, 0)
                    else:
                        # If the stat summary doesn't exists, then set the engineered feature count
                        # to zero
                        num_engineered_features = 0
                else:
                    num_engineered_features = 1
                coalesced_raw_feature_featurization_mapping.set_num_engineered_features(num_engineered_features)
                # Get the transformation summary
                coalesced_raw_feature_featurization_mapping.append_transformation(
                    raw_feature_transformation_info.get_all_transformations_as_str())
                coalesced_raw_feature_featurization_mapping.set_transformation_params(
                    raw_feature_transformation_info._transformer_as_json)

                temp_summary[raw_feature_name] = coalesced_raw_feature_featurization_mapping

        return temp_summary

    @classmethod
    def create_raw_features_num_engineered_features_mapping(
            cls, engineered_feature_name_json_dict: Any) -> Dict[str, int]:
        """
        Return a summary of number of engineered features create out of a raw feature.

        Takes a list of JSON objects for engineered feature names and returns a dictionary containing the
        raw feature name and the number of engineered feature names generated out of the raw feature.
        :param engineered_feature_name_json_dict: List of engineered feature names as JSON objects
        :return: Dictionary containing the summary of raw feature name and the number of engineered
                 features generated out of it.
        """
        raw_features_num_engineered_features_count = defaultdict(
            int)  # type: Dict[str, int]
        for engineered_feature_json in engineered_feature_name_json_dict.values():
            first_transformer_name = FeatureNamesHelper.get_transformer_name(1)
            if first_transformer_name in engineered_feature_json[_FeatureNameJSONTag.Transformations]:
                for raw_feature_name in engineered_feature_json[_FeatureNameJSONTag.Transformations][
                        first_transformer_name][_FeatureNameJSONTag.Input]:
                    # Sum all the engineered feature names that were generated out this raw features.
                    raw_features_num_engineered_features_count[raw_feature_name] += 1

        return raw_features_num_engineered_features_count
