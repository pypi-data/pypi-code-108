from unittest.mock import Mock

from openapi_client.rest import ApiException
import pytest

from anyscale.client.openapi_client.models import (
    Cloud,
    CloudListResponse,
    CloudResponse,
)
from anyscale.cloud import get_cloud_id_and_name, get_cloud_json_from_id


def test_get_cloud_json_from_id(cloud_test_data: Cloud) -> None:
    mock_api_client = Mock()
    mock_api_client.get_cloud_api_v2_clouds_cloud_id_get.return_value = CloudResponse(
        result=cloud_test_data
    )

    cloud_json = get_cloud_json_from_id(cloud_test_data.id, api_client=mock_api_client)
    expected_json = {
        "id": cloud_test_data.id,
        "name": cloud_test_data.name,
        "provider": cloud_test_data.provider,
        "region": cloud_test_data.region,
        "credentials": cloud_test_data.credentials,
        "config": cloud_test_data.config,
    }
    assert cloud_json == expected_json
    mock_api_client.get_cloud_api_v2_clouds_cloud_id_get.assert_called_once_with(
        cloud_id=cloud_test_data.id
    )


def test_get_cloud_json_from_id_api_error(base_mock_api_client: Mock) -> None:
    base_mock_api_client.get_cloud_api_v2_clouds_cloud_id_get = Mock(
        side_effect=ApiException()
    )

    cloud_json = get_cloud_json_from_id("cld_1234", base_mock_api_client)
    expected_json = {
        "error": {
            "cloud_id": "cld_1234",
            "message": "The cloud with id, cld_1234 has been deleted. Please create a new cloud with `anyscale cloud setup`.",
        }
    }

    assert cloud_json == expected_json


def test_get_cloud_id_and_name_no_args(
    base_mock_api_client: Mock, cloud_test_data: Cloud
) -> None:
    base_mock_api_client.list_clouds_api_v2_clouds_get = Mock(
        return_value=CloudListResponse(results=[cloud_test_data])
    )
    result_id, result_name = get_cloud_id_and_name(base_mock_api_client)
    assert result_id == cloud_test_data.id
    assert result_name == cloud_test_data.name
    base_mock_api_client.list_clouds_api_v2_clouds_get.assert_called_once()

    base_mock_api_client.list_clouds_api_v2_clouds_get = Mock(
        return_value=CloudListResponse(results=[cloud_test_data, cloud_test_data])
    )
    with pytest.raises(Exception):
        get_cloud_id_and_name(base_mock_api_client)

    base_mock_api_client.list_clouds_api_v2_clouds_get.assert_called_once()


def test_get_cloud_id_and_name_two_args(
    base_mock_api_client: Mock, cloud_test_data: Cloud
) -> None:
    with pytest.raises(Exception):
        get_cloud_id_and_name(
            base_mock_api_client, cloud_test_data.id, cloud_test_data.name
        )


def test_get_cloud_id_and_name_id_only(
    base_mock_api_client: Mock, cloud_test_data: Cloud
) -> None:
    base_mock_api_client.get_cloud_api_v2_clouds_cloud_id_get = Mock(
        return_value=CloudResponse(result=cloud_test_data)
    )
    result_id, result_name = get_cloud_id_and_name(
        base_mock_api_client, cloud_id=cloud_test_data.id
    )
    assert result_id == cloud_test_data.id
    assert result_name == cloud_test_data.name
    base_mock_api_client.get_cloud_api_v2_clouds_cloud_id_get.assert_called_once()


def test_get_cloud_id_and_name_name_only(
    base_mock_api_client: Mock, cloud_test_data: Cloud
) -> None:
    base_mock_api_client.find_cloud_by_name_api_v2_clouds_find_by_name_post = Mock(
        return_value=CloudResponse(result=cloud_test_data)
    )
    result_id, result_name = get_cloud_id_and_name(
        base_mock_api_client, cloud_name=cloud_test_data.name
    )
    assert result_id == cloud_test_data.id
    assert result_name == cloud_test_data.name
    base_mock_api_client.find_cloud_by_name_api_v2_clouds_find_by_name_post.assert_called_once()
