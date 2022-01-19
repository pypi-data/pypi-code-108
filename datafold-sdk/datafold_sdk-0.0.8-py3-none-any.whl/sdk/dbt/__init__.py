import logging
import sys
from os import path, environ, walk
import tempfile
import zipfile
import json
import time
from typing import List, Optional, Tuple

import pydantic

from datafold_sdk.sdk.ci import list_runs
from datafold_sdk.sdk.exceptions import DatafoldSDKException
from datafold_sdk.sdk.utils import prepare_api_url, prepare_headers, run_command, post_data

logger = logging.getLogger(__file__)

GITHUB_EVENT_PATH = 'GITHUB_EVENT_PATH'


def check_commit_sha(cwd: str) -> str:
    github_actions_config = environ.get(GITHUB_EVENT_PATH)
    if github_actions_config:
        logger.info("Looks like we're on Github Actions")
        with open(github_actions_config, 'r') as file:
            event = json.loads(file.read())
            # We only want to fetch this information when we're on a PR
            # in case of master, the fallback method works just fine
            # In certain situations the key isn't available
            if 'pull_request' in event:
                return event['pull_request']['head']['sha']

    logger.info(f"Attempting to resolve commit-sha in directory: {cwd}")
    # Attempt to resolve commit sha from git command
    commit_sha = run_command(["git", "rev-parse", "HEAD"], capture=True, cwd=cwd)
    logger.info(f"Found commit sha: {commit_sha}")
    return commit_sha


def submit_artifacts(host: str,
                     api_key: str,
                     ci_config_id: int,
                     run_type: str,
                     target_folder: str,
                     commit_sha: Optional[str] = None) -> str:
    """
    Submits dbt artifacts to the datafold app server.

    Args:
        host          (str): The location of the datafold app server.
        api_key       (str): The API_KEY to use for authentication
        ci_config_id  (int): The ID of the CI config for which you submit these artefacts
                             (See the CI config ID in the CI settings screen).
        run_type      (str): The run_type to apply. Can be either "pull_request" or "production"
        target_folder (str): The location of the `target` folder after the `dbt run`, which includes
                             files this utility will zip and include in the upload
        commit_sha    (str): Optional. If not provided, the SDK will resolve this through a git command
                             otherwise used as is.
    Returns:
        commit_sha    (str): The commit sha that just has been submitted
    """

    api_segment = f"api/v1/dbt/submit_artifacts/{ci_config_id}"
    url = prepare_api_url(host, api_segment)
    headers = prepare_headers(api_key)

    if not commit_sha:
        commit_sha = check_commit_sha(target_folder)

    if not commit_sha:
        logger.error("No commit sha resolved. Override the commit_sha with the --commit-sha parameter")
        raise DatafoldSDKException("No commit sha resolved")

    target_folder = path.abspath(target_folder)
    with tempfile.NamedTemporaryFile(suffix=".zip", mode='w+b', delete=True) as tmp_file:
        with zipfile.ZipFile(tmp_file.name, 'w') as zip_file:
            seen_manifest = False
            seen_results = False
            for folder_name, _, file_names in walk(target_folder):
                rel_path = path.relpath(folder_name, target_folder)
                for file_name in file_names:
                    if file_name == "manifest.json":
                        seen_manifest = True
                    if file_name == "run_results.json":
                        seen_results = True

                    file_path = path.join(folder_name, file_name)
                    zip_path = path.join(rel_path, path.basename(file_path))
                    zip_file.write(file_path, zip_path)

        if not seen_manifest or not seen_results:
            logger.error("The manifest.json or run_results.json is missing in the target directory.")
            raise DatafoldSDKException("The manifest.json or run_results.json is missing in the target directory.")

        files = {'artifacts': open(tmp_file.name, 'rb')}
        data = {'commit_sha': commit_sha, 'run_type': run_type}

        post_data(url, files=files, data=data, headers=headers)

    logger.info("Successfully uploaded the manifest")
    return commit_sha


def wait_for_completion(
        host: str,
        api_key: str,
        ci_config_id: int,
        commit_sha: str,
        wait_in_minutes: int = 60):
    """
    Blocks until Datafold is done running the diff
    """

    start = time.monotonic()
    while 1:
        runs = list_runs(
            host,
            api_key,
            ci_config_id,
            pr_sha=commit_sha,
            limit=1,
        )
        seconds_elapsed = time.monotonic() - start
        if runs:
            run = runs[0]
            logger.info(f'Run #{run.id}, PR {run.pr_num}: {run.status}, {seconds_elapsed:.0f}s')

            if run.status == 'done':
                break

            if run.status == 'cancelled':
                logger.warning("The CI job has been cancelled, probably an old commit hash")
                sys.exit(1)
        else:
            logger.info(f'Waiting for CI run to start, {seconds_elapsed:.0f}s')

        if not runs and seconds_elapsed > 60:
            raise TimeoutError("Timed out waiting for the Data Diff to start")

        if seconds_elapsed > 60 * wait_in_minutes:
            raise TimeoutError("Timed out waiting for the Data Diff to complete")

        time.sleep(5)


class DbtPkInfo(pydantic.BaseModel):
    source: str
    sql_table: Tuple[str, ...]
    sql_pks: List[str]
    dbt_fqn: Tuple[str, ...]
    dbt_pks: List[str]
    dbt_original_file_path: str
    dbt_patch_path: Optional[str]
    warnings: List[str]


def check_pks_in_manifest(
        host: str, api_key: str, ci_config_id: int, manifest: bytes
) -> List[DbtPkInfo]:
    api_segment = f"api/internal/ci/{ci_config_id}/check_pks_in_dbt_manifest"
    url = prepare_api_url(host, api_segment)
    headers = prepare_headers(api_key)
    result = post_data(url, data=manifest, headers=headers).json()
    return [DbtPkInfo(**x) for x in result]
