import click

from magic.shared.spellbook import read_spells

RESERVED_WORDS = ["add", "edit"]


# Line validation


def is_a_number(line):
    return line.isnumeric()


def is_yes_or_no(_line):
    line = _line.lower()
    return line in ["y", "yes", "n", "no"]


# List validation


def is_empty(_list):
    if len(_list):
        return "" in _list
    return True


def has_duplicates(_list):
    return len(_list) != len(set(_list))


def __is_each_word_available(words, spells):
    errors = []
    for word in words:
        if word in RESERVED_WORDS:
            errors.append(f"Error: '{word}' is a reserved word")
        if spells.get(word):
            errors.append(f"Error: '{word}' is already used in a spell")
    return errors


def __print_validation_errors(errors):
    error_string = "\n".join(errors) + "\n"
    print(click.style(error_string, fg="yellow"))


def magic_word_validator():
    spells = read_spells()

    def validate(line):
        words = [word.strip(" ") for word in line.split(",")]

        if is_empty(words):
            return False
        if has_duplicates(words):
            return False

        errors = __is_each_word_available(words, spells)
        if len(errors) > 0:
            __print_validation_errors(errors)
            return False

        return True

    return validate
