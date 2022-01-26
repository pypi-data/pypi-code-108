from enum import Enum

from parchmint.layer import Layer


class MINTLayerType(Enum):
    FLOW = 1
    CONTROL = 2
    INTEGRATION = 3

    def __str__(self) -> str:
        if self == MINTLayerType.FLOW:
            return "FLOW"
        elif self == MINTLayerType.CONTROL:
            return "CONTROL"
        elif self == MINTLayerType.INTEGRATION:
            return "INTEGRATION"
        else:
            raise Exception("Could not generate MINT Layer string")

    def __eq__(self, o: object) -> bool:
        if o.__class__ is MINTLayerType:
            return super().__eq__(o)
        elif o.__class__ is str:
            if self is MINTLayerType.FLOW and o == "FLOW":
                return True
            elif self is MINTLayerType.CONTROL and o == "CONTROL":
                return True
            elif self is MINTLayerType.INTEGRATION and o == "INTEGRATION":
                return True
            else:
                return False
        else:
            return False


class MINTLayer(Layer):
    """MINT Layer class that abstracts the Layer class and adds additional
    methods to help generating MINT
    """

    def __init__(
        self,
        id: str,
        name: str,
        group: str,
        layer_type: MINTLayerType,
    ) -> None:
        """Creates a MINT layer object

        Args:
            id (str): unique id of the layer
            name (str): name of the layer
            group (str): group name
            layer_type (MINTLayerType): layer type of the layer
        """
        super(MINTLayer, self).__init__()
        self.ID = id
        self.group = group
        self.name = name
        self.type = str(layer_type)

    def to_MINT(self, content: str) -> str:
        """Generates the MINT string for the layer

        Args:
            content (str): MINT content that needs to be wrapped into the layer MINT

        Returns:
            str: Returns the MINT string
        """
        ret = "LAYER {} \n\n{} \n\nEND LAYER".format(self.type, content)
        return ret
