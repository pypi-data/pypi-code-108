from dataclasses import dataclass
from typing import List

from magnumapi.optimization.config.ObjectiveConfig import ObjectiveConfig
from magnumapi.optimization.config.OptimizationNotebookConfig import OptimizationNotebookConfig


@dataclass
class ModelRunnerConfig:
    geometry_input_rel_path: str
    geometry_type: str
    cadata_input_rel_path: str
    is_notebook_scripted: bool
    model_creation_type: str
    objectives: List[ObjectiveConfig]
    notebooks: List[OptimizationNotebookConfig]

    def __str__(self) -> str:
        notebooks_str = "\n\n".join(str(notebook) for notebook in self.notebooks)
        objectives_str = "\n\n".join(str(objective) for objective in self.objectives)
        return "geometry_input_rel_path: %s\n" \
               "geometry_type: %s\n" \
               "cadata_input_rel_path: %s\n" \
               "is_notebook_scripted: %s\n" \
               "model_creation_type: %s" \
               "\n\nobjectives: \n\n%s" \
               "\n\nnotebooks: \n\n%s" % (self.geometry_input_rel_path,
                                          self.geometry_type,
                                          self.cadata_input_rel_path,
                                          self.is_notebook_scripted,
                                          self.model_creation_type,
                                          objectives_str,
                                          notebooks_str)

    @staticmethod
    def initialize_config(config_dct: dict) -> "ModelRunnerConfig":
        """ Static method initializing a model runner config from a dictionary

        :param config_dct: a model runner config dictionary
        :return: initialized ModelRunnerConfig instance
        """

        geometry_input_rel_path = config_dct['geometry_input_rel_path']
        geometry_type = config_dct['geometry_type']
        cadata_input_rel_path = config_dct['cadata_input_rel_path']
        is_notebook_scripted = config_dct['is_notebook_scripted']
        model_creation_type = config_dct['model_creation_type']

        objectives = [ObjectiveConfig(**obj) for obj in config_dct['objectives']]
        notebooks = [OptimizationNotebookConfig(**nb) for nb in config_dct['notebooks']]

        return ModelRunnerConfig(geometry_input_rel_path=geometry_input_rel_path,
                                 geometry_type=geometry_type,
                                 cadata_input_rel_path=cadata_input_rel_path,
                                 is_notebook_scripted=is_notebook_scripted,
                                 model_creation_type=model_creation_type,
                                 objectives=objectives,
                                 notebooks=notebooks)

    def get_weight(self, objective: str) -> float:
        """ Method iterating through the list of objective config, finding a matching name and returning
        corresponding weight.

        :param objective: name of an objective variable
        :return: value of the objective weight
        """
        for config_objective in self.objectives:
            if config_objective.objective == objective:
                return config_objective.weight

        raise KeyError('Objective name %s not present in objective configs.' % objective)

    def get_constraint(self, objective: str) -> float:
        """ Method iterating through the list of objective config, finding a matching name and returning
        corresponding constraint.

        :param objective: name of an objective variable
        :return: value of the objective constraint
        """
        for config_objective in self.objectives:
            if config_objective.objective == objective:
                return config_objective.constraint

        raise KeyError('Objective name %s not present in objective configs.' % objective)
