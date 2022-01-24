from typing import Optional

from tktl.core.loggers import LOG
from tktl.core.managers.project import ProjectManager
from tktl.core.t import TemplateT


def init_project(path: Optional[str], name: str, template: TemplateT):
    project_path = ProjectManager.init_project(path, name, template)
    LOG.log(
        f"Project scaffolding created successfully at {project_path}", color="green",
    )
