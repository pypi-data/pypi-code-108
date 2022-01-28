from datetime import datetime
from tempfile import NamedTemporaryFile
from typing import cast
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
import pytest_httpx
import yaml
from freezegun import freeze_time
from httpx._exceptions import HTTPStatusError

from chaosreliably.controls import experiment
from chaosreliably.types import (
    EntityContext,
    EntityContextExperimentEventLabels,
    EntityContextExperimentLabels,
    EntityContextExperimentRunLabels,
    EntityContextExperimentVersionLabels,
    EntityContextMetadata,
    EventType,
)


def test_create_entity_context_on_reliably_correctly_calls_reliably_api(
    httpx_mock: pytest_httpx._httpx_mock.HTTPXMock,
) -> None:
    title = "A Test Experiment Title"
    request_url = (
        "https://reliably.com/api/entities/test-org/" "reliably.com/v1/entitycontext"
    )
    expected_entity = EntityContext(
        metadata=EntityContextMetadata(
            labels=EntityContextExperimentLabels(title=title),
        )
    )
    httpx_mock.add_response(
        method="POST",
        url=request_url,
        match_content=expected_entity.json(by_alias=True).encode("utf-8"),
    )
    with NamedTemporaryFile(mode="w") as f:
        yaml.safe_dump(
            {
                "auths": {"reliably.com": {"token": "12345", "username": "jane"}},
                "currentOrg": {"name": "test-org"},
            },
            f,
            indent=2,
            default_flow_style=False,
        )
        f.seek(0)

        entity_context = experiment._create_entity_context_on_reliably(
            entity_context=expected_entity,
            configuration={"reliably_config_path": f.name},
            secrets=None,
        )
        assert entity_context == expected_entity


def test_create_entity_context_on_reliably_raises_exception_if_response_not_ok(
    httpx_mock: pytest_httpx._httpx_mock.HTTPXMock,
) -> None:
    title = "A Test Experiment Title"
    request_url = (
        "https://reliably.com/api/entities/test-org/" "reliably.com/v1/entitycontext"
    )
    expected_entity = EntityContext(
        metadata=EntityContextMetadata(
            labels=EntityContextExperimentLabels(title=title),
        )
    )
    httpx_mock.add_response(
        method="POST",
        url=request_url,
        match_content=expected_entity.json(by_alias=True).encode("utf-8"),
        status_code=500,
    )
    with NamedTemporaryFile(mode="w") as f:
        yaml.safe_dump(
            {
                "auths": {"reliably.com": {"token": "12345", "username": "jane"}},
                "currentOrg": {"name": "test-org"},
            },
            f,
            indent=2,
            default_flow_style=False,
        )
        f.seek(0)

        with pytest.raises(HTTPStatusError):
            _ = experiment._create_entity_context_on_reliably(
                entity_context=expected_entity,
                configuration={"reliably_config_path": f.name},
                secrets=None,
            )


@patch("chaosreliably.controls.experiment._create_entity_context_on_reliably")
def test_create_experiment_correct_calls_create_entity_context_and_returns_labels(
    mock_create_entity_context: MagicMock,
) -> None:
    title = "A Test Experiment Title"
    experiment_context = EntityContext(
        metadata=EntityContextMetadata(
            labels=EntityContextExperimentLabels(title=title),
        )
    )
    mock_create_entity_context.return_value = experiment_context

    labels = experiment._create_experiment(
        experiment_title=title, configuration=None, secrets=None
    )

    assert labels == experiment_context.metadata.labels.dict(by_alias=True)
    mock_create_entity_context.assert_called_once_with(
        entity_context=experiment_context, configuration=None, secrets=None
    )


@patch("chaosreliably.controls.experiment._create_entity_context_on_reliably")
def test_create_experiment_with_related_to_labels_correct_calls_create_entity_context_and_returns_labels(  # Noqa
    mock_create_entity_context: MagicMock,
) -> None:
    title = "A Test Experiment Title"
    related_to_labels = [
        {"name": "SLO Name 1", "service": "My services name"},
        {"random_key": "A random value"},
    ]
    experiment_context = EntityContext(
        metadata=EntityContextMetadata(
            labels=EntityContextExperimentLabels(title=title),
            related_to=related_to_labels,
        )
    )
    mock_create_entity_context.return_value = experiment_context

    labels = experiment._create_experiment(
        experiment_title=title,
        related_to_labels=related_to_labels,
        configuration=None,
        secrets=None,
    )

    assert labels == experiment_context.metadata.labels.dict(by_alias=True)
    mock_create_entity_context.assert_called_once_with(
        entity_context=experiment_context, configuration=None, secrets=None
    )


@patch("chaosreliably.controls.experiment._create_entity_context_on_reliably")
def test_create_experiment_version_calls_create_entity_context_and_returns_labels(
    mock_create_entity_context: MagicMock,
) -> None:
    commit_hash = "59f9f577e2d90719098f4d23d26329ce41f2d0bd"
    source = "https://github.com/chaostoolkit-incubator/chaostoolkit-reliably/exp.json"
    experiment_context = EntityContext(
        metadata=EntityContextMetadata(
            labels=EntityContextExperimentLabels(title="A Test Experiment Title"),
        )
    )
    experiment_version_context = EntityContext(
        metadata=EntityContextMetadata(
            labels=EntityContextExperimentVersionLabels(
                commit_hash=commit_hash, source=source
            ),
            related_to=[experiment_context.metadata.labels],
        )
    )
    mock_create_entity_context.return_value = experiment_version_context

    labels = experiment._create_experiment_version(
        commit_hash=commit_hash,
        source=source,
        experiment_labels=cast(
            EntityContextExperimentLabels, experiment_context.metadata.labels
        ),
        configuration=None,
        secrets=None,
    )

    assert labels == experiment_version_context.metadata.labels.dict(by_alias=True)
    mock_create_entity_context.assert_called_once_with(
        entity_context=experiment_version_context, configuration=None, secrets=None
    )


@freeze_time(
    datetime.now()
)  # Needed so that we get the same objects back from our assertions  # Noqa
@patch("chaosreliably.types.uuid4")  # Ditto
@patch("chaosreliably.controls.experiment._create_entity_context_on_reliably")
def test_create_experiment_run_calls_create_entity_context_and_returns_labels(
    mock_create_entity_context: MagicMock, mock_uuid4: MagicMock
) -> None:
    user = "TestUser"
    experiment_version_context = EntityContext(
        metadata=EntityContextMetadata(
            labels=EntityContextExperimentVersionLabels(
                commit_hash="59f9f577e2d90719098f4d23d26329ce41f2d0bd",
                source="https://github.com/chaostoolkit-incubator/chaostoolkit-reliably/exp.json",  # noqa
            )
        )
    )
    mock_uuid4.return_value = uuid4()
    experiment_run_context = EntityContext(
        metadata=EntityContextMetadata(
            labels=EntityContextExperimentRunLabels(user=user),
            related_to=[experiment_version_context.metadata.labels],
        )
    )
    mock_create_entity_context.return_value = experiment_run_context

    labels = experiment._create_experiment_run(
        user=user,
        experiment_version_labels=cast(
            EntityContextExperimentVersionLabels,
            experiment_version_context.metadata.labels,
        ),
        configuration=None,
        secrets=None,
    )

    assert labels == experiment_run_context.metadata.labels.dict(by_alias=True)
    mock_create_entity_context.assert_called_once_with(
        entity_context=experiment_run_context, configuration=None, secrets=None
    )


@freeze_time(
    datetime.now()
)  # Needed so that we get the same objects back from our assertions  # Noqa
@patch("chaosreliably.controls.experiment._create_entity_context_on_reliably")
def test_create_experiment_event_calls_create_entity_context_and_returns_labels(
    mock_create_entity_context: MagicMock,
) -> None:
    event_type = EventType.EXPERIMENT_START
    event_name = "A Start Event"
    event_output = str([1, 2, 3])
    experiment_run_context = EntityContext(
        metadata=EntityContextMetadata(
            labels=EntityContextExperimentRunLabels(user="TestUser"),
        )
    )
    experiment_event_context = EntityContext(
        metadata=EntityContextMetadata(
            labels=EntityContextExperimentEventLabels(
                event_type=event_type.value, name=event_name, output=event_output
            ),
            related_to=[experiment_run_context.metadata.labels],
        )
    )
    mock_create_entity_context.return_value = experiment_event_context

    labels = experiment._create_experiment_event(
        event_type=event_type,
        name=event_name,
        output=event_output,
        experiment_run_labels=cast(
            EntityContextExperimentRunLabels, experiment_run_context.metadata.labels
        ),
        configuration=None,
        secrets=None,
    )

    assert labels == experiment_event_context.metadata.labels.dict(by_alias=True)
    mock_create_entity_context.assert_called_once_with(
        entity_context=experiment_event_context, configuration=None, secrets=None
    )
