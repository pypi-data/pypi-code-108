# . -*- coding: utf-8 -*-
import json
import sys

import pytest
from apistar.exceptions import ErrorResponse

from arkindex_worker.cache import CachedElement
from arkindex_worker.worker import ActivityState, ElementsWorker

from . import BASE_API_CALLS

TEST_VERSION_ID = "test_123"
TEST_SLUG = "some_slug"


def test_get_worker_version(fake_dummy_worker):
    api_client = fake_dummy_worker.api_client

    response = {"worker": {"slug": TEST_SLUG}}

    api_client.add_response("RetrieveWorkerVersion", response, id=TEST_VERSION_ID)

    res = fake_dummy_worker.get_worker_version(TEST_VERSION_ID)

    assert res == response
    assert fake_dummy_worker._worker_version_cache[TEST_VERSION_ID] == response


def test_get_worker_version__uses_cache(fake_dummy_worker):
    api_client = fake_dummy_worker.api_client

    response = {"worker": {"slug": TEST_SLUG}}

    api_client.add_response("RetrieveWorkerVersion", response, id=TEST_VERSION_ID)

    response_1 = fake_dummy_worker.get_worker_version(TEST_VERSION_ID)
    response_2 = fake_dummy_worker.get_worker_version(TEST_VERSION_ID)

    assert response_1 == response
    assert response_1 == response_2

    # assert that only one call to the API
    assert len(api_client.history) == 1
    assert not api_client.responses


def test_get_worker_version_slug(mocker, fake_dummy_worker):
    fake_dummy_worker.get_worker_version = mocker.MagicMock()
    fake_dummy_worker.get_worker_version.return_value = {
        "id": TEST_VERSION_ID,
        "worker": {"slug": "mock_slug"},
    }

    slug = fake_dummy_worker.get_worker_version_slug(TEST_VERSION_ID)
    assert slug == "mock_slug"


def test_get_worker_version_slug_none(fake_dummy_worker):
    with pytest.raises(ValueError) as excinfo:
        fake_dummy_worker.get_worker_version_slug(None)
    assert str(excinfo.value) == "No worker version ID"


def test_readonly(responses, mock_elements_worker):
    """Test readonly worker does not trigger any API calls"""

    # Setup the worker as read-only
    mock_elements_worker.worker_version_id = None
    assert mock_elements_worker.is_read_only is True

    out = mock_elements_worker.update_activity("1234-deadbeef", ActivityState.Processed)

    # update_activity returns False in very specific cases
    assert out is True
    assert len(responses.calls) == len(BASE_API_CALLS)
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS


def test_activities_disabled(
    responses, monkeypatch, mock_worker_version_api, mock_user_api
):
    """Test worker process elements without updating activities when they are disabled for the process"""
    responses.add(
        responses.GET,
        "http://testserver/api/v1/imports/aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeffff/",
        status=200,
        body=json.dumps({"activity_state": "disabled"}),
        content_type="application/json",
    )
    monkeypatch.setattr(sys, "argv", ["worker"])
    worker = ElementsWorker()
    worker.configure()
    assert not worker.is_read_only

    assert len(responses.calls) == len(BASE_API_CALLS)
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS


def test_activities_dev_mode(mocker, mock_user_api, mock_worker_version_api):
    """
    Worker activities are not stored in dev mode
    """
    worker = ElementsWorker()
    mocker.patch.object(sys, "argv", ["worker", "--dev"])
    worker.configure()

    assert worker.args.dev is True
    assert worker.process_information is None
    assert worker.is_read_only is True
    assert worker.store_activity is False


def test_update_call(responses, mock_elements_worker, mock_process_api):
    """Test an update call with feature enabled triggers an API call"""
    responses.add(
        responses.PUT,
        "http://testserver/api/v1/workers/versions/12341234-1234-1234-1234-123412341234/activity/",
        status=200,
        json={
            "element_id": "1234-deadbeef",
            "process_id": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeffff",
            "state": "processed",
        },
    )

    out = mock_elements_worker.update_activity("1234-deadbeef", ActivityState.Processed)

    # Check the response received by worker
    assert out is True

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        (
            "PUT",
            "http://testserver/api/v1/workers/versions/12341234-1234-1234-1234-123412341234/activity/",
        ),
    ]

    # Check the request sent by worker
    assert json.loads(responses.calls[-1].request.body) == {
        "element_id": "1234-deadbeef",
        "process_id": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeffff",
        "state": "processed",
    }


@pytest.mark.parametrize(
    "process_exception, final_state",
    [
        # Successful process_element
        (None, "processed"),
        # Failures in process_element
        (
            ErrorResponse(title="bad gateway", status_code=502, content="Bad gateway"),
            "error",
        ),
        (ValueError("Something bad"), "error"),
        (Exception("Any error"), "error"),
    ],
)
def test_run(
    monkeypatch,
    mock_elements_worker_with_list,
    responses,
    process_exception,
    final_state,
    mock_activity_calls,
):
    """Check the normal runtime sends 2 API calls to update activity"""
    # Disable second configure call from run()
    monkeypatch.setattr(mock_elements_worker_with_list, "configure", lambda: None)
    assert mock_elements_worker_with_list.is_read_only is False

    # Mock exception in process_element
    if process_exception:

        def _err():
            raise process_exception

        monkeypatch.setattr(mock_elements_worker_with_list, "process_element", _err)

        # The worker stops because all elements failed !
        with pytest.raises(SystemExit):
            mock_elements_worker_with_list.run()
    else:
        # Simply run the process
        mock_elements_worker_with_list.run()

    assert len(responses.calls) == len(BASE_API_CALLS) + 3
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        ("GET", "http://testserver/api/v1/element/1234-deadbeef/"),
        (
            "PUT",
            "http://testserver/api/v1/workers/versions/12341234-1234-1234-1234-123412341234/activity/",
        ),
        (
            "PUT",
            "http://testserver/api/v1/workers/versions/12341234-1234-1234-1234-123412341234/activity/",
        ),
    ]

    # Check the requests sent by worker
    assert json.loads(responses.calls[-2].request.body) == {
        "element_id": "1234-deadbeef",
        "process_id": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeffff",
        "state": "started",
    }
    assert json.loads(responses.calls[-1].request.body) == {
        "element_id": "1234-deadbeef",
        "process_id": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeffff",
        "state": final_state,
    }


def test_run_cache(
    monkeypatch,
    mocker,
    mock_elements_worker_with_cache,
    mock_cached_elements,
    mock_activity_calls,
):
    # Disable second configure call from run()
    monkeypatch.setattr(mock_elements_worker_with_cache, "configure", lambda: None)

    # Make all the cached elements from the fixture initial elements
    CachedElement.update(initial=True).execute()

    mock_elements_worker_with_cache.process_element = mocker.MagicMock()
    mock_elements_worker_with_cache.run()

    assert mock_elements_worker_with_cache.process_element.call_args_list == [
        # Called once for each cached element
        mocker.call(elt)
        for elt in CachedElement.select()
    ]


def test_start_activity_conflict(
    monkeypatch, responses, mocker, mock_elements_worker_with_list
):
    # Disable second configure call from run()
    monkeypatch.setattr(mock_elements_worker_with_list, "configure", lambda: None)

    # Mock a "normal" conflict during in activity update, which returns the Exception
    responses.add(
        responses.PUT,
        "http://testserver/api/v1/workers/versions/12341234-1234-1234-1234-123412341234/activity/",
        body=ErrorResponse(
            title="conflict",
            status_code=409,
            content="Either this activity does not exists or this state is not allowed.",
        ),
    )
    from arkindex_worker.worker import logger

    logger.info = mocker.MagicMock()

    mock_elements_worker_with_list.run()

    assert len(responses.calls) == len(BASE_API_CALLS) + 2
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        ("GET", "http://testserver/api/v1/element/1234-deadbeef/"),
        (
            "PUT",
            "http://testserver/api/v1/workers/versions/12341234-1234-1234-1234-123412341234/activity/",
        ),
    ]
    assert logger.info.call_args_list[:2] == [
        mocker.call("Processing page Test Page n°1 (1234-deadbeef) (1/1)"),
        mocker.call("Skipping element 1234-deadbeef as it was already processed"),
    ]


def test_start_activity_error(
    monkeypatch, responses, mocker, mock_elements_worker_with_list
):
    # Disable second configure call from run()
    monkeypatch.setattr(mock_elements_worker_with_list, "configure", lambda: None)

    # Mock a random error occurring during the activity update
    responses.add(
        responses.PUT,
        "http://testserver/api/v1/workers/versions/12341234-1234-1234-1234-123412341234/activity/",
        body=Exception("A wild Petilil appears !"),
    )
    from arkindex_worker.worker import logger

    logger.error = mocker.MagicMock()

    with pytest.raises(SystemExit):
        mock_elements_worker_with_list.run()

    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        ("GET", "http://testserver/api/v1/element/1234-deadbeef/"),
        (
            "PUT",
            "http://testserver/api/v1/workers/versions/12341234-1234-1234-1234-123412341234/activity/",
        ),
        # Activity is updated to the "error" state regardless of the Exception occurring during the call
        (
            "PUT",
            "http://testserver/api/v1/workers/versions/12341234-1234-1234-1234-123412341234/activity/",
        ),
    ]
    assert logger.error.call_args_list == [
        mocker.call("Ran on 1 elements: 0 completed, 1 failed")
    ]
