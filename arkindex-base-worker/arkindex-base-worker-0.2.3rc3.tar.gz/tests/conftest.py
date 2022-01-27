# -*- coding: utf-8 -*-
import hashlib
import json
import os
import sys
import time
from pathlib import Path
from uuid import UUID

import pytest
import yaml
from peewee import SqliteDatabase

from arkindex.mock import MockApiClient
from arkindex_worker.cache import MODELS, CachedElement, CachedTranscription
from arkindex_worker.git import GitHelper, GitlabHelper
from arkindex_worker.worker import BaseWorker, ElementsWorker
from arkindex_worker.worker.transcription import TextOrientation

FIXTURES_DIR = Path(__file__).resolve().parent / "data"

__yaml_cache = {}


@pytest.fixture(autouse=True)
def disable_sleep(monkeypatch):
    """
    Do not sleep at all in between API executions
    when errors occur in unit tests.
    This speeds up the test execution a lot
    """
    monkeypatch.setattr(time, "sleep", lambda x: None)


@pytest.fixture
def cache_yaml(monkeypatch):
    """
    Cache all calls to yaml.safe_load in order to speedup
    every test cases that load the OpenAPI schema
    """
    # Keep a reference towards the original function
    _original_yaml_load = yaml.safe_load

    def _cached_yaml_load(yaml_payload):
        # Create a unique cache key for direct YAML strings
        # and file descriptors
        if isinstance(yaml_payload, str):
            yaml_payload = yaml_payload.encode("utf-8")
        if isinstance(yaml_payload, bytes):
            key = hashlib.md5(yaml_payload).hexdigest()
        else:
            key = yaml_payload.name

        # Cache result
        if key not in __yaml_cache:
            __yaml_cache[key] = _original_yaml_load(yaml_payload)

        return __yaml_cache[key]

    monkeypatch.setattr(yaml, "safe_load", _cached_yaml_load)


@pytest.fixture(autouse=True)
def setup_api(responses, monkeypatch, cache_yaml):

    # Always use the environment variable first
    schema_url = os.environ.get("ARKINDEX_API_SCHEMA_URL")
    if schema_url is None:
        # Try to load a local schema as the current developer of base-worker
        # may also work on the backend nearby
        paths = [
            "~/dev/ark/backend/schema.yml",
            "~/dev/ark/backend/output/schema.yml",
        ]
        for path in paths:
            path = Path(path).expanduser().absolute()
            if path.exists():
                monkeypatch.setenv("ARKINDEX_API_SCHEMA_URL", str(path))
                schema_url = str(path)
                break

    # Fallback to prod environment
    if schema_url is None:
        schema_url = "https://arkindex.teklia.com/api/v1/openapi/?format=openapi-json"
        monkeypatch.setenv("ARKINDEX_API_SCHEMA_URL", schema_url)

    # Allow accessing remote API schemas
    responses.add_passthru(schema_url)

    # Force api requests on a dummy server with dummy credentials
    monkeypatch.setenv("ARKINDEX_API_URL", "http://testserver/api/v1")
    monkeypatch.setenv("ARKINDEX_API_TOKEN", "unittest1234")


@pytest.fixture(autouse=True)
def give_env_variable(monkeypatch):
    """Defines required environment variables"""
    monkeypatch.setenv("WORKER_VERSION_ID", "12341234-1234-1234-1234-123412341234")
    monkeypatch.setenv("ARKINDEX_PROCESS_ID", "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeffff")
    monkeypatch.setenv("ARKINDEX_CORPUS_ID", "11111111-1111-1111-1111-111111111111")


@pytest.fixture
def mock_config_api(mock_worker_version_api, mock_process_api, mock_user_api):
    """Mock all API endpoints required to configure a worker"""
    pass


@pytest.fixture
def mock_worker_version_api(responses):
    """Provide a mock API response to get worker configuration"""
    payload = {
        "id": "12341234-1234-1234-1234-123412341234",
        "configuration": {
            "docker": {"image": "python:3"},
            "configuration": {"someKey": "someValue"},
            "secrets": [],
        },
        "revision": {
            "hash": "deadbeef1234",
            "name": "some git revision",
        },
        "docker_image": "python:3",
        "docker_image_name": "python:3",
        "state": "created",
        "worker": {
            "id": "deadbeef-1234-5678-1234-worker",
            "name": "Fake worker",
            "slug": "fake_worker",
            "type": "classifier",
        },
    }
    responses.add(
        responses.GET,
        "http://testserver/api/v1/workers/versions/12341234-1234-1234-1234-123412341234/",
        status=200,
        body=json.dumps(payload),
        content_type="application/json",
    )


@pytest.fixture
def mock_process_api(responses):
    """Provide a mock of the API response to get information on a process. Workers activity is enabled"""
    payload = {
        "name": None,
        "id": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeffff",
        "state": "running",
        "mode": "workers",
        "corpus": "11111111-1111-1111-1111-111111111111",
        "workflow": "http://testserver/ponos/v1/workflow/12341234-1234-1234-1234-123412341234/",
        "files": [],
        "revision": None,
        "element": {
            "id": "12341234-1234-1234-1234-123412341234",
            "type": "folder",
            "name": "Test folder",
            "corpus": {
                "id": "11111111-1111-1111-1111-111111111111",
                "name": "John Doe project",
                "public": False,
            },
            "thumbnail_url": "http://testserver/thumbnail.png",
            "zone": None,
            "thumbnail_put_url": "http://testserver/thumbnail.png",
        },
        "folder_type": None,
        "element_type": "page",
        "element_name_contains": None,
        "load_children": True,
        "use_cache": False,
        "activity_state": "ready",
    }
    responses.add(
        responses.GET,
        "http://testserver/api/v1/imports/aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeffff/",
        status=200,
        body=json.dumps(payload),
        content_type="application/json",
    )


@pytest.fixture
def mock_user_api(responses):
    """
    Provide a mock API response to retrieve user details
    Signup is disabled in this mock
    """
    payload = {
        "id": 1,
        "email": "bot@teklia.com",
        "display_name": "Bender",
        "features": {
            "signup": False,
        },
    }
    responses.add(
        responses.GET,
        "http://testserver/api/v1/user/",
        status=200,
        body=json.dumps(payload),
        content_type="application/json",
    )


@pytest.fixture
def mock_activity_calls(responses):
    """
    Mock responses when updating the activity state for multiple element of the same version
    """
    responses.add(
        responses.PUT,
        "http://testserver/api/v1/workers/versions/12341234-1234-1234-1234-123412341234/activity/",
        status=200,
    )


@pytest.fixture
def mock_elements_worker(monkeypatch, mock_config_api):
    """Build and configure an ElementsWorker with fixed CLI parameters to avoid issues with pytest"""
    monkeypatch.setattr(sys, "argv", ["worker"])

    worker = ElementsWorker()
    worker.configure()
    return worker


@pytest.fixture
def mock_elements_worker_with_list(monkeypatch, responses, mock_elements_worker):
    """
    Mock a worker instance to list and retrieve a single element
    """
    monkeypatch.setattr(
        mock_elements_worker, "list_elements", lambda: ["1234-deadbeef"]
    )
    responses.add(
        responses.GET,
        "http://testserver/api/v1/element/1234-deadbeef/",
        status=200,
        json={
            "id": "1234-deadbeef",
            "type": "page",
            "name": "Test Page n°1",
        },
    )
    return mock_elements_worker


@pytest.fixture
def mock_base_worker_with_cache(mocker, monkeypatch, mock_config_api):
    """Build a BaseWorker using SQLite cache, also mocking a PONOS_TASK"""
    monkeypatch.setattr(sys, "argv", ["worker"])

    worker = BaseWorker(support_cache=True)
    monkeypatch.setenv("PONOS_TASK", "my_task")
    return worker


@pytest.fixture
def mock_elements_worker_with_cache(monkeypatch, mock_config_api, tmp_path):
    """Build and configure an ElementsWorker using SQLite cache with fixed CLI parameters to avoid issues with pytest"""
    cache_path = tmp_path / "db.sqlite"
    cache_path.touch()
    monkeypatch.setattr(sys, "argv", ["worker", "-d", str(cache_path)])

    worker = ElementsWorker(support_cache=True)
    worker.configure()
    return worker


@pytest.fixture
def fake_page_element():
    with open(FIXTURES_DIR / "page_element.json", "r") as f:
        return json.load(f)


@pytest.fixture
def fake_ufcn_worker_version():
    with open(FIXTURES_DIR / "ufcn_line_historical_worker_version.json", "r") as f:
        return json.load(f)


@pytest.fixture
def fake_transcriptions_small():
    with open(FIXTURES_DIR / "line_transcriptions_small.json", "r") as f:
        return json.load(f)


@pytest.fixture
def fake_dummy_worker():
    api_client = MockApiClient()
    worker = ElementsWorker()
    worker.api_client = api_client
    return worker


@pytest.fixture
def fake_git_helper(mocker):
    gitlab_helper = mocker.MagicMock()
    return GitHelper(
        "repo_url",
        "/tmp/git_test/foo/",
        "/tmp/test/path/",
        "tmp_workflow_id",
        gitlab_helper,
    )


@pytest.fixture
def fake_gitlab_helper_factory():
    # have to set up the responses, before creating the client
    def run():
        return GitlabHelper(
            "balsac_exporter/balsac-exported-xmls-testing",
            "https://gitlab.com",
            "<GITLAB_TOKEN>",
            "gitlab_branch",
        )

    return run


@pytest.fixture
def mock_cached_elements():
    """Insert few elements in local cache"""
    CachedElement.create(
        id=UUID("11111111-1111-1111-1111-111111111111"),
        parent_id="12341234-1234-1234-1234-123412341234",
        type="something",
        polygon="[[1, 1], [2, 2], [2, 1], [1, 2]]",
        worker_version_id=UUID("56785678-5678-5678-5678-567856785678"),
    )
    CachedElement.create(
        id=UUID("22222222-2222-2222-2222-222222222222"),
        parent_id=UUID("12341234-1234-1234-1234-123412341234"),
        type="page",
        polygon="[[1, 1], [2, 2], [2, 1], [1, 2]]",
        worker_version_id=UUID("56785678-5678-5678-5678-567856785678"),
    )
    assert CachedElement.select().count() == 2


@pytest.fixture
def mock_cached_transcriptions():
    """Insert few transcriptions in local cache, on a shared element"""
    CachedElement.create(
        id=UUID("11111111-1111-1111-1111-111111111111"),
        type="page",
        polygon="[[1, 1], [2, 2], [2, 1], [1, 2]]",
        worker_version_id=UUID("56785678-5678-5678-5678-567856785678"),
    )
    CachedElement.create(
        id=UUID("22222222-2222-2222-2222-222222222222"),
        type="something_else",
        parent_id=UUID("11111111-1111-1111-1111-111111111111"),
        polygon="[[1, 1], [2, 2], [2, 1], [1, 2]]",
        worker_version_id=UUID("56785678-5678-5678-5678-567856785678"),
    )
    CachedElement.create(
        id=UUID("33333333-3333-3333-3333-333333333333"),
        type="page",
        parent_id=UUID("11111111-1111-1111-1111-111111111111"),
        polygon="[[1, 1], [2, 2], [2, 1], [1, 2]]",
        worker_version_id=UUID("56785678-5678-5678-5678-567856785678"),
    )
    CachedElement.create(
        id=UUID("44444444-4444-4444-4444-444444444444"),
        type="something_else",
        parent_id=UUID("22222222-2222-2222-2222-222222222222"),
        polygon="[[1, 1], [2, 2], [2, 1], [1, 2]]",
        worker_version_id=UUID("56785678-5678-5678-5678-567856785678"),
    )
    CachedElement.create(
        id=UUID("55555555-5555-5555-5555-555555555555"),
        type="something_else",
        parent_id=UUID("44444444-4444-4444-4444-444444444444"),
        polygon="[[1, 1], [2, 2], [2, 1], [1, 2]]",
        worker_version_id=UUID("56785678-5678-5678-5678-567856785678"),
    )
    CachedTranscription.create(
        id=UUID("11111111-1111-1111-1111-111111111111"),
        element_id=UUID("11111111-1111-1111-1111-111111111111"),
        text="This",
        confidence=0.42,
        orientation=TextOrientation.HorizontalLeftToRight,
        worker_version_id=UUID("56785678-5678-5678-5678-567856785678"),
    )
    CachedTranscription.create(
        id=UUID("22222222-2222-2222-2222-222222222222"),
        element_id=UUID("22222222-2222-2222-2222-222222222222"),
        text="is",
        confidence=0.42,
        orientation=TextOrientation.HorizontalLeftToRight,
        worker_version_id=UUID("90129012-9012-9012-9012-901290129012"),
    )
    CachedTranscription.create(
        id=UUID("33333333-3333-3333-3333-333333333333"),
        element_id=UUID("33333333-3333-3333-3333-333333333333"),
        text="a",
        confidence=0.42,
        orientation=TextOrientation.HorizontalLeftToRight,
        worker_version_id=UUID("90129012-9012-9012-9012-901290129012"),
    )
    CachedTranscription.create(
        id=UUID("44444444-4444-4444-4444-444444444444"),
        element_id=UUID("44444444-4444-4444-4444-444444444444"),
        text="good",
        confidence=0.42,
        orientation=TextOrientation.HorizontalLeftToRight,
        worker_version_id=UUID("90129012-9012-9012-9012-901290129012"),
    )
    CachedTranscription.create(
        id=UUID("55555555-5555-5555-5555-555555555555"),
        element_id=UUID("55555555-5555-5555-5555-555555555555"),
        text="test",
        confidence=0.42,
        orientation=TextOrientation.HorizontalLeftToRight,
        worker_version_id=UUID("90129012-9012-9012-9012-901290129012"),
    )


@pytest.fixture(scope="function")
def mock_databases(tmpdir):
    """
    Initialize several temporary databases
    to help testing the merge algorithm
    """
    out = {}
    for name in ("target", "first", "second", "conflict", "chunk_42"):
        # Build a local database in sub directory
        # for each name required
        filename = "db_42.sqlite" if name == "chunk_42" else "db.sqlite"
        path = tmpdir / name / filename
        (tmpdir / name).mkdir()
        local_db = SqliteDatabase(path)
        with local_db.bind_ctx(MODELS):
            # Create tables on the current local database
            # by binding temporarily the models on that database
            local_db.create_tables(MODELS)
        out[name] = {"path": path, "db": local_db}

    # Add an element in first parent database
    with out["first"]["db"].bind_ctx(MODELS):
        CachedElement.create(
            id=UUID("12341234-1234-1234-1234-123412341234"),
            type="page",
            polygon="[[1, 1], [2, 2], [2, 1], [1, 2]]",
            worker_version_id=UUID("56785678-5678-5678-5678-567856785678"),
        )
        CachedElement.create(
            id=UUID("56785678-5678-5678-5678-567856785678"),
            type="page",
            polygon="[[1, 1], [2, 2], [2, 1], [1, 2]]",
            worker_version_id=UUID("56785678-5678-5678-5678-567856785678"),
        )

    # Add another element with a transcription in second parent database
    with out["second"]["db"].bind_ctx(MODELS):
        CachedElement.create(
            id=UUID("42424242-4242-4242-4242-424242424242"),
            type="page",
            polygon="[[1, 1], [2, 2], [2, 1], [1, 2]]",
            worker_version_id=UUID("56785678-5678-5678-5678-567856785678"),
        )
        CachedTranscription.create(
            id=UUID("11111111-1111-1111-1111-111111111111"),
            element_id=UUID("42424242-4242-4242-4242-424242424242"),
            text="Hello!",
            confidence=0.42,
            orientation=TextOrientation.HorizontalLeftToRight,
            worker_version_id=UUID("56785678-5678-5678-5678-567856785678"),
        )

    # Add a conflicting element
    with out["conflict"]["db"].bind_ctx(MODELS):
        CachedElement.create(
            id=UUID("42424242-4242-4242-4242-424242424242"),
            type="page",
            polygon="[[1, 1], [2, 2], [2, 1], [1, 2]]",
            initial=True,
        )
        CachedTranscription.create(
            id=UUID("22222222-2222-2222-2222-222222222222"),
            element_id=UUID("42424242-4242-4242-4242-424242424242"),
            text="Hello again neighbor !",
            confidence=0.42,
            orientation=TextOrientation.HorizontalLeftToRight,
            worker_version_id=UUID("56785678-5678-5678-5678-567856785678"),
        )

    # Add an element in chunk parent database
    with out["chunk_42"]["db"].bind_ctx(MODELS):
        CachedElement.create(
            id=UUID("42424242-4242-4242-4242-424242424242"),
            type="page",
            polygon="[[1, 1], [2, 2], [2, 1], [1, 2]]",
            initial=True,
        )

    return out
