"""run_section.py"""

from argparse import ArgumentParser
from tabulate import tabulate
from termcolor import colored
from todoist_api_python.api_async import TodoistAPIAsync
from taoist.read_project_dict import read_project_dict
from taoist.parent_project import parent_project


async def run_section(args: ArgumentParser) -> None:
    """
    Run the section command
    """

    # Read config and project list
    config, project_dict = await read_project_dict()

    # Initialize Todoist API
    api = TodoistAPIAsync(config['Default']['token'])

    # Process subcommand
    if args.subcommand == "list":
        project_id = args.project_id if args.project_id else int(input("Enter project ID: "))
        try:
            sections = await api.get_sections(project_id=project_id)
        except Exception as error:
            raise error
        project_path_string = parent_project(project_id, project_dict)
        table_header = ["id", "name", "project"]
        section_list = []
        for section in sections:
            row = [
                section.id,
                colored(section.name, 'white', attrs=['bold']),
                project_path_string
            ]
            section_list.append(row)
        print(tabulate(section_list, headers=table_header))
    elif args.subcommand == "create":
        section_name = args.section_name if args.section_name else input("Enter new section name: ")
        project_id = args.project_id if args.project_id else int(input("Enter project ID: "))
        project_name = project_dict[project_id].name
        try:
            section = await api.add_section(name=section_name, project_id=project_id)
        except Exception as error:
            raise error
        print(f"Successfully added section \"{section_name}\" to project \"{project_name}\"")
    elif args.subcommand == "delete":
        section_id = args.section_id if args.section_id else int(input("Enter section ID: "))
        try:
            is_success = await api.delete_section(section_id=section_id)
        except Exception as error:
            raise error
        if is_success:
            print(f"Successfully deleted section {section_id}")  