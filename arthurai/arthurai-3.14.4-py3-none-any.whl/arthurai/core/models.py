import json
import logging
import re
import shutil
import sys
from datetime import datetime
from http import HTTPStatus
import json
import shutil
import os
from matplotlib.pyplot import get
import shortuuid
import numpy as np
import pyarrow.parquet as pq
import pytz

from arthurai.common.constants import API_PREFIX
import shortuuid
from arthurai import util as arthur_util
from arthurai.client.http.requests import HTTPClient
from arthurai.client import validation
from arthurai.common.constants import Stage, InputType, OutputType, ValueType, TextDelimiter, Enrichment, \
    ImageResponseType, IMAGE_FILE_EXTENSION_MAP, AccuracyMetric
from arthurai.common.exceptions import MethodNotApplicableError, MissingParameterError, UserValueError, \
    UserTypeError, ArthurUserError, ExpectedParameterNotFoundError, arthur_excepted, InternalTypeError
from arthurai.core import inferences as inferences_util
from arthurai.core import util as core_util
from arthurai.core.alerts import Alert, AlertStatus, AlertRule, AlertRuleSeverity, AlertRuleBound, MetricType, Metric
from arthurai.core.attributes import ArthurAttribute, AttributeCategory, AttributeBin
from arthurai.core.base import ArthurBaseJsonDataclass, NumberType

from arthurai.core.data_service import DatasetService, ImageZipper
from arthurai.core.inferences import FALSE_DEFAULT_IGNORE_JOIN_ERRORS
from arthurai.core.util import update_column_in_list_of_dicts
from arthurai.core.viz.visualizer import DataVisualizer
from arthurai.explainability.explanation_packager import ExplanationPackager
from arthurai.version import __version__
from dataclasses import dataclass, InitVar
from pandas import DataFrame, Series, CategoricalDtype, isna
from typing import Optional, Union, List, Dict, Any, Sequence
from arthurai.core.bias.bias_wrapper import ArthurBiasWrapper

logger = logging.getLogger(__name__)

INFERENCE_DATA_RETRIES = 3


@dataclass
class ExplainabilityParameters(ArthurBaseJsonDataclass):
    enabled: bool
    explanation_algo: Optional[str] = None
    model_server_cpu: Optional[str] = None
    model_server_memory: Optional[str] = None
    explanation_nsamples: Optional[int] = None


@dataclass
class ArthurModel(ArthurBaseJsonDataclass):
    """
    Arthur Model class represents the metadata which represents a registered model in the application

    :param client: :class:`arthurai.client.Client` object which manages data storage
    :param partner_model_id: Client provided unique id to associate with the model. This field must be unique across
                             all active models cannot be changed once set.
    :param input_type: :class:`arthurai.common.constants.InputType` representing the model's input data type.
    :param output_type: :class:`arthurai.common.constants.InputType` representing the model's output data format.
    :param explainability:  :class:`arthurai.core.models.ExplainabilityParameters` object representing parameters that
                            will be used to create inference explanations.
    :param id: The auto-generated unique UUID for the model. Will be overwritten if set by the user.
    :param display_name: An optional display name for the model.
    :param description: Optional description of the model.
    :param is_batch: Boolean value to determine whether the model sends inferences in batch or streaming format.
                     Defaults to False.
    :param archived: Indicates whether or not a model has been archived, defaults to false.
    :param created_at: UTC timestamp in ISO8601 format of when the model was created. Will be overwritten if set by the
                       user.
    :param updated_at: UTC timestamp in ISO8601 format of when the model was last updated. Will be overwritten if set by
                       the user.
    :param attributes: List of :class:`arthurai.core.attributes.ArthurAttribute` objects registered to the model
    :param tags: List of string keywords to associate with the model.
    :param classifier_thresholds: Threshold value for classification models, default is 0.5.
    :param text_delimiter: Only valid for models with input_type equal to
                           :py:attr:`arthurai.common.constants.InputType.NLP`. Represents the text delimiter
                           to divide input strings.
    :param expected_throughput_gb_per_day: Expected amount of throughput.
    :param pixel_height: Only valid for models with input_type equal to
                           :py:attr:`arthurai.common.constants.InputType.Image`. Expected image height in pixels.
    :param pixel_width: Only valid for models with input_type equal to
                           :py:attr:`arthurai.common.constants.InputType.Image`. Expected image width in pixels.
    """

    partner_model_id: str
    input_type: InputType
    output_type: OutputType
    # This is just used during init and will not be associated with
    # an instance of this class, instead reference ArthurModel._client
    client: InitVar[Optional[HTTPClient]] = None
    explainability: Optional[ExplainabilityParameters] = None
    id: Optional[str] = None
    display_name: Optional[str] = None
    description: Optional[str] = None
    is_batch: bool = False
    archived: bool = False
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    attributes: Optional[List[ArthurAttribute]] = None
    tags: Optional[List[str]] = None
    classifier_threshold: Optional[float] = None
    text_delimiter: Optional[TextDelimiter] = None
    expected_throughput_gb_per_day: Optional[int] = None
    pixel_height: Optional[int] = None
    pixel_width: Optional[int] = None
    image_class_labels: Optional[List[str]] = None
    reference_dataframe: Optional[DataFrame] = None

    # from model utils
    from arthurai.core.model_utils import check_attr_is_bias, check_has_bias_attrs, get_positive_predicted_class

    def __post_init__(self, client: HTTPClient):
        # variables created here will only be accessible directly on the object itself, they will not be in the result
        # of object.to_dict() even if marked as public (does not have preceding underscore)
        self._client = client
        self._explainer: Optional[ExplanationPackager] = None
        self.viz = DataVisualizer([self])
        self.attributes_type_dict = {}
        if self.attributes:
            for attr in self.attributes:
                self.attributes_type_dict[attr.name] = attr.value_type
        self.bias = ArthurBiasWrapper(self)
        self._store_model_id_in_env()

    def __str__(self):
        return str(self.to_dict())

    @arthur_excepted("failed to save model")
    def save(self) -> str:
        """Check and save this model.  Sets and returns the ID on successful upload.

        :return: The model id

        :raise: Exception: the model has already been saved
        :raise: ArthurUserError: failed due to user error
        :raise: ArthurInternalError: failed due to an internal error
        """
        # if the model has not been set yet
        if self.id is not None:
            raise MethodNotApplicableError("Cannot save a registered model; use update instead.")

        self._check_model_valid()

        if self.display_name is None:
            self.display_name = self.partner_model_id

        data = self.to_dict()
        data.pop("reference_dataframe", None)
        resp = self._client.post("/models", json=data, return_raw_response=True,
                                 validation_response_code=HTTPStatus.CREATED)
        if 'id' not in resp.json():
            raise ExpectedParameterNotFoundError(f"An error occurred: {resp}, {resp.status_code}, {resp.content}")

        # update fields with response from API
        self.id = resp.json()['id']
        self._store_model_id_in_env()

        # TODO: if explainability is enabled send resources

        # set reference data if it's waiting to be sent
        if self.reference_dataframe is not None:
            self.set_reference_data(data=self.reference_dataframe)
            # don't need to keep it around anymore
            self.reference_dataframe = None

        return self.id  # type: ignore

    def _check_model_valid(self) -> bool:
        """Check the validity of the model before saving, and prints out any errors it finds.

        (As time passes we can add more to this function to enforce more requirements.)

        :return: True if the model is valid, False otherwise.
        """

        # has attributes
        if self.attributes is None:
            # future enhancement, attributes should be initialized to empty not None
            raise InternalTypeError("attributes is None")
        if len(self.attributes) == 0:
            raise MissingParameterError("must add attributes to model before saving; see below for requirements.")

        # contains ground truth, input, and predicted attributes
        contains_gt = False
        contains_pred = False
        contains_ipt = False
        for attr in self.attributes:
            if attr.stage == Stage.GroundTruth:
                contains_gt = True
            if attr.stage == Stage.PredictedValue:
                contains_pred = True
            if attr.stage == Stage.ModelPipelineInput or attr.stage == Stage.PredictFunctionInput:
                contains_ipt = True
        if not contains_gt:
            raise MissingParameterError("does not contain any attribute with Stage.GroundTruth.")
        if not contains_pred:
            raise MissingParameterError("does not contain any attribute with Stage.PredictedValue.")
        if not contains_ipt:
            raise MissingParameterError(
                "does not have any attribute with Stage.ModelPipelineInput or Stage.PredictFunctionInput.")

        # for binary models, need one predicted attribute to be positive
        predicted_value_attributes = self.get_attributes(stage=Stage.PredictedValue)
        if len(predicted_value_attributes) == 2 and self.output_type == OutputType.Multiclass:  # is binary model
            has_pos_pred = False
            for pred in predicted_value_attributes:
                if pred.is_positive_predicted_attribute:
                    has_pos_pred = True
            if not has_pos_pred:
                raise MethodNotApplicableError("binary models must have a positive predicted attribute; use "
                                               "add_binary_classifier_output_attributes instead.")

        return True

    @arthur_excepted("failed to update model")
    def update(self):
        """Update the the current model object

        :raise: ArthurUserError: failed due to user error
        :raise: ArthurInternalError: failed due to an internal error
        """
        if self.id is None:
            raise MethodNotApplicableError(
                "Model has not been created yet, use save() to instantiate this model object")

        data = self.to_dict()
        resp = self._client.put(f"/models/{self.id}", json=data, return_raw_response=True,
                                validation_response_code=HTTPStatus.OK)

    @staticmethod
    def _get_attribute_data(value_type: ValueType, attribute_data_series: Series) -> Dict:
        """Generates metadata about a specific attribute based on a supplied dataframe

        :param value_type:                          DataType of the values in the series
        :param attribute_data_series:              Pandas Series of data for the specific attribute
        :return: Dictionary of attribute metadata and values inferred from the pandas series
        """
        if attribute_data_series.isnull().any():
            raise UserValueError("Column contains null value. Null values are not supported in reference or "
                                 f"inference data, please replace before proceeding.")

        cnt_distinct = len(attribute_data_series.unique())
        unique = cnt_distinct == len(attribute_data_series) and cnt_distinct > 10
        attribute_data: Dict[str, Optional[Any]] = {'is_unique': unique}

        categorical = False
        if value_type == ValueType.Timestamp:
            categorical = False

        elif (value_type == ValueType.Float and
              cnt_distinct == 2 and
              attribute_data_series.max() == 1 and
              attribute_data_series.min() == 0):
            # exactly [0.0, 1.0]
            categorical = True

        elif value_type == ValueType.Float:
            categorical = False
        elif value_type == ValueType.Integer and cnt_distinct <= 20:
            categorical = True
        elif value_type == ValueType.Integer:
            categorical = False
        elif value_type == ValueType.Unstructured_Text:
            categorical = True
        elif value_type == ValueType.Image:
            categorical = False
        else:
            categorical = True

        # even if unstructured text attributes aren't unique, we don't want categories
        if categorical and not attribute_data["is_unique"] and not value_type == ValueType.Unstructured_Text:
            attribute_data["categories"] = [AttributeCategory(value=str(cat)) for cat in
                                            list(set(attribute_data_series))]
        # if not categorical, and numerical, set min/max
        elif not categorical and value_type in [ValueType.Float, ValueType.Integer, ValueType.Boolean]:
            attribute_data["min_range"] = core_util.NumpyEncoder.convert_value(attribute_data_series.min())
            attribute_data["max_range"] = core_util.NumpyEncoder.convert_value(attribute_data_series.max())

        attribute_data["categorical"] = categorical

        return attribute_data

    def _to_arthur_dtype(self, dtype: str, series: Series, stage: Stage) -> Optional[ValueType]:
        """Select an :py:class:`.DataType` based on a pandas dtype

        :param dtype: the pandas dtype
        :param series: the Series to infer values for
        :return: The :py:class:`.DataType` corresponding to the pandas dtype
        """
    
        # in case of someone sending all nulls in a column, you can end up with empty series
        # handle example val of none, will not be able to distinguish between string or list, but should be edge case
        # and passing lists isn't expected, but we should handle most cases
        example_val = series.iloc[0] if len(series) > 0 else None

        if dtype in ["string", "object"] and (isinstance(example_val, str) or example_val is None):
            if self.input_type == InputType.Image and stage == Stage.ModelPipelineInput:
                return ValueType.Image
            else:
                return ValueType.String
        elif dtype == "category":  # the pandas "category" dtype will fail the "isinstance" check above
            cat_dtype = series.dtype
            if isinstance(cat_dtype, CategoricalDtype):
                return self._to_arthur_dtype(dtype=cat_dtype.categories.dtype.name, series=series, stage=stage)
            else:
                # should never happen but satisfies type checker
                raise TypeError(f"Pandas dtype was 'categorical' but data tyep was not a pd.Categorical")

        elif dtype in ["bool", "boolean"]:
            return ValueType.Boolean
        elif re.search("u?int*", dtype, flags=re.I) or re.search("u?Int*", dtype, flags=re.I):
            return ValueType.Integer
        elif re.search("float*", dtype, flags=re.I):
            return ValueType.Float
        elif re.search("(datetime|timestamp).*", dtype, flags=re.I):
            return ValueType.Timestamp
        else:
            return None

    def _get_pred_value_type(self, data: DataFrame, pred_to_ground_truth_map: Dict[str, str]) -> ValueType:
        """
        Infer the Prediction Value Type for a Regression model based on a sample dataset and prediction to ground truth
        map.
        :param data:
        :param pred_to_ground_truth_map:
        :return:
        """
        if len(pred_to_ground_truth_map) == 0:
            raise UserValueError("pred_to_ground_truth_map cannot be empty")
        value_types = set()
        for col_name in pred_to_ground_truth_map.keys():
            cur_col = data[col_name]
            cur_value_type = self._to_arthur_dtype(cur_col.dtype.name, cur_col, stage=Stage.PredictedValue)
            if cur_value_type is None:
                raise UserValueError(f"Cannot infer Arthur value type from Pandas dtype {cur_col.dtype.name} for "
                                     f"column {col_name}")
            value_types.add(cur_value_type)
        if len(value_types) > 1:
            raise UserValueError(f"Cannot have multiple prediction output columns with different datatypes! Got "
                                 f"types: {', '.join([str(v) for v in value_types])}")

        return value_types.pop()

    @arthur_excepted("failed to parse dataframe")
    def from_dataframe(self, data: Union[DataFrame, Series], stage: Stage) -> None:
        """Auto-generate attributes based on input data.

        .. deprecated:: 3.12.0
            Please use :func:`ArthurModel.infer_schema()` to add fields from a DataFrame to a model.

        Note that this does *not* automatically set reference
        data; this method only reads the passed-in data, and then infers attribute names, types, etc. and sets them up
        within the ArthurModel.

        .. seealso::
            To also set your data as reference data, see :func:`ArthurModel.build()`

        For PredictedValue and GroundTruth stages, use the correct `add_<modeltype>_output_attributes()` method instead.

        :param data: the data to infer attribute metadata from
        :param stage: :py:class:`.Stage` of the data
        :return: a DataFrame summarizing the inferred types
        :raise: ArthurUserError: failed due to user error
        :raise: ArthurInternalError: failed due to an internal error
        """
        return self.infer_schema(data=data, stage=stage)

    @arthur_excepted("failed to infer schema from DataFrame")
    def infer_schema(self, data: Union[DataFrame, Series], stage: Stage) -> None:
        """Auto-generate attributes based on input data.

        Note that this does *not* automatically set reference
        data; this method only reads the passed-in data, and then infers attribute names, types, etc. and sets them up
        within the ArthurModel.

        .. seealso::
            To also set your data as reference data, see :func:`ArthurModel.set_reference_data()`.

            To infer schemas for all stages and set reference data in a single call, see :func:`ArthurModel.build()`.

        For PredictedValue and GroundTruth stages, use the correct `add_<modeltype>_output_attributes()` method instead.

        :param data: the data to infer attribute metadata from
        :param stage: :py:class:`.Stage` of the data
        :return: a DataFrame summarizing the inferred types
        :raise: ArthurUserError: failed due to user error
        :raise: ArthurInternalError: failed due to an internal error
        """

        if stage == Stage.PredictedValue or stage == Stage.GroundTruth:
            raise MethodNotApplicableError("Use either add_regression_output_attributes(), "
                                           "add_multiclass_classifier_output_attributes(), "
                                           "add_binary_classifier_output_attributes(), "
                                           "or add_object_detection_output_attributes() to add output attributes.")

        if isinstance(data, DataFrame):
            df = data
        elif isinstance(data, Series):
            df = data.to_frame()
        else:
            raise UserTypeError("Unsupported data type: a pandas.DataFrame or pandas.Series is required")

        if len(df) == 0:
            raise UserValueError("Dataframe must have at least 1 row of data")

        found_categorical = False

        preferred_positions = self._generate_attr_positions(stage=stage,
                                                            preferred_positions=list(range(len(df.columns))))
        for i, column in enumerate(df.columns):

            series = core_util.standardize_pd_obj(df[column], dropna=True, replacedatetime=False,
                                                  attributes=self.attributes_type_dict)
            value_type = self._to_arthur_dtype(series.dtype.name, series, stage=stage)
            # handle unknown datatype
            if value_type is None:
                logger.warning(f"Cannot parse type {series.dtype.name} for column {column}. Not including in schema. "
                               f"Valid types are: str, int, float, datetime, timestamp, bool. To manually add an "
                               f"attribute use model.add_attribute(). Run help(model.add_attribute) for full "
                               f"documentation.")
                continue

            try:
                attribute_data = self._get_attribute_data(value_type, series)
            except ArthurUserError as e:
                raise ArthurUserError(f"Error in column: {column}: {str(e)}")

            if value_type == ValueType.String and self.input_type == InputType.NLP:
                value_type = ValueType.Unstructured_Text
                # even if unstructured text attributes are not unique we don't want to store categories
                attribute_data['categories'] = None

            if value_type == ValueType.Image:
                # even if image attributes are not unique we don't want to store categories
                attribute_data['categories'] = None

            if attribute_data['categorical'] and value_type != ValueType.Unstructured_Text:
                found_categorical = True

            attribute_data["position"] = preferred_positions[i]
            arthur_attribute = ArthurAttribute(
                name=column,
                stage=stage,
                value_type=value_type,
                **attribute_data
            )
            self._add_attribute_to_model(arthur_attribute)
        if found_categorical:
            logger.warning(f"Found one or more categorical attributes. It is suggested to use model.review() to "
                           "verify all possible categories were inferred correctly for each categorical attribute. "
                           "To update with new categories, use model.get_attribute(attr_name).set(categories=[cat_1, "
                           "cat_2, cat_3])")

    def build(self, data: DataFrame, pred_to_ground_truth_map: Dict[str, str],
              positive_predicted_attr: Optional[str] = None, non_input_columns: List[str] = None,
              set_reference_data=True) -> DataFrame:
        """
        Build a model from a reference DataFrame, inferring the attribute metadata and registering the reference data
        to be stored with Arthur. Note that this will remove any previously existing attributes.

        Combines calls to :func:`ArthurModel.infer_schema()` and (if `set_reference_data` is True)
        :func:`ArthurModel.set_reference_data()`
        :param data: a reference DataFrame to build the model from
        :param pred_to_ground_truth_map: a mapping from predicted column names to their corresponding ground truth
            column names
        :param positive_predicted_attr: name of the predicted attribute to register as the positive predicted
            attribute
        :param non_input_columns: list of columns that contain auxiliary data not directly passed into the model
        :param set_reference_data: if True, register the provided DataFrame as the model's reference dataset
        :return: a DataFrame summarizing the inferred types
        """
        if non_input_columns is None:
            non_input_columns = []

        if self.model_is_saved():
            raise MethodNotApplicableError("Model is already built and saved!")

        # do some initial validation to ensure columns match
        for col in non_input_columns:
            if col not in data.columns:
                raise UserValueError(f"Non Input Column '{col}' not in DataFrame")
        for col in pred_to_ground_truth_map.keys():
            if col not in data.columns:
                raise UserValueError(f"Prediction Column '{col}' not in DataFrame")
        for col in pred_to_ground_truth_map.values():
            if col not in data.columns:
                raise UserValueError(f"Ground Truth Column '{col}' not in DataFrame")

        # clear current attributes
        self.attributes = []

        # infer schema, filtering out prediction and ground truth columns
        input_cols = [col for col in data.columns if
                      (col not in pred_to_ground_truth_map.keys()) and
                      (col not in pred_to_ground_truth_map.values()) and
                      (col not in non_input_columns)]
        self.infer_schema(data=data[input_cols], stage=Stage.ModelPipelineInput)
        self.infer_schema(data=data[non_input_columns], stage=Stage.NonInputData)

        # add prediction and ground truth columns
        if self.output_type == OutputType.Multiclass:
            if len(pred_to_ground_truth_map) == 2:
                if positive_predicted_attr is None:
                    pred_classes = list(pred_to_ground_truth_map.keys())
                    raise UserTypeError(f"Binary Classifiers require 'positive_predicted_class' parameter. Please "
                                        f"add this parameter (possible values: '{pred_classes[0]}' or "
                                        f"'{pred_classes[1]}')")
                self.add_binary_classifier_output_attributes(positive_predicted_attr=positive_predicted_attr,
                                                             pred_to_ground_truth_map=pred_to_ground_truth_map)
            else:
                self.add_multiclass_classifier_output_attributes(pred_to_ground_truth_map=pred_to_ground_truth_map)
        elif self.output_type == OutputType.Regression:
            pred_value_type = self._get_pred_value_type(data, pred_to_ground_truth_map)
            self.add_regression_output_attributes(pred_to_ground_truth_map=pred_to_ground_truth_map,
                                                  value_type=pred_value_type)
        else:
            # future enhancement: make this method work for object detection models
            #  this will require accepting output class labels, which is generally a decent thing to do but is probably
            #  best included with adding multilabel support to not pollute our API with CV-specific parameters
            raise MethodNotApplicableError(f"Cannot use build() method for models with output type {self.output_type}")

        # set reference data
        if set_reference_data:
            self.set_reference_data(data=data)

        # review
        logger.info("Please review the inferred schema. If everything looks correct, lock in your model by calling "
                    "arthur_model.save()")
        return self.review()

    def _add_attribute_to_model(self, attribute: ArthurAttribute) -> ArthurAttribute:
        """Adds an already-made ArthurAttribute to the model.

        :param attribute: ArthurAttribute Object to add to the model
        :return: ArthurAttribute Object
        """
        if self.attributes is None:
            self.attributes = [attribute]
        else:
            self.attributes.append(attribute)

        self.attributes_type_dict[attribute.name] = attribute.value_type

        return attribute

    def _generate_attr_positions(self, stage: Stage, preferred_positions: List[int]) -> List[int]:
        """
        Given a list of preferred attribute positions, generate actual positions if the preferred indices are not
        available in the current stage
        :param stage:
        :param preferred_positions:
        :return:
        """
        cur_attr_positions = set()
        if self.attributes is not None:
            for attr in self.attributes:
                if attr.stage == stage and attr.position is not None:
                    cur_attr_positions.add(attr.position)

        actual_positions = []
        for pref_pos in preferred_positions:
            if pref_pos not in cur_attr_positions:
                position = pref_pos
            else:
                position = max(cur_attr_positions) + 1
            actual_positions.append(position)
            cur_attr_positions.add(position)
        return actual_positions

    @arthur_excepted("failed to add attribute")
    def add_attribute(self,
                      name: Optional[str] = None,
                      value_type: Optional[ValueType] = None,
                      stage: Optional[Stage] = None,
                      label: Optional[str] = None,
                      position: Optional[int] = None,
                      categorical: bool = False,
                      min_range: Optional[Union[float, int]] = None,
                      max_range: Optional[Union[float, int]] = None,
                      monitor_for_bias: bool = False,
                      categories: Optional[List[Union[str, AttributeCategory]]] = None,
                      bins: Optional[List[Union[NumberType, AttributeBin]]] = None,
                      is_unique: bool = False,
                      is_positive_predicted_attribute: bool = False,
                      attribute_link: Optional[str] = None,
                      arthur_attribute: Optional[ArthurAttribute] = None,
                      gt_pred_attrs_map: Optional[Dict] = None) -> List[ArthurAttribute]:
        """Adds a new attribute to the model and returns the attribute.

        Also validates that Stage is not PredictedValue or GroundTruth. Additionally, attribute names must contain
        only letters, numbers, and underscores, and cannot begin with a number.

        :param attribute_link: Only applicable for `GroundTruth` or `PredictedValue` staged attributes.
        If stage is equal to `GroundTruth`, this represents the associated `PredictedValue` attribute and vice versa
        :param is_positive_predicted_attribute: Only applicable for `PredictedValue` attributes on a Binary
        Classification model. Should be set to `True` on the positive predicted value attribute.
        :param is_unique: Boolean value used to signal if the values of this attribute are unique.
        :param bins: List of bin cut-offs used to discretize continuous attributes. Use `None` as an open ended value.
                     `[None, 18, 65, None]` represents the three following bins:
                     `value < 18, 18 < value < 65, value > 65`
        :param monitor_for_bias: boolean value set to `True` if the attribute should be monitored for bias
        :param max_range: Max value for a continuous attribute
        :param min_range: Min value for a continuous attribute
        :param categorical: Boolean value set to `True` if the attribute has categorical values.
        :param position: The array position of attribute within the stage. Required in the PREDICT_FUNCTION_INPUT stage.
        :param label: Label for attribute. If attribute has an encoded name, a more readable label can be set.
        :param stage: :class:`arthurai.common.constants.Stage` of this attribute in the model pipeline
        :param value_type: :class:`arthurai.common.constants.ValueType` associated with this attributes values
        :param name: Name of the attribute. Attribute names can only contain alpha-numeric characters and underscores
        and cannot start with a number.
        :param categories: [Only for Categorical Attributes] If the attribute is categorical, this will contain the
        attribute's categories. It is required only if the categorical flag is set to true.
        :param arthur_attribute: Optional ArthurAttribute to add to the model
        :param gt_pred_attrs_map: .. deprecated:: version 2.0.0 Use `ArthurModel.add_[model_type]_output_attributes()`
            instead

        :return: ArthurAttribute Object
        :raise: ArthurUserError: failed due to user error
        :raise: ArthurInternalError: failed due to an internal error
        """
        if arthur_attribute is None:
            if stage is None or value_type is None or name is None:
                raise MissingParameterError("At minimum stage, value_type, and name must be provided for an attribute")
            elif stage == Stage.PredictedValue or stage == Stage.GroundTruth or gt_pred_attrs_map is not None:
                raise MethodNotApplicableError("Use either add_regression_output_attributes(), "
                                               "add_multiclass_classifier_output_attributes(), "
                                               "or add_binary_classifier_output_attributes() to add output attributes.")

            if not self._validate_attribute_name(name):
                raise UserValueError("Invalid attribute name: must contain only numbers, letters, and underscores, "
                                     "and cannot start with a number.")

            # Add categories or bins if supplied
            attribute_categories = [AttributeCategory(value=c) if not isinstance(c, AttributeCategory) else c
                                    for c in categories] if categories else None

            attribute_bins: Optional[List[Any]] = None
            if bins and not isinstance(bins[0], AttributeBin):
                attribute_bins = [AttributeBin(bins[i], bins[i + 1]) for i in range(len(bins) - 1)]
            elif bins and isinstance(bins[0], AttributeBin):
                attribute_bins = bins

            attribute_to_add = ArthurAttribute(
                name=name,
                value_type=value_type,
                stage=stage,
                label=label,
                position=position,
                categorical=categorical,
                min_range=min_range,
                max_range=max_range,
                monitor_for_bias=monitor_for_bias,
                categories=attribute_categories,
                bins=attribute_bins,
                is_unique=is_unique,
                is_positive_predicted_attribute=is_positive_predicted_attribute,
                attribute_link=attribute_link
            )
            return [self._add_attribute_to_model(attribute_to_add)]

        else:
            self._validate_attribute_name(arthur_attribute.name)
            return [self._add_attribute_to_model(arthur_attribute)]

    @arthur_excepted("failed to add image attribute")
    def add_image_attribute(self, name: Optional[str] = None) -> List[ArthurAttribute]:
        """Wraps add_attribute for images

        :return: ArthurAttribute Object
        :raise: ArthurUserError: failed due to user error
        :raise: ArthurInternalError: failed due to an internal error
        """

        position = self._generate_attr_positions(Stage.ModelPipelineInput, preferred_positions=[0])[0]
        return self.add_attribute(
            name=name,
            stage=Stage.ModelPipelineInput,
            value_type=ValueType.Image,
            categorical=False,
            is_unique=True,
            position=position
        )

    @arthur_excepted("failed to fetch image")
    def get_image(self, image_id: str, save_path: str, type: ImageResponseType = ImageResponseType.RawImage) -> str:
        """Saves the image specified by image_id to a file

        :param image_id: id of image in model
        :param save_path: directory to save the downloaded image to
        :param type: type of response data

        :return: location of downloaded image file
        :raise: ArthurUserError: failed due to user error
        :raise: ArthurInternalError: failed due to an internal error
        """

        endpoint = f"/models/{self.id}/inferences/images/{image_id}"
        resp = self._client.get(endpoint, params={'type': type}, return_raw_response=True)

        # validate success response without specifying exact status code because it involves a redirect
        validation.validate_response_status(response_or_code=resp.status_code, allow_redirects=True)

        content_type = resp.headers['Content-Type']
        file_ext = IMAGE_FILE_EXTENSION_MAP.get(content_type, '')
        save_file = f"{save_path}/{type}_{image_id}{file_ext}"

        with open(save_file, 'wb') as file:
            file.write(resp.content)

        return save_file

    @arthur_excepted("failed to find image attribute")
    def get_image_attribute(self) -> ArthurAttribute:
        """Returns the attribute with value_type=Image for input_type=Image models

        :return: ArthurAttribute Object
        :raise: ArthurUserError: failed due to user error
        :raise: ArthurInternalError: failed due to an internal error
        """
        if self.attributes is None:
            raise UserValueError("No attributes have been defined on this model")

        for attr in self.attributes:
            if attr.value_type == ValueType.Image:
                return attr

        raise UserValueError("No attribute with value_type Image found")

    @staticmethod
    def _validate_attribute_name(attribute_name: str) -> bool:
        """Checks that attribute name is valid.

        :param attribute_name: name of the attribute to add to the model
        :return: boolean indicating whether the name is valid.
        """

        if bool(re.compile('\d').search(attribute_name[0])):  # \d is all the digits 0-9
            print("Attribute name cannot start with a number.")
            return False

        if bool(re.compile('\W').search(attribute_name)):  # \W is the complement of all alphanumeric characters and _.
            print("Attribute name can only contain numbers, letters, and underscores.")
            return False

        return True

    @arthur_excepted("failed to add regression output attributes")
    def add_regression_output_attributes(self, pred_to_ground_truth_map: Dict[str, str], value_type: ValueType) \
            -> Dict[str, ArthurAttribute]:
        """ Registers ground truth and predicted attribute parameters for regression models.
        This function will register two ArthurAttribute objects to the model, a predicted value attribute
        and ground truth attribute.

        :param pred_to_ground_truth_map: Map of predicted value attributes to their corresponding ground truth attribute names.
                                  The names provided in the dictionary will be used to register the one-hot encoded
                                  version of the attributes.
        :param value_type: Value type of regression model output attribute (usually either ValueType.Integer or ValueType.Float)

        :return: Mapping of added attributes string name -> ArthurAttribute Object
        :raise: ArthurUserError: failed due to user error
        :raise: ArthurInternalError: failed due to an internal error
        """
        attributes_added = {}

        preferred_positions = list(range(len(pred_to_ground_truth_map)))
        pred_attr_positions = self._generate_attr_positions(Stage.PredictedValue, preferred_positions)
        gt_attr_positions = self._generate_attr_positions(Stage.GroundTruth, preferred_positions)
        i = 0
        for pred_attr, gt_attr in pred_to_ground_truth_map.items():
            arthur_gt_attr = ArthurAttribute(
                name=gt_attr,
                stage=Stage.GroundTruth,
                value_type=value_type,
                categorical=False,
                attribute_link=pred_attr,
                position=gt_attr_positions[i]
            )
            arthur_pred_attr = ArthurAttribute(
                name=pred_attr,
                stage=Stage.PredictedValue,
                value_type=value_type,
                categorical=False,
                attribute_link=gt_attr,
                position=pred_attr_positions[i]
            )
            self._add_attribute_to_model(arthur_gt_attr)
            self._add_attribute_to_model(arthur_pred_attr)
            attributes_added[arthur_pred_attr.name] = arthur_pred_attr
            attributes_added[arthur_gt_attr.name] = arthur_gt_attr
            i += 1
        return attributes_added

    @arthur_excepted("failed to add output attributes")
    def add_multiclass_classifier_output_attributes(self, pred_to_ground_truth_map: Dict[str, str]) \
            -> Dict[str, ArthurAttribute]:
        """Registers ground truth and predicted attribute parameters. This function will create a predicted value and
        ground truth attribute for each mapping specified in pred_to_ground_truth_map.

        :param pred_to_ground_truth_map: Map of predicted value attributes to their corresponding ground truth attribute names.
                                  The names provided in the dictionary will be used to register the one-hot encoded
                                  version of the attributes. Ensure the ordering of items in this dictionary is an accurate
                                  representation of how model predictions (probability vectors) will be generated.
        :return: Mapping of added attributes string name -> ArthurAttribute Object
        :raise: ArthurUserError: failed due to user error
        :raise: ArthurInternalError: failed due to an internal error
        """

        if len(pred_to_ground_truth_map) == 2:
            raise MethodNotApplicableError(
                "To add output attributes to a multiclass model with two output attributes, use "
                "`add_binary_classifier_output_attributes`.")

        preferred_positions = list(range(len(pred_to_ground_truth_map)))
        pred_attr_positions = self._generate_attr_positions(Stage.PredictedValue, preferred_positions)
        gt_attr_positions = self._generate_attr_positions(Stage.GroundTruth, preferred_positions)
        attributes_added = {}
        for (i, (pred_attr, gt_attr)) in enumerate(pred_to_ground_truth_map.items()):
            arthur_gt_attr = ArthurAttribute(
                name=gt_attr,
                stage=Stage.GroundTruth,
                value_type=ValueType.Integer,
                categorical=True,
                categories=[AttributeCategory(value="0"), AttributeCategory(value="1")],
                attribute_link=pred_attr,
                position=gt_attr_positions[i]
            )
            arthur_pred_attr = ArthurAttribute(
                name=pred_attr,
                stage=Stage.PredictedValue,
                value_type=ValueType.Float,
                min_range=0,
                max_range=1,
                attribute_link=gt_attr,
                position=pred_attr_positions[i]
            )
            self._add_attribute_to_model(arthur_gt_attr)
            self._add_attribute_to_model(arthur_pred_attr)
            attributes_added[arthur_pred_attr.name] = arthur_pred_attr
            attributes_added[arthur_gt_attr.name] = arthur_gt_attr
        return attributes_added

    @arthur_excepted("failed to add output attributes")
    def add_binary_classifier_output_attributes(self, positive_predicted_attr: str,
                                                pred_to_ground_truth_map: Dict[str, str],
                                                threshold: float = 0.5) -> Dict[str, ArthurAttribute]:
        """Registers ground truth and predicted attribute parameters and their thresholds.

        This function will create a predicted value and ground truth attribute for each mapping specified in
        pred_to_ground_truth_map.

        For binary models, `GroundTruth` is always an integer, and `PredictedAttribute` is always a float.
        Additionally, `PredictedAttribute` is expected to be a probability (e.g. the output of a scikit-learn
        model's `predict_proba` method), rather than a classification to 0/1.

        This assumes that separate columns for predicted values and ground truth values have already been created,
        and that they have both been broken into two separate (pseudo-onehot) columns: for example, the column
        `ground_truth_label` becomes `ground_truth_label=0` and `ground_truth_label=1`, and the column `pred_prob`
        becomes `pred_prob=0` and `pred_prob=1`. The pandas function `pd.get_dummies()` can be useful for reformatting
        the ground truth column, but be sure that the datatype is specified correctly as an int.

        :param positive_predicted_attr: string name of the predicted attribute to register as the positive predicted attribute
        :param pred_to_ground_truth_map: Map of predicted value attributes to their corresponding ground truth attribute names.
                                  The names provided in the dictionary will be used to register the one-hot encoded
                                  version of the attributes. For example: `{'pred_0': 'gt_0', 'pred_1': 'gt_1'}`,
                                  Ensure the ordering of items in this dictionary is an accurate
                                  representation of how model predictions (probability vectors) will be generated.
        :param threshold: Threshold to use for the classifier model, defaults to 0.5

        :return: Mapping of added attributes string name -> ArthurAttribute Object
        :raise: ArthurUserError: failed due to user error
        :raise: ArthurInternalError: failed due to an internal error
        """
        if len(pred_to_ground_truth_map) != 2:
            raise UserValueError((f"Binary classifiers must have two output attributes, but pred_to_ground_truth_map "
                                  f"has {len(pred_to_ground_truth_map)}. To add more than two output attributes to a "
                                  f"multiclass model, use add_multiclass_classifier_output_attributes()."))
        if positive_predicted_attr not in pred_to_ground_truth_map.keys():
            raise UserValueError((f"The positive_predicted_attr must be included in the mapping "
                                  f"pred_to_ground_truth_map. positive_predicted_attr {positive_predicted_attr} not "
                                  f"found in pred_to_ground_truth_map keys: {pred_to_ground_truth_map.keys()}."))
        preferred_positions = list(range(len(pred_to_ground_truth_map)))
        pred_attr_positions = self._generate_attr_positions(Stage.PredictedValue, preferred_positions)
        gt_attr_positions = self._generate_attr_positions(Stage.GroundTruth, preferred_positions)
        attributes_added = {}
        for (i, (pred_attr, gt_attr)) in enumerate(pred_to_ground_truth_map.items()):
            is_pos_pred_attr = True if positive_predicted_attr == pred_attr else False
            arthur_gt_attr = ArthurAttribute(
                name=gt_attr,
                stage=Stage.GroundTruth,
                value_type=ValueType.Integer,
                categorical=True,
                categories=[AttributeCategory(value="0"), AttributeCategory(value="1")],
                attribute_link=pred_attr,
                position=gt_attr_positions[i]
            )
            arthur_pred_attr = ArthurAttribute(
                name=pred_attr,
                stage=Stage.PredictedValue,
                value_type=ValueType.Float,
                min_range=0,
                max_range=1,
                attribute_link=gt_attr,
                is_positive_predicted_attribute=is_pos_pred_attr,
                position=pred_attr_positions[i]
            )
            self._add_attribute_to_model(arthur_gt_attr)
            self._add_attribute_to_model(arthur_pred_attr)
            attributes_added[arthur_pred_attr.name] = arthur_pred_attr
            attributes_added[arthur_gt_attr.name] = arthur_gt_attr
        self.classifier_threshold = threshold
        return attributes_added

    @arthur_excepted("failed to add output attributes")
    def add_object_detection_output_attributes(self, predicted_attr_name: str,
                                               gt_attr_name: str,
                                               image_class_labels: List[str]) -> Dict[str, ArthurAttribute]:
        """Registers ground truth and predicted value attributes for an object detection model, as well as
        setting the image class labels.

        This function will create a predicted value attribute and ground truth attribute using the names provided,
        giving each a value type of Bounding Box. Image class labels are also set on the model object. The index
        of each label in the list should correspond to a class_id the model outputs.

        Ex: image_class_labels = ['cat', 'dog', 'person']
        So a bounding box with class_id of 0 would have label 'cat', class_id of 2 would have label 'person'

        :param predicted_attr_name: The name of the predicted value attribute
        :param gt_attr_name: The name of the ground truth attribute
        :param image_class_labels: The labels for each class the model can predict, ordered by their class_id

        :return: Mapping of added attributes string name -> ArthurAttribute Object
        :raise: ArthurUserError: failed due to user error
        :raise: ArthurInternalError: failed due to an internal error
        """
        if predicted_attr_name == gt_attr_name:
            raise UserValueError("Predicted value attribute name matched ground truth attribute name. Attribute names "
                                 "must be unique")
        if len(image_class_labels) == 0:
            raise UserValueError("Must provide at least one class label")
        if self.input_type != InputType.Image or self.output_type != OutputType.ObjectDetection:
            raise MethodNotApplicableError("This function can only be called for models with Image input and Object "
                                           "Detection output")

        arthur_gt_attr = ArthurAttribute(
            name=gt_attr_name,
            stage=Stage.GroundTruth,
            value_type=ValueType.BoundingBox,
            attribute_link=predicted_attr_name,
            position=self._generate_attr_positions(Stage.GroundTruth, preferred_positions=[0])[0]
        )
        arthur_pred_attr = ArthurAttribute(
            name=predicted_attr_name,
            stage=Stage.PredictedValue,
            value_type=ValueType.BoundingBox,
            attribute_link=gt_attr_name,
            position=self._generate_attr_positions(Stage.PredictedValue, preferred_positions=[0])[0]
        )
        self._add_attribute_to_model(arthur_gt_attr)
        self._add_attribute_to_model(arthur_pred_attr)
        self.image_class_labels = image_class_labels

        return {predicted_attr_name: arthur_pred_attr, gt_attr_name: arthur_gt_attr}

    @arthur_excepted("failed to get attribute")
    def get_attribute(self, name: str, stage: Optional[Stage] = None) -> ArthurAttribute:
        """Retrieves an attribute by name and stage

        :param name: string name of the attribute to retrieve
        :param stage: Optional `Stage` of attribute to retrieve

        :return: ArthurAttribute Object
        :raise: ArthurUserError: failed due to user error
        :raise: ArthurInternalError: failed due to an internal error
        """
        if self.attributes is None:
            raise MethodNotApplicableError("model does not have any attributes")
        for attr in self.attributes:
            if stage is not None and attr.name == name and attr.stage == Stage:
                return attr
            elif attr.name == name:
                return attr

        raise UserValueError(f"Attribute with name: {name} in stage: {stage} does not exist")

    @arthur_excepted("failed to get attributes")
    def get_attributes(self, stage: Optional[Stage]) -> Optional[List[ArthurAttribute]]:
        """Returns a list of attributes for the specified stage

        :param stage: :class:`arthurai.common.constants.Stage` to filter by
        :return: List of :class:`arthurai.attributes.ArthurAttribute`
        :raise: ArthurUserError: failed due to user error
        :raise: ArthurInternalError: failed due to an internal error
        """
        if self.attributes is None:
            return None
        return [attr for attr in self.attributes if stage and attr.stage == stage]

    @arthur_excepted("failed to get attribute names")
    def get_attribute_names(self, stage: Optional[Stage]) -> List[str]:
        """ Returns a list of all attribute names. If stage is supplied it will only return the attribute names which
        are in the specified stage.

        :param stage: :class:`arthurai.common.constants.Stage` to filter by
        :return: List of string attribute names
        :raise: ArthurUserError: failed due to user error
        :raise: ArthurInternalError: failed due to an internal error
        """
        if self.attributes is None:
            raise MethodNotApplicableError("model does not have any attributes")
        return [attr.name for attr in self.attributes if stage and attr.stage == stage]

    @arthur_excepted("failed to rename attribute")
    def rename_attribute(self, old_name: str, new_name: str, stage: Stage) -> ArthurAttribute:
        """Renames an attribute by name and stage

        :param old_name: string name of the attribute to rename
        :param new_name: string new name of the attribute
        :param stage: `Stage` of attribute

        :return: ArthurAttribute Object
        :raise: ArthurUserError: failed due to user error
        :raise: ArthurInternalError: failed due to an internal error
        """
        attribute = self.get_attribute(old_name, stage)
        attribute.name = new_name

        return attribute

    @arthur_excepted("failed to set attribute labels")
    def set_attribute_labels(self, attribute_name: str, labels: Dict[Union[int, str], str],
                             attribute_stage: Optional[Stage] = None):
        """
        Sets labels for individual categories of a specific attribute
        :param attribute_name: Attribute name to set the categories labels
        :param attribute_stage: Optional stage of the attribute which is being updated
        :param labels: Dictionary where the key is the categorical value and the value is the string categorical label
        :return: None
        :raise: ArthurUserError: failed due to user error
        :raise: ArthurInternalError: failed due to an internal error
        """
        attr_to_update = self.get_attribute(name=attribute_name, stage=attribute_stage)
        categories = []
        for cat_value, cat_label in labels.items():
            categories.append(AttributeCategory(value=cat_value, label=cat_label))
        attr_to_update.categories = categories

    @arthur_excepted("failed to generate summary")
    def review(self, stage: Stage = None, props: Optional[List[str]] = None, print_df=False) -> Optional[DataFrame]:
        """Prints a summary of the properties of all attributes in the model.

        :param stage: restrict the output to a particular :py:class:`.Stage` (defaults to all stages)
        :param props: a list of properties to display in the summary
                   valid properties are data_type, categorical, is_unique, categories, cutoffs, range, monitor_for_bias, position
                   (defaults to data_type, categorical, is_unique)
        :param print_df: boolean value whether to print df or return it, defaults to False

        :return: a DataFrame summarizing the inferred types; or None if `print_df` is True
        :raise: ArthurUserError: failed due to user error
        :raise: ArthurInternalError: failed due to an internal error
        """

        if props is None:
            props = ["value_type", "categorical", "is_unique", "categories", "bins", "range", "monitor_for_bias"]

        attributes: Optional[List[ArthurAttribute]] = None
        if stage is None:
            attributes = self.attributes
            display_items = ["name", "stage"] + props
        else:
            attributes = self.get_attributes(stage=stage)
            display_items = ["name"] + props
        if attributes is None:
            raise MissingParameterError("model does not have any attributes")

        result_df = DataFrame(columns=display_items)
        for attribute in attributes:
            row: Dict[str, Union[str, List[str]]] = {}
            for item in display_items:
                if item == 'range':
                    row[item] = f"[{attribute.min_range}, {attribute.max_range}]"
                elif item == 'categories':
                    string_categories = []
                    categories = [] if attribute.categories is None else attribute.categories
                    for cat in categories:
                        if cat.label is not None:
                            string_categories.append("{" + f"label: {cat.label}, value: {cat.value}" + "}")
                        else:
                            string_categories.append("{" + f"value: {cat.value}" + "}")
                    row[item] = string_categories
                else:
                    row[item] = attribute.__getattribute__(item)
            result_df = result_df.append(row, ignore_index=True)

        if print_df:
            try:
                display(result_df)  # type: ignore
            except NameError:
                print(result_df)
            return None
        else:
            return result_df

    @arthur_excepted("failed to set predict function input order")
    def set_predict_function_input_order(self, attributes: List[str]) -> None:
        """Sets the expected order of attributes used by the prediction function.

        :param attributes: a list of attribute names

        :return: None
        :raise: ArthurUserError: failed due to user error
        :raise: ArthurInternalError: failed due to an internal error
        """
        for idx, name in enumerate(attributes):
            attribute = self.get_attribute(name, Stage.ModelPipelineInput)
            attribute.position = idx

    @arthur_excepted("failed to set attribute as sensitive")
    def set_attribute_as_sensitive(self, attribute_name: str, attribute_stage: Optional[Stage] = None) -> None:
        """Sets the passed-in attribute to be sensitive by setting `attr.monitor_for_bias` = True.

        You will need to call `self.save()` or `self.update()` after this method; we do not
        automatically call the API in this method.

        :param attribute_name: Name of attribute to set as sensitive.
        :param attribute_stage: Stage of attribute to set as sensitive.

        :return: None

        :raise: ArthurUserError: failed due to user error
        :raise: ArthurInternalError: failed due to an internal error
        """
        attribute = self.get_attribute(attribute_name, attribute_stage)

        attribute.monitor_for_bias = True

    @arthur_excepted("failed to enable explainability")
    def enable_explainability(self, df: Optional[DataFrame] = None,
                              project_directory: Optional[str] = None,
                              user_predict_function_import_path: Optional[str] = None,
                              streaming_explainability_enabled: Optional[bool] = True,
                              requirements_file: str = "requirements.txt",
                              python_version: Optional[str] = None,
                              sdk_version: str = __version__,
                              model_server_num_cpu: Optional[str] = None,
                              model_server_memory: Optional[str] = None,
                              model_server_max_replicas: Optional[int] = None,
                              inference_consumer_num_cpu: Optional[str] = None,
                              inference_consumer_memory: Optional[str] = None,
                              inference_consumer_thread_pool_size: Optional[int] = None,
                              inference_consumer_score_percent: Optional[float] = None,
                              explanation_nsamples: Optional[int] = None,
                              explanation_algo: Optional[str] = None,
                              ignore_dirs: List = None) -> None:
        """Enable explainability for this model.

        :param df:                                a dataframe containing the :py:class:`.Stage.ModelPipelineInput` values for this model. Required for non-image models.
        :param project_directory:                 the name of the directory containing the model source code. Required.
        :param user_predict_function_import_path: the name of the file that implements or wraps the predict function. Required.
        :param streaming_explainability_enabled:  Defaults to true. flag to turn on streaming explanations which will explain every inference sent to the platform. If false, explanations will need to be manually generated for each inference via the Arthur API. Set to false if worried about compute cost.
        :param requirements_file:                 the name of the file that contains the pip requirements (default: requirements.txt)
        :param python_version:                    the python version (default: sys.version). Should be in the form of <major>.<minor>
        :param sdk_version:                       the version of the sdk to initialize the model servier with
        :param model_server_num_cpu:              string number of CPUs to provide to model server docker container. If not provided, 1 CPU is used. Specified in the format of Kubernetes CPU resources. '1', '1.5', '100m', etc. (default: None)
        :param model_server_memory:               The amount of memory to allocate to the model server docker container. Provided in the format of kubernetes memory resources "1Gi" or "500Mi" (default: None).
        :param model_server_max_replicas          The max number of model servers to create
        :param inference_consumer_num_cpu:        string number of CPUs to provide to inference consumer docker container. If not provided, 1 CPU is used. Specified in the format of Kubernetes CPU resources. '1', '1.5', '100m', etc. (default: '1')
        :param inference_consumer_memory:         The amount of memory to allocate to the model server docker container. Provided in the format of kubernetes memory resources "1Gi" or "500Mi" (default: '1G').
        :param inference_consumer_thread_pool_size  The number of inference consumer workers, this determines how many requests to the model server can be made in parallel. Default of 5. If increasing, CPU should be increased as well.
        :param inference_consumer_score_percent   What percent of inferences should get scored. Should be a value between 0.0 and 1.0. Default 1.0 (everything is scored)
        :param explanation_nsamples:              number of predictions to use in the explanation. For SHAP the default is 2048 + 2(num features). For LIME, the default is 5000. (default: None)
        :param explanation_algo:                  the algorithm to use for explaining inferences. Valid values are 'lime' and 'shap'. Defaults to 'lime'.
        :param ignore_dirs:                       a list of directories within the project_directory that you do not want to include when uploading the model.  Path is relative to project_directory.
        :return: None
        :raise: ArthurUserError: failed due to user error
        :raise: ArthurInternalError: failed due to an internal error
        """
        if self.input_type == InputType.NLP and self.text_delimiter is None:
            raise MissingParameterError("Must set a text delimiter for NLP models prior to enabling explainability")
        if python_version is None:
            python_version = f'{sys.version_info[0]}.{sys.version_info[1]}'
            if sys.version_info[0] == 3 and sys.version_info[1] >= 9:
                raise UserValueError("Explainability not supported for Python 3.9 and greater. Please use Python 3.8")
        if self.input_type != InputType.Image and df is None:
            raise MissingParameterError("Must provide example dataframe for NLP and Tabular models")
        if project_directory is None:
            raise MissingParameterError("project_directory must be specified")
        if user_predict_function_import_path is None:
            raise MissingParameterError("user_predict_function_import_path must be specified")
        if df is not None and len(df) < 5000:
            logger.warning(f"Only pasing {len(df)} rows into explainer. The explanation algorithm uses this example "
                           f"data to generate distributions  in order to perturb data and generate explanations. This "
                           f"example data should be representative of your training set. Ideally this data should "
                           f"contain examples of all possible categorical values, and wide range of possible "
                           f"continuous attributes. If desired, rerun this function with more data passed to update "
                           f"the explainer.")

        explainability_config = dict(
            df=df,
            project_directory=project_directory,
            ignore_dirs=ignore_dirs if ignore_dirs else [],
            user_predict_function_import_path=user_predict_function_import_path,
            streaming_explainability_enabled=streaming_explainability_enabled,
            requirements_file=requirements_file,
            python_version=python_version,
            sdk_version=sdk_version,
            explanation_nsamples=explanation_nsamples,
            explanation_algo=explanation_algo,
            model_server_num_cpu=model_server_num_cpu,
            model_server_memory=model_server_memory,
            model_server_max_replicas=model_server_max_replicas,
            inference_consumer_num_cpu=inference_consumer_num_cpu,
            inference_consumer_memory=inference_consumer_memory,
            inference_consumer_thread_pool_size=inference_consumer_thread_pool_size,
            inference_consumer_score_percent=inference_consumer_score_percent
        )
        return self.update_enrichment(Enrichment.Explainability, True, explainability_config)

    @arthur_excepted("failed to enable bias mitigation")
    def enable_bias_mitigation(self):

        self._check_model_save()

        if not self.check_has_bias_attrs():
            raise MethodNotApplicableError("This model has no attributes marked as monitor for bias.")
        if not self.get_positive_predicted_class():
            raise MethodNotApplicableError("Bias mitigation is currently only supported for binary classifiers.")

        return self.update_enrichment(Enrichment.BiasMitigation, True, config=None)

    def model_is_saved(self) -> bool:
        return self.id is not None

    def _check_model_save(self, msg="You must save the model before sending"):
        if not self.model_is_saved():
            raise MethodNotApplicableError(msg)

    def _store_model_id_in_env(self):
        if self.id is not None:
            os.environ['ARTHUR_LAST_MODEL_ID'] = self.id

    @arthur_excepted("failed to send inferences")
    def send_inferences(self,
                        inferences: Union[List[Dict[str, Any]], Dict[str, List[Any]], DataFrame],
                        predictions: Optional[Union[List[Dict[str, Any]], Dict[str, List[Any]],
                                                    DataFrame, Sequence[Any]]] = None,
                        inference_timestamps: Optional[Sequence[Union[datetime, str]]] = None,
                        ground_truths: Optional[Union[List[Dict[str, Any]], Dict[str, List[Any]],
                                                      DataFrame, Sequence[Any]]] = None,
                        ground_truth_timestamps: Optional[Sequence[Union[datetime, str]]] = None,
                        partner_inference_ids: Optional[Sequence[str]] = None,
                        batch_id: Optional[str] = None,
                        fail_silently: bool = False,
                        complete_batch: bool = True):
        """
        Send inferences to the Arthur API. The `inferences` parameter may contain all the inference data, or only the
        input data if predictions and metadata are supplied separately. At a minimum, input data and predictions should
        be passed in: `partner_inference_id`, `inference_timestamp`, and (if ground truth data is supplied)
        `ground_truth_timestamp` fields are required by the Arthur API, but these will be generated if not supplied.

        .. seealso::
            To send large amounts of data or Parquet files, see :func:`ArthurModel.send_bulk_inferences()`

        **Examples:**

        An input dataframe and predicted probabilities array, leaving the partner inference IDs and timestamps to be
        auto-generated:

        .. code-block:: python

            input_df = pd.DataFrame({"input_attr": [2]})
            pred_array = my_sklearn_model.predict_proba(input_df)
            arthur_model.send_inferences(input_df, predictions=pred_array, batch_id='batch1')

        All data in the inferences parameter in the format expected by the
        `Arthur API <https://docs.arthur.ai/api-documentation/v3-api-docs.html#tag/inferences/paths/~1models~1{model_id}
        ~1inferences/post>`_:

        .. code-block:: python

            inference_data = [
                {
                    "inference_timestamp": "2021-06-16T16:52:11Z",
                    "partner_inference_id": "inf1",
                    "batch_id": "batch1",
                    "inference_data": {
                        "input_attr": 2,
                        "predicted_attr": 0.6
                    },
                    "ground_truth_timestamp": "2021-06-16T16:53:45Z",
                    "ground_truth_data": {
                        "ground_truth_attr": 1
                    }
                }
            ]
            arthur_model.send_inferences(inference_data)

        A list of dicts without nested `inference_data` or `ground_truth` fields:

        .. code-block:: python

            inference_data = [
                {
                    "inference_timestamp": "2021-06-16T16:52:11Z",
                    "partner_inference_id": "inf1",
                    "batch_id": "batch1",
                    "input_attr": 2,
                    "predicted_attr": 0.6,
                    "ground_truth_timestamp": "2021-06-16T16:53:45Z",
                    "ground_truth_attr": 1
                }
            ]
            arthur_model.send_inferences(inference_data)


        :param inferences: inference data to send, containing at least input values and optionally predictions, ground
         truth, timestamps, partner inference ids, and batch IDs.
        :param predictions: the model predictions, in a table-like format for one or more columns or a list-like format
         if the model has only one predicted column. overwrites any predictions supplied in the `inferences` parameter
        :param inference_timestamps: the inference timestamps, in a list-like format as ISO-8601 strings or datetime
         objects. if no timestamps are supplied in `inferences` or this parameter, they will be generated from the
         current time. overwrites any timestamps in the `inferences` parameter.
        :param ground_truths: the optional ground truth data (true labels), in a table-like format for one or more
         columns or a list-like format if the model has only one ground truth column. overwrites any ground truth values
         supplied in the `inferences` parameter
        :param ground_truth_timestamps: the ground truth timestamps, in a list-like format as ISO-8601 strings or
         datetime objects. if no ground truth timestamps are supplied in `inferences` or this parameter but ground truth
         data is supplied, they will be generated from the current time. overwrites any timestamps in the `inferences`
         parameter.
        :param partner_inference_ids: partner_inference_ids to be attached to these inferences, which can be used to
         send ground truth data later or retrieve specific inferences, in a list-like format containing strings. if no
         partner_inference_ids are supplied in `inference` or this parameter, they will be auto-generated.
        :param batch_id: a single batch ID to use for all inferences supplied. overwrites any batch IDs in the
         `inferences` parameter
        :param fail_silently: if True, log failed inferences but do not raise an exception
        :param complete_batch: if True, mark all batches in this dataset as completed

        :return: Upload status response in the following format:

         .. code-block:: python

            {
              "counts": {
                "success": 1,
                "failure": 0,
                "total": 1
              },
              "results": [
                {
                  "partner_inference_id" "inf-id",
                  "message": "success",
                  "status": 200
                }
              ]
            }

        :raise: ArthurUserError: failed due to user error
        :raise: ArthurInternalError: failed due to an internal error
        """
        self._check_model_save(msg="Must save model before sending inferences.")

        # first map initial arg into list-of-dicts format, it may be flat (all fields in top-level dict) or nested
        #  (with model attributes nested under inference_data)
        inferences = core_util.dataframe_like_to_list_of_dicts(inferences)

        # if inference_data and/or gt_data are not nested, nest them
        # with 25 attributes this runs at about 150,000 rows / sec, not terribly slow but could definitely be better
        inferences = inferences_util.nest_inference_and_ground_truth_data(inferences, self.attributes)

        # if predictions and/or ground truth are provided separately, add them
        if predictions is not None:
            inferences_util.add_predictions_or_ground_truth(inferences, predictions, self.attributes,
                                                            Stage.PredictedValue)
        if ground_truths is not None:
            inferences_util.add_predictions_or_ground_truth(inferences, ground_truths, self.attributes,
                                                            Stage.GroundTruth)
        # if timestamps and/or partner inference ids are provided separately, add them
        if inference_timestamps is not None:
            update_column_in_list_of_dicts(inferences, 'inference_timestamp', inference_timestamps)
        if ground_truth_timestamps is not None:
            update_column_in_list_of_dicts(inferences, 'ground_truth_timestamp', ground_truth_timestamps)
        if partner_inference_ids is not None:
            update_column_in_list_of_dicts(inferences, 'partner_inference_id', partner_inference_ids)

        inferences = arthur_util.format_timestamps(inferences)

        added_inference_timestamps = 0
        added_gt_timestamps = 0
        added_partner_inference_ids = 0
        sent_partner_inference_ids = []
        batch_counts: Dict[str, int] = {}
        current_iso_timestamp = datetime.now(pytz.utc).isoformat()
        for i in range(len(inferences)):
            inferences[i]["inference_data"] = self._replace_nans_and_infinities_in_dict(inferences[i]["inference_data"])
            inferences[i]['inference_data'] = self._convert_numpy_to_native(inferences[i]["inference_data"])
            if 'inference_timestamp' not in inferences[i].keys():
                inferences[i]['inference_timestamp'] = current_iso_timestamp
                added_inference_timestamps += 1
            if 'ground_truth_data' in inferences[i].keys():
                inferences[i]['ground_truth_data'] = self._convert_numpy_to_native(inferences[i]["ground_truth_data"])
                if 'ground_truth_timestamp' not in inferences[i]:
                    inferences[i]['ground_truth_timestamp'] = current_iso_timestamp
                    added_gt_timestamps += 1
            if batch_id is not None:
                inferences[i]['batch_id'] = batch_id
            if 'partner_inference_id' not in inferences[i].keys():
                inferences[i]['partner_inference_id'] = shortuuid.uuid()
                added_partner_inference_ids += 1
            if 'batch_id' in inferences[i].keys():
                batch_counts[inferences[i]['batch_id']] = batch_counts.get(inferences[i]['batch_id'], 0) + 1
            sent_partner_inference_ids.append(inferences[i]['partner_inference_id'])
        if added_inference_timestamps > 0:
            logger.info(f"{added_inference_timestamps} rows were missing inference_timestamp fields, so the current "
                        f"time was populated")
        if added_gt_timestamps > 0:
            logger.info(f"{added_gt_timestamps} rows were missing ground_truth_timestamp fields, so the current time "
                        f"was populated")
        if added_partner_inference_ids > 0:
            logger.info(f"{added_partner_inference_ids} rows were missing partner_inference_id fields, so UUIDs were "
                        f"generated, see return values")

        if self.input_type == InputType.Image:
            resp = self._upload_cv_inferences(inferences=inferences)
            return resp.json()

        endpoint = f"/models/{self.id}/inferences"
        resp = self._client.post(endpoint, json=inferences, return_raw_response=True,
                                 validation_response_code=HTTPStatus.MULTI_STATUS)

        user_failures, internal_failures = \
            validation.validate_multistatus_response_and_get_failures(resp, raise_on_failures=(not fail_silently))
        if fail_silently and (len(user_failures) > 0) or (len(internal_failures) > 0):
            message = "not all inferences succeeded!"
            message += f" user failures: {user_failures}." if len(user_failures) > 0 else ""
            message += f" internal failures: {internal_failures}." if len(internal_failures) > 0 else ""
            logger.error(message)

        parsed_response = resp.json()
        if 'results' not in parsed_response.keys():
            logger.warning(f"no inference-level results in response")
        elif len(parsed_response['results']) != len(sent_partner_inference_ids):
            logger.warning(f"response results length {len(parsed_response['results'])} does not match "
                           f"partner_inference_ids list length {len(sent_partner_inference_ids)}")
        else:
            for i in range(len(parsed_response['results'])):
                parsed_response['results'][i]['partner_inference_id'] = sent_partner_inference_ids[i]

        # complete batches
        if complete_batch:
            for batch_id, batch_count in batch_counts.items():
                endpoint = f"/models/{self.id}/batches/{batch_id}"
                self._close_dataset(endpoint, batch_count)

        return parsed_response

    def _upload_cv_inferences(self, inferences: List[Dict[str, Any]]):
        cv_attr = self.get_image_attribute()
        image_zipper = ImageZipper()

        for inf in inferences:
            image_path = inf['inference_data'][cv_attr.name]
            image_zipper.add_file(image_path)

        zip_file = image_zipper.get_zip()
        headers = {'Content-Type': 'multipart/form-data'}
        form_parts = {
            'image_data': ('images.zip', zip_file),
            'inference_data': ('inferences.json', json.dumps(inferences))
        }

        endpoint = f"/models/{self.id}/inferences/file"
        # TODO: PE-983 - add validation
        return self._client.post(endpoint, json=None, files=form_parts, headers=headers, return_raw_response=True)

    def _format_inference_request(self, inference_timestamp: Union[str, datetime],
                                  partner_inference_id: Optional[str] = None,
                                  model_pipeline_input=None,
                                  non_input_data=None,
                                  predicted_value=None,
                                  ground_truth=None):
        """takes in an inference to send following the old sdk contract and converts the data to the request body
        of the new api format.


        :param inference_timestamp: a mapping of the name of ground truth attributes to their value
        :param partner_inference_id: an external id (partner_inference_id) to assign to the inferences
        :param model_pipeline_input: a mapping of the name of pipeline input attributes to their value
        :param non_input_data: a mapping of the name of non-input data attributes to their value
        :param predicted_value: a mapping of the name of predicted value attributes to their value
        :param ground_truth: a mapping of the name of ground truth attributes to their value

        :return: dictionary object which can be used to send the inference
        """
        if model_pipeline_input is None:
            model_pipeline_input = {}
        if non_input_data is None:
            non_input_data = {}
        if predicted_value is None:
            predicted_value = {}

        model_pipeline_input.update(predicted_value)
        model_pipeline_input.update(non_input_data)
        inference = {
            "inference_timestamp": inference_timestamp,
            "partner_inference_id": partner_inference_id,
            "inference_data": model_pipeline_input,
        }

        if ground_truth is not None:
            inference["ground_truth_timestamp"] = inference_timestamp
            inference["ground_truth_data"] = ground_truth

        return inference

    @staticmethod
    def _replace_nans_and_infinities_in_dict(dict_to_update) -> Optional[Dict]:
        if dict_to_update is None:
            return None

        dict_to_return = {}

        for key, value in dict_to_update.items():
            if type(value) in (Series, list, np.ndarray):
                pass
            elif isna(value) or value in (np.Inf, -np.inf, np.inf):
                value = None
            dict_to_return[key] = value

        return dict_to_return

    @staticmethod
    def _convert_numpy_to_native(dict_to_update) -> Dict:
        final_dict = {}
        for k, v in dict_to_update.items():
            if isinstance(v, np.generic):
                final_dict[k] = v.item()
            else:
                final_dict[k] = v
        return final_dict

    @arthur_excepted("failed to send inference")
    def send_inference(self, inference_timestamp: Union[str, datetime],
                       partner_inference_id: str = "",
                       model_pipeline_input=None,
                       non_input_data=None,
                       predicted_value=None,
                       ground_truth=None):
        """Uploads an inference with or without ground truth; this sends a single inference.

        All inferences should follow the column format specified in `add_<modeltype>_classifier_output_attributes()`.
        Additionally, external_id and inference_timestamp must be provided.

        :param inference_timestamp: timestamp for inference to send; generated by external partner (not Arthur)
        :param partner_inference_id: an external id (partner_inference_id) to assign to the inferences
        :param model_pipeline_input: a mapping of the name of pipeline input attributes to their value
        :param non_input_data: a mapping of the name of non-input data attributes to their value
        :param predicted_value: a mapping of the name of predicted value attributes to their value
        :param ground_truth: a mapping of the name of ground truth attributes to their value

        :return: Upload status response in the following format:

         .. code-block:: JSON

            {
                "counts": {
                    "success": 0,
                    "failure": 0,
                    "total": 0
                },
                "results": [
                    {
                        "message": "success",
                        "status": 200
                    }
                ]
            }

        :raise: ArthurUserError: failed due to user error
        :raise: ArthurInternalError: failed due to an internal error
        """
        if predicted_value is None:
            predicted_value = {}
        if non_input_data is None:
            non_input_data = {}
        if model_pipeline_input is None:
            model_pipeline_input = {}

        self._check_model_save(msg="Must save model before sending inferences.")

        inference = self._format_inference_request(
            inference_timestamp=inference_timestamp,
            partner_inference_id=partner_inference_id,
            model_pipeline_input=ArthurModel._replace_nans_and_infinities_in_dict(model_pipeline_input),
            non_input_data=ArthurModel._replace_nans_and_infinities_in_dict(non_input_data),
            predicted_value=ArthurModel._replace_nans_and_infinities_in_dict(predicted_value),
            ground_truth=ArthurModel._replace_nans_and_infinities_in_dict(ground_truth)
        )
        return self.send_inferences([inference])

    @arthur_excepted("failed to update inference ground truths")
    def update_inference_ground_truths(self,
                                       ground_truths: Union[List[Dict[str, Any]], Dict[str, List[Any]], DataFrame,
                                                            Sequence[Any]],
                                       partner_inference_ids: Optional[Sequence[str]] = None,
                                       ground_truth_timestamps: Optional[Sequence[Union[datetime, str]]] = None,
                                       fail_silently: bool = False):
        """
        Updates inferences with the supplied ground truth values.

        The `ground_truth` parameter may contain all the required data, or only the data for the attributes from
        Stage.GroundTruth if metadata is supplied separately. At a minimum, Stage.GroundTruth attribute data and
        `partner_inference_id` should be passed in, either along with the attribute data in the `ground_truths`
        parameter, or in the `partner_inference_ids` parameter.
        Additionally, a `ground_truth_timestamp` field is required by the Arthur API, but this will be generated if not
        supplied.

        .. seealso::
            To send large amounts of data or Parquet files, see :func:`ArthurModel.send_bulk_ground_truths()`

        **Examples:**

        A DataFrame containing all required values:

        .. code-block:: python

            y_test = [1, 0, 1]
            existing_inference_ids = [f"batch_1-inf_{i}" for i in len(y_test)]
            ground_truth_df = pd.DataFrame({"ground_truth_positive_labels": y_test,
                                            "ground_truth_negative_labels": 1 - y_test,
                                            "partner_inference_id": existing_inference_ids})
            arthur_model.update_inference_ground_truths(ground_truth_df)

        A single list of values, with partner_inference_ids supplied separately:

        .. code-block:: python

            y_test = [14.3, 19.6, 15.7]
            existing_inference_ids = [f"batch_1-inf_{i}" for i in len(y_test)]
            arthur_model.update_inference_ground_truths(y_test, partner_inference_ids=existing_inference_ids)

        All data in the inferences parameter in the format expected by the
        `Arthur API <https://docs.arthur.ai/api-documentation/v3-api-docs.html#tag/inferences/paths/~1models~1{model_id}
        ~1inferences/patch>`_:

        .. code-block:: python

            ground_truth_data = [
                {
                    "partner_inference_id": "inf1",
                    "ground_truth_timestamp": "2021-06-16T16:53:45Z",
                    "ground_truth_data": {
                        "ground_truth_attr": 1
                    }
                }
            ]
            arthur_model.update_inference_ground_truths(ground_truth_data)

        A list of dicts without nested `ground_truth` fields:

        .. code-block:: python

            inference_data = [
                {
                    "partner_inference_id": "inf1",
                    "ground_truth_timestamp": "2021-06-16T16:53:45Z",
                    "ground_truth_attr": 1
                }
            ]
            arthur_model.send_inferences(inference_data)

        ======
        :param ground_truths: ground truth data to send, containing at least values for the ground truth attributes,
            and optionally `ground_truth_timestamp`s and `partner_inference_id`s.
        :param partner_inference_ids: partner_inference_ids for the existing inferences to be updated, in a list-like
            format as strings. Required if not a field in `ground_truths`.
        :param ground_truth_timestamps: the ground truth timestamps, in a list-like format as ISO-8601 strings or
         datetime objects. if no ground truth timestamps are supplied in `inferences` or this parameter, they will be
         generated from the current time. overwrites any timestamps in the `ground_truths` parameter.
        :param fail_silently: if True, log failed inferences but do not raise an exception.

        :return: Upload status response in the following format:

            .. code-block:: JSON

                {
                    "counts": {
                        "success": 1,
                        "failure": 0,
                        "total": 1
                    },
                    "results": [
                        {
                            "message": "success",
                            "status": 200
                        }
                    ]
                }

        :raise: ArthurUserError: failed due to user error
        :raise: ArthurInternalError: failed due to an internal error
        """
        self._check_model_save()

        # parse the input data into the expected format
        ground_truths = inferences_util.parse_stage_attributes(ground_truths, self.attributes, Stage.GroundTruth)
        ground_truths = inferences_util.nest_inference_and_ground_truth_data(ground_truths, self.attributes)

        # if timestamps and/or partner inference ids are provided separately, add them
        if ground_truth_timestamps is not None:
            update_column_in_list_of_dicts(ground_truths, 'ground_truth_timestamp', ground_truth_timestamps)
        if partner_inference_ids is not None:
            update_column_in_list_of_dicts(ground_truths, 'partner_inference_id', partner_inference_ids)

        ground_truths = arthur_util.format_timestamps(ground_truths)

        added_timestamps = 0
        current_iso_timestamp = datetime.now(pytz.utc).isoformat()
        for i in range(len(ground_truths)):
            ground_truths[i]['ground_truth_data'] = self._convert_numpy_to_native(ground_truths[i]["ground_truth_data"])
            if 'ground_truth_timestamp' not in ground_truths[i]:
                ground_truths[i]['ground_truth_timestamp'] = current_iso_timestamp
                added_timestamps += 1
        if added_timestamps > 0:
            logger.info(f"{added_timestamps} rows were missing ground_truth_timestamp fields, so the current time "
                        f"was populated")

        endpoint = f"/models/{self.id}/inferences"
        resp = self._client.patch(endpoint, json=ground_truths, return_raw_response=True,
                                  validation_response_code=HTTPStatus.MULTI_STATUS)
        user_failures, internal_failures = \
            validation.validate_multistatus_response_and_get_failures(resp, raise_on_failures=(not fail_silently))
        if fail_silently and (len(user_failures) > 0) or (len(internal_failures) > 0):
            message = "not all ground truth updates succeeded!"
            message += f" user failures: {user_failures}." if len(user_failures) > 0 else ""
            message += f" internal failures: {internal_failures}." if len(internal_failures) > 0 else ""
            logger.error(message)

        return resp.json()

    @arthur_excepted("failed to binarize")
    def binarize(self, attribute_value):
        """Creates a binary class probability based on classes defined in a :py:attr:`.ModelType.Multiclass` model.

        :param attribute_value: a mapping of the name of a predicted value attribute to its value

        :return: A two-value dictionary with probabilities for both predicted classes.
        :raise: ArthurUserError: failed due to user error
        :raise: ArthurInternalError: failed due to an internal error
        """

        if len(attribute_value) > 1:
            raise UserValueError("A dictionary containing a key, value pair for one ground truth attribute is required")

        name, value = attribute_value.popitem()
        name = str(name)
        predicted_value = self.get_attributes(Stage.PredictedValue)
        if name not in [attr.name for attr in predicted_value]:
            raise UserValueError(f"Attribute {name} not found in {Stage.PredictedValue}")

        valid_type = lambda attr: attr.value_type == ValueType.Float and attr.min_range == 0.0 and attr.max_range == 1.0
        if len(predicted_value) == 2 and all([valid_type(attr) for attr in predicted_value]):
            return dict([(attr.name, value if attr.name == name else 1 - value) for attr in predicted_value])
        else:
            raise MethodNotApplicableError("This model is not a binary classification model.")

    @arthur_excepted("failed to one hot encode")
    def one_hot_encode(self, value):
        """Creates a one hot encoding of a class label based on classes defined in a :py:attr:`.ModelType.Multiclass` model.

        :param value: the ground truth value

        :return: A dictionary with a one hot encoding of possible ground truth values.
        :raise: ArthurUserError: failed due to user error
        :raise: ArthurInternalError: failed due to an internal error
        """
        name = str(value)
        ground_truth = self.get_attribute_names(stage=Stage.GroundTruth)
        if name not in ground_truth:
            raise UserValueError(f"Attribute {name} not found in {Stage.GroundTruth}")
        elif self.output_type != OutputType.Multiclass:
            raise MethodNotApplicableError("This model is not a Multiclass model")
        else:
            return dict([(attr_name, 1 if attr_name == name else 0) for attr_name in ground_truth])

    def _send_parquet_files(self,
                            endpoint: str,
                            file_name: str,
                            directory_path: Optional[str] = None,
                            data: Optional[DataFrame] = None,
                            initial_form_data: Optional[Dict[str, Any]] = None,
                            retries: int = 0):

        self._check_model_save(msg="Must save model before uploading reference data")

        if directory_path is None and data is None:
            raise MissingParameterError("Either directory_path or data must be provided")

        if data is not None:
            if isinstance(data, DataFrame):
                directory_path = DatasetService.convert_dataframe(model_id=self.id, stage=None, df=data)
            else:
                raise InternalTypeError("Expected a pandas.DataFrame in the 'data' parameter")

        if self.input_type == InputType.Image:
            logger.info('Processing image data, this may take a couple minutes')
            # to avoid large requets, we chunk image data into multiple zip files
            directory_path = DatasetService.chunk_parquet_image_set(directory_path, self.get_image_attribute().name)
            logger.info("Image processing complete!")

        _, file_info = DatasetService.send_parquet_files_from_dir_iteratively(self,
                                                                              directory_path,
                                                                              endpoint,
                                                                              file_name,
                                                                              additional_form_params=initial_form_data,
                                                                              retries=retries)

        # if image data, all data has been chunked and moved to different temporary directory
        # than what the user passed in, ensure that is cleaned up
        if self.input_type == InputType.Image:
            shutil.rmtree(directory_path)  # type: ignore

        return file_info

    @arthur_excepted("failed to set reference data")
    def set_reference_data(self, directory_path: Optional[str] = None, data: Optional[Union[DataFrame, Series]] = None):
        """Validates and sets the reference data for the given stage to the provided data.

        Either directory_path or data must be provided. Additionally, there must be
        one column per `ModelPipelineInput` and `NonInput` attribute.

        For Image models, the image file path should be included as the image atribute value, in either
        the parquet files specified by `directory_path` or the DataFrame provided.

        :param directory_path: file path to a directory of parquet files to upload for batch data
        :param data:  a DataFrame or Series containing the ground truth data

        :return: Returns a tuple, the first variable is the response from sending the reference set and the second
        is the response from closing the dataset.

        :raise: ArthurUserError: failed due to user error
        :raise: ArthurInternalError: failed due to an internal error
        """
        if directory_path is None and data is None:
            raise MissingParameterError("Either directory_path or data must be provided")

        if not self.model_is_saved():
            if data is not None:
                self.reference_dataframe = data
                return
            else:
                raise UserTypeError("Can only set reference data for an unsaved model using a DataFrame. Please save "
                                    "your model first to send Parquet files or set reference data with the 'data' "
                                    "parameter.")

        if data is not None:
            data = core_util.standardize_pd_obj(data, dropna=False, replacedatetime=False,
                                                attributes=self.attributes_type_dict)
            if isinstance(data, Series):
                data = data.to_frame()
            elif not isinstance(data, DataFrame):
                raise UserTypeError("Unsupported data type: a pandas.DataFrame or pandas.Series is required")

        endpoint = f"/models/{self.id}/reference_data"
        res = self._send_parquet_files(endpoint, 'reference_data.parquet', directory_path, data)

        ref_set_close_res = None
        if res[DatasetService.COUNTS][DatasetService.FAILURE] != 0:
            logger.warning(f"{res[DatasetService.COUNTS][DatasetService.FAILURE]} inferences failed to upload")
            logger.warning("Reference dataset auto-close was aborted because not all "
                           "inferences in the reference set were successfully uploaded")
        else:
            if data is None:
                files = core_util.retrieve_parquet_files(directory_path)
                num_rows = self._count_parquet_num_rows(files)
            else:
                num_rows = len(data)

            if num_rows == 0:
                raise UserValueError("data provided does not have any rows")

            ref_set_close_res = self._close_dataset(f"/models/{self.id}/reference_data",
                                                    num_rows)
        return res, ref_set_close_res

    @arthur_excepted("failed to send bulk ground truths")
    def send_bulk_ground_truths(self, directory_path: Optional[str] = None,
                                data: Optional[Union[DataFrame, Series]] = None):
        """Uploads a DataFrame or directory containing parquet files to the Arthur bulk inferences ingestion endpoint.

        :param directory_path: file path to a directory of parquet files containing ground truth data. Required if
            `data` is not provided, and cannot be populated if `data` is provided.
        :param data: a DataFrame or Series containing the ground truth data. Required if `directory_path` is not
            provided, and cannot be populated it `directory_path` is not provided.
        :return: Upload status response in the following format:

            .. code-block:: JSON

                {
                    "counts": {
                        "success": 0,
                        "failure": 0,
                        "total": 0
                    },
                    "results": [
                        {
                            "message": "success",
                            "status": 200
                        }
                    ]
                }
        :raise: ArthurUserError: failed due to user error
        :raise: ArthurInternalError: failed due to an internal error
        """

        self._check_model_save()

        if directory_path is None and data is None:
            raise MissingParameterError("Either directory_path or data must be provided")

        if data is None:
            pass
        elif isinstance(data, Series):
            data = data.to_frame()
        elif not isinstance(data, DataFrame):
            raise UserTypeError("Unsupported data type: a pandas.DataFrame or pandas.Series is required")

        prepped_data = None if data is None else inferences_util.add_inference_metadata_to_dataframe(data,
                                                                                                     self.attributes)

        endpoint = f"/models/{self.id}/inferences/file"
        return self._send_parquet_files(endpoint, 'ground_truths.parquet', directory_path, prepped_data,
                                        retries=INFERENCE_DATA_RETRIES)

    @arthur_excepted("failed to send batch ground truths")
    def send_batch_ground_truths(self, directory_path: Optional[str] = None,
                                 data: Optional[Union[DataFrame, Series]] = None):
        """
        .. deprecated:: 3.10.0
            Please use :func:`ArthurModel.send_bulk_ground_truths()` for both streaming and batch data.

        :param directory_path: file path to a directory of parquet files containing ground truth data
        :param data:  a DataFrame or Series containing the reference data for the :py:class:`Stage`

        :return: Upload status response in the following format:

            .. code-block:: JSON

                {
                    "counts": {
                        "success": 1,
                        "failure": 0,
                        "total": 1
                    },
                    "results": [
                        {
                            "message": "success",
                            "status": 200
                        }
                    ]
                }
        :raise: ArthurUserError: failed due to user error
        :raise: ArthurInternalError: failed due to an internal error
        """
        logger.warning("DEPRECATION WARNING: The ArthurModel.send_batch_ground_truths() method is deprecated. Please "
                       "use ArthurModel.send_bulk_ground_truths() for both streaming and batch data.")
        return self.send_bulk_ground_truths(directory_path=directory_path, data=data)

    @arthur_excepted("failed to send bulk inferences")
    def send_bulk_inferences(self,
                             batch_id: Optional[str] = None,
                             directory_path: Optional[str] = None,
                             data: Optional[DataFrame] = None,
                             complete_batch: bool = True,
                             ignore_join_errors: bool = FALSE_DEFAULT_IGNORE_JOIN_ERRORS):
        """Validates and uploads parquet files containing columns for inference data, partner_inference_id,
        inference_timestamp, and optionally a batch_id. Either directory_path or data must be
        specified.

        .. seealso::
            To send ground truth for your inferences, see :func:`ArthurModel.send_bulk_ground_truth()`

        The columns for predicted attributes should follow the column format specified in
        `add_<modeltype>_classifier_output_attributes()`.  Additionally, `partner_inference_id`,
        must be specified for all inferences unless `ignore_join_errors` is True.

        :param batch_id: string id for the batch to upload; if supplied, this will override any batch_id column
            specified in the provided dataset
        :param directory_path: file path to a directory of parquet files containing inference data. Required if
            `data` is not provided, and cannot be populated if `data` is provided.
        :param data: a DataFrame or Series containing the inference data. Required if `directory_path` is not
            provided, and cannot be populated it `directory_path` is not provided.
        :param complete_batch: Defaults to true and will automatically close a batch once it is sent
        :param ignore_join_errors: if True, allow inference data without `partner_inference_id`s or ground truth data

        :return: A tuple of the batch upload response and the close batch response.
        The batch upload response is in the following format:

            .. code-block:: JSON

                {
                    "counts": {
                        "success": 1,
                        "failure": 0,
                        "total": 1
                    },
                    "results": [
                        {
                            "message": "success",
                            "status": 200
                        }
                    ]
                }
        :raise: ArthurUserError: failed due to user error
        :raise: ArthurInternalError: failed due to an internal error
        """
        if not self.is_batch:
            complete_batch = False

        initial_form_data = {'batch_id': (None, batch_id)}
        endpoint = f"/models/{self.id}/inferences/file"

        if directory_path is None and data is None:
            raise MissingParameterError("Either directory_path or data must be provided.")

        if data is not None:
            if isinstance(data, DataFrame):
                num_rows = len(data)
                data = core_util.standardize_pd_obj(data, dropna=False, replacedatetime=False,
                                                    attributes=self.attributes_type_dict)
            else:
                raise UserTypeError("Unsupported data type: a pandas.DataFrame is required")
        else:
            files = core_util.retrieve_parquet_files(directory_path)
            num_rows = self._count_parquet_num_rows(files)

        if num_rows == 0:
            raise UserValueError("data provided does not have any rows")

        prepped_data = None if data is None else inferences_util.add_inference_metadata_to_dataframe(
            data, self.attributes, ignore_join_errors=ignore_join_errors)

        res = self._send_parquet_files(endpoint, 'inferences.parquet', directory_path, prepped_data,
                                       initial_form_data=initial_form_data,
                                       retries=INFERENCE_DATA_RETRIES)
        batch_res = None
        if res[DatasetService.COUNTS][DatasetService.FAILURE] != 0:
            logger.warning(f"{res[DatasetService.COUNTS][DatasetService.FAILURE]} inferences failed to upload")
            if complete_batch:
                logger.warning("Batch auto-close was aborted because not all inferences were successfully uploaded")
        elif complete_batch:
            endpoint = f"/models/{self.id}/batches/{batch_id}"
            batch_res = self._close_dataset(endpoint, num_rows)
        return res, batch_res

    def send_batch_inferences(self,
                              batch_id: Optional[str],
                              directory_path: Optional[str] = None,
                              data: Optional[DataFrame] = None,
                              complete_batch: bool = True):
        """
        .. deprecated:: 3.10.0
            Use :func:`ArthurModel.send_inferences()` to send batch or streaming data synchronously (recommended fewer
            than 100,000 rows), or :func:`ArthurModel.send_bulk_inferences()` to send many inferences or Parquet files.

        :param batch_id: string id for the batch to upload; if supplied, this will override any batch_id column
            specified in the provided dataset
        :param data: a DataFrame containing the reference data.
        :param directory_path: file path to a directory of parquet files containing ground truth data
        :param complete_batch: Defaults to true and will automatically close a batch once it is sent

        :return: A tuple of the batch upload response and the close batch response.
        The batch upload response is in the following format:

            .. code-block:: JSON

                {
                    "counts": {
                        "success": 0,
                        "failure": 0,
                        "total": 0
                    },
                    "failures": []
                }
        :raise: ArthurUserError: failed due to user error
        :raise: ArthurInternalError: failed due to an internal error
        """
        logger.warning("DEPRECATION WARNING: The ArthurModel.send_batch_inferences() method is deprecated. Please use "
                       "ArthurModel.send_inferences() or ArthurModel.send_bulk_inferences(). Both methods support "
                       "batch and streaming models, simply supply a `batch_id` field for batch models or omit it for "
                       "streaming models. Use send_bulk_inferences() to send a larger number of inferences "
                       "(recommended for more than 100,000 rows) asynchronously, or to upload Parquet files directly.")
        return self.send_bulk_inferences(batch_id=batch_id, directory_path=directory_path, data=data,
                                         complete_batch=complete_batch)

    def _count_parquet_num_rows(self, file_paths: List[str]) -> int:
        num_rows = 0
        for file in file_paths:
            pqfile = pq.ParquetFile(file)
            num_rows += pqfile.metadata.num_rows
            cols = [pqfile.schema[i].name for i in range(len(pqfile.schema))]

        return num_rows

    def _close_dataset(self, endpoint: str, num_inferences: Optional[int] = None) -> Dict:
        body: Dict[str, Union[str, int]] = {
            "status": "uploaded"
        }
        if num_inferences is not None:
            body["total_record_count"] = num_inferences

        batch_res = self._client.patch(endpoint=endpoint, json=body, return_raw_response=True,
                                       retries=INFERENCE_DATA_RETRIES, validation_response_code=HTTPStatus.OK)
        return {"dataset_close_result": batch_res.json()}

    @arthur_excepted("failed to close batch")
    def close_batch(self, batch_id: str, num_inferences: Optional[int] = None) -> Dict:
        """Closes the specified batch, optionally can supply the number of inferences that are contained in the batch

        :param batch_id: String batch_id associated with the batch that will be closed
        :param num_inferences: Optional number of inferences that are contained in the batch
        :return: Response of the batch close rest call
        :raise: ArthurUserError: failed due to user error
        :raise: ArthurInternalError: failed due to an internal error
        """
        endpoint = f"/models/{self.id}/batches/{batch_id}"
        return self._close_dataset(endpoint, num_inferences)

    @arthur_excepted("failed to delete explainer")
    def delete_explainer(self) -> None:
        """Spin down the model explainability server.

        :return: the server response

        :raise: ArthurUserError: failed due to user error
        :raise: ArthurInternalError: failed due to an internal error
        """
        if not hasattr(self, "_explainer"):
            raise MethodNotApplicableError(f"There is no explainability server to delete for model {self.id}")

        endpoint = f"/models/{self.id}/explainability"
        self._client.delete(endpoint, return_raw_response=True, validation_response_code=HTTPStatus.NO_CONTENT)
        logger.info(f"Successfully removed explainability server for model {self.id}")

    @arthur_excepted("failed to archive model")
    def archive(self):
        """Archives the model with a DELETE request.

        :return: the server response
        :raise: Exception: the model has no ID, or the model has not been archived
        """
        self._check_model_save(msg="Cannot archive an unregistered model.")

        endpoint = f"/models/{self.id}"
        # TODO [TMJ]: REMOVE RETRIES...this is a temporary band-aid to deal with issues
        #             our archive endpoint has.
        self._client.delete(endpoint,
                            return_raw_response=True,
                            validation_response_code=HTTPStatus.NO_CONTENT,
                            retries=3)

    @arthur_excepted("failed to execute query")
    def query(self, body: Dict[str, Any], query_type='base'):
        """ Execute query against the model's inferences.
        For full description of possible functions, aggregations, and transformations, see
        https://docs.arthur.ai/api-query-guide/
        For queries pertaining to datadrift metrics ('drift' or 'drift_psi_bucket_table' query types), please see
        https://docs.arthur.ai/api-query-guide/data_drift.html

        :param body: dict
        :param query_type: str Can be either 'base', 'drift', or 'drift_psi_bucket_table'

        .. code-block:: python

            body = {
                       "select":[
                          {"property":"batch_id"},
                          {
                             "function":"count",
                             "alias":"inference_count"
                          }
                       ],
                       "group_by":[
                          {"property":"batch_id"}
                       ]
                    }

        .. code-block:: python

            body = {
                       "select":[,
                          {"property":"batch_id"},
                          {
                             "function":"rate",
                             "alias":"positive_rate",
                             "parameters":{
                                "property":"predicted_1",
                                "comparator":"gt",
                                "value":0.75
                             }
                          }
                       ],
                       "group_by":[
                          {"property":"batch_id"}
                       ]
                    }


        :return: the query response as documented in https://docs.arthur.ai/api-query-guide/
        :raise: ArthurUserError: failed due to user error
        :raise: ArthurInternalError: failed due to an internal error
        """
        self._check_model_save(msg="You must save model before querying.")

        endpoint = f"/models/{self.id}/inferences/query"
        if query_type == "base":
            pass
        elif query_type == "drift":
            endpoint = f"{endpoint}/data_drift"
        elif query_type == "drift_psi_bucket_table":
            endpoint = f"{endpoint}/data_drift_psi_bucket_calculation_table"
        else:
            raise UserValueError(f"Invalid query type '{query_type}', must be on of 'base', 'drift', or "
                                 f"'drift_psi_bucket_table'")
        resp = self._client.post(endpoint, json=body, return_raw_response=True, validation_response_code=HTTPStatus.OK)

        return resp.json()["query_result"]

    @arthur_excepted("failed to create metric")
    def create_metric(self, name: str, query: Dict[str, Any], is_data_drift: bool = False) -> str:
        """
        Creates a metric registered to this model and returns the UUID assigned to the newly created metric.
        This metric can be used to create alert rules on.
        :param name: Name of the metric to create.
        :param query: Query which makes up the metric
        :param is_data_drift: Boolean to signal whether this query is a data drift metric or not.
        :return: UUID of the newly created metric
        """
        endpoint = f"/models/{self.id}/metrics"
        metric_endpoint = f"{API_PREFIX}/models/{self.id}/inferences/query" if not is_data_drift \
            else f"{API_PREFIX}/models/{self.id}/inferences/query/data_drift"
        request_body = {
            "name": name,
            "query": query,
            "endpoint": metric_endpoint
        }
        resp = self._client.post(endpoint, json=request_body, return_raw_response=True)
        validation.validate_response_status(resp, expected_status_code=HTTPStatus.CREATED)
        return resp.json()["id"]

    @arthur_excepted("failed to retrieve metrics")
    def get_metrics(self,
                    default_metrics: bool = False,
                    metric_type: Optional[MetricType] = None,
                    metric_id: Optional[str] = None,
                    metric_name: Optional[str] = None,
                    attribute_name: Optional[str] = None) -> List[Metric]:
        """Retrieves metrics associated with the current model. Can add optional filters to search with function parameters.
        :param default_metrics: If set to True will return only metrics that are automatically created by default for your model
        :param metric_type: MetricType to filter metric query with
        :param metric_id: Metric UUID to use in filtering metric search
        :param metric_name: Metric name filter to use in metric search
        :param attribute_name: Attribute name filter to use in metric search
        :return: list of metrics returned from metric search
        """
        if metric_id is not None:
            endpoint = f"/models/{self.id}/metrics/{metric_id}"
            resp = self._client.get(endpoint, return_raw_response=True)
            validation.validate_response_status(resp, expected_status_code=HTTPStatus.OK)
            return [Metric.from_dict(resp.json())]
        else:
            query_params = {"expand": "type"}
            if default_metrics:
                query_params["default"] = "true"
            if metric_type:
                if metric_type not in MetricType.list():
                    raise ArthurUserError(
                        f"Must use a metric_type from arthurai.core.alerts.MetricType: {MetricType.list()}")
                query_params["type"] = metric_type
            if metric_name:
                query_params["metric_name"] = metric_name
            if attribute_name:
                query_params["attribute_name"] = attribute_name

            endpoint = f"/models/{self.id}/metrics"
            current_page = total_pages = 1
            metrics = []
            while current_page <= total_pages:
                query_params["page"] = str(current_page)
                resp = self._client.get(endpoint, params=query_params, return_raw_response=True)
                validation.validate_response_status(resp, expected_status_code=HTTPStatus.OK)
                response_object = resp.json()
                json_metrics = response_object["metrics"]
                if len(json_metrics) == 0:
                    break
                metrics.extend([Metric.from_dict(m) for m in json_metrics])
                total_pages = response_object["total_pages"]
                current_page = response_object["page"] + 1

        return metrics

    @arthur_excepted("failed to create alert rule")
    def create_alert_rule(self,
                          metric_id: str,
                          bound: AlertRuleBound,
                          threshold: NumberType,
                          severity: AlertRuleSeverity,
                          name: Optional[str] = None,
                          lookback_period: Optional[NumberType] = None,
                          subsequent_alert_wait_time: Optional[NumberType] = None) -> AlertRule:
        """Creates alert rules for the current model.
        :param metric_id: UUID of the metric to use to create an alert rule.
        :param name: A name for the alert rule, a default will be generated if this is not supplied.
        :param bound: Either AlertRuleBound.Upper or AlertRuleBound.Lower
        :param threshold: Threshold of alert rule
        :param severity: AlertRuleSeverity of the alert which gets triggered when the metric violates the threshold of
                         the alert rule.
        :param lookback_period: The lookback time or "window length" in minutes to use when calculating the alert rule
                                metric. For example, a lookback period of 5 minutes for an alert rule on average
                                prediction will calculate average prediction for the past 5 minutes in a rolling window
                                format. This will default to 5 minutes
        :param subsequent_alert_wait_time: If metric continues to pass threshold this is the time in minutes to wait
                                           before triggering another alert. This defaults to 0. This does not need to
                                           be set for batch alerts.
        :return: the created alert rule
        :raise: ArthurUserError: failed due to user error
        :raise: ArthurInternalError: failed due to an internal error
        """
        alert_rule = AlertRule(
            name=name,
            bound=bound,
            threshold=threshold,
            metric_id=metric_id,
            severity=severity,
            lookback_period=lookback_period,
            subsequent_alert_wait_time=subsequent_alert_wait_time,
        )

        endpoint = f"/models/{self.id}/alert_rules"
        resp = self._client.post(endpoint, json=alert_rule.to_dict(), return_raw_response=True, validation_response_code=HTTPStatus.OK)

        return AlertRule.from_dict(resp.json())

    @arthur_excepted("failed to get model alert rules")
    def get_alert_rules(self, page: int = 1, page_size: int = 20) -> List[AlertRule]:
        """Returns a paginated list of alert rules registered to this model

        :param page: page of alert rules to retrieve, defaults to 1
        :param page_size: number of alert rules to return per page, defaults to 20
        :return: List of :class:`arthurai.client.apiv3.AlertRule` objects
        :raise: ArthurUserError: failed due to user error
        :raise: ArthurInternalError: failed due to an internal error
        """
        endpoint = f"/models/{self.id}/alert_rules?page_size={page_size}&page={page}"
        resp = self._client.get(endpoint, return_raw_response=True, validation_response_code=HTTPStatus.OK)

        if 'data' not in resp.json():
            raise ExpectedParameterNotFoundError(
                "An error occurred when retrieving alert rules: {0}".format(resp.json()))

        alert_rules = []
        for rule in resp.json()['data']:
            alert_rules.append(AlertRule.from_dict(rule))
        return alert_rules

    @arthur_excepted("failed to update alert rule")
    def update_alert_rule(self, alert_rule: AlertRule, alert_rule_id: Optional[str] = None):
        """Updates alert rule fields included in the `alert_rule` object for the specified alert rule id. If the
        alert rules id field is present in the `alert_rule` parameter that is used otherwise `alert_rule_id`
        must be supplied

        :param alert_rule: Object which contains fields to update on the specified alert rule
        :param alert_rule_id: If the alert rule id is not specified in the `alert_rule_to_update` object then this
                              must be provided to determine which alert rule to update.
        :return: Updates alert rule object
        :raise: ArthurUserError: failed due to user error
        :raise: ArthurInternalError: failed due to an internal error
        """
        if alert_rule.id is None and alert_rule_id is None:
            raise MethodNotApplicableError("alert_rule_to_update must have a valid id, if the alert rule has not been "
                                           "created yet call model.create_alert_rule(...)")

        alert_rule_id = alert_rule.id if alert_rule.id is not None else alert_rule_id
        alert_rule.id = None

        endpoint = f"/models/{self.id}/alert_rules/{alert_rule_id}"
        resp = self._client.patch(endpoint, json=alert_rule.to_dict(), return_raw_response=True,
                                  validation_response_code=HTTPStatus.OK)

        return AlertRule.from_dict(resp.json())

    @arthur_excepted("failed to get model alerts")
    def get_alerts(self, page: int = 1, page_size: int = 500, status: Optional[str] = None,
                   alert_rule_id: Optional[str] = None, batch_id: Optional[str] = None,
                   start_time: Optional[str] = None, end_time: Optional[str] = None) -> List[Alert]:
        """Returns a paginated list of alert registered to this model.

        :param page: page of alert rules to retrieve, defaults to 1
        :param page_size: number of alert rules to return per page, defaults to 500
        :param status: status of alert rule
        :param alert_rule_id: id of alert rule
        :param batch_id: constrain returned alert rules to this batch id
        :param start_time: constrain returned alert rules to after this time
        :param end_time: constrain returned alert rules to before this time
        :return: List of :class:`arthurai.client.apiv3.Alert` objects
        :raise: ArthurUserError: failed due to user error
        :raise: ArthurInternalError: failed due to an internal error
        """
        url = f"{self._client.base_path}/alerts?model_id={self.id}&page_size={page_size}&page={page}"
        if status:
            url += f"&status={status}"
        if alert_rule_id:
            url += f"&alert_rule_id={alert_rule_id}"
        if batch_id:
            url += f"&batch_id={batch_id}"
        if start_time:
            url += f"&start_time={start_time}"
        if end_time:
            url += f"&end_time={end_time}"

        resp = self._client.get(url, return_raw_response=True)

        validation.validate_response_status(resp, expected_status_code=HTTPStatus.OK)
        if 'data' not in resp.json():
            raise ExpectedParameterNotFoundError(
                "An error occurred when retrieving alerts: {0}".format(resp.json()))

        alerts = []
        for rule in resp.json()['data']:
            alerts.append(Alert.from_dict(rule))
        return alerts

    @arthur_excepted("failed to update alert")
    def update_alert(self, status: AlertStatus, alert_id: str) -> Alert:
        """Updates alert to have a particular status.

        :param status: one of "resolved" or "acknowledged"
        :param alert_id: alert id
        :return: updated alert object
        :raise: ArthurUserError: failed due to user error
        :raise: ArthurInternalError: failed due to an internal error
        """
        if status not in AlertStatus.list():
            raise ValueError(f"status={status} is not valid and must be one of {AlertStatus.list()}")

        url = f"{self._client.base_path}/alerts/{alert_id}"
        resp = self._client.patch(url, data={"status": status}, return_raw_response=True)

        validation.validate_response_status(resp, expected_status_code=HTTPStatus.OK)

        return Alert.from_dict(resp.json())

    @arthur_excepted("failed to get enrichments")
    def get_enrichments(self) -> Dict[str, Any]:
        """Returns configuration for all enrichments.

        :return: Upload status response in the following format:

            .. code-block:: JSON

                {
                    "anomaly_detection": {
                        "enabled": false
                    },
                    "explainability": {
                        "config": {
                            "python_version": "3.7",
                            "sdk_version": "3.0.11",
                            "streaming_explainability_enabled": false,
                            "user_predict_function_import_path": "entrypoint",
                            "shap_expected_values": "[0.7674405187893311, 0.23255948121066888]",
                            "model_server_cpu": "2",
                            "model_server_memory": "1Gi",
                            "model_server_max_replicas": "5",
                            "explanation_nsamples": 1000,
                            "explanation_algo": "lime",
                            "inference_consumer_cpu": "100m",
                            "inference_consumer_memory": "512Mi",
                            "inference_consumer_score_percent": "1.0",
                            "inference_consumer_thread_pool_size": "1",
                            "service_account_id": "8231affb-c107-478e-a1b4-e24e7f1f6619"
                        },
                        "enabled": true
                    }
                }
        :raise: ArthurUserError: failed due to user error
        :raise: ArthurInternalError: failed due to an internal error
        """
        endpoint = f"/models/{self.id}/enrichments"
        resp = self._client.get(endpoint, return_raw_response=True, validation_response_code=HTTPStatus.OK)
        return resp.json()

    @arthur_excepted("failed to get enrichment")
    def get_enrichment(self, enrichment: Enrichment) -> Dict[str, Any]:
        """Returns configuration for the specified enrichment.

        :param enrichment: Enrichment constant
        :return: Enrichment config

            .. code-block:: JSON

                {
                    "enabled": true,
                    "config": {
                        "python_version": "3.7",
                        "sdk_version": "3.0.11",
                        "streaming_explainability_enabled": false,
                        "user_predict_function_import_path": "entrypoint",
                        "shap_expected_values": "[0.7674405187893311, 0.23255948121066888]",
                        "model_server_cpu": "2",
                        "model_server_memory": "1Gi",
                        "model_server_max_replicas": "5",
                        "explanation_nsamples": 1000,
                        "explanation_algo": "lime",
                        "inference_consumer_cpu": "100m",
                        "inference_consumer_memory": "512Mi",
                        "inference_consumer_score_percent": "1.0",
                        "inference_consumer_thread_pool_size": "1",
                        "service_account_id": "8231affb-c107-478e-a1b4-e24e7f1f6619"
                    }
                }
        :raise: ArthurUserError: failed due to user error
        :raise: ArthurInternalError: failed due to an internal error
        """
        endpoint = f"/models/{self.id}/enrichments/{enrichment}"
        resp = self._client.get(endpoint, return_raw_response=True, validation_response_code=HTTPStatus.OK)
        return resp.json()

    @arthur_excepted("failed to update enrichments")
    def update_enrichments(self, enrichment_configs: Dict[Union[str, Enrichment], Any]) -> Dict[str, Any]:
        """Update the configuration for 1 or more enrichments.
        See the enrichments guide at http://docs.arthur.ai/guides/enrichments.html.

        :param enrichment_configs: Dict containing the configuration for each enrichment

            .. code-block:: JSON

            {
                    "anomaly_detection": {
                        "enabled": false
                    },
                    "explainability": {
                        "config": {
                            "streaming_explainability_enabled": false,
                            "explanation_nsamples": 1000,
                            "explanation_algo": "lime",
                            "inference_consumer_score_percent": "1.0"
                        },
                        "enabled": true
                    }
                    "hotspots": {
                        "enabled": false
                    }
                }
        :return: the resulting enrichments configuration
        :raise: ArthurUserError: failed due to user error
        :raise: ArthurInternalError: failed due to an internal error
        """

        files = []
        # handle specifics for different enrichments
        if Enrichment.Explainability in enrichment_configs and enrichment_configs[Enrichment.Explainability]['enabled']:
            explanationPackager = ExplanationPackager(self, **enrichment_configs[Enrichment.Explainability]['config'])

            # check to see if user is trying to update files
            onePresent, allPresent = explanationPackager.contains_file_fields()
            if onePresent and not allPresent:
                raise MissingParameterError(
                    f"If updating model files for explainability, all of the following fields must be present in the config {ExplanationPackager.FILE_FIELDS}")
            # package explainer files
            elif allPresent:
                explanationPackager.make_zip()
                explanationPackager.create()
                files += explanationPackager.get_request_files()
            # replace passed in config (has file specific fields) with actual config
            enrichment_configs[Enrichment.Explainability]["config"] = explanationPackager.get_request_config()

        # build and make request
        headers = {"Content-Type": "multipart/form-data"}
        endpoint = f"/models/{self.id}/enrichments"
        data = {"config": json.dumps(enrichment_configs)}

        resp = self._client.patch(endpoint, json=data, files=files, headers=headers, return_raw_response=True,
                                  validation_response_code=HTTPStatus.ACCEPTED)
        return resp.json()

    @arthur_excepted("failed to update enrichment")
    def update_enrichment(self, enrichment: Enrichment, enabled: Optional[bool] = None,
                          config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Update the configuration for a single enrichment.
        :param enrichment: the enrichment to update
        :param enabled: whether the enrichment should be enabled or disabled
        :param config: the configuration for the enrichment, None by default
        :raise: ArthurUserError: failed due to user error
        :raise: ArthurInternalError: failed due to an internal error
        """

        data: Dict[str, Any] = {}
        if enabled is not None:
            data['enabled'] = enabled
        if config is not None:
            data['config'] = config
        return self.update_enrichments({enrichment: data})

    @arthur_excepted("failed to enable hotspots")
    def enable_hotspots(self):
        self._check_model_save()

        if not self.input_type == InputType.Tabular:
            raise MethodNotApplicableError("Hotspots may only be enabled on tabular models.")

        return self.update_enrichment(Enrichment.Hotspots, True)

    @arthur_excepted("failed to find hotspots")
    def find_hotspots(self,
                      metric: AccuracyMetric = AccuracyMetric.Accuracy,
                      threshold: float = 0.5,
                      batch_id: str = None,
                      date: str = None,
                      ref_set_id: str = None) -> Dict[str, Any]:
        """Retrieve hotspots from the model
        :param metric: accuracy metric used to filter hotspots tree by, defaults to "accuracy"
        :param threshold: threshold for of performance metric used for filtering hotspots, defaults to 0.5
        :param batch_id: string id for the batch to find hotspots in, defaults to None
        :param date: string used to define date, defaults to None
        :param ref_set_id: string id for the reference set to find hotspots in, defaults to None
        :raise: ArthurUserError: failed due to user error
        :raise: ArthurInternalError: failed due to an internal error
        """
        data_param_count = sum((batch_id is not None, date is not None, ref_set_id is not None))
        if data_param_count != 1:
            raise ArthurUserError(f"Exactly one of batch_id/date/ref_set_id must be specified, {data_param_count} were provided")

        endpoint = f"/models/{self.id}/enrichments/hotspots/find"
        query_params = {"metric": metric, "threshold": threshold}
        if batch_id is not None:
            query_params['batch_id'] = batch_id
        if date is not None:
            query_params['date'] = date
        if ref_set_id is not None:
            query_params['ref_set_id'] = ref_set_id

        endpoint = endpoint

        resp = self._client.get(endpoint, params=query_params, return_raw_response=True)
        validation.validate_response_status(resp, expected_status_code=HTTPStatus.OK)

        return resp.json()
