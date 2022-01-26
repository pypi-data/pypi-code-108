from dataclasses import dataclass


@dataclass
class BlockDefinition:
    """Class for block definition.

   Attributes:
       no (int): The row index of a block definition
       type (int): The block type (e.g., 1 - cos-theta, 2 - rectangular).
       nco (int): The number of conductors.
       current (float): The current in a block.
       condname (str): The name of a conductor in the cable database.
       n1 (int): The number of strands in the narrow direction.
       n2 (int): The number of strands in the wide direction.
       imag (int): 1: Block imaged at x-axis; 0: No action. (not with "Symmetric Coil" -option).
       turn (float): Block turned by angle. (not with "Symmetric Coil" -option).
    """
    no: int
    type: int
    nco: int
    current: float
    condname: str
    n1: int
    n2: int
    imag: int
    turn: float