from typing import Optional
from autoclass import autoclass
from pangeamt_tea.project.workflow.workflow import Workflow
from pangeamt_tea.project.config import Config
import pathlib


@autoclass
class Project:
    def __init__(self, config: Config, workflow: Optional[Workflow]):
        pass

    @staticmethod
    def new(
        customer: str,
        src_lang: str,
        tgt_lang: str,
        parent_dir: pathlib.Path,
        version: int = 1,
        flavor: Optional[str] = None,
    ) -> "Project":

        # Create the project directory
        project_dir_name = f"{customer}_{src_lang}_{tgt_lang}"
        if flavor is not None:
            project_dir_name += f"_{flavor}"
        if version != 1:
            project_dir_name += f"_{version}"

        project_dir = parent_dir.joinpath(project_dir_name)
        if project_dir.is_dir():
            raise ProjectAlreadyExistsException(project_dir)

        try:
            project_dir.mkdir()
        except Exception as e:
            raise ProjectDirCreateException(project_dir, e)

        # Create the config file
        config = Config(
            project_dir=project_dir,
            customer=customer,
            src_lang=src_lang,
            tgt_lang=tgt_lang,
            flavor=flavor,
            version=version,
        )
        config.save()

        # Create the data dir
        config.data_dir.mkdir()

        # Return the project object
        return Project(config, None)

    @staticmethod
    def load(project_dir: pathlib.Path) -> "Project":
        if not project_dir.is_dir():
            raise ProjectNotFoundException(project_dir)
        config = Config.load(project_dir)
        return Project(config, None)

    # async def new_workflow(self, force):
    #     return await Workflow.new(self, force)


class ProjectAlreadyExistsException(Exception):
    def __init__(self, project_dir: pathlib.Path):
        super().__init__(f"`{project_dir}` already exists")


class ProjectNotFoundException(Exception):
    def __init__(self, project_dir: pathlib.Path):
        super().__init__(f"`Project dir {project_dir} not found ")


class ProjectDirCreateException(Exception):
    def __init__(self, project_dir: pathlib.Path, e: Exception):
        super().__init__(f"`Unable to create project dir {project_dir}. {e}")
