from typing import Dict, List, Optional

import pandas as pd

from pyrasgo.api.connection import Connection
from pyrasgo.schemas import feature as schema
from pyrasgo.schemas.attributes import Attribute, FeatureAttributes, FeatureAttributeBulkCreate
from pyrasgo.schemas.enums import Granularity


class FeatureList():
    """
        Convenience class to enable simpler console presentation,
        iteration and searching through lists of Features objects
    """

    def __init__(self, api_object):
        self.data = [Feature(api_object=entry) for entry in api_object]

    def __getitem__(self, i: int):
        return self.data[i]

    def __len__(self) -> int:
        return len(self.data)

    def __str__(self):
        ids = [str(feature.id) for feature in self]
        return (f"Features({len(self.data)} total, "
                f"ids: [{','.join(ids if len(self) < 7 else ids[0:3] + ['...'] + ids[-3:])}])")

    def __add__(self, other):
        if isinstance(other, Feature):
            return type(self)([feature.dict() for feature in self.data + [other]])
        if isinstance(other, type(self)):
            return type(self)([feature.dict() for feature in self.data + other.data])
        if isinstance(other, list) and all([isinstance(entry, Feature) for entry in other]):
            return type(self)([feature.dict() for feature in self.data + other])
        raise TypeError(f"unsupported operand type(s) for +: '{type(self)}' and '{type(other)}'")

    def __repr__(self):
        return str(self)

    def filter(self, **kwargs):
        return [feature for feature in self.data
                if [feature.__getattr__(key) for key in kwargs.keys()] == list(kwargs.values())]


class Feature(Connection):
    """
    Stores a Rasgo Feature
    """

    def __init__(self, api_object, **kwargs):
        super().__init__(**kwargs)
        self._fields = schema.Feature(**api_object)

    def __getattr__(self, item):
        try:
            return self._fields.__getattribute__(item)
        except KeyError:
            raise AttributeError(f"No attribute named {item}")

    def __repr__(self):
        return str(self)

    def __str__(self):
        return f"Feature(id={self.id}, name={self.displayName}, dataType={self.dataType}, description={self.description}, status={self.status})"

# ----------
# Properties
# ----------
    @property
    def attributes(self) -> dict:
        """
        Helper property to convert a list of dicts into a single dict
        """
        attr_dict = {}
        for a in self._fields.attributes:
            attr_dict.update({a.key: a.value})
        return attr_dict

    @property
    def dataTable(self):
        data_source = self._fields.dataSource
        if data_source:
            return data_source.dataTable
        return None

    @property
    def granularities(self):
        """
        Retrieves granularities for the feature
        """
        granularities = self._fields.granularities
        if granularities:
            return [Granularity(granularity.name.lower()) for granularity in granularities]
        return []

    @property
    def indexFields(self):
        """
        Retrieves the dimensions column name in the feature set table
        """
        return [d.columnName for d in self._fields.dimensions]

    @property
    def sourceTable(self):
        """
        Retrieves the feature set table for the feature
        """
        table_dict = self.dataTable.dict(exclude_unset=True)
        if table_dict.get('fqtn'):
            return table_dict['fqtn']
        if table_dict.get('tableName'):
            return table_dict['tableName']
        return None

    @property
    def status(self):
        """
        Returns feature status: Sandbox or Production
        """
        return 'Production' if self.orchestrationStatus == 'Productionized' else 'Sandbox'

    @property
    def tags(self) -> List[str]:
        return self._fields.tags

# -------
# Methods
# -------
    def add_attributes(self, attributes: List[dict]):
        if not isinstance(attributes, list):
            raise ValueError('attributes parameter must be passed in as a list of k:v pairs. Example: [{"key": "value"}, {"key": "value"}]')
        attr = []
        for kv in attributes:
            if not isinstance(kv, dict):
                raise ValueError('attributes parameter must be passed in as a list of k:v pairs. Example: [{"key": "value"}, {"key": "value"}]')
            for k, v in kv.items():
                attr.append(Attribute(key=k, value=v))
        attr_in = FeatureAttributeBulkCreate(featureId = self.id, attributes=attr)
        self._put(f"/features/{self.id}/attributes", attr_in.dict(exclude_unset=True), api_version=1).json()
        self.refresh()

    def add_tag(self, tag: str):
        if tag in self._fields.tags:
            return
        self._fields = schema.Feature(**self._put(f"/features/{self.id}/tags",
                                                api_version=1, _json={"tags": [tag, *self._fields.tags]}).json())

    def add_tags(self, tags: List[str]):
        if all(tag in self._fields.tags for tag in tags):
            return
        self._fields = schema.Feature(**self._put(f"/features/{self.id}/tags",
                                                api_version=1, _json={"tags": [*tags, *self._fields.tags]}).json())

    def build_stats(self):
        return self._post(f"/features/{self.id}/stats", api_version=1).json()

    def display_source_code(self):
        """
        Convenience function to display the sourceCode property
        """
        data_source = self._fields.dataSource
        if data_source:
            return data_source.sourceCode
        return None

    def delete_tag(self, tag: str):
        if tag not in self._fields.tags:
            return
        self._fields = schema.Feature(**self._delete(f"/features/{self.id}/tags",
                                                   api_version=1, _json={"tags": [tag]}).json())

    def delete_tags(self, tags: List[str]):
        if all(tag not in self._fields.tags for tag in tags):
            return
        self._fields = schema.Feature(**self._delete(f"/features/{self.id}/tags",
                                                   api_version=1, _json={"tags": [*tags]}).json())

    def get_stats(self):
        try:
            stats_json = self._get(f"/features/{self.id}/stats", api_version=1).json()
        except:
            return 'Cannot find stats for this feature'
        stats_obj = schema.FeatureStats(**stats_json['featureStats']) or None
        return stats_obj

    def productionize(self):
        """
        Sets a Feature's status from Sandbox to Production
        """
        print(f"Setting feature from {self.status} to Production")
        feature = schema.FeatureUpdate(id=self.id, orchestrationStatus='Productionized')
        self._fields = schema.Feature(**self._patch(f"/features/{self.id}",
                                                 api_version=1, _json=feature.dict(exclude_unset=True, exclude_none=True)).json())

    def read_into_df(self,
                     filters: Optional[Dict[str, str]] = None,
                     limit: Optional[int] = None) -> pd.DataFrame:
        """
        Pull Feature data from DataWarehouse into a pandas Dataframe
        """
        from pyrasgo.api.read import Read
        return Read().feature_data(id=self.id, filters=filters, limit=limit)

    def refresh(self):
        """
        Updates the Feature's attributes from the API
        """
        self._fields = schema.Feature(**self._get(f"/features/{self.id}", api_version=1).json())

    def rename(self, new_name: str):
        """
        Updates a Feature's display name
        """
        print(f"Renaming Feature {self.id} from {self.displayName} to {new_name}")
        feature = schema.FeatureUpdate(id=self.id, name=new_name)
        self._fields = schema.Feature(**self._patch(f"/features/{self.id}",
                                                 api_version=1, _json=feature.dict(exclude_unset=True, exclude_none=True)).json())

    def to_dict(self):
        feature_as_dict = {}
        feature_as_dict["sourceTable"] = self.sourceTable
        feature_as_dict["features"] = [{"columnName": self.columnName, "dataType": self.dataType, "displayName": self.displayName, "description": self.description}]
        feature_as_dict["dimensions"] = []
        for d in self._fields.dimensions:
            feature_as_dict["dimensions"].append({"columnName": d.columnName, "dataType": d.dataType, "granularity": d.granularity.name})
        feature_as_dict["status"] = self.orchestrationStatus
        feature_as_dict["tags"] = self.tags
        feature_as_dict["attributes"] = []
        for a in self._fields.attributes:
            feature_as_dict["attributes"].append({a.key: a.value})
        feature_as_dict["gitRepo"] = self.gitRepo
        return feature_as_dict

    def _make_table_metadata(self):
        payload = self.dataTable
        metadata = {
            "database": payload.databaseName,
            "schema": payload.schemaName,
            "table": payload.tableName,
        }
        return metadata