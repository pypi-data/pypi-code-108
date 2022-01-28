from collections import defaultdict
from syncer import sync

from pandas import DataFrame

from unacatlib.unacast.metric.v1 import Dimension as v1_Dimension, DimensionValue as v1_DimensionValue

from .index_job import IndexJob


class Dimension(object):

    def __init__(self, catalog, dimension_val = v1_Dimension):
        self._catalog = catalog
        self._dimension_operator_service = catalog._client.dimension_operator_service
        self._dimension = dimension_val

    @property
    def id(self):
        return self._dimension.dimension_id

    def search(self, query: str) -> DataFrame:
        dim_values = self._catalog.client.search_dimension_values(self._catalog.id, self.id, query + "*")

        dataframe_dict = defaultdict(list)
        dimension_value: v1_DimensionValue
        for dimension_value in dim_values:
            dataframe_dict['value'].append(dimension_value.value)
            dataframe_dict['display_name'].append(dimension_value.display_name)

        return DataFrame.from_dict(dataframe_dict)

    def list(self) -> DataFrame:
        return self.search("")

    def index(self, big_query_table_id: str) -> IndexJob:
        res = sync(
            self._dimension_operator_service.index_dimension(
                catalog_id=self._catalog.id,
                dimension_id=self._dimension.dimension_id, 
                big_query_table_id=big_query_table_id,
            )
        )
        return IndexJob(self._catalog, res.job_id)

    def delete_dimension(self):
        sync(self._dimension_operator_service.delete_dimension(dimension_id=self._dimension.dimension_id, catalog_id=self._catalog.id))