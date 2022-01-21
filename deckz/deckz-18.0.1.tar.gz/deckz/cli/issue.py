from logging import getLogger
from pathlib import Path
from typing import Optional

from pydantic import BaseModel
from typer import Argument, Option
from yaml import safe_load

from deckz.cli import app
from deckz.github_querying import GitHubAPI
from deckz.paths import GlobalPaths


@app.command()
def issue(
    title: str = Argument(..., help="Title of the issue"),
    body: Optional[str] = Argument(None, help="Body of the issue"),
    workdir: Path = Option(
        Path("."), help="Path to move into before running the command"
    ),
) -> None:
    """Create an issue on GitHub."""
    logger = getLogger(__name__)
    config = IssuesConfig.from_global_paths(GlobalPaths.from_defaults(workdir))
    api = GitHubAPI(config.api_key)
    url = api.create_issue(config.owner, config.repo, title, body, config.project)
    logger.info(
        f"Successfully created the issue [link={url}]on GitHub[/link]",
        extra=dict(markup=True),
    )


class IssuesConfig(BaseModel):

    api_key: str
    repo: str
    owner: str
    project: Optional[int] = None

    @classmethod
    def from_global_paths(cls, paths: GlobalPaths) -> "IssuesConfig":
        return cls.parse_obj(safe_load(paths.github_issues.read_text(encoding="utf8")))
