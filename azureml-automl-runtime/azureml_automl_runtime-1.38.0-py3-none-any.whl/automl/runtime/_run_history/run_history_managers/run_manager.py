# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Any, Dict, Optional, Type

from azureml._restclient.models.run_dto import RunDto
from azureml.core import Experiment, Run


class RunManager:
    """This is wrapper class around a single run, designed to manage its interactions with AML services.
    Current run APIs may lend themselves to higher network usage than is ideal.
    TODO: there are plans to extend this class in subsequent PRs."""

    def __init__(self, experiment: Experiment, run_dto: RunDto) -> None:
        self.run = Run._dto_to_run(experiment, run_dto)

    @classmethod
    def create_from_run(cls: Type['RunManager'], run: Run) -> 'RunManager':
        return RunManager(run.experiment, run._client.run_dto)

    def create_child_run(
        self,
        run_id: str,
        properties: Optional[Dict[str, Any]] = None,
        tags: Optional[Dict[str, Any]] = None
    ) -> "RunManager":
        child_run_dto = self.run._client.create_child_run(
            run_id=run_id,
            name=self.run._client.run_dto.name,
            target=self.run._client.run_dto.target,
            properties=properties,
            tags=tags)
        return RunManager(self.run.experiment, child_run_dto)
