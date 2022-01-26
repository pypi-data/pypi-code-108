import os
from pathlib import Path

from magnumapi.commons.DirectoryManager import DirectoryManager
from magnumapi.optimization.model import NotebookConverter
from magnumapi.optimization.logger.Logger import Logger
from magnumapi.optimization.model.ModelRunner import ModelRunner
from magnumapi.optimization.config.OptimizationConfig import OptimizationConfig
from magnumapi.optimization.design_variable.DesignVariableFactory import init_genetic_design_variables_with_csv
from magnumapi.optimization.design_variable.Individual import Individual
from magnumapi.optimization.genetic.update_operators import UpdateOperatorFactory


class GeneticOptimizationDirectoryManager:

    @staticmethod
    def initialize_folder_structure(config: OptimizationConfig) -> Path:
        """ Method initializing the folder directory structure to store optimization results outside of the main
        directory.

        :return: a path to the output root directory where all results are stored.
        """
        DirectoryManager.create_directory_if_nonexistent(Path(config.output_abs_path))
        subdirectory_name = DirectoryManager.find_output_subdirectory_name(config.output_abs_path)
        if config.append_new_output_subdirectory:
            subdirectory_name = subdirectory_name + 1
        subdirectory_name = str(subdirectory_name)
        output_subdirectory_dir = Path(config.output_abs_path).joinpath(subdirectory_name)

        DirectoryManager.delete_directory_if_existent(output_subdirectory_dir)
        DirectoryManager.create_directory_if_nonexistent(output_subdirectory_dir)
        # ToDo: Get rid of hardcoded paths
        DirectoryManager.copy_folder_content(config.root_abs_path, 'input', output_subdirectory_dir)
        DirectoryManager.copy_notebook_folders(config.root_abs_path,
                                               config.model_runner_config.notebooks,
                                               output_subdirectory_dir)
        DirectoryManager.create_directory_if_nonexistent(output_subdirectory_dir.joinpath(config.optimization_folder))
        DirectoryManager.copy_folder_content(config.root_abs_path, os.path.join(config.optimization_folder, 'input'), output_subdirectory_dir)

        logger_path = os.path.join(output_subdirectory_dir, config.logger_rel_path)
        print('The logger is saved in: %s' % logger_path)

        for config_notebook in config.model_runner_config.notebooks:
            input_ipynb_file_path = os.path.join(output_subdirectory_dir,
                                                 config_notebook.notebook_folder,
                                                 config_notebook.notebook_name)
            output_ipynb_file_path = os.path.join(output_subdirectory_dir,
                                                  config_notebook.notebook_folder,
                                                  config_notebook.notebook_name.lower().replace('.ipynb', '_script.py'))
            NotebookConverter.convert_notebook_to_script(input_ipynb_file_path,
                                                         config_notebook.notebook_name.lower().split('.')[0],
                                                         output_ipynb_file_path)

        return output_subdirectory_dir


class GeneticOptimizationBuilder:

    @staticmethod
    def build(config: OptimizationConfig, output_subdirectory_dir):
        update_operator = UpdateOperatorFactory.build(config.update_operator_config)

        logger = Logger(os.path.join(output_subdirectory_dir, config.optimization_folder, config.logger_rel_path))

        design_variables = init_genetic_design_variables_with_csv(os.path.join(output_subdirectory_dir,
                                                                               config.optimization_folder,
                                                                               config.design_variables_rel_path))
        model_runner = ModelRunner(config.model_runner_config, output_subdirectory_dir)

        return GeneticOptimization(n_pop=config.n_pop,
                                   n_gen=config.n_gen,
                                   update_operator=update_operator,
                                   logger=logger,
                                   model_runner=model_runner,
                                   design_variables=design_variables)


class GeneticOptimization:
    """ A GeneticOptimization class implementing a basic genetic optimization algorithm. The class contains methods
    for updating a ROXIE input according to the update from the genetic algorithm.

    """
    def __init__(self,
                 n_pop,
                 n_gen,
                 update_operator,
                 logger,
                 model_runner,
                 design_variables) -> None:
        """ Constructor of a RoxieGeneticOptimization instance

        """

        # to genetic operators config
        self.individuals = []

        # to config
        self.n_pop = n_pop
        self.n_gen = n_gen

        self.update_operator = update_operator
        self.logger = logger

        self.model_runner = model_runner
        self.design_variables = design_variables

    def optimize(self) -> None:
        """ Method executing the main optimization loop of the genetic algorithm

        """
        # enumerate generations
        for gen in range(self.n_gen):
            print('Generation:', gen)
            self.initialize_or_execute(gen)
            self.calculate_scores()
            self.display_scores()

            self.logger.append_individuals_to_logger(self.individuals)
            self.logger.save_logger()
            self.model_runner.save_the_best_individual(self.individuals, gen)

            self.individuals = self.update_operator.update_generation(self.individuals)

    def initialize_or_execute(self, gen):
        if gen == 0:
            while len(self.individuals) < self.n_pop:
                individual = Individual(self.design_variables)
                individual = self.model_runner.model_translator.generate_random_individual(individual)
                individual = self.execute_individual_model(individual)

                if individual.is_fom_correct():
                    self.individuals.append(individual)
        else:
            self.individuals = [self.model_runner.execute_model_with_error_handling(individual, index)
                                for index, individual in enumerate(self.individuals)]

    def execute_individual_model(self, individual):
        return self.model_runner.execute_model_with_error_handling(individual, len(self.individuals))

    def calculate_scores(self):
        for individual in self.individuals:
            print('Figures of merit', individual.fom)
            individual.score = individual.calculate_score(self.model_runner.objective_configs)
            print('Score', individual.score)

    def display_scores(self):
        individuals_sorted = sorted(self.individuals, key=lambda individual: individual.score)
        scores = [individual.score for individual in individuals_sorted]
        print(scores)
        print(individuals_sorted[0].assemble_chromosome())
