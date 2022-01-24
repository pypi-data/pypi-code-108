from pydantic.dataclasses import dataclass
from typing import List

import numpy as np

from magnumapi.optimization.config.UpdateOperatorConfig import OperatorConfig
from magnumapi.optimization.design_variable.Individual import Individual


@dataclass
class SelectionOperator:
    k_selection: int

    def select(self, individuals: List[Individual]) -> Individual:
        """ Method selecting best individuals according to the fitness value. The algorithm starts with a randomly
        selected individual. Then, it selects k random indices. For each of the indices it updates the initially
        selected individual by comparing the fitness with k selected individuals.

        :param individuals: population of individuals, a list of genomes; sorted according to the score in ascending order
        :param scores: a list of fitness function scores, one per genome; sorted according to the score in ascending
        order
        :param k: the size of the tournament selection
        :return: a selected genome
        """
        # first random selection
        selection_ix = np.random.randint(len(individuals))
        for ix in np.random.randint(0, len(individuals), self.k_selection - 1):
            # check if better (i.e. perform a tournament)
            if individuals[ix].score < individuals[selection_ix].score:
                selection_ix = ix

        return individuals[selection_ix]


type_to_update_factory_class = {"default": SelectionOperator}


class SelectionOperatorFactory:

    @staticmethod
    def build(config: OperatorConfig):
        return type_to_update_factory_class[config.type](**config.params)