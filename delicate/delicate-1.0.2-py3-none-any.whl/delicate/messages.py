#!/usr/bin/env python
# -*- coding: utf-8 -*-

# List of colors that we can use to style the console printed message
# We also have some other special properties like bold/underline etc..
class _styles:
    BLACK = '\033[30m'
    LIGHTBLACK = '\033[90m'
    DARKRED = '\033[31m'
    RED = '\033[91m'
    DARKGREEN = '\033[32m'
    GREEN = '\033[92m'
    DARKYELLOW = '\033[33m'
    YELLOW = '\033[93m'
    DARKBLUE = '\033[34m'
    BLUE = '\033[94m'
    DARKMAGENTA = '\033[35m'
    MAGENTA = '\033[95m'
    DARKCYAN = '\033[36m'
    CYAN = '\033[96m'
    GRAY = '\033[37m'
    WHITE = '\033[97m'

    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

# A method that print the message to the console output, and we support styling for the messages
def log(message, color=None):
    if (color == None):
        print(message)
    else:
        if hasattr(_styles, color):
            print(getattr(_styles, color) + message + '\033[0m')
        else:
            print(message + '\033[0m')
