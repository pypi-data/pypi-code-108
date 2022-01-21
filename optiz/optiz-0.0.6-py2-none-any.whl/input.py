from typing import Any, List
import os
from .constants import INPUT_DIR
from .utils import in_ipynb


def input_from_file(file, input_folder=INPUT_DIR):
    with open(os.path.join(input_folder, file), "r") as f:
        lines = f.readlines()

    def input():
        line = lines.pop(0)
        return line
    return input


def default_select_from_list(list, title="Select an item:"):
    """
    Select an item from a list.
    """
    if len(list) == 0:
        raise ValueError("List is empty")
    if len(list) == 1:
        return list[0]
    for i, item in enumerate(list):
        print(f"{i} - {item}")
    try:
        choice = input(f"{title} ")
    except KeyboardInterrupt:
        print("\nExiting...")
        exit()
    try:
        return list[int(choice)]
    except (ValueError, IndexError):
        raise ValueError(f"Invalid choice: {choice}")


def select_in_list(choices: List[Any], title="Select an item:"):
    if in_ipynb():
        return default_select_from_list(choices, title)
    else:
        import inquirer
        str_choices = list(map(str, choices))
        questions = [
            inquirer.List('value',
                          message=title,
                          choices=str_choices,
                          ),
        ]
        answers = inquirer.prompt(questions)
        return choices[str_choices.index(answers["value"])]


def select_input_instance(input_folder=INPUT_DIR):
    return select_in_list(os.listdir(input_folder), title="Select an input instance:")
