from unittest.mock import Mock

import pytest
from tests.test_connect import RAY_COMMIT, RAY_VERSION

from anyscale.utils.ray_version_checker import check_required_ray_version


@pytest.mark.parametrize(
    "version,commit",
    [
        pytest.param("1.1.0", "fake_commit", id="BothWrong"),
        pytest.param(RAY_VERSION, RAY_COMMIT[2:], id="BadCommit"),
        pytest.param("1.0.0", RAY_COMMIT, id="BadVersion"),
    ],
)
def test_invalid_check_required_ray_version(version: str, commit: str) -> None:
    with pytest.raises(ValueError):
        check_required_ray_version(
            Mock(),
            ray_version=RAY_VERSION,
            ray_commit=RAY_COMMIT,
            required_ray_commit=commit,
            required_ray_version=version,
            ignore_version_check=False,
        )
    check_required_ray_version(
        Mock(),
        ray_version=RAY_VERSION,
        ray_commit=RAY_COMMIT,
        required_ray_commit=commit,
        required_ray_version=version,
        ignore_version_check=True,
    )


@pytest.mark.parametrize("ignore", [False, True])
def test_valid_check_required_ray_version(ignore) -> None:
    check_required_ray_version(
        Mock(),
        RAY_VERSION,
        RAY_COMMIT,
        RAY_VERSION,
        RAY_COMMIT,
        ignore_version_check=ignore,
    )
