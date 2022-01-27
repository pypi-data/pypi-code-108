import sys
from pygments import highlight as highlight_py
from pygments.lexers import get_lexer_by_name
from pygments.formatters import Terminal256Formatter
import json as jsonlib
from difflib import SequenceMatcher, unified_diff as difflib_unified_diff
from colorama import Fore
import itertools
from ansiwrap import wrap
import re
import pyperclip
from pprint import pprint
from .status import Status

def run_or_exit(func, *args, out=None, err=None, err_func=None, err_args=[], err_kwargs={}, **kwargs):
    if out:
        print(out, end="", flush=True)
    try:
        return_obj = func(*args, **kwargs)
        if out:
            print(f" {Fore.GREEN}OK{Fore.RESET}", end="\n", flush=True)
        return return_obj
    except Exception as e:
        if out:
            print(f" {Fore.RED}ERROR{Fore.RESET}", end="\n")
        if err:
            print(f"{Fore.RED}{err}{Fore.RESET}")
            print(e)

        sys.stdout.flush()

        if err_func:
            return err_func(*err_args, **err_kwargs)
        else:
            exit(1)

# TODO: Normalize newline endings
def load_file(path):
    try:
        with open(path, "r") as f:
            content = f.read()
            if content.endswith("\n"):
                content = content[:-1]
            return content
    except FileNotFoundError:
        print(f"{Fore.RED}Couldn't open file: {path}{Fore.RESET}")
        exit(1)


def highlight(text, syntax, light=False):
    theme = "monokai"
    if light:
        theme = "solarized-light"

    return highlight_py(text, get_lexer_by_name(syntax), Terminal256Formatter(style=theme))


def line_number_print(text):
    for i, line in enumerate(text.split("\n")):
        print("{0: 8}  {1:}".format(i + 1, line))


def remove_color(string):
    ansi_escape = r'\x1b\[(?:\d;)?\d{1,2}m'
    ansi_pattern = re.compile(ansi_escape)
    return ansi_pattern.sub('', string)


def column_print(first, second, title_first="", title_second="", n=40):
    margin = 10
    space = n + margin
    margin_left = 4
    space_left = margin_left * " "

    def get_nchars(string):
        return len(remove_color(string))

    if title_first or title_second:
        padding_first = " " * (space - get_nchars(title_first))
        padding_second = " " * (space - get_nchars(title_second))
        print(f"{space_left}{title_first}{padding_first}    {title_second}{padding_second}")
        total_char = space * 2
        print(f"{space_left}{total_char * '━'}")

    first = first.splitlines()
    second = second.splitlines()
    for i, j in itertools.zip_longest(first, second):
        i = "^" + i + "$" if i is not None else ""
        j = "^" + j + "$" if j is not None else ""
        i_list = wrap(i, n)
        j_list = wrap(j, n)
        for ii, jj in itertools.zip_longest(i_list, j_list):
            ii = ii if ii is not None else ""
            jj = jj if jj is not None else ""

            padding_ii = " " * (space - get_nchars(ii))
            padding_jj = " " * (space - get_nchars(jj))
            print(f"{space_left}{ii}{padding_ii}    {jj}{padding_jj}")


def json(content, sort_keys=False):
    return jsonlib.dumps(content, sort_keys=sort_keys, indent=2)


def prettify_dict(dictionary, sort_keys=True):
    print(json(dictionary, sort_keys=sort_keys))


def save_json(content, path, sort_keys=False):
    json_content = json(conent, sort_keys=sort_keys)
    f = open(path, "w")
    f.write(json_content)
    f.close()


def colored_diff(real, expected, junk=""):
    a = real.splitlines()
    b = expected.splitlines()
    diffcodes = SequenceMatcher(a=a, b=b, isjunk=lambda x: x in f" \t{junk}").get_opcodes()
    colored_real = []
    colored_expected = []

    # Both match exactly
    perfect = True
    # There is more information in real, but they match
    presentation = False
    # There is information missing in real
    failed = False

    for diff, ir, jr, ie, je in diffcodes:
        # Color to apply to the next text in diffcode
        color_real = None
        color_expected = None

        if diff == "replace":
            failed = True

            ar = re.split('(\W)', "\n".join(a[ir:jr]))
            br = re.split('(\W)', "\n".join(b[ie:je]))
            colored_ar = ""
            colored_br = ""
            replace_codes = SequenceMatcher(a=ar, b=br, isjunk=lambda x: x in f" \t{junk}").get_opcodes()

            for replace_tag, irr, jrr, ire, jre in replace_codes:
                if replace_tag == "equal":
                    color_expected = Fore.GREEN
                    color_real = Fore.GREEN
                elif replace_tag == "delete":
                    color_real = Fore.CYAN
                elif replace_tag == "insert":
                    color_expected = Fore.YELLOW
                elif replace_tag == "replace":
                    color_real = Fore.RED
                    color_expected = Fore.RED

                # Append to colored_real
                if irr < jrr:
                    s = "".join(ar[irr:jrr])
                    colored_ar += f"{color_real}{s}{Fore.RESET}"

                # Append to colored_expected
                if ire < jre:
                    s = "".join(br[ire:jre])
                    colored_br += f"{color_expected}{s}{Fore.RESET}"

            colored_real += colored_ar.splitlines()
            colored_expected += colored_br.splitlines()

        else:
            # They are the same
            if diff == "equal":
                color_expected = Fore.GREEN
                color_real = Fore.GREEN

            # This information is in real but not in expected
            elif diff == "delete":
                failed = True
                color_real = Fore.CYAN

            # This information is in expected but not in real
            elif diff == "insert":
                failed = True
                color_expected = Fore.YELLOW

            # Append to colored_real
            if color_real:
                colored_real += [
                    color_real + s + Fore.RESET
                    for s in a[ir:jr]
                ]
            else:
                colored_real += a[ir:jr]
            # Append to colored_expected
            if color_expected:
                colored_expected += [
                    color_expected + s + Fore.RESET
                    for s in b[ie:je]
                ]
            else:
                colored_expected += b[ie:je]


    if failed:
        status = Status.FAILED
    elif presentation:
        status = Status.PRESENTATION
    elif perfect:
        status = Status.PERFECT

    # print(repr(real))
    # print(repr(colored_real))
    return "\n".join(colored_real), "\n".join(colored_expected), status

def unified_diff(real, expected, junk=""):
    return "\n".join(list(difflib_unified_diff(real.splitlines(), expected.splitlines(), fromfile="output", tofile="output", lineterm="")))

def print_lines(text, start="", end=""):
    for line in text.splitlines():
        if line:
            # print(repr(line))
            print(f"{start}{line}{end}")

def copy_clipboard(content):
    pyperclip.copy(content)

