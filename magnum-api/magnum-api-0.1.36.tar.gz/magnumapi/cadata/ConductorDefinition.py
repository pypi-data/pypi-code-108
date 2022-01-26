from dataclasses import dataclass

from magnumapi.cadata.Definition import Definition


@dataclass
class ConductorDefinition(Definition):
    """Class for conductor definition.

       Attributes:
           type (int): The conductor type (e.g., HTS tape, Rutherford cable).
           cable_geom (str): The cable geometry name (defined in Cable geometry block).
           strand (str): The strand name (defined in Strand block).
           filament (str): The filament name (defined in Filament block).
           insulation (str): The insulation name (defined in Insul block).
           transient (str): -
           quench_mat (str): Quench material, not always present. Defaults to an empty string.
           temp_ref (float): The operating temperature in K. All conductors in the cross-section must have the same
            temperature. Adaptations can be made via the design variables.
    """
    type: int
    cable_geom: str
    strand: str
    filament: str
    insulation: str
    transient: str
    temp_ref: float
    quench_mat: str = ''

    @staticmethod
    def get_magnum_to_roxie_dct() -> dict:
        return {"name": "Name",
                "type": "Type",
                "cable_geom": "CableGeom.",
                "strand": "Strand",
                "filament": "Filament",
                "insulation": "Insul",
                "transient": "Trans",
                "quench_mat": "QuenchMat.",
                "temp_ref": "T_o",
                "comment": "Comment"}
