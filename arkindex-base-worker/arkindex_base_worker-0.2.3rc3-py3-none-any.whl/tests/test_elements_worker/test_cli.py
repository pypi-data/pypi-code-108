# -*- coding: utf-8 -*-
import json
import os
import sys
import tempfile
from uuid import UUID

import pytest

from arkindex_worker.worker import ElementsWorker


def test_cli_default(monkeypatch, mock_config_api):
    _, path = tempfile.mkstemp()
    with open(path, "w") as f:
        json.dump(
            [
                {"id": "volumeid", "type": "volume"},
                {"id": "pageid", "type": "page"},
                {"id": "actid", "type": "act"},
                {"id": "surfaceid", "type": "surface"},
            ],
            f,
        )

    monkeypatch.setenv("TASK_ELEMENTS", path)
    monkeypatch.setattr(sys, "argv", ["worker"])
    worker = ElementsWorker()
    worker.configure()

    assert worker.args.elements_list.name == path
    assert not worker.args.element
    os.unlink(path)


def test_cli_arg_elements_list_given(mocker, mock_config_api):
    _, path = tempfile.mkstemp()
    with open(path, "w") as f:
        json.dump(
            [
                {"id": "volumeid", "type": "volume"},
                {"id": "pageid", "type": "page"},
                {"id": "actid", "type": "act"},
                {"id": "surfaceid", "type": "surface"},
            ],
            f,
        )

    mocker.patch.object(sys, "argv", ["worker", "--elements-list", path])
    worker = ElementsWorker()
    worker.configure()

    assert worker.args.elements_list.name == path
    assert not worker.args.element
    os.unlink(path)


def test_cli_arg_element_one_given_not_uuid(mocker):
    mocker.patch.object(sys, "argv", ["worker", "--element", "1234"])
    worker = ElementsWorker()
    with pytest.raises(SystemExit):
        worker.configure()


def test_cli_arg_element_one_given(mocker, mock_config_api):
    mocker.patch.object(
        sys, "argv", ["worker", "--element", "12341234-1234-1234-1234-123412341234"]
    )
    worker = ElementsWorker()
    worker.configure()

    assert worker.args.element == [UUID("12341234-1234-1234-1234-123412341234")]
    # elements_list is None because TASK_ELEMENTS environment variable isn't set
    assert not worker.args.elements_list


def test_cli_arg_element_many_given(mocker, mock_config_api):
    mocker.patch.object(
        sys,
        "argv",
        [
            "worker",
            "--element",
            "12341234-1234-1234-1234-123412341234",
            "43214321-4321-4321-4321-432143214321",
        ],
    )
    worker = ElementsWorker()
    worker.configure()

    assert worker.args.element == [
        UUID("12341234-1234-1234-1234-123412341234"),
        UUID("43214321-4321-4321-4321-432143214321"),
    ]
    # elements_list is None because TASK_ELEMENTS environment variable isn't set
    assert not worker.args.elements_list
