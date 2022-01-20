"""run_section.py"""
from argparse import ArgumentParser
from tabulate import tabulate
from taoist.read_project_dict import read_project_dict
from todoist_api_python.api_async import TodoistAPIAsync

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
        try:
            sections = await api.get_sections(project_id=args.project_id)
        except Exception as error:
            print(error)
        project = project_dict[args.project_id]
        project_path = [project.name]
        project_parent_id = project.parent_id
        while project_parent_id:
            project_parent = project_dict[project_parent_id]
            project_path = [project_parent.name] + project_path
            project_parent_id = project_parent.parent_id
        project_path_string = '/'.join(project_path)
        table_header = ["id", "name", "project"]
        section_list = []
        for section in sections:
            row = [section.id, section.name, project_path_string]
            section_list.append(row)
        print(tabulate(section_list, headers=table_header))
    elif args.subcommand == "create":
        try:
            section = await api.add_section(name=args.section_name, project_id=args.project_id)
            print(f"Added section {args.section_name}")
        except Exception as error:
            print(error)
    elif args.subcommand == "delete":
        try:
            is_success = await api.delete_section(section_id=args.section_id)
            if is_success:
                print(f"Deleted section {args.section_id}")
        except Exception as error:
            print(error)       