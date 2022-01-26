#!/usr/bin/env python


def parse_file(
    filename, replace_starts=False, replace_goals=False, surround_with_walls=False
):
    """parse the map file to an array representation

    Args:
        filename (string): path to the map file.
        replace_starts (bool, optional): replace the start line with default empty tiles. Defaults to False.
        replace_goals (bool, optional): replace the goal line with default empty tiles. Defaults to False.
        surround_with_walls (bool, optional): add addtional wall tiles surrounding the map. Defaults to False.

    Returns:
        [type]: [description]
    """
    with open(filename, "r+") as f:
        first = f.readline().split()
        height = int(first[1])
        width = int(first[2])

        map = []
        for _ in range(height):
            line = f.readline().rstrip()
            if replace_starts:
                line = line.replace("s", ".")
            if replace_goals:
                line = line.replace("g", ".")
            map.append(line)

        if surround_with_walls:
            height = height + 2
            width = width + 2
            wall_line = ""
            for _ in range(width):
                wall_line += "x"

            for i, line in enumerate(map):
                new_line = "x" + line + "x"
                map[i] = new_line

            map = [wall_line] + map + [wall_line]

        return height, width, map
