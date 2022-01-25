from unittest.mock import Mock, patch

import click
import pytest

from anyscale.cluster_env import (
    get_build_from_cluster_env_identifier,
    get_cluster_env_from_name,
    list_builds,
    validate_successful_build,
)


def test_get_build_id_from_cluster_env_identifier():
    mock_anyscale_api_client = Mock()

    mock_get_cluster_env_from_name = Mock()
    mock_list_builds = Mock(return_value=[Mock(revision=3, id="mock_build_id")])
    with patch.multiple(
        "anyscale.cluster_env",
        get_cluster_env_from_name=mock_get_cluster_env_from_name,
        list_builds=mock_list_builds,
    ):
        assert (
            get_build_from_cluster_env_identifier(
                "my_cluster_env:3", mock_anyscale_api_client
            ).id
            == "mock_build_id"
        )

    mock_list_builds = Mock(
        return_value=[
            Mock(revision=3, id="mock_build_id3"),
            Mock(revision=1, id="mock_build_id1"),
        ]
    )
    with patch.multiple(
        "anyscale.cluster_env",
        get_cluster_env_from_name=mock_get_cluster_env_from_name,
        list_builds=mock_list_builds,
    ):
        assert (
            get_build_from_cluster_env_identifier(
                "my_cluster_env", mock_anyscale_api_client
            ).id
            == "mock_build_id3"
        )

    mock_list_builds = Mock(return_value=[])
    with patch.multiple(
        "anyscale.cluster_env",
        get_cluster_env_from_name=mock_get_cluster_env_from_name,
        list_builds=mock_list_builds,
    ):
        with pytest.raises(click.ClickException):
            get_build_from_cluster_env_identifier(
                "my_cluster_env:3", mock_anyscale_api_client
            )

    mock_list_builds = Mock(return_value=[])
    with patch.multiple(
        "anyscale.cluster_env",
        get_cluster_env_from_name=mock_get_cluster_env_from_name,
        list_builds=mock_list_builds,
    ):
        with pytest.raises(click.ClickException):
            get_build_from_cluster_env_identifier(
                "my_cluster_env", mock_anyscale_api_client
            )


def test_get_cluster_env_id_from_name():
    mock_anyscale_api_client = Mock()

    mock_cluster_env = Mock(id="my_cluster_env_id")
    mock_cluster_env.name = "my_cluster_env"
    mock_anyscale_api_client.search_cluster_environments = Mock(
        return_value=Mock(results=[mock_cluster_env])
    )
    assert (
        get_cluster_env_from_name("my_cluster_env", mock_anyscale_api_client).id
        == "my_cluster_env_id"
    )
    mock_anyscale_api_client.search_cluster_environments.assert_called_once_with(
        {"name": {"equals": "my_cluster_env"}, "paging": {"count": 1}}
    )

    mock_anyscale_api_client.search_cluster_environments.return_value = Mock(results=[])
    with pytest.raises(click.ClickException):
        assert get_cluster_env_from_name("my_cluster_env", mock_anyscale_api_client)


def test_list_builds():
    mock_anyscale_api_client = Mock()

    mock_anyscale_api_client.list_cluster_environment_builds = Mock(
        return_value=Mock(
            results=["result1", "result2"], metadata=Mock(next_paging_token=None)
        )
    )
    assert list_builds("my_cluster_env_id", mock_anyscale_api_client) == [
        "result1",
        "result2",
    ]
    mock_anyscale_api_client.list_cluster_environment_builds.assert_called_once_with(
        "my_cluster_env_id", count=50, paging_token=None
    )


def test_validate_successful_build():
    # Check the function return without error for successful build
    mock_anyscale_api_client = Mock()
    mock_anyscale_api_client.get_cluster_environment_build = Mock(
        return_value=Mock(result=Mock(status="succeeded"))
    )
    validate_successful_build("mock_build_id", mock_anyscale_api_client)
    mock_anyscale_api_client.get_cluster_environment_build.assert_called_once_with(
        "mock_build_id"
    )

    # Check the function raises an error for non-successful builds
    mock_anyscale_api_client.get_cluster_environment_build = Mock(
        return_value=Mock(
            result=Mock(status="failed", cluster_environment_id="mock_cluster_env_id")
        )
    )
    with pytest.raises(click.ClickException):
        validate_successful_build("mock_build_id", mock_anyscale_api_client)
    mock_anyscale_api_client.get_cluster_environment_build.assert_called_once_with(
        "mock_build_id"
    )
    mock_anyscale_api_client.get_cluster_environment.assert_called_once_with(
        "mock_cluster_env_id"
    )
