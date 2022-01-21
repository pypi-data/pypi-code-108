import pathlib
import re
import zipfile
from typing import Tuple

import click
from levo_commons.utils import get_grpc_channel

from ...apitesting import levo_testplans_service_pb2 as test_plans_service
from ...apitesting import levo_testplans_service_pb2_grpc as test_plans_service_grpc
from ...env_constants import TEST_PLANS_GRPC_URL, get_feature_testing_headers
from ...logger import get_logger
from .models import Plan

log = get_logger(__name__)

WORKSPACE_ID_HEADER = "x-levo-workspace-id"
LRN_REGEX = r"^[a-zA-Z0-9 _$%@!^*()+=?><:;'\".#|{}\[\]-]{0,127}:.*:tp/[a-z0-9A-Z _$%@!^*()+=?><:;'\".#|{}\[\]-]{0,127}"


def is_lrn_format(plan_lrn: str) -> bool:
    """Checks if the input string is in LRN format.
    Returns True or False.
    """
    if not re.fullmatch(LRN_REGEX, plan_lrn):
        return False

    return True


def get_plan(
    *, plan_lrn: str, workspace_id: str, local_dir: pathlib.Path, authz_header: str
) -> Plan:
    """Fetch the test plan specified by the LRN from Levo SaaS.
    Returns a valid Plan on success. A NULL (empty string) Plan.lrn
    indicates a failure.
    """
    path, plan = download(
        plan_lrn=plan_lrn,
        workspace_id=workspace_id,
        authz_header=authz_header,
        directory=local_dir,
    )

    # Did the remote download of plan succeed?
    if plan.lrn:
        extract(path, local_dir)

    return plan


def download(
    *,
    plan_lrn: str,
    workspace_id: str,
    authz_header: str,
    directory: pathlib.Path,
) -> Tuple[pathlib.Path, Plan]:
    """Downloads the test plan from Levo service by using Levo's GRPC API endpoint.
    Returns an empty Plan on error, where the lrn is a NULL string.
    """
    create_plans_directory(directory)

    metadata = [("authorization", authz_header), (WORKSPACE_ID_HEADER, workspace_id)]
    # Append the feature testing related headers to the metadata
    headers = get_feature_testing_headers()
    if headers:
        metadata.extend(headers.items())

    with get_grpc_channel(TEST_PLANS_GRPC_URL) as channel:
        stub = test_plans_service_grpc.LevoTestPlansServiceStub(channel)
        request = test_plans_service.ExportTestPlanByLrnRequest(test_plan_lrn=plan_lrn)  # type: ignore

        try:
            log.debug(
                f"Downloading test plan: {plan_lrn}",
                server=TEST_PLANS_GRPC_URL,
                request=request,
                metadata=metadata,
            )
            click.echo("Downloading the test plan from Levo SaaS...")
            plan = stub.ExportTestPlan(request=request, metadata=metadata)
        except Exception as e:
            log.debug(f"Error fetching test plan using LRN: {plan_lrn}", error=e)
            no_plan: Plan = Plan("", pathlib.Path(""), "")
            return pathlib.Path(""), no_plan

        plan_path = directory / f"{plan.name}.zip"
        save_plan(plan_path, plan.contents.bytes)
        saved_plan = Plan(
            name=plan.name, lrn=plan_lrn, catalog=directory, workspace_id=workspace_id
        )
        log.debug(f"Saved the test plan to directory: {plan_path}", plan=saved_plan)
        return plan_path, saved_plan


def create_plans_directory(directory: pathlib.Path) -> None:
    try:
        directory.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        click.secho(
            f"Cannot export test plan to the specified directory.\n"
            f"Please ensure the path is accessible from the CLI container.",
            fg="red",
        )
        log.debug("Could not create plans directory.", error=e)
        raise click.exceptions.Exit(1)


def save_plan(path: pathlib.Path, data: bytes) -> None:
    try:
        with path.open("wb") as fd:
            fd.write(data)
    except OSError as e:
        click.secho(
            "Cannot export test plan to the specified directory.\n Please check filesystem permissions.",
            fg="red",
        )
        log.error("Could not save the test plan.", path=path, error=e)
        raise click.exceptions.Exit(1)


def extract(path: pathlib.Path, directory: pathlib.Path) -> None:
    """Extract all test plans into `directory`."""
    click.echo("Extracting the test plan...")
    with zipfile.ZipFile(path) as archive:
        archive.extractall(directory)
