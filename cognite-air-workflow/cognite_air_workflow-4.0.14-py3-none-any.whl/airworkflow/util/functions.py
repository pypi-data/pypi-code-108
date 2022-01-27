import os
import time
from pathlib import Path
from typing import Dict, Iterator, Optional, Union

from cognite.client.exceptions import CogniteAPIError
from cognite.experimental import CogniteClient
from cognite.experimental.data_classes import Function
from requests.exceptions import ConnectionError
from urllib3.exceptions import MaxRetryError, ReadTimeoutError

from cognite.airworkflow import constants
from cognite.airworkflow.util import cdf, env
from cognite.airworkflow.util.cdf import FuncStatus

CHANNEL = "model_deployment_fails"


class DeployError(Exception):
    pass


def validate_secrets(secret_dct):
    if len(secret_dct) > 5:
        raise ValueError(f"No more than 5 secrets allowed, got {len(secret_dct)}!")

    for secret in secret_dct:
        if len(secret) > 15:
            raise ValueError(f"Secret name is too long (15 characters max): {secret}")


def format_secret_names(secrets: Dict[str, str]) -> Dict[str, str]:
    new_secrets = {}
    for key, item in secrets.items():
        new_key = key.lower().replace("_", "-")
        new_secrets[new_key] = item
    return new_secrets


def delete_function_if_exists(
    client: CogniteClient,
    function_name: Optional[str] = None,
    function_id: Optional[int] = None,
):
    assert function_name is not None or function_id is not None

    if cdf.does_function_exist(client, function_name, function_id):
        print(
            f"Function with name/id {function_name if function_id is None else function_id} "
            + f"already exists for {client.config.project}, will delete it.",
            flush=True,
        )
        if function_id:
            client.functions.delete(id=function_id)
        if function_name:
            client.functions.delete(external_id=function_name)
        time.sleep(5)


def deploy_function(
    client: CogniteClient,
    function_name: str,
    file_id: int,
    secrets: Dict[str, str],
    owner: str = "",
    oidc: bool = True,
) -> None:
    delete_function_if_exists(client, function_name)
    secrets = format_secret_names(secrets)
    validate_secrets(secrets)
    print(
        f"Deploying function using {'OIDC' if oidc else 'API-key'} for function: "
        f"{function_name} in project: {client.config.project}."
    )
    for deploy_try in range(1, 4):
        try:
            function = client.functions.create(
                name=function_name,
                file_id=file_id,
                secrets=secrets,
                external_id=function_name,
                api_key=None if oidc else client._config.api_key,
                owner=owner,
            )
            success, fn_obj = cdf.await_function_deployment(client, function, 1800)  # 30 minutes
            if success:
                print(
                    f"Function {function_name} (id: {function.id}) successfully "
                    f"created in project {client.config.project}.",
                    flush=True,
                )
                return
            if fn_obj.status == FuncStatus.FAILED:
                print(f"Error while deploying function {function_name} and function_id: {fn_obj.id}")
                print(f"Error message: {fn_obj.error['message']}")
                print(f"Error stack trace: {fn_obj.error['trace']}")
                # Raise an error that will be retried:
                raise DeployError(f"Deployment of function with external id {function_name} failed.")

            # Raise an error that will NOT be retried:
            raise TimeoutError(f"Deployment of function with external id {function_name} timed out.")

        except (DeployError, ReadTimeoutError, CogniteAPIError, MaxRetryError, ConnectionError) as e:
            print(f"Error happened during deployment: {e!r}", flush=True)
            delete_function_if_exists(client, function_name)
            if deploy_try >= 3:
                raise TimeoutError("Max function deploy retry count reached!") from e
            time.sleep(10)


def delete_function(client: CogniteClient, external_id: str):
    if cdf.does_function_exist(client, external_id):
        print(f"Deleting function named {external_id} ...", flush=True)
        client.functions.delete(external_id=external_id)
        print(f"Function {external_id} successfully deleted from project {client.config.project}.", flush=True)


def list_dangling_function(
    client: CogniteClient,
    expected_functions: Iterator[str],
    *,
    name_prefix: str = "",
) -> Iterator[Function]:
    functions = client.functions.list()
    if name_prefix:
        functions = list(filter(lambda f: name_prefix in f.name, functions))
    return filter(lambda f: f.name not in expected_functions, functions)


def get_function_name(
    path: Union[Path, str],
    *,
    version: str = "",
    ref: str = "",
    pr: bool = False,
    latest: bool = False,
) -> str:
    if isinstance(path, str):
        path = Path(path)
    if os.getenv(constants.gitlab_ci_project):
        function_name = f"{os.environ[constants.gitlab_ci_project]}/{path.name}:"
    else:
        function_name = f"{env.get_repo_name_auto()}/{path.name}:"
    if latest:
        return f"{function_name}latest"
    elif pr:
        if os.getenv(constants.gitlab_function_name_addition):
            return f"{function_name}{ref if ref else env.get_env_value(constants.gitlab_function_name_addition)}"

        else:
            return f"{function_name}{ref if ref else env.get_env_value('GITHUB_HEAD_REF')}"
    return f"{function_name}{version}"


def get_relative_function_path(path: Path) -> str:
    return "/".join(path.parts[path.parts.index("functions") + 1 :])  # noqa
