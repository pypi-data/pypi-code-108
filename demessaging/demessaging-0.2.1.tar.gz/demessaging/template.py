import pathlib
from dataclasses import field
from typing import Any, Dict

import jinja2
from pydantic.dataclasses import dataclass  # pylint: disable=no-name-in-module

TEMPLATE_FOLDER = pathlib.Path(__file__).parent / "templates"


@dataclass
class Template:
    """A convenience wrapper to render a jinja2 template."""

    name: str
    folder: pathlib.Path = TEMPLATE_FOLDER
    suffix: str = ".jinja2"
    context: Dict[str, Any] = field(default_factory=dict)

    @property
    def path(self) -> pathlib.Path:
        return self.folder / (self.name + self.suffix)

    @property
    def renderer(self) -> Any:
        loader = jinja2.FileSystemLoader(str(self.folder), followlinks=True)
        env = jinja2.Environment(loader=loader)
        return env.get_template(self.name + self.suffix)

    def render(self, **context) -> str:
        context.update(self.context)
        context["set"] = set
        return self.renderer.render(**context)
