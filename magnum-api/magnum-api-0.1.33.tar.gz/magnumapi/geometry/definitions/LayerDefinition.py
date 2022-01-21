import ast
from typing import Union


class LayerDefinition:
    """Class for layer definition.
    """

    def __init__(self, no: int, symm: int, typexy: int, blocks: Union[str, list]) -> None:
        """ A constructor of a layer definition instance

        :param no: the row index of a layer definition
        :param symm: multipolar symmetry
        :param typexy: It takes four values:
        - None: The blocks are not duplicated. In 3D one semi-arc of an n-polar coil end is generated.
        - All: All blocks of an n-polar coil are generated. In 3D full coil arcs are generated.
        - One coil: The selected blocks are duplicated only once and placed as to constitute one coil of an n-polar
        cross-section. In 3D a full arc is generated
        - Connection side: the selected blocks are duplicated once per coil in an n-polar cross-section. In 3D only
        semi-arcs are generated. In a connection-side coil end of the asymmetric second half needs to be generated
        separately.
        :param blocks: a list of block indices belonging to a layer
        """
        self.no = no
        self.symm = symm
        self.typexy = typexy
        if isinstance(blocks, str):
            self.blocks = ast.literal_eval(blocks)
        else:
            self.blocks = blocks

    def to_roxie_dict(self):
        return dict(no=self.no,
                    symm=self.symm,
                    typexy=self.typexy,
                    blocks=' '.join([str(block) for block in self.blocks]))


class SlottedLayerDefinition(LayerDefinition):

    def __init__(self,
                 no: int,
                 symm: int,
                 typexy: int,
                 spar_thickness: float,
                 midplane_wedge_thickness: float,
                 blocks: Union[str, list]) -> None:
        """ A constructor of a layer definition instance

        :param spar_thickness: a thickness of a layer spar in mm
        :param midplane_wedge_thickness: a thickness of a midplane wedge in mm
        """
        super().__init__(no=no, symm=symm, typexy=typexy, blocks=blocks)
        self.spar_thickness = spar_thickness
        self.midplane_wedge_thickness = midplane_wedge_thickness
