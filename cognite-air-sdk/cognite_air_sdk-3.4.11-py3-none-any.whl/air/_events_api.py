import enum
import hashlib
from types import MappingProxyType
from typing import Any, Dict, List, Union

from cognite.air._api import BaseAPIClient
from cognite.air.constants import (
    AIR_ALERT_EVENTS_FIELD_SUBTYPE,
    AIR_EVENTS_FIELD_SUBTYPE,
    AIR_EVENTS_FIELD_TYPE,
    AIR_LOCAL_TESTING_ERROR_MESSAGE,
    EVENT_ASSET_IDS,
    EVENT_DATA_SET_ID,
    EVENT_DATA_SET_IDS,
    EVENT_EXT_ID,
    EVENT_METADATA,
    EVENT_SUBTYPE,
    EVENT_TYPE,
    AIREventMeta,
)
from cognite.air.utils import air_data_set_id, is_string_truthy, valfilter, valmap
from cognite.client.data_classes import Event, EventList


@enum.unique
class EventEndpoints(enum.Enum):
    LIST = enum.auto()
    CREATE = enum.auto()


class AIREventsAPI(BaseAPIClient):
    RESERVED_AIR_EVENT_META_KEYS = AIREventMeta.get_reserved_meta_key_set()
    RESERVED_PARAMS_DCT = MappingProxyType(
        {
            EventEndpoints.LIST: set([EVENT_TYPE, EVENT_SUBTYPE, EVENT_DATA_SET_IDS]),
            EventEndpoints.CREATE: set([EVENT_EXT_ID, EVENT_TYPE, EVENT_SUBTYPE, EVENT_DATA_SET_ID]),
        }
    )

    @property
    def air_event_required_meta(self):
        fields_dict = {
            AIREventMeta.model: self._config.model_name,
            AIREventMeta.model_version: self._config.model_version_stripped,
            AIREventMeta.sa_ext_id: self._config.schedule_asset_ext_id,
        }
        if (
            AIREventMeta.parent_template_group_ext_id in self._config.schedule_asset.metadata
            and AIREventMeta.parent_template_instance_ext_id in self._config.schedule_asset.metadata
            and AIREventMeta.schedule_asset_type in self._config.schedule_asset.metadata
            and AIREventMeta.template_name in self._config.schedule_asset.metadata
        ):
            fields_dict[AIREventMeta.parent_template_group_ext_id] = self._config.schedule_asset.metadata[
                AIREventMeta.parent_template_group_ext_id
            ]
            fields_dict[AIREventMeta.parent_template_instance_ext_id] = self._config.schedule_asset.metadata[
                AIREventMeta.parent_template_instance_ext_id
            ]

            fields_dict[AIREventMeta.template_name] = self._config.schedule_asset.metadata[AIREventMeta.template_name]

            fields_dict[AIREventMeta.schedule_asset_type] = self._config.schedule_asset.metadata[
                AIREventMeta.schedule_asset_type
            ]
            return fields_dict
        else:

            fields_dict[AIREventMeta.dashboard_id] = self._config.schedule_asset.metadata[AIREventMeta.dashboard_id]
            fields_dict[AIREventMeta.system_id] = self._config.schedule_asset.metadata[AIREventMeta.system_id]

            return fields_dict

    def _create_air_attr_dct(self, meta):
        return {
            EVENT_TYPE: AIR_EVENTS_FIELD_TYPE,
            EVENT_SUBTYPE: AIR_EVENTS_FIELD_SUBTYPE,
            EVENT_METADATA: {**meta, **self.air_event_required_meta},
        }

    def _create_air_alert_attr_dct(self, meta):
        notification = is_string_truthy(meta.get("sendNotification", True))
        return {
            EVENT_TYPE: AIR_EVENTS_FIELD_TYPE,
            EVENT_SUBTYPE: AIR_ALERT_EVENTS_FIELD_SUBTYPE,
            EVENT_METADATA: {
                **meta,
                **self.air_event_required_meta,
                AIREventMeta.original_model_version: self._config.model_version_stripped,
                AIREventMeta.project_name: self._config.client.config.project,
                AIREventMeta.skip_notification: str(not notification),
                AIREventMeta.acknowledged: str(not notification),
                AIREventMeta.show: str(meta.get(AIREventMeta.show, True)),
            },
        }

    def _verify_valid_air_event_query(self, endpoint: EventEndpoints, query_dct: Dict) -> None:
        reserved_params = self.RESERVED_PARAMS_DCT.get(endpoint)
        if reserved_params is None:
            raise TypeError(f"Expected 'endpoint' to be an {EventEndpoints}, not {type(endpoint)}")

        illegal_params = reserved_params.intersection(query_dct)
        if illegal_params:
            raise ValueError(f"Got one or more parameters reserved for AIR: {illegal_params}")

        kw_meta = query_dct.get(EVENT_METADATA, {})
        illegal_meta_keys = self.RESERVED_AIR_EVENT_META_KEYS.intersection(kw_meta)
        if illegal_meta_keys:
            raise ValueError(f"{EVENT_METADATA} contained one or more keys reserved for AIR: {illegal_meta_keys}")

    def _create_event_external_id(self, ev_dct: Dict[str, Any]) -> str:
        dcts = self.air_event_required_meta, ev_dct, ev_dct.get(EVENT_METADATA, {})
        hash_input = "".join((f"{k}{v}" for d in dcts for k, v in d.items() if isinstance(v, (str, int, float, bool))))
        return hashlib.md5(hash_input.encode()).hexdigest()  # nosec

    def _handle_asset_ids(self, param_dct: Dict) -> List[int]:
        asset_ids = param_dct.get(EVENT_ASSET_IDS, [])
        if not isinstance(asset_ids, list):
            asset_ids = [asset_ids]  # Single given
        if not all(isinstance(a_id, int) for a_id in asset_ids):
            raise TypeError(f"One or more asset ids were not integers! {asset_ids}")
        # We always include link to the schedule asset:
        if asset_ids:
            asset_ids.append(self._config.schedule_asset_id)
            return list(set(asset_ids))
        return [self._config.schedule_asset_id]

    def _make_events_air_compatible_inplace(self, events: List[Event], *, is_alert: bool) -> None:
        for ev in events:
            param_dct = valfilter(lambda v: v is not None, vars(ev))
            self._verify_valid_air_event_query(EventEndpoints.CREATE, param_dct)

            _attr_fn = self._create_air_alert_attr_dct if is_alert else self._create_air_attr_dct
            attr_dct = _attr_fn(meta=valmap(str, ev.metadata or {}))
            attr_dct.update(
                {
                    EVENT_DATA_SET_ID: self._config.data_set_id,
                    EVENT_EXT_ID: self._create_event_external_id(param_dct),
                    EVENT_ASSET_IDS: self._handle_asset_ids(param_dct),
                }
            )
            for attr, val in attr_dct.items():
                setattr(ev, attr, val)

    def _create(self, event: Union[Event, List[Event]], *, is_alert: bool) -> Union[Event, EventList]:
        single_item = not isinstance(event, list)
        items = [event] if single_item else event
        if any(not isinstance(ev, Event) for ev in items):
            raise TypeError(f"Expected single (or list of) Event object(s) ({Event})")

        self._make_events_air_compatible_inplace(items, is_alert=is_alert)
        if self._config.local_testing and not self._config.dev_write_back:
            raise ValueError(AIR_LOCAL_TESTING_ERROR_MESSAGE)
        if self._config.dev_write_back:
            for item in items:
                item.asset_ids = None
                item.data_set_id = air_data_set_id(self._config.client, "AIR")
        else:
            for item in items:
                item.data_set_id = self._config.data_set_id
        return self.client.events.create(items[0] if single_item else items)

    def create(self, event: Union[Event, List[Event]]) -> Union[Event, EventList]:
        """Create an AIR Event or a list of AIR Events.

        The Events will be versioned but not seen through the front end (for that use the `create_alert` method).

        Args:
            event (Union[Event, List[Event]]): Event or a list of Events

        Returns:
            (nion[Event, EventList]: Created Event or EventList

        """
        return self._create(event, is_alert=False)

    def create_alert(self, event: Union[Event, List[Event]]) -> Union[Event, EventList]:
        """Create one or more alert event(s) that by default are shown in front end.

        Pass event(s) with metadata field 'show' set to 'False' to hide.

        Args:
            event (Union[Event, List[Event]]): Event or a list of Events

        Returns:
            Union[Event, EventList]: Created Event or EventList
        """
        return self._create(event, is_alert=True)

    def _list(self, *, subtype, user_kwargs) -> EventList:
        self._verify_valid_air_event_query(EventEndpoints.LIST, user_kwargs)
        air_kwargs = self._create_air_attr_dct(meta=user_kwargs.pop(EVENT_METADATA, {}))
        air_kwargs.update(dict(subtype=subtype, data_set_ids=[self._config.data_set_id]))
        return self.client.events.list(**user_kwargs, **air_kwargs)

    def list(self, **kwargs) -> EventList:
        return self._list(subtype=AIR_EVENTS_FIELD_SUBTYPE, user_kwargs=kwargs)

    def list_alerts(self, **kwargs) -> EventList:
        return self._list(subtype=AIR_ALERT_EVENTS_FIELD_SUBTYPE, user_kwargs=kwargs)
