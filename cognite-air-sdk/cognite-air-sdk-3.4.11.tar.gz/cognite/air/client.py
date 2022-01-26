from typing import Any, Dict, List, Optional

from cognite.air._api import AIRClientError
from cognite.air._backfilling_api import AIRBackfillingAPI, NoBackfillAPI
from cognite.air._config import AIRClientConfig
from cognite.air._events_api import AIREventsAPI
from cognite.air._time_series_api import AIRTimeSeriesAPI
from cognite.air._utils import (
    get_local_testing,
    path_to_yaml,
    retrieve_backfilling,
    retrieve_field_definitions,
    retrieve_local_testing,
    retrieve_model_name,
    retrieve_model_version,
)
from cognite.air.constants import (
    AIR_DATA_DEV_WRITE_BACK,
    AIR_TYPES,
    LEGAL_FIELD_TYPES,
    MA_FIELD_META_FIELDS,
    MA_FIELD_META_MODELVERSION,
    MA_FIELD_META_MTDESCRIPTION,
    MA_FIELD_META_MTNAME,
    SA_EXT_ID,
    SA_FIELD_META_DATA,
)
from cognite.air.utils import air_data_set_id, is_string_truthy, parse_json_if_json
from cognite.client import CogniteClient
from cognite.client.data_classes import Asset, TimeSeries


class AIRClient:
    """The AIRClient.
        For local testing pass all fields of the model specified in the config.yaml,
        as well as the name of the model (folder name) and the path to the config.yaml.
        If the test run should write back to Cognite Data Fusion also pass in `"dev": "True"`

    Args:
        data (Dict): Dictionary.
        client (CogniteClient): CogniteClient
        secrets (Dict): Secrets.

    """

    def __init__(self, data: Dict[str, Any], client: CogniteClient, secrets: Dict[str, Any], debug: bool = False):
        del secrets  # Unused for now (required in function signature)
        self._testing = get_local_testing(data)
        backfilling_asset = None
        if not self._testing:
            sa_ext_id = self._extract_and_validate_sa_ext_id(data)
            schedule_asset = self._retrieve_and_verify_schedule_asset(client, sa_ext_id)
            model_asset = self._retrieve_and_verify_model_asset(client, schedule_asset.parent_external_id)
            model_version = model_asset.metadata[MA_FIELD_META_MODELVERSION]
            # Retrieve backfilling asset if the model uses backfilling:
            if is_string_truthy(model_asset.metadata.get("backfill")):
                backfilling_asset = self._retrieve_and_verify_backfill_asset(client, sa_ext_id, model_version)

            self._config = AIRClientConfig(
                client=client,
                data_set_id=schedule_asset.data_set_id,
                schedule_asset=schedule_asset,
                schedule_asset_id=schedule_asset.id,
                schedule_asset_ext_id=sa_ext_id,
                data_fields=parse_json_if_json(schedule_asset.metadata.get(SA_FIELD_META_DATA)) or {},
                data_fields_defs=self.create_data_field_dct(model_asset.metadata.get(MA_FIELD_META_FIELDS)),
                model_name=model_asset.name,
                model_version=model_version,
                local_testing=False,
                dev_write_back=False,
            )

        else:
            dev_write_back = retrieve_local_testing(data, AIR_DATA_DEV_WRITE_BACK, False)
            model_version = retrieve_model_version(data)
            sa_ext_id = "ScheduleAssetTestExtId"
            model_name = retrieve_model_name(data)
            fake_data_set_id = 123
            fake_schedule_asset_id = 123
            fake_backfill_completed = data.get("backfill_completed", "False")
            fake_backfilled_until = data.get("backfilled_until", "0")

            if is_string_truthy(retrieve_backfilling(data)) and is_string_truthy(data.get("backfilling")):
                backfilling_asset = self.create_fake_backfilling_asset(
                    model_name,
                    fake_schedule_asset_id,
                    sa_ext_id,
                    fake_data_set_id,
                    fake_backfill_completed,
                    fake_backfilled_until,
                    model_version,
                )
            yaml_path = path_to_yaml(data)
            self._config = AIRClientConfig(
                client=client,
                data_set_id=air_data_set_id(client, "AIR") if dev_write_back else fake_data_set_id,
                schedule_asset=Asset(metadata={"dashboardId": "dashboard123", "systemId": "system123"}),
                schedule_asset_id=fake_schedule_asset_id,
                schedule_asset_ext_id=sa_ext_id,
                data_fields=data,
                data_fields_defs=self.create_data_field_dct(retrieve_field_definitions(yaml_path)),
                model_name=model_name,
                model_version=model_version,
                local_testing=True,
                dev_write_back=dev_write_back,
            )
        self.events = AIREventsAPI(self._config)
        self.time_series = AIRTimeSeriesAPI(self._config)
        self.backfilling = NoBackfillAPI()
        if backfilling_asset:
            backfilling = AIRBackfillingAPI(self._config, backfilling_asset)
            if backfilling.in_progress:
                self.backfilling = backfilling  # type: ignore

        if debug or self._testing:
            print(
                f"Tenant: {client.config.project}\nSchedule asset ext. ID: {self._config.schedule_asset_ext_id}\n"
                f"Model name: {self._config.model_name}\nModel version: {self._config.model_version}\n"
                f"Backfilling in progress: {self.backfilling.in_progress}\n"
            )

    @property
    def config(self):
        return self._config

    @property
    def cognite_client(self):
        return self._config.client

    @property
    def schedule_asset_id(self):
        return self._config.schedule_asset_id

    @property
    def schedule_asset_ext_id(self):
        return self._config.schedule_asset_ext_id

    @property
    def schedule_external_id(self):
        """Retrieve the unique external ID of the underlying schedule. Helpful when creating Time Series with unique
        external IDs.
        """
        return self._config.schedule_asset_ext_id

    @property
    def model_name(self):
        return self._config.model_name

    @property
    def model_version(self):
        return self._config.model_version

    @property
    def schedule_front_end_name(self):
        return self._config.schedule_asset.metadata.get(MA_FIELD_META_MTNAME)

    def set_schedule_front_end_name(self, name):
        if name != self.schedule_front_end_name:
            self._config.schedule_asset.metadata[MA_FIELD_META_MTNAME] = name
            self.cognite_client.assets.update(self._config.schedule_asset)

    @property
    def schedule_front_end_description(self):
        return self._config.schedule_asset.metadata.get(MA_FIELD_META_MTDESCRIPTION)

    def set_schedule_front_end_description(self, description):
        if description != self.schedule_front_end_description:
            self._config.schedule_asset.metadata[MA_FIELD_META_MTDESCRIPTION] = description
            self.cognite_client.assets.update(self._config.schedule_asset)

    def retrieve_fields(self, field_names: List[str]) -> List[AIR_TYPES]:
        if not isinstance(field_names, list) or not all(isinstance(s, str) for s in field_names):
            raise TypeError(f"Expected '{field_names}' to be a list of strings!")

        fields = list(map(self._config.data_fields.get, field_names))
        if None in fields:
            err_field_names = [id for id, field in zip(field_names, fields) if field is None]
            raise ValueError(f"The following field names were not found: {err_field_names}")

        return [
            self.convert_field_type(
                field_type=self._config.data_fields_defs[id]["python-type"], user_field_input=parse_json_if_json(field)
            )
            for id, field in zip(field_names, fields)
        ]

    def convert_field_type(self, field_type, user_field_input):
        # NB: We start with bool, because bool(string) is True for all non-empty strings
        #     and we can never have "more than one":
        if field_type is bool:
            return is_string_truthy(user_field_input)

        # If user input is 'list', that means 'multiple=True' and we must apply 'type' to all items.
        # TimeSeries and Assets are special, as they are passed by string (external ids):
        if isinstance(user_field_input, list):
            if field_type is TimeSeries:
                return self.cognite_client.time_series.retrieve_multiple(
                    external_ids=user_field_input, ignore_unknown_ids=False
                )
            if field_type is Asset:
                return self.cognite_client.assets.retrieve_multiple(
                    external_ids=user_field_input, ignore_unknown_ids=False
                )
            return list(map(field_type, user_field_input))  # Simple stuff: str/int/float

        if field_type is TimeSeries:
            # We use 'retrieve_multiple' becuase it throws error when external_id is missing:
            return self.cognite_client.time_series.retrieve_multiple(
                external_ids=[user_field_input], ignore_unknown_ids=False
            )[0]
        if field_type is Asset:
            return self.cognite_client.assets.retrieve_multiple(
                external_ids=[user_field_input], ignore_unknown_ids=False
            )[0]

        return field_type(user_field_input)

    def retrieve_field(self, field_name: str) -> AIR_TYPES:
        if not isinstance(field_name, str):
            raise TypeError(f"Expected 'field_name' to be of type {str}, not {type(field_name)}")
        return self.retrieve_fields([field_name])[0]

    @staticmethod
    def convert_type_info(dct):
        python_type = LEGAL_FIELD_TYPES.get(dct["type"])
        if python_type is None:
            raise TypeError(f"Field type '{dct['type']}' not understood. Legal values: {set(LEGAL_FIELD_TYPES)}")
        dct["python-type"] = python_type
        return dct

    def create_data_field_dct(self, json: Optional[str]):
        lst_of_field_defs = parse_json_if_json(json) or []
        return {dct.pop("id"): self.convert_type_info(dct) for dct in lst_of_field_defs}

    @staticmethod
    def _extract_and_validate_sa_ext_id(data):
        sa_ext_id = data.get(SA_EXT_ID)
        if sa_ext_id is None:
            raise KeyError(f"Missing required input field '{SA_EXT_ID}'")
        if not isinstance(sa_ext_id, str):
            raise TypeError(f"Expected field '{SA_EXT_ID}' to be of type {str}, not {type(sa_ext_id)}")
        return sa_ext_id

    @staticmethod
    def _retrieve_and_verify_schedule_asset(client, sa_ext_id):
        schedule_asset = client.assets.retrieve(external_id=sa_ext_id)
        if schedule_asset is None:
            raise AIRClientError(f"Asset not found: No 'schedule asset' with external_id: '{sa_ext_id}'")
        if is_string_truthy(schedule_asset.metadata.get("deleted")):
            raise AIRClientError(
                f"Monitoring task given by 'schedule asset' with external_id: '{sa_ext_id}' indicates that "
                "it has been deleted and should not be run! Reschedule it from the front-end!"
            )
        return schedule_asset

    @staticmethod
    def _retrieve_and_verify_model_asset(client, model_ext_id):
        model_asset = client.assets.retrieve(external_id=model_ext_id)
        if model_asset is None:
            raise AIRClientError(f"Asset not found: No 'model asset' with external_id: '{model_ext_id}'")
        return model_asset

    @staticmethod
    def _retrieve_and_verify_backfill_asset(client, sa_ext_id, model_version):
        backfill_asset_list = client.assets.list(parent_external_ids=[sa_ext_id], metadata={"version": model_version})
        if len(backfill_asset_list) == 1:
            return backfill_asset_list[0]
        raise AIRClientError(
            f"Found {len(backfill_asset_list)} backfilling asset(s). Expected exactly 1 backfilling asset"
        )

    @staticmethod
    def create_fake_backfilling_asset(
        model_name: str,
        schedule_asset_id: int,
        schedule_asset_ext_id: str,
        data_set_id: int,
        backfill_complete: str,
        backfilled_until: str,
        model_version: str,
    ):
        bf_asset_dict = {
            "external_id": "bf1234",
            "name": f"{model_name} backfill",
            "parent_id": schedule_asset_id,
            "parent_external_id": schedule_asset_ext_id,
            "data_set_id": data_set_id,
            "metadata": {
                "backfill_complete": backfill_complete,
                "backfilled_until": backfilled_until,
                "call_lock": "1234",
                "model": schedule_asset_id,
                "version": model_version,
            },
            "id": 123456,
            "root_id": 6789,
        }
        return Asset(**bf_asset_dict)
