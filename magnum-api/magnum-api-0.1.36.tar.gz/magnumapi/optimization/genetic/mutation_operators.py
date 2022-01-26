from copy import deepcopy
from dataclasses import dataclass

import numpy as np

from magnumapi.optimization.config.UpdateOperatorConfig import OperatorConfig
from magnumapi.optimization.design_variable.Individual import Individual


@dataclass
class MutationOperator:
    r_mut : float

    def mutate(self, individual: Individual) -> Individual:
        """ Method performing a bit-flip mutation with a certain probability

        :param individual: input individual for which the mutation is performed
        :return: updated individual
        """
        chromosome = individual.assemble_chromosome()
        for i in range(len(chromosome)):
            # check for a mutation
            if np.random.rand() < self.r_mut:
                # flip the bit
                chromosome[i] = 1 - chromosome[i]

        individual_out = deepcopy(individual)
        individual_out.sequence_chromosome(chromosome)
        return individual_out


type_to_update_factory_class = {"default": MutationOperator}


class MutationOperatorFactory:

    @staticmethod
    def build(config: OperatorConfig):
        return type_to_update_factory_class[config.type](**config.params)