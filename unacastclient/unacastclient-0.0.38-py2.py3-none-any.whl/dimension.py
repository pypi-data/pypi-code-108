from collections import defaultdict
from unacastclient.unacast.metric.v1 import DimensionSpec as v1_DimensionSpec, DimensionValue as v1_DimensionValue
from pandas import DataFrame


class Dimension(object):

    def __init__(self, catalog, dimension_val=v1_DimensionSpec):
        self._catalog = catalog
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