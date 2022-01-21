import sys
from dataclasses import dataclass
from typing import Callable

from colorama import Fore

from tecton import conf
from tecton import Workspace
from tecton._internals import metadata_service
from tecton._internals.utils import is_live_workspace
from tecton._internals.workspace_utils import PROD_WORKSPACE_NAME_CLIENT
from tecton.cli import printer
from tecton.cli.common import get_current_workspace
from tecton.cli.engine import update_tecton_state
from tecton_proto.metadataservice.metadata_service_pb2 import CreateWorkspaceRequest
from tecton_proto.metadataservice.metadata_service_pb2 import DeleteWorkspaceRequest
from tecton_proto.metadataservice.metadata_service_pb2 import GetWorkspaceRequest
from tecton_proto.metadataservice.metadata_service_pb2 import ListWorkspacesRequest


@dataclass
class WorkspaceCommand:
    command: str
    description: str
    handler: Callable


def command_select(args):
    # validate
    workspace_names = {w.name for w in list_workspaces()}
    if args.workspace not in workspace_names:
        printer.safe_print(
            f'Workspace "{args.workspace}" not found. Run `tecton workspace list` to see list of available workspaces.'
        )
        sys.exit(1)

    switch_to_workspace(args.workspace)


def command_list():
    current_workspace = get_current_workspace()
    workspaces = list_workspaces()
    materializable = [w.name for w in workspaces if w.capabilities.materializable]
    nonmaterializable = [w.name for w in workspaces if not w.capabilities.materializable]

    if materializable:
        printer.safe_print("Live Workspaces:")
        for name in materializable:
            marker = "*" if name == current_workspace else " "
            printer.safe_print(f"{marker} {name}")

    # Print whitespace between the two sections if needed.
    if materializable and nonmaterializable:
        printer.safe_print()

    if nonmaterializable:
        printer.safe_print("Development Workspaces:")
        for name in nonmaterializable:
            marker = "*" if name == current_workspace else " "
            printer.safe_print(f"{marker} {name}")


def command_show():
    workspace_name = get_current_workspace()
    workspace = get_workspace(workspace_name)
    workspace_type = "Live" if workspace.capabilities.materializable else "Development"
    printer.safe_print(f"{workspace_name} ({workspace_type})")


def command_create(args):
    # There is a check for this on the server side too, but we optimistically validate
    # here as well to show a pretty error message.
    workspace_names = {w.name for w in list_workspaces()}
    if args.workspace in workspace_names:
        printer.safe_print(f"Workspace {args.workspace} already exists", file=sys.stderr)
        sys.exit(1)

    # create
    create_workspace(args.workspace, args.live)

    # switch to new workspace
    switch_to_workspace(args.workspace)
    printer.safe_print(
        """
You're now on a new, empty workspace. Workspaces isolate their state,
so if you run "tecton plan" Tecton will not see any existing state
for this configuration.
    """
    )


def command_delete(args):
    # validate
    if args.workspace == PROD_WORKSPACE_NAME_CLIENT:
        printer.safe_print(f"Deleting workspace '{PROD_WORKSPACE_NAME_CLIENT}' not allowed.")
        sys.exit(1)

    is_live = is_live_workspace(args.workspace)

    # confirm deletion
    confirmation = "y" if args.yes else None
    while confirmation not in ("y", "n", ""):
        confirmation_text = f'Are you sure you want to delete the workspace "{args.workspace}"? (y/N)'
        if is_live:
            confirmation_text = f"{Fore.RED}Warning{Fore.RESET}: This will delete any materialized data in this workspace.\n{confirmation_text}"
        confirmation = input(confirmation_text).lower().strip()
    if confirmation == "n" or confirmation == "":
        printer.safe_print("Cancelling delete action.")
        sys.exit(1)

    # archive all fcos in the remote state unconditionally.
    # This will need to be updated when workspaces support materialization.
    with Workspace(args.workspace):
        update_tecton_state(
            objects=[],
            repo_root="",
            repo_files=[],
            apply=True,
            interactive=is_live,
            debug=False,
            upgrade_all=False,
        )

    # delete
    delete_workspace(args.workspace)

    # switch to prod if deleted current
    if args.workspace == get_current_workspace():
        switch_to_workspace(PROD_WORKSPACE_NAME_CLIENT)


COMMANDS = [
    WorkspaceCommand("show", description="Show active workspace.", handler=lambda args: command_show()),
    WorkspaceCommand("create", description="Create a new workspace.", handler=lambda args: command_create(args)),
    WorkspaceCommand("select", description="Select a workspace.", handler=lambda args: command_select(args)),
    WorkspaceCommand("list", description="List available workspaces.", handler=lambda args: command_list()),
    WorkspaceCommand("delete", description="Delete workspace.", handler=lambda args: command_delete(args)),
]


def switch_to_workspace(workspace_name: str):
    conf.set("TECTON_WORKSPACE", workspace_name)
    conf._save_tecton_config()
    printer.safe_print(f'Switched to workspace "{workspace_name}".')


def create_workspace(workspace_name: str, materializable: bool):
    request = CreateWorkspaceRequest()
    request.workspace_name = workspace_name
    request.capabilities.materializable = materializable
    metadata_service.instance().CreateWorkspace(request)
    printer.safe_print(f'Created workspace "{workspace_name}".')


def delete_workspace(workspace_name: str):
    with Workspace(workspace_name):
        request = DeleteWorkspaceRequest()
        request.workspace = workspace_name
        metadata_service.instance().DeleteWorkspace(request)
    printer.safe_print(f'Deleted workspace "{workspace_name}".')


def get_workspace(workspace_name: str):
    request = GetWorkspaceRequest()
    request.workspace_name = workspace_name
    response = metadata_service.instance().GetWorkspace(request)
    return response.workspace


def list_workspaces():
    request = ListWorkspacesRequest()
    response = metadata_service.instance().ListWorkspaces(request)
    return response.workspaces


def run_workspace_command(args):
    for command in COMMANDS:
        if args.workspace_command == command.command:
            command.handler(args)
            break
    else:
        printer.safe_print(args)
        printer.safe_print("Unknown command", args.command.strip(), file=sys.stderr)
        sys.exit(1)


def build_parser(root_parser):
    workspace_parsers = root_parser.add_subparsers(dest="workspace_command", help="List of workspace commands.")
    workspace_parsers.required = True

    for c in COMMANDS:
        p = workspace_parsers.add_parser(c.command, help=c.description)
        if c.command in {"select", "delete", "create"}:
            p.add_argument("workspace", help="Workspace name.")
        if c.command == "create":
            # Keeping "--automatic-materialization-enabled" around for backwards compatibility
            p.add_argument(
                "--live",
                "--automatic-materialization-enabled",
                action="store_true",
                help="Create a live workspace, which enables materialization and online serving.",
            )
        if c.command == "delete":
            p.add_argument("-y", "--yes", action="store_true")
