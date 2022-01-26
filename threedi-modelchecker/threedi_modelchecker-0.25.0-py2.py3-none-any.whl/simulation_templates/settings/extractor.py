from enum import Enum
from sqlalchemy.orm import Query
from sqlalchemy.orm.session import Session
from threedi_api_client.openapi.models import AggregationSettings
from threedi_api_client.openapi.models import NumericalSettings
from threedi_api_client.openapi.models import TimeStepSettings
from threedi_api_client.openapi.models.physical_settings import (
    PhysicalSettings,
)
from threedi_modelchecker.simulation_templates.models import Settings
from threedi_modelchecker.simulation_templates.settings.mappings import (
    aggregation_settings_map,
)
from threedi_modelchecker.simulation_templates.settings.mappings import (
    numerical_settings_map,
)
from threedi_modelchecker.simulation_templates.settings.mappings import (
    physical_settings_map,
)
from threedi_modelchecker.simulation_templates.settings.mappings import (
    sqlalchemy_to_api_model,
)
from threedi_modelchecker.simulation_templates.settings.mappings import (
    time_step_settings_map,
)
from threedi_modelchecker.threedi_model.constants import FlowVariable
from threedi_modelchecker.threedi_model.models import (
    AggregationSettings as SQLAggregationSettings,
)
from threedi_modelchecker.threedi_model.models import GlobalSetting
from threedi_modelchecker.threedi_model.models import (
    NumericalSettings as SQLNumericalSettings,
)
from typing import List
from typing import Optional


class SettingsExtractor(object):
    def __init__(self, session: Session, global_settings_id: Optional[int] = None):
        self.session = session
        self._global_settings = None
        self._global_settings_id = global_settings_id
        self._numerical_settings = None
        self._aggregation_settings = None

    @property
    def _sql_aggregation_settings(self) -> List[SQLAggregationSettings]:
        if self._aggregation_settings is None:
            self._aggregation_settings = (
                Query(SQLAggregationSettings)
                .with_session(self.session)
                .filter(
                    SQLAggregationSettings.global_settings_id == self.global_settings.id
                )
                .all()
            )
            if self._aggregation_settings is None:
                self._aggregation_settings = []
        return self._aggregation_settings

    @property
    def _sql_numerical_settings(self) -> SQLNumericalSettings:
        if self._numerical_settings is None:
            self._numerical_settings = (
                Query(SQLNumericalSettings)
                .with_session(self.session)
                .filter(
                    SQLNumericalSettings.id
                    == self.global_settings.numerical_settings_id
                )
                .first()
            )
        return self._numerical_settings

    @property
    def global_settings(self) -> GlobalSetting:
        if self._global_settings is None:
            qr = Query(GlobalSetting).with_session(self.session)
            if self._global_settings_id is not None:
                qr = qr.filter(GlobalSetting.id == self._global_settings_id)
            self._global_settings = qr.first()
        return self._global_settings

    @property
    def timestep_settings(self) -> TimeStepSettings:
        config_dict = {
            x.name: getattr(self.global_settings, x.name)
            for x in self.global_settings.__table__.columns
        }
        return sqlalchemy_to_api_model(
            config_dict, TimeStepSettings, time_step_settings_map
        )

    @property
    def physical_settings(self) -> PhysicalSettings:
        config_dict = {
            x.name: getattr(self.global_settings, x.name)
            for x in self.global_settings.__table__.columns
        }
        return sqlalchemy_to_api_model(
            config_dict, PhysicalSettings, physical_settings_map
        )

    @property
    def aggregation_settings(self) -> List[AggregationSettings]:
        agg_settings = []

        def convert_enum(value):
            if isinstance(value, FlowVariable):
                # Mismatch between sqlite and API....
                mapping = {
                    "waterlevel": "water_level",
                    "wet_cross-section": "wet_cross_section",
                }
                value = value.value
                value = mapping.get(value, value)
            elif isinstance(value, Enum):
                value = value.value
            return value

        for agg_setting in self._sql_aggregation_settings:
            agg_setting: SQLAggregationSettings
            config_dict = {
                x.name: convert_enum(getattr(agg_setting, x.name))
                for x in agg_setting.__table__.columns
            }
            agg_settings.append(
                sqlalchemy_to_api_model(
                    config_dict,
                    AggregationSettings,
                    aggregation_settings_map,
                    extra_exclude={
                        "name",
                    },
                )
            )
        return agg_settings

    @property
    def numerical_settings(self) -> NumericalSettings:
        config_dict = {
            x.name: getattr(self.global_settings, x.name)
            for x in self.global_settings.__table__.columns
        }
        config_dict.update(
            {
                x.name: getattr(self._sql_numerical_settings, x.name)
                for x in self._sql_numerical_settings.__table__.columns
            }
        )
        return sqlalchemy_to_api_model(
            config_dict, NumericalSettings, numerical_settings_map
        )

    def all_settings(self) -> Settings:
        return Settings(
            numerical=self.numerical_settings,
            physical=self.physical_settings,
            timestep=self.timestep_settings,
            aggregations=self.aggregation_settings,
        )
