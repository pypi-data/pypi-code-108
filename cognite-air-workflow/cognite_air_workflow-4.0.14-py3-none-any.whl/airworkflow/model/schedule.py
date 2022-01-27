import random
from pathlib import Path

import pandas as pd
from cognite.experimental import CogniteClient

import cognite.airworkflow.constants as const
import cognite.airworkflow.util.cdf as cdf
from cognite.airworkflow.model.config import Config, Schedule
from cognite.airworkflow.model.project import ProjectInfo


class DeploySchedule:
    def __init__(self, project: str, path: Path, config: Config):
        self.info: ProjectInfo = const.AUTHENTICATION[project]
        self.schedule: Schedule = config.schedule
        self.client: CogniteClient = cdf.experimental_client(self.info.project)
        self.model_name: str = path.parts[-1]
        self.model_name_latest: str = self.model_name + ":latest"
        self.functions = self.client.functions.list().to_pandas()

    def has_schedule(self) -> bool:
        schedules = self.client.functions.schedules.list().to_pandas()
        if schedules.shape[0]:
            schedules = schedules.query("functionExternalId.str.contains(@self.model_name_latest)")
            return schedules.shape[0] > 0
        return False

    def retrieve_model_external_id(self, series: pd.Series) -> str:
        return series[series.map(lambda x: x.split("/")[-1] == self.model_name + ":latest")].iloc[0]

    def create_schedule(self, model_external_id: str):
        ran = int(random.random() * 1e5)  # nosec
        return self.client.functions.schedules.create(
            function_external_id=model_external_id,
            name=self.model_name + "-" + str(ran),
            data={},
            description="",
            cron_expression=self.schedule.cron_expression,
        ).name

    def run(self) -> str:
        if not self.schedule.cron_expression:
            return ""

        if self.functions.shape[0] == 0:
            return ""

        if self.functions.query("externalId.str.contains(@self.model_name_latest)").shape[0] == 0:
            return ""

        if self.has_schedule():
            return ""

        model_external_id = self.retrieve_model_external_id(self.functions["externalId"])
        return self.create_schedule(model_external_id)
