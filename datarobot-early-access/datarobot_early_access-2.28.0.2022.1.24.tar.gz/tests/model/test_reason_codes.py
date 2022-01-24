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

from datarobot import ReasonCodes, ReasonCodesInitialization
from datarobot.models.reason_codes import ReasonCodesPage, ReasonCodesRow


@pytest.fixture
def rci_url(project_collection_url, rci_data):
    return "{}{}/models/{}/reasonCodesInitialization/".format(
        project_collection_url, rci_data["project_id"], rci_data["model_id"]
    )


def test_reason_codes_initialization_future_proof(rci_data):
    ReasonCodesInitialization.from_data(dict(rci_data, future="new"))


def test_reason_codes_future_proof(rc_data):
    ReasonCodes.from_data(dict(rc_data, future="new"))


def test_reason_codes_page_future_proof(rcp_data):
    with patch(
        "datarobot.models.reason_codes.t.URL.check", side_effect=(lambda url, context=None: url)
    ):
        ReasonCodesPage.from_data(dict(rcp_data, future="new"))


@responses.activate
@pytest.mark.usefixtures("known_warning")
def test_reason_codes_initialization_get_returns_valid_data(rci_url, rci_json, one_rci):
    responses.add(
        responses.GET, rci_url, body=rci_json, status=200, content_type="application/json"
    )
    initialization = ReasonCodesInitialization.get(one_rci.project_id, one_rci.model_id)
    assert isinstance(initialization, ReasonCodesInitialization)
    assert initialization.project_id == one_rci.project_id
    assert initialization.model_id == one_rci.model_id
    assert initialization.reason_codes_sample


@responses.activate
@pytest.mark.usefixtures("known_warning")
def test_reason_codes_initialization_create(rci_data, rci_url, project_url, base_job_server_data):
    job_url = "{}jobs/{}/".format(project_url, base_job_server_data["id"])
    responses.add(
        responses.POST,
        rci_url,
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
        adding_headers={"Location": rci_url},
    )

    rci_job = ReasonCodesInitialization.create(
        project_id=rci_data["project_id"], model_id=rci_data["model_id"]
    )
    assert str(rci_job.id) == base_job_server_data["id"]


@responses.activate
@pytest.mark.usefixtures("known_warning")
def test_reason_codes_initialization_delete(rci_url, rci_data):
    responses.add(responses.DELETE, rci_url, status=200)

    rci = ReasonCodesInitialization.from_data(rci_data)
    rci.delete()


@responses.activate
@pytest.mark.usefixtures("known_warning")
def test_reason_codes_get_returns_valid_data(project_id, project_url, rc_json, one_rc):
    url = "{}reasonCodesRecords/{}/".format(project_url, one_rc.id)
    responses.add(responses.GET, url, body=rc_json, status=200, content_type="application/json")
    record = ReasonCodes.get(project_id, one_rc.id)
    assert isinstance(record, ReasonCodes)
    assert record.id == one_rc.id
    assert record.model_id == one_rc.model_id


@responses.activate
def test_reason_codes_page_get_returns_valid_data(project_id, project_url, rcp_json, one_rcp):
    url = "{}reasonCodes/{}/".format(project_url, one_rcp.id)
    responses.add(responses.GET, url, body=rcp_json, status=200, content_type="application/json")
    with patch(
        "datarobot.models.reason_codes.t.URL.check", side_effect=(lambda url, context=None: url)
    ):
        record = ReasonCodesPage.get(project_id, one_rcp.id)
    assert isinstance(record, ReasonCodesPage)
    assert record.id == one_rcp.id
    assert record.data == one_rcp.data
    assert record.adjustment_method == "N/A"


@responses.activate
def test_reason_codes_page_get_returns_valid_data_adjusted(
    project_id, project_url, rcp_data_with_adjusted_predictions, one_rcp
):
    url = "{}reasonCodes/{}/".format(project_url, one_rcp.id)
    responses.add(
        responses.GET,
        url,
        json=rcp_data_with_adjusted_predictions,
        status=200,
        content_type="application/json",
    )
    with patch(
        "datarobot.models.reason_codes.t.URL.check", side_effect=(lambda url, context=None: url)
    ):
        record = ReasonCodesPage.get(project_id, one_rcp.id)
    assert isinstance(record, ReasonCodesPage)
    assert record.id == one_rcp.id
    assert record.data == one_rcp.data
    assert record.adjustment_method == "exposureNormalized"
    for rc_row in record.data:
        assert rc_row["adjusted_prediction"] == rc_row["prediction"]
        assert rc_row["adjusted_prediction_values"] == rc_row["prediction_values"]


@responses.activate
@pytest.mark.usefixtures("known_warning")
def test_reason_codes_create(
    project_id, project_url, project_collection_url, base_job_server_data, rcp_data
):
    rcp_base_url = "{}{}/reasonCodes/".format(project_collection_url, project_id)
    job_url = "{}jobs/{}/".format(project_url, base_job_server_data["id"])
    rcp_url = "{}/{}/".format(rcp_base_url, rcp_data["id"])

    responses.add(
        responses.POST,
        rcp_base_url,
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
        adding_headers={"Location": rcp_url},
    )

    rcp_job = ReasonCodes.create(
        project_id=project_id,
        model_id="578e59a41ced2e5a9eb18960",
        dataset_id="581c6256100d2b60586980d9",
    )
    assert str(rcp_job.id) == base_job_server_data["id"]


@responses.activate
@pytest.mark.usefixtures("known_warning")
def test_reason_codes_list(project_id, project_url, rc_list_json):
    rc_base_url = "{}reasonCodesRecords/".format(project_url)
    responses.add(
        responses.GET,
        rc_base_url + "?modelId=578e59a41ced2e5a9eb18965",
        status=200,
        body=rc_list_json,
        content_type="application/json",
        match_querystring=True,
    )
    rc_list = ReasonCodes.list(project_id, model_id="578e59a41ced2e5a9eb18965")
    assert len(rc_list) == 3
    for rc in rc_list:
        assert isinstance(rc, ReasonCodes)


@responses.activate
@pytest.mark.usefixtures("known_warning")
def test_reason_codes_delete(project_collection_url, project_id, rc_data):
    rc_url = "{}{}/reasonCodesRecords/{}/".format(project_collection_url, project_id, rc_data["id"])
    responses.add(responses.DELETE, rc_url, status=200)

    rc = ReasonCodes.from_data(rc_data)
    rc.delete()


@responses.activate
@pytest.mark.usefixtures("known_warning")
def test_reason_codes_iteration(project_id, project_url, one_rcp):
    url = "{}reasonCodes/{}/".format(project_url, one_rcp.id)
    url_page1 = url + "?offset=0&excludeAdjustedPredictions=true"
    url_page2 = url + "?limit=2&offset=2&excludeAdjustedPredictions=true"
    url_page3 = url + "?limit=2&offset=4&excludeAdjustedPredictions=true"
    resp_data_1 = {
        "id": one_rcp.id,
        "count": 5,
        "previous": None,
        "next": url_page2,
        "data": one_rcp.data[:2],
        "reason_codes_record_location": one_rcp.reason_codes_record_location,
    }
    resp_data_2 = dict(resp_data_1, previous=url_page1, next=url_page3, data=one_rcp.data[2:4])
    resp_data_3 = dict(resp_data_1, previous=url_page2, next=None, data=one_rcp.data[4:5])
    responses.add(responses.GET, url_page1, json=resp_data_1, status=200, match_querystring=True)
    responses.add(responses.GET, url_page2, json=resp_data_2, status=200, match_querystring=True)
    responses.add(responses.GET, url_page3, json=resp_data_3, status=200, match_querystring=True)
    with patch(
        "datarobot.models.reason_codes.t.URL.check", side_effect=(lambda url, context=None: url)
    ):
        reason_codes_rows = list(
            ReasonCodes(one_rcp.id, project_id, "", "", "", 0, 0, "").get_rows()
        )
    assert len(reason_codes_rows) == 5
    for i, row in enumerate(reason_codes_rows):
        assert isinstance(row, ReasonCodesRow)
        assert row.row_id == one_rcp.data[i]["row_id"]
        assert row.prediction == one_rcp.data[i]["prediction"]
        assert row.prediction_values == one_rcp.data[i]["prediction_values"]
        assert row.reason_codes == one_rcp.data[i]["reason_codes"]


@responses.activate
@pytest.mark.usefixtures("known_warning")
def test_reason_codes_as_dataframe_regression(project_url, rcp_data, one_rc):
    url = "{}reasonCodes/{}/".format(project_url, one_rc.id)
    responses.add(responses.GET, url, json=rcp_data, status=200)
    with patch(
        "datarobot.models.reason_codes.t.URL.check", side_effect=(lambda url, context=None: url)
    ):
        reason_codes_as_dataframe = one_rc.get_all_as_dataframe()
    assert isinstance(reason_codes_as_dataframe, pandas.DataFrame)
    rows = rcp_data["count"]
    # 5 columns per reason code, plus prediction and row id
    columns = 5 * one_rc.max_codes + 2
    assert reason_codes_as_dataframe.shape == (rows, columns)


@responses.activate
@pytest.mark.usefixtures("known_warning")
def test_reason_codes_as_dataframe_regression_with_exposure(
    project_url, one_rc, rcp_data_with_adjusted_predictions
):
    url = "{}reasonCodes/{}/".format(project_url, one_rc.id)
    responses.add(responses.GET, url, json=rcp_data_with_adjusted_predictions, status=200)
    with patch(
        "datarobot.models.reason_codes.t.URL.check", side_effect=(lambda url, context=None: url)
    ):
        reason_codes_as_dataframe = one_rc.get_all_as_dataframe()
    assert isinstance(reason_codes_as_dataframe, pandas.DataFrame)
    rows = rcp_data_with_adjusted_predictions["count"]
    # 5 columns per reason code, plus prediction, adjusted prediction and row id
    columns = 5 * one_rc.max_codes + 3
    assert reason_codes_as_dataframe.shape == (rows, columns)


@responses.activate
@pytest.mark.usefixtures("known_warning")
def test_reason_codes_as_dataframe_classification(project_url, rcp_data_classification, one_rc):
    url = "{}reasonCodes/{}/".format(project_url, one_rc.id)
    responses.add(responses.GET, url, json=rcp_data_classification, status=200)
    with patch(
        "datarobot.models.reason_codes.t.URL.check", side_effect=(lambda url, context=None: url)
    ):
        reason_codes_as_dataframe = one_rc.get_all_as_dataframe()
    assert isinstance(reason_codes_as_dataframe, pandas.DataFrame)
    rows = rcp_data_classification["count"]
    # 5 columns per reason code, plus 2 columns per target level, plus row_id and prediction
    columns = (5 * one_rc.max_codes) + (2 * 2) + 2
    assert reason_codes_as_dataframe.shape == (rows, columns)


def test_reason_codes_download_to_csv():
    with patch("datarobot.models.reason_codes.ReasonCodes.get_all_as_dataframe") as rcmock:
        reason_codes = ReasonCodes("fake_id", "fake_project_id", "", "", 3, 0, 0, "")
        reason_codes.download_to_csv("test_file.csv", encoding="ascii")
        rcmock.return_value.to_csv.assert_called_once_with(
            path_or_buf="test_file.csv", header=True, index=False, encoding="ascii"
        )
