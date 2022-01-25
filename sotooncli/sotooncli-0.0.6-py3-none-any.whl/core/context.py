import click

from sotooncli.core.help_formatter import SotoonHelpFormatter


class SotoonContext(click.Context):
    formatter_class = SotoonHelpFormatter

    @property
    def command_path(self):
        parent_command_path = ""
        if self.parent:
            parent_command_path = self.parent.command_path
        return f"{parent_command_path} {self.info_name}"
