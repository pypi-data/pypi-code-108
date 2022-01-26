import math
from dataclasses import dataclass

from magnumapi.cadata.Definition import Definition


@dataclass
class StrandDefinition(Definition):
    """Class for strand definition.

       Attributes:
           d_strand (float): The strand diameter (mm).
           f_cu_nocu (float): The Copper to superconductor ratio.
           rrr (float): The Residual Resistivity ratio.
           temp_ref (float): The Reference Temperature (K) for Bref. This value is never used in the code and serves
           only for reference for Bref and Jc@BrTr.
           b_ref (float): The Reference Field for the definition of a linear approximation of the Jc curve.
           j_c_at_b_ref_t_ref (float): The Critical current density at Bref for the definition of a linear approximation
           of the Jc curve. (LINMARG)
           dj_c_over_db (float): dJc/dB at Bref and Tref for the definition of a linear approximation of the Jc curve.
           (LINMARG)
    """
    d_strand: float
    f_cu_nocu: float
    rrr: float
    temp_ref: float
    b_ref: float
    j_c_at_b_ref_t_ref: float
    dj_c_over_db: float

    @staticmethod
    def get_magnum_to_roxie_dct() -> dict:
        return {"name": "Name",
                "d_strand": "diam.",
                "f_cu_nocu": "cu/sc",
                "rrr": "RRR",
                "temp_ref": "Tref",
                "b_ref": "Bref",
                "j_c_at_b_ref_t_ref": "Jc@BrTr",
                "dj_c_over_db": "dJc/dB",
                "comment": "Comment"}

    def compute_surface_cu(self):
        """ Method computing copper surface of a strand as S = f_co * pi * d_strand^2 / 4

        :return: a copper surface of a strand in mm^2
        """
        return self.compute_f_cu() * self.compute_surface()

    def compute_surface_nocu(self):
        """ Method computing non-copper surface of a strand as S = f_nocu * pi * d_strand^2 / 4

        :return: a non-copper surface of a strand in mm^2
        """
        return self.compute_f_nocu() * self.compute_surface()

    def compute_f_nocu(self):
        """ Method fraction of non-copper in a strand

        :return: a fraction of non-copper in a strand (no unit)
        """
        return 1 / (1 + self.f_cu_nocu)

    def compute_f_cu(self):
        """ Method fraction of copper in a strand

        :return: a fraction of copper in a strand (no unit)
        """
        return self.f_cu_nocu / (1 + self.f_cu_nocu)

    def compute_surface(self):
        """ Method computing surface of a strand as S = pi * d_strand^2 / 4

        :return: a surface of a strand in mm^2
        """
        return math.pi * self.d_strand**2 / 4
