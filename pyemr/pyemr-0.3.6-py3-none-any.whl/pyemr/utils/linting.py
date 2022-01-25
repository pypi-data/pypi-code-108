"""A collection of aws tools"""
import os
import string

import fire
from autocorrect import Speller, load_from_tar

from pyemr.utils.config import cprint
from pyemr.utils.sys import argskwargs_to_argv


CUSTOM_VOCAB = {
    "pyemr": 233895398,
    "PYEMR": 233895398,
    "aws": 233895398,
    "emr": 233895398,
    "EMR": 233895398,
    "docker": 233895398,
    "halcyon": 2123,
    "airflow": 233895398,
    "jupyter": 233895398,
    "stdout": 233895398,
    "stderr": 233895398,
    "Debug": 233895398,
    "venv": 233895398,
    "ssm": 233895398,
    "config": 233895398,
    "pyproject": 233895398,
    "stackoverflow": 233895398,
    "toml": 233895398,
    "init": 233895398,
    "target_cluster": 233895398,
    "TODO": 233895398,
    "todo": 233895398,
    "SPARK_HOME": 233895398,
    "pyspark": 233895398,
    "zsh": 233895398,
    "NOTE": 233895398,
}

ENCHANT_ADDITIONAL_VOCAB = [
    "monkeypatch",
    "url",
    "jupyter",
    "endswith",
    "subprocess",
    "os",
    "pytestconfig",
    "readscript",
    "venv",
    "Args",
    "str",
    "env",
    "config",
    "emr",
    "datetime",
    "bool",
    "args",
    "kwargs",
    "wr",
    "configs",
    "aws",
    "pyspark",
    "pwd",
    "cmd",
    "dockerfile",
    "ipykernel",
    "IPython",
    "sys",
    "sql",
    "Dataframe",
    "pyemr",
    "step_id",
    "DataFrame",
    "ssm",
    "toml",
    "pyproject",
    "awswrangler",
    "gitignore",
    "stdout",
    "stderr",
    "pypi",
    "formatter",
    "smm",
    "qa",
    "sys",
    "dev",
    "uid",
    "stdin",
    "stderr",
    "cwd",
    "pytestconfig",
]


def spell_check(path):
    """

    Args:
      path:

    Returns:

    """
    cprint(f"Spell checking '{path}'")
    print("")
    words = load_from_tar("en")
    words.update(CUSTOM_VOCAB)
    spell = Speller(nlp_data=words)
    code_open = False

    def get_spell_changes(text):
        """

        Args:
          text:

        Returns:

        """
        res = {}
        for word in text.split(" "):
            word = word.strip(string.punctuation)
            cword = spell(word)
            if word != cword and word not in CUSTOM_VOCAB:
                res[word] = cword

        return res

    with open(path) as file:
        for line in file:
            if line.count("```") % 2 == 1:
                code_open = not code_open
            if not code_open:
                original = line.strip()
                correct = spell(original)
                if correct != original:
                    corrections = get_spell_changes(original)
                    cprint("In: " + original, "FAIL")
                    cprint("\t Suggest: " + str(corrections), "OKGREEN")


def format_code():
    """Runs a series of python code format converts on the code in the working directory."""
    os.system("pyment --output=google --write .")

    os.system(
        "autoflake --in-place --remove-unused-variables --remove-all-unused-imports **/*.py",
    )
    os.system("autopep8 --in-place **/*.py")
    os.system("black .")
    os.system("isort .")
    os.system("brunette **/*.py")
    os.system("gray *")


PYLINT_MESSAGE_TYPES = ["R", "C", "E", "W"]


def lint_wd(spelling=False, *args, **kwargs):
    """Runs pylint on the pwd.

    Args:
      *args:
      **kwargs:
      spelling: (Default value = False)

    Returns:

    """
    if not spelling and "S" not in kwargs:
        cmd = [
            "pylint",
            "--ignore",
            "HOWTO.md,README.md,poetry.lock,pyproject.toml,pyemr/files/templates/airflow_spark_step.template.py",
        ]
        cmd += argskwargs_to_argv(args, kwargs)
        cmd += ["*"]
        os.system(" ".join(cmd).replace("--E", "-E"))
    else:
        cmd = ["pylint"]
        cmd += ["--disable", "all", "--enable", "spelling", "--spelling-dict", "en_US"]
        cmd += ["--spelling-ignore-words", ",".join(ENCHANT_ADDITIONAL_VOCAB)]
        cmd += ["*"]
        os.system(" ".join(cmd))


if __name__ == "__main__":
    fire.Fire(format_code)
