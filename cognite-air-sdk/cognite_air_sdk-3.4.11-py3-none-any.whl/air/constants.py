from typing import Union

from cognite.client.data_classes import Asset, AssetList, TimeSeries, TimeSeriesList

# Local Testing
AIR_DATA_LOCAL_TESTING = "AIR_local_test"
AIR_DATA_PATH_TO_YAML = "path_to_yaml"
AIR_DATA_MODEL_NAME = "model_name"
AIR_DATA_DEV_WRITE_BACK = "dev"
AIR_DATA_BACKFILL_COMPLETED = "backfill_completed"
AIR_DATA_BACKFILL_UNTIL = "backfilled_until"
AIR_DATA_ALLOWED_KEYS = [
    AIR_DATA_PATH_TO_YAML,
    AIR_DATA_MODEL_NAME,
    AIR_DATA_DEV_WRITE_BACK,
    AIR_DATA_BACKFILL_COMPLETED,
    AIR_DATA_BACKFILL_UNTIL,
]
AIR_LOCAL_TESTING_ERROR_MESSAGE = (
    "Testing locally but cannot write back to Cognite Data Fusion."
    + "\nSet 'dev'='True' in data parameter when testing locally."
    + "\nVisit https://cognite-cognite-air-sdk.readthedocs-hosted.com/en/latest/#local-testing to learn"
    + " more about local testing with the AIR SDK."
)

# Model- and schedule asset constants:
SA_EXT_ID = "schedule_asset_ext_id"
SA_FIELD_META_DATA = "data"
MA_FIELD_META_FIELDS = "fields"
MA_FIELD_META_MODELVERSION = "modelVersion"
MA_FIELD_META_MTNAME = "monitoring_task_name"
MA_FIELD_META_MTDESCRIPTION = "monitoring_task_description"

# Constants related to CDF Event and Time Series resources:
EVENT_EXT_ID = "external_id"
EVENT_TYPE = "type"
EVENT_SUBTYPE = "subtype"
EVENT_ASSET_IDS = "asset_ids"
EVENT_DATA_SET_ID = "data_set_id"
EVENT_DATA_SET_IDS = "data_set_ids"
EVENT_METADATA = "metadata"

AIR_EVENTS_FIELD_TYPE = "AIR"
AIR_EVENTS_FIELD_SUBTYPE = "model_output"
AIR_ALERT_EVENTS_FIELD_SUBTYPE = "ALERT"
AIR_TS_FIELD_ASSET_ID = "asset_id"
AIR_TS_META_KEY_VISUALIZE = "visualize"


class AIREventMeta:
    model = "model"
    model_version = "model_version"
    sa_ext_id = SA_EXT_ID
    dashboard_id = "dashboardId"
    system_id = "systemId"
    original_model_version = "original_model_version"
    project_name = "project_name"
    skip_notification = "skip_notification"
    acknowledged = "acknowledged"
    show = "show"
    parent_template_group_ext_id = "parent_template_group_ext_id"
    parent_template_instance_ext_id = "parent_template_instance_ext_id"
    template_name = "template_name"
    schedule_asset_type = "schedule_asset_type"

    @classmethod
    def get_meta_key_set(cls):
        return set((v for k, v in vars(cls).items() if isinstance(v, str) and not k.startswith("__")))

    @classmethod
    def get_reserved_meta_key_set(cls):
        return cls.get_meta_key_set() - set([cls.show])


AIR_TS_FIELD_DATASET = "data_set_id"
AIR_TS_FIELD_METADATA = "metadata"
AIR_MT_META_KEY_MODEL_NAME = "model"
AIR_TS_META_KEY_MODEL_VERSION = "model_version"
AIR_TS_META_KEY_SCHEDULE_ASSET_ID = SA_EXT_ID


AIR_META_BACKFILL_COMPLETE = "backfill_complete"
AIR_META_BACKFILLED_UNTIL = "backfilled_until"
AIR_META_BACKFILL_LOCK = "backfill_lock"
AIR_META_BACKFILL_LOCK_SET_TIME_UNIX = "backfill_lock_set_time"
AIR_META_BACKFILL_LOCK_MAX_LOCK_TIME = 30 * 60 * 1000  # 30 mins

# Other:
LEGAL_FIELD_TYPES = {
    "str": str,
    "int": int,
    "float": float,
    "bool": bool,
    "TimeSeries": TimeSeries,
    "Asset": Asset,
}
AIR_TYPES = Union[bool, str, int, float, Asset, TimeSeries, AssetList, TimeSeriesList]
