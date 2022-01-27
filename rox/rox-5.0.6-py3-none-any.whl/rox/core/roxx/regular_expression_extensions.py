import re

from rox.core.utils.type_utils import is_string


class RegularExpressionExtensions:
    def __init__(self, parser):
        self.parser = parser

    def extend(self):
        self.parser.add_operator('match', match)


def match(parser, stack, context):
    text = stack.pop()
    pattern = stack.pop()
    flags = stack.pop()

    if not is_string(text) or not is_string(pattern) or not is_string(flags):
        stack.push(False)
        return

    options = 0
    for flag in flags:
        if flag == "i":
            options |= re.IGNORECASE
        elif flag == "x":
            options |= re.VERBOSE
        elif flag == "s":
            options |= re.DOTALL
        elif flag == "m":
            options |= re.MULTILINE

    stack.push(re.search(pattern, text, options) is not None)
