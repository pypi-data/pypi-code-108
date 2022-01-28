from typing import Any, Dict, cast
from unittest.mock import MagicMock, patch

from chaosreliably.controls import experiment
from chaosreliably.types import EntityContextExperimentRunLabels, EventType


@patch("chaosreliably.controls.experiment._create_experiment_event")
def test_after_hypothesis_control_calls_create_experiment_event(
    mock_create_experiment_event: MagicMock,
) -> None:
    run_labels = EntityContextExperimentRunLabels(user="TestUser")
    title = "Check our test system is OK"
    probe = {
        "type": "probe",
        "name": "test-probe",
        "tolerance": True,
        "provider": {
            "type": "python",
            "module": "test.module",
            "func": "test_func",
        },
    }
    state = {
        "steady_state_met": False,
        "probes": [
            {
                "activity": probe,
                "output": False,
                "status": "succeeded",
                "start": "2021-08-17T08:34:46.884325",
                "end": "2021-08-17T08:34:46.891386",
                "duration": 0.007061,
                "tolerance_met": False,
            }
        ],
    }
    configuration = {"chaosreliably": {"experiment_run_labels": run_labels.dict()}}

    experiment.after_hypothesis_control(
        context={"title": title, "probes": [probe]},
        **cast(
            Dict[str, Any],
            {
                "state": state,
                "configuration": configuration,
                "secrets": None,
            },
        )
    )

    mock_create_experiment_event.assert_called_once_with(
        event_type=EventType.HYPOTHESIS_END,
        name=title,
        output=state,
        experiment_run_labels=run_labels,
        configuration=configuration,
        secrets=None,
    )


@patch("chaosreliably.controls.experiment.logger")
def test_that_an_exception_does_not_get_raised_and_warning_logged(
    mock_logger: MagicMock,
) -> None:
    experiment.after_hypothesis_control(
        context={"title": "test-title", "probes": []},
        **cast(Dict[str, Any], {"state": {}, "configuration": {}, "secrets": None})
    )
    mock_logger.debug.assert_called_once_with(
        "An error occurred: 'chaosreliably', while running the After Hypothesis "
        "control, the Experiment execution won't be affected."
    )
