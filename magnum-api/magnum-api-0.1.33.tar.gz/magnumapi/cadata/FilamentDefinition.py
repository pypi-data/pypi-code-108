from dataclasses import dataclass

from magnumapi.cadata.Definition import Definition


@dataclass
class FilamentDefinition(Definition):
    """Class for strand definition.

       Attributes:
           d_fil_out (float): The outer diameter of filament (um).
           d_fil_in (float): The inner diameter of filament (um).
           fit_j_c (str): Critical current fit.
           fit_perp (str): Name of the critical surface fit for orthogonal direction 2.
    """
    d_fil_out: float
    d_fil_in: float
    fit_j_c: str
    fit_perp: str

    @staticmethod
    def get_magnum_to_roxie_dct() -> dict:
        return {"name": "Name",
                "d_fil_out": "fildiao",
                "d_fil_in": "fildiai",
                "fit_j_c": "Jc-Fit",
                "fit_perp": "fit-|",
                "comment": "Comment"}
