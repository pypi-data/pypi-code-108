from copy import deepcopy
from dataclasses import dataclass
from typing import Tuple

import numpy as np

from magnumapi.optimization.config.UpdateOperatorConfig import OperatorConfig
from magnumapi.optimization.design_variable.Individual import Individual


@dataclass
class CrossOverOperator:
    r_cross : float

    def crossover(self, parent1: Individual, parent2: Individual) -> Tuple[Individual, Individual]:
        """ Method performing a single cross-over operation between two parents and creates two children. The cross-over
        point is selected at random.

        :param parent1: first parent
        :param parent2: second parent
        :return: a tuple with two children
        """
        # children chromosomes are copies of parents by default
        chromosome1, chromosome2 = parent1.assemble_chromosome(), parent2.assemble_chromosome()
        chromosome1_copy, chromosome2_copy = deepcopy(chromosome1), deepcopy(chromosome2)
        # check for recombination
        if np.random.rand() < self.r_cross:
            # select crossover point that is not on the end of the bitstring chromosome
            idx_crossover = np.random.randint(1, len(chromosome1) - 2)
            # perform crossover
            chromosome1 = chromosome1_copy[:idx_crossover] + chromosome2_copy[idx_crossover:]
            chromosome2 = chromosome2_copy[:idx_crossover] + chromosome1_copy[idx_crossover:]
        child1 = deepcopy(parent1)
        child2 = deepcopy(parent2)
        child1.sequence_chromosome(chromosome1)
        child2.sequence_chromosome(chromosome2)
        return child1, child2


type_to_update_factory_class = {"default": CrossOverOperator}


class CrossOverOperatorFactory:

    @staticmethod
    def build(config: OperatorConfig):
        return type_to_update_factory_class[config.type](**config.params)