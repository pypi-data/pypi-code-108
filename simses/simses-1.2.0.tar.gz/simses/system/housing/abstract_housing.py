from abc import ABC, abstractmethod
from simses.commons.log import Logger
from simses.system.housing.layer import Layer


class Housing(ABC):
    """ class to specify the housing of the storage system"""

    def __init__(self, layer_inner: Layer = None, layer_mid: Layer = None, layer_outer: Layer = None, default_scale: int=0):
        super().__init__()
        self.__log: Logger = Logger(type(self).__name__)
        self.__layer_inner = layer_inner
        self.__layer_mid = layer_mid
        self.__layer_outer = layer_outer
        self.__internal_component_volume: float = 0.0
        self.__scale_factor: int = default_scale
        self.__volume_usability_factor: float = 0.2

    def add_component_volume(self, volume: float):
        self.__internal_component_volume += volume
        while self.__internal_component_volume > self.__volume_usability_factor * self.internal_volume:
            self.__scale_factor += 1
            self.__layer_inner.update_scale()
            self.__layer_mid.update_scale()
            self.__layer_outer.update_scale()
            self.__log.info('Increasing number of containers to ' + str(self.__scale_factor))

    @property
    def inner_layer(self) -> Layer:
        """
        Access to layer attributes of inner-layer such as temperature, dimensions, mass, thermal properties

        Returns
        -------

        """
        return self.__layer_inner

    @property
    def mid_layer(self) -> Layer:
        """

        Access to layer attributes of mid-layer such as temperature, dimensions, mass, thermal properties

        Returns
        -------

        """
        return self.__layer_mid

    @property
    def outer_layer(self) -> Layer:
        """
        Access to layer attributes of outer-layer such as temperature, dimensions, mass, thermal properties

        Returns
        -------

        """
        return self.__layer_outer

    @property
    def internal_volume(self) -> float:
        """
        Returns internal volume of housing in m3

        Returns
        -------

        """
        return (self.inner_layer.length * self.inner_layer.breadth * self.inner_layer.height) * self.__scale_factor

    @property
    def internal_air_volume(self) -> float:
        """
        Returns internal air volume of housing in m3

        Returns
        -------

        """
        return self.internal_volume - self.__internal_component_volume

    @property
    @abstractmethod
    def azimuth(self) -> float:
        pass

    @property
    @abstractmethod
    def albedo(self) -> float:
        pass

    def get_number_of_containers(self) -> int:
        return self.__scale_factor

    def close(self) -> None:
        self.__log.close()
