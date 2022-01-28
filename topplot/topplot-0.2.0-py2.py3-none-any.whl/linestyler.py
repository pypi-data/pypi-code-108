# Copyright (c) 2019-2020 Jonathan Sambrook and Codethink Ltd.
# -----------------------------------------------------------------------------
# Class to keep all instances of a plotted line having the same colour,
# linestyle, and marker across different plots.


class LineStyler:

    arbitrary_marker_offset = 0

    linestyles = ["-", ":", "-.", "--"]

    linestyle_count = len(linestyles)

    marks = [
        ".",  # point
        #    ",", # pixel
        "o",  # circle
        "v",  # triangle_down
        "^",  # triangle_up
        "<",  # triangle_left
        ">",  # triangle_right
        "1",  # tri_down
        "2",  # tri_up
        "3",  # tri_left
        "4",  # tri_right
        # "8", # octagon # Looks too much like a circle when small
        "s",  # square
        "p",  # pentagon
        "P",  # plus (filled)
        "*",  # star
        "h",  # hexagon1
        "H",  # hexagon2
        "+",  # plus
        "x",  # x
        "X",  # x (filled)
        "D",  # diamond
        "d",  # thin_diamond
        "|",  # vline
    ]

    mark_count = len(marks)

    def __init__(self):
        self.colours = {}
        self.linestyles = {}
        self.marks = {}

        self.arbitrary_marker_offset = LineStyler.arbitrary_marker_offset
        LineStyler.arbitrary_marker_offset += 5
        self.count = 0

    # -------------------------------------------------------------------------
    # Define one if undefined, then apply a line's style.

    def style(self, name, line):
        if name not in self.marks:
            self.count += 1
            self.marks[name] = LineStyler.marks[
                (self.count + self.arbitrary_marker_offset) % LineStyler.mark_count
            ]
            self.linestyles[name] = LineStyler.linestyles[
                int(self.count / LineStyler.mark_count) % LineStyler.linestyle_count
            ]
            self.colours[name] = line.get_color()

        # print(
        #    f"mark: >{self.marks[name]}<  ls: >{self.linestyles[name]}<  col:"
        #    f" >{self.colours[name]}<  name: >{name}<"
        # )

        line.set_color(self.colours[name])
        line.set_linestyle(self.linestyles[name])
        line.set_marker(self.marks[name])


# ------------------------------------------------------------------------------
# vi: sw=4:ts=4:et:tw=0
