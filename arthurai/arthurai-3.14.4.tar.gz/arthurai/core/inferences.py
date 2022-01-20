from datetime import datetime
import logging
from typing import List, Dict, Any, Union, Iterable, Collection
from collections.abc import Iterable as IterableABC

import pandas as pd
import pytz
import shortuuid

from arthurai import ArthurAttribute
from arthurai.common.constants import Stage
from arthurai.common.exceptions import InternalValueError, UserValueError, UserTypeError
from arthurai.core.util import intersection_is_non_empty


INFERENCE_STAGES = {Stage.ModelPipelineInput, Stage.PredictFunctionInput, Stage.NonInputData, Stage.PredictedValue}
RESERVED_COLUMNS = {"inference_timestamp", "partner_inference_id", "batch_id", "ground_truth_timestamp",
                    "inference_data", "ground_truth_data"}
FALSE_DEFAULT_IGNORE_JOIN_ERRORS = False

logger = logging.getLogger(__name__)


def parse_stage_attributes(data: Union[List[Dict[str, Any]], Dict[str, List[Any]],
                                       pd.DataFrame, Iterable[Any]],
                           attributes: List[ArthurAttribute],
                           stage: Stage):
    """
    Parses data for a single stage into the standard List of Dicts format. If the stage contains only a single
    attribute, data can be a single list-like column.

    .. seealso::
        Similar to dataframe_like_to_list_of_dicts, but an expected column (attribute)-aware and supports single columns
    :param data:
    :param attributes:
    :param stage:
    :return: parsed data in List of Dicts formt
    """
    expected_attributes = {attr.name for attr in attributes if attr.stage == stage}

    # parsing
    if isinstance(data, list) and isinstance(data[0], dict):
        pass
    elif isinstance(data, dict):
        data = pd.DataFrame(data).to_dict(orient='records')
    elif isinstance(data, pd.DataFrame):
        data = data.to_dict(orient='records')
    elif isinstance(data, IterableABC):
        if len(expected_attributes) != 1:
            raise UserValueError(f"Only a single column was provided for {stage} data but there are "
                                 f"{len(expected_attributes)} expected attributes: {expected_attributes}")
        attr = next(iter(expected_attributes))
        data = [{attr: val} for val in data]
    else:
        raise UserTypeError(f"Cannot parse {stage} data of type {type(data)}, should be list of dicts, dict of "
                            f"lists, DataFrame, or Sequence of values")

    return data


def add_predictions_or_ground_truth(inference_data: List[Dict[str, Any]],
                                    new_data: Union[List[Dict[str, Any]], Dict[str, List[Any]],
                                                    pd.DataFrame, Iterable[Any]],
                                    attributes: List[ArthurAttribute],
                                    stage: Stage):
    """
    Add prediction or ground truth data to inference data *in place*.
    :param inference_data: the inference data as a List of Dicts as expected by the Arthur API
    :param new_data: the new data to add in, as a List of Dicts, Dict of Lists, DataFrame, or Sequence
    (if a single column)
    :param attributes: the model's attributes
    :param stage: the Stage of the new data, either PredictedValue or GroundTruth
    :return: None (modifies inference_data in place)
    """
    # initial validation and config
    if stage == Stage.GroundTruth:
        target_field = "ground_truth_data"
    elif stage == Stage.PredictedValue:
        target_field = "inference_data"
    else:
        raise InternalValueError(f"Unexpected stage {stage}, should be GroundTruth or PredictedValue")

    # dataframe being interpreted as Any but adding pandas stubs break a lot of typing so ignoring for now
    if len(new_data) == 0:  # type: ignore
        if len(inference_data) == 0:
            return inference_data
        else:
            raise UserValueError(f"Cannot add empty {stage} data to non-empty inference data")

    # parse new data into common format
    new_data = parse_stage_attributes(new_data, attributes, stage)

    # add new data
    if len(new_data) != len(inference_data):
        raise UserValueError(f"Size of {stage} data ({len(new_data)} does not match size of inference data "
                             f"{len(inference_data)}")
    for i in range(len(inference_data)):
        if target_field not in inference_data[i].keys():
            inference_data[i][target_field] = {}
        for new_key in new_data[i].keys():
            inference_data[i][target_field][new_key] = new_data[i][new_key]


def nest_inference_and_ground_truth_data(data: List[Dict[str, Any]], attributes: List[ArthurAttribute]) -> \
        List[Dict[str, Any]]:
    """
    Reformat List of Dicts inference data to nest inference and ground truth data as expected by the Arthur API.
    For example:

    .. code-block:: python

        [
            {
                "input_attr_1": 1.0,
                "prediction_1": 0.95,
                "inference_timestamp": "2021-06-03T19:44:33.169334+00:00",
                "ground_truth_1": 1,
                "ground_truth_timestamp": "2021-06-03T19:44:56.892019+00:00"
            }
        ]

    Will become:

    .. code-block:: python

        [
            {
                "inference_data":
                {
                    "input_attr_1": 1.0,
                    "prediction_1": 0.95
                },
                "ground_truth_data":
                {
                    "ground_truth_1": 1
                },
                "inference_timestamp": "2021-06-03T19:44:33.169334+00:00",
                "ground_truth_timestamp": "2021-06-03T19:44:56.892019+00:00"
            }
        ]

    :param data: the input data to reformat, either already nested or flat
    :param attributes: the model's attributes
    :return: the nested data
    """
    if len(data) == 0:
        return []

    inference_attrs = {attr.name for attr in attributes if attr.stage in INFERENCE_STAGES}
    gt_attrs = {attr.name for attr in attributes if attr.stage == Stage.GroundTruth}

    # ensure the data is not mixed nested and un-nested
    for i in range(len(data)):
        row = data[i]
        if "inference_data" in row.keys() and intersection_is_non_empty(inference_attrs, row.keys()):
            raise UserValueError(f"Inference data should be nested or non-nested, not mixed. Row {i} contains "
                                 "'inference_data' field and inference attribute fields.")
        if "ground_truth_data" in row.keys() and intersection_is_non_empty(gt_attrs, row.keys()):
            raise UserValueError(f"Ground truth data should be nested or non-nested, not mixed. Row {i} contains "
                                 "'ground_truth_data' field and ground truth attribute fields.")

    # generate nested data
    nested_data = []
    for i in range(len(data)):
        row = data[i]
        nested_row: Dict[str, Any] = {}
        # if the data needs to be nested create the wrapper dicts, otherwise validate the type
        if 'inference_data' not in row.keys():
            if intersection_is_non_empty(inference_attrs, row.keys()):
                nested_row['inference_data'] = {}
        elif not isinstance(row['inference_data'], dict):
            raise UserTypeError(f"'inference_data' field present but is of type {type(row['inference_data'])}, "
                                f"should be dict")
        if 'ground_truth_data' not in row.keys():
            if intersection_is_non_empty(gt_attrs, row.keys()):
                nested_row['ground_truth_data'] = {}
        elif not isinstance(row['ground_truth_data'], dict):
            raise UserTypeError(f"'ground_truth_data' field present but is of type "
                                f"{type(row['ground_truth_data'])}, should be dict")

        # copy the data into the new struct
        for key in row.keys():
            if key in inference_attrs:
                nested_row['inference_data'][key] = row[key]
            elif key in RESERVED_COLUMNS:
                # copy reserved dict columns since they may be nested
                if isinstance(row[key], dict):
                    nested_row[key] = row[key].copy()
                else:
                    nested_row[key] = row[key]
            elif key in gt_attrs:
                nested_row['ground_truth_data'][key] = row[key]
            else:
                raise UserValueError(f"Unexpected key {key} on row {i} of data")
        nested_data.append(nested_row)

    return nested_data


def add_inference_metadata_to_dataframe(df: pd.DataFrame,
                                        model_attributes: Collection[ArthurAttribute],
                                        ignore_join_errors: bool = FALSE_DEFAULT_IGNORE_JOIN_ERRORS) -> pd.DataFrame:
    """
    Adds timestamp and/or partner_inference_id fields to the DataFrame.
    :param df:
    :param model_attributes:
    :param ignore_join_errors: if True, allow inference data without `partner_inference_id`s or ground truth data
    :return: the input DataFrame if no updates are needed, otherwise a shallow copy with the new columns
    :raise UserValueError: if inference data is supplied without `partner_inference_id`s or ground truth data, and
        `ignore_join_errors` is False.
    """
    # determine whether the dataset contains inference data, ground truth data, or both
    attributes_by_name = {attr.name: attr for attr in model_attributes}
    contains_inference_columns = False
    contains_ground_truth_columns = False
    for col in df.columns:
        if col in attributes_by_name.keys():
            attr = attributes_by_name[col]
            if attr.stage in INFERENCE_STAGES:
                contains_inference_columns = True
            elif attr.stage == Stage.GroundTruth:
                contains_ground_truth_columns = True
        if contains_inference_columns and contains_ground_truth_columns:
            break
    if (not contains_inference_columns) and (not contains_ground_truth_columns):
        raise UserValueError(f"No inference or ground truth data was found in the DataFrame with columns "
                             f"{list(df.columns)}")

    # determine what fields need to be added so that we can avoid copying the DataFrame if there's no work to do
    add_inference_timestamp, add_gt_timestamp, add_partner_ids = False, False, False
    if contains_inference_columns and 'inference_timestamp' not in df.columns:
        add_inference_timestamp = True
    if contains_ground_truth_columns and 'ground_truth_timestamp' not in df.columns:
        add_gt_timestamp = True
    if 'partner_inference_id' not in df.columns:
        # ensure that the customer isn't only supplying ground truth
        if contains_ground_truth_columns and (not contains_inference_columns):
            raise UserValueError(f"Cannot send ground truth data without `partner_inference_id` field to join to "
                                 "existing inference data. Please supply the `partner_inference_id` of the already-"
                                 "uploaded inferences or supply inference data with your ground truth data.")
        add_partner_ids = True

    if not (add_inference_timestamp or add_gt_timestamp or add_partner_ids):
        return df

    if (contains_inference_columns and (not contains_ground_truth_columns) and add_partner_ids
            and (not ignore_join_errors)):
        raise UserValueError(
            "You are sending inference data without `partner_inference_id`s or ground truth data, it will be difficult "
            "to append ground truth data at a later time. If you wish to append ground truth data at a later time "
            "please supply a `partner_inference_id` field to your inferences or use the synchronous send_inferences() "
            "method to auto-generate them, and retain the generated values. If you do not intend to send ground truth "
            "data you may override this error with the 'ignore_join_errors=True' flag.")

    # copy the dataframe and add the needed fields
    df = df.copy()
    current_timestamp = datetime.now(pytz.utc)
    if add_inference_timestamp:
        df['inference_timestamp'] = current_timestamp
        logger.info("inference_timestamp field was not supplied in the DataFrame, so the current time was populated")
    if add_gt_timestamp:
        df['ground_truth_timestamp'] = current_timestamp
        logger.info("ground_truth_timestamp field was not supplied in the DataFrame, so the current time was populated")
    if add_partner_ids:
        df['partner_inference_id'] = [str(shortuuid.uuid()) for _ in range(len(df))]

    return df
