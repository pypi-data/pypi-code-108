"""The test module which communicates with Levo platform, gets the tests, runs them,
and reports the results back to Levo.
"""
import importlib
import json
import os
import pathlib
import tempfile
from typing import Callable, Generator, List, Tuple

import click
import pkg_resources
from levo_commons.config import AuthConfig, PlanConfig
from levo_commons.events import InternalError
from levo_commons.utils import syspath_prepend

from levocli.docker_utils import map_hostpath_to_container
from levocli.errors import LevoCustomError

from ... import events
from ...config import TestPlanCommandConfig
from ...handlers import EventHandler
from ...logger import get_logger
from ...login import get_config_or_exit
from ...utils import format_exception
from . import local, remote
from .context import ExecutionContext
from .event_handler import LevoPlansEventHandler
from .logging import build_plan_logger
from .models import Plan
from .reporters.default import TestPlanConsoleOutputHandler
from .reporters.report_portal import TestPlanReportPortalHandler

TEST_PLAN_RUN_METHOD_NAME = "run_test_plan"

log = get_logger(__name__)


class PlanEventStream(events.EventStream):
    def stop(self) -> None:
        pass


def get_test_plan_entrypoint(module_path: str) -> Callable:
    """Load test case module & extract its entrypoint."""
    module = importlib.import_module(module_path)
    return getattr(module, TEST_PLAN_RUN_METHOD_NAME)


def should_process(path: pathlib.Path) -> bool:
    return path.is_dir() and path.name != "__pycache__"


def into_event_stream(plan: Plan, config: PlanConfig) -> events.EventStream:
    """Create a stream of Levo events."""
    return PlanEventStream(iter_cases(plan, config), lambda x: x)


def get_internal_error_event(exc: Exception) -> InternalError:
    exception_type = f"{exc.__class__.__module__}.{exc.__class__.__qualname__}"
    message = f"Could not run the test case."
    exception = format_exception(exc)
    exception_with_traceback = format_exception(exc, include_traceback=True)
    return InternalError(
        message=message,
        exception_type=exception_type,
        exception=exception,
        exception_with_traceback=exception_with_traceback,
        is_terminal=False,
    )


def iter_cases(plan: Plan, config: PlanConfig) -> Generator:
    # From the levo test framework, import levo.run_test_plan and run that with PlanConfig
    entrypoint = get_test_plan_entrypoint("levo")
    try:
        yield from entrypoint(config)
    except Exception as e:
        # This means we failed to run the test plan, which is considered as an error.
        # Hence, yield an error event here with details.
        yield get_internal_error_event(e)


def get_auth_config(input_config: TestPlanCommandConfig):
    if not input_config.auth:
        return None

    if input_config.auth_type.lower() == "basic":
        auth: Tuple[str, str] = input_config.auth
        return AuthConfig(auth_type="basic", username=auth[0], password=auth[1])
    elif input_config.auth_type.lower() == "token":
        return AuthConfig(auth_type="token", token=input_config.auth)
    elif input_config.auth_type.lower() == "apikey":
        return AuthConfig(auth_type="apikey", token=input_config.auth)
    else:
        msg = f"Unknown auth_type: {input_config.auth_type}"
        click.secho(msg, fg="red")
        raise click.UsageError(msg)


def _resolve_test_plan(workspace_id: str, testplan_ref: str, authz_header: str) -> Plan:
    """Resolve and fetch the test plan specified by the test plan reference string.
    The reference string can either be a LRN or a folder name. Returns Plan on success.
    Throws exceptions on failure.
    """
    # Is this a well formed LRN?
    if remote.is_lrn_format(plan_lrn=testplan_ref):
        plan: Plan = remote.get_plan(
            plan_lrn=testplan_ref,
            workspace_id=workspace_id,
            local_dir=pathlib.Path(tempfile.mkdtemp()),
            authz_header=authz_header,
        )

        if not plan.lrn:
            raise LevoCustomError(
                "Error retrieving the test plan from Levo SaaS."
                " The LRN provided is well formed, but the retrieve failed."
                " Please check if you are logged into the correct organization."
            )
        else:
            return plan

    # Is this a test plan folder?
    mapped_path: str = map_hostpath_to_container(testplan_ref)
    if os.path.isdir(mapped_path):
        plan = local.get_plan(mapped_path, workspace_id=workspace_id)

        if not plan.lrn:
            raise LevoCustomError(
                "The specified folder exists, but is not a valid Levo test plan."
            )
        else:
            return plan

    # If we get here, we neither have a valid LRN, nor a valid folder
    raise LevoCustomError(
        "Error resolving test plan."
        " The test plan must be either a valid Levo Resource Name (LRN) or folder.\n"
        "If specifying a folder, please ensure it exists, and the path is accessible by the Levo CLI container."
    )
    # End


def validate_argument_constraints(input_config: TestPlanCommandConfig):
    """Validate cross argument/options constraints that cannot be done
    via Click's argument validation callbacks
    """
    # We do not allow simultaneous use of both --auth-type and --env-file
    # options. We prefer --env-file in such cases as --auth-type is a subset
    if input_config.env_file_path and (input_config.auth_type and input_config.auth):
        click.secho(
            "\nSpecifying both '--env-file' and '--auth-type/--auth' options is not allowed."
            " Please use '--env-file' instead, as it's capabilities are a superset"
            " of '--auth-type'.",
            fg="red",
        )
        raise click.exceptions.Exit(1)


def _validate_all_python_requirements(catalog):
    """This method validates that all python requirements of LTF and test plan are satisfied by the
    CLI. If not, we raise an exception.
    """
    # Get all python requirements of LTF from the egg-info folder.
    requirements_file = catalog / "levo_test_framework.egg-info" / "requires.txt"
    if not requirements_file.exists():
        click.secho(
            "Error validating python requirements. The LTF egg-info folder does not contain a 'requires.txt' file.",
            fg="red",
        )
        raise click.exceptions.Exit(1)

    lines = []
    with open(requirements_file) as reqs_file:
        for line in reqs_file.readlines():
            # Read the lines until we hit [test] since we need to exclude the test requirements
            if line.startswith("[test]"):
                break
            lines.append(line)

        requirements = pkg_resources.parse_requirements(lines)
        deps = []
        for requirement in requirements:
            deps.append(str(requirement))
        log.debug(f"Python requirements of LevoTestFramework: {deps}")
        try:
            pkg_resources.require(deps)
        except (pkg_resources.DistributionNotFound, pkg_resources.VersionConflict) as e:
            click.secho(
                f"{e.req} dependency of Levo Test framework isn't met. "
                "Please use the latest CLI version to run the test plan.",
                fg="red",
            )
            raise click.exceptions.Exit(1)


def cli_entrypoint(input_config: TestPlanCommandConfig):
    config = get_config_or_exit()
    auth_config = config.auth
    # Get workspace_id
    workspace_id = config.workspace_id if config.workspace_id else ""

    try:
        plan: Plan = _resolve_test_plan(
            workspace_id=workspace_id,
            testplan_ref=input_config.testplan_ref,
            authz_header=auth_config.token_type + " " + auth_config.access_token,
        )
    except LevoCustomError as e:
        click.secho(e.message, fg="red")
        raise click.exceptions.Exit(1)

    if not plan.name:
        click.secho("Plan name is empty but required.", fg="red")
        raise click.exceptions.Exit(1)

    _validate_all_python_requirements(plan.catalog)

    config = PlanConfig(
        spec_path="",  # This should be optional ideally.
        test_plan_path=os.path.join(plan.catalog, plan.name),
        target_url=input_config.target_url,
        auth=input_config.auth,
        auth_type=input_config.auth_type,
        report_to_saas=input_config.report_to_saas,
        auth_config=get_auth_config(input_config) if input_config.auth else None,
        env_file_path=input_config.env_file_path,
        headers=input_config.headers,
    )
    execution_context = ExecutionContext(
        plan=plan, show_errors_tracebacks=input_config.show_errors_tracebacks
    )

    logger = build_plan_logger(plan.name, execution_context)
    execution_context.logger = logger

    reporters: List[EventHandler] = [TestPlanConsoleOutputHandler()]
    # Report the test results to ReportPortal, if enabled.
    if input_config.report_to_saas:
        reporters.append(TestPlanReportPortalHandler(plan, auth_config.access_token))

    reporter_names = [r.get_name() for r in reporters]
    log.debug(f"Initialized the reporters: {reporter_names}")

    handler = LevoPlansEventHandler(reporters=reporters, config=input_config)

    # Initialize modules
    manifest_path = pathlib.Path(config.test_plan_path).resolve() / "manifest.json"
    with manifest_path.open() as fd:
        manifest_json_dict = json.load(fd)
    if "modules" in manifest_json_dict:
        test_plan_modules = manifest_json_dict["modules"]
        config.module_providers = handler.setup_modules(test_plan_modules)

    with syspath_prepend(plan.catalog):
        event_stream = into_event_stream(plan, config)
        return events.handle([handler], event_stream, execution_context)


def export_plan(plan_lrn: str, local_dir: str):
    config = get_config_or_exit()
    auth_config = config.auth
    plan: Plan = remote.get_plan(
        plan_lrn=plan_lrn,
        workspace_id=config.workspace_id if config.workspace_id else "",
        local_dir=pathlib.Path(local_dir),
        authz_header=auth_config.token_type + " " + auth_config.access_token,
    )
    if not plan.lrn:
        raise LevoCustomError(
            "Error retrieving the test plan from Levo SaaS."
            " The LRN provided is well formed, but the retrieve failed."
        )
