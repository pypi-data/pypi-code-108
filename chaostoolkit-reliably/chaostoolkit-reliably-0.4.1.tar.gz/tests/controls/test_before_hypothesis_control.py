from unittest.mock import MagicMock, patch

from chaosreliably.controls import experiment
from chaosreliably.types import EntityContextExperimentRunLabels, EventType


@patch("chaosreliably.controls.experiment._create_experiment_event")
def test_before_hypothesis_control_calls_create_experiment_event(
    mock_create_experiment_event: MagicMock,
) -> None:
    run_labels = EntityContextExperimentRunLabels(user="TestUser")
    title = "Check our test system is OK"
    configuration = {"chaosreliably": {"experiment_run_labels": run_labels.dict()}}

    experiment.before_hypothesis_control(
        context={"title": title, "probes": []},
        **{"configuration": configuration, "secrets": None}
    )

    mock_create_experiment_event.assert_called_once_with(
        event_type=EventType.HYPOTHESIS_START,
        name=title,
        output=None,
        experiment_run_labels=run_labels,
        configuration=configuration,
        secrets=None,
    )


@patch("chaosreliably.controls.experiment.logger")
def test_that_an_exception_does_not_get_raised_and_warning_logged(
    mock_logger: MagicMock,
) -> None:

    experiment.before_hypothesis_control(
        context={"title": "test-title", "probes": []},
        **{"configuration": {}, "secrets": None}
    )
    mock_logger.debug.assert_called_once_with(
        "An error occurred: 'chaosreliably', while running the Before Hypothesis "
        "control, the Experiment execution won't be affected."
    )
