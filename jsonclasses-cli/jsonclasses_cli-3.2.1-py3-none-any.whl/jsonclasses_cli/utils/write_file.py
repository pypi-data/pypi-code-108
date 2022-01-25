from os import getcwd
from pathlib import Path
from rich import print

def write_file(path: Path, content: str, silent: bool = False) -> None:
    if not path.parent.exists():
        path.parent.mkdir(parents=True)
    with open(path, 'w') as file:
        if not silent:
            print(f"[bold green]CREATE[/bold green] {path.relative_to(getcwd())}")
        file.write(content)
