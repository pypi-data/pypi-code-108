import os
import shutil
import time
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Optional, Tuple

from cognite.client import CogniteClient
from cognite.experimental import CogniteClient as ExperimentalClient
from cognite.experimental.data_classes import Function

from cognite.airworkflow.constants import AUTHENTICATION, COGNITE_CLIENT_NAME

os.environ["COGNITE_MAX_RETRIES"] = "5"
os.environ["COGNITE_TIMEOUT"] = "120"


class FuncStatus:
    # Not an exhaustive list, only what's needed:
    FAILED = "Failed"
    READY = "Ready"


def data_set_id(client: CogniteClient, name: str) -> int:
    return client.data_sets.retrieve(external_id=name).id


def zip_and_upload(client: CogniteClient, code_path: Path, file_name: str, data_set_name: str) -> int:
    print(f"Uploading code from {code_path} ... ", flush=True)
    with TemporaryDirectory() as tmpdir:
        zip_path = Path(tmpdir) / "function"
        shutil.make_archive(str(zip_path), "zip", str(code_path))
        id = data_set_id(client, data_set_name)
        file = client.files.upload(
            f"{zip_path}.zip",
            name=f"{file_name}.zip",
            external_id=f"{file_name}.zip",
            overwrite=True,
            data_set_id=id,
        )
        counter = 0
        while client.files.retrieve(file.id) is None:
            time.sleep(0.5)
            counter += 1
            if counter > 5:
                break
        print(f"Upload complete. \n{file}", flush=True)
        return file.id


def does_function_exist(
    client: ExperimentalClient, function_name: Optional[str] = None, function_id: Optional[int] = None
) -> bool:
    assert function_name is not None or function_id is not None
    if function_id:
        return bool(client.functions.retrieve(id=function_id))
    if function_name:
        return bool(client.functions.retrieve(external_id=function_name))
    return False


def await_function_deployment(client: ExperimentalClient, function: Function, max_wait: int) -> Tuple[bool, Function]:
    t_end = time.time() + max_wait
    old_id = function.id
    while time.time() < t_end:
        function = client.functions.retrieve(id=function.id)
        if function is not None:
            print(f"Function status {function.status} - Function id {function.id}", flush=True)
            if function.status == FuncStatus.READY:
                return True, function
            if function.status == FuncStatus.FAILED:
                return False, function
        else:
            print(f"API returns None for Function id {old_id}", flush=True)
        time.sleep(15.0)

    return False, function


def experimental_client(project: str) -> ExperimentalClient:
    project_auth = AUTHENTICATION[project]
    if project_auth.oidc:
        experimental_client = ExperimentalClient(
            token_url=project_auth.token_url,
            token_client_id=project_auth.client_id,
            token_client_secret=project_auth.get_client_secret(),
            token_scopes=project_auth.scopes,
            project=project,
            base_url=project_auth.base_url,
            client_name=COGNITE_CLIENT_NAME,
        )
    else:
        experimental_client = ExperimentalClient(
            api_key=project_auth.get_client_api_key(),
            client_name=COGNITE_CLIENT_NAME,
            project=project,
            base_url=project_auth.base_url,
        )
    return experimental_client
