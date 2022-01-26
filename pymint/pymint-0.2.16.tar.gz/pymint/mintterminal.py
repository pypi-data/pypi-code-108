from typing import Union
from parchmint.layer import Layer
from pymint.mintcomponent import MINTComponent
from pymint.mintlayer import MINTLayer


class MINTTerminal(MINTComponent):
    """Class for representing the MINT terminal, its modelled as a
    Parchmint Component while giving helpful methods to model the design

    """

    def __init__(
        self, name: str, port_number: int, layer: Union[MINTLayer, Layer]
    ) -> None:
        super(MINTTerminal, self).__init__(name, "TERMINAL", {}, [layer])
        self.__port_number = port_number

    @property
    def port_number(self) -> int:
        """Returns the port number of the terminal (at a device level)

        Returns:
            int: port value
        """
        return self.__port_number

    def to_MINT(self) -> str:
        return "TERMINAL {} {}".format(self.name, self.__port_number)
