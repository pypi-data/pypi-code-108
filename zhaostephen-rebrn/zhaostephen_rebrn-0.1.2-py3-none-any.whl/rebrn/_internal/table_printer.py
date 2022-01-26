from typing import List


def format_table_by_columns(input_table_columns: List[List[str]]) -> str:
    column_widths = list(
        max(len(item) for item in column) for column in input_table_columns
    )

    num_of_rows = len(input_table_columns[0])
    num_of_columns = len(input_table_columns)

    rows = []
    for y in range(num_of_rows):
        row = []
        for x in range(num_of_columns):
            row.append(input_table_columns[x][y].rjust(column_widths[x]))
        rows.append(row)

    return "\n".join(" ".join(row) for row in rows)


def print_table_by_columns(input_table_columns: List[List[str]]) -> None:
    print(format_table_by_columns(input_table_columns))
