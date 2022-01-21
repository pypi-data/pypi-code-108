import sys

import click

# Emoji spacing in terminal is unpredictable
# These extra spaces appear to fix issues
EMOJI_FAILURE = "\u274c\ufeff"
EMOJI_FIRE = "\U0001f525"
EMOJI_SPARKLE = "\u2728\ufeff"
EMOJI_SUCCESS = "\u2705\ufeff"
EMOJI_TIMER = "\u23f1\u0020"
EMOJI_TRASH = "\U0001f5d1\u0020"
EMOJI_WIZARD = "\U0001f9d9"


RESET_COLOR = "\u001b[0m"


def print_error(error):
    print(click.style(f'{EMOJI_FIRE} Error: {error}', fg='red'))


def clear_last_line():
    sys.stdout.write("\033[F")  # back to previous line
    sys.stdout.write("\033[K")  # clear line
