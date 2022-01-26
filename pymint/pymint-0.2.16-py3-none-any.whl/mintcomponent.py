from __future__ import annotations

from typing import TYPE_CHECKING, List, Union

from parchmint.component import Component
from parchmint.layer import Layer

if TYPE_CHECKING:
    from pymint import MINTLayer

from pymint.mintparams import MINTParams


class MINTComponent(Component):
    """Component Class abstracting parchmint component
    while adding helper methods to generate MINT

    """

    def __init__(
        self,
        name: str,
        technology: str,
        params: dict,
        layers: List[Union[MINTLayer, Layer]] = None,
    ) -> None:
        """Creates a MINT component

        Args:
            name (str): [description]
            technology (str): [description]
            params (dict): [description]
            layers (List[MINTLayer], optional): [description]. Defaults to None.

        Raises:
            Exception: hrows the exception if no layer information is present
        """
        super(MINTComponent, self).__init__()
        self.name = name
        self.ID = name
        self.entity = technology
        self.params = MINTParams(params)
        if layers is None:
            raise Exception("Cannot have no layer information")
        for layer in layers:
            self.layers.append(layer)

    def overwrite_id(self, id: str) -> None:
        """Overwites the ID

        Args:
            id (str): New id of the component
        """
        self.ID = id

    @property
    def component_spacing(self) -> int:
        """Returns the component spacing of the component

        Returns:
            int: Component Spacing Value in microns
        """
        return self.params.get_param("component_spacing")

    @component_spacing.setter
    def connection_spacing(self, value: int) -> None:
        """Sets the component spacing of the component

        Args:
            value (int): Value for the component spacing in microns
        """
        self.params.set_param("component_spacing", value)

    def to_MINT(self) -> str:
        """Returns the MINT String for the component

        Returns:
            str: This is the MINT string for the serialization
        """
        ret = "{} {} {};".format(self.entity, self.name, self.params.to_MINT())
        return ret

    def __hash__(self) -> int:
        return hash((self.ID, self.entity))
