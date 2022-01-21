from logging import getLogger
from pathlib import Path
from random import choice
from typing import Dict

from pydantic import BaseModel, EmailStr
from rich.console import Console
from rich.markdown import Markdown
from rich.prompt import Prompt
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from typer import Argument, Option
from yaml import safe_load

from deckz.cli import app
from deckz.paths import GlobalPaths


@app.command()
def random(
    reason: str = Argument(..., help='Reason for the deckz random ("Pay the bill")'),
    workdir: Path = Option(
        Path("."), help="Path to move into before running the command"
    ),
) -> None:
    """Roll the dice and email the result."""
    logger = getLogger(__name__)
    config = MailsConfig.from_global_paths(GlobalPaths.from_defaults(workdir))
    console = Console()
    names = list(config.to)
    names_list_str = "\n".join(
        f"{i}. {name} <{config.to[name]}>" for i, name in enumerate(names, start=1)
    )
    console.print(Markdown(f"Here are the possible participants:\n\n{names_list_str}"))
    print()
    ok = False
    default = ", ".join(map(str, range(1, len(names) + 1)))
    while not ok:
        answer = Prompt().ask(
            "Please enter a comma separated list of numbers to select participants "
            f"(default: {default})",
            default=default,
        )
        numbers_str = answer.split(",")
        try:
            numbers = [int(number_str.strip()) for number_str in numbers_str]
            if not all(0 < n <= len(names) for n in numbers):
                raise ValueError(
                    "All numbers should be between 1 and the number of participants"
                )
            ok = True
        except Exception:
            console.print("Could not parse your selection, please try again.")
    selected_names = [names[i - 1] for i in numbers]
    name = choice(selected_names)
    draw_info = f"{name} was drawn randomly from {', '.join(selected_names)}"
    logger.info(draw_info)
    sendgrid_email = Mail(
        from_email=config.mail,
        to_emails=list(config.to.values()),
        subject=f"[deckz random] {reason}: {name} got picked",
        plain_text_content=draw_info,
    )
    client = SendGridAPIClient(config.api_key)
    client.send(sendgrid_email)


class MailsConfig(BaseModel):

    api_key: str
    mail: str
    to: Dict[str, EmailStr]

    @classmethod
    def from_global_paths(cls, paths: GlobalPaths) -> "MailsConfig":
        return cls.parse_obj(safe_load(paths.mails.read_text(encoding="utf8")))
