import warnings
from time import sleep

from cognite.air._api import BaseAPIClient
from cognite.air.constants import (
    AIR_LOCAL_TESTING_ERROR_MESSAGE,
    AIR_MT_META_KEY_MODEL_NAME,
    AIR_TS_FIELD_ASSET_ID,
    AIR_TS_FIELD_DATASET,
    AIR_TS_FIELD_METADATA,
    AIR_TS_META_KEY_MODEL_VERSION,
    AIR_TS_META_KEY_SCHEDULE_ASSET_ID,
    AIR_TS_META_KEY_VISUALIZE,
    MA_FIELD_META_MODELVERSION,
)
from cognite.air.utils import air_data_set_id, is_string_truthy, strip_patch_from_version
from cognite.client.data_classes import TimeSeries


class AIRTimeSeriesAPI(BaseAPIClient):
    RESERVED_AIR_TS_KWARGS = set([AIR_TS_FIELD_DATASET])
    RESERVED_AIR_TS_META_KEYS = set([AIR_TS_META_KEY_MODEL_VERSION, AIR_TS_META_KEY_SCHEDULE_ASSET_ID])

    def _verify_valid_air_time_series_query(self, query_dct):
        illegal_params = self.RESERVED_AIR_TS_KWARGS.intersection(query_dct)
        if illegal_params:
            raise ValueError(f"Got one or more parameters reserved for AIR: {illegal_params}")

        metadata = query_dct.get(AIR_TS_FIELD_METADATA, {})
        illegal_meta_keys = self.RESERVED_AIR_TS_META_KEYS.intersection(metadata)
        if illegal_meta_keys:
            raise ValueError(
                f"'{AIR_TS_FIELD_METADATA}' contained one or more keys reserved for AIR: {illegal_meta_keys}"
            )

    def _update(self, ts, sleep_time=3):
        self.client.time_series.update(ts)
        sleep(sleep_time)

    def retrieve(self, ts_ext_id: str = "", external_id: str = "", visualize: bool = False, **kwargs) -> TimeSeries:
        """Retrieving a versioned Time Series.

        If the Time Series does not exist or is out of version, a new Time Series
        will be created. The out-of-version Time Series will get an extension to the external ID.

        Args:
            external_id (str): External ID of Time Series. Make sure that this is unique.
            ts_ext_id (str): [to be deprecated use external_id instead]
                Same as external_id - will be replaced by external_id.
            visualize (bool): If the Time Series should be visualized in AIR Front End.
            **kwargs (Dict): Additional keywords such as metadata etc.

        Examples:
            >>> air_client.time_series.retrieve(external_id=f"my_ts_{air_client.schedule_external_id}")

        """
        if not isinstance(visualize, bool):
            raise TypeError(f"Keyword arg 'visualize' must be {bool}, not {type(visualize)}")
        self._verify_valid_air_time_series_query(kwargs)
        if not ts_ext_id and not external_id:
            raise ValueError("Please specify external_id of Time Series.")
        if ts_ext_id and not external_id:
            warnings.warn(
                "The parameter named 'ts_ext_id' is deprecated and will be removed in a later release, "
                + "please use 'external_id' instead.",
                DeprecationWarning,
            )
            external_id = ts_ext_id

        cur_ts_version = None
        cur_ts = self.client.time_series.retrieve(external_id=external_id)
        if cur_ts:
            cur_ts_version = strip_patch_from_version(cur_ts.metadata[AIR_TS_META_KEY_MODEL_VERSION])
            cur_ts_sa_xid = cur_ts.metadata.get(AIR_TS_META_KEY_SCHEDULE_ASSET_ID)
            if cur_ts_sa_xid != self._config.schedule_asset_ext_id:
                # Ensuring backward compatibility: Add schedule asset ext. ID to the metadata of 'cur_ts':
                if cur_ts.asset_id == self._config.schedule_asset_id:
                    cur_ts.metadata[AIR_TS_META_KEY_SCHEDULE_ASSET_ID] = self._config.schedule_asset_ext_id
                    self._update(cur_ts)
                else:
                    raise ValueError(
                        "Time series external ID, '{external_id}', is already in use in another context."
                        f"It is related to the AIR schedule asset with id: '{cur_ts_sa_xid or 'unknown'}'"
                    )
            # ensure backward compatibility: Add model name to metadata
            cur_ts_model_name = cur_ts.metadata.get(AIR_MT_META_KEY_MODEL_NAME)
            if cur_ts_model_name != self._config.model_name:
                cur_ts.metadata[AIR_MT_META_KEY_MODEL_NAME] = self._config.model_name
                self._update(cur_ts)

        if cur_ts_version == self._config.model_version_stripped:
            # Check if the visualization changed, and update accordingly
            cur_ts_viz_setting = is_string_truthy(cur_ts.metadata.get(AIR_TS_META_KEY_VISUALIZE))
            if cur_ts_viz_setting is not visualize:
                cur_ts.metadata[AIR_TS_META_KEY_VISUALIZE] = str(visualize)
                self._update(cur_ts)
            return cur_ts

        # Current version of the time series is for an older version of the model:
        if cur_ts:
            # We deprecate the time series and (possibly) move it back to the schedule asset so that we
            # don't end up with multiple time series of different versions connected to a production asset:
            cur_ts.external_id = f"{cur_ts.external_id}:v.{cur_ts_version}"
            cur_ts.name = cur_ts.external_id
            cur_ts.asset_id = self._config.schedule_asset_id
            self._update(cur_ts)
        asset_ids = kwargs.pop(AIR_TS_FIELD_ASSET_ID, self._config.schedule_asset_id)
        time_series_to_be_created = TimeSeries(
            external_id=external_id,
            metadata={
                **kwargs.pop(AIR_TS_FIELD_METADATA, {}),
                AIR_TS_META_KEY_VISUALIZE: str(visualize),
                AIR_TS_META_KEY_MODEL_VERSION: self._config.model_version,
                AIR_TS_META_KEY_SCHEDULE_ASSET_ID: self._config.schedule_asset_ext_id,
                MA_FIELD_META_MODELVERSION: self._config.model_version,
            },
            **kwargs,
        )

        if self._config.dev_write_back:
            time_series_to_be_created.data_set_id = air_data_set_id(self._config.client, "AIR")
            return self.client.time_series.create(time_series_to_be_created)
        if self._config.local_testing:
            raise ValueError(AIR_LOCAL_TESTING_ERROR_MESSAGE)

        time_series_to_be_created.asset_id = asset_ids
        time_series_to_be_created.data_set_id = self._config.data_set_id
        return self.client.time_series.create(time_series_to_be_created)
