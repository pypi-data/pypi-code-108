from typing import Any, List
import inquirer
import os
from .constants import INPUT_DIR


def input_from_file(file, input_folder=INPUT_DIR):
    with open(os.path.join(input_folder, file), "r") as f:
        lines = f.readlines()

    def input():
        line = lines.pop(0)
        return line
    return input


def select_input_instance(input_folder=INPUT_DIR):
    questions = [
        inquirer.List("instance",
                      message="Which instance do you want to run?",
                      choices=os.listdir(input_folder),
                      ),
    ]
    answers = inquirer.prompt(questions)
    return answers["instance"]


def select_in_list(choices: List[Any], question: str):
    str_choices = list(map(str, choices))
    questions = [
        inquirer.List('value',
                      message=question,
                      choices=str_choices,
                      ),
    ]
    answers = inquirer.prompt(questions)
    return choices[str_choices.index(answers["value"])]
