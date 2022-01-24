from dataclasses import dataclass

import magnumapi.commons.json_file as json_file
from magnumapi.optimization.config.ModelRunnerConfig import ModelRunnerConfig
from magnumapi.optimization.config.UpdateOperatorConfig import UpdateOperatorConfig


@dataclass
class OptimizationConfig:
    """Class for optimization config used for the genetic algorithm.

    Attributes:
       input_folder (str): The path to an input folder
       output_folder (float): The path to an output folder
       logger_rel_path (float): The path to the logger csv file
       n_pop (int): The number of individuals, i.e., the population size
       n_gen (int): The number of generations
       r_cross (float): The probability of crossover
       r_mut (float): The probability of mutation
       objectives (list): The list of objective configs
       notebooks (list): The list of notebook configs
       model_creation_type (str): type of model creation: default, programmable, targeted
    """
    root_abs_path: str
    output_abs_path: str
    optimization_folder: str
    append_new_output_subdirectory: bool
    n_gen: int
    n_pop: int
    logger_rel_path: str
    design_variables_rel_path: str
    update_operator_config: UpdateOperatorConfig
    model_runner_config: ModelRunnerConfig

    def __str__(self) -> str:
        return "root_abs_path: %s\n" \
               "output_abs_path: %s\n" \
               "optimization_folder: %s\n" \
               "append_new_output_subdirectory: %s\n" \
               "n_pop: %d\n" \
               "n_gen: %d\n" \
               "logger_rel_path: %s\n" \
               "design_variables_rel_path: %s\n" \
               "\nupdate_operator_config: \n\n%s" \
               "\nmodel_runner_config: \n\n%s" % (self.root_abs_path,
                                                  self.output_abs_path,
                                                  self.optimization_folder,
                                                  self.append_new_output_subdirectory,
                                                  self.n_pop,
                                                  self.n_gen,
                                                  self.logger_rel_path,
                                                  self.design_variables_rel_path,
                                                  self.update_operator_config,
                                                  self.model_runner_config)

    @staticmethod
    def initialize_config(json_path: str) -> "OptimizationConfig":
        """ Static method initializing an optimization config from a json file

        :param json_path: a path to a json file with config
        :return: initialized OptimizationConfig instance
        """
        data = json_file.read(json_path)

        root_abs_path = data['root_abs_path']
        output_abs_path = data['output_abs_path']
        optimization_folder = data['optimization_folder']
        append_new_output_subdirectory = data['append_new_output_subdirectory']
        n_gen = data['n_gen']
        n_pop = data['n_pop']
        logger_rel_path = data['logger_rel_path']
        design_variables_rel_path = data['design_variables_rel_path']
        update_operator_config = UpdateOperatorConfig.initialize_config(data['update_operator'])
        model_runner_config = ModelRunnerConfig.initialize_config(data['model_runner'])
        return OptimizationConfig(root_abs_path=root_abs_path,
                                  output_abs_path=output_abs_path,
                                  optimization_folder=optimization_folder,
                                  append_new_output_subdirectory=append_new_output_subdirectory,
                                  n_gen=n_gen,
                                  n_pop=n_pop,
                                  logger_rel_path=logger_rel_path,
                                  design_variables_rel_path=design_variables_rel_path,
                                  update_operator_config=update_operator_config,
                                  model_runner_config=model_runner_config)

    def get_weight(self, objective: str) -> float:
        """ Method iterating through the list of objective config, finding a matching name and returning
        corresponding weight.

        :param objective: name of an objective variable
        :return: value of the objective weight
        """
        return self.model_runner_config.get_weight(objective)

    def get_constraint(self, objective: str) -> float:
        """ Method iterating through the list of objective config, finding a matching name and returning
        corresponding constraint.

        :param objective: name of an objective variable
        :return: value of the objective constraint
        """
        return self.model_runner_config.get_constraint(objective)
