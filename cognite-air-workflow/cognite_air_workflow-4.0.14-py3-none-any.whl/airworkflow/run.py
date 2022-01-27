import os
import sys
from itertools import product
from pathlib import Path

import cognite.airworkflow.constants as const
from cognite.airworkflow.function_deployer import FunctionDeployer
from cognite.airworkflow.master_config import get_master_config, get_parallel_deployment, write_dependency_yamls
from cognite.airworkflow.model_asset_hierarchy import ModelAssetHierarchy
from cognite.airworkflow.util import cdf, env, functions, github, yaml


def handle_asset_hierarchy():
    function_name, project = sys.argv[3].split("@")
    function_name_path = Path(function_name)
    function_path = const.FUNCTIONS_PATH / function_name_path / const.FUNCTION_REL_CONFIG_PATH
    master_config = {
        function_path.parent.parent: yaml.load_and_validate(function_path, const.CONFIG_SCHEMA_PATH, function_name)
    }
    write_dependency_yamls(master_config)
    if len(sys.argv) >= 2:
        airInfra = sys.argv[2] == "True"
    else:
        airInfra = False
    print(f"Running Model Asset Hierarchy create/update for project {project}")
    ModelAssetHierarchy(master_config, project, airInfra).create_or_update()


def handle_function_deployments():
    github_event_name = env.get_env_value("GITHUB_EVENT_NAME")
    github_ref = env.get_env_value("GITHUB_REF")
    is_delete = "IS_DELETE" in os.environ and os.environ["IS_DELETE"] == "true"
    is_pr = github_event_name == "pull_request"
    assert (
        len(sys.argv) >= 3 and sys.argv[2]
    ), "Expected a function name passed as a command line argument, but got nothing"
    function_name, project_name = sys.argv[2].split("@")
    print(f"HANDLING {github_event_name} ON {github_ref} FOR FUNCTION {function_name}", flush=True)
    for deployment in get_parallel_deployment(function_name, project_name):
        FunctionDeployer(deployment, is_delete, is_pr).handle_deployment()


def handle_delete_functions():
    """
    1. Find name of all functions that should be deployed: Based on what's on master and what's in PRs
    2. List all functions currently deployed
    3. Delete the diff
    """
    _, project_to_config = get_master_config()
    for project, config in project_to_config.items():
        function_paths = [functions.get_relative_function_path(p) for p in config]
        if os.getenv("CI_PROJECT_ID") and os.getenv("GITLAB_ACCESS_TOKEN"):
            pr_refs = github.gitlab_open_mrs(str(os.environ["CI_PROJECT_ID"]), str(os.environ["GITLAB_ACCESS_TOKEN"]))
        else:
            pr_refs = github.get_open_pr_refs()
        all_functions = [functions.get_function_name(f, latest=True) for f in function_paths] + [
            functions.get_function_name(f, pr=True, ref=ref) for ref, f in list(product(pr_refs, function_paths))
        ]
        info = const.AUTHENTICATION[project]
        client = cdf.experimental_client(info.project)
        dangling = functions.list_dangling_function(client, all_functions, name_prefix=env.get_repo_name_auto())
        for function in dangling:
            functions.delete_function(client, function.external_id)


def handle_check_deployment():
    function_name, project_name = sys.argv[2].split("@")
    client = cdf.experimental_client(project_name)
    model_asset = client.assets.retrieve(external_id=function_name)
    if model_asset is None:
        print(str(True))
        return str(True)

    # check if function has been deployed
    repo_name = env.get_env_value("GITHUB_REPOSITORY")
    function_external_id = str(repo_name) + "/" + str(function_name) + ":latest"

    function_asset = client.functions.retrieve(external_id=function_external_id)
    if function_asset is None:
        print(str(True))
        return str(True)

    cdf_model_version = model_asset.metadata["modelVersion"]
    configuration = get_master_config()[1][project_name]
    key1 = [i for i in configuration.keys() if i.parts[-1] == function_name][0]
    model_version = configuration[key1].model_version
    model_version = ".".join(model_version.split(".")[:-1])
    already_deployed = str(model_version != cdf_model_version)
    print(already_deployed)
    return already_deployed


if __name__ == "__main__":
    if sys.argv[1] == "model":
        handle_asset_hierarchy()
    elif sys.argv[1] == "function":
        handle_function_deployments()
    elif sys.argv[1] == "delete":
        handle_delete_functions()
    elif sys.argv[1] == "check_deployment":
        handle_check_deployment()
