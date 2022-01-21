#!/bin/env python

import logging
import os
import shutil
import sys

logging.basicConfig(level=logging.INFO)


def get_layout_variant() -> list[str | None]:
    setxkbmap_output = os.popen("setxkbmap -query").read()
    values = [x.split(":") for x in setxkbmap_output.strip("\n").split("\n")]
    stripped_values = [(y[0], y[1].strip()) for y in values]
    indexed_values = dict(stripped_values)
    return [indexed_values["layout"], indexed_values.get("variant")]


def cycle_layout(layouts: list[list[str | None]]):
    layout_variant = get_layout_variant()
    next_layout_index = 0

    if layout_variant in layouts:
        next_layout_index = layouts.index(layout_variant) + 1
        if next_layout_index == len(layouts):
            next_layout_index = 0

    next_layout = layouts[next_layout_index]

    command = "setxkbmap %s" % next_layout[0]
    if next_layout[1] is not None:
        command = "%s %s" % (command, next_layout[1])

    change_layout_result = os.system(command)

    if change_layout_result != 0:
        logging.error("Failed to cycle keyboard layout using: %s" % command)
    else:
        logging.info("Successfully cycled keyboard layout using: %s" % command)


def help():
    print(
        """Usage: langycycle LAYOUT[:VARIANT] [LAYOUT[:VARIANT]]...

Cycles through keyboard layouts and variants using setxkbmap.

example: langycycle.py us fr ca:eng ca:fr ca:multi"""
    )


def get_layouts_from_args(args: list[str]) -> list[list[str | None]]:
    parsed = [x.split(":") for x in args[1:]]
    return list([y[0], y[1] if len(y) > 1 else None] for y in parsed)


def main():
    if len(sys.argv[1:]) == 0 or sys.argv[1] in ("help", "-h", "--help"):
        help()
        sys.exit()

    setxkbmap_executable = shutil.which("setxkbmap")

    if setxkbmap_executable is None:
        sys.exit("Cannot find setxkbmap")

    layouts = get_layouts_from_args(sys.argv)

    cycle_layout(layouts)


if __name__ == "__main__":
    main()
