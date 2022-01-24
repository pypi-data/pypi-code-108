from dataclasses import dataclass

from magnumapi.cadata.Definition import Definition


@dataclass
class RemFitDefinition(Definition):
    """Class for remenent magnetization definition definition.

       Attributes:
           type (float): The Remfit type.
           c1 (float): fit coefficient 1.
           c2 (float): fit coefficient 2.
           c3 (float): fit coefficient 3.
           c4 (float): fit coefficient 4.
           c5 (float): fit coefficient 5.
           c6 (float): fit coefficient 6.
           c7 (float): fit coefficient 7.
           c8 (float): fit coefficient 8.
           c9 (float): fit coefficient 9.
           c10 (float): fit coefficient 10.
           c11 (float): fit coefficient 11.
    """
    type: str = ''
    c1: float = 0.0
    c2: float = 0.0
    c3: float = 0.0
    c4: float = 0.0
    c5: float = 0.0
    c6: float = 0.0
    c7: float = 0.0
    c8: float = 0.0
    c9: float = 0.0
    c10: float = 0.0
    c11: float = 0.0

    @staticmethod
    def get_magnum_to_roxie_dct() -> dict:
        return {"name": "Name",
                "type": "Type",
                "c1": "C1",
                "c2": "C2",
                "c3": "C3",
                "c4": "C4",
                "c5": "C5",
                "c6": "C6",
                "c7": "C7",
                "c8": "C8",
                "c9": "C9",
                "c10": "C10",
                "c11": "C11",
                "comment": "Comment"}
