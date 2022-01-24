#
# Copyright 2021 DataRobot, Inc. and its affiliates.
#
# All rights reserved.
#
# DataRobot, Inc.
#
# This is proprietary source code of DataRobot, Inc. and its
# affiliates.
#
# Released under the terms of DataRobot Tool and Utility Agreement.
from mock import patch
import pandas
import pytest
import responses

from datarobot import PredictionExplanations, PredictionExplanationsInitialization
from datarobot.models.prediction_explanations import (
    PredictionExplanationsPage,
    PredictionExplanationsRow,
)


@pytest.fixture
def pei_url(project_collection_url, pei_data):
    return "{}{}/models/{}/predictionExplanationsInitialization/".format(
        project_collection_url, pei_data["project_id"], pei_data["model_id"]
    )


def test_prediction_explanations_initialization_future_proof(pei_data):
    PredictionExplanationsInitialization.from_data(dict(pei_data, future="new"))


def test_prediction_explanations_future_proof(pe_data):
    PredictionExplanations.from_data(dict(pe_data, future="new"))


def test_prediction_explanations_page_future_proof(pep_data):
    with patch(
        "datarobot.models.prediction_explanations.t.URL.check",
        side_effect=(lambda url, context=None: url),
    ):
        PredictionExplanationsPage.from_data(dict(pep_data, future="new"))


@responses.activate
def test_prediction_explanations_initialization_get_returns_valid_data(pei_url, pei_json, one_pei):
    responses.add(
        responses.GET, pei_url, body=pei_json, status=200, content_type="application/json"
    )
    initialization = PredictionExplanationsInitialization.get(one_pei.project_id, one_pei.model_id)
    assert isinstance(initialization, PredictionExplanationsInitialization)
    assert initialization.project_id == one_pei.project_id
    assert initialization.model_id == one_pei.model_id
    assert initialization.prediction_explanations_sample


@responses.activate
def test_prediction_explanations_initialization_create(
    pei_data, pei_url, project_url, base_job_server_data
):
    job_url = "{}jobs/{}/".format(project_url, base_job_server_data["id"])
    responses.add(
        responses.POST,
        pei_url,
        body="",
        status=202,
        content_type="application/json",
        adding_headers={"Location": job_url},
    )
    responses.add(
        responses.GET,
        job_url,
        json=base_job_server_data,
        status=303,
        adding_headers={"Location": pei_url},
    )

    pei_job = PredictionExplanationsInitialization.create(
        project_id=pei_data["project_id"], model_id=pei_data["model_id"]
    )
    assert str(pei_job.id) == base_job_server_data["id"]


@responses.activate
def test_prediction_explanations_initialization_delete(pei_url, pei_data):
    responses.add(responses.DELETE, pei_url, status=200)

    pei = PredictionExplanationsInitialization.from_data(pei_data)
    pei.delete()


@responses.activate
def test_prediction_explanations_get_returns_valid_data(project_id, project_url, pe_json, one_pe):
    url = "{}predictionExplanationsRecords/{}/".format(project_url, one_pe.id)
    responses.add(responses.GET, url, body=pe_json, status=200, content_type="application/json")
    record = PredictionExplanations.get(project_id, one_pe.id)
    assert isinstance(record, PredictionExplanations)
    assert record.id == one_pe.id
    assert record.model_id == one_pe.model_id


@responses.activate
def test_prediction_explanations_page_get_returns_valid_data(
    project_id, project_url, pep_json, one_pep
):
    url = "{}predictionExplanations/{}/".format(project_url, one_pep.id)
    responses.add(responses.GET, url, body=pep_json, status=200, content_type="application/json")
    with patch(
        "datarobot.models.prediction_explanations.t.URL.check",
        side_effect=(lambda url, context=None: url),
    ):
        record = PredictionExplanationsPage.get(project_id, one_pep.id)
    assert isinstance(record, PredictionExplanationsPage)
    assert record.id == one_pep.id
    assert record.data == one_pep.data
    assert record.adjustment_method == "N/A"


@responses.activate
def test_prediction_explanations_page_get_returns_valid_data_adjusted(
    project_id, project_url, pep_data_with_adjusted_predictions, one_pep
):
    url = "{}predictionExplanations/{}/".format(project_url, one_pep.id)
    responses.add(
        responses.GET,
        url,
        json=pep_data_with_adjusted_predictions,
        status=200,
        content_type="application/json",
    )
    with patch(
        "datarobot.models.prediction_explanations.t.URL.check",
        side_effect=(lambda url, context=None: url),
    ):
        record = PredictionExplanationsPage.get(project_id, one_pep.id)
    assert isinstance(record, PredictionExplanationsPage)
    assert record.id == one_pep.id
    assert record.data == one_pep.data
    assert record.adjustment_method == "exposureNormalized"
    for pe_row in record.data:
        assert pe_row["adjusted_prediction"] == pe_row["prediction"]
        assert pe_row["adjusted_prediction_values"] == pe_row["prediction_values"]


@responses.activate
def test_prediction_explanations_create(
    project_id, project_url, project_collection_url, base_job_server_data, pep_data
):
    pep_base_url = "{}{}/predictionExplanations/".format(project_collection_url, project_id)
    job_url = "{}jobs/{}/".format(project_url, base_job_server_data["id"])
    pep_url = "{}/{}/".format(pep_base_url, pep_data["id"])

    responses.add(
        responses.POST,
        pep_base_url,
        body="",
        status=202,
        content_type="application/json",
        adding_headers={"Location": job_url},
    )
    responses.add(
        responses.GET,
        job_url,
        json=base_job_server_data,
        status=303,
        adding_headers={"Location": pep_url},
    )

    pep_job = PredictionExplanations.create(
        project_id=project_id,
        model_id="578e59a41ced2e5a9eb18960",
        dataset_id="581c6256100d2b60586980d9",
    )
    assert str(pep_job.id) == base_job_server_data["id"]


@responses.activate
def test_prediction_explanations_list(project_id, project_url, pe_list_json):
    pe_base_url = "{}predictionExplanationsRecords/".format(project_url)
    responses.add(
        responses.GET,
        pe_base_url + "?modelId=578e59a41ced2e5a9eb18965",
        status=200,
        body=pe_list_json,
        content_type="application/json",
        match_querystring=True,
    )
    pe_list = PredictionExplanations.list(project_id, model_id="578e59a41ced2e5a9eb18965")
    assert len(pe_list) == 3
    for pe in pe_list:
        assert isinstance(pe, PredictionExplanations)


@responses.activate
def test_prediction_explanations_delete(project_collection_url, project_id, pe_data):
    pe_url = "{}{}/predictionExplanationsRecords/{}/".format(
        project_collection_url, project_id, pe_data["id"]
    )
    responses.add(responses.DELETE, pe_url, status=200)

    pe = PredictionExplanations.from_data(pe_data)
    pe.delete()


@responses.activate
def test_prediction_explanations_iteration(project_id, project_url, one_pep):
    url = "{}predictionExplanations/{}/".format(project_url, one_pep.id)
    url_page1 = url + "?offset=0&excludeAdjustedPredictions=true"
    url_page2 = url + "?limit=2&offset=2&excludeAdjustedPredictions=true"
    url_page3 = url + "?limit=2&offset=4&excludeAdjustedPredictions=true"
    resp_data_1 = {
        "id": one_pep.id,
        "count": 5,
        "previous": None,
        "next": url_page2,
        "data": one_pep.data[:2],
        "prediction_explanations_record_location": one_pep.prediction_explanations_record_location,
    }
    resp_data_2 = dict(resp_data_1, previous=url_page1, next=url_page3, data=one_pep.data[2:4])
    resp_data_3 = dict(resp_data_1, previous=url_page2, next=None, data=one_pep.data[4:5])
    responses.add(responses.GET, url_page1, json=resp_data_1, status=200, match_querystring=True)
    responses.add(responses.GET, url_page2, json=resp_data_2, status=200, match_querystring=True)
    responses.add(responses.GET, url_page3, json=resp_data_3, status=200, match_querystring=True)
    with patch(
        "datarobot.models.prediction_explanations.t.URL.check",
        side_effect=(lambda url, context=None: url),
    ):
        prediction_explanations_rows = list(
            PredictionExplanations(one_pep.id, project_id, "", "", "", 0, 0, "").get_rows()
        )
    assert len(prediction_explanations_rows) == 5
    for i, row in enumerate(prediction_explanations_rows):
        assert isinstance(row, PredictionExplanationsRow)
        assert row.row_id == one_pep.data[i]["row_id"]
        assert row.prediction == one_pep.data[i]["prediction"]
        assert row.prediction_values == one_pep.data[i]["prediction_values"]
        assert row.prediction_explanations == one_pep.data[i]["prediction_explanations"]


@responses.activate
def test_prediction_explanations_as_dataframe_regression(project_url, pep_data, one_pe):
    url = "{}predictionExplanations/{}/".format(project_url, one_pe.id)
    responses.add(responses.GET, url, json=pep_data, status=200)
    with patch(
        "datarobot.models.prediction_explanations.t.URL.check",
        side_effect=(lambda url, context=None: url),
    ):
        prediction_explanations_as_dataframe = one_pe.get_all_as_dataframe()
    assert isinstance(prediction_explanations_as_dataframe, pandas.DataFrame)
    rows = pep_data["count"]
    # 5 columns per prediction explanation, plus prediction and row id
    columns = 5 * one_pe.max_explanations + 2
    assert prediction_explanations_as_dataframe.shape == (rows, columns)


@responses.activate
def test_prediction_explanations_as_dataframe_regression_with_exposure(
    project_url, one_pe, pep_data_with_adjusted_predictions
):
    url = "{}predictionExplanations/{}/".format(project_url, one_pe.id)
    responses.add(responses.GET, url, json=pep_data_with_adjusted_predictions, status=200)
    with patch(
        "datarobot.models.prediction_explanations.t.URL.check",
        side_effect=(lambda url, context=None: url),
    ):
        prediction_explanations_as_dataframe = one_pe.get_all_as_dataframe()
    assert isinstance(prediction_explanations_as_dataframe, pandas.DataFrame)
    rows = pep_data_with_adjusted_predictions["count"]
    # 5 columns per prediction explanation, plus prediction, adjusted prediction and row id
    columns = 5 * one_pe.max_explanations + 3
    assert prediction_explanations_as_dataframe.shape == (rows, columns)


@responses.activate
def test_prediction_explanations_as_dataframe_classification(
    project_url, pep_data_classification, one_pe
):
    url = "{}predictionExplanations/{}/".format(project_url, one_pe.id)
    responses.add(responses.GET, url, json=pep_data_classification, status=200)
    with patch(
        "datarobot.models.prediction_explanations.t.URL.check",
        side_effect=(lambda url, context=None: url),
    ):
        prediction_explanations_as_dataframe = one_pe.get_all_as_dataframe()
    assert isinstance(prediction_explanations_as_dataframe, pandas.DataFrame)
    rows = pep_data_classification["count"]
    # 5 columns per explanation, plus 2 columns per target level, plus row_id and prediction
    columns = (5 * one_pe.max_explanations) + (2 * 2) + 2
    assert prediction_explanations_as_dataframe.shape == (rows, columns)
    for idx, row in prediction_explanations_as_dataframe.iterrows():
        assert "class_0_label" in row
        assert row["class_0_label"] == 0


def test_prediction_explanations_download_to_csv():
    patch_target = (
        "datarobot.models.prediction_explanations.PredictionExplanations.get_all_as_dataframe"
    )
    with patch(patch_target) as pemock:
        prediction_explanations = PredictionExplanations(
            "fake_id", "fake_project_id", "", "", 3, 0, 0, ""
        )
        prediction_explanations.download_to_csv("test_file.csv", encoding="ascii")
        pemock.return_value.to_csv.assert_called_once_with(
            path_or_buf="test_file.csv", header=True, index=False, encoding="ascii"
        )
