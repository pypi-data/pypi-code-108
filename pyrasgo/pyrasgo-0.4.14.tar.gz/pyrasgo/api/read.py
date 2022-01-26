import pandas as pd
from typing import Dict, List, Optional

from .error import APIError
from pyrasgo import config
from pyrasgo import schemas as api
from pyrasgo.primitives import Collection, Feature, FeatureList, DataSource, Dataset


class Read():

    def __init__(self):
        from . import Get
        from pyrasgo.storage import DataWarehouse, SnowflakeDataWarehouse

        self.data_warehouse: SnowflakeDataWarehouse = DataWarehouse.connect()
        self.get = Get()

    def collection_data(self,
                        id: int,
                        filters: Optional[Dict[str, str]] = None,
                        limit: Optional[int] = None) -> pd.DataFrame:
        """
        Constructs a pandas DataFrame from the specified Rasgo Collection

        :param id: int
        :param filters: dictionary providing columns as keys and the filtering values as values.
        :param limit: integer limit for number of rows returned
        :return: Dataframe containing feature data
        """
        collection = self.get.collection(id)
        if collection:
            try:
                table_metadata = collection._make_table_metadata()
                query, values = self.data_warehouse.make_select_statement_filter_dict(table_metadata, filters, limit)
                return self.data_warehouse.query_into_dataframe(query, values)
            except Exception as e:
                raise APIError(f"Collection table is not reachable: {e}")
        raise APIError("Collection does not exist")

    def feature_data(self,
                     id: int,
                     filters: Optional[Dict[str, str]] = None,
                     limit: Optional[int] = None) -> pd.DataFrame:
        """
        Constructs a pandas DataFrame from the specified Rasgo Feature data

        :param id: int
        :param filters: dictionary providing columns as keys and the filtering values as values.
        :param limit: integer limit for number of rows returned
        :return: Dataframe containing feature data
        """
        feature = self.get.feature(id)
        if feature.sourceTable:
            try:
                table_metadata = feature._make_table_metadata()
                #TODO: if we ever support multiple features, add them to this line -
                features = feature.columnName
                indices = ','.join(feature.indexFields)
                columns = indices +', '+features
                query, values = self.data_warehouse.make_select_statement_filter_dict(table_metadata, filters, limit, columns)
                return self.data_warehouse.query_into_dataframe(query, values)
            except Exception as e:
                raise APIError(f"Feature table is not reachable: {e}")
        raise APIError("Feature table does not exist")

    def source_data(self,
                    id: int,
                    filters: Optional[Dict[str, str]] = None,
                    limit: Optional[int] = None) -> pd.DataFrame:
        """
        Constructs a pandas DataFrame from the specified Rasgo DataSource

        :param id: int
        :param filters: dictionary providing columns as keys and the filtering values as values.
        :param limit: integer limit for number of rows returned
        :return: Dataframe containing feature data
        """
        data_source = self.get.data_source(id)
        if data_source:
            try:
                table_metadata = data_source._make_table_metadata()
                query, values = self.data_warehouse.make_select_statement_filter_dict(table_metadata, filters, limit)
                return self.data_warehouse.query_into_dataframe(query, values)
            except Exception as e:
                raise APIError(f"DataSource table is not reachable: {e}")
        raise APIError("DataSource does not exist")

    def dataset(
            self,
            id: Optional[int] = None,
            dataset: Optional[Dataset] = None,
            filters: Optional[List[str]] = None,
            order_by: Optional[List[str]] = None,
            columns: Optional[List[str]] = None,
            limit: Optional[int] = None,
            snapshot_index: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Constructs and returns pandas DataFrame from the specified Rasgo Dataset

        You can supply SQL WHERE clause filters, order the dataset by columns, only
        return selected columns, and add a return limit as well

        Example:
            ```
            rasgo.read.dataset(
                id=74,
                filters=['SALESTERRITORYKEY = 1', 'TOTALPRODUCTCOST BETWEEN 1000 AND 2000'],
                order_by=['TOTALPRODUCTCOST'],
                columns=['PRODUCTKEY', 'TOTALPRODUCTCOST', 'SALESTERRITORYKEY'],
                limit=50
            )
            ```

        Args:
            id: dataset id to read into df
            dataset: Dataset obj to read into df
            filters: List of SQL WHERE filters strings to filter on returned df
            order_by: List of columns to order by in returned dataset
            columns: List of columns to return in the df
            limit: Only return this many rows in the df
            snapshot: the index of a snapshot from Dataset.snapshots to read 
        """
        # Validate one dataset passed in, id or dataset obj
        if not dataset and id is None:
            raise ValueError(f"Must pass either a valid dataset ID or Dataset "
                             f"object to read into a DataFrame")
        if not dataset:
            # Note: Func below already raises API error if dataset with id doesn't exist
            dataset = self.get.dataset(id)
        
        fqtn = dataset.fqtn

        if snapshot_index:
            try:    
                fqtn = dataset._api_dataset.snapshots[snapshot_index].fqtn
            except IndexError:
                raise ValueError(f"Snapshot index does not exist")

        if dataset:
            try:
                query = self.data_warehouse.make_select_statement(
                    table_metadata={'fqtn': fqtn},
                    filters=filters,
                    order_by=order_by,
                    columns=columns,
                    limit=limit
                )
                return self.data_warehouse.query_into_dataframe(query)
            except Exception as e:
                raise APIError(f"Dataset table is not reachable: {e}")
