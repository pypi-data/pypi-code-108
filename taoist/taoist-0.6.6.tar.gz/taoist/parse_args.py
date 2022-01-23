"""parse_args.py"""

import sys
import argparse

from taoist import __version__

def parse_args() -> argparse.ArgumentParser:
    """
    Parse arguments for taoist program
    """

    # Define main parser
    parser = argparse.ArgumentParser(
        prog="taoist", description="Python-based Terminal Utility for Todoist"
    )

    parser.add_argument("--version", action="version", version=__version__)

    # Define main subparser
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Define parser for init command
    init_parser = subparsers.add_parser("init", help="authenticate to Todoist API")
    init_parser.add_argument(
        "--token",
        action="store",
        metavar="STR",
        type=str,
        help="Todoist user account API token",
    )

    # Define parser for project command
    project_parser = subparsers.add_parser(
        "project", help="project-related functions"
    )

    # Add project subcommand parser
    project_subparser = project_parser.add_subparsers(dest="subcommand", help="subcommands")

    # Parse project/list
    project_list_subparser = project_subparser.add_parser("list", help="list projects")
 
    # Parse project/create
    project_create_subparser = project_subparser.add_parser("create", help="create new project")
    project_create_subparser.add_argument(
        "--name",
        dest="project_name",
        action="store",
        metavar="STR",
        type=str,
        help="name of new project to create",
    )

    # Parse project/delete
    project_delete_subparser = project_subparser.add_parser("delete", help="delete existing project")
    project_delete_subparser.add_argument(
        "--project-id",
        dest="project_id",
        action="store",
        metavar="INT",
        type=int,
        help="id of project to delete",
    )

    # Define parser for task command
    task_parser = subparsers.add_parser(
        "task", help="task-related functions"
    )

    # Add task subcommand parser
    task_subparser = task_parser.add_subparsers(dest="subcommand", help="subcommands")

    # Parse task/list
    task_list_subparser = task_subparser.add_parser("list", help="list active tasks")
    task_list_subparser.add_argument(
        "--label-id",
        dest="label_id",
        action="store",
        metavar="INT",
        type=int,
        help="list only task with given label ID",
    )
    task_list_subparser.add_argument(
        "--project-id",
        dest="project_id",
        action="store",
        metavar="INT",
        type=int,
        help="list only task from a given project",
    )

    # Parse task/view
    task_view_subparser = task_subparser.add_parser("view", help="view task details")
    task_view_subparser.add_argument(
        "--task-id",
        dest="task_id",
        action="store",
        metavar="INT",
        type=int,
        help="view task details",
    )

    # Parse task/create
    task_create_subparser = task_subparser.add_parser("create", help="create new task")
    task_create_subparser.add_argument(
        "--name",
        dest="task_name",
        action="store",
        metavar="STR",
        type=str,
        help="task name",
    )

    task_create_subparser.add_argument(
        "--due",
        action="store",
        metavar="STR",
        type=str,
        default="Tomorrow",
        help="human language describing due date [default: %(default)s]",
    )

    task_create_subparser.add_argument(
        "--project-name",
        dest="project_name",
        action="store",
        metavar="STR",
        type=str,
        default="Inbox",
        help="name of project in which to create new task [default: %(default)s]",
    )

    task_create_subparser.add_argument(
        "--priority",
        action="store",
        metavar="INT",
        type=int,
        choices=[1, 2, 3, 4],
        default=1,
        help="priority level 1-4 [default: %(default)s]",
    )

    # Parse task/delete
    task_delete_subparser = task_subparser.add_parser("delete", help="delete existing task")
    task_delete_subparser.add_argument(
        "--task-id",
        dest="task_id",
        action="store",
        metavar="INT",
        type=int,
        help="delete task",
    )

    # Parse task/label
    task_label_subparser = task_subparser.add_parser("label", help="add label to existing task")
    task_label_subparser.add_argument(
        "--task-id",
        dest="task_id",
        action="store",
        metavar="INT",
        type=int,
        help="id of existing task to add label",
    )
    
    task_label_subparser.add_argument(
        "--label-id",
        dest="label_id",
        action="store",
        metavar="INT",
        type=int,
        help="id of label to add to task",
    )

    # Parse task/done
    task_done_subparser = task_subparser.add_parser("done", help="mark active task as done")
    task_done_subparser.add_argument(
        "--task-id",
        dest="task_id",
        action="store",
        metavar="INT",
        type=int,
        help="id of task to mark as done",
    )

    # Define parser for label command
    label_parser = subparsers.add_parser(
        "label", help="label-related functions"
    )

    # Add label subcommand parser
    label_subparser = label_parser.add_subparsers(dest="subcommand", help="subcommands")

    # Parse label/list
    label_list_subparser = label_subparser.add_parser("list", help="list existing labels")

    # Parse label/create
    label_create_subparser = label_subparser.add_parser("create", help="create new label")
    label_create_subparser.add_argument(
        "--name",
        dest="label_name",
        action="store",
        metavar="STR",
        type=str,
        help="name of new label to create",
    )

    # Parse label/delete
    label_delete_subparser = label_subparser.add_parser("delete", help="delete existing label")
    label_delete_subparser.add_argument(
        "--label-id",
        dest="label_id",
        action="store",
        metavar="INT",
        type=int,
        help="id of existing label to delete",
    )

    # Define parser for project command
    section_parser = subparsers.add_parser(
        "section", help="section-related functions"
    )

    # Add section subcommand parser
    section_subparser = section_parser.add_subparsers(dest="subcommand", help="subcommands")

    # Parse section/list
    section_list_subparser = section_subparser.add_parser("list", help="list sections")
    section_list_subparser.add_argument(
        "--project-id",
        dest="project_id",
        action="store",
        metavar="INT",
        type=int,
        help="id of project to list sections",
    )

    # Parse section/create
    section_create_subparser = section_subparser.add_parser("create", help="create new section")
    section_create_subparser.add_argument(
        "--project-id",
        dest="project_id",
        action="store",
        metavar="INT",
        type=int,
        help="id of project in which new section will be created",
    )

    section_create_subparser.add_argument(
        "--name",
        dest="section_name",
        action="store",
        metavar="STR",
        type=str,
        help="name of the new section",
    )

    # Parse section/delete
    section_delete_subparser = section_subparser.add_parser("delete", help="delete existing section")
    section_delete_subparser.add_argument(
        "--section-id",
        dest="section_id",
        action="store",
        metavar="INT",
        type=int,
        help="id of existing section to delete",
    )

    # Parse arguments
    return parser.parse_args(args=None if sys.argv[1:] else ["--help"])