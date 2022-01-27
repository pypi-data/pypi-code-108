import json
import time
from pathlib import Path
from typing import Dict

import pandas as pd
from cognite.client.data_classes import Asset, AssetUpdate
from pandas import DataFrame

import cognite.airworkflow.constants as const
from cognite.airworkflow.model.config import Config
from cognite.airworkflow.util import cdf

AIR_INFRA = "airInfra"
AIR_MODELS = "airModels"
AIR_SOURCE = "AIR Application"
AIR_ROOT_ID = "AIR_root_asset"


class ModelAssetHierarchy:
    def __init__(self, config: Dict[Path, Config], project: str, airInfra: bool = False):
        self.config = config
        self.airInfra = airInfra
        project_info = const.AUTHENTICATION[project]
        print("Project: " + project_info.name, flush=True)
        self.client = cdf.experimental_client(project)
        self._hierarchy: Dict[str, Dict] = {}
        self._existing_hierarchy: DataFrame = pd.DataFrame()
        self._data_set_id: int = 0

    @property
    def hierarchy(self) -> Dict[str, Dict]:
        return self._hierarchy if self._hierarchy else self._get_asset_hierarchy()

    @property
    def existing_hierarchy(self) -> DataFrame:
        return self._existing_hierarchy if self._existing_hierarchy.shape[0] else self._get_existing_asset_hierarchy()

    @property
    def data_set_id(self) -> int:
        return self._data_set_id if self._data_set_id else cdf.data_set_id(self.client, "AIR")

    def _get_asset_hierarchy(self) -> Dict[str, Dict]:
        hierarchy: Dict[str, Dict] = {AIR_MODELS: {}, AIR_INFRA: {}}
        for key, value in self.config.items():
            if self.airInfra:
                hierarchy[AIR_INFRA].update({key: value.to_dict()})
            else:
                hierarchy[AIR_MODELS].update({key: value.to_dict()})

        self._hierarchy = hierarchy
        return hierarchy

    def _get_existing_asset_hierarchy(self) -> DataFrame:
        assets = self.client.assets.list(data_set_ids=[self.data_set_id], limit=-1).to_pandas()
        if assets.shape[0] == 0:
            existing_hierarchy = pd.DataFrame()
        else:
            air_asset_id = assets.loc[assets["name"] == "AIR", "id"].iloc[0]
            existing_hierarchy = assets[assets["rootId"] == air_asset_id]

        self._existing_hierarchy = existing_hierarchy
        return existing_hierarchy

    def _asset_exists(self, model_name: str) -> bool:
        return self.existing_hierarchy.shape[0] and model_name in self.existing_hierarchy["name"].tolist()

    def _create_structure_if_not_exist(self):
        update = False
        if (self.existing_hierarchy.shape[0] == 0) or ("AIR" not in self.existing_hierarchy["name"].tolist()):
            self._create_asset(AIR_ROOT_ID, "", name="AIR")
            update = True
        if (self.existing_hierarchy.shape[0] == 0) or (AIR_MODELS not in self.existing_hierarchy["name"].tolist()):
            self._create_asset(
                AIR_MODELS,
                "All custom models are stored here.",
                parent_external_id=AIR_ROOT_ID,
            )
            update = True
        if (self.existing_hierarchy.shape[0] == 0) or (AIR_INFRA not in self.existing_hierarchy["name"].tolist()):
            self._create_asset(
                AIR_INFRA,
                "All AIR infrastructure models are stored here.",
                parent_external_id=AIR_ROOT_ID,
            )
            update = True
        if update:
            assets = self.client.assets.list(data_set_ids=self.data_set_id, limit=-1).to_pandas()
            while (assets.shape[0] == 0) or (
                not all([i in assets["name"].tolist() for i in ["AIR", AIR_MODELS, AIR_INFRA]])
            ):
                time.sleep(1)
                assets = self.client.assets.list(data_set_ids=self.data_set_id, limit=-1).to_pandas()
            return self._get_existing_asset_hierarchy()
        return self.existing_hierarchy

    def _create_asset(
        self,
        ext_id: str,
        desc: str,
        *,
        name: str = "",
        parent_external_id: str = None,
        meta: Dict = None,
    ) -> None:
        self.client.assets.create(
            Asset(
                external_id=ext_id,
                name=name if name else ext_id,
                description=desc,
                data_set_id=self.data_set_id,
                source=AIR_SOURCE,
                parent_external_id=parent_external_id,
                metadata=meta,
            )
        )

    def _create_air_asset(self, model_type: str, model_name: str, model_config: Dict) -> None:
        self._create_asset(
            model_name,
            model_config["description"],
            meta=self._clean_metadata(model_config),
            parent_external_id=self.existing_hierarchy.loc[
                self.existing_hierarchy["name"] == model_type, "externalId"
            ].iloc[0],
        )

    def _update_asset(self, model_name: str, model_config: Dict) -> None:
        model_asset = model_config
        metadata = self._clean_metadata(model_config)

        cdf_model = self.existing_hierarchy[self.existing_hierarchy["name"] == model_name]
        updated_asset = AssetUpdate(id=cdf_model["id"].iloc[0])
        update = False
        if model_asset["description"] != cdf_model["description"].iloc[0]:
            updated_asset = updated_asset.description.set(model_asset["description"])
            update = True
        if metadata != cdf_model["metadata"].iloc[0]:
            updated_asset = updated_asset.metadata.set(metadata)
            update = True
        if update:
            self.client.assets.update(updated_asset)

    def create_or_update(self):
        self._create_structure_if_not_exist()
        for model_type, model_paths in self.hierarchy.items():
            for path, model_config in model_paths.items():
                model_name = path.name
                if self._asset_exists(model_name):
                    self._update_asset(model_name, model_config)
                else:
                    self._create_air_asset(model_type, model_name, model_config)

    @staticmethod
    def _clean_metadata(model_config) -> Dict:
        if model_config.get("deploy"):
            model_config.pop("deploy")
        if model_config:
            model_version = model_config.get("modelVersion")
            if model_version:
                model_version = ".".join(model_version.split(".")[:-1])
                model_config.update({"modelVersion": model_version})
            else:
                model_config.update({"modelVersion": ""})

            # metadata.update({"schedule": str(model_config.get("schedule"))})
            model_config = {
                key: json.dumps(value) if isinstance(value, dict) or isinstance(value, list) else str(value)
                for key, value in model_config.items()
            }
        else:
            model_config = {}
        return model_config
