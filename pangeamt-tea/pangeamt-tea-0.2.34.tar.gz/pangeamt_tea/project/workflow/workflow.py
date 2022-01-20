import os
import shutil
from pangeamt_tea.project.workflow.stage.stage_factory import StageFactory
from pangeamt_tea.project.workflow.stage.init_stage import InitStage
from pangeamt_tea.project.workflow.config import Config
from autoclass import autoclass


@autoclass
class Workflow:
    DIR = "workflow"

    def __init__(self, project, config):
        pass

    @staticmethod
    async def new(project, force=False):
        project_dir = project.config.project_dir
        workflow_dir = Workflow.get_dir(project_dir)
        if os.path.isdir(workflow_dir):
            if force:
                os.rmdir(workflow_dir)
            else:
                raise WorkflowAlreadyExists(project_dir)
        os.mkdir(workflow_dir)
        config = Config.new(workflow_dir)
        workflow = Workflow(project, config)
        init_stage = InitStage(workflow)
        await init_stage.run_with_time_report()
        return Workflow(project, config)

    @staticmethod
    def load(project):
        project_dir = project.config.project_dir
        workflow_dir = Workflow.get_dir(project_dir)
        if os.path.isdir(workflow_dir):
            config = Config.load(workflow_dir)
            return Workflow(project, config)
        else:
            raise WorkflowNotFound(project_dir)

    @staticmethod
    def remove(project):
        pass

    @staticmethod
    def get_dir(project_dir) -> str:
        return os.path.join(project_dir, Workflow.DIR)

    async def run_stage(self, stage_name, *args, **kwargs) -> None:
        runable_stage = self.config.get_runable_stage()
        if runable_stage is None and stage_name == "prepare":
            pass
        else:
            if runable_stage != stage_name:
                raise StageNotRunable(stage_name, Workflow.DIR)

        stage = StageFactory.new(stage_name, self)

        await stage.run_with_time_report(*args, **kwargs)

    def show(self) -> None:
        self.config.show()

    def reset(self, project_dir) -> None:
        shutil.rmtree(os.path.join(project_dir, Workflow.DIR))

    def reset_stage(self, stage_name: str, project_dir: str) -> None:
        self.config.reset_stage(stage_name, project_dir, self)


class WorkflowNotFound(Exception):
    def __init__(self, project_dir):

        message = f"Workflow not found in project {project_dir} "
        super().__init__(message)


class WorkflowAlreadyExists(Exception):
    def __init__(self, project_dir):

        message = f"The workflow already exists in project {project_dir} "
        super().__init__(message)


class StageNotRunable(Exception):
    def __init__(self, stage_name, project_dir):
        message = (
            f"Unable to run {stage_name}, either it has been already runned or "
            "needs another stage to run first."
        )
        super().__init__(message)
