# -*- coding: utf-8 -*-
import json
from uuid import UUID

import pytest
from apistar.exceptions import ErrorResponse
from playhouse.shortcuts import model_to_dict

from arkindex_worker.cache import CachedElement, CachedTranscription
from arkindex_worker.models import Element
from arkindex_worker.worker.transcription import TextOrientation

from . import BASE_API_CALLS

TRANSCRIPTIONS_SAMPLE = [
    {
        "polygon": [[100, 150], [700, 150], [700, 200], [100, 200]],
        "score": 0.5,
        "text": "The",
    },
    {
        "polygon": [[0, 0], [2000, 0], [2000, 3000], [0, 3000]],
        "score": 0.75,
        "text": "first",
    },
    {
        "polygon": [[1000, 300], [1200, 300], [1200, 500], [1000, 500]],
        "score": 0.9,
        "text": "line",
    },
]


def test_create_transcription_wrong_element(mock_elements_worker):
    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_transcription(
            element=None,
            text="i am a line",
            score=0.42,
        )
    assert (
        str(e.value)
        == "element shouldn't be null and should be an Element or CachedElement"
    )

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_transcription(
            element="not element type",
            text="i am a line",
            score=0.42,
        )
    assert (
        str(e.value)
        == "element shouldn't be null and should be an Element or CachedElement"
    )


def test_create_transcription_wrong_text(mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_transcription(
            element=elt,
            text=None,
            score=0.42,
        )
    assert str(e.value) == "text shouldn't be null and should be of type str"

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_transcription(
            element=elt,
            text=1234,
            score=0.42,
        )
    assert str(e.value) == "text shouldn't be null and should be of type str"


def test_create_transcription_wrong_score(mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_transcription(
            element=elt,
            text="i am a line",
            score=None,
        )
    assert (
        str(e.value) == "score shouldn't be null and should be a float in [0..1] range"
    )

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_transcription(
            element=elt,
            text="i am a line",
            score="wrong score",
        )
    assert (
        str(e.value) == "score shouldn't be null and should be a float in [0..1] range"
    )

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_transcription(
            element=elt,
            text="i am a line",
            score=0,
        )
    assert (
        str(e.value) == "score shouldn't be null and should be a float in [0..1] range"
    )

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_transcription(
            element=elt,
            text="i am a line",
            score=2.00,
        )
    assert (
        str(e.value) == "score shouldn't be null and should be a float in [0..1] range"
    )


def test_create_transcription_default_orientation(responses, mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})
    responses.add(
        responses.POST,
        f"http://testserver/api/v1/element/{elt.id}/transcription/",
        status=200,
        json={
            "id": "56785678-5678-5678-5678-567856785678",
            "text": "Animula vagula blandula",
            "confidence": 0.42,
            "worker_version_id": "12341234-1234-1234-1234-123412341234",
        },
    )
    mock_elements_worker.create_transcription(
        element=elt,
        text="Animula vagula blandula",
        score=0.42,
    )
    assert json.loads(responses.calls[-1].request.body) == {
        "text": "Animula vagula blandula",
        "worker_version": "12341234-1234-1234-1234-123412341234",
        "score": 0.42,
        "orientation": "horizontal-lr",
    }


def test_create_transcription_orientation(responses, mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})
    responses.add(
        responses.POST,
        f"http://testserver/api/v1/element/{elt.id}/transcription/",
        status=200,
        json={
            "id": "56785678-5678-5678-5678-567856785678",
            "text": "Animula vagula blandula",
            "confidence": 0.42,
            "worker_version_id": "12341234-1234-1234-1234-123412341234",
        },
    )
    mock_elements_worker.create_transcription(
        element=elt,
        text="Animula vagula blandula",
        orientation=TextOrientation.VerticalLeftToRight,
        score=0.42,
    )
    assert json.loads(responses.calls[-1].request.body) == {
        "text": "Animula vagula blandula",
        "worker_version": "12341234-1234-1234-1234-123412341234",
        "score": 0.42,
        "orientation": "vertical-lr",
    }


def test_create_transcription_wrong_orientation(mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})
    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_transcription(
            element=elt,
            text="Animula vagula blandula",
            score=0.26,
            orientation="eliptical",
        )
    assert (
        str(e.value)
        == "orientation shouldn't be null and should be of type TextOrientation"
    )


def test_create_transcription_api_error(responses, mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})
    responses.add(
        responses.POST,
        f"http://testserver/api/v1/element/{elt.id}/transcription/",
        status=500,
    )

    with pytest.raises(ErrorResponse):
        mock_elements_worker.create_transcription(
            element=elt,
            text="i am a line",
            score=0.42,
        )

    assert len(responses.calls) == len(BASE_API_CALLS) + 5
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        # We retry 5 times the API call
        ("POST", f"http://testserver/api/v1/element/{elt.id}/transcription/"),
        ("POST", f"http://testserver/api/v1/element/{elt.id}/transcription/"),
        ("POST", f"http://testserver/api/v1/element/{elt.id}/transcription/"),
        ("POST", f"http://testserver/api/v1/element/{elt.id}/transcription/"),
        ("POST", f"http://testserver/api/v1/element/{elt.id}/transcription/"),
    ]


def test_create_transcription(responses, mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})
    responses.add(
        responses.POST,
        f"http://testserver/api/v1/element/{elt.id}/transcription/",
        status=200,
        json={
            "id": "56785678-5678-5678-5678-567856785678",
            "text": "i am a line",
            "score": 0.42,
            "confidence": 0.42,
            "worker_version_id": "12341234-1234-1234-1234-123412341234",
        },
    )

    mock_elements_worker.create_transcription(
        element=elt,
        text="i am a line",
        score=0.42,
    )

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        ("POST", f"http://testserver/api/v1/element/{elt.id}/transcription/"),
    ]

    assert json.loads(responses.calls[-1].request.body) == {
        "text": "i am a line",
        "worker_version": "12341234-1234-1234-1234-123412341234",
        "score": 0.42,
        "orientation": "horizontal-lr",
    }


def test_create_transcription_with_cache(responses, mock_elements_worker_with_cache):
    elt = CachedElement.create(id="12341234-1234-1234-1234-123412341234", type="thing")

    responses.add(
        responses.POST,
        f"http://testserver/api/v1/element/{elt.id}/transcription/",
        status=200,
        json={
            "id": "56785678-5678-5678-5678-567856785678",
            "text": "i am a line",
            "score": 0.42,
            "confidence": 0.42,
            "orientation": "horizontal-lr",
            "worker_version_id": "12341234-1234-1234-1234-123412341234",
        },
    )

    mock_elements_worker_with_cache.create_transcription(
        element=elt,
        text="i am a line",
        score=0.42,
    )

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        ("POST", f"http://testserver/api/v1/element/{elt.id}/transcription/"),
    ]

    assert json.loads(responses.calls[-1].request.body) == {
        "text": "i am a line",
        "worker_version": "12341234-1234-1234-1234-123412341234",
        "orientation": "horizontal-lr",
        "score": 0.42,
    }

    # Check that created transcription was properly stored in SQLite cache
    assert list(CachedTranscription.select()) == [
        CachedTranscription(
            id=UUID("56785678-5678-5678-5678-567856785678"),
            element_id=UUID(elt.id),
            text="i am a line",
            confidence=0.42,
            orientation=TextOrientation.HorizontalLeftToRight,
            worker_version_id=UUID("12341234-1234-1234-1234-123412341234"),
        )
    ]


def test_create_transcription_orientation_with_cache(
    responses, mock_elements_worker_with_cache
):
    elt = CachedElement.create(id="12341234-1234-1234-1234-123412341234", type="thing")
    responses.add(
        responses.POST,
        f"http://testserver/api/v1/element/{elt.id}/transcription/",
        status=200,
        json={
            "id": "56785678-5678-5678-5678-567856785678",
            "text": "Animula vagula blandula",
            "confidence": 0.42,
            "orientation": "vertical-lr",
            "worker_version_id": "12341234-1234-1234-1234-123412341234",
        },
    )
    mock_elements_worker_with_cache.create_transcription(
        element=elt,
        text="Animula vagula blandula",
        orientation=TextOrientation.VerticalLeftToRight,
        score=0.42,
    )
    assert json.loads(responses.calls[-1].request.body) == {
        "text": "Animula vagula blandula",
        "worker_version": "12341234-1234-1234-1234-123412341234",
        "orientation": "vertical-lr",
        "score": 0.42,
    }
    # Check that the text orientation was properly stored in SQLite cache
    assert list(map(model_to_dict, CachedTranscription.select())) == [
        {
            "id": UUID("56785678-5678-5678-5678-567856785678"),
            "element": {
                "id": UUID("12341234-1234-1234-1234-123412341234"),
                "parent_id": None,
                "type": "thing",
                "image": None,
                "polygon": None,
                "rotation_angle": 0,
                "mirrored": False,
                "initial": False,
                "worker_version_id": None,
            },
            "text": "Animula vagula blandula",
            "confidence": 0.42,
            "orientation": TextOrientation.VerticalLeftToRight.value,
            "worker_version_id": UUID("12341234-1234-1234-1234-123412341234"),
        }
    ]


def test_create_transcriptions_wrong_transcriptions(mock_elements_worker):
    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_transcriptions(
            transcriptions=None,
        )
    assert str(e.value) == "transcriptions shouldn't be null and should be of type list"

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_transcriptions(
            transcriptions=1234,
        )
    assert str(e.value) == "transcriptions shouldn't be null and should be of type list"

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_transcriptions(
            transcriptions=[
                {
                    "element_id": "11111111-1111-1111-1111-111111111111",
                    "text": "The",
                    "score": 0.75,
                },
                {
                    "text": "word",
                    "score": 0.5,
                },
            ],
        )
    assert (
        str(e.value)
        == "Transcription at index 1 in transcriptions: element_id shouldn't be null and should be of type str"
    )

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_transcriptions(
            transcriptions=[
                {
                    "element_id": "11111111-1111-1111-1111-111111111111",
                    "text": "The",
                    "score": 0.75,
                },
                {
                    "element_id": None,
                    "text": "word",
                    "score": 0.5,
                },
            ],
        )
    assert (
        str(e.value)
        == "Transcription at index 1 in transcriptions: element_id shouldn't be null and should be of type str"
    )

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_transcriptions(
            transcriptions=[
                {
                    "element_id": "11111111-1111-1111-1111-111111111111",
                    "text": "The",
                    "score": 0.75,
                },
                {
                    "element_id": 1234,
                    "text": "word",
                    "score": 0.5,
                },
            ],
        )
    assert (
        str(e.value)
        == "Transcription at index 1 in transcriptions: element_id shouldn't be null and should be of type str"
    )

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_transcriptions(
            transcriptions=[
                {
                    "element_id": "11111111-1111-1111-1111-111111111111",
                    "text": "The",
                    "score": 0.75,
                },
                {
                    "element_id": "11111111-1111-1111-1111-111111111111",
                    "score": 0.5,
                },
            ],
        )
    assert (
        str(e.value)
        == "Transcription at index 1 in transcriptions: text shouldn't be null and should be of type str"
    )

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_transcriptions(
            transcriptions=[
                {
                    "element_id": "11111111-1111-1111-1111-111111111111",
                    "text": "The",
                    "score": 0.75,
                },
                {
                    "element_id": "11111111-1111-1111-1111-111111111111",
                    "text": None,
                    "score": 0.5,
                },
            ],
        )
    assert (
        str(e.value)
        == "Transcription at index 1 in transcriptions: text shouldn't be null and should be of type str"
    )

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_transcriptions(
            transcriptions=[
                {
                    "element_id": "11111111-1111-1111-1111-111111111111",
                    "text": "The",
                    "score": 0.75,
                },
                {
                    "element_id": "11111111-1111-1111-1111-111111111111",
                    "text": 1234,
                    "score": 0.5,
                },
            ],
        )
    assert (
        str(e.value)
        == "Transcription at index 1 in transcriptions: text shouldn't be null and should be of type str"
    )

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_transcriptions(
            transcriptions=[
                {
                    "element_id": "11111111-1111-1111-1111-111111111111",
                    "text": "The",
                    "score": 0.75,
                },
                {
                    "element_id": "11111111-1111-1111-1111-111111111111",
                    "text": "word",
                },
            ],
        )
    assert (
        str(e.value)
        == "Transcription at index 1 in transcriptions: score shouldn't be null and should be a float in [0..1] range"
    )

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_transcriptions(
            transcriptions=[
                {
                    "element_id": "11111111-1111-1111-1111-111111111111",
                    "text": "The",
                    "score": 0.75,
                },
                {
                    "element_id": "11111111-1111-1111-1111-111111111111",
                    "text": "word",
                    "score": None,
                },
            ],
        )
    assert (
        str(e.value)
        == "Transcription at index 1 in transcriptions: score shouldn't be null and should be a float in [0..1] range"
    )

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_transcriptions(
            transcriptions=[
                {
                    "element_id": "11111111-1111-1111-1111-111111111111",
                    "text": "The",
                    "score": 0.75,
                },
                {
                    "element_id": "11111111-1111-1111-1111-111111111111",
                    "text": "word",
                    "score": "a wrong score",
                },
            ],
        )
    assert (
        str(e.value)
        == "Transcription at index 1 in transcriptions: score shouldn't be null and should be a float in [0..1] range"
    )

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_transcriptions(
            transcriptions=[
                {
                    "element_id": "11111111-1111-1111-1111-111111111111",
                    "text": "The",
                    "score": 0.75,
                },
                {
                    "element_id": "11111111-1111-1111-1111-111111111111",
                    "text": "word",
                    "score": 0,
                },
            ],
        )
    assert (
        str(e.value)
        == "Transcription at index 1 in transcriptions: score shouldn't be null and should be a float in [0..1] range"
    )

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_transcriptions(
            transcriptions=[
                {
                    "element_id": "11111111-1111-1111-1111-111111111111",
                    "text": "The",
                    "score": 0.75,
                },
                {
                    "element_id": "11111111-1111-1111-1111-111111111111",
                    "text": "word",
                    "score": 2.00,
                },
            ],
        )
    assert (
        str(e.value)
        == "Transcription at index 1 in transcriptions: score shouldn't be null and should be a float in [0..1] range"
    )

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_transcriptions(
            transcriptions=[
                {
                    "element_id": "11111111-1111-1111-1111-111111111111",
                    "text": "The",
                    "score": 0.75,
                },
                {
                    "element_id": "11111111-1111-1111-1111-111111111111",
                    "text": "word",
                    "score": 0.28,
                    "orientation": "wobble",
                },
            ],
        )
    assert (
        str(e.value)
        == "Transcription at index 1 in transcriptions: orientation shouldn't be null and should be of type TextOrientation"
    )


def test_create_transcriptions_api_error(responses, mock_elements_worker):
    responses.add(
        responses.POST,
        "http://testserver/api/v1/transcription/bulk/",
        status=500,
    )
    trans = [
        {
            "element_id": "11111111-1111-1111-1111-111111111111",
            "text": "The",
            "score": 0.75,
        },
        {
            "element_id": "11111111-1111-1111-1111-111111111111",
            "text": "word",
            "score": 0.42,
        },
    ]

    with pytest.raises(ErrorResponse):
        mock_elements_worker.create_transcriptions(transcriptions=trans)

    assert len(responses.calls) == len(BASE_API_CALLS) + 5
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        # We retry 5 times the API call
        ("POST", "http://testserver/api/v1/transcription/bulk/"),
        ("POST", "http://testserver/api/v1/transcription/bulk/"),
        ("POST", "http://testserver/api/v1/transcription/bulk/"),
        ("POST", "http://testserver/api/v1/transcription/bulk/"),
        ("POST", "http://testserver/api/v1/transcription/bulk/"),
    ]


def test_create_transcriptions(responses, mock_elements_worker_with_cache):
    CachedElement.create(id="11111111-1111-1111-1111-111111111111", type="thing")
    trans = [
        {
            "element_id": "11111111-1111-1111-1111-111111111111",
            "text": "The",
            "score": 0.75,
        },
        {
            "element_id": "11111111-1111-1111-1111-111111111111",
            "text": "word",
            "score": 0.42,
        },
    ]

    responses.add(
        responses.POST,
        "http://testserver/api/v1/transcription/bulk/",
        status=200,
        json={
            "worker_version": "12341234-1234-1234-1234-123412341234",
            "transcriptions": [
                {
                    "id": "00000000-0000-0000-0000-000000000000",
                    "element_id": "11111111-1111-1111-1111-111111111111",
                    "text": "The",
                    "orientation": "horizontal-lr",
                    "confidence": 0.75,
                },
                {
                    "id": "11111111-1111-1111-1111-111111111111",
                    "element_id": "11111111-1111-1111-1111-111111111111",
                    "text": "word",
                    "orientation": "horizontal-lr",
                    "confidence": 0.42,
                },
            ],
        },
    )

    mock_elements_worker_with_cache.create_transcriptions(
        transcriptions=trans,
    )

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        ("POST", "http://testserver/api/v1/transcription/bulk/"),
    ]

    assert json.loads(responses.calls[-1].request.body) == {
        "worker_version": "12341234-1234-1234-1234-123412341234",
        "transcriptions": [
            {
                "element_id": "11111111-1111-1111-1111-111111111111",
                "text": "The",
                "score": 0.75,
                "orientation": TextOrientation.HorizontalLeftToRight.value,
            },
            {
                "element_id": "11111111-1111-1111-1111-111111111111",
                "text": "word",
                "score": 0.42,
                "orientation": TextOrientation.HorizontalLeftToRight.value,
            },
        ],
    }

    # Check that created transcriptions were properly stored in SQLite cache
    assert list(CachedTranscription.select()) == [
        CachedTranscription(
            id=UUID("00000000-0000-0000-0000-000000000000"),
            element_id=UUID("11111111-1111-1111-1111-111111111111"),
            text="The",
            confidence=0.75,
            orientation=TextOrientation.HorizontalLeftToRight,
            worker_version_id=UUID("12341234-1234-1234-1234-123412341234"),
        ),
        CachedTranscription(
            id=UUID("11111111-1111-1111-1111-111111111111"),
            element_id=UUID("11111111-1111-1111-1111-111111111111"),
            text="word",
            confidence=0.42,
            orientation=TextOrientation.HorizontalLeftToRight,
            worker_version_id=UUID("12341234-1234-1234-1234-123412341234"),
        ),
    ]


def test_create_transcriptions_orientation(responses, mock_elements_worker_with_cache):
    CachedElement.create(id="11111111-1111-1111-1111-111111111111", type="thing")
    trans = [
        {
            "element_id": "11111111-1111-1111-1111-111111111111",
            "text": "Animula vagula blandula",
            "score": 0.12,
            "orientation": TextOrientation.HorizontalRightToLeft,
        },
        {
            "element_id": "11111111-1111-1111-1111-111111111111",
            "text": "Hospes comesque corporis",
            "score": 0.21,
            "orientation": TextOrientation.VerticalLeftToRight,
        },
    ]

    responses.add(
        responses.POST,
        "http://testserver/api/v1/transcription/bulk/",
        status=200,
        json={
            "worker_version": "12341234-1234-1234-1234-123412341234",
            "transcriptions": [
                {
                    "id": "00000000-0000-0000-0000-000000000000",
                    "element_id": "11111111-1111-1111-1111-111111111111",
                    "text": "Animula vagula blandula",
                    "orientation": "horizontal-rl",
                    "confidence": 0.12,
                },
                {
                    "id": "11111111-1111-1111-1111-111111111111",
                    "element_id": "11111111-1111-1111-1111-111111111111",
                    "text": "Hospes comesque corporis",
                    "orientation": "vertical-lr",
                    "confidence": 0.21,
                },
            ],
        },
    )

    mock_elements_worker_with_cache.create_transcriptions(
        transcriptions=trans,
    )

    assert json.loads(responses.calls[-1].request.body) == {
        "worker_version": "12341234-1234-1234-1234-123412341234",
        "transcriptions": [
            {
                "element_id": "11111111-1111-1111-1111-111111111111",
                "text": "Animula vagula blandula",
                "score": 0.12,
                "orientation": TextOrientation.HorizontalRightToLeft.value,
            },
            {
                "element_id": "11111111-1111-1111-1111-111111111111",
                "text": "Hospes comesque corporis",
                "score": 0.21,
                "orientation": TextOrientation.VerticalLeftToRight.value,
            },
        ],
    }

    # Check that oriented transcriptions were properly stored in SQLite cache
    assert list(map(model_to_dict, CachedTranscription.select())) == [
        {
            "id": UUID("00000000-0000-0000-0000-000000000000"),
            "element": {
                "id": UUID("11111111-1111-1111-1111-111111111111"),
                "parent_id": None,
                "type": "thing",
                "image": None,
                "polygon": None,
                "rotation_angle": 0,
                "mirrored": False,
                "initial": False,
                "worker_version_id": None,
            },
            "text": "Animula vagula blandula",
            "confidence": 0.12,
            "orientation": TextOrientation.HorizontalRightToLeft.value,
            "worker_version_id": UUID("12341234-1234-1234-1234-123412341234"),
        },
        {
            "id": UUID("11111111-1111-1111-1111-111111111111"),
            "element": {
                "id": UUID("11111111-1111-1111-1111-111111111111"),
                "parent_id": None,
                "type": "thing",
                "image": None,
                "polygon": None,
                "rotation_angle": 0,
                "mirrored": False,
                "initial": False,
                "worker_version_id": None,
            },
            "text": "Hospes comesque corporis",
            "confidence": 0.21,
            "orientation": TextOrientation.VerticalLeftToRight.value,
            "worker_version_id": UUID("12341234-1234-1234-1234-123412341234"),
        },
    ]


def test_create_element_transcriptions_wrong_element(mock_elements_worker):
    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_element_transcriptions(
            element=None,
            sub_element_type="page",
            transcriptions=TRANSCRIPTIONS_SAMPLE,
        )
    assert (
        str(e.value)
        == "element shouldn't be null and should be an Element or CachedElement"
    )

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_element_transcriptions(
            element="not element type",
            sub_element_type="page",
            transcriptions=TRANSCRIPTIONS_SAMPLE,
        )
    assert (
        str(e.value)
        == "element shouldn't be null and should be an Element or CachedElement"
    )


def test_create_element_transcriptions_wrong_sub_element_type(mock_elements_worker):
    elt = Element({"zone": None})

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_element_transcriptions(
            element=elt,
            sub_element_type=None,
            transcriptions=TRANSCRIPTIONS_SAMPLE,
        )
    assert (
        str(e.value) == "sub_element_type shouldn't be null and should be of type str"
    )

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_element_transcriptions(
            element=elt,
            sub_element_type=1234,
            transcriptions=TRANSCRIPTIONS_SAMPLE,
        )
    assert (
        str(e.value) == "sub_element_type shouldn't be null and should be of type str"
    )


def test_create_element_transcriptions_wrong_transcriptions(mock_elements_worker):
    elt = Element({"zone": None})

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_element_transcriptions(
            element=elt,
            sub_element_type="page",
            transcriptions=None,
        )
    assert str(e.value) == "transcriptions shouldn't be null and should be of type list"

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_element_transcriptions(
            element=elt,
            sub_element_type="page",
            transcriptions=1234,
        )
    assert str(e.value) == "transcriptions shouldn't be null and should be of type list"

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_element_transcriptions(
            element=elt,
            sub_element_type="page",
            transcriptions=[
                {
                    "polygon": [[0, 0], [2000, 0], [2000, 3000], [0, 3000]],
                    "score": 0.75,
                    "text": "The",
                },
                {
                    "polygon": [[100, 150], [700, 150], [700, 200], [100, 200]],
                    "score": 0.5,
                },
            ],
        )
    assert (
        str(e.value)
        == "Transcription at index 1 in transcriptions: text shouldn't be null and should be of type str"
    )

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_element_transcriptions(
            element=elt,
            sub_element_type="page",
            transcriptions=[
                {
                    "polygon": [[0, 0], [2000, 0], [2000, 3000], [0, 3000]],
                    "score": 0.75,
                    "text": "The",
                },
                {
                    "polygon": [[100, 150], [700, 150], [700, 200], [100, 200]],
                    "score": 0.5,
                    "text": None,
                },
            ],
        )
    assert (
        str(e.value)
        == "Transcription at index 1 in transcriptions: text shouldn't be null and should be of type str"
    )

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_element_transcriptions(
            element=elt,
            sub_element_type="page",
            transcriptions=[
                {
                    "polygon": [[0, 0], [2000, 0], [2000, 3000], [0, 3000]],
                    "score": 0.75,
                    "text": "The",
                },
                {
                    "polygon": [[100, 150], [700, 150], [700, 200], [100, 200]],
                    "score": 0.5,
                    "text": 1234,
                },
            ],
        )
    assert (
        str(e.value)
        == "Transcription at index 1 in transcriptions: text shouldn't be null and should be of type str"
    )

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_element_transcriptions(
            element=elt,
            sub_element_type="page",
            transcriptions=[
                {
                    "polygon": [[0, 0], [2000, 0], [2000, 3000], [0, 3000]],
                    "score": 0.75,
                    "text": "The",
                },
                {
                    "polygon": [[100, 150], [700, 150], [700, 200], [100, 200]],
                    "text": "word",
                },
            ],
        )
    assert (
        str(e.value)
        == "Transcription at index 1 in transcriptions: score shouldn't be null and should be a float in [0..1] range"
    )

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_element_transcriptions(
            element=elt,
            sub_element_type="page",
            transcriptions=[
                {
                    "polygon": [[0, 0], [2000, 0], [2000, 3000], [0, 3000]],
                    "score": 0.75,
                    "text": "The",
                },
                {
                    "polygon": [[100, 150], [700, 150], [700, 200], [100, 200]],
                    "score": None,
                    "text": "word",
                },
            ],
        )
    assert (
        str(e.value)
        == "Transcription at index 1 in transcriptions: score shouldn't be null and should be a float in [0..1] range"
    )

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_element_transcriptions(
            element=elt,
            sub_element_type="page",
            transcriptions=[
                {
                    "polygon": [[0, 0], [2000, 0], [2000, 3000], [0, 3000]],
                    "score": 0.75,
                    "text": "The",
                },
                {
                    "polygon": [[100, 150], [700, 150], [700, 200], [100, 200]],
                    "score": "a wrong score",
                    "text": "word",
                },
            ],
        )
    assert (
        str(e.value)
        == "Transcription at index 1 in transcriptions: score shouldn't be null and should be a float in [0..1] range"
    )

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_element_transcriptions(
            element=elt,
            sub_element_type="page",
            transcriptions=[
                {
                    "polygon": [[0, 0], [2000, 0], [2000, 3000], [0, 3000]],
                    "score": 0.75,
                    "text": "The",
                },
                {
                    "polygon": [[100, 150], [700, 150], [700, 200], [100, 200]],
                    "score": 0,
                    "text": "word",
                },
            ],
        )
    assert (
        str(e.value)
        == "Transcription at index 1 in transcriptions: score shouldn't be null and should be a float in [0..1] range"
    )

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_element_transcriptions(
            element=elt,
            sub_element_type="page",
            transcriptions=[
                {
                    "polygon": [[0, 0], [2000, 0], [2000, 3000], [0, 3000]],
                    "score": 0.75,
                    "text": "The",
                },
                {
                    "polygon": [[100, 150], [700, 150], [700, 200], [100, 200]],
                    "score": 2.00,
                    "text": "word",
                },
            ],
        )
    assert (
        str(e.value)
        == "Transcription at index 1 in transcriptions: score shouldn't be null and should be a float in [0..1] range"
    )

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_element_transcriptions(
            element=elt,
            sub_element_type="page",
            transcriptions=[
                {
                    "polygon": [[0, 0], [2000, 0], [2000, 3000], [0, 3000]],
                    "score": 0.75,
                    "text": "The",
                },
                {"score": 0.5, "text": "word"},
            ],
        )
    assert (
        str(e.value)
        == "Transcription at index 1 in transcriptions: polygon shouldn't be null and should be of type list"
    )

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_element_transcriptions(
            element=elt,
            sub_element_type="page",
            transcriptions=[
                {
                    "polygon": [[0, 0], [2000, 0], [2000, 3000], [0, 3000]],
                    "score": 0.75,
                    "text": "The",
                },
                {"polygon": None, "score": 0.5, "text": "word"},
            ],
        )
    assert (
        str(e.value)
        == "Transcription at index 1 in transcriptions: polygon shouldn't be null and should be of type list"
    )

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_element_transcriptions(
            element=elt,
            sub_element_type="page",
            transcriptions=[
                {
                    "polygon": [[0, 0], [2000, 0], [2000, 3000], [0, 3000]],
                    "score": 0.75,
                    "text": "The",
                },
                {"polygon": "not a polygon", "score": 0.5, "text": "word"},
            ],
        )
    assert (
        str(e.value)
        == "Transcription at index 1 in transcriptions: polygon shouldn't be null and should be of type list"
    )

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_element_transcriptions(
            element=elt,
            sub_element_type="page",
            transcriptions=[
                {
                    "polygon": [[0, 0], [2000, 0], [2000, 3000], [0, 3000]],
                    "score": 0.75,
                    "text": "The",
                },
                {"polygon": [[1, 1], [2, 2]], "score": 0.5, "text": "word"},
            ],
        )
    assert (
        str(e.value)
        == "Transcription at index 1 in transcriptions: polygon should have at least three points"
    )

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_element_transcriptions(
            element=elt,
            sub_element_type="page",
            transcriptions=[
                {
                    "polygon": [[0, 0], [2000, 0], [2000, 3000], [0, 3000]],
                    "score": 0.75,
                    "text": "The",
                },
                {
                    "polygon": [[1, 1, 1], [2, 2, 1], [2, 1, 1], [1, 2, 1]],
                    "score": 0.5,
                    "text": "word",
                },
            ],
        )
    assert (
        str(e.value)
        == "Transcription at index 1 in transcriptions: polygon points should be lists of two items"
    )

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_element_transcriptions(
            element=elt,
            sub_element_type="page",
            transcriptions=[
                {
                    "polygon": [[0, 0], [2000, 0], [2000, 3000], [0, 3000]],
                    "score": 0.75,
                    "text": "The",
                },
                {"polygon": [[1], [2], [2], [1]], "score": 0.5, "text": "word"},
            ],
        )
    assert (
        str(e.value)
        == "Transcription at index 1 in transcriptions: polygon points should be lists of two items"
    )

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_element_transcriptions(
            element=elt,
            sub_element_type="page",
            transcriptions=[
                {
                    "polygon": [[0, 0], [2000, 0], [2000, 3000], [0, 3000]],
                    "score": 0.75,
                    "text": "The",
                },
                {
                    "polygon": [["not a coord", 1], [2, 2], [2, 1], [1, 2]],
                    "score": 0.5,
                    "text": "word",
                },
            ],
        )
    assert (
        str(e.value)
        == "Transcription at index 1 in transcriptions: polygon points should be lists of two numbers"
    )

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_element_transcriptions(
            element=elt,
            sub_element_type="page",
            transcriptions=[
                {
                    "polygon": [[0, 0], [2000, 0], [2000, 3000], [0, 3000]],
                    "score": 0.75,
                    "text": "The",
                },
                {
                    "polygon": [[100, 150], [700, 150], [700, 200], [100, 200]],
                    "score": 0.35,
                    "text": "word",
                    "orientation": "uptown",
                },
            ],
        )
        assert (
            str(e.value)
            == "Transcription at index 1 in transcriptions: orientation shouldn't be null and should be of type TextOrientation"
        )


def test_create_element_transcriptions_api_error(responses, mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})
    responses.add(
        responses.POST,
        f"http://testserver/api/v1/element/{elt.id}/transcriptions/bulk/",
        status=500,
    )

    with pytest.raises(ErrorResponse):
        mock_elements_worker.create_element_transcriptions(
            element=elt,
            sub_element_type="page",
            transcriptions=TRANSCRIPTIONS_SAMPLE,
        )

    assert len(responses.calls) == len(BASE_API_CALLS) + 5
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        # We retry 5 times the API call
        ("POST", f"http://testserver/api/v1/element/{elt.id}/transcriptions/bulk/"),
        ("POST", f"http://testserver/api/v1/element/{elt.id}/transcriptions/bulk/"),
        ("POST", f"http://testserver/api/v1/element/{elt.id}/transcriptions/bulk/"),
        ("POST", f"http://testserver/api/v1/element/{elt.id}/transcriptions/bulk/"),
        ("POST", f"http://testserver/api/v1/element/{elt.id}/transcriptions/bulk/"),
    ]


def test_create_element_transcriptions(responses, mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})
    responses.add(
        responses.POST,
        f"http://testserver/api/v1/element/{elt.id}/transcriptions/bulk/",
        status=200,
        json=[
            {
                "id": "56785678-5678-5678-5678-567856785678",
                "element_id": "11111111-1111-1111-1111-111111111111",
                "created": True,
            },
            {
                "id": "67896789-6789-6789-6789-678967896789",
                "element_id": "22222222-2222-2222-2222-222222222222",
                "created": False,
            },
            {
                "id": "78907890-7890-7890-7890-789078907890",
                "element_id": "11111111-1111-1111-1111-111111111111",
                "created": True,
            },
        ],
    )

    annotations = mock_elements_worker.create_element_transcriptions(
        element=elt,
        sub_element_type="page",
        transcriptions=TRANSCRIPTIONS_SAMPLE,
    )

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        ("POST", f"http://testserver/api/v1/element/{elt.id}/transcriptions/bulk/"),
    ]

    assert json.loads(responses.calls[-1].request.body) == {
        "element_type": "page",
        "worker_version": "12341234-1234-1234-1234-123412341234",
        "transcriptions": [
            {
                "polygon": [[100, 150], [700, 150], [700, 200], [100, 200]],
                "score": 0.5,
                "text": "The",
                "orientation": TextOrientation.HorizontalLeftToRight.value,
            },
            {
                "polygon": [[0, 0], [2000, 0], [2000, 3000], [0, 3000]],
                "score": 0.75,
                "text": "first",
                "orientation": TextOrientation.HorizontalLeftToRight.value,
            },
            {
                "polygon": [[1000, 300], [1200, 300], [1200, 500], [1000, 500]],
                "score": 0.9,
                "text": "line",
                "orientation": TextOrientation.HorizontalLeftToRight.value,
            },
        ],
        "return_elements": True,
    }
    assert annotations == [
        {
            "id": "56785678-5678-5678-5678-567856785678",
            "element_id": "11111111-1111-1111-1111-111111111111",
            "created": True,
        },
        {
            "id": "67896789-6789-6789-6789-678967896789",
            "element_id": "22222222-2222-2222-2222-222222222222",
            "created": False,
        },
        {
            "id": "78907890-7890-7890-7890-789078907890",
            "element_id": "11111111-1111-1111-1111-111111111111",
            "created": True,
        },
    ]


def test_create_element_transcriptions_with_cache(
    responses, mock_elements_worker_with_cache
):
    elt = CachedElement(id="12341234-1234-1234-1234-123412341234", type="thing")

    responses.add(
        responses.POST,
        f"http://testserver/api/v1/element/{elt.id}/transcriptions/bulk/",
        status=200,
        json=[
            {
                "id": "56785678-5678-5678-5678-567856785678",
                "element_id": "11111111-1111-1111-1111-111111111111",
                "created": True,
            },
            {
                "id": "67896789-6789-6789-6789-678967896789",
                "element_id": "22222222-2222-2222-2222-222222222222",
                "created": False,
            },
            {
                "id": "78907890-7890-7890-7890-789078907890",
                "element_id": "11111111-1111-1111-1111-111111111111",
                "created": True,
            },
        ],
    )

    annotations = mock_elements_worker_with_cache.create_element_transcriptions(
        element=elt,
        sub_element_type="page",
        transcriptions=TRANSCRIPTIONS_SAMPLE,
    )

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        ("POST", f"http://testserver/api/v1/element/{elt.id}/transcriptions/bulk/"),
    ]

    assert json.loads(responses.calls[-1].request.body) == {
        "element_type": "page",
        "worker_version": "12341234-1234-1234-1234-123412341234",
        "transcriptions": [
            {
                "polygon": [[100, 150], [700, 150], [700, 200], [100, 200]],
                "score": 0.5,
                "text": "The",
                "orientation": TextOrientation.HorizontalLeftToRight.value,
            },
            {
                "polygon": [[0, 0], [2000, 0], [2000, 3000], [0, 3000]],
                "score": 0.75,
                "text": "first",
                "orientation": TextOrientation.HorizontalLeftToRight.value,
            },
            {
                "polygon": [[1000, 300], [1200, 300], [1200, 500], [1000, 500]],
                "score": 0.9,
                "text": "line",
                "orientation": TextOrientation.HorizontalLeftToRight.value,
            },
        ],
        "return_elements": True,
    }
    assert annotations == [
        {
            "id": "56785678-5678-5678-5678-567856785678",
            "element_id": "11111111-1111-1111-1111-111111111111",
            "created": True,
        },
        {
            "id": "67896789-6789-6789-6789-678967896789",
            "element_id": "22222222-2222-2222-2222-222222222222",
            "created": False,
        },
        {
            "id": "78907890-7890-7890-7890-789078907890",
            "element_id": "11111111-1111-1111-1111-111111111111",
            "created": True,
        },
    ]

    # Check that created transcriptions and elements were properly stored in SQLite cache
    assert list(CachedElement.select()) == [
        CachedElement(
            id=UUID("11111111-1111-1111-1111-111111111111"),
            parent_id=UUID("12341234-1234-1234-1234-123412341234"),
            type="page",
            polygon="[[100, 150], [700, 150], [700, 200], [100, 200]]",
            worker_version_id=UUID("12341234-1234-1234-1234-123412341234"),
        ),
        CachedElement(
            id=UUID("22222222-2222-2222-2222-222222222222"),
            parent_id=UUID("12341234-1234-1234-1234-123412341234"),
            type="page",
            polygon="[[0, 0], [2000, 0], [2000, 3000], [0, 3000]]",
            worker_version_id=UUID("12341234-1234-1234-1234-123412341234"),
        ),
    ]
    assert list(CachedTranscription.select()) == [
        CachedTranscription(
            id=UUID("56785678-5678-5678-5678-567856785678"),
            element_id=UUID("11111111-1111-1111-1111-111111111111"),
            text="The",
            confidence=0.5,
            orientation=TextOrientation.HorizontalLeftToRight.value,
            worker_version_id=UUID("12341234-1234-1234-1234-123412341234"),
        ),
        CachedTranscription(
            id=UUID("67896789-6789-6789-6789-678967896789"),
            element_id=UUID("22222222-2222-2222-2222-222222222222"),
            text="first",
            confidence=0.75,
            orientation=TextOrientation.HorizontalLeftToRight.value,
            worker_version_id=UUID("12341234-1234-1234-1234-123412341234"),
        ),
        CachedTranscription(
            id=UUID("78907890-7890-7890-7890-789078907890"),
            element_id=UUID("11111111-1111-1111-1111-111111111111"),
            text="line",
            confidence=0.9,
            orientation=TextOrientation.HorizontalLeftToRight.value,
            worker_version_id=UUID("12341234-1234-1234-1234-123412341234"),
        ),
    ]


def test_create_transcriptions_orientation_with_cache(
    responses, mock_elements_worker_with_cache
):
    elt = CachedElement(id="12341234-1234-1234-1234-123412341234", type="thing")

    responses.add(
        responses.POST,
        f"http://testserver/api/v1/element/{elt.id}/transcriptions/bulk/",
        status=200,
        json=[
            {
                "id": "56785678-5678-5678-5678-567856785678",
                "element_id": "11111111-1111-1111-1111-111111111111",
                "created": True,
            },
            {
                "id": "67896789-6789-6789-6789-678967896789",
                "element_id": "22222222-2222-2222-2222-222222222222",
                "created": False,
            },
            {
                "id": "78907890-7890-7890-7890-789078907890",
                "element_id": "11111111-1111-1111-1111-111111111111",
                "created": True,
            },
        ],
    )

    oriented_transcriptions = [
        {
            "polygon": [[100, 150], [700, 150], [700, 200], [100, 200]],
            "score": 0.5,
            "text": "Animula vagula blandula",
        },
        {
            "polygon": [[0, 0], [2000, 0], [2000, 3000], [0, 3000]],
            "score": 0.75,
            "text": "Hospes comesque corporis",
            "orientation": TextOrientation.VerticalLeftToRight,
        },
        {
            "polygon": [[100, 150], [700, 150], [700, 200], [100, 200]],
            "score": 0.9,
            "text": "Quae nunc abibis in loca",
            "orientation": TextOrientation.HorizontalRightToLeft,
        },
    ]

    annotations = mock_elements_worker_with_cache.create_element_transcriptions(
        element=elt,
        sub_element_type="page",
        transcriptions=oriented_transcriptions,
    )

    assert json.loads(responses.calls[-1].request.body) == {
        "element_type": "page",
        "worker_version": "12341234-1234-1234-1234-123412341234",
        "transcriptions": [
            {
                "polygon": [[100, 150], [700, 150], [700, 200], [100, 200]],
                "score": 0.5,
                "text": "Animula vagula blandula",
                "orientation": TextOrientation.HorizontalLeftToRight.value,
            },
            {
                "polygon": [[0, 0], [2000, 0], [2000, 3000], [0, 3000]],
                "score": 0.75,
                "text": "Hospes comesque corporis",
                "orientation": TextOrientation.VerticalLeftToRight.value,
            },
            {
                "polygon": [[100, 150], [700, 150], [700, 200], [100, 200]],
                "score": 0.9,
                "text": "Quae nunc abibis in loca",
                "orientation": TextOrientation.HorizontalRightToLeft.value,
            },
        ],
        "return_elements": True,
    }
    assert annotations == [
        {
            "id": "56785678-5678-5678-5678-567856785678",
            "element_id": "11111111-1111-1111-1111-111111111111",
            "created": True,
        },
        {
            "id": "67896789-6789-6789-6789-678967896789",
            "element_id": "22222222-2222-2222-2222-222222222222",
            "created": False,
        },
        {
            "id": "78907890-7890-7890-7890-789078907890",
            "element_id": "11111111-1111-1111-1111-111111111111",
            "created": True,
        },
    ]

    # Check that the text orientation was properly stored in SQLite cache
    assert list(map(model_to_dict, CachedTranscription.select())) == [
        {
            "id": UUID("56785678-5678-5678-5678-567856785678"),
            "element": {
                "id": UUID("11111111-1111-1111-1111-111111111111"),
                "parent_id": UUID(elt.id),
                "type": "page",
                "image": None,
                "polygon": [[100, 150], [700, 150], [700, 200], [100, 200]],
                "rotation_angle": 0,
                "mirrored": False,
                "initial": False,
                "worker_version_id": UUID("12341234-1234-1234-1234-123412341234"),
            },
            "text": "Animula vagula blandula",
            "confidence": 0.5,
            "orientation": TextOrientation.HorizontalLeftToRight.value,
            "worker_version_id": UUID("12341234-1234-1234-1234-123412341234"),
        },
        {
            "id": UUID("67896789-6789-6789-6789-678967896789"),
            "element": {
                "id": UUID("22222222-2222-2222-2222-222222222222"),
                "parent_id": UUID(elt.id),
                "type": "page",
                "image": None,
                "polygon": [[0, 0], [2000, 0], [2000, 3000], [0, 3000]],
                "rotation_angle": 0,
                "mirrored": False,
                "initial": False,
                "worker_version_id": UUID("12341234-1234-1234-1234-123412341234"),
            },
            "text": "Hospes comesque corporis",
            "confidence": 0.75,
            "orientation": TextOrientation.VerticalLeftToRight.value,
            "worker_version_id": UUID("12341234-1234-1234-1234-123412341234"),
        },
        {
            "id": UUID("78907890-7890-7890-7890-789078907890"),
            "element": {
                "id": UUID("11111111-1111-1111-1111-111111111111"),
                "parent_id": UUID(elt.id),
                "type": "page",
                "image": None,
                "polygon": [[100, 150], [700, 150], [700, 200], [100, 200]],
                "rotation_angle": 0,
                "mirrored": False,
                "initial": False,
                "worker_version_id": UUID("12341234-1234-1234-1234-123412341234"),
            },
            "text": "Quae nunc abibis in loca",
            "confidence": 0.9,
            "orientation": TextOrientation.HorizontalRightToLeft.value,
            "worker_version_id": UUID("12341234-1234-1234-1234-123412341234"),
        },
    ]


def test_list_transcriptions_wrong_element(mock_elements_worker):
    with pytest.raises(AssertionError) as e:
        mock_elements_worker.list_transcriptions(element=None)
    assert (
        str(e.value)
        == "element shouldn't be null and should be an Element or CachedElement"
    )

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.list_transcriptions(element="not element type")
    assert (
        str(e.value)
        == "element shouldn't be null and should be an Element or CachedElement"
    )


def test_list_transcriptions_wrong_element_type(mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.list_transcriptions(
            element=elt,
            element_type=1234,
        )
    assert str(e.value) == "element_type should be of type str"


def test_list_transcriptions_wrong_recursive(mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.list_transcriptions(
            element=elt,
            recursive="not bool",
        )
    assert str(e.value) == "recursive should be of type bool"


def test_list_transcriptions_wrong_worker_version(mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.list_transcriptions(
            element=elt,
            worker_version=1234,
        )
    assert str(e.value) == "worker_version should be of type str"


def test_list_transcriptions_api_error(responses, mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})
    responses.add(
        responses.GET,
        "http://testserver/api/v1/element/12341234-1234-1234-1234-123412341234/transcriptions/",
        status=500,
    )

    with pytest.raises(
        Exception, match="Stopping pagination as data will be incomplete"
    ):
        next(mock_elements_worker.list_transcriptions(element=elt))

    assert len(responses.calls) == len(BASE_API_CALLS) + 5
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        # We do 5 retries
        (
            "GET",
            "http://testserver/api/v1/element/12341234-1234-1234-1234-123412341234/transcriptions/",
        ),
        (
            "GET",
            "http://testserver/api/v1/element/12341234-1234-1234-1234-123412341234/transcriptions/",
        ),
        (
            "GET",
            "http://testserver/api/v1/element/12341234-1234-1234-1234-123412341234/transcriptions/",
        ),
        (
            "GET",
            "http://testserver/api/v1/element/12341234-1234-1234-1234-123412341234/transcriptions/",
        ),
        (
            "GET",
            "http://testserver/api/v1/element/12341234-1234-1234-1234-123412341234/transcriptions/",
        ),
    ]


def test_list_transcriptions(responses, mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})
    trans = [
        {
            "id": "0000",
            "text": "hey",
            "confidence": 0.42,
            "worker_version_id": "56785678-5678-5678-5678-567856785678",
            "element": None,
        },
        {
            "id": "1111",
            "text": "it's",
            "confidence": 0.42,
            "worker_version_id": "56785678-5678-5678-5678-567856785678",
            "element": None,
        },
        {
            "id": "2222",
            "text": "me",
            "confidence": 0.42,
            "worker_version_id": "56785678-5678-5678-5678-567856785678",
            "element": None,
        },
    ]
    responses.add(
        responses.GET,
        "http://testserver/api/v1/element/12341234-1234-1234-1234-123412341234/transcriptions/",
        status=200,
        json={
            "count": 3,
            "next": None,
            "results": trans,
        },
    )

    for idx, transcription in enumerate(
        mock_elements_worker.list_transcriptions(element=elt)
    ):
        assert transcription == trans[idx]

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        (
            "GET",
            "http://testserver/api/v1/element/12341234-1234-1234-1234-123412341234/transcriptions/",
        ),
    ]


@pytest.mark.parametrize(
    "filters, expected_ids",
    (
        # Filter on element should give first transcription
        (
            {
                "element": CachedElement(
                    id="11111111-1111-1111-1111-111111111111", type="page"
                ),
            },
            ("11111111-1111-1111-1111-111111111111",),
        ),
        # Filter on element and element_type should give first transcription
        (
            {
                "element": CachedElement(
                    id="11111111-1111-1111-1111-111111111111", type="page"
                ),
                "element_type": "page",
            },
            ("11111111-1111-1111-1111-111111111111",),
        ),
        # Filter on element and worker_version should give first transcription
        (
            {
                "element": CachedElement(
                    id="11111111-1111-1111-1111-111111111111", type="page"
                ),
                "worker_version": "56785678-5678-5678-5678-567856785678",
            },
            ("11111111-1111-1111-1111-111111111111",),
        ),
        # Filter recursively on element should give all transcriptions inserted
        (
            {
                "element": CachedElement(
                    id="11111111-1111-1111-1111-111111111111", type="page"
                ),
                "recursive": True,
            },
            (
                "11111111-1111-1111-1111-111111111111",
                "22222222-2222-2222-2222-222222222222",
                "33333333-3333-3333-3333-333333333333",
                "44444444-4444-4444-4444-444444444444",
                "55555555-5555-5555-5555-555555555555",
            ),
        ),
        # Filter recursively on element and worker_version should give four transcriptions
        (
            {
                "element": CachedElement(
                    id="11111111-1111-1111-1111-111111111111", type="page"
                ),
                "worker_version": "90129012-9012-9012-9012-901290129012",
                "recursive": True,
            },
            (
                "22222222-2222-2222-2222-222222222222",
                "33333333-3333-3333-3333-333333333333",
                "44444444-4444-4444-4444-444444444444",
                "55555555-5555-5555-5555-555555555555",
            ),
        ),
        # Filter recursively on element and element_type should give three transcriptions
        (
            {
                "element": CachedElement(
                    id="11111111-1111-1111-1111-111111111111", type="page"
                ),
                "element_type": "something_else",
                "recursive": True,
            },
            (
                "22222222-2222-2222-2222-222222222222",
                "44444444-4444-4444-4444-444444444444",
                "55555555-5555-5555-5555-555555555555",
            ),
        ),
    ),
)
def test_list_transcriptions_with_cache(
    responses,
    mock_elements_worker_with_cache,
    mock_cached_transcriptions,
    filters,
    expected_ids,
):
    # Check we have 5 elements already present in database
    assert CachedTranscription.select().count() == 5

    # Query database through cache
    transcriptions = mock_elements_worker_with_cache.list_transcriptions(**filters)
    assert transcriptions.count() == len(expected_ids)
    for transcription, expected_id in zip(transcriptions.order_by("id"), expected_ids):
        assert transcription.id == UUID(expected_id)

    # Check the worker never hits the API for elements
    assert len(responses.calls) == len(BASE_API_CALLS)
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS
