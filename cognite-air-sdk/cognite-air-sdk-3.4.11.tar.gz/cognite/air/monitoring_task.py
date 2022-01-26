import json
import pprint
from typing import Any, Dict, Optional, Union

import requests

from cognite.air._air_api_url import retrieve_air_api_url
from cognite.client import CogniteClient
from cognite.client.exceptions import CogniteAPIError


class MonitoringTaskCreator:
    """Class to create monitoring task via Python

    Args:
        client (CogniteClient): The client to associate with this object.
        model_name (str): Name of the model the monitoring task should be created for.
        show_fields (bool): Print out the fields for the model in question.

    """

    def __init__(self, client: CogniteClient, model_name: str, show_fields: bool = True):

        self.client = client
        self.model_name = model_name
        self._project_url = retrieve_air_api_url(client)
        self.model = self._retrieve_model()
        self.fields = json.loads(self.model["metadata"]["fields"])
        if show_fields:
            pprint.pprint(self.fields)

    def _retrieve_models(self):
        url = f"{self._project_url}/models"
        headers = {"api-key": self.client.config.api_key, "Content-Type": "application/json"}
        r = requests.get(url, headers=headers)
        return json.loads(r.content.decode("utf-8"))["models"]

    def _retrieve_model(self):
        models = self._retrieve_models()
        model = [i for i in models if i["externalId"] == self.model_name]
        if len(model) == 0:
            raise ValueError(f"Model with external id {self.model_name} does not exist")
        return model[0]

    def _validate(self, arguments):
        field_ids = [i["id"] for i in self.fields]
        for i in field_ids:
            if i not in arguments.keys():
                raise ValueError(f"Field {i} needs to be defined.")
        for field in self.fields:
            argument = arguments[field["id"]]
            error = False
            if field["type"] == "TimeSeries":
                error = self._validate_time_series(argument)
            elif field["type"] == "Asset":
                error = self._validate_asset(argument)
            elif field["type"] == "bool":
                error = self._validate_bool(argument)
            elif field["type"] == "float":
                error = self._validate_float(argument)
            elif field["type"] == "str":
                error = self._validate_str(argument)

            if error:
                raise ValueError(f"{field['id']} is not of type {field['type']} or is empty.")

    def _validate_time_series(self, time_series):
        return self.client.time_series.retrieve(external_id=time_series) is None

    def _validate_asset(self, asset):
        return self.client.assets.retrieve(external_id=asset) is None

    def _validate_bool(self, boolean):
        return not isinstance(boolean, bool)

    def _validate_float(self, number):
        return not (isinstance(number, float) or isinstance(number, int))

    def _validate_str(self, string):
        return string == ""

    def _create_payload(
        self, data: Dict[str, Any], space_id: str, group_id: str, name_of_monitoring_task: Optional[str] = None
    ) -> Dict:
        payload = {}
        payload["project"] = self.client.config.project
        schedule: Dict[str, Union[str, Dict]] = {}
        schedule["name"] = name_of_monitoring_task if name_of_monitoring_task else f"{self.model_name} schedule"
        schedule["modelId"] = str(self.model["id"])
        schedule["modelExternalId"] = self.model["externalId"]
        schedule["dashboardId"] = space_id
        schedule["systemId"] = group_id
        schedule["data"] = data
        payload["schedule"] = schedule
        return payload

    def create(self, space_id: str, group_id: str, name_of_monitoring_task: Optional[str] = None, **kwargs):
        """Create Monitoring Task in a specific Space and Group.

        The `space_id` and `group_id` can be extracted from the url:
        `https://air.cogniteapp.com/my_project/space/123/group/567`

        123 would be the `space_id` and 567 would be the `group_id`.

        Args:
            space_id (str): The id for the Space where the Monitoring Task is created in.
            group_id (str): The id for the Group where the Monitoring Task is created in.
            name_of_monitoring_task (str): Optional name for the Monitoring Task
            kwargs: Keyword arguments that specify the fields for the specific model.

        Examples:
            >>> from cognite.client import CogniteClient
            >>> from cognite.air.monitoring_task import MonitoringTaskCreator
            >>> c = CogniteClient()
            >>> mt = MonitoringTaskCreator(c, "my_model")
            >>> mt.create(space_id="123",
            ...         group_id="567",
            ...         time_series_field="external_id_of_ts",
            ...         threshold=50)




        """
        self._validate(kwargs)
        data = {k: str(v) for k, v in kwargs.items()}
        payload = self._create_payload(data, space_id, group_id, name_of_monitoring_task)
        # TODO: check if schedule asset in this form already exists!
        self._create_schedule_asset(payload)

    def _create_schedule_asset(self, payload: Dict):
        url = f"{self._project_url}/schedule"
        headers = {"api-key": self.client.config.api_key, "Content-Type": "application/json"}
        r = requests.post(url, data=json.dumps(payload), headers=headers)
        if r.status_code != 200:
            raise CogniteAPIError(r.reason)
