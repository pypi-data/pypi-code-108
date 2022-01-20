#!/usr/bin/env python
"""Create tasks for a project by looping input until the user quits."""
from prompt_toolkit.completion import FuzzyWordCompleter
from prompt_toolkit.shortcuts import prompt
from taskw import TaskWarrior


def get_projects(show_all=False):
    """Get a list of projects from taskwarrior."""
    w = TaskWarrior(
        config_filename="~/.config/task/taskrc"
    )  # pylint: disable=invalid-name
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
    project_completer = FuzzyWordCompleter(get_projects())
    text = prompt(
        "Which project? ", completer=project_completer, complete_while_typing=True
    )
    print(f"Project: {text}")


if __name__ == "__main__":
    main()
