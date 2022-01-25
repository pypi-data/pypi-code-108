"""Utility functions for the Templator."""

import glob
import importlib
import json
import os
import shutil
from collections import OrderedDict
from contextlib import contextmanager
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, Template
from loguru import logger

from pytemplator.constants import YES_SET
from pytemplator.exceptions import UserCancellationError


@contextmanager
def cd(new_dir):  # pylint: disable=invalid-name
    """Cd into the directory.

    Used as context manager to avoid side-effects if
    something goes wrong.
    See SO #24176022
    """
    previous_dir = os.getcwd()
    os.chdir(os.path.expanduser(new_dir))
    try:
        yield
    finally:
        os.chdir(previous_dir)


def is_yes(reply):
    """Handle human-readable replies."""
    if isinstance(reply, bool):
        return reply
    return reply.lower() in YES_SET


def import_module_from_path(path):
    """Import and execute a module in a safer way.

    Recipe taken from importlib doc at
    https://docs.python.org/3/library/importlib.html
    """
    path = Path(path).resolve(strict=True)
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def generate_context_from_json(json_file, context, no_input):
    """Generate the context from a json file.

    Same behavior as cookiecutter.
    """
    with open(json_file, encoding="UTF-8") as file:
        questions = json.load(file, object_pairs_hook=OrderedDict)
    for key, value in questions.items():
        question = key.replace("-", " ").replace("_", " ")
        default_value = Template(str(value)).render(context)
        if no_input:
            answer = default_value
        else:
            answer = input(f"{question} [{default_value}] ") or default_value
        context["pytemplator"][key] = context["cookiecutter"][key] = context[
            key
        ] = answer
    return context


def check_if_new_dirs_can_be_created(
    directories, context, destination_dir, no_input: bool
):
    """Check if any of the templated directories already exist.

    If so, offer the user to overwrite them.
    """
    existing_target_dirs = []
    for directory in directories:
        new_dir_name = Template(directory.name).render(context)
        new_dir_path = destination_dir / new_dir_name
        if new_dir_path.exists():
            existing_target_dirs.append(new_dir_path)
    if not existing_target_dirs:
        return True
    if no_input:
        logger.warning(
            "\nThe following directories already existed and have been overwritten:\n\t{}".format(
                "\n\t".join(str(dir) for dir in existing_target_dirs)
            )
        )
        overwrite = True
    else:
        logger.warning(
            "\nThe following directories already exist:\n\t{}".format(
                "\n\t".join(str(dir) for dir in existing_target_dirs)
            )
        )
        overwrite = input("Overwrite those directories [Y]/N ") or True
    if is_yes(overwrite):
        for directory in existing_target_dirs:
            shutil.rmtree(directory)
        return True
    raise UserCancellationError


def render_templates(templates, root_directories, context, destination_dir, no_input):
    """Render the templated directories/files into the current location."""
    with cd(destination_dir):
        check_if_new_dirs_can_be_created(
            directories=root_directories,
            context=context,
            destination_dir=destination_dir,
            no_input=no_input,
        )
        jinja_env = Environment(
            loader=FileSystemLoader(str(templates), followlinks=True),
            keep_trailing_newline=True,
        )
        to_copy_as_is = []
        for pattern in context.get("_copy_without_render", []):
            to_copy_as_is.extend(glob.glob(pattern, recursive=True))

        for template in jinja_env.list_templates():
            new_file = Path(Template(template).render(context))
            # pylint: disable=no-member
            new_file.parents[0].mkdir(parents=True, exist_ok=True)
            template = jinja_env.get_template(template)
            content = template.render(context)
            with open(new_file, "w", encoding="UTF-8") as templated_file:
                templated_file.write(content)


class Question:
    """Class handling the user input and validation for a context key."""

    def __init__(self, key, ask=None, default=None, validators=None):
        """Initialize the Question."""
        self.key = key
        self.ask = key.replace("_", " ").title() if ask is None else ask
        self.default = default
        self.validators = validators or []
        self.validation_errors = []
        self.answer = None

    def resolve(self):
        """Fill the `answer` attribute, prompting the user if required."""
        if self.answer is not None:
            return self.answer

        if self.ask is False:
            self.answer = self.default() if callable(self.default) else self.default
        else:
            while self.answer is None or not self.is_valid():
                if self.validation_errors:
                    logger.warning(
                        f"The answer for question {self.key} failed the following "
                        f"validations: {self.validation_errors}"
                    )
                if self.default:
                    default = self.default() if callable(self.default) else self.default
                    self.answer = input(f"{self.ask} [{default}] ") or default
                else:
                    self.answer = input(f"{self.ask} ")
        return self.answer

    def is_valid(self):
        """Make sure the user input passes validation."""
        self.validation_errors = [
            validator.check(self) for validator in self.validators
        ]
        return not self.validation_errors


class Context:
    """Utility class handling the context passed to the Jinja2 engine."""

    def __init__(self, questions=None):
        """Set a private dict representing the context."""
        self._dict = {}
        self.questions = questions or []

    def __getitem__(self, key):
        """Access the private dict."""
        return self._dict[key]

    def resolve(self):
        """Resolve the questions and populate the context dict."""
        for question in self.questions:
            self._dict[question.key] = question.resolve()

    def as_dict(self):
        """Return the context as dictionary."""
        return self._dict
