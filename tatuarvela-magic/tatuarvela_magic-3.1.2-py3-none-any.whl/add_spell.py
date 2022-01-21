import re

from magic.shared.display import EMOJI_WIZARD
from magic.shared.prompt import multiline_prompt, prompt, yes_or_no_prompt
from magic.shared.spellbook import create_spell
from magic.shared.validation import magic_word_validator

PROMPT_COLOR = "cyan"


def add_spell():
    print(
        f"{EMOJI_WIZARD} This wizard will add a new spell to your .spellbook.json file.\n"
        f"Press ^C at any time to quit.\n"
    )

    commands = multiline_prompt(
        "Enter commands to be run in the spell, separated by line breaks.\n"
        "You may use $a0, $a1, etc. to provide arguments.\n"
        "Leave the line empty to continue.",
        required=True,
        color=PROMPT_COLOR,
    )
    print("")

    description = prompt(
        "Enter a short description.\n"
        "You may use arguments ($a0, $a1, etc.) that will be filled for the casting message.",
        required=True,
        color=PROMPT_COLOR,
    )
    print("")

    magic_words = [
        word.strip(" ")
        for word in prompt(
            "Enter magic words, separated by commas.\n"
            "Any of them can be used for calling the spell: 'magic <magic_word>'.",
            validate=magic_word_validator(),
            color=PROMPT_COLOR,
        ).split(",")
    ]
    print("")

    show_message = yes_or_no_prompt(
        "Do you want to show a message when casting the spell, YES or no?",
        default="yes",
        color=PROMPT_COLOR,
    )
    print("")

    show_success_message = yes_or_no_prompt(
        "Do you want to show a message on completion "
        "(containing the starting time and duration of the spell), YES or no?",
        default="yes",
        color=PROMPT_COLOR,
    )

    spell = {
        "description": description,
        "magicWords": magic_words,
        "commands": commands,
        "argumentCount": __count_arguments(description, commands),
        "showMessage": show_message,
        "showSuccessMessage": show_success_message,
    }

    create_spell(spell)


def __count_arguments(description, commands):
    arg_matcher = "\\$a[0-9]+"

    combined_strings = f"{description} {' '.join(commands)}"
    args = re.findall(arg_matcher, combined_strings)
    for index, arg in enumerate(args):
        args[index] = int(arg.replace("$a", ""))
    args.sort()

    if len(args) == 0:
        return 0
    return args[-1] + 1
