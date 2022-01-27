import argparse
import imp
import importlib
import io
import os
import shutil
import sys
import tarfile
from contextlib import redirect_stdout
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import Callable
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

import pendulum
import requests
from google.protobuf.empty_pb2 import Empty
from yaspin.spinners import Spinners

import tecton
from .cli_utils import bold
from .cli_utils import confirm_or_exit
from tecton._internals import metadata_service
from tecton._internals import sdk_decorators
from tecton._internals.analytics import AnalyticsLogger
from tecton._internals.analytics import TectonStateUpdateMetrics
from tecton._internals.display import Displayable
from tecton._internals.tecton_errors import TectonAPIInaccessibleError
from tecton._internals.utils import format_freshness_table
from tecton._internals.utils import format_materialization_attempts
from tecton._internals.utils import get_all_freshness
from tecton.cli import api_key
from tecton.cli import common
from tecton.cli import hook_template
from tecton.cli import printer
from tecton.cli import workspace
from tecton.cli.engine import dump_local_state
from tecton.cli.engine import update_tecton_state
from tecton.cli.error_utils import pretty_error
from tecton.okta import OktaAuthorizationFlow
from tecton_proto.metadataservice.metadata_service_pb2 import GetFeatureViewRequest
from tecton_proto.metadataservice.metadata_service_pb2 import GetMaterializationStatusRequest
from tecton_proto.metadataservice.metadata_service_pb2 import GetRestoreInfoRequest
from tecton_proto.metadataservice.metadata_service_pb2 import GetStateUpdateLogRequest
from tecton_spark import repo_file_handler


analytics = AnalyticsLogger()


@dataclass
class Command:
    command: str
    description: str
    uses_workspace: bool  # Behavior will depend on selected workspace
    requires_auth: bool
    handler: Callable


def py_path_to_module(path: Path, repo_root: Path) -> str:
    return str(path.relative_to(repo_root))[: -len(".py")].replace("./", "").replace("/", ".").replace("\\", ".")


def plural(x, singular, plural):
    if x == 1:
        return singular
    else:
        return plural


Fco = Union[
    tecton.Entity,
    tecton.data_sources.data_source.BaseDataSource,
    tecton.transformations.transformation.Transformation,
    tecton.feature_views.FeatureDefinition,
    tecton.FeatureService,
]


def import_module_with_pretty_errors(
    file_path: Path,
    module_path: str,
    py_files: List[Path],
    repo_root: Path,
    debug: bool,
    before_error: Callable[[], None],
) -> ModuleType:
    from pyspark.sql.utils import AnalysisException

    try:
        module = importlib.import_module(module_path)
        if Path(module.__file__) != file_path:
            before_error()
            relpath = file_path.relative_to(repo_root)
            printer.safe_print(
                f"Python module name {bold(module_path)} ({relpath}) conflicts with module {module_path} from {module.__file__}. Please use a different name.",
                file=sys.stderr,
            )
            sys.exit(1)

        return module
    except AnalysisException as e:
        before_error()
        pretty_error(
            Path(file_path),
            py_files,
            exception=e,
            repo_root=repo_root,
            error_message="Analysis error",
            error_details=e.desc,
            debug=debug,
        )
        sys.exit(1)
    except tecton.tecton_errors.TectonValidationError as e:
        before_error()
        pretty_error(Path(file_path), py_files, exception=e, repo_root=repo_root, error_message=e.args[0], debug=debug)
        sys.exit(1)
    except SyntaxError as e:
        before_error()
        details = None
        if e.text and e.offset:
            details = e.text + (" " * e.offset) + "^^^"
        pretty_error(
            Path(file_path),
            py_files,
            exception=e,
            repo_root=repo_root,
            error_message=e.args[0],
            error_details=details,
            debug=debug,
        )
        sys.exit(1)
    except TectonAPIInaccessibleError as e:
        before_error()
        printer.safe_print("Failed to connect to Tecton server at", e.args[1], ":", e.args[0])
        sys.exit(1)
    except Exception as e:
        before_error()
        pretty_error(Path(file_path), py_files, exception=e, repo_root=repo_root, error_message=e.args[0], debug=debug)
        sys.exit(1)


def collect_top_level_objects(py_files: List[Path], repo_root: Path, debug: bool, pretty_errors: bool) -> List[Fco]:
    from tecton._internals.fco import _ALL_FCOS

    modules = [py_path_to_module(p, repo_root) for p in py_files]

    with printer.safe_yaspin(Spinners.earth, text="Importing feature repository modules") as sp:
        for file_path, module_path in zip(py_files, modules):
            sp.text = f"Processing feature repository module {module_path}"

            if pretty_errors:
                module = import_module_with_pretty_errors(
                    file_path=file_path,
                    module_path=module_path,
                    py_files=py_files,
                    repo_root=repo_root,
                    debug=debug,
                    before_error=lambda: sp.fail(printer.safe_string("⛔")),
                )
            else:
                module = importlib.import_module(module_path)

        num_modules = len(modules)
        sp.text = (
            f"Imported {num_modules} Python {plural(num_modules, 'module', 'modules')} from the feature repository"
        )
        sp.ok(printer.safe_string("✅"))

        return list(_ALL_FCOS.values())


def prepare_args(args) -> Tuple[List[Fco], str, List[Path]]:
    repo_file_handler.ensure_prepare_repo()
    repo_files = repo_file_handler.repo_files()
    repo_root = repo_file_handler.repo_root()

    py_files = [p for p in repo_files if p.suffix == ".py"]
    os.chdir(repo_root)

    top_level_objects = collect_top_level_objects(
        py_files, repo_root=Path(repo_root), debug=args.debug, pretty_errors=True
    )

    return top_level_objects, repo_root, repo_files


def check_version():
    try:
        metadata_service.instance().Nop(Empty())
    except Exception as e:
        printer.safe_print("Error connecting to tecton server: ", e, file=sys.stderr)
        sys.exit(1)


def debug_dump(args) -> None:
    top_level_objects, _, _ = prepare_args(args)
    dump_local_state(top_level_objects)


def maybe_run_tests(args):
    pyfile = Path(".tecton/hooks/plan.py")
    if not pyfile.exists():
        return 0

    prepare_args(args)

    f = io.StringIO()
    with printer.safe_yaspin(Spinners.earth, text="Running Tests") as sp:
        with open(pyfile, "rb") as fp:
            test_module = imp.load_module(".tecton/hooks", fp, ".tecton/hooks/plan.py", (".py", "rb", imp.PY_SOURCE))
            # pytest has noisy output so it should only be printed if there are failures.
            with redirect_stdout(f):
                result = test_module.run()
            if result is None:
                sp.text = "Running Tests: No tests found."
                sp.ok(printer.safe_string("✅"))
                return 0
            elif result != 0:
                # Only display output for test failures.
                test_output = f.getvalue()
                sp.text = "Running Tests: Tests failed :("
                sp.fail(printer.safe_string("⛔")),
                printer.safe_print(test_output, file=sys.stderr)
                return result
            else:
                sp.text = "Running Tests: Tests passed!"
                sp.ok(printer.safe_string("✅"))
                return 0


def run_tests(args):
    if maybe_run_tests(args) != 0:
        sys.exit(1)


def run_engine(args, apply: bool = False, destroy=False, upgrade_all=False) -> TectonStateUpdateMetrics:
    check_version()

    # Resolve the json_out_filename prior to running `prepare_args(...)` so
    # that relative directories in the file name are supported (`prepare_args`
    # changes the working directory).
    json_out_path = None
    if args.json_out:
        json_out_path = Path(args.json_out).resolve()

    if destroy:
        top_level_objects: List[Fco] = []
        repo_root = None
        repo_files: List[Path] = []
    else:
        top_level_objects, repo_root, repo_files = prepare_args(args)

    if not args.skip_tests:
        run_tests(args)

    return update_tecton_state(
        objects=top_level_objects,
        apply=apply,
        debug=args.debug,
        interactive=not args.no_safety_checks,
        repo_files=repo_files,
        repo_root=repo_root,
        upgrade_all=upgrade_all,
        json_out_path=json_out_path,
    )


def write_hooks():
    hook_dir = ".tecton/hooks"
    os.makedirs(hook_dir)
    hook_file = hook_dir + "/plan.py"
    with open(hook_file, "wt") as f:
        f.write(hook_template.PLAN_TEMPLATE)
    os.chmod(hook_file, 0o755)
    printer.safe_print("✅ .tecton directory created", file=sys.stderr)


def init(args) -> None:
    init_feature_repo(reset_hooks=args.reset_hooks)


def init_feature_repo(reset_hooks=False) -> None:
    if Path().resolve() == Path.home():
        printer.safe_print("You cannot set feature repository root to the home directory", file=sys.stderr)
        sys.exit(1)

    # If .tecton exists in a parent or child directory, error out.
    repo_root = repo_file_handler._maybe_get_repo_root()
    if repo_root not in [Path().resolve(), None]:
        printer.safe_print(".tecton already exists in a parent directory:", repo_root)
        sys.exit(1)

    child_dir_matches = list(Path().rglob("*/.tecton"))
    if len(child_dir_matches) > 0:
        dirs_str = "\n\t".join(map(lambda c: str(c.parent.resolve()), child_dir_matches))
        printer.safe_print(f".tecton already exists in child directories:\n\t{dirs_str}")
        sys.exit(1)

    # Delete everything under .tecton/ (or the .tecton file)
    # and recreate default example hooks.
    dot_tecton = Path(".tecton")
    if reset_hooks:
        if dot_tecton.exists():
            if dot_tecton.is_dir():
                shutil.rmtree(dot_tecton)
            else:
                dot_tecton.unlink()

    if not dot_tecton.exists():
        write_hooks()
        printer.safe_print("Local feature repository root set to", Path().resolve(), "\n", file=sys.stderr)
        printer.safe_print(
            "💡 We recommend tracking the contents of this directory in git:", Path(".tecton").resolve(), file=sys.stderr
        )
        printer.safe_print(
            "💡 Run `tecton apply` to apply the feature repository to the Tecton cluster.", file=sys.stderr
        )
    elif not dot_tecton.is_dir():
        dot_tecton.unlink()
        write_hooks()
        printer.safe_print(
            "Plan Hooks configured! See https://docs.tecton.ai/v2/examples/using-plan-hooks.html for more info.",
            file=sys.stderr,
        )
    else:
        printer.safe_print("Feature repository is already set to", Path().resolve(), file=sys.stderr)


def restore(args):
    # Get the repo download URL from the metadata service.
    r = GetRestoreInfoRequest()
    r.workspace = common.get_current_workspace()
    if args.commit:
        r.commit_id = args.commit
    response = metadata_service.instance().GetRestoreInfo(r)

    # Download the repo.
    url = response.signed_url_for_repo_download
    commit_id = response.commit_id
    sdk_version = response.sdk_version
    # TODO: always print this message once enough customers are on new sdk versions
    sdk_version_msg = f"applied by SDK version {sdk_version}" if sdk_version else ""
    printer.safe_print(f"Restoring from commit {commit_id} {sdk_version_msg}")
    try:
        tar_response = requests.get(url)
        tar_response.raise_for_status()
    except requests.RequestException as e:
        raise SystemExit(e)

    # Find the repo root or initialize a default repot if not in a repo.
    root = repo_file_handler._maybe_get_repo_root()
    if not root:
        init_feature_repo()
        root = Path().resolve()
    repo_file_handler.ensure_prepare_repo()

    # Get user confirmation.
    repo_files = repo_file_handler.repo_files()
    if len(repo_files) > 0:
        for f in repo_files:
            printer.safe_print(f)
        confirm_or_exit("This operation may delete or modify the above files. Ok?")
        for f in repo_files:
            os.remove(f)

    # Extract the feature repo.
    with tarfile.open(fileobj=io.BytesIO(tar_response.content), mode="r|gz") as tar:
        for entry in tar:
            if os.path.isabs(entry.name) or ".." in entry.name:
                raise ValueError("Illegal tar archive entry")
            elif os.path.exists(root / Path(entry.name)):
                raise ValueError(f"tecton restore would overwrite an unexpected file: {entry.name}")
            tar.extract(entry, path=root)
    printer.safe_print("Success")


def log(args):
    logRequest = GetStateUpdateLogRequest()
    logRequest.workspace = common.get_current_workspace()
    # default to readable number
    logRequest.limit = args.limit
    response = metadata_service.instance().GetStateUpdateLog(logRequest)
    for entry in response.entries:
        printer.safe_print(f"Commit:\t{entry.commit_id}")
        printer.safe_print(f"Author:\t{entry.applied_by}")
        printer.safe_print(f"Date:\t{entry.applied_at.ToDatetime()}")
        printer.safe_print()


def _cluster_url() -> Optional[str]:
    from tecton import conf

    api_service = conf.get_or_none("API_SERVICE")
    if api_service:
        # API_SERVICE URLs of the form <subdomain>.tecton.ai/api are expected so this check
        # ensures an internal DNS address isn't being used or an invalid path is specified.
        if api_service.endswith("/api") and "ingress" not in api_service:
            return api_service[: -len("/api")]
        else:
            printer.safe_print(f"Warning: CLI is configured with non-standard URL: {api_service}", file=sys.stderr)
            return None
    else:
        return None


def login(args):
    from urllib.parse import urlparse, urljoin
    from tecton import conf

    host = _cluster_url()

    if args.tecton_url is None:
        printer.safe_print("Enter configuration. Press enter to use current value")
        prompt = "Tecton Cluster URL [%s]: " % (host or "no current value. example: https://yourco.tecton.ai")
        new_host = input(prompt).strip()
        if new_host:
            host = new_host
    else:
        host = args.tecton_url
    try:
        urlparse(host)
    except:
        printer.safe_print("Tecton Cluster URL must be a valid URL")
        sys.exit(1)
    # add this check for now since it can be hard to debug if you don't specify https and API_SERVICE fails
    if host is None or not (host.startswith("https://") or host.startswith("http://localhost:")):
        if host is not None and "//" not in host:
            host = f"https://{host}"
        else:
            printer.safe_print("Tecton Cluster URL must start with https://")
            sys.exit(1)

    # find the cli's client id
    okta_config_url = urljoin(host, "app/okta-config.json")

    try:
        response = requests.get(okta_config_url)
        response.raise_for_status()
    except requests.RequestException as e:
        raise SystemExit(e)
    cli_client_id = response.json()["OKTA_CLI_CLIENT_ID"]
    conf.set("CLI_CLIENT_ID", cli_client_id)

    flow = OktaAuthorizationFlow(hands_free=not args.manual)
    auth_code, code_verifier, redirect_uri = flow.get_authorization_code()
    access_token, _, refresh_token, access_token_expiration = flow.get_tokens(auth_code, code_verifier, redirect_uri)
    if not access_token:
        printer.safe_print("Unable to obtain Tecton credentials")
        sys.exit(1)

    conf.set("API_SERVICE", urljoin(host, "api"))
    # FEATURE_SERVICE and API_SERVICE are expected to have the same base URI: <host>/api
    conf.set("FEATURE_SERVICE", conf.get_or_none("API_SERVICE"))
    conf.set("CLI_CLIENT_ID", cli_client_id)
    conf.set("OAUTH_ACCESS_TOKEN", access_token)
    if refresh_token is not None:
        conf.set("OAUTH_REFRESH_TOKEN", refresh_token)
    conf.set("OAUTH_ACCESS_TOKEN_EXPIRATION", access_token_expiration)

    conf._save_tecton_config()
    conf._save_token(access_token, access_token_expiration, refresh_token)
    printer.safe_print(f"✅ Updated configuration at {conf._LOCAL_TECTON_CONFIG_FILE}")


def freshness_state():
    # TODO: use GetAllFeatureFreshnessRequest once we implement Chronosphere based API.
    freshness_statuses = get_all_freshness(common.get_current_workspace())
    num_fvs = len(freshness_statuses)
    if num_fvs == 0:
        printer.safe_print("No Feature Views found in this workspace.")
        return

    printer.safe_print(format_freshness_table(freshness_statuses))


def materialization_status(args):
    # Fetch FeatureView
    fvRequest = GetFeatureViewRequest()
    fvRequest.version_specifier = args.name
    fvRequest.workspace = common.get_current_workspace()
    fvResponse = metadata_service.instance().GetFeatureView(fvRequest)
    if not fvResponse.HasField("feature_view"):
        printer.safe_print(f"Feature view '{args.name}' not found.")
        sys.exit(1)
    fv_id = fvResponse.feature_view.feature_view_id

    # Fetch Materialization Status
    statusRequest = GetMaterializationStatusRequest()
    statusRequest.feature_package_id.CopyFrom(fv_id)
    statusResponse = metadata_service.instance().GetMaterializationStatus(statusRequest)

    column_names, materialization_status_rows = format_materialization_attempts(
        statusResponse.materialization_status.materialization_attempts,
        verbose=args.verbose,
        limit=args.limit,
        errors_only=args.errors_only,
    )

    printer.safe_print("All the displayed times are in UTC time zone")

    # Setting `max_width=0` creates a table with an unlimited width.
    table = Displayable.from_items(headings=column_names, items=materialization_status_rows, max_width=0)
    # Align columns in the middle horizontally
    table._text_table.set_cols_align(["c" for _ in range(len(column_names))])
    printer.safe_print(table)


COMMANDS = [
    Command(
        "api-key",
        description="Interact with Tecton readonly api-keys.",
        uses_workspace=False,
        requires_auth=True,
        handler=lambda args: api_key.run_api_key_command(args),
    ),
    Command(
        "init",
        description="Initialize feature repo.",
        uses_workspace=False,
        requires_auth=True,
        handler=lambda args: init(args),
    ),
    Command(
        "plan",
        description="Compare your local feature definitions with remote state and *show* the plan to bring them in sync.",
        uses_workspace=True,
        requires_auth=True,
        handler=lambda args: run_engine(args, apply=False),
    ),
    Command(
        "apply",
        description="Compare your local feature definitions with remote state and *apply* local changes to the remote.",
        uses_workspace=True,
        requires_auth=True,
        handler=lambda args: run_engine(args, apply=True),
    ),
    Command(
        "test",
        description="[BETA] Run plan hook tests.",
        uses_workspace=True,
        requires_auth=True,
        handler=lambda args: run_tests(args),
    ),
    Command(
        "upgrade",
        description="Upgrade remote feature definitions.",
        uses_workspace=True,
        requires_auth=True,
        handler=lambda args: run_engine(args, apply=True, upgrade_all=True),
    ),
    Command(
        "login",
        description="Log in and authenticate Tecton CLI.",
        uses_workspace=False,
        requires_auth=False,
        handler=lambda args: login(args),
    ),
    Command(
        "workspace",
        description="Manipulate a tecton workspace.",
        uses_workspace=False,
        requires_auth=True,
        handler=lambda args: workspace.run_workspace_command(args),
    ),
    Command(
        "restore",
        description="Restore feature repo state to that of past `tecton apply`.",
        uses_workspace=True,
        requires_auth=True,
        handler=lambda args: restore(args),
    ),
    Command(
        "log",
        description="View log of past `tecton apply`.",
        uses_workspace=True,
        requires_auth=True,
        handler=lambda args: log(args),
    ),
    Command(
        "destroy",
        description="Destroy all objects on the server side.",
        uses_workspace=True,
        requires_auth=True,
        handler=lambda args: run_engine(args, destroy=True, apply=True),
    ),
    Command(
        "version",
        description="Print version.",
        uses_workspace=False,
        requires_auth=False,
        handler=lambda args: tecton.version.summary(),
    ),
    Command(
        "dump",
        description="Print debug info.",
        uses_workspace=False,
        requires_auth=True,
        handler=lambda args: debug_dump(args),
    ),
    Command(
        "freshness",
        description="Show cluster-wide feature freshness states.",
        uses_workspace=False,
        requires_auth=True,
        handler=lambda args: freshness_state(),
    ),
    Command(
        "materialization-status",
        description="Show materialization status information for a FeatureView in the 'prod' workspace. Prepend the verbose flag for more information.",
        uses_workspace=False,
        requires_auth=True,
        handler=lambda args: materialization_status(args),
    ),
]


def _get_cli_commands_string():
    output = "\ncommands:"
    for c in sorted(COMMANDS, key=lambda x: x.command):
        if c.command == "workspace":
            for w in sorted(workspace.COMMANDS, key=lambda x: x.command):
                cmd = "workspace " + w.command
                output += f"\n  {cmd: <22} {w.description}"
        elif c.command == "api-key":
            for w in sorted(api_key.COMMANDS, key=lambda x: x.command):
                cmd = "api-key " + w.command
                output += f"\n  {cmd: <22} {w.description}"
        # hide help descriptions for internal-use commands
        elif c.command not in ("dump", "upgrade"):
            output += f"\n  {c.command: <22} {c.description}"
    return output


def main() -> None:
    # add cwd to path
    from tecton_spark.logger import set_logging_level
    import logging

    set_logging_level(logging.ERROR)
    sdk_decorators.disable_sdk_public_method_decorator()

    sys.path.append("")

    parser = argparse.ArgumentParser(
        description="Tecton command-line tool.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=_get_cli_commands_string(),
    )
    command_parsers = parser.add_subparsers(metavar="CMD", help="Command")

    cli_commands = [c for c in COMMANDS]

    for c in cli_commands:
        p = command_parsers.add_parser(c.command, description=c.description)
        p.set_defaults(command=c.command)
        if c.command == "init":
            p.add_argument(
                "--reset-hooks",
                action="store_true",
                default=False,
                help="Delete and recreate default hooks under .tecton/.",
            )
        if c.command == "login":
            p.add_argument(
                "tecton_url",
                nargs="?",
                default=None,
                help="Url of tecton web-ui: example `https://customer.tecton.ai`.",
            )
            p.add_argument(
                "--manual",
                action="store_true",
                default=False,
                help="Manually require user to open browser and paste login token. Needed when using the Tecton CLI in a headless environment.",
            )
        if c.command == "restore":
            p.add_argument("commit", nargs="?", default=None, help="Commit to restore to. Defaults to latest.")
        if c.command in ("plan", "apply", "destroy", "upgrade"):
            p.add_argument("--skip-tests", action="store_true", default=False)
            p.add_argument(
                "--no-safety-checks", action="store_true", default=False, help="Disable interactive safety checks."
            )
            p.add_argument(
                "--json-out",
                default="",
                type=str,
                help="[BETA][not stable] Output the tecton state update diff (as JSON) to the file path provided.",
            )
        if c.command == "workspace":
            workspace.build_parser(p)
        if c.command == "log":
            p.add_argument("--limit", default=10, type=int, help="Number of log entries to return.")
        if c.command == "api-key":
            api_key.build_parser(p)
        if c.command == "materialization-status":
            p.add_argument("name", help="Name of the FeatureView to lookup.")
            p.add_argument("--limit", default=100, type=int, help="Set the maximum limit of results.")
            p.add_argument(
                "--errors-only", dest="errors_only", default=False, action="store_true", help="Only show errors."
            )

    parser.add_argument("--verbose", action="store_true", default=False, help="Be verbose.")
    parser.add_argument("--debug", action="store_true", default=False, help="Enable debug info.")

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()
    try:
        for c in COMMANDS:
            if args.command == c.command:
                host = _cluster_url()
                cluster_configured = host is not None
                # Do not try logging events if cluster has never be configured or if user is trying to log in,
                # otherwise the CLI either won't be able to find the MDS or auth token might have expired
                if cluster_configured:
                    if c.uses_workspace:
                        printer.safe_print(f'Using workspace "{common.get_current_workspace()}" on cluster {host}')
                    start_time = pendulum.now("UTC")
                    state_update_event = c.handler(args)
                    execution_time = pendulum.now("UTC") - start_time
                    if c.requires_auth:
                        if state_update_event:
                            analytics.log_cli_event(c.command, execution_time, state_update_event)
                            if state_update_event.error_message:
                                sys.exit(1)
                        else:
                            analytics.log_cli_event(c.command, execution_time)
                elif not c.requires_auth:
                    # Do not try executing anything besides unauthenticated commnds (`login`, `version`) when cluster hasn't been configured.
                    c.handler(args)
                else:
                    printer.safe_print(
                        f"`tecton {c.command}` requires authentication. Please authenticate using `tecton login`."
                    )
                    sys.exit(1)
                break
        else:
            printer.safe_print("Unknown command", args.command.strip(), file=sys.stderr)
            sys.exit(1)
    finally:
        metadata_service.close_instance()


if __name__ == "__main__":
    main()
