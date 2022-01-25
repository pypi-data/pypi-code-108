from unittest.mock import ANY, Mock, patch

from anyscale.cluster_compute import (
    get_cluster_compute_from_name,
    get_default_cluster_compute,
    register_compute_template,
)
from anyscale.sdk.anyscale_client import ComputeTemplateQuery, CreateComputeTemplate


def test_get_default_cluster_compute():
    mock_api_client = Mock()
    mock_anyscale_api_client = Mock()
    mock_anyscale_api_client.get_default_compute_config = Mock(
        return_value=Mock(result="mock_config_obj")
    )
    mock_register_template = Mock(return_value="mock_compute_template")
    with patch.multiple(
        "anyscale.cluster_compute",
        get_cloud_id_and_name=Mock(return_value=("mock_cloud_id", "mock_cloud_name")),
        register_compute_template=mock_register_template,
    ):
        assert (
            get_default_cluster_compute(
                "mock_cloud_name", None, mock_api_client, mock_anyscale_api_client
            )
            == "mock_compute_template"
        )
    mock_anyscale_api_client.get_default_compute_config.assert_called_once_with(
        "mock_cloud_id"
    )
    mock_register_template.assert_called_once_with("mock_config_obj")


def test_register_compute_template():
    mock_api_client = Mock()
    mock_api_client.create_compute_template_api_v2_compute_templates_post = Mock(
        return_value=Mock(result=Mock(id="mock_template_id"))
    )

    assert (
        register_compute_template("mock_template_obj", mock_api_client).id
        == "mock_template_id"
    )
    mock_api_client.create_compute_template_api_v2_compute_templates_post.assert_called_once_with(
        create_compute_template=CreateComputeTemplate(
            name=ANY, config="mock_template_obj", anonymous=True,
        )
    )


def test_get_cluster_compute_from_name():
    mock_api_client = Mock()
    mock_api_client.search_compute_templates_api_v2_compute_templates_search_post = Mock(
        return_value=Mock(results=[Mock(id="mock_id")])
    )
    assert get_cluster_compute_from_name("mock_name", mock_api_client).id == "mock_id"

    mock_api_client.search_compute_templates_api_v2_compute_templates_search_post.assert_called_once_with(
        ComputeTemplateQuery(
            orgwide=True, name={"equals": "mock_name"}, include_anonymous=True,
        )
    )
