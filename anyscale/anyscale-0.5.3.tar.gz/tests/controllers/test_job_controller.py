import json
import os
from pathlib import Path
import tempfile
from typing import Any, Dict, Optional
from unittest.mock import Mock, mock_open, patch

import click
import pytest
import yaml

from anyscale.client.openapi_client import CreateProductionJob, ProductionJobConfig
from anyscale.controllers.job_controller import JobConfig, JobController


CONDA_DICT = {"dependencies": ["pip", {"pip": ["pip-install-test==0.5"]}]}
PIP_LIST = ["requests==1.0.0", "pip-install-test"]


@pytest.fixture
def test_directory():
    with tempfile.TemporaryDirectory() as tmp_dir:
        path = Path(tmp_dir)
        subdir = path / "subdir"
        subdir.mkdir(parents=True)
        requirements_file = subdir / "requirements.txt"
        with requirements_file.open(mode="w") as f:
            print("\n".join(PIP_LIST), file=f)

        good_conda_file = subdir / "good_conda_env.yaml"
        with good_conda_file.open(mode="w") as f:
            yaml.dump(CONDA_DICT, f)

        bad_conda_file = subdir / "bad_conda_env.yaml"
        with bad_conda_file.open(mode="w") as f:
            print("% this is not a YAML file %", file=f)

        old_dir = os.getcwd()
        os.chdir(tmp_dir)
        yield subdir, requirements_file, good_conda_file, bad_conda_file
        os.chdir(old_dir)


@pytest.fixture
def patch_jobs_anyscale_api_client(base_mock_anyscale_api_client: Mock):
    base_mock_anyscale_api_client.get_cluster_environment_build = Mock(
        return_value=Mock(result=Mock(status="succeeded"))
    )
    with patch.multiple(
        "anyscale.cluster_env",
        get_auth_api_client=Mock(
            return_value=Mock(anyscale_api_client=base_mock_anyscale_api_client)
        ),
    ):
        yield


@pytest.mark.parametrize(
    "config_dict",
    [
        {
            "entrypoint": "mock_entrypoint",
            "build_id": "mock_build_id",
            "compute_config_id": "mock_compute_config_id",
        },
        {
            "entrypoint": "mock_entrypoint",
            "cluster_env": "mock_cluster_env",
            "compute_config": "mock_compute_config",
        },
        {
            "entrypoint": "mock_entrypoint",
            "cluster_env": "mock_cluster_env",
            "cloud": "mock_cloud",
        },
        {"entrypoint": "mock_entrypoint", "cluster_env": "mock_cluster_env"},
        {"entrypoint": "mock_entrypoint", "cloud": "mock_cloud"},
        {"entrypoint": "mock_entrypoint"},
        {"entrypoint": "mock_entrypoint", "project_id": "specified_project_id"},
    ],
)
@pytest.mark.parametrize("use_default_project", [True, False])
def test_submit_job(
    mock_auth_api_client, config_dict: Dict[str, Any], use_default_project: bool,
) -> None:
    config_project_id = config_dict.get("project_id")
    job_controller = JobController()
    mock_project_definition = Mock()
    mock_project_definition.root = "/some/directory"
    if use_default_project:
        mock_find_project_root = Mock(return_value=None)
        job_controller.anyscale_api_client.get_default_project = Mock(
            return_value=Mock(result=Mock(id="mock_default_project_id"))
        )
    else:
        mock_find_project_root = Mock(return_value="root_path")

    mock_get_project_id = Mock(return_value="mock_project_id")

    mock_get_build_from_cluster_env_identifier = Mock(
        return_value=Mock(id="mock_build_id")
    )
    mock_get_cluster_compute_from_name = Mock(
        return_value=Mock(id="mock_compute_config_id")
    )
    mock_get_default_cluster_compute = Mock(
        return_value=Mock(id="mock_compute_config_id")
    )
    mock_validate_successful_build = Mock()
    mock_get_default_cluster_env_build = Mock(return_value=Mock(id="mock_build_id"))
    with patch(
        "builtins.open", mock_open(read_data=json.dumps(config_dict))
    ), patch.multiple(
        "anyscale.controllers.job_controller",
        find_project_root=mock_find_project_root,
        get_project_id=mock_get_project_id,
        get_build_from_cluster_env_identifier=mock_get_build_from_cluster_env_identifier,
        get_cluster_compute_from_name=mock_get_cluster_compute_from_name,
        get_default_cluster_compute=mock_get_default_cluster_compute,
        validate_successful_build=mock_validate_successful_build,
        get_default_cluster_env_build=mock_get_default_cluster_env_build,
    ), patch.multiple(
        "os.path", exists=Mock(return_value=True)
    ):
        job_controller.submit(
            "mock_config_file", name="mock_name", description="mock_description"
        )
    mock_validate_successful_build.assert_called_once_with("mock_build_id")
    if use_default_project and not config_project_id:
        job_controller.anyscale_api_client.get_default_project.assert_called_once_with()

    if config_project_id:
        final_project_id = config_project_id
    elif use_default_project:
        final_project_id = "mock_default_project_id"
    else:
        final_project_id = "mock_project_id"
    job_controller.api_client.create_job_api_v2_decorated_ha_jobs_create_post.assert_called_once_with(
        CreateProductionJob(
            name="mock_name",
            description="mock_description",
            project_id=final_project_id,
            config=ProductionJobConfig(
                **{
                    "entrypoint": "mock_entrypoint",
                    "build_id": "mock_build_id",
                    "compute_config_id": "mock_compute_config_id",
                }
            ),
        )
    )
    if "cluster_env" not in config_dict and "build_id" not in config_dict:
        mock_get_default_cluster_env_build.assert_called_once_with()


@pytest.mark.parametrize("include_all_users", [False, True])
@pytest.mark.parametrize("name", ["mock_job_name", None])
@pytest.mark.parametrize("job_id", ["mock_job_id", None])
@pytest.mark.parametrize("project_id", ["mock_project_id", None])
@pytest.mark.parametrize(
    "is_service", [False, True]
)  # Whether command should list jobs or services
@pytest.mark.parametrize(
    "passed_service_id", [False, True]
)  # Whether `job_id` is id of job or service
def test_list_jobs(
    mock_auth_api_client,
    include_all_users: bool,
    name: Optional[str],
    job_id: Optional[str],
    project_id: Optional[str],
    is_service: bool,
    passed_service_id: bool,
) -> None:
    job_controller = JobController()
    job_controller.api_client.get_user_info_api_v2_userinfo_get = Mock(
        return_value=Mock(result=Mock(id="mock_user_id"))
    )
    job_controller.api_client.list_decorated_jobs_api_v2_decorated_ha_jobs_get = Mock(
        return_value=Mock(
            results=[Mock(config=Mock(entrypoint=""))] * 10,
            metadata=Mock(next_paging_token="paging_token"),
        )
    )
    job_controller.api_client.get_job_api_v2_decorated_ha_jobs_production_job_id_get = Mock(
        return_value=Mock(
            result=Mock(
                config=Mock(entrypoint="", is_service=passed_service_id),
                is_service=passed_service_id,
            )
        )
    )

    if is_service != passed_service_id and job_id is not None:
        # Raise error if trying to list id that is not valid for the command.
        # Eg: job_id providied for `anyscale service list`
        with pytest.raises(click.ClickException):
            job_controller.list(
                include_all_users=include_all_users,
                name=name,
                job_id=job_id,
                project_id=project_id,
                is_service=is_service,
                max_items=20,
            )
        return
    else:
        job_controller.list(
            include_all_users=include_all_users,
            name=name,
            job_id=job_id,
            project_id=project_id,
            is_service=is_service,
            max_items=20,
        )

    if job_id:
        job_controller.api_client.get_job_api_v2_decorated_ha_jobs_production_job_id_get.assert_called_once_with(
            job_id
        )
        job_controller.api_client.get_user_info_api_v2_userinfo_get.assert_not_called()
        job_controller.api_client.list_decorated_jobs_api_v2_decorated_ha_jobs_get.assert_not_called()
    else:
        creator_id: Optional[str] = None
        if not include_all_users:
            creator_id = "mock_user_id"
            job_controller.api_client.get_user_info_api_v2_userinfo_get.assert_called_once()
        else:
            job_controller.api_client.get_user_info_api_v2_userinfo_get.assert_not_called()
        job_controller.api_client.get_job_api_v2_decorated_ha_jobs_production_job_id_get.assert_not_called()
        job_controller.api_client.list_decorated_jobs_api_v2_decorated_ha_jobs_get.assert_any_call(
            creator_id=creator_id,
            name=name,
            project_id=project_id,
            type_filter="SERVICE" if is_service else "BATCH_JOB",
            count=10,
        )
        job_controller.api_client.list_decorated_jobs_api_v2_decorated_ha_jobs_get.assert_any_call(
            creator_id=creator_id,
            name=name,
            project_id=project_id,
            type_filter="SERVICE" if is_service else "BATCH_JOB",
            count=10,
            paging_token="paging_token",
        )
        assert (
            job_controller.api_client.list_decorated_jobs_api_v2_decorated_ha_jobs_get.call_count
            == 2
        )


@pytest.mark.parametrize(
    "is_service", [False, True]
)  # Whether command should list jobs or services
@pytest.mark.parametrize("name", ["mock_job_name", None])
@pytest.mark.parametrize("id", ["mock_job_id", None])
def test_terminate_job(
    mock_auth_api_client, name: Optional[str], id: Optional[str], is_service: bool,
) -> None:
    job_controller = JobController()
    job_controller.api_client.list_decorated_jobs_api_v2_decorated_ha_jobs_get = Mock(
        return_value=Mock(results=[Mock(id="mock_job_id")])
    )
    if not name and not id:
        with pytest.raises(click.ClickException):
            job_controller.terminate(id, name, is_service)
        return
    else:
        job_controller.terminate(id, name, is_service)

    job_controller.api_client.terminate_job_api_v2_decorated_ha_jobs_production_job_id_terminate_post.assert_called_once_with(
        "mock_job_id"
    )
    if name is not None and id is None:
        job_controller.api_client.list_decorated_jobs_api_v2_decorated_ha_jobs_get.assert_called_once_with(
            name=name, type_filter="SERVICE" if is_service else "BATCH_JOB",
        )


class TestValidateConda:
    def test_validate_conda_str(self, test_directory, patch_jobs_anyscale_api_client):
        jc = JobConfig(
            entrypoint="ls",
            build_id="123",
            compute_config_id="test",
            runtime_env={"conda": "env_name"},
        )
        assert jc.runtime_env["conda"] == "env_name"

    def test_validate_conda_invalid_path(self, patch_jobs_anyscale_api_client):
        with pytest.raises(click.ClickException):
            JobConfig(
                entrypoint="ls",
                build_id="123",
                compute_config_id="test",
                runtime_env={"conda": "../bad_path.yaml"},
            )

    @pytest.mark.parametrize("absolute_path", [True, False])
    def test_validate_conda_valid_file(
        self, test_directory, absolute_path, patch_jobs_anyscale_api_client
    ):
        _, _, good_conda_file, _ = test_directory

        if absolute_path:
            good_conda_file = good_conda_file.resolve()

        jc = JobConfig(
            entrypoint="ls",
            build_id="123",
            compute_config_id="test",
            runtime_env={"conda": str(good_conda_file)},
        )
        assert jc.runtime_env["conda"] == CONDA_DICT

    @pytest.mark.parametrize("absolute_path", [True, False])
    def test_validate_conda_invalid_file(
        self, test_directory, absolute_path, patch_jobs_anyscale_api_client
    ):
        _, _, _, bad_conda_file = test_directory

        if absolute_path:
            bad_conda_file = bad_conda_file.resolve()

        with pytest.raises(click.ClickException):
            JobConfig(
                entrypoint="ls",
                build_id="123",
                compute_config_id="test",
                runtime_env={"conda": str(bad_conda_file)},
            )

    def test_validate_conda_valid_dict(self, patch_jobs_anyscale_api_client):
        jc = JobConfig(
            entrypoint="ls",
            build_id="123",
            compute_config_id="test",
            runtime_env={"conda": CONDA_DICT},
        )
        assert jc.runtime_env["conda"] == CONDA_DICT


class TestValidatePip:
    def test_validate_pip_invalid_path(self, patch_jobs_anyscale_api_client):
        with pytest.raises(click.ClickException):
            JobConfig(
                entrypoint="ls",
                build_id="123",
                compute_config_id="test",
                runtime_env={"pip": "../bad_path.txt"},
            )

    @pytest.mark.parametrize("absolute_path", [True, False])
    def test_validate_pip_valid_file(
        self, test_directory, absolute_path, patch_jobs_anyscale_api_client
    ):
        _, requirements_file, _, _ = test_directory

        if absolute_path:
            requirements_file = requirements_file.resolve()

        jc = JobConfig(
            entrypoint="ls",
            build_id="123",
            compute_config_id="test",
            runtime_env={"pip": str(requirements_file)},
        )
        assert jc.runtime_env["pip"] == PIP_LIST

    def test_validate_pip_valid_list(self, patch_jobs_anyscale_api_client):
        jc = JobConfig(
            entrypoint="ls",
            build_id="123",
            compute_config_id="test",
            runtime_env={"pip": PIP_LIST},
        )
        assert jc.runtime_env["pip"] == PIP_LIST


class TestValidateWorkingDir:
    def test_reject_local_dir(self, patch_jobs_anyscale_api_client):
        with pytest.raises(click.ClickException):
            JobConfig(
                entrypoint="ls",
                build_id="123",
                compute_config_id="test",
                runtime_env={"working_dir": "."},
            )

        with pytest.raises(click.ClickException):
            JobConfig(
                entrypoint="ls",
                build_id="123",
                compute_config_id="test",
                runtime_env={"working_dir": "/tmp/dir"},
            )

    def test_accept_uri(self, patch_jobs_anyscale_api_client):
        jc = JobConfig(
            entrypoint="ls",
            build_id="123",
            compute_config_id="test",
            runtime_env={"working_dir": "s3://path/to/archive.zip"},
        )
        assert jc.runtime_env["working_dir"] == "s3://path/to/archive.zip"


class TestValidatePyModules:
    def test_reject_local_dir(self, patch_jobs_anyscale_api_client):
        with pytest.raises(click.ClickException):
            JobConfig(
                entrypoint="ls",
                build_id="123",
                compute_config_id="test",
                runtime_env={"py_modules": ["."]},
            )

        with pytest.raises(click.ClickException):
            JobConfig(
                entrypoint="ls",
                build_id="123",
                compute_config_id="test",
                runtime_env={"py_modules": ["/tmp/dir"]},
            )

    def test_accept_uri(self, patch_jobs_anyscale_api_client):
        jc = JobConfig(
            entrypoint="ls",
            build_id="123",
            compute_config_id="test",
            runtime_env={"py_modules": ["s3://path/to/archive.zip"]},
        )
        assert jc.runtime_env["py_modules"] == ["s3://path/to/archive.zip"]


@pytest.mark.parametrize("project_id", [None, "proj_id"])
@pytest.mark.parametrize("project_name", [None, "proj_name"])
def test_validate_project_id_field(
    project_id: Optional[str], project_name: Optional[str]
):
    mock_get_proj_id_from_name = Mock(return_value="proj_id")
    mock_validate_successful_build = Mock()
    config_dict = {
        "entrypoint": "mock_entrypoint",
        "build_id": "mock_build_id",
        "compute_config_id": "mock_compute_config_id",
        "project_id": project_id,
        "project": project_name,
    }
    with patch.multiple(
        "anyscale.controllers.job_controller",
        get_proj_id_from_name=mock_get_proj_id_from_name,
        validate_successful_build=mock_validate_successful_build,
    ):
        if project_id and project_name:
            with pytest.raises(click.ClickException):
                job_config = JobConfig.parse_obj(config_dict)
        else:
            job_config = JobConfig.parse_obj(config_dict)
            if project_name:
                assert job_config.project_id == "proj_id"
                mock_get_proj_id_from_name.assert_called_once_with(project_name)
            else:
                assert job_config.project_id == project_id
