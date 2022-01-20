import json
import os
from datetime import datetime, timezone
import numpy as np
import pandas as pd

from mock import patch, mock_open, MagicMock
import pytest
import responses

from tests.fixtures.models import regression as reg, multiclass as mclass
from tests.fixtures.models.regression import initial_batch_model as reg_initial_batch_model, \
    unsaved_batch_model as reg_unsaved_batch_model, streaming_model
from tests.fixtures.models.multiclass import initial_biclass_model
from tests.fixtures.mocks import client

from arthurai.common.constants import ValueType, Stage, InputType, OutputType, ImageResponseType, ImageContentType
from arthurai.core.attributes import AttributeCategory, AttributeBin, ArthurAttribute
from arthurai.core.models import ArthurModel
import arthurai.core.util as core_util
from arthurai.common.exceptions import UserValueError, MethodNotApplicableError, ArthurInternalError
from tests.helpers import mock_get, assert_attributes_equal, mock_post, mock_get
from tests.test_request_models.fixtures import model_response_json_strings


@responses.activate
def test_send_parquet_file():
    input_dict = {
        "attr1": np.Inf,
        "attr2": "string1",
        "attr3": 3.44,
        "attr4": True,
        "attr5": np.nan,
        "attr6": -np.inf,
        "attr7": "string2",
        "attr8": None,
        "attr9": "",
        "attr10": np.inf,
    }
    expected_dict = {
        "attr1": None,
        "attr2": "string1",
        "attr3": 3.44,
        "attr4": True,
        "attr5": None,
        "attr6": None,
        "attr7": "string2",
        "attr8": None,
        "attr9": "",
        "attr10": None,
    }
    output_dict = ArthurModel._replace_nans_and_infinities_in_dict(input_dict)
    assert expected_dict == output_dict


def test_replace_nans_none_type():
    output_dict = ArthurModel._replace_nans_and_infinities_in_dict(None)
    assert output_dict is None


def test_standardize_pd_obj_for_nans():
    input_df = pd.DataFrame(
        [
            [1, 2, 3., 4, 5, 6, np.inf, np.nan, 1, 1],
            [7, 8, 9., 1, 2, 3, np.nan, -np.inf, 2, 2],
            [4, 5.5, 9., -np.inf, np.nan, np.Inf, np.nan, np.nan, np.nan, np.nan],
        ],
        columns = ["x0", "x1", "x2", "x3", "x4", "x5", "x6", "x7", "x8", "x9"]
    )
    expected_df = pd.DataFrame(
        [
            [1, 2, 3., 4, 5, 6, np.nan, np.nan, 1, 1],
            [7, 8, 9., 1, 2, 3, np.nan, np.nan, 2, 2],
            [4, 5.5, 9., np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],
        ],
        columns = ["x0", "x1", "x2", "x3", "x4", "x5", "x6", "x7", "x8", "x9"]
    )
    expected_df.x3 = expected_df.x3.astype(pd.Int64Dtype())
    expected_df.x4 = expected_df.x4.astype(pd.Int64Dtype())
    expected_df.x5 = expected_df.x5.astype(pd.Int64Dtype())

    attributes = {
        "x3": ValueType.Integer,
        "x4": ValueType.Integer,
        "x5": ValueType.Integer,
        "x8": ValueType.Float,
    }

    assert expected_df.equals(
        core_util.standardize_pd_obj(input_df, dropna=False, replacedatetime=False, attributes=attributes)
    )
    with pytest.raises(ValueError):
        assert expected_df.equals(
            core_util.standardize_pd_obj(input_df, dropna=True, replacedatetime=False, attributes=attributes)
        )


def test_standardize_pd_obj_for_series():
    input_series = [
        pd.Series([1, 2, 3]),
        pd.Series([1., 2., 3.]),
        pd.Series([1, 2, np.Inf], name="x1"),
        pd.Series([1, 2, np.Inf], name="x1"),
        pd.Series([1, 2, np.Inf], name="x1"),
        pd.Series([np.nan, -np.inf, np.inf]),
    ]
    input_attributes = [
        {},
        None,
        {"x1": ValueType.Integer},
        {"x1": ValueType.Float},
        {"x2": ValueType.Integer},
        {}
    ]
    expected_undropped_series = [
        pd.Series([1, 2, 3]),
        pd.Series([1., 2., 3.]),
        pd.Series([1, 2, np.nan]).astype(pd.Int64Dtype()),
        pd.Series([1, 2, np.nan]),
        pd.Series([1, 2, np.nan]),
        pd.Series([np.nan, np.nan, np.nan]),
    ]
    expected_dropped_series = [
        pd.Series([1, 2, 3]),
        pd.Series([1., 2., 3.]),
        pd.Series([1, 2]).astype(pd.Int64Dtype()),
        pd.Series([1, 2.]),
        pd.Series([1, 2.]),
        pd.Series([]),
    ]

    for inp, inp_attributes, exp_undropped, exp_dropped in zip(input_series, input_attributes, expected_undropped_series, expected_dropped_series):
        print(inp_attributes)
        assert exp_undropped.equals(
            core_util.standardize_pd_obj(inp, dropna=False, replacedatetime=False, attributes=inp_attributes)
        )
        assert exp_dropped.equals(
            core_util.standardize_pd_obj(inp, dropna=True, replacedatetime=False, attributes=inp_attributes)
        )


def test_standardize_pd_obj_bad_input():
    for inp in ["string", "", 123, [1,2,3], {"key": "value"}]:
        with pytest.raises(TypeError):
            core_util.standardize_pd_obj(inp, dropna=True, replacedatetime=False)


def test_standardize_pd_obj_for_datetimes():
    unaware_timestamp = datetime(2021, 2, 8, 12, 10, 5)
    aware_timestamp = datetime(2021, 2, 8, 12, 10, 5, tzinfo=timezone.utc)
    timestamp_to_expected_output = (
        (unaware_timestamp, ValueError),
        (aware_timestamp, "2021-02-08T12:10:05Z"),
    )

    for timestamp, expected_output in timestamp_to_expected_output:
        if isinstance(expected_output, str):
            actual_output = core_util.standardize_pd_obj(pd.Series([timestamp]), dropna=False, replacedatetime=True)
            assert expected_output == actual_output.values[0]
        else:
            with pytest.raises(expected_output):
                core_util.standardize_pd_obj(pd.Series([timestamp]), dropna=False, replacedatetime=True)


def test_add_attribute_with_categories():
    model = ArthurModel.from_json(model_response_json_strings[2])
    model.add_attribute(
        name="test_categorical_1",
        value_type=ValueType.Integer,
        stage=Stage.ModelPipelineInput,
        categorical=True,
        categories=[1, 2, 3, 4],
    )
    attr = model.get_attribute(name="test_categorical_1")
    assert len(attr.categories) == 4
    assert isinstance(attr.categories[0], AttributeCategory)

    model.add_attribute(
        name="test_categorical_2",
        value_type=ValueType.Integer,
        stage=Stage.ModelPipelineInput,
        categorical=True,
        categories=[AttributeCategory(value="hello")],
    )
    attr = model.get_attribute(name="test_categorical_2")
    assert len(attr.categories) == 1
    assert isinstance(attr.categories[0], AttributeCategory)
    assert attr.categories[0].value == "hello"


def test_add_attribute_with_bins():
    model = ArthurModel.from_json(model_response_json_strings[2])
    model.add_attribute(
        name="test_bins_1",
        value_type=ValueType.Integer,
        stage=Stage.ModelPipelineInput,
        categorical=True,
        bins=[None, 10, 15, 20, None],
    )
    attr = model.get_attribute(name="test_bins_1")
    assert len(attr.bins) == 4
    assert isinstance(attr.bins[0], AttributeBin)
    assert attr.bins[0].continuous_start is None
    assert attr.bins[0].continuous_end == 10

    model.add_attribute(
        name="test_bins_2",
        value_type=ValueType.Integer,
        stage=Stage.ModelPipelineInput,
        categorical=True,
        bins=[
            AttributeBin(continuous_start=None, continuous_end=10),
            AttributeBin(continuous_start=10, continuous_end=15),
            AttributeBin(continuous_start=15, continuous_end=20),
        ],
    )
    attr = model.get_attribute(name="test_bins_2")
    assert len(attr.bins) == 3
    assert isinstance(attr.bins[0], AttributeBin)
    assert attr.bins[0].continuous_start is None
    assert attr.bins[0].continuous_end == 10


def test_add_nlp_attribute():
    model = ArthurModel(
        partner_model_id="test",
        client=None,
        input_type=InputType.NLP,
        output_type=OutputType.Multiclass,
    )
    ref_data = pd.DataFrame(
        {"input_text": ["hello", "hi", "what's up", "yo", "cool"],}
    )
    model.infer_schema(ref_data, stage=Stage.ModelPipelineInput)

    assert (
        model.get_attribute("input_text").value_type == ValueType.Unstructured_Text
    )
    assert model.get_attribute("input_text").categories is None


def test_all_null_column():
    model = ArthurModel(
        partner_model_id="test",
        client=None,
        input_type=InputType.NLP,
        output_type=OutputType.Multiclass,
    )
    df = pd.DataFrame({'col1': [1], 'col2': [float("nan")]})
    model.infer_schema(df, stage=Stage.ModelPipelineInput)

    expected_attributes = [
        ArthurAttribute(name='col1', value_type=ValueType.Integer, stage=Stage.ModelPipelineInput, position=0,
                        categorical=True, categories=[AttributeCategory(value='1', label=None)], is_unique=False),
        ArthurAttribute(name='col2', value_type=ValueType.Float, stage=Stage.ModelPipelineInput, position=1,
                        categorical=False, is_unique=False)]

    assert model.attributes == expected_attributes


def test_nonzero_index_column():
    model = ArthurModel(
        partner_model_id="test",
        client=None,
        input_type=InputType.NLP,
        output_type=OutputType.Multiclass,
    )
    df = pd.DataFrame({'col1': [1], 'col2': [float("nan")]})
    df.index = [5]
    model.infer_schema(df, stage=Stage.ModelPipelineInput)

    expected_attributes = [
        ArthurAttribute(name='col1', value_type=ValueType.Integer, stage=Stage.ModelPipelineInput, position=0,
                        categorical=True, categories=[AttributeCategory(value='1', label=None)], is_unique=False),
        ArthurAttribute(name='col2', value_type=ValueType.Float, stage=Stage.ModelPipelineInput, position=1,
                        categorical=False, is_unique=False)]

    assert model.attributes == expected_attributes


def test_infer_numerical_string():
    model = ArthurModel(
        partner_model_id="test",
        client=None,
        input_type=InputType.Tabular,
        output_type=OutputType.Multiclass,
    )
    df = pd.DataFrame({'col1': ["0", "1", "0", "1", "1", "0"], 'col2': ["0.0", "1.0", "0.0", "1.0", "1.0", "0.0"]})
    model.infer_schema(df, stage=Stage.ModelPipelineInput)

    expected_attributes = [
        ArthurAttribute(name='col1', value_type=ValueType.String, stage=Stage.ModelPipelineInput, position=0,
                        categorical=True, categories=[AttributeCategory(value='0', label=None),
                                                      AttributeCategory(value='1', label=None)], is_unique=False),
        ArthurAttribute(name='col2', value_type=ValueType.String, stage=Stage.ModelPipelineInput, position=1,
                        categorical=True, categories=[AttributeCategory(value='0.0', label=None),
                                                      AttributeCategory(value='1.0', label=None)], is_unique=False)
    ]

    assert_attributes_equal(expected_attributes, model.attributes)


def test_infer_string_categorical_dtype():
    model = ArthurModel(
        partner_model_id="test",
        client=None,
        input_type=InputType.Tabular,
        output_type=OutputType.Multiclass
    )

    df = pd.DataFrame({"col1": list("abca"), "col2": list("bccd")}, dtype="category")
    model.infer_schema(df, stage=Stage.ModelPipelineInput)

    expected_attributes = [
        ArthurAttribute(name='col1', value_type=ValueType.String, stage=Stage.ModelPipelineInput, position=0,
                        categorical=True, categories=[AttributeCategory(value='a', label=None),
                                                      AttributeCategory(value='b', label=None),
                                                      AttributeCategory(value='c', label=None)], is_unique=False),
        ArthurAttribute(name='col2', value_type=ValueType.String, stage=Stage.ModelPipelineInput, position=1,
                        categorical=True, categories=[AttributeCategory(value='d', label=None),
                                                      AttributeCategory(value='b', label=None),
                                                      AttributeCategory(value='c', label=None)], is_unique=False)
    ]
    assert_attributes_equal(expected_attributes, model.attributes)


def test_infer_int_categorical_dtype():
    model = ArthurModel(
        partner_model_id="test",
        client=None,
        input_type=InputType.Tabular,
        output_type=OutputType.Multiclass
    )

    df = pd.DataFrame({"col1": [1, 0, 0, 1], "col2": [1, 2, 1, 0]}, dtype="category")
    model.infer_schema(df, stage=Stage.ModelPipelineInput)

    expected_attributes = [
        ArthurAttribute(name='col1', value_type=ValueType.Integer, stage=Stage.ModelPipelineInput, position=0,
                        categorical=True, categories=[AttributeCategory(value='0', label=None),
                                                      AttributeCategory(value='1', label=None)], is_unique=False),
        ArthurAttribute(name='col2', value_type=ValueType.Integer, stage=Stage.ModelPipelineInput, position=1,
                        categorical=True, categories=[AttributeCategory(value='0', label=None),
                                                      AttributeCategory(value='1', label=None),
                                                      AttributeCategory(value='2', label=None)], is_unique=False)
    ]
    assert_attributes_equal(expected_attributes, model.attributes)


def test_set_categorical_value_labels():
    model = ArthurModel.from_json(model_response_json_strings[2])
    model.add_attribute(
        name="test_categorical_1",
        value_type=ValueType.Integer,
        stage=Stage.ModelPipelineInput,
        categorical=True,
        categories=[1, 2],
    )
    expected_categories = {1: "Male", 2: "Female"}
    model.set_attribute_labels("test_categorical_1", labels=expected_categories)
    cats = model.get_attribute("test_categorical_1").categories
    for category in cats:
        assert int(category.value) in expected_categories
        assert expected_categories[int(category.value)] == category.label


@responses.activate
def test_get_image(client):
    model = ArthurModel(client=client.client,
                        partner_model_id="test",
                        input_type=InputType.Image,
                        output_type=OutputType.Multiclass)
    model.id = '1234567890abcdef'
    image_id = '0a1b2c3d4e5f9687'
    path = '.'
    type = ImageResponseType.RawImage
    file_ext = '.png'
    response_content = 'content'.encode()
    expected_image_file = f"{path}/{type}_{image_id}{file_ext}"

    mock_get(f"/api/v3/models/{model.id}/inferences/images/{image_id}?type={type}", response_content,
             headers={'Content-Type': ImageContentType.Png})
    open_mock = mock_open()
    with patch("arthurai.core.models.open", open_mock, create=True):
        resulting_file = model.get_image(image_id, path, type=type)

    assert resulting_file == expected_image_file
    open_mock.assert_called_with(expected_image_file, 'wb')
    open_mock.return_value.write.assert_called_once_with(response_content)


def test_add_object_detection_output_attributes():
    model = ArthurModel(
        partner_model_id="test",
        client=None,
        input_type=InputType.Image,
        output_type=OutputType.Multiclass,
    )

    # cannot call without proper types
    with pytest.raises(MethodNotApplicableError):
        model.add_object_detection_output_attributes('pred', 'gt', ['class_1', 'class_2'])
    model.input_type = InputType.NLP
    model.output_type = OutputType.ObjectDetection
    with pytest.raises(MethodNotApplicableError):
        model.add_object_detection_output_attributes('pred', 'gt', ['class_1', 'class_2'])

    # cannot call without classes
    model.output_type = OutputType.ObjectDetection
    model.input_type = InputType.Image
    with pytest.raises(UserValueError):
        model.add_object_detection_output_attributes('pred', 'gt', [])

    # names cannot match
    with pytest.raises(UserValueError):
        model.add_object_detection_output_attributes('pred', 'pred', ['class_1', 'class_2'])

    # happy path
    model.add_object_detection_output_attributes('pred', 'gt', ['class_1', 'class_2'])
    assert model.get_attribute('pred').value_type == ValueType.BoundingBox
    assert model.get_attribute('gt').value_type == ValueType.BoundingBox
    assert model.image_class_labels == ['class_1', 'class_2']


def test_build_tabular_model(reg_initial_batch_model):
    pred_gt_map = {reg.PRED: reg.GROUND_TRUTH}
    reg_initial_batch_model.build(data=reg.SAMPLE_DATAFRAME, pred_to_ground_truth_map=pred_gt_map,
                                  non_input_columns=[reg.FLOAT_NONINPUT])

    assert_attributes_equal(reg_initial_batch_model.attributes, reg.MODEL_ATTRIBUTES)
    pd.testing.assert_frame_equal(reg_initial_batch_model.reference_dataframe, reg.SAMPLE_DATAFRAME)


def test_build_tabular_class_model(initial_biclass_model):
    pred_gt_map = {mclass.DOG_PRED: mclass.DOG_GROUND_TRUTH, mclass.CAT_PRED: mclass.CAT_GROUND_TRUTH}
    initial_biclass_model.build(data=mclass.SAMPLE_DATAFRAME, pred_to_ground_truth_map=pred_gt_map,
                                non_input_columns=[mclass.FLOAT_NONINPUT], positive_predicted_attr=mclass.DOG_PRED)

    assert_attributes_equal(initial_biclass_model.attributes, mclass.MODEL_ATTRIBUTES)
    pd.testing.assert_frame_equal(initial_biclass_model.reference_dataframe, mclass.SAMPLE_DATAFRAME)


def test_build_tabular_model_no_refset(reg_unsaved_batch_model):
    pred_gt_map = {reg.PRED: reg.GROUND_TRUTH}
    reg_unsaved_batch_model.build(data=reg.SAMPLE_DATAFRAME, pred_to_ground_truth_map=pred_gt_map,
                                  non_input_columns=[reg.FLOAT_NONINPUT], set_reference_data=False)

    assert_attributes_equal(reg_unsaved_batch_model.attributes, reg.MODEL_ATTRIBUTES)
    assert reg_unsaved_batch_model.reference_dataframe is None


def test_build_nlp():
    model = ArthurModel(
        partner_model_id="test",
        client=None,
        input_type=InputType.NLP,
        output_type=OutputType.Regression,
    )
    ref_data = pd.DataFrame({"input_text": ["hello there", "hi", "what's up", "yo", "cool"],
                             "pred": [90, 80, 50, 31, 26],
                             "gt": [95, 81, 42, 30, 30]})
    model.build(ref_data, pred_to_ground_truth_map={"pred": "gt"})

    assert model.get_attribute("input_text").value_type == ValueType.Unstructured_Text
    assert model.get_attribute("input_text").categories is None
    pd.testing.assert_frame_equal(model.reference_dataframe, ref_data)


def test_build_image():
    model = ArthurModel(
        partner_model_id="test",
        client=None,
        input_type=InputType.Image,
        output_type=OutputType.Regression,
    )
    data = pd.DataFrame({'image': ["path1", "path2"], 'preds': [15.2, 31.6], 'gt': [12, 40]})
    model.build(data, pred_to_ground_truth_map={'preds': 'gt'})

    assert model.get_attribute("image").value_type == ValueType.Image
    assert model.get_attribute("image").categories is None
    pd.testing.assert_frame_equal(model.reference_dataframe, data)


def test_build_object_detection():
    model = ArthurModel(
        partner_model_id="test",
        client=None,
        input_type=InputType.Image,
        output_type=OutputType.ObjectDetection,
    )
    # not actually valid object data but that's okay
    data = pd.DataFrame({'image': ["path1", "path2"], 'preds': [0.8, 0.3], 'gt': [1, 0]})
    with pytest.raises(MethodNotApplicableError):
        model.build(data, pred_to_ground_truth_map={'preds': 'gt'})


@responses.activate
def test_save_model_with_refset(reg_unsaved_batch_model):
    reg_unsaved_batch_model.reference_dataframe = reg.SAMPLE_DATAFRAME
    mock_set_ref_data = MagicMock()
    reg_unsaved_batch_model.set_reference_data = mock_set_ref_data
    mock_post("/api/v3/models", response_body={'id': reg.TABULAR_MODEL_ID}, status=201)

    reg_unsaved_batch_model.save()

    mock_set_ref_data.assert_called_once_with(data=reg.SAMPLE_DATAFRAME)
    assert len(responses.calls) == 1
    assert os.getenv("ARTHUR_LAST_MODEL_ID") == reg.TABULAR_MODEL_ID


@responses.activate
def test_save_model_no_refset(reg_unsaved_batch_model):
    mock_set_ref_data = MagicMock()
    reg_unsaved_batch_model.set_reference_data = mock_set_ref_data
    mock_post("/api/v3/models", response_body={'id': reg.TABULAR_MODEL_ID}, status=201)

    reg_unsaved_batch_model.save()

    mock_set_ref_data.assert_not_called()
    assert len(responses.calls) == 1
    assert os.getenv("ARTHUR_LAST_MODEL_ID") == reg.TABULAR_MODEL_ID


def test_add_attribute_positions(reg_unsaved_batch_model):
    reg_unsaved_batch_model.infer_schema(reg.SAMPLE_DATAFRAME[reg.INT_INPUT], stage=Stage.ModelPipelineInput)
    reg_unsaved_batch_model.infer_schema(reg.SAMPLE_DATAFRAME[reg.FLOAT_NONINPUT], stage=Stage.NonInputData)
    reg_unsaved_batch_model.add_regression_output_attributes({reg.PRED: reg.GROUND_TRUTH}, value_type=ValueType.Integer)
    # there is one actual attribute in each stage so should be two in each with duplicates
    expected_attr_positions = {0, 1}
    for stage in (Stage.ModelPipelineInput, Stage.NonInputData, Stage.PredictedValue, Stage.GroundTruth):
        actual_attr_positions = [attr.position for attr in reg_unsaved_batch_model.attributes if attr.stage == stage]
        assert len(actual_attr_positions) == len(expected_attr_positions)
        assert set(actual_attr_positions) == expected_attr_positions


@responses.activate
def test_find_hotspots(streaming_model):
    model = streaming_model

    response_body = {'data': [{'rules': {},
                               'gt_to_info': {'-1': {'class_f1': 0.8870523415977962,
                                                     'class_precision': 0.8298969072164949,
                                                     'class_recall': 0.9526627218934911,
                                                     'count': 169,
                                                     'pred_to_count': {'-1': 161, '1': 8}},
                                              '1': {'class_f1': 0.9356357927786499,
                                                    'class_precision': 0.9738562091503268,
                                                    'class_recall': 0.9003021148036254,
                                                    'count': 331,
                                                    'pred_to_count': {'-1': 33, '1': 298}}},
                               'precision': 0.9251979650966916,
                               'recall': 0.918,
                               'f1': 0.9192145862795214,
                               'accuracy': 0.918,
                               'impurity': 0.15055200000000002,
                               'n_samples': 500,
                               'feature': 'x2',
                               'cutoff': -3.560836390126483}]}

    mock_get(f"/api/v3/models/{model.id}/enrichments/hotspots/find?metric=f1&threshold=0.999&date=2021-08-04",
             response_body=response_body, status=200)
    model.find_hotspots(metric="f1", threshold=0.999, date="2021-08-04")
    assert len(responses.calls) == 1


@responses.activate
def test_query(streaming_model):
    query_body = {"property": "my_base_prop"}
    response_body = {'query_result': "base query response"}
    mock_post(f"/api/v3/models/{streaming_model.id}/inferences/query",
              response_body=response_body, status=200)

    streaming_model.query(query_body)

    assert len(responses.calls) == 1
    assert responses.calls[0].request.body == json.dumps(query_body)


@responses.activate
def test_query_psi_buckets(streaming_model):
    query_body = {"property": "my_psi_prop"}
    response_body = {'query_result': "psi bucket response"}
    mock_post(f"/api/v3/models/{streaming_model.id}/inferences/query/data_drift_psi_bucket_calculation_table",
              response_body=response_body, status=200)

    streaming_model.query(query_body, query_type="drift_psi_bucket_table")

    # assert request body was query
    assert len(responses.calls) == 1
    assert responses.calls[0].request.body == json.dumps(query_body)


@responses.activate
def test_query_bad_type(streaming_model):
    query_body = {"property": "my_prop"}
    with pytest.raises(UserValueError):
        streaming_model.query(query_body, query_type="foobar")
