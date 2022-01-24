from typing import Dict, List, Union

from shyft.dashboard.maps.map_layer import MapLayer


class LayerDataError(RuntimeError):
    pass


class LayerDataHandle:

    def __init__(self,
                 map_layer: MapLayer,
                 data: Dict[str, List[Union[str, int, float, List[Union[str, int, float]]]]]) -> None:
        """
        Container obj for sending data to the map viewer to update a layer
        """
        if not isinstance(map_layer, MapLayer):
            raise LayerDataError(f"Map layer provided is not of type MapLayer {map_layer}")
        self._map_layer = map_layer
        self._data = data

    @property
    def map_layer(self) -> MapLayer:
        return self._map_layer

    @property
    def data(self) -> Dict[str, List[Union[str, int, float]]]:
        return self._data
