from unittest.mock import MagicMock, patch

from chaosreliably.controls import experiment
from chaosreliably.types import EntityContextExperimentRunLabels, EventType


@patch("chaosreliably.controls.experiment._create_experiment_event")
def test_after_experiment_control_calls_create_experiment_event(
    mock_create_experiment_event: MagicMock,
) -> None:
    run_labels = EntityContextExperimentRunLabels(user="TestUser")
    configuration = {"chaosreliably": {"experiment_run_labels": run_labels.dict()}}
    title = "A Test Experiment Title"
    journal = {
        "chaoslib-version": None,
        "platform": None,
        "node": None,
        "experiment": None,
        "start": None,
        "status": None,
        "deviated": None,
        "steady_states": None,
        "run": None,
        "rollbacks": None,
        "end": None,
        "duration": None,
    }

    experiment.after_experiment_control(
        context={"title": title, "description": "A test description", "method": []},
        **{"state": journal, "configuration": configuration, "secrets": None},
    )

    mock_create_experiment_event.assert_called_once_with(
        event_type=EventType.EXPERIMENT_END,
        name=f"Experiment: {title} - Ended",
        output=journal,
        experiment_run_labels=run_labels,
        configuration=configuration,
        secrets=None,
    )


@patch("chaosreliably.controls.experiment.logger")
def test_than_an_exception_does_not_get_raised_and_warning_logged(
    mock_logger: MagicMock,
) -> None:
    journal = {
        "chaoslib-version": None,
        "platform": None,
        "node": None,
        "experiment": None,
        "start": None,
        "status": None,
        "deviated": None,
        "steady_states": None,
        "run": None,
        "rollbacks": None,
        "end": None,
        "duration": None,
    }

    experiment.after_experiment_control(
        context={
            "title": "A Test Experiment Title",
            "description": "A test description",
            "method": [],
        },
        **{"state": journal, "configuration": {}, "secrets": None},
    )

    mock_logger.debug.assert_called_once_with(
        "An error occurred: 'chaosreliably', while running the After Experiment"
        " control, the Experiment execution won't be affected."
    )
