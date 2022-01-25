from typing import List, Optional

from .error import APIError
from pyrasgo import schemas as api
from pyrasgo.primitives import Collection, Feature, FeatureList, DataSource
from pyrasgo.schemas.enums import Granularity, ModelType


class Match():

    def __init__(self):
        from . import Get
        from .connection import Connection
        from pyrasgo.config import get_session_api_key

        api_key = get_session_api_key()
        self.api = Connection(api_key=api_key)
        self.get = Get()

    def data_source(self, fqtn: str) -> DataSource:
        """
        Returns the first Data Source that matches the specified name
        """
        try:
            response = self.api._get(f"/data-source", {"table": fqtn}, api_version=1).json()
            return DataSource(api_object=response[0])
        except:
            return None

    def dataframe(self, name: str = None, unique_id: str = None) -> api.Dataframe:
        """
        Returns the first Dataframe that matches the specified name or uid
        """
        try:
            if name:
                response = self.api._get(f"/dataframes", {"name": name}, api_version=1).json()
                return api.Dataframe(**response[0])
            elif unique_id:
                response = self.api._get(f"/dataframes/{unique_id}", api_version=1).json()
                return api.Dataframe(**response)
        except:
            return None
        return None

    def feature(self, column_name: str, data_source_id: int) -> Optional[Feature]:
        """
        Returns the first Feature matching the specified name in a DataSource
        """
        try:
            features = self.get.data_source(data_source_id).features
            for f in features:
                if column_name.upper() == f.columnName.upper():
                    return Feature(api_object=f.dict())
            return None
        except:
            return None