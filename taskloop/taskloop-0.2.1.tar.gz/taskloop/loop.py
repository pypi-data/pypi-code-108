#!/usr/bin/env python
"""Create tasks for a project by looping input until the user quits."""
import sys
from prompt_toolkit.completion import FuzzyWordCompleter
from prompt_toolkit.shortcuts import prompt
from taskw import TaskWarrior
from rich.console import Console


def get_projects(show_all=False):
    """Get a list of projects from taskwarrior."""
    w = TaskWarrior( # pylint: disable=invalid-name
        config_filename="~/.config/task/taskrc"
    )
    tasks = w.load_tasks()
    projects = []
    try:
        for task in tasks["pending"]:
            if task["project"] not in projects:
                projects.append(task["project"])
        if show_all:
            for task in tasks["completed"]:
                if task["project"] not in projects:
                    projects.append(task["project"])
    except KeyError:
        pass
    return projects

def main():
    """Main function."""
    # populate the autocomplete list from tasks
    project_completer = FuzzyWordCompleter(get_projects())
    project = prompt(
        "Which project? ", completer=project_completer, complete_while_typing=True
    )
    if project == "":
        # if the user hits enter, exit
        sys.exit(0)
    print(f"Project: {project}")

    task_text = None  #initialize var to None so while loop logic works
    while task_text != "":
        # Blank line will end input loop
        task_text = prompt("Task: ")
        if task_text != "":
            w = TaskWarrior( # pylint: disable=invalid-name
                config_filename="~/.config/task/taskrc"
            )
            if task_text.startswith("."):
                task_text = task_text[1:].lstrip()
                task = w.task_add(task_text, project=project, dep=task_id)
            else:
                task = w.task_add(task_text, project=project)
            task_id = task["id"]
    # This should be an option, but force sync for now
    task_sync = True
    if task_sync:
        console = Console()
        with console.status("Syncing tasks...", spinner="point"):
            w.sync()


if __name__ == "__main__":
    main()
