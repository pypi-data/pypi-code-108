# -*- coding: utf-8 -*-
import logging
import os
import sys
from pathlib import Path

import gnupg
import pytest

from arkindex.mock import MockApiClient
from arkindex_worker import logger
from arkindex_worker.worker import BaseWorker


def test_init_default_local_share(monkeypatch):
    worker = BaseWorker()

    assert worker.work_dir == os.path.expanduser("~/.local/share/arkindex")
    assert worker.worker_version_id == "12341234-1234-1234-1234-123412341234"


def test_init_default_xdg_data_home(monkeypatch):
    path = str(Path(__file__).absolute().parent)
    monkeypatch.setenv("XDG_DATA_HOME", path)
    worker = BaseWorker()

    assert worker.work_dir == f"{path}/arkindex"
    assert worker.worker_version_id == "12341234-1234-1234-1234-123412341234"


def test_init_with_local_cache(monkeypatch):
    worker = BaseWorker(support_cache=True)

    assert worker.work_dir == os.path.expanduser("~/.local/share/arkindex")
    assert worker.worker_version_id == "12341234-1234-1234-1234-123412341234"
    assert worker.support_cache is True


def test_init_var_ponos_data_given(monkeypatch):
    path = str(Path(__file__).absolute().parent)
    monkeypatch.setenv("PONOS_DATA", path)
    worker = BaseWorker()

    assert worker.work_dir == f"{path}/current"
    assert worker.worker_version_id == "12341234-1234-1234-1234-123412341234"


def test_init_var_worker_version_id_missing(
    monkeypatch, mock_user_api, mock_process_api
):
    monkeypatch.setattr(sys, "argv", ["worker"])
    monkeypatch.delenv("WORKER_VERSION_ID")
    worker = BaseWorker()
    worker.configure()
    assert worker.worker_version_id is None
    assert worker.is_read_only is True
    assert worker.config == {}  # default empty case


def test_init_var_worker_local_file(
    monkeypatch, tmp_path, mock_user_api, mock_process_api
):
    # Build a dummy yaml config file
    config = tmp_path / "config.yml"
    config.write_text("---\nlocalKey: abcdef123")

    monkeypatch.setattr(sys, "argv", ["worker", "-c", str(config)])
    monkeypatch.delenv("WORKER_VERSION_ID")
    worker = BaseWorker()
    worker.configure()
    assert worker.worker_version_id is None
    assert worker.is_read_only is True
    assert worker.config == {"localKey": "abcdef123"}  # Use a local file for devs

    config.unlink()


def test_cli_default(mocker, mock_config_api):
    worker = BaseWorker()
    spy = mocker.spy(worker, "add_arguments")
    assert not spy.called
    assert logger.level == logging.NOTSET
    assert not hasattr(worker, "api_client")

    mocker.patch.object(sys, "argv", ["worker"])
    worker.configure()

    assert spy.called
    assert spy.call_count == 1
    assert not worker.args.verbose
    assert logger.level == logging.NOTSET
    assert worker.api_client
    assert worker.worker_version_id == "12341234-1234-1234-1234-123412341234"
    assert worker.is_read_only is False
    assert worker.config == {"someKey": "someValue"}  # from API

    logger.setLevel(logging.NOTSET)


def test_cli_arg_verbose_given(mocker, mock_config_api):
    worker = BaseWorker()
    spy = mocker.spy(worker, "add_arguments")
    assert not spy.called
    assert logger.level == logging.NOTSET
    assert not hasattr(worker, "api_client")

    mocker.patch.object(sys, "argv", ["worker", "-v"])
    worker.configure()

    assert spy.called
    assert spy.call_count == 1
    assert worker.args.verbose
    assert logger.level == logging.DEBUG
    assert worker.api_client
    assert worker.worker_version_id == "12341234-1234-1234-1234-123412341234"
    assert worker.is_read_only is False
    assert worker.config == {"someKey": "someValue"}  # from API

    logger.setLevel(logging.NOTSET)


def test_configure_dev_mode(
    mocker, monkeypatch, mock_user_api, mock_worker_version_api
):
    """
    Configuring a worker in developer mode avoid retrieving process information
    """
    worker = BaseWorker()
    mocker.patch.object(sys, "argv", ["worker", "--dev"])
    monkeypatch.setenv(
        "ARKINDEX_WORKER_RUN_ID", "aaaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
    )
    worker.configure()

    assert worker.args.dev is True
    assert worker.process_information is None
    assert worker.worker_version_id == "12341234-1234-1234-1234-123412341234"
    assert worker.is_read_only is True
    assert worker.user_configuration == {}


def test_configure_worker_run(mocker, monkeypatch, responses, mock_config_api):
    worker = BaseWorker()
    mocker.patch.object(sys, "argv", ["worker"])
    run_id = "aaaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
    configuration_id = "bbbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"
    monkeypatch.setenv("ARKINDEX_WORKER_RUN_ID", run_id)
    responses.add(
        responses.GET,
        f"http://testserver/api/v1/imports/workers/{run_id}/",
        json={"id": run_id, "configuration_id": configuration_id},
    )
    responses.add(
        responses.GET,
        f"http://testserver/api/v1/workers/configurations/{configuration_id}/",
        json={"id": configuration_id, "name": "BBB", "configuration": {"a": "b"}},
    )
    worker.configure()

    assert worker.user_configuration == {"a": "b"}


def test_configure_worker_run_missing_worker_conf(
    mocker, monkeypatch, responses, mock_config_api
):
    worker = BaseWorker()
    mocker.patch.object(sys, "argv", ["worker"])
    run_id = "aaaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
    monkeypatch.setenv("ARKINDEX_WORKER_RUN_ID", run_id)
    responses.add(
        responses.GET,
        f"http://testserver/api/v1/imports/workers/{run_id}/",
        json={"id": run_id},
    )
    worker.configure()

    assert worker.user_configuration == {}


def test_configure_worker_run_missing_conf(
    mocker, monkeypatch, responses, mock_config_api
):
    worker = BaseWorker()
    mocker.patch.object(sys, "argv", ["worker"])
    run_id = "aaaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
    configuration_id = "bbbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"
    monkeypatch.setenv("ARKINDEX_WORKER_RUN_ID", run_id)
    responses.add(
        responses.GET,
        f"http://testserver/api/v1/imports/workers/{run_id}/",
        json={"id": run_id, "configuration_id": configuration_id},
    )
    responses.add(
        responses.GET,
        f"http://testserver/api/v1/workers/configurations/{configuration_id}/",
        json={"id": configuration_id, "name": "BBB"},
    )
    worker.configure()

    assert worker.user_configuration is None


def test_load_missing_secret():
    worker = BaseWorker()
    worker.api_client = MockApiClient()

    with pytest.raises(
        Exception, match="Secret missing/secret is not available on the API nor locally"
    ):
        worker.load_secret("missing/secret")


def test_load_remote_secret():
    worker = BaseWorker()
    worker.api_client = MockApiClient()
    worker.api_client.add_response(
        "RetrieveSecret",
        name="testRemote",
        response={"content": "this is a secret value !"},
    )

    assert worker.load_secret("testRemote") == "this is a secret value !"

    # The one mocked call has been used
    assert len(worker.api_client.history) == 1
    assert len(worker.api_client.responses) == 0


def test_load_json_secret():
    worker = BaseWorker()
    worker.api_client = MockApiClient()
    worker.api_client.add_response(
        "RetrieveSecret",
        name="path/to/file.json",
        response={"content": '{"key": "value", "number": 42}'},
    )

    assert worker.load_secret("path/to/file.json") == {
        "key": "value",
        "number": 42,
    }

    # The one mocked call has been used
    assert len(worker.api_client.history) == 1
    assert len(worker.api_client.responses) == 0


def test_load_yaml_secret():
    worker = BaseWorker()
    worker.api_client = MockApiClient()
    worker.api_client.add_response(
        "RetrieveSecret",
        name="path/to/file.yaml",
        response={
            "content": """---
somekey: value
aList:
  - A
  - B
  - C
struct:
 level:
   X
"""
        },
    )

    assert worker.load_secret("path/to/file.yaml") == {
        "aList": ["A", "B", "C"],
        "somekey": "value",
        "struct": {"level": "X"},
    }

    # The one mocked call has been used
    assert len(worker.api_client.history) == 1
    assert len(worker.api_client.responses) == 0


def test_load_local_secret(monkeypatch, tmpdir):
    # Setup arkindex config dir in a temp directory
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmpdir))

    # Write a dummy secret
    secrets_dir = tmpdir / "arkindex" / "secrets"
    os.makedirs(secrets_dir)
    secret = secrets_dir / "testLocal"
    secret.write_text("this is a local secret value", encoding="utf-8")

    # Mock GPG decryption
    class GpgDecrypt(object):
        def __init__(self, fd):
            self.ok = True
            self.data = fd.read()

    monkeypatch.setattr(gnupg.GPG, "decrypt_file", lambda gpg, f: GpgDecrypt(f))

    worker = BaseWorker()
    worker.api_client = MockApiClient()

    assert worker.load_secret("testLocal") == "this is a local secret value"

    # The remote api is checked first
    assert len(worker.api_client.history) == 1
    assert worker.api_client.history[0].operation == "RetrieveSecret"
