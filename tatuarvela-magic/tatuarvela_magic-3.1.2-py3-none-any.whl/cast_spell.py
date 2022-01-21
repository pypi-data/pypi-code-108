import subprocess  # nosec
from datetime import datetime, timedelta
from string import Template

import click

from magic.shared.display import (
    EMOJI_FAILURE,
    EMOJI_SPARKLE,
    EMOJI_SUCCESS,
    EMOJI_TIMER,
    print_error,
)
from magic.shared.spellbook import read_spell


def cast_spell(magic_word, arguments):
    start_time = datetime.now()

    try:
        # __attempt_spell returns true if showSuccessMessage is true
        show_success_message = __attempt_spell(magic_word, arguments)
        if show_success_message:
            __print_result(start_time, success=True)

    except RuntimeError:
        __print_result(start_time, success=False)


def __check_args(argument_count, spell_args):
    if argument_count is not None and len(spell_args) < argument_count:
        raise Exception(f"Not enough arguments, {argument_count} required")
    return spell_args


def __substitute_args(text, args):
    template = Template(text)
    args_dict = {f"a{index}": arg for index, arg in enumerate(args)}
    return template.substitute(**args_dict)


def __handle_message(spell, spell_args):
    description = spell.get("description")
    show_message = spell.get("showMessage")
    if show_message is not False:
        if spell_args is not None:
            description = __substitute_args(description, spell_args)
        print(f"{EMOJI_SPARKLE} {click.style(description, fg='cyan')}")


def __parse_command(command, spell_args):
    if spell_args is not None:
        command = __substitute_args(command, spell_args)
    return command


def __attempt_spell(magic_word, arguments):
    try:
        spell = read_spell(magic_word)

        if spell:
            spell_args = __check_args(spell.get("argumentCount"), arguments)
            __handle_message(spell, spell_args)

            executable_commands = ""
            for command in spell["commands"]:
                parsed_command = __parse_command(command, spell_args)
                executable_commands = f"{executable_commands}\n{parsed_command}"

            with subprocess.Popen(executable_commands, shell=True) as process:  # nosec
                exit_code = process.wait()

                if exit_code != 0:
                    raise Exception(f"Command returned exit code {exit_code}")
                return spell.get("showSuccessMessage") is not False

        raise Exception(f"Spell not found for magic word: {magic_word}")

    except Exception as error:
        print_error(error)
        raise RuntimeError from error


def __print_result(start_time, success):
    current_time = datetime.now().strftime("%H:%M:%S")
    elapsed_time = datetime.now() - start_time
    elapsed_time = elapsed_time - timedelta(microseconds=elapsed_time.microseconds)

    result_emoji = EMOJI_SUCCESS if success else EMOJI_FAILURE
    time_message = (
        click.style(current_time, fg="green")
        if success
        else click.style(current_time, fg="red")
    )

    print(f"{result_emoji} {time_message} | {EMOJI_TIMER} {elapsed_time}")
