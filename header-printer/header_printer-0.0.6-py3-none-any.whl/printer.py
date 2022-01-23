import shutil
from textwrap import dedent


def print_header(text):
    terminal_columns, _ = shutil.get_terminal_size()

    formated_header = dedent(f"""
    {"*" * terminal_columns}
    {text.center(terminal_columns)}
    {"*" * terminal_columns}
    """)

    print(formated_header)
