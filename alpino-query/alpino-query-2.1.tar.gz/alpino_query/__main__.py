#!/usr/bin/env python3
import sys

from lxml import etree
from .marker import main as mark
from .subtree import main as generate_subtree
from .xpath_generator import main as generate_xpath


def help():
    print("""
[action]
    mark
    subtree
    xpath

For mark:
    mark [inputxml] [tokens] [attributes]

For subtree:
    subtree [marked xml] [remove=rel/relcat/cat]

For xpath:
    xpath [subtree xml] [order=1/0]
""")


def main():
    if len(sys.argv) > 1:
        action = sys.argv[1]
    else:
        help()
        return

    if action == "mark":
        [inputxml, tokens, attributes] = sys.argv[2:]
        twig = mark(inputxml.replace('\\n', '\n'), tokens.split(' '), attributes.split(' '))
        print(etree.tostring(twig, pretty_print=True).decode())
    elif action == "subtree":
        [inputxml, remove] = sys.argv[2:]
        subtree = generate_subtree(inputxml.replace('\\n', '\n'), remove)
        print(etree.tostring(subtree, pretty_print=True).decode())
    elif action == "xpath":
        [inputxml, order] = sys.argv[2:]
        print(generate_xpath(inputxml.replace('\\n', '\n'), order))
    else:
        help()


if __name__ == "__main__":
    main()
