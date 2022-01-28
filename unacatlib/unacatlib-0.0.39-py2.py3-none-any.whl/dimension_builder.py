
from .layer import Layer
from .address_component import AddressComponent
from .dimension import Dimension
from syncer import sync

from unacatlib.unacast.operator.v1 import CreateLayerRequest 
from unacatlib.unacast.maps.v1 import LayerSpec, Layer as v1_Layer, AddressComponent as v1_AddressComponent, ComponentKind
from unacatlib.unacast.metric.v1 import Dimension as v1_Dimension

class DimensionBuilder(object):
  
    def __init__(self, catalog: 'Catalog', dimension: str):
        self._catalog = catalog
        self._dimension_operator_service = catalog._client.dimension_operator_service

        self._dimension = dimension
        self._display_name = None
        self._id_display_name = None

    def with_display_name(self, display_name: str):
      self._display_name = display_name
      return self

    def with_id_display_name(self, id_display_name: str):
      self._id_display_name = id_display_name
      return self

    def create(self) -> Dimension:
      res: v1_Dimension = sync(
            self._dimension_operator_service.create_dimension(
              catalog_id=self._catalog.id,
              dimension_id=self._dimension, 
              display_name=self._display_name,
              id_display_name=self._id_display_name,
            )
      )
      return Dimension(self._catalog, res)
    
    