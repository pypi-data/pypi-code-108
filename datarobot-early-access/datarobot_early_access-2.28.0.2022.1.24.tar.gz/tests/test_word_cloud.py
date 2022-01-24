# coding=utf-8
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

from numpy import isclose
import pytest
import responses

from datarobot import Model
from datarobot.models.word_cloud import WordCloud


@pytest.fixture
def word_cloud_data():
    return {
        "ngrams": [
            {
                "ngram": u"エピソード",
                "coefficient": 0.2074072186419962,
                "isStopword": False,
                "count": 10,
                "frequency": 0.1449275362318841,
            },
            {
                "ngram": u"外",
                "coefficient": 0.3669030452411179,
                "isStopword": True,
                "count": 8,
                "frequency": 0.1159420289855072,
            },
            {
                "ngram": u"閉鎖",
                "coefficient": -0.1343662758815528,
                "isStopword": False,
                "count": 5,
                "frequency": 0.07246376811594203,
            },
        ]
    }


@pytest.fixture
def word_cloud_data_with_class(word_cloud_data):
    for ngram in word_cloud_data["ngrams"]:
        ngram["class"] = "classname"
    return word_cloud_data


@pytest.fixture
def word_cloud_data_with_multiple_classes(word_cloud_data):
    word_cloud_data["ngrams"][0]["class"] = "class_0"
    word_cloud_data["ngrams"][1]["class"] = "class_1"
    word_cloud_data["ngrams"][2]["class"] = "class_2"
    return word_cloud_data


@pytest.fixture
def word_cloud_data_with_variable(word_cloud_data_with_class):
    for ngram in word_cloud_data_with_class["ngrams"]:
        ngram["variable"] = "SOURCE_COLUMN"
    return word_cloud_data_with_class


def test_instantiation(word_cloud_data):
    wc = WordCloud.from_server_data(word_cloud_data)

    assert len(word_cloud_data["ngrams"]) == len(wc.ngrams)
    for i in range(len(wc.ngrams)):
        assert wc.ngrams[i]["ngram"] == word_cloud_data["ngrams"][i]["ngram"]
        assert wc.ngrams[i]["is_stopword"] == word_cloud_data["ngrams"][i]["isStopword"]
        assert wc.ngrams[i]["count"] == word_cloud_data["ngrams"][i]["count"]
        assert isclose(wc.ngrams[i]["coefficient"], word_cloud_data["ngrams"][i]["coefficient"])
        assert isclose(wc.ngrams[i]["frequency"], word_cloud_data["ngrams"][i]["frequency"])
        # Backward compatible - for old return results fill with None
        assert wc.ngrams[i]["class"] is None


def test_instantiation_with_class(word_cloud_data_with_class):
    wc = WordCloud.from_server_data(word_cloud_data_with_class)
    assert len(word_cloud_data_with_class["ngrams"]) == len(wc.ngrams)
    for i in range(len(wc.ngrams)):
        assert wc.ngrams[i]["class"] == "classname"


def test_ngrams_per_class(word_cloud_data_with_multiple_classes):
    wc = WordCloud.from_server_data(word_cloud_data_with_multiple_classes)
    ngrams_per_class = wc.ngrams_per_class()
    assert set(ngrams_per_class.keys()) == {"class_0", "class_1", "class_2"}


def test_instantiation_with_variable(word_cloud_data_with_variable):
    wc = WordCloud.from_server_data(word_cloud_data_with_variable)
    assert len(word_cloud_data_with_variable["ngrams"]) == len(wc.ngrams)
    assert all(ngram["variable"] == "SOURCE_COLUMN" for ngram in wc.ngrams)


def test_future_proof(word_cloud_data):
    data_with_future_keys = dict(word_cloud_data, new_key="new_value")
    data_with_future_keys["ngrams"][0]["some_additional_data"] = "we never expected this"
    WordCloud.from_server_data(data_with_future_keys)


def test_most_frequent(word_cloud_data):
    wc = WordCloud.from_server_data(word_cloud_data)
    most_frequent_list = wc.most_frequent(1)
    assert len(most_frequent_list) == 1
    most_frequent = most_frequent_list[0]
    assert all(most_frequent["frequency"] >= wc_ngram["frequency"] for wc_ngram in wc.ngrams)


def test_most_important(word_cloud_data):
    wc = WordCloud.from_server_data(word_cloud_data)
    most_important_list = wc.most_important(1)
    assert len(most_important_list) == 1
    most_important = most_important_list[0]
    assert all(
        abs(most_important["coefficient"]) >= abs(wc_ngram["coefficient"]) for wc_ngram in wc.ngrams
    )


@pytest.fixture
def word_cloud_url(project_id, model_id):
    return "https://host_name.com/projects/{}/models/{}/wordCloud/".format(project_id, model_id)


@responses.activate
def test_get_word_cloud(word_cloud_data, word_cloud_url, project_id, model_id):
    responses.add(
        responses.GET,
        word_cloud_url,
        status=200,
        content_type="application/json",
        body=json.dumps(word_cloud_data),
    )
    model = Model(id=model_id, project_id=project_id)
    wc = model.get_word_cloud()

    assert len(word_cloud_data["ngrams"]) == len(wc.ngrams)
    for i in range(len(wc.ngrams)):
        assert wc.ngrams[i]["ngram"] == word_cloud_data["ngrams"][i]["ngram"]
        assert wc.ngrams[i]["is_stopword"] == word_cloud_data["ngrams"][i]["isStopword"]
        assert wc.ngrams[i]["count"] == word_cloud_data["ngrams"][i]["count"]
        assert isclose(wc.ngrams[i]["coefficient"], word_cloud_data["ngrams"][i]["coefficient"])
        assert isclose(wc.ngrams[i]["frequency"], word_cloud_data["ngrams"][i]["frequency"])
