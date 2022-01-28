from unittest.mock import MagicMock, patch

from chaosreliably.slo.probes import slo_is_met


@patch("chaosreliably.slo.probes.all_objective_results_ok")
@patch("chaosreliably.slo.probes.get_objective_results_by_labels")
def test_that_slo_is_met_correctly_calls_probe_and_tolerance_with_no_limit(
    mock_get_objective_results_by_labels: MagicMock,
    mock_all_objective_results_ok: MagicMock,
) -> None:
    expected_results = [{"objective_result": "a-result"}]
    mock_get_objective_results_by_labels.return_value = expected_results
    mock_all_objective_results_ok.return_value = True
    expected_labels = {"a-label": "a-label-value"}

    slo_is_met_result = slo_is_met(labels=expected_labels, limit=1)

    mock_get_objective_results_by_labels.assert_called_once_with(
        limit=1, labels=expected_labels, configuration=None, secrets=None
    )
    mock_all_objective_results_ok.assert_called_once_with(expected_results)

    assert slo_is_met_result


@patch("chaosreliably.slo.probes.all_objective_results_ok")
@patch("chaosreliably.slo.probes.get_objective_results_by_labels")
def test_that_slo_is_met_correctly_calls_probe_and_tolerance_with_limit(
    mock_get_objective_results_by_labels: MagicMock,
    mock_all_objective_results_ok: MagicMock,
) -> None:
    expected_results = [{"objective_result": "a-result"}]
    mock_get_objective_results_by_labels.return_value = expected_results
    mock_all_objective_results_ok.return_value = False
    expected_labels = {"a-label": "a-label-value"}

    slo_is_met_result = slo_is_met(labels=expected_labels, limit=10)

    mock_get_objective_results_by_labels.assert_called_once_with(
        limit=10, labels=expected_labels, configuration=None, secrets=None
    )
    mock_all_objective_results_ok.assert_called_once_with(expected_results)

    assert not slo_is_met_result
