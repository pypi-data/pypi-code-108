import sys

import click

from magic.shared.display import clear_last_line
from magic.shared.validation import is_yes_or_no


def prompt(
    message,
    color,
    validate=None,
    default=None,
    required=False,
):
    print(click.style(message, fg=color))

    return __prompt_input(validate, default, required)


def multiline_prompt(
    message, color, validate=None, default=None, required=False
):
    print(click.style(message, fg=color))

    lines = []
    while True:
        line = __prompt_input(validate, default)
        if line:
            lines.append(line)
        elif not required or len(lines) > 0:
            clear_last_line()
            break
    return lines


def yes_or_no_prompt(message, color, default=None, required=False):
    print(click.style(message, fg=color))

    return __yes_or_no(__prompt_input(is_yes_or_no, default, required))


def __yes_or_no(value):
    if value in ("y", "yes"):
        return True
    return False


def __prompt_input(validate=None, default=None, required=False):
    input_message = "> "

    response = None
    while response is None:
        try:
            response = input(click.style(input_message, fg="cyan"))
        except KeyboardInterrupt:
            sys.exit()

        if default is not None:
            if response == "":
                clear_last_line()
                print(click.style(f"{input_message}{default}", fg="cyan"))
                response = default

        if required and response == "":
            response = None
            clear_last_line()

        if validate is not None:
            if validate(response) is False:
                response = None
                clear_last_line()

    return response
