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
import json

import pytest
import responses

from datarobot import Project
from datarobot.enums import JOB_TYPE
from datarobot.errors import ClientError, InputNotUnderstoodError, JobAlreadyRequested
from datarobot.models.rating_table import RatingTable


@pytest.fixture
def rating_table_url(project_collection_url, rating_table_backend_generated_json):
    d = json.loads(rating_table_backend_generated_json)
    return "{}{}/ratingTables/{}/".format(project_collection_url, d["projectId"], d["id"])


@pytest.fixture
def downloaded_rating_table_contents():
    return b"""Matrix of word-grams occurrences tokenizer: scikit-learn based tokenizer
Matrix of word-grams occurrences binary: True
Matrix of word-grams occurrences sublinear_tf: False
Matrix of word-grams occurrences use_idf: False
Matrix of word-grams occurrences norm: L2
Intercept: -0.35839674349
Model precision: single
Loss distribution: Binomial Deviance
Link function: logit
Pairwise interactions found:
( number_emergency & number_inpatient ),0.0065962098320561146
( glyburide & number_emergency ),0.0016387530180316434

Feature Name,Feature Strength,Type,Transform1,Value1,Transform2,Value2,Weight,Coefficient
A1Cresult,0.0012348212995812102,CAT,One-hot,'>7',,,58.0,0.0082157774356443683
A1Cresult,0.0012348212995812102,CAT,One-hot,'>8',,,129.0,-0.012579536153936071
A1Cresult,0.0012348212995812102,CAT,One-hot,'Norm',,,59.0,0.032774696491885628
A1Cresult,0.0012348212995812102,CAT,One-hot,Missing value,,,1354.0,-0.00029931592903424328"""


@pytest.fixture
def downloaded_rating_table_file(temporary_file, downloaded_rating_table_contents):
    with open(temporary_file, "wb") as out_f:
        out_f.write(downloaded_rating_table_contents)
    return temporary_file


@pytest.fixture
def completed_rating_table_validation_job(job_id, project_id, job_url):
    return {
        "status": "COMPLETED",
        "url": job_url,
        "id": job_id,
        "jobType": JOB_TYPE.RATING_TABLE_VALIDATION,
        "isBlocked": False,
        "projectId": project_id,
    }


@responses.activate
def test_get_rating_table_backend_generated(
    rating_table_backend_generated_json, rating_table_backend_generated
):
    backend_generated_id = rating_table_backend_generated.id
    url = "https://host_name.com/projects/p-id/ratingTables/{}/".format(backend_generated_id)

    responses.add(
        responses.GET,
        url,
        body=rating_table_backend_generated_json,
        status=200,
        content_type="application/json",
    )

    table = RatingTable.get("p-id", backend_generated_id)
    assert isinstance(table, RatingTable)
    assert table.id == backend_generated_id
    assert not table.validation_job_id
    assert table.model_id


@responses.activate
def test_get_rating_table_not_modeled(
    rating_table_uploaded_but_not_modeled_json, rating_table_uploaded_but_not_modeled
):
    not_modeled_id = rating_table_uploaded_but_not_modeled.id
    url = "https://host_name.com/projects/p-id/ratingTables/{}/".format(not_modeled_id)

    responses.add(
        responses.GET,
        url,
        body=rating_table_uploaded_but_not_modeled_json,
        status=200,
        content_type="application/json",
    )
    table = RatingTable.get("p-id", not_modeled_id)
    assert isinstance(table, RatingTable)
    assert table.id == not_modeled_id
    assert table.validation_job_id
    assert not table.model_id


@responses.activate
def test_get_rating_table_modeled(
    rating_table_uploaded_and_modeled_json, rating_table_uploaded_and_modeled
):
    modeled_id = rating_table_uploaded_and_modeled.id
    url = "https://host_name.com/projects/p-id/ratingTables/{}/".format(modeled_id)

    responses.add(
        responses.GET,
        url,
        body=rating_table_uploaded_and_modeled_json,
        status=200,
        content_type="application/json",
    )
    table = RatingTable.get("p-id", modeled_id)
    assert isinstance(table, RatingTable)
    assert table.id == modeled_id
    assert table.validation_job_id
    assert table.model_id


@responses.activate
@pytest.mark.usefixtures("known_warning")
def test_get_invalid_rating_table_is_fine_but_warns(
    invalid_rating_table_json, invalid_rating_table
):
    modeled_id = invalid_rating_table.id
    url = "https://host_name.com/projects/p-id/ratingTables/{}/".format(modeled_id)

    responses.add(
        responses.GET,
        url,
        body=invalid_rating_table_json,
        status=200,
        content_type="application/json",
    )
    table = RatingTable.get("p-id", modeled_id)
    assert isinstance(table, RatingTable)
    assert table.id == modeled_id
    assert table.validation_job_id
    assert table.model_id


@responses.activate
@pytest.mark.usefixtures("known_warning")
def test_get_invalid_rating_table_from_job_warns(
    project_url,
    rating_table_url,
    invalid_rating_table_json,
    downloaded_rating_table_file,
    invalid_rating_table,
    completed_rating_table_validation_job,
    job_url,
):
    server_data = json.loads(invalid_rating_table_json)
    create_url = "{}ratingTables/".format(project_url)
    responses.add(
        responses.POST,
        create_url,
        body="",
        status=202,
        content_type="application/json",
        adding_headers={"Location": job_url},
    )
    responses.add(
        responses.GET,
        job_url,
        json=completed_rating_table_validation_job,
        status=303,
        adding_headers={"Location": rating_table_url},
    )
    responses.add(
        responses.GET,
        rating_table_url,
        body=invalid_rating_table_json,
        status=200,
        content_type="application/json",
    )
    job = RatingTable.create(
        server_data["projectId"], invalid_rating_table.model_id, downloaded_rating_table_file
    )
    table = job.get_result_when_complete()
    assert isinstance(table, RatingTable)
    assert table.validation_job_id
    assert table.model_id


@responses.activate
def test_list_with_invalid_rating_table_does_not_warn(project_url, invalid_rating_table_json):
    server_data = json.loads(invalid_rating_table_json)
    list_url = "{}ratingTables/".format(project_url)
    responses.add(
        responses.GET,
        list_url,
        body=json.dumps({"data": [server_data]}),
        status=200,
        content_type="application/json",
    )
    rating_tables = Project(server_data["projectId"]).get_rating_tables()
    table = rating_tables[0]
    assert isinstance(table, RatingTable)
    assert table.validation_job_id
    assert table.model_id


@responses.activate
def test_get_rating_table_not_found(rating_table_uploaded_and_modeled):
    modeled_id = rating_table_uploaded_and_modeled.id
    url = "https://host_name.com/projects/p-id/ratingTables/{}/".format(modeled_id)

    responses.add(
        responses.GET,
        url,
        body=json.dumps({"message": "This resource does not exist."}),
        status=404,
        content_type="application/json",
    )
    with pytest.raises(ClientError):
        RatingTable.get("p-id", modeled_id)


@responses.activate
def test_download_model_export(
    temporary_file, downloaded_rating_table_contents, rating_table_uploaded_and_modeled
):
    pid = rating_table_uploaded_and_modeled.project_id
    id = rating_table_uploaded_and_modeled.id
    url = "https://host_name.com/projects/{}/ratingTables/{}/file".format(pid, id)

    responses.add(responses.GET, url, body=downloaded_rating_table_contents)

    rating_table_uploaded_and_modeled.download(temporary_file)

    with open(temporary_file, "rb") as in_f:
        saved_code = in_f.read()
    assert saved_code == downloaded_rating_table_contents


@responses.activate
def test_create(
    project_url,
    base_job_server_data,
    rating_table_url,
    downloaded_rating_table_file,
    rating_table_backend_generated,
):
    url = "{}ratingTables/".format(project_url)
    job_url = "{}jobs/{}/".format(project_url, base_job_server_data["id"])
    responses.add(
        responses.POST,
        url,
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
        adding_headers={"Location": rating_table_url},
    )

    job = RatingTable.create(
        base_job_server_data["projectId"],
        rating_table_backend_generated.model_id,
        downloaded_rating_table_file,
    )
    assert str(job.id) == base_job_server_data["id"]


@responses.activate
def test_create_from_file(
    project_url,
    base_job_server_data,
    rating_table_url,
    rating_table_backend_generated,
    downloaded_rating_table_file,
):
    url = "{}ratingTables/".format(project_url)
    job_url = "{}jobs/{}/".format(project_url, base_job_server_data["id"])
    responses.add(
        responses.POST,
        url,
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
        adding_headers={"Location": rating_table_url},
    )

    job = RatingTable.create(
        base_job_server_data["projectId"],
        rating_table_backend_generated.model_id,
        downloaded_rating_table_file,
    )
    assert str(job.id) == base_job_server_data["id"]


@responses.activate
def test_create_invalid_sourcedata(base_job_server_data, rating_table_backend_generated):
    with pytest.raises(InputNotUnderstoodError):
        RatingTable.create(
            base_job_server_data["projectId"],
            rating_table_backend_generated.model_id,
            "Not real Rating Table content",
        )


@responses.activate
def test_create_bad_parent_model(project_url, base_job_server_data, downloaded_rating_table_file):
    url = "{}ratingTables/".format(project_url)
    responses.add(
        responses.POST,
        url,
        body=json.dumps({"message": "No existing rating table in the model"}),
        status=400,
        content_type="application/json",
    )

    with pytest.raises(ClientError):
        RatingTable.create(
            base_job_server_data["projectId"],
            "999999999999999999999999",
            downloaded_rating_table_file,
        )


@responses.activate
def test_create_model(
    rating_table_uploaded_but_not_modeled, base_job_server_data, rating_table_model_url, project_url
):
    url = "{}ratingTableModels/".format(project_url)
    job_url = "{}jobs/{}/".format(project_url, base_job_server_data["id"])
    responses.add(
        responses.POST,
        url,
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
        adding_headers={"Location": rating_table_model_url},
    )

    job = rating_table_uploaded_but_not_modeled.create_model()
    assert str(job.id) == base_job_server_data["id"]


@responses.activate
def test_create_model_from_invalid_rating_table(
    project_url, base_job_server_data, rating_table_uploaded_but_not_modeled
):
    url = "{}ratingTableModels/".format(project_url)
    job_url = "{}jobs/{}/".format(project_url, base_job_server_data["id"])
    responses.add(
        responses.POST,
        url,
        body=json.dumps(
            {"message": "A prerequisite was not satisfied: Rating Table failed validation"}
        ),
        status=422,
        content_type="application/json",
        adding_headers={"Location": job_url},
    )

    with pytest.raises(ClientError):
        rating_table_uploaded_but_not_modeled.create_model()


@responses.activate
def test_create_model_from_used_rating_table(
    project_url, base_job_server_data, rating_table_uploaded_and_modeled
):
    url = "{}ratingTableModels/".format(project_url)
    job_url = "{}jobs/{}/".format(project_url, base_job_server_data["id"])
    responses.add(
        responses.POST,
        url,
        body=json.dumps(
            {"message": "Rating Table already has a model", "errorName": "JobAlreadyAdded"}
        ),
        status=422,
        content_type="application/json",
        adding_headers={"Location": job_url},
    )

    with pytest.raises(JobAlreadyRequested):
        rating_table_uploaded_and_modeled.create_model()


@responses.activate
def test_rename_rating_table(
    rating_table_uploaded_but_not_modeled, rating_table_renamed_json, renamed_rating_table
):
    project_id = renamed_rating_table.project_id
    table_id = renamed_rating_table.id
    url = "https://host_name.com/projects/{}/ratingTables/{}/".format(project_id, table_id)
    responses.add(
        responses.PATCH,
        url,
        body=rating_table_renamed_json,
        status=202,
        content_type="application/json",
    )
    table = rating_table_uploaded_but_not_modeled
    assert isinstance(table, RatingTable)
    assert table.rating_table_name != "renamed"
    table.rename("renamed")
    assert table.rating_table_name == "renamed"
