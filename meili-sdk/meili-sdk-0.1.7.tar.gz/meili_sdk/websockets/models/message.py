import typing as t

from meili_sdk.exceptions import MissingAttributesException, ValidationError
from meili_sdk.models.base import BaseModel
from meili_sdk.websockets.constants import (
    ALL,
    EVENT_REGISTER,
    EVENT_LOCATION,
    EVENT_BATTERY,
    EVENT_GOAL_STATUS,
    EVENT_TOPICS_LIST,
    EVENT_TOPIC_DATA,
    EVENT_PATH_DATA,
)

__all__ = ("Message",)


class Message(BaseModel):
    """
    Message to be sent via websocket

    Some pre-sending validation is done here
    """

    event: str
    value: t.Optional[dict] = None
    vehicle: t.Optional[str] = None
    vehicles: t.Optional[t.List[str]] = None

    def __init__(self, *, event, **kwargs) -> None:
        if event not in ALL:
            raise ValueError("Invalid event")

        if event == EVENT_REGISTER:
            if "vehicles" not in kwargs:
                raise MissingAttributesException(self.__class__, "vehicles")
        else:
            if "vehicle" not in kwargs:
                raise MissingAttributesException(self.__class__, "vehicles")
            if "value" not in kwargs:
                raise MissingAttributesException(self.__class__, "value")

        kwargs["event"] = event
        super().__init__(**kwargs)

    def validate_value(self):
        value = self.value
        event = self.event

        {
            EVENT_REGISTER: self._validate_value_for_registration,
            EVENT_LOCATION: self._validate_value_for_location,
            EVENT_BATTERY: self._validate_value_for_battery,
            EVENT_GOAL_STATUS: self._validate_value_for_goal_status,
            EVENT_TOPICS_LIST: self._validate_value_for_topics_list,
            EVENT_TOPIC_DATA: self._validate_value_for_topic_data,
            EVENT_PATH_DATA: self._validate_value_for_path_data,
        }[event](value)
        return value

    def _validate_value_for_registration(self, _):
        vehicles = self.vehicles

        if not isinstance(vehicles, (list, tuple, set)):
            raise ValidationError("Vehicles requires an iterable type")

    @staticmethod
    def _validate_value_for_location(value):
        sets = (
            {"x", "y"},
            {"xm", "ym"},
            {"lat", "lon"},
        )
        given_keys = set(value.keys())

        if not any([len(key_set - given_keys) == 0 for key_set in sets]):
            raise ValidationError(
                f"Location value needs to have one of the following full pairs: (x,y), (xm, ym) or (lat, lon)"
            )

    def _validate_value_for_battery(self, value):
        pass

    @staticmethod
    def _validate_value_for_goal_status(value):
        missing_keys = {"status_id", "goal_id"} - set(value.keys())
        if len(missing_keys) > 0:
            raise ValidationError(f"Missing keys: {', '.join(missing_keys)}")

    @staticmethod
    def _validate_value_for_topics_list(value):
        if not isinstance(value, list):
            raise ValidationError("Value needs to be a list")
        for val in value:
            if not isinstance(val, dict):
                raise ValidationError("Each item in value needs to be a dictionary")

            missing_keys = {"topic", "messageType"} - val.keys()

            if len(missing_keys) > 0:
                raise ValidationError(f"Missing properties: {', '.join(missing_keys)}")

    def _validate_value_for_topic_data(self, value):
        pass

    @staticmethod
    def _validate_value_for_path_data(value):
        if "path" not in value:
            raise ValidationError(f"Missing properties: path")
        path = value["path"]
        if not isinstance(path, (list, set, tuple)):
            raise ValidationError("path needs to be a list of lists")

        for path_point in path:
            if not isinstance(path_point, (list, set, tuple)):
                raise ValidationError("path needs to be a list of lists")
