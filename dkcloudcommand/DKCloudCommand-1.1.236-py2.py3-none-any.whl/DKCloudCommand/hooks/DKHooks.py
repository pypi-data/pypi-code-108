import json
import os
import string
import subprocess
import sys

from DKCloudCommand.modules.DKFileHelper import DKFileHelper
from jinja2 import Template
from jinja2.exceptions import TemplateSyntaxError


def check_json(path: str) -> None:
    content = DKFileHelper.read_file(path)
    sub_dict = {}
    t = Template(content)
    fs = t.render(sub_dict)
    template = string.Template(fs)
    it = template.safe_substitute(sub_dict)
    json.loads(it)


def check_text_file(path: str) -> None:
    content = DKFileHelper.read_file(path)
    sub_dict = {}
    t = Template(content)
    fs = t.render(sub_dict)
    template = string.Template(fs)
    it = template.safe_substitute(sub_dict)


def check_file(basepath: str, path: str) -> bool:
    msg = "Checking " + path

    sys.stdout.write(msg)

    error = None

    try:
        extension = path.split(".")[-1]
        full_path = os.path.join(basepath, path)

        if extension == "json":
            check_json(full_path)
        elif extension in ["txt", "html", "sql", "ktr"]:
            check_text_file(full_path)

    except TemplateSyntaxError as e:
        error = f"Error validating Jinja expresions in file {path} at line {e.lineno}: {e}"
    except ValueError as e:
        error = f"Error validating JSON file {path}: {e}"

    DKFileHelper.write_file(sys.stdout, " " * max(1, 70 - len(msg)))

    print("\033[32mOK\033[39m" if not error else "\033[31mFailed\033[39m")

    if error:
        print(error)

    return error is None


def do_pre_commit() -> None:
    output = subprocess.check_output(["git", "rev-parse", "--verify", "HEAD"])

    head = output.strip()

    diff = subprocess.check_output(["git", "diff-index", "--name-only", "--cached", head])

    success = True

    diff = diff.strip()

    if len(diff) > 0:
        for change in diff.strip().split("\n"):
            if not check_file(os.getcwd(), change):
                success = False

        if not success:
            sys.exit(1)


if __name__ == "__main__":
    option = sys.argv[1].split("/")[-1]

    if option == "pre-commit":
        do_pre_commit()
