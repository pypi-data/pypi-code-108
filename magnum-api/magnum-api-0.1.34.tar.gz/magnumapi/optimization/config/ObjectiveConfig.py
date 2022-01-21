from dataclasses import dataclass


@dataclass
class ObjectiveConfig:
    """Class for objective config used for fitness function calculation.

    Attributes:
       objective (str): The name of an objective
       weight (float): The weight of an objective
       constraint (float): The constraint value of an objective (subtracted from the objective)
    """
    objective: str
    weight: float
    constraint: float

    def __str__(self):
        return "objective: %s\n" \
               "weight: %f\n" \
               "constraint: %f" % (self.objective,
                                   self.weight,
                                   self.constraint)
