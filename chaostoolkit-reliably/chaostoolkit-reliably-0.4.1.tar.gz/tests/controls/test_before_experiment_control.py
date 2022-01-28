from typing import Any, Dict, cast
from unittest.mock import MagicMock, patch

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


@patch("chaosreliably.controls.experiment._create_experiment_event")
@patch("chaosreliably.controls.experiment._create_experiment_run")
@patch("chaosreliably.controls.experiment._create_experiment_version")
@patch("chaosreliably.controls.experiment._create_experiment")
def test_that_create_experiment_entities_for_before_experiment_control_creates_entities(
    mock_create_experiment: MagicMock,
    mock_create_experiment_version: MagicMock,
    mock_create_experiment_run: MagicMock,
    mock_create_experiment_event: MagicMock,
) -> None:
    title = "A title"
    commit_hash = "59f9f577e2d90719098f4d23d26329ce41f2d0bd"
    source = "https://github.com/chaostoolkit-incubator/chaostoolkit-reliably/exp.json"
    user = "TestUser"
    name = f"Experiment: {title} - Started"
    experiment_context = EntityContext(
        metadata=EntityContextMetadata(
            labels=EntityContextExperimentLabels(title=title),
        )
    )
    experiment_version_context = EntityContext(
        metadata=EntityContextMetadata(
            labels=EntityContextExperimentVersionLabels(
                commit_hash=commit_hash,
                source=source,
            ),
            related_to=[experiment_context.metadata.labels],
        )
    )
    experiment_run_context = EntityContext(
        metadata=EntityContextMetadata(
            labels=EntityContextExperimentRunLabels(user=user),
            related_to=[experiment_version_context.metadata.labels],
        )
    )
    experiment_event_context = EntityContext(
        metadata=EntityContextMetadata(
            labels=EntityContextExperimentEventLabels(
                event_type=EventType.EXPERIMENT_START.value,
                name=name,
                output=str(None),
            ),
            related_to=[experiment_run_context.metadata.labels],
        )
    )
    mock_create_experiment.return_value = experiment_context.metadata.labels
    mock_create_experiment_version.return_value = (
        experiment_version_context.metadata.labels
    )
    mock_create_experiment_run.return_value = experiment_run_context.metadata.labels
    mock_create_experiment_event.return_value = experiment_event_context.metadata.labels

    experiment_run_labels = (
        experiment._create_experiment_entities_for_before_experiment_control(
            experiment_title=title,
            commit_hash=commit_hash,
            source=source,
            user=user,
            configuration=None,
            secrets=None,
        )
    )

    assert experiment_run_labels == experiment_run_context.metadata.labels

    mock_create_experiment.assert_called_once_with(
        experiment_title=title, configuration=None, secrets=None, related_to_labels=[]
    )
    mock_create_experiment_version.assert_called_once_with(
        commit_hash=commit_hash,
        source=source,
        experiment_labels=experiment_context.metadata.labels,
        configuration=None,
        secrets=None,
    )
    mock_create_experiment_run.assert_called_once_with(
        user=user,
        experiment_version_labels=experiment_version_context.metadata.labels,
        configuration=None,
        secrets=None,
    )
    mock_create_experiment_event.assert_called_once_with(
        event_type=EventType.EXPERIMENT_START,
        name=name,
        output=None,
        experiment_run_labels=experiment_run_context.metadata.labels,
        configuration=None,
        secrets=None,
    )


@patch("chaosreliably.controls.experiment._create_experiment_event")
@patch("chaosreliably.controls.experiment._create_experiment_run")
@patch("chaosreliably.controls.experiment._create_experiment_version")
@patch("chaosreliably.controls.experiment._create_experiment")
def test_that_create_experiment_entities_for_before_experiment_control_creates_entities_when_experiment_has_relations(  # Noqa
    mock_create_experiment: MagicMock,
    mock_create_experiment_version: MagicMock,
    mock_create_experiment_run: MagicMock,
    mock_create_experiment_event: MagicMock,
) -> None:
    title = "A title"
    commit_hash = "59f9f577e2d90719098f4d23d26329ce41f2d0bd"
    source = "https://github.com/chaostoolkit-incubator/chaostoolkit-reliably/exp.json"
    user = "TestUser"
    name = f"Experiment: {title} - Started"
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
    experiment_version_context = EntityContext(
        metadata=EntityContextMetadata(
            labels=EntityContextExperimentVersionLabels(
                commit_hash=commit_hash,
                source=source,
            ),
            related_to=[experiment_context.metadata.labels],
        )
    )
    experiment_run_context = EntityContext(
        metadata=EntityContextMetadata(
            labels=EntityContextExperimentRunLabels(user=user),
            related_to=[experiment_version_context.metadata.labels],
        )
    )
    experiment_event_context = EntityContext(
        metadata=EntityContextMetadata(
            labels=EntityContextExperimentEventLabels(
                event_type=EventType.EXPERIMENT_START.value,
                name=name,
                output=str(None),
            ),
            related_to=[experiment_run_context.metadata.labels],
        )
    )
    mock_create_experiment.return_value = experiment_context.metadata.labels
    mock_create_experiment_version.return_value = (
        experiment_version_context.metadata.labels
    )
    mock_create_experiment_run.return_value = experiment_run_context.metadata.labels
    mock_create_experiment_event.return_value = experiment_event_context.metadata.labels

    experiment_run_labels = (
        experiment._create_experiment_entities_for_before_experiment_control(
            experiment_title=title,
            commit_hash=commit_hash,
            source=source,
            user=user,
            configuration=None,
            secrets=None,
            experiment_related_to_labels=related_to_labels,
        )
    )

    assert experiment_run_labels == experiment_run_context.metadata.labels

    mock_create_experiment.assert_called_once_with(
        experiment_title=title,
        configuration=None,
        secrets=None,
        related_to_labels=related_to_labels,
    )
    mock_create_experiment_version.assert_called_once_with(
        commit_hash=commit_hash,
        source=source,
        experiment_labels=experiment_context.metadata.labels,
        configuration=None,
        secrets=None,
    )
    mock_create_experiment_run.assert_called_once_with(
        user=user,
        experiment_version_labels=experiment_version_context.metadata.labels,
        configuration=None,
        secrets=None,
    )
    mock_create_experiment_event.assert_called_once_with(
        event_type=EventType.EXPERIMENT_START,
        name=name,
        output=None,
        experiment_run_labels=experiment_run_context.metadata.labels,
        configuration=None,
        secrets=None,
    )


@patch(
    "chaosreliably.controls.experiment._create_experiment_entities_for_before_experiment_control"  # Noqa
)
def test_before_experiment_control_calls_create_experiment_entities(
    mock_create_experiment_entities: MagicMock,
) -> None:
    configuration = {"random_config": {"hi": "hello"}, "thing": 123}
    title = "A title"
    commit_hash = "59f9f577e2d90719098f4d23d26329ce41f2d0bd"
    source = "https://github.com/chaostoolkit-incubator/chaostoolkit-reliably/exp.json"
    user = "TestUser"
    experiment_run_context = EntityContext(
        metadata=EntityContextMetadata(
            labels=EntityContextExperimentRunLabels(user=user)
        )
    )
    mock_create_experiment_entities.return_value = (
        experiment_run_context.metadata.labels
    )

    experiment.before_experiment_control(
        context={"title": title},
        **{
            "configuration": configuration,
            "secrets": None,
            "commit_hash": commit_hash,
            "source": source,
            "user": user,
        },
    )

    mock_create_experiment_entities.assert_called_once_with(
        experiment_title=title,
        commit_hash=commit_hash,
        source=source,
        user=user,
        configuration=configuration,
        secrets=None,
        experiment_related_to_labels=[],
    )

    assert "chaosreliably" in configuration
    chaosreliably = cast(Dict[str, Any], configuration["chaosreliably"])
    assert (
        chaosreliably["experiment_run_labels"] == experiment_run_context.metadata.labels
    )


@patch(
    "chaosreliably.controls.experiment._create_experiment_entities_for_before_experiment_control"  # Noqa
)
def test_before_experiment_control_calls_create_experiment_entities_when_experiment_has_relations(  # Noqa
    mock_create_experiment_entities: MagicMock,
) -> None:
    configuration = {"random_config": {"hi": "hello"}, "thing": 123}
    title = "A title"
    commit_hash = "59f9f577e2d90719098f4d23d26329ce41f2d0bd"
    source = "https://github.com/chaostoolkit-incubator/chaostoolkit-reliably/exp.json"
    user = "TestUser"
    related_to_labels = [
        {"name": "SLO Name 1", "service": "My services name"},
        {"random_key": "A random value"},
    ]
    experiment_run_context = EntityContext(
        metadata=EntityContextMetadata(
            labels=EntityContextExperimentRunLabels(user=user),
            related_to=related_to_labels,
        )
    )
    mock_create_experiment_entities.return_value = (
        experiment_run_context.metadata.labels
    )

    experiment.before_experiment_control(
        context={"title": title},
        **{
            "configuration": configuration,
            "secrets": None,
            "commit_hash": commit_hash,
            "source": source,
            "user": user,
            "experiment_related_to_labels": related_to_labels,
        },
    )

    mock_create_experiment_entities.assert_called_once_with(
        experiment_title=title,
        commit_hash=commit_hash,
        source=source,
        user=user,
        configuration=configuration,
        secrets=None,
        experiment_related_to_labels=related_to_labels,
    )

    assert "chaosreliably" in configuration
    chaosreliably = cast(Dict[str, Any], configuration["chaosreliably"])
    assert (
        chaosreliably["experiment_run_labels"] == experiment_run_context.metadata.labels
    )


@patch("chaosreliably.controls.experiment.logger")
@patch(
    "chaosreliably.controls.experiment._create_experiment_entities_for_before_experiment_control"  # Noqa
)
def test_that_before_experiment_control_does_nothing_if_kwargs_not_present(
    mock_create_experiment_entities: MagicMock,
    mock_logger: MagicMock,
) -> None:
    experiment.before_experiment_control(
        context={"title": "a-title"}, **{"configuration": None, "secrets": None}
    )
    mock_logger.debug.assert_called_once_with(
        "The parameters: `commit_hash`, `source`, and `user` are required for the "
        "chaosreliably controls, please provide them. This Experiment Run will not "
        "be tracked with Reliably."
    )
    mock_create_experiment_entities.assert_not_called()


@patch("chaosreliably.controls.experiment.logger")
@patch(
    "chaosreliably.controls.experiment._create_experiment_entities_for_before_experiment_control"  # Noqa
)
def test_that_an_exception_does_not_get_raised_and_warning_logged(
    mock_create_experiment_entities: MagicMock, mock_logger: MagicMock
) -> None:
    mock_create_experiment_entities.side_effect = Exception("An exception happened")
    experiment.before_experiment_control(
        context={"title": "a-title"},
        **{
            "configuration": None,
            "secrets": None,
            "commit_hash": "blah",
            "source": "blah",
            "user": "blah",
        },
    )
    mock_logger.debug.assert_called_once_with(
        "An error occurred: An exception happened, whilst running the Before Experiment"
        " control, no further entities will be created, the Experiment execution won't"
        " be affected"
    )
