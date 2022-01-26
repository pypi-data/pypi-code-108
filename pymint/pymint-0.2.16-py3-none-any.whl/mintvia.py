from typing import List, Union

from parchmint.layer import Layer

from pymint.mintcomponent import MINTComponent
from pymint.mintlayer import MINTLayer


class MINTVia(MINTComponent):
    """Class to represent MINT Vias that are modelled as a Parchmint component.
    The class has helpful methods for adding and modifying the vias

    """

    def __init__(self, name: str, layers: List[Union[MINTLayer, Layer]]) -> None:
        """Creates a new instance of a Via

        Args:
            name (str): name/ID of the via
            layers (List[MINTLayer]): List of layer objects where the via is present
        """
        width = 0
        super(MINTVia, self).__init__(name, "VIA", {"width": width}, layers)

    def set_width(self, width: int) -> None:
        """Sets the width of the via

        Args:
            width (int): via width
        """
        self.params.set_param("width", width)

    def to_MINT(self) -> str:
        """Returns the MINT string of the via

        Returns:
            str: returns the via
        """
        return "VIA {}".format(self.name)
