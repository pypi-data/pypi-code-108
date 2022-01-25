'''Utilities for printing output to the terminal.
'''
import re
from shutil import get_terminal_size
from sys import stdout
from threading import Event
from typing import TextIO


# From cli-spinners (https://www.npmjs.com/package/cli-spinners)
INTERVAL = 0.080  # seconds
ASCII_FRAMES = ['|', '/', '-', '\\']
FRAMES = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']


COLORS = dict(red=31, green=32, yellow=33, blue=34, magenta=35, grey=90)
'''Dictionary of supported color values for `rpa_logger.utils.terminal.color`.
'''


def bold(text: str) -> str:
    '''Bold given text with ANSI escape codes.

    Args:
        text: Text to be formatted.

    Returns:
        String with formatted text.
    '''
    return f'\033[1m{text}\033[22m'


def color(text: str, color_name: str) -> str:
    '''Color given text with ANSI escape codes.

    Args:
        text: Text to be formatted.
        color_name: Color to format text with. See
            `rpa_logger.utils.terminal.COLORS` for available values.

    Returns:
        String with formatted text.
    '''
    if color_name not in COLORS:
        return text
    return f'\033[{COLORS[color_name]}m{text}\033[39m'


def remove_ansi_escapes(text: str) -> str:
    '''Remove ANSI escape codes from given string.

    Args:
        text: String with ANSI escape codes.

    Returns:
        `text` without any ANSI escape codes.
    '''
    return re.sub(r'\033\[[^m]+m', '', text)


def fit_to_width(text: str) -> str:
    '''Fit formatted text into current terminal width

    If text does not fit to current terminal width, the end of the string is
    replaced with '…' character. If text contains ANSI escape codes,
    formatting is cleared when text is truncated.

    Args:
        text: Text to fit to terminal width.

    Returns:
        The possibly truncated string
    '''
    max_len = get_terminal_size().columns
    non_formatted_text = remove_ansi_escapes(text.replace('\r', ''))

    if len(non_formatted_text) <= max_len:
        return text

    i = 0
    j = 0
    while i < max_len - 2:
        match = re.match(r'\r|\033\[[0-9]+m', text[(i + j):])
        if match:
            j += len(match.group(0))
        else:
            i += 1

    clear_formatting = '\033[0m' if re.search(r'\033\[[0-9]+m', text) else ''
    return f'{text[:(i + j)]}{clear_formatting}…'


def clear_current_row(file: TextIO = stdout):
    '''Clear current terminal row

    Can be used, for example, when progress text is replaced with shorter one.

    Args:
        file: File to print output to. Defaults to stdout.
    '''
    width = get_terminal_size().columns
    print(f'\r{" " * width}', file=file, end='')


def print_spinner_and_text(
        text: str,
        stop_event: Event,
        file: TextIO = stdout,
        ascii_only: bool = False) -> None:
    '''Print spinner and text until stop event

    Args:
        text: Text to print after spinner.
        stop_event: Event to stop spinner loop.
        file: File to print output to. Defaults to stdout.
        ascii_only: If true, use ascii only spinner.
    '''
    frames = FRAMES if not ascii_only else ASCII_FRAMES

    i = 0
    while not stop_event.wait(INTERVAL):
        print(
            fit_to_width(f'\r{frames[i % len(frames)]} {text}'),
            file=file,
            end='')
        i += 1

    print('\r', end='')
