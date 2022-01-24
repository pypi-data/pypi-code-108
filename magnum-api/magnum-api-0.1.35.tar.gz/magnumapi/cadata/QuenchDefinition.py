from dataclasses import dataclass

from magnumapi.cadata.Definition import Definition


@dataclass
class QuenchDefinition(Definition):
    """Class for quench definition.

       Attributes:
           cp_sc (str): The fit function for the specific heat of the superconductor.
           See also: http://cern.ch/roxie > Documentation > Materials.pdf
           cp_cu (str): The fit function for the specific heat of copper.
           See also: http://cern.ch/roxie > Documentation > Materials.pdf
           k_cu (str): The fit function for the thermal conductivity of copper.
           See also: http://cern.ch/roxie > Documentation > Materials.pdf
           res_cu (str): The fit function for the electrical resistitvity of copper.
           See also: http://cern.ch/roxie > Documentation > Materials.pdf
           cp_ins (str): The fit function for the heat capacity of the cable insulation.
           See also: http://cern.ch/roxie > Documentation > Materials.pdf
           k_ins (str): The fit function for the thermal conductivity of the cable insulation.
           See also: http://cern.ch/roxie > Documentation > Materials.pdf
           cp_fill (str): The fit function for the heat capacity of the material filling the cable voids.
           See also: http://cern.ch/roxie > Documentation > Materials.pdf
           perc_he (float): The percentage of the cable voids that is filled by helium.

    """
    cp_sc: str = ''
    cp_cu: str = ''
    k_cu: str = ''
    res_cu: str = ''
    cp_ins: str = ''
    k_ins: str = ''
    cp_fill: str = ''
    perc_he: float = ''

    @staticmethod
    def get_magnum_to_roxie_dct() -> dict:
        return {"name": "Name",
                "cp_sc": "SCHeatCapa",
                "cp_cu": "CuHeatCapa",
                "k_cu": "CuThermCond",
                "res_cu": "CuElecRes",
                "cp_ins": "InsHeatCapa",
                "k_ins": "InsThermCond",
                "cp_fill": "FillHeatCapa",
                "perc_he": "He%",
                "comment": "Comment"}
