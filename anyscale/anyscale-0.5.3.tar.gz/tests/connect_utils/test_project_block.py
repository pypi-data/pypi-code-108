import os
from typing import Optional
from unittest.mock import Mock, mock_open as mock_open_factory, patch

import click
import pytest

from anyscale.connect_utils.project import ProjectBlock


@pytest.fixture
def mock_project_block():
    with patch.multiple(
        "anyscale.connect_utils.project.ProjectBlock", __init__=Mock(return_value=None)
    ):
        project_block = ProjectBlock()
        project_block.anyscale_api_client = Mock()
        project_block.log = Mock()
        project_block.block_label = ""
        return project_block


def test_get_default_project(mock_project_block):
    mock_project = Mock(id="project_id")
    mock_project.name = "project_name"
    mock_project_block.anyscale_api_client.get_default_project = Mock(
        return_value=Mock(result=mock_project)
    )
    assert mock_project_block._get_default_project() == (
        mock_project.id,
        mock_project.name,
    )

    mock_project_block.anyscale_api_client.get_default_project.assert_called_once_with()


def test_ensure_project_setup_at_dir_config_exists(mock_project_block):
    # Case where .anyscale.yaml exists and is correctly set up
    with patch.multiple("os.path", exists=Mock(return_value=True)), patch.multiple(
        "anyscale.project", get_project_id=Mock(return_value="project_id")
    ), patch("builtins.open", mock_open_factory()):
        mock_project = Mock(id="project_id")
        mock_project.name = "project_name"
        mock_project_block.anyscale_api_client.get_project = Mock(
            return_value=Mock(result=mock_project)
        )
        assert mock_project_block._ensure_project_setup_at_dir(
            "mock_project_dir", None
        ) == ("project_id", "project_name")

    # Case where .anyscale.yaml exists but has invalid project id
    with patch.multiple("os.path", exists=Mock(return_value=True)), patch.multiple(
        "anyscale.project", get_project_id=Mock(return_value="project_id")
    ), patch("builtins.open", mock_open_factory()):
        mock_project = Mock(id="project_id")
        mock_project.name = "project_name"
        mock_project_block.anyscale_api_client.get_project = Mock(
            side_effect=click.ClickException("")
        )
        with pytest.raises(click.ClickException):
            assert mock_project_block._ensure_project_setup_at_dir(
                "mock_project_dir", None
            )
        mock_project_block.anyscale_api_client.get_project.assert_called_once_with(
            "project_id"
        )

    # Case where .anyscale.yaml exists but doesn't have project_id in the file
    with patch.multiple("os.path", exists=Mock(return_value=True)), patch.multiple(
        "anyscale.project", get_project_id=Mock(return_value=None)
    ), patch("builtins.open", mock_open_factory()):
        with pytest.raises(click.ClickException):
            assert mock_project_block._ensure_project_setup_at_dir(
                "mock_project_dir", None
            )


@pytest.mark.parametrize("project_id", [None, "project_id"])
def test_ensure_project_setup_at_dir_no_config(
    mock_project_block, project_id: Optional[str]
):
    # Case where .anyscale.yaml doesn't exist

    mock_project_block.anyscale_api_client.search_projects = Mock(
        return_value=Mock(results=[Mock(id=project_id)])
    )
    mock_project_block.anyscale_api_client.create_project = Mock(
        return_value=Mock(result=Mock(id="project_id"))
    )
    mock_yaml_dump = Mock()
    with patch.multiple("os.path", exists=Mock(return_value=False)), patch(
        "builtins.open", mock_open_factory()
    ) as mock_open, patch.multiple("yaml", dump=mock_yaml_dump):
        mock_project_block._ensure_project_setup_at_dir(
            "mock_project_dir", "project_name"
        )
    if not project_id:
        mock_project_block.anyscale_api_client.create_project.assert_called_once_with(
            {
                "name": "project_name",
                "description": "Automatically created by Anyscale Connect",
            }
        )
    mock_open.assert_called_once_with("mock_project_dir/.anyscale.yaml", "w+")
    mock_yaml_dump.assert_called_once_with({"project_id": "project_id"})


@pytest.mark.parametrize("project_dir", [None, "test_project_dir"])
@pytest.mark.parametrize("project_exists_in_dir_tree", [True, False])
def test_init(project_dir: Optional[str], project_exists_in_dir_tree: bool):
    mock_get_default_project = Mock(
        return_value=("test_default_project_id", "test_default_project_name")
    )
    mock_ensure_project_setup_at_dir = Mock(
        return_value=("test_project_id", "test_project_name")
    )
    mock_find_project_root = Mock(
        return_value="test_project_dir" if project_exists_in_dir_tree else None
    )
    with patch.multiple(
        "anyscale.connect_utils.project.ProjectBlock",
        _get_default_project=mock_get_default_project,
        _ensure_project_setup_at_dir=mock_ensure_project_setup_at_dir,
    ), patch.multiple(
        "anyscale.connect_utils.project", get_auth_api_client=Mock(return_value=Mock())
    ), patch.multiple(
        "anyscale.project", find_project_root=mock_find_project_root
    ):
        project_block = ProjectBlock(
            project_dir=project_dir, project_name="test_project_name"
        )
        if project_dir:
            # Project dir passed in
            assert project_block.project_dir == os.path.abspath(
                os.path.expanduser(project_dir)
            )
            assert project_block.project_name == "test_project_name"
            mock_ensure_project_setup_at_dir.assert_called_once_with(
                os.path.abspath(os.path.expanduser(project_dir)), "test_project_name"
            )
        elif project_exists_in_dir_tree:
            # Find project dir in local directory structure
            assert project_block.project_dir == "test_project_dir"
            assert project_block.project_name == "test_project_name"
            mock_ensure_project_setup_at_dir.assert_called_once_with(
                "test_project_dir", "test_project_name"
            )
        else:
            # Use default project
            assert project_block.project_dir is None
            assert project_block.project_name == "test_default_project_name"
            mock_get_default_project.assert_called_once_with()
