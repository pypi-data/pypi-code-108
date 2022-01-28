
from .layer import Layer
from .address_component import AddressComponent
from syncer import sync

from unacatlib.unacast.operator.v1 import CreateLayerRequest 
from unacatlib.unacast.maps.v1 import LayerSpec, Layer as v1_Layer, AddressComponent as v1_AddressComponent, ComponentKind

class AddressComponentBuilder(object):
  
    def __init__(self, catalog: 'Catalog', component: str):
        self._catalog = catalog
        self.address_component_operator_service = catalog._client.address_component_operator_service

        self._component = component
        self._kind = ComponentKind.FREE_FORM_UNSPECIFIED
        self._display_name = None
        self._id_display_name = None
        self._short_name = None

    def with_display_name(self, display_name: str):
      self._display_name = display_name
      return self

    def with_id_display_name(self, id_display_name: str):
        self._id_display_name = id_display_name
        return self

    def with_short_name(self, short_name: str):
      self._short_name = short_name
      return self

    def with_kind(self, kind: ComponentKind):
      self._kind = kind
      return self

    def create(self) -> AddressComponent:
      res: v1_AddressComponent = sync(
            self.address_component_operator_service.create_address_component(
              catalog_id=self._catalog.id,
              component=self._component, 
              short_name=self._short_name,
              display_name=self._display_name,
              id_display_name=self._id_display_name,
              kind=self._kind
            )
      )
      return AddressComponent(self._catalog, res)
    
    