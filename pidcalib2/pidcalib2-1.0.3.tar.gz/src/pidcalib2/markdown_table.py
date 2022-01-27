"""A module for printing simple Markdown tables.

Each column can have a different numeric precision, any cell can have a string
instead of a number.

Usage:
    table = MarkdownTable(["Column1", "Column2"])
    table.add_row(["Row1", 3.14])
    table.set_precision([0, 1])
    table.print()
"""


class MarkdownTable:
    """Class representing a Markdown table with support for pretty printing."""

    def __init__(self, header):
        """Initialize table with supplied column titles.

        Args:
            header: A list containing column titles.
        """
        assert type(header) in [list, tuple]
        self.header = header
        self.rows = []
        self.precision = [3 for _ in header]

    def set_precision(self, precisions):
        """Set columns' decimal precisions.

        Applies only to numeric cells.

        Args:
            precisions: A list of integers representing number of decimals in
                each column.
        """
        assert len(precisions) == len(self.header)
        assert type(precisions) in [list, tuple]
        self.precision = precisions

    def add_row(self, row):
        """Add a single row.

        The row must be the same length as the header used to initialize the
        table.
        """
        assert len(self.header) == len(row)
        self.rows.append(row)

    # def add_midline(self):
    #     self.rows.append(["" for _ in range(len(header))])

    def get_length_of_number(self, number, precision):
        """Return the length of a number written with a specified precision."""
        number_format = "{:." + str(precision) + "f}"
        return len(number_format.format(number))

    def get_column_widths(self):
        """Return the maximum width of content in all columns."""
        columns = []
        for col in range(len(self.header)):
            cells = []
            for row in self.rows:
                if type(row[col]) is str:
                    cells.append(len(row[col]))
                else:
                    cells.append(
                        self.get_length_of_number(row[col], self.precision[col])
                    )
            cells.append(len(self.header[col]))
            columns.append(max(cells))
        return columns

    def print(self):
        """Print the table."""
        self.columns_widths = self.get_column_widths()
        self.print_row(self.header)
        self.print_separator()
        for row in self.rows:
            self.print_row(row)

    def get_format_string(self, width, precision=None):
        """Get a formatting string.

        You normally write these yourself, but here we want all the rows in a
        column to have the same width, regardless of content.

        Args:
            width: Total requested width of the string.
            precision: Optional precision for numeric cells.
        """
        format_string = "{:" + str(width)
        if precision is not None:
            format_string += "." + str(precision) + "f} | "
        else:
            format_string += "} | "
        return format_string

    def print_row(self, row):
        """Print a single row."""
        row_text = ""
        for col, cell in enumerate(row):
            format_string = self.get_format_string(
                self.columns_widths[col],
                (None if type(cell) is str else self.precision[col]),
            )
            row_text += format_string.format(cell)

        print(row_text.rstrip(" |"))

    def print_separator(self):
        """Print a separator row (midrule)."""
        print("|".rjust(self.columns_widths[0] + 2, "-"), end="")
        for col, _ in enumerate(self.header[1:-1]):
            print("|".rjust(self.columns_widths[col + 1] + 3, "-"), end="")
        print("".ljust(self.columns_widths[-1] + 1, "-"))
