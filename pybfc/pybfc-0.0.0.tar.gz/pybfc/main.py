# Pybfc - BranFuck compiler write in python
# Copyright (C) 2022 - Awiteb <awiteb@hotmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from pathlib import Path
from typing import Tuple, Optional

import typer

from .bfctypes import BFCommand, CompilerSettings, Memory
from .exceptions import SyntaxError
from .version import version

__all__ = ("BFCompiler", "MEMORY_SIZE")

MEMORY_SIZE = 30_000

app = typer.Typer(name="pybfc", add_completion=False)


class BFCompiler:
    __slots__ = "bf_file", "settings", "memory"

    def __init__(
        self,
        bf_file: Path,
        settings: CompilerSettings = CompilerSettings(),
        memory: Memory = Memory(),
    ) -> None:
        """Initialize compiler instance

        Args:
            bf_file (Path): BranFuck file
            settings (CompilerSettings, optional): Settings. Defaults to default settings.
            memory (Memory, optional): [description]. The memory on which the BF will be executed Defaults to default memory.
        """
        self.bf_file = bf_file
        self.settings = settings
        self.memory = memory

    @classmethod
    def __get_loop(cls, start_index: int, source_code: str) -> Tuple[int, str]:
        """Returns loop contents and end index of loop

        Args:
            start_index (int): Start of loop
            source_code (str): The source code

        Raises:
            Exception: Unclose loop

        Returns:
            Tuple[int, str]: end of loop, loop contents
        """
        brackets = 0
        for idx, char in enumerate(source_code[start_index:]):
            if char == "]":
                brackets -= 1
            elif char == "[":
                brackets += 1
            if brackets == 0:
                return (idx + start_index), source_code[
                    start_index + 1 : idx + start_index
                ]
        raise SyntaxError(f"Loop does not close! '{source_code[start_index:]}'")

    @classmethod
    def __execute_command(
        cls,
        command: str,
        memory: Memory,
        debug: bool = False,
        loop_number: int = 0,
    ):
        """execute command in memory

        Args:
            command (str): Command to execute it in memory
            memory (Memory): Memory to execute code in it
            debug (bool): Enable debug mode
            loop_number (int): Number of the loop (for debugging) if execution in loop

        """
        memory.execute(BFCommand(command))

        if debug:
            typer.echo(
                f"\nCommand -> '{command}', Loop -> {loop_number}\n"
                f"\tAddress -> {memory.pointer}, Value -> {memory.value}"
            )

    @classmethod
    def execute(
        cls,
        source_code: str,
        memory: Memory,
        settings: CompilerSettings,
        is_loop: bool = False,
        loop_number: int = 0,
    ):
        """Execute the given source code in memory
        Args:
            source_code (str): Source code you want to execute
            memory (Memory): Memory to execute code in it
            is_loop (bool): Execute source code as a loop
            loop_number (int): Number of the loop if execution in loop
        """
        char_counter = 0
        while char_counter < len(source_code):
            command = source_code[char_counter]
            if command == "[":
                end_loop, loop_content = cls.__get_loop(char_counter, source_code)
                char_counter = end_loop
                if memory.value > 0:
                    cls.execute(
                        loop_content,
                        memory,
                        settings=settings,
                        is_loop=True,
                        loop_number=loop_number + 1,
                    )
            else:
                cls.__execute_command(
                    command, memory, settings.debug, loop_number=loop_number
                )
            if (char_counter + 1) == len(source_code) and is_loop and memory.value > 0:
                char_counter = 0
            else:
                char_counter += 1

    @property
    def source_code(self) -> str:
        with open(self.bf_file, "r") as f:
            source_code = "".join(
                filter(
                    lambda char: char in (">", "<", "+", "-", "[", "]", ".", ","),
                    f.read(),
                )
            )
        return source_code

    def run(self) -> None:
        """
        Run Branfuck file
        """
        self.__class__.execute(
            self.source_code, self.memory, self.settings, is_loop=False
        )


def version_callback(value: bool):
    if value:
        typer.echo(f"Pybfc - Version: {version}")
        raise typer.Exit()


@app.command(
    name="bfc",
)
def compile_branfuck(
    file_path: Path = typer.Argument(
        ...,
        readable=True,
        exists=True,
        file_okay=True,
        dir_okay=False,
        help="BranFuck path to execute it.",
    ),
    debug: bool = typer.Option(
        False, "--debug", "-d", help="Enable debugging with execution."
    ),
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-V",
        help="Print Pybfc version and exit.",
        callback=version_callback,
    ),
) -> None:
    """Python BranFuck Compiler 🐍⚙️"""
    BFCompiler(bf_file=file_path, settings=CompilerSettings(debug=debug)).run()


def main() -> None:
    app()


if __name__ == "__main__":
    main()
