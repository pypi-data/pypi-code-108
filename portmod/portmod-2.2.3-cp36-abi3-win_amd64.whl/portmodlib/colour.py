# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

from colorama import Fore, Style, init

init()


def yellow(text):
    return "{}{}{}".format(Fore.YELLOW, text, Style.RESET_ALL)


def blue(text):
    return "{}{}{}".format(Fore.BLUE, text, Style.RESET_ALL)


def lcyan(text):
    return "{}{}{}".format(Fore.LIGHTCYAN_EX, text, Style.RESET_ALL)


def cyan(text):
    return "{}{}{}".format(Fore.CYAN, text, Style.RESET_ALL)


def lblue(text):
    return "{}{}{}".format(Fore.LIGHTBLUE_EX, text, Style.RESET_ALL)


def green(text):
    return "{}{}{}".format(Fore.GREEN, text, Style.RESET_ALL)


def lred(text):
    return "{}{}{}".format(Fore.LIGHTRED_EX, text, Style.RESET_ALL)


def red(text):
    return "{}{}{}".format(Fore.RED, text, Style.RESET_ALL)


def magenta(text):
    return "{}{}{}".format(Fore.MAGENTA, text, Style.RESET_ALL)


def lgreen(text):
    return "{}{}{}".format(Fore.LIGHTGREEN_EX, text, Style.RESET_ALL)


def bright(text):
    return "{}{}{}".format(Style.BRIGHT, text, Style.RESET_ALL)


def colour(colour, text):
    return "{}{}{}".format(colour, text, Style.RESET_ALL)
