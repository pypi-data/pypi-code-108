from rich.console import Console
from rich.prompt import Confirm, Prompt

console = Console()

ask = Prompt.ask

confirm = Confirm.ask


def style_str(string: str, style: str) -> str:
    return f"[{style}]{string}[/{style}]"


def green_str(string: str) -> str:
    return style_str(string, "green")


def red_str(string: str) -> str:
    return style_str(string, "red")


def magenta_str(string: str) -> str:
    return style_str(string, "magenta")
