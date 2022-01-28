from tempfile import NamedTemporaryFile
from typing import Any
from urllib.parse import quote

import pytest
import pytest_httpx
import yaml
from chaoslib.exceptions import ActivityFailed

from chaosreliably.slo.probes import get_objective_results_by_labels


def test_that_get_objective_results_by_label_returns_correct_results(
    httpx_mock: pytest_httpx._httpx_mock.HTTPXMock, results: Any
) -> None:
    labels = {
        "name": "exploring-reliability-guide",
        "service": "exploring-reliability-guide-service",
    }
    encoded_labels = quote(
        ",".join([f"{key}={value}" for key, value in labels.items()])
    )
    request_url = (
        "https://reliably.com/api/entities/test-org/reliably.com/v1/objectiveresult"
        f"?objective-match={encoded_labels}&limit=1"
    )
    httpx_mock.add_response(method="GET", url=request_url, json=results[:1])

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
        res = get_objective_results_by_labels(
            labels=labels, configuration={"reliably_config_path": f.name}, secrets=None
        )
        assert len(res) == 1


def test_that_get_objective_results_by_label_raises_exception_if_non_200(
    httpx_mock: pytest_httpx._httpx_mock.HTTPXMock,
) -> None:
    labels = {
        "name": "exploring-reliability-guide",
        "service": "exploring-reliability-guide-service",
    }
    encoded_labels = quote(
        ",".join([f"{key}={value}" for key, value in labels.items()])
    )
    request_url = (
        "https://reliably.com/api/entities/test-org/reliably.com/v1/objectiveresult"
        f"?objective-match={encoded_labels}&limit=1"
    )
    httpx_mock.add_response(method="GET", url=request_url, status_code=400)

    with pytest.raises(ActivityFailed):
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
            get_objective_results_by_labels(
                labels=labels,
                configuration={"reliably_config_path": f.name},
                secrets=None,
            )


def test_that_get_objective_results_by_label_passes_limit_parameter_correctly(
    httpx_mock: pytest_httpx._httpx_mock.HTTPXMock, results: Any
) -> None:
    labels = {
        "name": "exploring-reliability-guide",
        "service": "exploring-reliability-guide-service",
    }
    encoded_labels = quote(
        ",".join([f"{key}={value}" for key, value in labels.items()])
    )
    request_url = (
        "https://reliably.com/api/entities/test-org/reliably.com/v1/objectiveresult"
        f"?objective-match={encoded_labels}&limit=20"
    )
    httpx_mock.add_response(method="GET", url=request_url, json=results)

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
        res = get_objective_results_by_labels(
            labels=labels,
            limit=20,
            configuration={"reliably_config_path": f.name},
            secrets=None,
        )
        assert len(res) == 10
