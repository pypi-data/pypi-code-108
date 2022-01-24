from copy import deepcopy
from typing import List

import numpy as np

from magnumapi.optimization.config.ObjectiveConfig import ObjectiveConfig
from magnumapi.optimization.constants import PENALTY, SCORE_KEYWORD
from magnumapi.optimization.design_variable.GeneticDesignVariable import GeneticDesignVariable, \
    GeneticLayerDesignVariable, GeneticBlockDesignVariable, GeneticMultiBlockDesignVariable


class Individual:
    # ToDo: set score and fom as gene and value for DesignVariable
    def __init__(self, gen_dvs: List[GeneticDesignVariable]):
        self.gen_dvs = deepcopy(gen_dvs)
        self.score = float('nan')
        self.fom = {}

    def generate_random_genes(self) -> None:
        for dv in self.gen_dvs:
            dv.generate_random_gene()

    def is_fom_correct(self):
        return all([not np.isnan(value) for value in self.fom.values()])

    def calculate_score(self, objective_configs: List[ObjectiveConfig]) -> float:
        """ Method calculating score from a dictionary mapping objective variable to its value.
        If any of the returned values is NaN, then the penalty value is returned.

        :param objective_configs:
        :return: fitness function value obtained as weighted sum
        """
        if not self.is_fom_correct():
            return PENALTY

        score = 0.0
        for objective_config in objective_configs:
            score += objective_config.weight * (self.fom[objective_config.objective] - objective_config.constraint)

        return score

    def to_dict(self):
        design_variables_to_values = {gen_dv.get_compact_variable_name(): gen_dv.value for gen_dv in self.gen_dvs}
        return {**design_variables_to_values, **self.fom, **{SCORE_KEYWORD: self.score}}

    def get_global_dvs(self) -> List[GeneticDesignVariable]:
        return [gen_dv for gen_dv in self.gen_dvs if isinstance(gen_dv, GeneticDesignVariable)]

    def get_layer_dvs(self) -> List[GeneticLayerDesignVariable]:
        return [gen_dv for gen_dv in self.gen_dvs if isinstance(gen_dv, GeneticLayerDesignVariable)]

    def get_block_dvs(self) -> List[GeneticBlockDesignVariable]:
        return [gen_dv for gen_dv in self.gen_dvs if isinstance(gen_dv, GeneticBlockDesignVariable)]

    def get_multiblock_dvs(self) -> List[GeneticMultiBlockDesignVariable]:
        return [gen_dv for gen_dv in self.gen_dvs if isinstance(gen_dv, GeneticMultiBlockDesignVariable)]

    def assemble_chromosome(self) -> List[int]:
        chromosome = []
        for gen_dv in self.gen_dvs:
            chromosome.extend(gen_dv.gene)

        return chromosome

    def sequence_chromosome(self, chromosome: List[int]) -> None:
        index_start = 0
        for gen_dv in self.gen_dvs:
            index_end = index_start + gen_dv.bits
            gen_dv.gene = chromosome[index_start: index_end]
            index_start = index_end
