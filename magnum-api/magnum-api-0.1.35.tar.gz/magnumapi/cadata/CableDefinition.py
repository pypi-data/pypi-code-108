from dataclasses import dataclass

from magnumapi.cadata.Definition import Definition


@dataclass
class CableDefinition(Definition):
    """Class for cable geometry definition.

       Attributes:
           width (float): The length (mm) of the long side of the cable cross-section.
           thickness_i (float): The inner narrow side thickness (mm).
           thickness_o (float): The outer narrow side thickness (mm).
           n_s (int): The number of strands (mm).
           l_tp (float): The length of the transposition pitch (mm) of the Rutherford-type cable.
           f_degrad (float): The degradation of the critical current density in %.
           type (str): The cable type (e.g., Rutherford cable, HTS tape).
    """
    width: float
    thickness_i: float
    thickness_o: float
    n_s: int
    l_tp: float
    f_degrad: float
    type: str = ""

    @staticmethod
    def get_magnum_to_roxie_dct() -> dict:
        return {"name": "Name",
                "width": "height",
                "thickness_i": "width_i",
                "thickness_o": "width_o",
                "n_s": "ns",
                "l_tp": "transp.",
                "f_degrad": "degrd",
                "comment": "Comment",
                "type": None}
