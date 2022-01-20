"""run_project.py"""
from argparse import ArgumentParser
from taoist.read_project_dict import read_project_dict
from tabulate import tabulate
from todoist_api_python.api_async import TodoistAPIAsync

async def run_project(args: ArgumentParser) -> None:
    """
    Run project command
    """

    # Read config and project list
    config, project_dict = await read_project_dict()

    # Process subcommand
    if args.subcommand == "list":
        table_header = ["id", "name"]
        project_list = []
        for key, project in project_dict.items():
            project_path = [project.name]
            project_parent_id = project.parent_id
            while project_parent_id:
                project_parent = project_dict[project_parent_id]
                project_path = [project_parent.name] + project_path
                project_parent_id = project_parent.parent_id
            project_path_string = '/'.join(project_path)
            row = [key, project_path_string]
            project_list.append(row)
        print(tabulate(project_list, headers=table_header))
    elif args.subcommand == "create":
        api = TodoistAPIAsync(config['Default']['token'])
        try:
            project = await api.add_project(name=args.project_name)
        except Exception as error:
            print(error)
    elif args.subcommand == "delete":
        api = TodoistAPIAsync(config['Default']['token'])
        try:
            is_success = await api.delete_project(project_id=args.project_id)
            if is_success:
                print(f"Deleted project {project_dict[args.project_id].name}")
        except Exception as error:
            print(error)        
