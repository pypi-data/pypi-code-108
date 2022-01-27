import time
from tqdm import tqdm
from typing import Dict, List, Optional, Union

from .feature import Feature, FeatureList

import pandas as pd
from pyrasgo.api.connection import Connection
from pyrasgo.api.error import APIError
from pyrasgo.schemas import collection as schema
from pyrasgo.schemas.attributes import Attribute, CollectionAttributeBulkCreate
from pyrasgo.schemas.enums import ModelType


class Collection(Connection):
    """
    Stores a Rasgo Collection
    """
    def __init__(self, api_object, **kwargs):
        super().__init__(**kwargs)
        self._fields = schema.Collection(**api_object)

    def __repr__(self):
        return str(self)

    def __str__(self):
        return f"Collection(id={self.id}, name={self.name}, type={self.modelType.name}, " \
               f"authorId={self.authorId}, isShared={self.isShared})"

    def __getattr__(self, item):
        try:
            return self._fields.__getattribute__(item)
        except KeyError:
            self._refresh()
        try:
            return self._fields.__getattribute__(item)
        except KeyError:
            raise AttributeError(f"No attribute named {item}")


# ----------
# Properties
# ----------

    @property
    def attributes(self) -> dict:
        """
        Helper property to convert a list of dicts into a single dict
        """
        attr_dict = {}
        response = self._get(f"/models/{self.id}/attributes", api_version=1).json()
        for a in response:
            attr_dict.update({a['key']: a['value']})
        return attr_dict

    @property
    def author(self) -> str:
        """
        Returns the author object of the Collection (includes credentials if user is author)
        """
        if self._profile['id'] == self.authorId:
            author = self._profile
        else:
            author = self._get(f"/users/{self.authorId}", api_version=1).json()
        return f'Author({author["id"]}, {author["firstName"]} {author["lastName"]})'

    @property
    def dimensions(self):
        if not self._fields.dimensions:
            self._refresh()
        return self._fields.dimensions

    @property
    def features(self) -> FeatureList:
        """
        Returns the Features within the Collection
        """
        try:
            return FeatureList([feature.dict() for feature in self._fields.features])
        except (AttributeError, TypeError):
            self._refresh()
        return FeatureList([feature.dict() for feature in self._fields.features])

    @features.setter
    def features(self, features: Union[List[Feature], FeatureList, Feature]):
        # Update the namespace
        all_features = [Feature(api_object=feature.dict()) for feature in self.features + features]
        self._fields.__setattr__('features', all_features)

    @property
    def modelType(self) -> ModelType:
        """
        Returns the type of the Collection
        """
        return ModelType(self._fields.type)

# -------
# Methods
# -------

    def get_compatible_features(self, return_dict: bool = False) -> Union[Dict, pd.DataFrame]:
        """
        Return all the compatible features which could be added to this collection

        Args:
            return_dict: Set to True to return as Dict instead of df
        """
        try:
            url = f"/models/{self.id}/compatible_features"
            all_compatible_features = self._get(url, api_version=1).json()
            if return_dict:
                return all_compatible_features
            return pd.DataFrame.from_dict(all_compatible_features)
        except:
            raise APIError(f"Collection {self.id} does not exist or this "
                           f"API key does not have access to it.")

    def preview(self, limit: int = 10) -> pd.DataFrame:
        """
        Preview the first x rows of this collection rows as a df

        Args:
            limit: integer limit for number of rows returned (Default 10)

        Returns:
            Pandas Dataframe Preview of Dataframe
        """
        return self.read_into_df(limit=limit)

    def add_attributes(self, attributes: List[dict]) -> List[dict]:
        if not isinstance(attributes, list):
            raise ValueError('attributes parameter must be passed in as a list of k:v pairs. Example: '
                             '[{"key": "value"}, {"key": "value"}]')
        attr = []
        for kv in attributes:
            if not isinstance(kv, dict):
                raise ValueError('attributes parameter must be passed in as a list of k:v pairs. Example: '
                                 '[{"key": "value"}, {"key": "value"}]')
            for k, v in kv.items():
                attr.append(Attribute(key=k, value=v))
        attr_in = CollectionAttributeBulkCreate(collectionId=self.id, attributes=attr)
        return self._put(f"/models/{self.id}/attributes", attr_in.dict(exclude_unset=True), api_version=1).json()

    def add_feature(self, feature: Feature) -> None:
        """
        Adds a single feature to the Collection
        """
        self.features = feature
        self._patch(f"/models/{self.id}/features", api_version=1,
                    _json={"featureIds": [str(feature.id)]})

    def add_features(self, features: Union[List[Feature], FeatureList]) -> None:
        """
        Adds a FeatureList or a list of Features to the Collection
        """
        self.features = features
        self._patch(f"/models/{self.id}/features", api_version=1,
                    _json={"featureIds": [str(feature.id) for feature in features]})

    def generate_training_data(self, trigger_stats: bool = True) -> None:
        """
        Triggers the generation of the Collection's training data.
        """
        self._post(f"/trainings/",
                   _json={"modelId": int(self.id),
                          "userId": self._profile['id']},
                   params={"trigger_stats": trigger_stats} if trigger_stats is not None else {},
                   api_version=0)
        for _ in tqdm(range(0, 10), leave=False):
            if self.is_data_ready():
                break
            time.sleep(1)

    def is_data_ready(self) -> bool:
        """
        Performs check against API for training data readiness, if true, a dataframe can be pulled down.
        :return:
        """
        r = self._get("/trainings/latest", api_version=0)
        if any([model['state'] == 'done' for model in r.json() if model['model']['id'] == self.id]):
            return True
        if any([model['state'] == 'error' for model in r.json() if model['model']['id'] == self.id]):
            raise SystemError("There's been an issue with the training data generation")
        return False

    def read_into_df(self,
                     filters: Optional[Dict[str, str]] = None,
                     limit: Optional[int] = None) -> pd.DataFrame:
        from pyrasgo.api.read import Read
        return Read().collection_data(id=self.id, filters=filters, limit=limit)

    def _refresh(self) -> None:
        """
        Updates the Collection's attributes from the API
        """
        this_collection_dict = self._get(f"/models/{self.id}", api_version=1).json()
        self._fields = schema.Collection(**this_collection_dict)

    def rename(self, new_name: str) -> None:
        """
        Updates a Collection's display name
        """
        print(f"Renaming Collection {self.id} from {self.name} to {new_name}")
        collection = schema.CollectionUpdate(id=self.id, name=new_name)
        self._fields = schema.Collection(**self._patch(
            f"/models/{self.id}/details",
            api_version=1,
            _json=collection.dict(exclude_unset=True, exclude_none=True)
        ).json())

    def render_sql_definition(self) -> str:
        sql_str = self._get(f"/models/{self.id}/sql", api_version=1).json()
        return sql_str

    def share(self, share: bool = True) -> bool:
        """
        Share the Collection with your organization
        :param share: True to make your Collection public. False to make your Collection private
        """
        response = self._patch(f"/models/{self.id}/details", api_version=1, _json={"isShared": share}).json()
        return response['isShared']

    def toggle_stats(self, trigger_stats: bool) -> dict:
        """
        Determine whether to run correlation and join stats when training the Collection
        """
        response = self.add_attributes([{"_trigger_stats": trigger_stats}])
        for r in response:
            if r.get("key") == "_trigger_stats":
                return {r["key"]: r["value"]}

    def _make_table_metadata(self) -> dict:
        organization = self._get_profile().get("organization")
        metadata = {
            "database": organization.get("database"),
            "schema": organization.get("schema"),
            "table": self._fields.dataTableName,
        }
        return metadata
