from dataclasses import dataclass
import magnumapi.commons.json_file as json_file
from magnumapi.optimization.config.ModelRunnerConfig import ModelRunnerConfig

from magnumapi.optimization.config.OptimizationConfig import OptimizationConfig
from magnumapi.optimization.config.UpdateOperatorConfig import UpdateOperatorConfig


@dataclass
class ParallelOptimizationConfig(OptimizationConfig):
    """Class for parallel optimization config used for the genetic algorithm.

    Attributes:
       ansys (ParallelAnsysConfig): parallel ANSYS config

    """
    ansys: "ParallelAnsysConfig"

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
               "\nmodel_runner_config: \n\n%s" \
               "\nansys: \n\n%s" % (self.root_abs_path,
                                    self.output_abs_path,
                                    self.optimization_folder,
                                    self.append_new_output_subdirectory,
                                    self.n_pop,
                                    self.n_gen,
                                    self.logger_rel_path,
                                    self.design_variables_rel_path,
                                    self.update_operator_config,
                                    self.model_runner_config,
                                    self.ansys)

    @staticmethod
    def initialize_config(json_path: str) -> "ParallelOptimizationConfig":
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
        ansys = ParallelAnsysConfig(**data['ansys'])
        return ParallelOptimizationConfig(root_abs_path=root_abs_path,
                                          output_abs_path=output_abs_path,
                                          optimization_folder=optimization_folder,
                                          append_new_output_subdirectory=append_new_output_subdirectory,
                                          n_gen=n_gen,
                                          n_pop=n_pop,
                                          logger_rel_path=logger_rel_path,
                                          design_variables_rel_path=design_variables_rel_path,
                                          update_operator_config=update_operator_config,
                                          model_runner_config=model_runner_config,
                                          ansys=ansys)


@dataclass
class ParallelAnsysConfig:
    run_dir: str
    n_parallel_runners: int
    n_proc: int
    root_dir: str
    exec_file: str
    master_input_file: str
    template_to_input_file: dict
    additional_upload_files: list
