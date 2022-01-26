"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
from pathlib import Path

# * Third Party Imports --------------------------------------------------------------------------------->
import click
from rich.table import Table
from rich.markup import escape
from rich.console import Console as RichConsole

# * Gid Imports ----------------------------------------------------------------------------------------->
from gidapptools.general_helper.output_helper.rich_helper import dict_to_rich_tree

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()
CONSOLE = RichConsole(soft_wrap=True, record=True)
# endregion[Constants]


@click.group(name="appmeta")
def appmeta_cli():
    ...


@appmeta_cli.command(help="Lists all available Plugins")
def plugins():
    from gidapptools.meta_data.interface import app_meta
    table = Table(title="[b u light_steel_blue3]AVAILABLE APPMETA-PLUGINS[/b u light_steel_blue3]")
    table.add_column("Plugin Item", style="i chartreuse2 on grey15", header_style="b white on grey37", justify="center", no_wrap=True)
    table.add_column('Module', style="b light_slate_blue on grey15", header_style="b white on grey37", justify="center", no_wrap=True)
    table.add_column('File', style="u dark_khaki on grey15", header_style="b white on grey37", justify="center", no_wrap=True)

    for data in app_meta.plugin_data:
        table.add_row(data.get("product_name"), data.get("module"), f":open_file_folder: [link file://{data.get('file')}]{escape(data.get('file'))}")
    CONSOLE.print("")
    CONSOLE.print(table)


@appmeta_cli.command()
def base_settings():
    from gidapptools.meta_data.interface import app_meta

    CONSOLE.print(dict_to_rich_tree('Base Settings', app_meta.default_base_configuration))


# region[Main_Exec]
if __name__ == '__main__':
    pass
# endregion[Main_Exec]
