import datetime
import os
import webbrowser
from pathlib import Path


def user_file(username: str, command: str, task_did: str) -> None:
    """[Used to save the history of the user]"""
    maxlength = 100
    with open((os.getcwd() + f"/resources/ {username}.elsa"), "a") as history:
        history.write(f"{'-' * maxlength}\n DATE{datetime.datetime.now()} USER INPUT: {command} OUTPUT: {task_did}\n{'-' * maxlength}\n\n")


def user_read(event = "", username: str = "dummy") -> None:
    """[Open the user history file]"""
    if not Path(userpth := (os.getcwd() + f"/resources/ {username}.elsa")).exists():
        userpth = os.getcwd() + "/resources/ dummy.elsa"
    webbrowser.open(userpth)


def clear_history(name: str) -> None:
    """[Clears the history of the user]"""
    with open((os.getcwd() + f"/resources/ {name}.elsa"), "w") as history: history.write("")
