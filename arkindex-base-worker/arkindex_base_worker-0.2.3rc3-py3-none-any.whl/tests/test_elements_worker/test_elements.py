# -*- coding: utf-8 -*-
import json
from argparse import Namespace
from uuid import UUID

import pytest
from apistar.exceptions import ErrorResponse

from arkindex_worker.cache import CachedElement, CachedImage
from arkindex_worker.models import Element
from arkindex_worker.worker import ElementsWorker
from arkindex_worker.worker.element import MissingTypeError

from . import BASE_API_CALLS


def test_check_required_types_argument_types(mock_elements_worker):
    corpus_id = "12341234-1234-1234-1234-123412341234"
    worker = ElementsWorker()

    with pytest.raises(AssertionError) as e:
        worker.check_required_types(corpus_id)
    assert str(e.value) == "At least one element type slug is required."

    with pytest.raises(AssertionError) as e:
        worker.check_required_types(corpus_id, "lol", 42)
    assert str(e.value) == "Element type slugs must be strings."


def test_check_required_types(monkeypatch, tmp_path, mock_elements_worker, responses):
    elements_path = tmp_path / "elements.json"
    elements_path.write_text("[]")
    monkeypatch.setenv("TASK_ELEMENTS", str(elements_path))

    corpus_id = "12341234-1234-1234-1234-123412341234"
    responses.add(
        responses.GET,
        f"http://testserver/api/v1/corpus/{corpus_id}/",
        json={
            "id": corpus_id,
            "name": "Some Corpus",
            "types": [{"slug": "folder"}, {"slug": "page"}],
        },
    )
    worker = ElementsWorker()
    worker.configure()

    assert worker.check_required_types(corpus_id, "page")
    assert worker.check_required_types(corpus_id, "page", "folder")

    with pytest.raises(MissingTypeError) as e:
        assert worker.check_required_types(corpus_id, "page", "text_line", "act")
    assert (
        str(e.value)
        == "Element type(s) act, text_line were not found in the Some Corpus corpus (12341234-1234-1234-1234-123412341234)."
    )


def test_list_elements_elements_list_arg_wrong_type(
    monkeypatch, tmp_path, mock_elements_worker
):
    elements_path = tmp_path / "elements.json"
    elements_path.write_text("{}")

    monkeypatch.setenv("TASK_ELEMENTS", str(elements_path))
    worker = ElementsWorker()
    worker.configure()

    with pytest.raises(AssertionError) as e:
        worker.list_elements()
    assert str(e.value) == "Elements list must be a list"


def test_list_elements_elements_list_arg_empty_list(
    monkeypatch, tmp_path, mock_elements_worker
):
    elements_path = tmp_path / "elements.json"
    elements_path.write_text("[]")

    monkeypatch.setenv("TASK_ELEMENTS", str(elements_path))
    worker = ElementsWorker()
    worker.configure()

    with pytest.raises(AssertionError) as e:
        worker.list_elements()
    assert str(e.value) == "No elements in elements list"


def test_list_elements_elements_list_arg_missing_id(
    monkeypatch, tmp_path, mock_elements_worker
):
    elements_path = tmp_path / "elements.json"
    with elements_path.open("w") as f:
        json.dump([{"type": "volume"}], f)

    monkeypatch.setenv("TASK_ELEMENTS", str(elements_path))
    worker = ElementsWorker()
    worker.configure()

    elt_list = worker.list_elements()

    assert elt_list == []


def test_list_elements_elements_list_arg(monkeypatch, tmp_path, mock_elements_worker):
    elements_path = tmp_path / "elements.json"
    with elements_path.open("w") as f:
        json.dump(
            [
                {"id": "volumeid", "type": "volume"},
                {"id": "pageid", "type": "page"},
                {"id": "actid", "type": "act"},
                {"id": "surfaceid", "type": "surface"},
            ],
            f,
        )

    monkeypatch.setenv("TASK_ELEMENTS", str(elements_path))
    worker = ElementsWorker()
    worker.configure()

    elt_list = worker.list_elements()

    assert elt_list == ["volumeid", "pageid", "actid", "surfaceid"]


def test_list_elements_element_arg(mocker, mock_elements_worker):
    mocker.patch(
        "arkindex_worker.worker.base.argparse.ArgumentParser.parse_args",
        return_value=Namespace(
            element=["volumeid", "pageid"],
            verbose=False,
            elements_list=None,
            database=None,
            dev=False,
        ),
    )

    worker = ElementsWorker()
    worker.configure()

    elt_list = worker.list_elements()

    assert elt_list == ["volumeid", "pageid"]


def test_list_elements_both_args_error(mocker, mock_elements_worker, tmp_path):
    elements_path = tmp_path / "elements.json"
    with elements_path.open("w") as f:
        json.dump(
            [
                {"id": "volumeid", "type": "volume"},
                {"id": "pageid", "type": "page"},
                {"id": "actid", "type": "act"},
                {"id": "surfaceid", "type": "surface"},
            ],
            f,
        )
    mocker.patch(
        "arkindex_worker.worker.base.argparse.ArgumentParser.parse_args",
        return_value=Namespace(
            element=["anotherid", "againanotherid"],
            verbose=False,
            elements_list=elements_path.open(),
            database=None,
            dev=False,
        ),
    )

    worker = ElementsWorker()
    worker.configure()

    with pytest.raises(AssertionError) as e:
        worker.list_elements()
    assert str(e.value) == "elements-list and element CLI args shouldn't be both set"


def test_database_arg(mocker, mock_elements_worker, tmp_path):
    database_path = tmp_path / "my_database.sqlite"
    database_path.touch()

    mocker.patch(
        "arkindex_worker.worker.base.argparse.ArgumentParser.parse_args",
        return_value=Namespace(
            element=["volumeid", "pageid"],
            verbose=False,
            elements_list=None,
            database=str(database_path),
            dev=False,
        ),
    )

    worker = ElementsWorker(support_cache=True)
    worker.configure()

    assert worker.use_cache is True
    assert worker.cache_path == str(database_path)


def test_load_corpus_classes_api_error(responses, mock_elements_worker):
    corpus_id = "12341234-1234-1234-1234-123412341234"
    responses.add(
        responses.GET,
        f"http://testserver/api/v1/corpus/{corpus_id}/classes/",
        status=500,
    )

    assert not mock_elements_worker.classes
    with pytest.raises(
        Exception, match="Stopping pagination as data will be incomplete"
    ):
        mock_elements_worker.load_corpus_classes(corpus_id)

    assert len(responses.calls) == len(BASE_API_CALLS) + 5
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        # We do 5 retries
        ("GET", f"http://testserver/api/v1/corpus/{corpus_id}/classes/"),
        ("GET", f"http://testserver/api/v1/corpus/{corpus_id}/classes/"),
        ("GET", f"http://testserver/api/v1/corpus/{corpus_id}/classes/"),
        ("GET", f"http://testserver/api/v1/corpus/{corpus_id}/classes/"),
        ("GET", f"http://testserver/api/v1/corpus/{corpus_id}/classes/"),
    ]
    assert not mock_elements_worker.classes


def test_load_corpus_classes(responses, mock_elements_worker):
    corpus_id = "12341234-1234-1234-1234-123412341234"
    responses.add(
        responses.GET,
        f"http://testserver/api/v1/corpus/{corpus_id}/classes/",
        status=200,
        json={
            "count": 3,
            "next": None,
            "results": [
                {
                    "id": "0000",
                    "name": "good",
                },
                {
                    "id": "1111",
                    "name": "average",
                },
                {
                    "id": "2222",
                    "name": "bad",
                },
            ],
        },
    )

    assert not mock_elements_worker.classes
    mock_elements_worker.load_corpus_classes(corpus_id)

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        ("GET", f"http://testserver/api/v1/corpus/{corpus_id}/classes/"),
    ]
    assert mock_elements_worker.classes == {
        "12341234-1234-1234-1234-123412341234": {
            "good": "0000",
            "average": "1111",
            "bad": "2222",
        }
    }


def test_create_sub_element_wrong_element(mock_elements_worker):
    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_sub_element(
            element=None,
            type="something",
            name="0",
            polygon=[[1, 1], [2, 2], [2, 1], [1, 2]],
        )
    assert str(e.value) == "element shouldn't be null and should be of type Element"

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_sub_element(
            element="not element type",
            type="something",
            name="0",
            polygon=[[1, 1], [2, 2], [2, 1], [1, 2]],
        )
    assert str(e.value) == "element shouldn't be null and should be of type Element"


def test_create_sub_element_wrong_type(mock_elements_worker):
    elt = Element({"zone": None})

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_sub_element(
            element=elt,
            type=None,
            name="0",
            polygon=[[1, 1], [2, 2], [2, 1], [1, 2]],
        )
    assert str(e.value) == "type shouldn't be null and should be of type str"

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_sub_element(
            element=elt,
            type=1234,
            name="0",
            polygon=[[1, 1], [2, 2], [2, 1], [1, 2]],
        )
    assert str(e.value) == "type shouldn't be null and should be of type str"


def test_create_sub_element_wrong_name(mock_elements_worker):
    elt = Element({"zone": None})

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_sub_element(
            element=elt,
            type="something",
            name=None,
            polygon=[[1, 1], [2, 2], [2, 1], [1, 2]],
        )
    assert str(e.value) == "name shouldn't be null and should be of type str"

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_sub_element(
            element=elt,
            type="something",
            name=1234,
            polygon=[[1, 1], [2, 2], [2, 1], [1, 2]],
        )
    assert str(e.value) == "name shouldn't be null and should be of type str"


def test_create_sub_element_wrong_polygon(mock_elements_worker):
    elt = Element({"zone": None})

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_sub_element(
            element=elt,
            type="something",
            name="0",
            polygon=None,
        )
    assert str(e.value) == "polygon shouldn't be null and should be of type list"

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_sub_element(
            element=elt,
            type="something",
            name="O",
            polygon="not a polygon",
        )
    assert str(e.value) == "polygon shouldn't be null and should be of type list"

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_sub_element(
            element=elt,
            type="something",
            name="O",
            polygon=[[1, 1], [2, 2]],
        )
    assert str(e.value) == "polygon should have at least three points"

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_sub_element(
            element=elt,
            type="something",
            name="O",
            polygon=[[1, 1, 1], [2, 2, 1], [2, 1, 1], [1, 2, 1]],
        )
    assert str(e.value) == "polygon points should be lists of two items"

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_sub_element(
            element=elt,
            type="something",
            name="O",
            polygon=[[1], [2], [2], [1]],
        )
    assert str(e.value) == "polygon points should be lists of two items"

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_sub_element(
            element=elt,
            type="something",
            name="O",
            polygon=[["not a coord", 1], [2, 2], [2, 1], [1, 2]],
        )
    assert str(e.value) == "polygon points should be lists of two numbers"


def test_create_sub_element_api_error(responses, mock_elements_worker):
    elt = Element(
        {
            "id": "12341234-1234-1234-1234-123412341234",
            "corpus": {"id": "11111111-1111-1111-1111-111111111111"},
            "zone": {"image": {"id": "22222222-2222-2222-2222-222222222222"}},
        }
    )
    responses.add(
        responses.POST,
        "http://testserver/api/v1/elements/create/",
        status=500,
    )

    with pytest.raises(ErrorResponse):
        mock_elements_worker.create_sub_element(
            element=elt,
            type="something",
            name="0",
            polygon=[[1, 1], [2, 2], [2, 1], [1, 2]],
        )

    assert len(responses.calls) == len(BASE_API_CALLS) + 5
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        # We retry 5 times the API call
        ("POST", "http://testserver/api/v1/elements/create/"),
        ("POST", "http://testserver/api/v1/elements/create/"),
        ("POST", "http://testserver/api/v1/elements/create/"),
        ("POST", "http://testserver/api/v1/elements/create/"),
        ("POST", "http://testserver/api/v1/elements/create/"),
    ]


def test_create_sub_element(responses, mock_elements_worker):
    elt = Element(
        {
            "id": "12341234-1234-1234-1234-123412341234",
            "corpus": {"id": "11111111-1111-1111-1111-111111111111"},
            "zone": {"image": {"id": "22222222-2222-2222-2222-222222222222"}},
        }
    )
    responses.add(
        responses.POST,
        "http://testserver/api/v1/elements/create/",
        status=200,
        json={"id": "12345678-1234-1234-1234-123456789123"},
    )

    sub_element_id = mock_elements_worker.create_sub_element(
        element=elt,
        type="something",
        name="0",
        polygon=[[1, 1], [2, 2], [2, 1], [1, 2]],
    )

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        ("POST", "http://testserver/api/v1/elements/create/"),
    ]
    assert json.loads(responses.calls[-1].request.body) == {
        "type": "something",
        "name": "0",
        "image": "22222222-2222-2222-2222-222222222222",
        "corpus": "11111111-1111-1111-1111-111111111111",
        "polygon": [[1, 1], [2, 2], [2, 1], [1, 2]],
        "parent": "12341234-1234-1234-1234-123412341234",
        "worker_version": "12341234-1234-1234-1234-123412341234",
    }
    assert sub_element_id == "12345678-1234-1234-1234-123456789123"


def test_create_elements_wrong_parent(mock_elements_worker):
    with pytest.raises(TypeError) as e:
        mock_elements_worker.create_elements(
            parent=None,
            elements=[],
        )
    assert (
        str(e.value) == "Parent element should be an Element or CachedElement instance"
    )

    with pytest.raises(TypeError) as e:
        mock_elements_worker.create_elements(
            parent="not element type",
            elements=[],
        )
    assert (
        str(e.value) == "Parent element should be an Element or CachedElement instance"
    )


def test_create_elements_no_zone(mock_elements_worker):
    elt = Element({"zone": None})
    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_elements(
            parent=elt,
            elements=None,
        )
    assert str(e.value) == "create_elements cannot be used on parents without zones"

    elt = CachedElement(
        id="11111111-1111-1111-1111-1111111111", name="blah", type="blah"
    )
    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_elements(
            parent=elt,
            elements=None,
        )
    assert str(e.value) == "create_elements cannot be used on parents without images"


def test_create_elements_wrong_elements(mock_elements_worker):
    elt = Element({"zone": {"image": {"id": "image_id"}}})

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_elements(
            parent=elt,
            elements=None,
        )
    assert str(e.value) == "elements shouldn't be null and should be of type list"

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_elements(
            parent=elt,
            elements="not a list",
        )
    assert str(e.value) == "elements shouldn't be null and should be of type list"


def test_create_elements_wrong_elements_instance(mock_elements_worker):
    elt = Element({"zone": {"image": {"id": "image_id"}}})

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_elements(
            parent=elt,
            elements=["not a dict"],
        )
    assert str(e.value) == "Element at index 0 in elements: Should be of type dict"


def test_create_elements_wrong_elements_name(mock_elements_worker):
    elt = Element({"zone": {"image": {"id": "image_id"}}})

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_elements(
            parent=elt,
            elements=[
                {
                    "name": None,
                    "type": "something",
                    "polygon": [[1, 1], [2, 2], [2, 1], [1, 2]],
                }
            ],
        )
    assert (
        str(e.value)
        == "Element at index 0 in elements: name shouldn't be null and should be of type str"
    )

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_elements(
            parent=elt,
            elements=[
                {
                    "name": 1234,
                    "type": "something",
                    "polygon": [[1, 1], [2, 2], [2, 1], [1, 2]],
                }
            ],
        )
    assert (
        str(e.value)
        == "Element at index 0 in elements: name shouldn't be null and should be of type str"
    )


def test_create_elements_wrong_elements_type(mock_elements_worker):
    elt = Element({"zone": {"image": {"id": "image_id"}}})

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_elements(
            parent=elt,
            elements=[
                {
                    "name": "0",
                    "type": None,
                    "polygon": [[1, 1], [2, 2], [2, 1], [1, 2]],
                }
            ],
        )
    assert (
        str(e.value)
        == "Element at index 0 in elements: type shouldn't be null and should be of type str"
    )

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_elements(
            parent=elt,
            elements=[
                {
                    "name": "0",
                    "type": 1234,
                    "polygon": [[1, 1], [2, 2], [2, 1], [1, 2]],
                }
            ],
        )
    assert (
        str(e.value)
        == "Element at index 0 in elements: type shouldn't be null and should be of type str"
    )


def test_create_elements_wrong_elements_polygon(mock_elements_worker):
    elt = Element({"zone": {"image": {"id": "image_id"}}})

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_elements(
            parent=elt,
            elements=[
                {
                    "name": "0",
                    "type": "something",
                    "polygon": None,
                }
            ],
        )
    assert (
        str(e.value)
        == "Element at index 0 in elements: polygon shouldn't be null and should be of type list"
    )

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_elements(
            parent=elt,
            elements=[
                {
                    "name": "0",
                    "type": "something",
                    "polygon": "not a polygon",
                }
            ],
        )
    assert (
        str(e.value)
        == "Element at index 0 in elements: polygon shouldn't be null and should be of type list"
    )

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_elements(
            parent=elt,
            elements=[
                {
                    "name": "0",
                    "type": "something",
                    "polygon": [[1, 1], [2, 2]],
                }
            ],
        )
    assert (
        str(e.value)
        == "Element at index 0 in elements: polygon should have at least three points"
    )

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_elements(
            parent=elt,
            elements=[
                {
                    "name": "0",
                    "type": "something",
                    "polygon": [[1, 1, 1], [2, 2, 1], [2, 1, 1], [1, 2, 1]],
                }
            ],
        )
    assert (
        str(e.value)
        == "Element at index 0 in elements: polygon points should be lists of two items"
    )

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_elements(
            parent=elt,
            elements=[
                {
                    "name": "0",
                    "type": "something",
                    "polygon": [[1], [2], [2], [1]],
                }
            ],
        )
    assert (
        str(e.value)
        == "Element at index 0 in elements: polygon points should be lists of two items"
    )

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_elements(
            parent=elt,
            elements=[
                {
                    "name": "0",
                    "type": "something",
                    "polygon": [["not a coord", 1], [2, 2], [2, 1], [1, 2]],
                }
            ],
        )
    assert (
        str(e.value)
        == "Element at index 0 in elements: polygon points should be lists of two numbers"
    )


def test_create_elements_api_error(responses, mock_elements_worker):
    elt = Element(
        {
            "id": "12341234-1234-1234-1234-123412341234",
            "zone": {
                "image": {
                    "id": "c0fec0fe-c0fe-c0fe-c0fe-c0fec0fec0fe",
                    "width": 42,
                    "height": 42,
                    "url": "http://aaaa",
                }
            },
        }
    )
    responses.add(
        responses.POST,
        "http://testserver/api/v1/element/12341234-1234-1234-1234-123412341234/children/bulk/",
        status=500,
    )

    with pytest.raises(ErrorResponse):
        mock_elements_worker.create_elements(
            parent=elt,
            elements=[
                {
                    "name": "0",
                    "type": "something",
                    "polygon": [[1, 1], [2, 2], [2, 1], [1, 2]],
                }
            ],
        )

    assert len(responses.calls) == len(BASE_API_CALLS) + 5
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        # We retry 5 times the API call
        (
            "POST",
            "http://testserver/api/v1/element/12341234-1234-1234-1234-123412341234/children/bulk/",
        ),
        (
            "POST",
            "http://testserver/api/v1/element/12341234-1234-1234-1234-123412341234/children/bulk/",
        ),
        (
            "POST",
            "http://testserver/api/v1/element/12341234-1234-1234-1234-123412341234/children/bulk/",
        ),
        (
            "POST",
            "http://testserver/api/v1/element/12341234-1234-1234-1234-123412341234/children/bulk/",
        ),
        (
            "POST",
            "http://testserver/api/v1/element/12341234-1234-1234-1234-123412341234/children/bulk/",
        ),
    ]


def test_create_elements_cached_element(responses, mock_elements_worker_with_cache):
    image = CachedImage.create(
        id=UUID("c0fec0fe-c0fe-c0fe-c0fe-c0fec0fec0fe"),
        width=42,
        height=42,
        url="http://aaaa",
    )
    elt = CachedElement.create(
        id=UUID("12341234-1234-1234-1234-123412341234"),
        type="parent",
        image_id=image.id,
        polygon="[[0, 0], [0, 1000], [1000, 1000], [1000, 0], [0, 0]]",
    )
    responses.add(
        responses.POST,
        "http://testserver/api/v1/element/12341234-1234-1234-1234-123412341234/children/bulk/",
        status=200,
        json=[{"id": "497f6eca-6276-4993-bfeb-53cbbbba6f08"}],
    )

    created_ids = mock_elements_worker_with_cache.create_elements(
        parent=elt,
        elements=[
            {
                "name": "0",
                "type": "something",
                "polygon": [[1, 1], [2, 2], [2, 1], [1, 2]],
            }
        ],
    )

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        (
            "POST",
            "http://testserver/api/v1/element/12341234-1234-1234-1234-123412341234/children/bulk/",
        ),
    ]
    assert json.loads(responses.calls[-1].request.body) == {
        "elements": [
            {
                "name": "0",
                "type": "something",
                "polygon": [[1, 1], [2, 2], [2, 1], [1, 2]],
            }
        ],
        "worker_version": "12341234-1234-1234-1234-123412341234",
    }
    assert created_ids == [{"id": "497f6eca-6276-4993-bfeb-53cbbbba6f08"}]

    # Check that created elements were properly stored in SQLite cache
    assert list(CachedElement.select().order_by(CachedElement.id)) == [
        elt,
        CachedElement(
            id=UUID("497f6eca-6276-4993-bfeb-53cbbbba6f08"),
            parent_id=elt.id,
            type="something",
            image_id="c0fec0fe-c0fe-c0fe-c0fe-c0fec0fec0fe",
            polygon=[[1, 1], [2, 2], [2, 1], [1, 2]],
            worker_version_id=UUID("12341234-1234-1234-1234-123412341234"),
        ),
    ]


def test_create_elements(responses, mock_elements_worker_with_cache, tmp_path):
    elt = Element(
        {
            "id": "12341234-1234-1234-1234-123412341234",
            "zone": {
                "image": {
                    "id": "c0fec0fe-c0fe-c0fe-c0fe-c0fec0fec0fe",
                    "width": 42,
                    "height": 42,
                    "url": "http://aaaa",
                }
            },
        }
    )
    responses.add(
        responses.POST,
        "http://testserver/api/v1/element/12341234-1234-1234-1234-123412341234/children/bulk/",
        status=200,
        json=[{"id": "497f6eca-6276-4993-bfeb-53cbbbba6f08"}],
    )

    created_ids = mock_elements_worker_with_cache.create_elements(
        parent=elt,
        elements=[
            {
                "name": "0",
                "type": "something",
                "polygon": [[1, 1], [2, 2], [2, 1], [1, 2]],
            }
        ],
    )

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        (
            "POST",
            "http://testserver/api/v1/element/12341234-1234-1234-1234-123412341234/children/bulk/",
        ),
    ]
    assert json.loads(responses.calls[-1].request.body) == {
        "elements": [
            {
                "name": "0",
                "type": "something",
                "polygon": [[1, 1], [2, 2], [2, 1], [1, 2]],
            }
        ],
        "worker_version": "12341234-1234-1234-1234-123412341234",
    }
    assert created_ids == [{"id": "497f6eca-6276-4993-bfeb-53cbbbba6f08"}]

    # Check that created elements were properly stored in SQLite cache
    assert (tmp_path / "db.sqlite").is_file()

    assert list(CachedElement.select()) == [
        CachedElement(
            id=UUID("497f6eca-6276-4993-bfeb-53cbbbba6f08"),
            parent_id=UUID("12341234-1234-1234-1234-123412341234"),
            type="something",
            image_id="c0fec0fe-c0fe-c0fe-c0fe-c0fec0fec0fe",
            polygon=[[1, 1], [2, 2], [2, 1], [1, 2]],
            worker_version_id=UUID("12341234-1234-1234-1234-123412341234"),
        )
    ]


def test_create_elements_integrity_error(
    responses, mock_elements_worker_with_cache, caplog
):
    elt = Element(
        {
            "id": "12341234-1234-1234-1234-123412341234",
            "zone": {
                "image": {
                    "id": "c0fec0fe-c0fe-c0fe-c0fe-c0fec0fec0fe",
                    "width": 42,
                    "height": 42,
                    "url": "http://aaaa",
                }
            },
        }
    )
    responses.add(
        responses.POST,
        "http://testserver/api/v1/element/12341234-1234-1234-1234-123412341234/children/bulk/",
        status=200,
        json=[
            # Duplicate IDs, which will cause an IntegrityError when stored in the cache
            {"id": "497f6eca-6276-4993-bfeb-53cbbbba6f08"},
            {"id": "497f6eca-6276-4993-bfeb-53cbbbba6f08"},
        ],
    )

    elements = [
        {
            "name": "0",
            "type": "something",
            "polygon": [[1, 1], [2, 2], [2, 1], [1, 2]],
        },
        {
            "name": "1",
            "type": "something",
            "polygon": [[1, 1], [3, 3], [3, 1], [1, 3]],
        },
    ]

    created_ids = mock_elements_worker_with_cache.create_elements(
        parent=elt,
        elements=elements,
    )

    assert created_ids == [
        {"id": "497f6eca-6276-4993-bfeb-53cbbbba6f08"},
        {"id": "497f6eca-6276-4993-bfeb-53cbbbba6f08"},
    ]

    assert len(caplog.records) == 1
    assert caplog.records[0].levelname == "WARNING"
    assert caplog.records[0].message.startswith(
        "Couldn't save created elements in local cache:"
    )

    assert list(CachedElement.select()) == []


def test_list_element_children_wrong_element(mock_elements_worker):
    with pytest.raises(AssertionError) as e:
        mock_elements_worker.list_element_children(element=None)
    assert (
        str(e.value)
        == "element shouldn't be null and should be an Element or CachedElement"
    )

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.list_element_children(element="not element type")
    assert (
        str(e.value)
        == "element shouldn't be null and should be an Element or CachedElement"
    )


def test_list_element_children_wrong_best_class(mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.list_element_children(
            element=elt,
            best_class=1234,
        )
    assert str(e.value) == "best_class should be of type str or bool"


def test_list_element_children_wrong_folder(mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.list_element_children(
            element=elt,
            folder="not bool",
        )
    assert str(e.value) == "folder should be of type bool"


def test_list_element_children_wrong_name(mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.list_element_children(
            element=elt,
            name=1234,
        )
    assert str(e.value) == "name should be of type str"


def test_list_element_children_wrong_recursive(mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.list_element_children(
            element=elt,
            recursive="not bool",
        )
    assert str(e.value) == "recursive should be of type bool"


def test_list_element_children_wrong_type(mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.list_element_children(
            element=elt,
            type=1234,
        )
    assert str(e.value) == "type should be of type str"


def test_list_element_children_wrong_with_best_classes(mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.list_element_children(
            element=elt,
            with_best_classes="not bool",
        )
    assert str(e.value) == "with_best_classes should be of type bool"


def test_list_element_children_wrong_with_corpus(mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.list_element_children(
            element=elt,
            with_corpus="not bool",
        )
    assert str(e.value) == "with_corpus should be of type bool"


def test_list_element_children_wrong_with_has_children(mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.list_element_children(
            element=elt,
            with_has_children="not bool",
        )
    assert str(e.value) == "with_has_children should be of type bool"


def test_list_element_children_wrong_with_zone(mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.list_element_children(
            element=elt,
            with_zone="not bool",
        )
    assert str(e.value) == "with_zone should be of type bool"


def test_list_element_children_wrong_worker_version(mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.list_element_children(
            element=elt,
            worker_version=1234,
        )
    assert str(e.value) == "worker_version should be of type str"


def test_list_element_children_api_error(responses, mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})
    responses.add(
        responses.GET,
        "http://testserver/api/v1/elements/12341234-1234-1234-1234-123412341234/children/",
        status=500,
    )

    with pytest.raises(
        Exception, match="Stopping pagination as data will be incomplete"
    ):
        next(mock_elements_worker.list_element_children(element=elt))

    assert len(responses.calls) == len(BASE_API_CALLS) + 5
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        # We do 5 retries
        (
            "GET",
            "http://testserver/api/v1/elements/12341234-1234-1234-1234-123412341234/children/",
        ),
        (
            "GET",
            "http://testserver/api/v1/elements/12341234-1234-1234-1234-123412341234/children/",
        ),
        (
            "GET",
            "http://testserver/api/v1/elements/12341234-1234-1234-1234-123412341234/children/",
        ),
        (
            "GET",
            "http://testserver/api/v1/elements/12341234-1234-1234-1234-123412341234/children/",
        ),
        (
            "GET",
            "http://testserver/api/v1/elements/12341234-1234-1234-1234-123412341234/children/",
        ),
    ]


def test_list_element_children(responses, mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})
    expected_children = [
        {
            "id": "0000",
            "type": "page",
            "name": "Test",
            "corpus": {},
            "thumbnail_url": None,
            "zone": {},
            "best_classes": None,
            "has_children": None,
            "worker_version_id": None,
        },
        {
            "id": "1111",
            "type": "page",
            "name": "Test 2",
            "corpus": {},
            "thumbnail_url": None,
            "zone": {},
            "best_classes": None,
            "has_children": None,
            "worker_version_id": None,
        },
        {
            "id": "2222",
            "type": "page",
            "name": "Test 3",
            "corpus": {},
            "thumbnail_url": None,
            "zone": {},
            "best_classes": None,
            "has_children": None,
            "worker_version_id": None,
        },
    ]
    responses.add(
        responses.GET,
        "http://testserver/api/v1/elements/12341234-1234-1234-1234-123412341234/children/",
        status=200,
        json={
            "count": 3,
            "next": None,
            "results": expected_children,
        },
    )

    for idx, child in enumerate(
        mock_elements_worker.list_element_children(element=elt)
    ):
        assert child == expected_children[idx]

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        (
            "GET",
            "http://testserver/api/v1/elements/12341234-1234-1234-1234-123412341234/children/",
        ),
    ]


def test_list_element_children_with_cache_unhandled_param(
    mock_elements_worker_with_cache,
):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})

    with pytest.raises(AssertionError) as e:
        mock_elements_worker_with_cache.list_element_children(
            element=elt, with_corpus=True
        )
    assert (
        str(e.value)
        == "When using the local cache, you can only filter by 'type' and/or 'worker_version'"
    )


@pytest.mark.parametrize(
    "filters, expected_ids",
    (
        # Filter on element should give all elements inserted
        (
            {
                "element": CachedElement(id="12341234-1234-1234-1234-123412341234"),
            },
            (
                "11111111-1111-1111-1111-111111111111",
                "22222222-2222-2222-2222-222222222222",
            ),
        ),
        # Filter on element and page should give the second element
        (
            {
                "element": CachedElement(id="12341234-1234-1234-1234-123412341234"),
                "type": "page",
            },
            ("22222222-2222-2222-2222-222222222222",),
        ),
        # Filter on element and worker version should give all elements
        (
            {
                "element": CachedElement(id="12341234-1234-1234-1234-123412341234"),
                "worker_version": "56785678-5678-5678-5678-567856785678",
            },
            (
                "11111111-1111-1111-1111-111111111111",
                "22222222-2222-2222-2222-222222222222",
            ),
        ),
        # Filter on element, type something  and worker version should give first
        (
            {
                "element": CachedElement(id="12341234-1234-1234-1234-123412341234"),
                "type": "something",
                "worker_version": "56785678-5678-5678-5678-567856785678",
            },
            ("11111111-1111-1111-1111-111111111111",),
        ),
    ),
)
def test_list_element_children_with_cache(
    responses,
    mock_elements_worker_with_cache,
    mock_cached_elements,
    filters,
    expected_ids,
):

    # Check we have 2 elements already present in database
    assert CachedElement.select().count() == 2

    # Query database through cache
    elements = mock_elements_worker_with_cache.list_element_children(**filters)
    assert elements.count() == len(expected_ids)
    for child, expected_id in zip(elements.order_by("id"), expected_ids):
        assert child.id == UUID(expected_id)

    # Check the worker never hits the API for elements
    assert len(responses.calls) == len(BASE_API_CALLS)
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS
