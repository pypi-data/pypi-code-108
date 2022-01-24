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
import trafaret

from datarobot import errors
from datarobot.models.training_predictions import RowsIterator


@responses.activate
def test_rows_iterator__empty_response__ok(client):
    body = {"data": [], "next": None}
    responses.add(
        responses.GET,
        "https://host_name.com/foobar",
        body=json.dumps(body),
        content_type="application/json",
    )

    it = RowsIterator(client, "foobar")

    assert list(it) == []


@responses.activate
def test_rows_iterator__two_items__ok(client):
    url = "https://host_name.com/foobar"
    body = {"data": [{"foo": "bar"}], "next": "{}?offset=1&limit=1".format(url)}
    responses.add(
        responses.GET, url, body=json.dumps(body), content_type="application/json",
    )

    it = RowsIterator(client, "foobar", limit=1)

    assert next(it, None) == {"foo": "bar"}
    assert len(responses.calls) == 1

    responses.reset()
    body2 = {"data": [{"bar": "foo"}], "next": "{}?offset=2&limit=1".format(url)}
    responses.add(
        responses.GET, url, body=json.dumps(body2), content_type="application/json",
    )

    assert next(it, None) == {"bar": "foo"}
    assert len(responses.calls) == 1

    responses.reset()
    body3 = {"data": [], "next": "{}?offset=3&limit=1".format(url)}
    responses.add(
        responses.GET, url, body=json.dumps(body3), content_type="application/json",
    )

    assert next(it, None) is None
    assert len(responses.calls) == 1


@responses.activate
def test_rows_iterator__http_504__raise_error(client):
    url = "https://host_name.com/foobar"
    body = {"message": "test-error"}
    responses.add(
        responses.GET, url, body=json.dumps(body), content_type="application/json", status=504,
    )

    with pytest.raises(errors.ServerError) as exc:
        it = RowsIterator(client, "foobar")
        next(it, None)

    assert exc.value.status_code == 504


@responses.activate
def test_rows_iterator__no_data_field__raise_error(client):
    url = "https://host_name.com/foobar"
    body = {"message": "test-error", "next": "test"}
    responses.add(
        responses.GET, url, body=json.dumps(body), content_type="application/json",
    )

    with pytest.raises(Exception) as exc:
        it = RowsIterator(client, "foobar")
        next(it, None)

    assert isinstance(exc.value, trafaret.DataError)
