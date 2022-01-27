# -*- coding: utf-8 -*-
import json

import pytest
from apistar.exceptions import ErrorResponse

from arkindex_worker.models import Element
from arkindex_worker.worker import MetaType

from . import BASE_API_CALLS


def test_create_metadata_wrong_element(mock_elements_worker):
    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_metadata(
            element=None,
            type=MetaType.Location,
            name="Teklia",
            value="La Turbine, Grenoble 38000",
        )
    assert str(e.value) == "element shouldn't be null and should be of type Element"

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_metadata(
            element="not element type",
            type=MetaType.Location,
            name="Teklia",
            value="La Turbine, Grenoble 38000",
        )
    assert str(e.value) == "element shouldn't be null and should be of type Element"


def test_create_metadata_wrong_type(mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_metadata(
            element=elt,
            type=None,
            name="Teklia",
            value="La Turbine, Grenoble 38000",
        )
    assert str(e.value) == "type shouldn't be null and should be of type MetaType"

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_metadata(
            element=elt,
            type=1234,
            name="Teklia",
            value="La Turbine, Grenoble 38000",
        )
    assert str(e.value) == "type shouldn't be null and should be of type MetaType"

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_metadata(
            element=elt,
            type="not_a_metadata_type",
            name="Teklia",
            value="La Turbine, Grenoble 38000",
        )
    assert str(e.value) == "type shouldn't be null and should be of type MetaType"


def test_create_metadata_wrong_name(mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_metadata(
            element=elt,
            type=MetaType.Location,
            name=None,
            value="La Turbine, Grenoble 38000",
        )
    assert str(e.value) == "name shouldn't be null and should be of type str"

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_metadata(
            element=elt,
            type=MetaType.Location,
            name=1234,
            value="La Turbine, Grenoble 38000",
        )
    assert str(e.value) == "name shouldn't be null and should be of type str"


def test_create_metadata_wrong_value(mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_metadata(
            element=elt,
            type=MetaType.Location,
            name="Teklia",
            value=None,
        )
    assert str(e.value) == "value shouldn't be null and should be of type str"

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_metadata(
            element=elt,
            type=MetaType.Location,
            name="Teklia",
            value=1234,
        )
    assert str(e.value) == "value shouldn't be null and should be of type str"


def test_create_metadata_wrong_entity(mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_metadata(
            element=elt,
            type=MetaType.Location,
            name="Teklia",
            value="La Turbine, Grenoble 38000",
            entity=1234,
        )
    assert str(e.value) == "entity should be of type str"


def test_create_metadata_api_error(responses, mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})
    responses.add(
        responses.POST,
        "http://testserver/api/v1/element/12341234-1234-1234-1234-123412341234/metadata/",
        status=500,
    )

    with pytest.raises(ErrorResponse):
        mock_elements_worker.create_metadata(
            element=elt,
            type=MetaType.Location,
            name="Teklia",
            value="La Turbine, Grenoble 38000",
        )

    assert len(responses.calls) == len(BASE_API_CALLS) + 5
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        # We retry 5 times the API call
        (
            "POST",
            "http://testserver/api/v1/element/12341234-1234-1234-1234-123412341234/metadata/",
        ),
        (
            "POST",
            "http://testserver/api/v1/element/12341234-1234-1234-1234-123412341234/metadata/",
        ),
        (
            "POST",
            "http://testserver/api/v1/element/12341234-1234-1234-1234-123412341234/metadata/",
        ),
        (
            "POST",
            "http://testserver/api/v1/element/12341234-1234-1234-1234-123412341234/metadata/",
        ),
        (
            "POST",
            "http://testserver/api/v1/element/12341234-1234-1234-1234-123412341234/metadata/",
        ),
    ]


def test_create_metadata(responses, mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})
    responses.add(
        responses.POST,
        "http://testserver/api/v1/element/12341234-1234-1234-1234-123412341234/metadata/",
        status=200,
        json={"id": "12345678-1234-1234-1234-123456789123"},
    )

    metadata_id = mock_elements_worker.create_metadata(
        element=elt,
        type=MetaType.Location,
        name="Teklia",
        value="La Turbine, Grenoble 38000",
    )

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        (
            "POST",
            "http://testserver/api/v1/element/12341234-1234-1234-1234-123412341234/metadata/",
        ),
    ]
    assert json.loads(responses.calls[-1].request.body) == {
        "type": "location",
        "name": "Teklia",
        "value": "La Turbine, Grenoble 38000",
        "entity_id": None,
        "worker_version": "12341234-1234-1234-1234-123412341234",
    }
    assert metadata_id == "12345678-1234-1234-1234-123456789123"
