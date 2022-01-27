from abc import ABC

from dkist_processing_common.tasks import ScienceTaskL0ToL1Base

from dkist_processing_vbi.models.constants import VbiConstants


class VbiScienceTask(ScienceTaskL0ToL1Base, ABC):
    def __init__(self, recipe_run_id: int, workflow_name: str, workflow_version: str):
        super().__init__(recipe_run_id, workflow_name, workflow_version)
        self.constants = VbiConstants(self._constants_db)
