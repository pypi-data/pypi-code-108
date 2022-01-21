"""run_project.py"""
from argparse import ArgumentParser
from tabulate import tabulate
from todoist_api_python.api_async import TodoistAPIAsync
from taoist.read_project_dict import read_project_dict
from taoist.parent_project import parent_project

async def run_project(args: ArgumentParser) -> None:
    """
    Run project command
    """

    # Read config and project list
    config, project_dict = await read_project_dict()

    # Initialize Todoist API
    api = TodoistAPIAsync(config['Default']['token'])

    # Process subcommand
    if args.subcommand == "list":
        table_header = ["id", "name"]
        project_list = []
        for key in project_dict.keys():
            project_path_string = parent_project(key, project_dict) 
            row = [key, project_path_string]
            project_list.append(row)
        print(tabulate(project_list, headers=table_header))
    elif args.subcommand == "create":
        try:
            project = await api.add_project(name=args.project_name)
        except Exception as error:
            raise error
        print(f"Created project \"{args.project_name}\" with id {project.id}")
    elif args.subcommand == "delete":
        try:
            is_success = await api.delete_project(project_id=args.project_id)
        except Exception as error:
            raise error
        if is_success:
            print(f"Deleted project \"{project_dict[args.project_id].name}\"")   
