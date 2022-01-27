import json
from typing import Iterator, List, Optional, Tuple, Union

import numpy as np
from cognite.experimental import CogniteClient
from cognite.experimental.data_classes import FunctionSchedule

from cognite.airworkflow.util.cdf import data_set_id

AIR_MODELS = "airModels"
AIR_INFRA = "airInfra"
AIR_DS_REPO = "cognitedata/air-ds-infrastructure"
DATA_SET_NAME = "AIR"


class Schedule:
    def __init__(
        self,
        model_name,
        schedule: Optional[dict] = None,
        schedule_asset_external_id: Optional[str] = None,
        id: Optional[int] = None,
    ):
        if not schedule:
            schedule = {}
        self.model: str = model_name
        self.cron_expression: Union[str, None] = schedule.get("cronExpression")
        self.schedule_asset_external_id: Union[str, None] = schedule_asset_external_id
        self.id: Union[int, None] = id

    @property
    def identifier(self):
        return f"{self.model}-{self.schedule_asset_external_id}"

    @property
    def function_external_id(self):
        return AIR_DS_REPO + self.model + ":latest"

    @property
    def data(self):
        return {"schedule_asset_ext_id": self.schedule_asset_external_id}

    def __eq__(self, other):
        return self.identifier == other.identifier and self.cron_expression == other.cron_expression

    def __hash__(self):
        return hash(self.identifier)

    def __repr__(self):
        return f"Schedule with schedule asset external id {self.schedule_asset_external_id}"


def retrieve_model_assets(client: CogniteClient, model_type: List = [AIR_MODELS, AIR_INFRA]) -> Iterator:
    air_assets = client.assets.list(data_set_ids=[data_set_id(client, DATA_SET_NAME)], limit=-1)
    air_model_assets = filter(lambda x: x.parent_external_id in model_type, air_assets)
    return air_model_assets


def retrieve_schedule_assets_external_ids(client: CogniteClient) -> List:
    air_model_assets = retrieve_model_assets(client)
    air_assets = client.assets.list(data_set_ids=[data_set_id(client, DATA_SET_NAME)], limit=-1)
    schedule_assets: List[str] = []
    for air_model_asset in air_model_assets:
        model_ext_id = air_model_asset.external_id
        schedule_assets += [i.external_id for i in filter(lambda x: x.parent_external_id == model_ext_id, air_assets)]
    return schedule_assets


def retrieve_dependency_of_model(client: CogniteClient, model_asset_external_id: str) -> List[str]:
    air_assets = client.assets.list(data_set_ids=[data_set_id(client, DATA_SET_NAME)], limit=-1)
    asset = list(filter(lambda x: model_asset_external_id == x.external_id, air_assets))
    if len(asset) == 0:
        return []
    dependencies_raw = asset[0].metadata.get("dependencies")
    if dependencies_raw:
        dependencies = json.loads(dependencies_raw)
        dependencies = [i.split("==")[0] for i in dependencies]
        additional_dependencies: List[str] = []
        for dependency in dependencies:
            additional_dependency = retrieve_dependency_of_model(client, dependency)
            if len(additional_dependency):
                additional_dependencies += additional_dependency
        dependencies += additional_dependencies
        return list(np.unique(dependencies))
    return []


def create_schedule_instance(client, model_schedule_external_id):
    air_assets = client.assets.list(data_set_ids=[data_set_id(client, DATA_SET_NAME)], limit=-1)
    schedule_asset = [i for i in filter(lambda x: model_schedule_external_id == x.external_id, air_assets)][0]
    end_model = [
        i
        for i in filter(
            lambda x: schedule_asset.parent_external_id == x.external_id,
            air_assets,
        )
    ][0]
    models = retrieve_dependency_of_model(client, end_model.external_id)
    models += [end_model.external_id]
    schedule_instances = []
    for model in models:
        model_asset = list(filter(lambda x: x.external_id == model, air_assets))
        if len(model_asset) == 0:
            continue
        model_asset = model_asset[0]
        schedule = model_asset.metadata.get("schedule")
        if schedule:
            schedule_info = json.loads(schedule)
        else:
            schedule_info = None
        schedule = Schedule(model, schedule_info, model_schedule_external_id)
        schedule_instances.append(schedule)
    return schedule_instances


def retrieve_schedule_asset_instances(client: CogniteClient) -> List:
    external_ids = retrieve_schedule_assets_external_ids(client)
    schedule_asset_instances: List[Schedule] = []
    for external_id in external_ids:
        schedule_asset_instances += create_schedule_instance(client, external_id)
    return schedule_asset_instances


def retrieve_air_schedules(client: CogniteClient) -> List[Schedule]:
    schedules = client.functions.schedules.list()
    model_assets = retrieve_model_assets(client)
    model_assets_external_ids = [i.external_id for i in model_assets]
    for schedule in schedules:
        schedule.model_ext_id = from_function_ext_id_to_model_name(schedule.function_external_id)
    schedules = filter(lambda x: schedule.model_ext_id in model_assets_external_ids, schedules)
    schedules = [function_schedule_to_schedule(i) for i in schedules]
    return schedules


def retrieve_schedule_assets(client: CogniteClient) -> Iterator:
    air_assets = client.assets.list(data_set_ids=[data_set_id(client, DATA_SET_NAME)], limit=-1)
    model_assets = retrieve_model_assets(client)
    model_external_ids = [m.external_id for m in model_assets]
    schedule_assets = filter(
        lambda a: a.parent_external_id in model_external_ids
        and "schedule" in a.name
        and a.metadata.get("deleted", "False") != "True",
        air_assets,
    )
    return schedule_assets


def from_function_ext_id_to_model_name(function_external_id: str) -> str:
    """Get the model name from function external id.
    For non-AIR models just return an empty string.
    """
    try:
        return function_external_id.split("/")[2].split(":")[0]
    except IndexError:
        return ""


def function_schedule_to_schedule(function_schedule: FunctionSchedule):
    model_name = from_function_ext_id_to_model_name(function_schedule.function_external_id)
    data = {}
    data.update({"cronExpression": function_schedule.cron_expression})
    return Schedule(model_name, data, function_schedule.description, function_schedule.id)


def retrieve_undeployed_schedule_assets(client: CogniteClient) -> List:
    deployed_schedules = retrieve_air_schedules(client)
    identifiers = [i.identifier for i in deployed_schedules]
    schedule_assets = retrieve_schedule_asset_instances(client)
    return [schedule_asset for schedule_asset in schedule_assets if schedule_asset.identifier not in identifiers]


def retrieve_deleted_schedules(client: CogniteClient) -> List:
    deployed_schedules = retrieve_air_schedules(client)
    schedule_assets = retrieve_schedule_asset_instances(client)
    identifiers = [i.identifier for i in schedule_assets]
    return [
        deployed_schedule for deployed_schedule in deployed_schedules if deployed_schedule.identifier not in identifiers
    ]


def retrieve_updated_schedules(client: CogniteClient) -> Tuple:
    deployed_schedules = retrieve_air_schedules(client)
    schedule_assets = retrieve_schedule_asset_instances(client)
    updated = set()
    to_be_deleted = set()
    for schedule_asset in schedule_assets:
        for deployed_schedule in deployed_schedules:
            if schedule_asset != deployed_schedule and schedule_asset.identifier == deployed_schedule.identifier:
                updated.add(schedule_asset)
                to_be_deleted.add(deployed_schedule)
    return updated, to_be_deleted


def delete_schedules(client, schedules: List[Schedule]):
    for schedule in schedules:
        client.functions.schedules.delete(schedule.id)


def create_schedules(client: CogniteClient, schedules: List[Schedule]):
    for schedule in schedules:
        client.functions.schedules.create(
            name=schedule.identifier,
            function_external_id=schedule.function_external_id,
            cron_expression=schedule.cron_expression,
            description=schedule.schedule_asset_external_id,
            data=schedule.data,
        )


def update_schedules(
    client: CogniteClient,
    schedules_update: List[Schedule],
    schedules_delete: List[Schedule],
):
    if len(schedules_delete):
        delete_schedules(client, schedules_delete)
    if len(schedules_update):
        create_schedules(client, schedules_update)


def execute(client):
    to_be_deleted: List[Schedule] = retrieve_deleted_schedules(client)
    if len(to_be_deleted):
        # delete_schedules(client, to_be_deleted)
        pass
    to_be_created: List[Schedule] = retrieve_undeployed_schedule_assets(client)
    if len(to_be_created):
        create_schedules(client, to_be_created)
    updated, to_be_deleted = retrieve_updated_schedules(client)
    update_schedules(client, updated, to_be_deleted)
    print(f"Deleted: {len(to_be_deleted)}, Created: {len(to_be_created)}, Updated: {len(updated)}", flush=True)
