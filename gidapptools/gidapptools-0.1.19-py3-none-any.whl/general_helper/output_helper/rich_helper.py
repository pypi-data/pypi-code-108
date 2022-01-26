"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
import re
import types
import random
import shutil
import subprocess
from io import StringIO
from time import sleep
from string import ascii_letters
from typing import Any
from pathlib import Path
from tempfile import TemporaryDirectory

# * Third Party Imports --------------------------------------------------------------------------------->
from rich import inspect as rinspect
from rich.tree import Tree
from rich.panel import Panel
from rich.console import Console as RichConsole
from rich.terminal_theme import TerminalTheme

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]

MY_TERMINAL_THEME = TerminalTheme(
    (40, 40, 40),
    (102, 255, 50),
    [
        (0, 0, 0),
        (15, 140, 220),
        (86, 216, 86),
        (255, 215, 0),
        (98, 96, 180),
        (18, 255, 156),
        (25, 128, 128),
        (192, 192, 192),
    ],
    [
        (128, 128, 128),
        (150, 25, 25),
        (200, 200, 100),
        (150, 150, 25),
        (25, 25, 150),
        (0, 176, 255),
        (213, 121, 255),
        (150, 150, 150),
    ],
)


def dict_to_rich_tree(label: str, in_dict: dict) -> Tree:
    base_tree = Tree(label=label)

    def _handle_sub_dict(in_sub_dict: dict, attach_node: Tree):
        for k, v in in_sub_dict.items():
            key_node = attach_node.add(k)
            if isinstance(v, dict):
                _handle_sub_dict(v, key_node)
            elif isinstance(v, list):
                key_node.add(Panel(',\n'.join(f"{i}" for i in v)))
            else:
                key_node.add(f"{v}")

    _handle_sub_dict(in_dict, base_tree)
    return base_tree


def inspect_object_with_html(obj: object,
                             show_all: bool = False,
                             show_methods: bool = False,
                             show_dunder: bool = False,
                             show_private: bool = False,
                             show_docs: bool = True,
                             show_help: bool = False):

    def _make_title(_obj: Any) -> str:

        title_str = (
            str(_obj)
            if (isinstance(_obj, type) or callable(_obj) or isinstance(_obj, types.ModuleType))
            else str(type(_obj))
        )
        if hasattr(obj, "name") and obj.name != str(_obj):
            title_str += f' -| {_obj.name!r} |-'

        return title_str

    def sanitize_name(name: str) -> str:

        return re.sub(r"\.\s\-\?\!\,\(\)\[\]\<\>\|\:\;\'\"\&\%\$\§\\", '_', name)

    def make_file_name(_obj) -> str:
        # if hasattr(_obj, 'name'):
        #     text = _obj.name

        # elif hasattr(_obj, '__name__'):
        #     text = _obj.__name__
        # else:
        text = ''.join(random.choices(ascii_letters, k=random.randint(5, 10)))

        return sanitize_name(text) + '.html'

    with StringIO() as throw_away_file:
        console = RichConsole(soft_wrap=True, record=True, file=throw_away_file)
        title = None
        try:
            title = _make_title(obj)
        except Exception as e:
            print(e)
            title = None
        rinspect(obj=obj,
                 title=title,
                 help=show_help,
                 methods=show_methods,
                 docs=show_docs,
                 private=show_private,
                 dunder=show_dunder,
                 all=show_all,
                 console=console)
        with TemporaryDirectory() as temp_directory:
            out_file = Path(temp_directory).joinpath(make_file_name(obj))

            console.save_html(out_file, theme=MY_TERMINAL_THEME)
            firefox = shutil.which("firefox.exe")
            cmd = f'"{firefox}" -new-window "{str(out_file)}"'

            _cmd = subprocess.run(cmd, check=True, text=True)
            sleep(0.5)


# region[Main_Exec]

if __name__ == '__main__':
    # inspect_object_with_html(, show_all=True, show_help=True),
    pass
# endregion[Main_Exec]
