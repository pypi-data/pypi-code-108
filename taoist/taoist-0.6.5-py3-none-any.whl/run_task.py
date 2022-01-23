"""run_task.py"""

from argparse import ArgumentParser
from tabulate import tabulate
from termcolor import colored
from todoist_api_python.api_async import TodoistAPIAsync
from taoist.read_project_dict import read_project_dict
from taoist.read_label_dict import read_label_dict
from taoist.parent_project import parent_project


async def run_task(args: ArgumentParser) -> None:
    """
    Run the task command
    """

    # Read config and project list
    api, project_dict = await read_project_dict()

    # Read label list into dictionary
    label_dict = await read_label_dict(api)

    # Process subcommand
    if args.subcommand == "list":
        try:
            tasks = await api.get_tasks()
        except Exception as error:
            raise error
        table_header = ["id", "content", "project", "status", "due", "labels"]
        task_list = []
        for task in tasks:
            label_list = []
            status = "Done" if task.completed else "Open"
            pass_label_filter = False if args.label_id else True
            pass_project_filter = False if args.project_id else True
            if pass_project_filter == False and task.project_id == args.project_id:
                pass_project_filter = True
            for lab in task.label_ids:
                if pass_label_filter == False and lab == args.label_id:
                    pass_label_filter = True
                label_list.append(label_dict[lab].name) 
            label_string = ','.join(label_list)
            if task.due:
                due_date = task.due.date
            else:
                due_date = ""
            project_path_string = parent_project(task.project_id, project_dict)
            if pass_label_filter and pass_project_filter:
                row = [
                    task.id,
                    colored(task.content, 'white', attrs=['bold']),
                    project_path_string,
                    status,
                    due_date,
                    label_string
                ]
                task_list.append(row)
        task_list.sort(key=lambda x: x[4])
        print(tabulate(task_list, headers=table_header))
    elif args.subcommand == "delete":
        task_id = args.task_id if args.task_id else int(input("Enter task ID: "))
        try:
            is_success = await api.delete_task(task_id=task_id)
        except Exception as error:
            raise error
        if is_success:
            print(f"Successfully deleted task {task_id}")
    elif args.subcommand == "done":
        task_id = args.task_id if args.task_id else int(input("Enter task ID: "))
        try:
            is_success = await api.close_task(task_id=task_id)
        except Exception as error:
            raise error
        if is_success:
            print(f"Successfully marked task {task_id} as done")
    elif args.subcommand == "view":
        task_id = args.task_id if args.task_id else int(input("Enter task ID: "))
        view_list = []
        try:
            task = await api.get_task(task_id=task_id)
        except Exception as error:
            raise error
        task_dict = task.to_dict()
        view_list.append(["Name", task_dict['content']])
        project_path_string = parent_project(task.project_id, project_dict)
        view_list.append(["Project", project_path_string])
        due_dict = task_dict['due']
        if due_dict:
            view_list.append(["Due", due_dict['date']])
            view_list.append(["Recurring", due_dict['recurring']])
        view_list.append(["Priority", task_dict['priority']])
        label_list = []
        for lab in task_dict['label_ids']:
            label_list.append(label_dict[lab].name)
        if len(label_list) > 0:
            label_string = ','.join(label_list)
            view_list.append(["Labels", label_string])
        print(tabulate(view_list))
    elif args.subcommand == "label":
        task_id = args.task_id if args.task_id else int(input("Enter task ID: "))
        label_id = args.label_id if args.label_id else int(input("Enter label ID: "))
        try:
            task = await api.get_task(task_id=task_id)
        except Exception as error:
            raise error
        new_list = task.label_ids
        new_list.append(label_id)
        try:
            is_success = await api.update_task(task_id=task_id, label_ids=new_list)
        except Exception as error:
            raise error
        if is_success:
            print(f"Successfully added label {label_id} to task {task_id}")
    elif args.subcommand == "create":
        task_name = args.task_name if args.task_name else input("Enter task name: ")
        for key, val in project_dict.items():
            if val.name == args.project_name:
                project_id = key
        try:
            task = await api.add_task(
                content=task_name,
                due_string=args.due,
                project_id=project_id,
                due_lang='en',
                priority=args.priority,
            )
        except Exception as error:
            raise error
        print(f"Successfully created task \"{task_name}\"")
