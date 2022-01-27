# -*- coding: utf-8 -*-
import json
from uuid import UUID

import pytest
from apistar.exceptions import ErrorResponse

from arkindex_worker.cache import CachedClassification, CachedElement
from arkindex_worker.models import Element

from . import BASE_API_CALLS


def test_get_ml_class_id_load_classes(responses, mock_elements_worker):
    corpus_id = "12341234-1234-1234-1234-123412341234"
    responses.add(
        responses.GET,
        f"http://testserver/api/v1/corpus/{corpus_id}/classes/",
        status=200,
        json={
            "count": 1,
            "next": None,
            "results": [
                {
                    "id": "0000",
                    "name": "good",
                }
            ],
        },
    )

    assert not mock_elements_worker.classes
    ml_class_id = mock_elements_worker.get_ml_class_id(corpus_id, "good")

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        ("GET", f"http://testserver/api/v1/corpus/{corpus_id}/classes/"),
    ]
    assert mock_elements_worker.classes == {
        "12341234-1234-1234-1234-123412341234": {"good": "0000"}
    }
    assert ml_class_id == "0000"


def test_get_ml_class_id_inexistant_class(mock_elements_worker, responses):
    # A missing class is now created automatically
    corpus_id = "12341234-1234-1234-1234-123412341234"
    mock_elements_worker.classes = {
        "12341234-1234-1234-1234-123412341234": {"good": "0000"}
    }

    responses.add(
        responses.POST,
        f"http://testserver/api/v1/corpus/{corpus_id}/classes/",
        status=201,
        json={"id": "new-ml-class-1234"},
    )

    # Missing class at first
    assert mock_elements_worker.classes == {
        "12341234-1234-1234-1234-123412341234": {"good": "0000"}
    }

    ml_class_id = mock_elements_worker.get_ml_class_id(corpus_id, "bad")
    assert ml_class_id == "new-ml-class-1234"

    # Now it's available
    assert mock_elements_worker.classes == {
        "12341234-1234-1234-1234-123412341234": {
            "good": "0000",
            "bad": "new-ml-class-1234",
        }
    }


def test_get_ml_class_id(mock_elements_worker):
    corpus_id = "12341234-1234-1234-1234-123412341234"
    mock_elements_worker.classes = {
        "12341234-1234-1234-1234-123412341234": {"good": "0000"}
    }

    ml_class_id = mock_elements_worker.get_ml_class_id(corpus_id, "good")
    assert ml_class_id == "0000"


def test_get_ml_class_reload(responses, mock_elements_worker):
    corpus_id = "12341234-1234-1234-1234-123412341234"

    # Add some initial classes
    responses.add(
        responses.GET,
        f"http://testserver/api/v1/corpus/{corpus_id}/classes/",
        json={
            "count": 1,
            "next": None,
            "results": [
                {
                    "id": "class1_id",
                    "name": "class1",
                }
            ],
        },
    )

    # Invalid response when trying to create class2
    responses.add(
        responses.POST,
        f"http://testserver/api/v1/corpus/{corpus_id}/classes/",
        status=400,
        json={"non_field_errors": "Already exists"},
    )

    # Add both classes (class2 is created by another process)
    responses.add(
        responses.GET,
        f"http://testserver/api/v1/corpus/{corpus_id}/classes/",
        json={
            "count": 2,
            "next": None,
            "results": [
                {
                    "id": "class1_id",
                    "name": "class1",
                },
                {
                    "id": "class2_id",
                    "name": "class2",
                },
            ],
        },
    )

    # Simply request class 2, it should be reloaded
    assert mock_elements_worker.get_ml_class_id(corpus_id, "class2") == "class2_id"

    assert len(responses.calls) == len(BASE_API_CALLS) + 3
    assert mock_elements_worker.classes == {
        corpus_id: {
            "class1": "class1_id",
            "class2": "class2_id",
        }
    }
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        ("GET", f"http://testserver/api/v1/corpus/{corpus_id}/classes/"),
        ("POST", f"http://testserver/api/v1/corpus/{corpus_id}/classes/"),
        ("GET", f"http://testserver/api/v1/corpus/{corpus_id}/classes/"),
    ]


def test_create_classification_wrong_element(mock_elements_worker):
    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_classification(
            element=None,
            ml_class="a_class",
            confidence=0.42,
            high_confidence=True,
        )
    assert (
        str(e.value)
        == "element shouldn't be null and should be an Element or CachedElement"
    )

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_classification(
            element="not element type",
            ml_class="a_class",
            confidence=0.42,
            high_confidence=True,
        )
    assert (
        str(e.value)
        == "element shouldn't be null and should be an Element or CachedElement"
    )


def test_create_classification_wrong_ml_class(mock_elements_worker, responses):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_classification(
            element=elt,
            ml_class=None,
            confidence=0.42,
            high_confidence=True,
        )
    assert str(e.value) == "ml_class shouldn't be null and should be of type str"

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_classification(
            element=elt,
            ml_class=1234,
            confidence=0.42,
            high_confidence=True,
        )
    assert str(e.value) == "ml_class shouldn't be null and should be of type str"

    # Automatically create a missing class !
    responses.add(
        responses.POST,
        "http://testserver/api/v1/corpus/11111111-1111-1111-1111-111111111111/classes/",
        status=201,
        json={"id": "new-ml-class-1234"},
    )
    responses.add(
        responses.POST,
        "http://testserver/api/v1/classifications/",
        status=201,
        json={"id": "new-classification-1234"},
    )
    mock_elements_worker.classes = {
        "11111111-1111-1111-1111-111111111111": {"another_class": "0000"}
    }
    mock_elements_worker.create_classification(
        element=elt,
        ml_class="a_class",
        confidence=0.42,
        high_confidence=True,
    )

    # Check a class & classification has been created
    for call in responses.calls:
        print(call.request.url, call.request.body)

    assert [
        (call.request.url, json.loads(call.request.body))
        for call in responses.calls[-2:]
    ] == [
        (
            "http://testserver/api/v1/corpus/11111111-1111-1111-1111-111111111111/classes/",
            {"name": "a_class"},
        ),
        (
            "http://testserver/api/v1/classifications/",
            {
                "element": "12341234-1234-1234-1234-123412341234",
                "ml_class": "new-ml-class-1234",
                "worker_version": "12341234-1234-1234-1234-123412341234",
                "confidence": 0.42,
                "high_confidence": True,
            },
        ),
    ]


def test_create_classification_wrong_confidence(mock_elements_worker):
    mock_elements_worker.classes = {
        "11111111-1111-1111-1111-111111111111": {"a_class": "0000"}
    }
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})
    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_classification(
            element=elt,
            ml_class="a_class",
            confidence=None,
            high_confidence=True,
        )
    assert (
        str(e.value)
        == "confidence shouldn't be null and should be a float in [0..1] range"
    )

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_classification(
            element=elt,
            ml_class="a_class",
            confidence="wrong confidence",
            high_confidence=True,
        )
    assert (
        str(e.value)
        == "confidence shouldn't be null and should be a float in [0..1] range"
    )

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_classification(
            element=elt,
            ml_class="a_class",
            confidence=0,
            high_confidence=True,
        )
    assert (
        str(e.value)
        == "confidence shouldn't be null and should be a float in [0..1] range"
    )

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_classification(
            element=elt,
            ml_class="a_class",
            confidence=2.00,
            high_confidence=True,
        )
    assert (
        str(e.value)
        == "confidence shouldn't be null and should be a float in [0..1] range"
    )


def test_create_classification_wrong_high_confidence(mock_elements_worker):
    mock_elements_worker.classes = {
        "11111111-1111-1111-1111-111111111111": {"a_class": "0000"}
    }
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_classification(
            element=elt,
            ml_class="a_class",
            confidence=0.42,
            high_confidence=None,
        )
    assert (
        str(e.value) == "high_confidence shouldn't be null and should be of type bool"
    )

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_classification(
            element=elt,
            ml_class="a_class",
            confidence=0.42,
            high_confidence="wrong high_confidence",
        )
    assert (
        str(e.value) == "high_confidence shouldn't be null and should be of type bool"
    )


def test_create_classification_api_error(responses, mock_elements_worker):
    mock_elements_worker.classes = {
        "11111111-1111-1111-1111-111111111111": {"a_class": "0000"}
    }
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})
    responses.add(
        responses.POST,
        "http://testserver/api/v1/classifications/",
        status=500,
    )

    with pytest.raises(ErrorResponse):
        mock_elements_worker.create_classification(
            element=elt,
            ml_class="a_class",
            confidence=0.42,
            high_confidence=True,
        )

    assert len(responses.calls) == len(BASE_API_CALLS) + 5
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        # We retry 5 times the API call
        ("POST", "http://testserver/api/v1/classifications/"),
        ("POST", "http://testserver/api/v1/classifications/"),
        ("POST", "http://testserver/api/v1/classifications/"),
        ("POST", "http://testserver/api/v1/classifications/"),
        ("POST", "http://testserver/api/v1/classifications/"),
    ]


def test_create_classification(responses, mock_elements_worker):
    mock_elements_worker.classes = {
        "11111111-1111-1111-1111-111111111111": {"a_class": "0000"}
    }
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})
    responses.add(
        responses.POST,
        "http://testserver/api/v1/classifications/",
        status=200,
    )

    mock_elements_worker.create_classification(
        element=elt,
        ml_class="a_class",
        confidence=0.42,
        high_confidence=True,
    )

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        ("POST", "http://testserver/api/v1/classifications/"),
    ]

    assert json.loads(responses.calls[-1].request.body) == {
        "element": "12341234-1234-1234-1234-123412341234",
        "ml_class": "0000",
        "worker_version": "12341234-1234-1234-1234-123412341234",
        "confidence": 0.42,
        "high_confidence": True,
    }

    # Classification has been created and reported
    assert mock_elements_worker.report.report_data["elements"][elt.id][
        "classifications"
    ] == {"a_class": 1}


def test_create_classification_with_cache(responses, mock_elements_worker_with_cache):
    mock_elements_worker_with_cache.classes = {
        "11111111-1111-1111-1111-111111111111": {"a_class": "0000"}
    }
    elt = CachedElement.create(id="12341234-1234-1234-1234-123412341234", type="thing")

    responses.add(
        responses.POST,
        "http://testserver/api/v1/classifications/",
        status=200,
        json={
            "id": "56785678-5678-5678-5678-567856785678",
            "element": "12341234-1234-1234-1234-123412341234",
            "ml_class": "0000",
            "worker_version": "12341234-1234-1234-1234-123412341234",
            "confidence": 0.42,
            "high_confidence": True,
            "state": "pending",
        },
    )

    mock_elements_worker_with_cache.create_classification(
        element=elt,
        ml_class="a_class",
        confidence=0.42,
        high_confidence=True,
    )

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        ("POST", "http://testserver/api/v1/classifications/"),
    ]

    assert json.loads(responses.calls[-1].request.body) == {
        "element": "12341234-1234-1234-1234-123412341234",
        "ml_class": "0000",
        "worker_version": "12341234-1234-1234-1234-123412341234",
        "confidence": 0.42,
        "high_confidence": True,
    }

    # Classification has been created and reported
    assert mock_elements_worker_with_cache.report.report_data["elements"][elt.id][
        "classifications"
    ] == {"a_class": 1}

    # Check that created classification was properly stored in SQLite cache
    assert list(CachedClassification.select()) == [
        CachedClassification(
            id=UUID("56785678-5678-5678-5678-567856785678"),
            element_id=UUID(elt.id),
            class_name="a_class",
            confidence=0.42,
            state="pending",
            worker_version_id=UUID("12341234-1234-1234-1234-123412341234"),
        )
    ]


def test_create_classification_duplicate(responses, mock_elements_worker):
    mock_elements_worker.classes = {
        "11111111-1111-1111-1111-111111111111": {"a_class": "0000"}
    }
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})
    responses.add(
        responses.POST,
        "http://testserver/api/v1/classifications/",
        status=400,
        json={
            "non_field_errors": [
                "The fields element, worker_version, ml_class must make a unique set."
            ]
        },
    )

    mock_elements_worker.create_classification(
        element=elt,
        ml_class="a_class",
        confidence=0.42,
        high_confidence=True,
    )

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        ("POST", "http://testserver/api/v1/classifications/"),
    ]

    assert json.loads(responses.calls[-1].request.body) == {
        "element": "12341234-1234-1234-1234-123412341234",
        "ml_class": "0000",
        "worker_version": "12341234-1234-1234-1234-123412341234",
        "confidence": 0.42,
        "high_confidence": True,
    }

    # Classification has NOT been created
    assert mock_elements_worker.report.report_data["elements"] == {}


def test_create_classifications_wrong_element(mock_elements_worker):
    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_classifications(
            element=None,
            classifications=[
                {
                    "class_name": "portrait",
                    "confidence": 0.75,
                    "high_confidence": False,
                },
                {
                    "class_name": "landscape",
                    "confidence": 0.25,
                    "high_confidence": False,
                },
            ],
        )
    assert (
        str(e.value)
        == "element shouldn't be null and should be an Element or CachedElement"
    )

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_classifications(
            element="not element type",
            classifications=[
                {
                    "class_name": "portrait",
                    "confidence": 0.75,
                    "high_confidence": False,
                },
                {
                    "class_name": "landscape",
                    "confidence": 0.25,
                    "high_confidence": False,
                },
            ],
        )
    assert (
        str(e.value)
        == "element shouldn't be null and should be an Element or CachedElement"
    )


def test_create_classifications_wrong_classifications(mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_classifications(
            element=elt,
            classifications=None,
        )
    assert (
        str(e.value) == "classifications shouldn't be null and should be of type list"
    )

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_classifications(
            element=elt,
            classifications=1234,
        )
    assert (
        str(e.value) == "classifications shouldn't be null and should be of type list"
    )

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_classifications(
            element=elt,
            classifications=[
                {
                    "class_name": "portrait",
                    "confidence": 0.75,
                    "high_confidence": False,
                },
                {
                    "confidence": 0.25,
                    "high_confidence": False,
                },
            ],
        )
    assert (
        str(e.value)
        == "Classification at index 1 in classifications: class_name shouldn't be null and should be of type str"
    )

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_classifications(
            element=elt,
            classifications=[
                {
                    "class_name": "portrait",
                    "confidence": 0.75,
                    "high_confidence": False,
                },
                {
                    "class_name": None,
                    "confidence": 0.25,
                    "high_confidence": False,
                },
            ],
        )
    assert (
        str(e.value)
        == "Classification at index 1 in classifications: class_name shouldn't be null and should be of type str"
    )

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_classifications(
            element=elt,
            classifications=[
                {
                    "class_name": "portrait",
                    "confidence": 0.75,
                    "high_confidence": False,
                },
                {
                    "class_name": 1234,
                    "confidence": 0.25,
                    "high_confidence": False,
                },
            ],
        )
    assert (
        str(e.value)
        == "Classification at index 1 in classifications: class_name shouldn't be null and should be of type str"
    )

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_classifications(
            element=elt,
            classifications=[
                {
                    "class_name": "portrait",
                    "confidence": 0.75,
                    "high_confidence": False,
                },
                {
                    "class_name": "landscape",
                    "high_confidence": False,
                },
            ],
        )
    assert (
        str(e.value)
        == "Classification at index 1 in classifications: confidence shouldn't be null and should be a float in [0..1] range"
    )

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_classifications(
            element=elt,
            classifications=[
                {
                    "class_name": "portrait",
                    "confidence": 0.75,
                    "high_confidence": False,
                },
                {
                    "class_name": "landscape",
                    "confidence": None,
                    "high_confidence": False,
                },
            ],
        )
    assert (
        str(e.value)
        == "Classification at index 1 in classifications: confidence shouldn't be null and should be a float in [0..1] range"
    )

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_classifications(
            element=elt,
            classifications=[
                {
                    "class_name": "portrait",
                    "confidence": 0.75,
                    "high_confidence": False,
                },
                {
                    "class_name": "landscape",
                    "confidence": "wrong confidence",
                    "high_confidence": False,
                },
            ],
        )
    assert (
        str(e.value)
        == "Classification at index 1 in classifications: confidence shouldn't be null and should be a float in [0..1] range"
    )

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_classifications(
            element=elt,
            classifications=[
                {
                    "class_name": "portrait",
                    "confidence": 0.75,
                    "high_confidence": False,
                },
                {
                    "class_name": "landscape",
                    "confidence": 0,
                    "high_confidence": False,
                },
            ],
        )
    assert (
        str(e.value)
        == "Classification at index 1 in classifications: confidence shouldn't be null and should be a float in [0..1] range"
    )

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_classifications(
            element=elt,
            classifications=[
                {
                    "class_name": "portrait",
                    "confidence": 0.75,
                    "high_confidence": False,
                },
                {
                    "class_name": "landscape",
                    "confidence": 2.00,
                    "high_confidence": False,
                },
            ],
        )
    assert (
        str(e.value)
        == "Classification at index 1 in classifications: confidence shouldn't be null and should be a float in [0..1] range"
    )

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_classifications(
            element=elt,
            classifications=[
                {
                    "class_name": "portrait",
                    "confidence": 0.75,
                    "high_confidence": False,
                },
                {
                    "class_name": "landscape",
                    "confidence": 0.25,
                    "high_confidence": "wrong high_confidence",
                },
            ],
        )
    assert (
        str(e.value)
        == "Classification at index 1 in classifications: high_confidence should be of type bool"
    )


def test_create_classifications_api_error(responses, mock_elements_worker):
    responses.add(
        responses.POST,
        "http://testserver/api/v1/classification/bulk/",
        status=500,
    )
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})
    classes = [
        {
            "class_name": "portrait",
            "confidence": 0.75,
            "high_confidence": False,
        },
        {
            "class_name": "landscape",
            "confidence": 0.25,
            "high_confidence": False,
        },
    ]

    with pytest.raises(ErrorResponse):
        mock_elements_worker.create_classifications(
            element=elt, classifications=classes
        )

    assert len(responses.calls) == len(BASE_API_CALLS) + 5
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        # We retry 5 times the API call
        ("POST", "http://testserver/api/v1/classification/bulk/"),
        ("POST", "http://testserver/api/v1/classification/bulk/"),
        ("POST", "http://testserver/api/v1/classification/bulk/"),
        ("POST", "http://testserver/api/v1/classification/bulk/"),
        ("POST", "http://testserver/api/v1/classification/bulk/"),
    ]


def test_create_classifications(responses, mock_elements_worker_with_cache):
    elt = CachedElement.create(id="12341234-1234-1234-1234-123412341234", type="thing")
    classes = [
        {
            "class_name": "portrait",
            "confidence": 0.75,
            "high_confidence": False,
        },
        {
            "class_name": "landscape",
            "confidence": 0.25,
            "high_confidence": False,
        },
    ]

    responses.add(
        responses.POST,
        "http://testserver/api/v1/classification/bulk/",
        status=200,
        json={
            "parent": str(elt.id),
            "worker_version": "12341234-1234-1234-1234-123412341234",
            "classifications": [
                {
                    "id": "00000000-0000-0000-0000-000000000000",
                    "class_name": "portrait",
                    "confidence": 0.75,
                    "high_confidence": False,
                    "state": "pending",
                },
                {
                    "id": "11111111-1111-1111-1111-111111111111",
                    "class_name": "landscape",
                    "confidence": 0.25,
                    "high_confidence": False,
                    "state": "pending",
                },
            ],
        },
    )

    mock_elements_worker_with_cache.create_classifications(
        element=elt, classifications=classes
    )

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        ("POST", "http://testserver/api/v1/classification/bulk/"),
    ]

    assert json.loads(responses.calls[-1].request.body) == {
        "parent": str(elt.id),
        "worker_version": "12341234-1234-1234-1234-123412341234",
        "classifications": classes,
    }

    # Check that created classifications were properly stored in SQLite cache
    assert list(CachedClassification.select()) == [
        CachedClassification(
            id=UUID("00000000-0000-0000-0000-000000000000"),
            element_id=UUID(elt.id),
            class_name="portrait",
            confidence=0.75,
            state="pending",
            worker_version_id=UUID("12341234-1234-1234-1234-123412341234"),
        ),
        CachedClassification(
            id=UUID("11111111-1111-1111-1111-111111111111"),
            element_id=UUID(elt.id),
            class_name="landscape",
            confidence=0.25,
            state="pending",
            worker_version_id=UUID("12341234-1234-1234-1234-123412341234"),
        ),
    ]
