from rich import print
from os import system


def run(cmd: str, silent: bool = False) -> None:
    if not silent:
        print(f"[bold green]RUN[/bold green] {cmd}")
        system(cmd)
