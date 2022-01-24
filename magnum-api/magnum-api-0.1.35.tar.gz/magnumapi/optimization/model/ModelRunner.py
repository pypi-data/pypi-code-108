import json
import os

from magnumapi.cadata.CableDatabase import CableDatabase
from magnumapi.geometry.GeometryFactory import GeometryFactory
from magnumapi.optimization.model.NotebookExecutor import ExecutorFactory
from magnumapi.optimization.config.ModelRunnerConfig import ModelRunnerConfig
from magnumapi.optimization.design_variable.Individual import Individual
from magnumapi.optimization.model.ModelTranslator import ModelTranslator, ModelTranslatorFactory


class ModelRunner:
    def __init__(self, config: ModelRunnerConfig, output_subdirectory_dir):
        self.model_input_path = os.path.join(output_subdirectory_dir, config.geometry_input_rel_path)
        self.cadata_input_path = os.path.join(output_subdirectory_dir, config.cadata_input_rel_path)

        self.output_subdirectory_dir = output_subdirectory_dir
        self.notebook_executor = ExecutorFactory.build(config.is_notebook_scripted)

        self.objective_configs = config.objectives
        self.notebook_configs = config.notebooks
        geometry = self.initialize_geometry(config.geometry_type)
        self.model_translator: ModelTranslator = ModelTranslatorFactory.build(config.model_creation_type, geometry)

    def initialize_geometry(self, geometry_type: str):
        cadata = CableDatabase.read_cadata(self.cadata_input_path)
        if geometry_type == 'slotted':
            geometry = GeometryFactory.init_slotted_with_json(self.model_input_path, cadata)
        elif geometry_type == 'regular':
            geometry = GeometryFactory.init_with_json(self.model_input_path, cadata)
        else:
            raise KeyError('Geometry type %s not supported!' % geometry_type)
        return geometry

    def execute_model_with_error_handling(self, individual: Individual, index, fom_dct_init=None) -> Individual:
        print('\tIndividual:', index)
        try:
            geometry_updated = self.model_translator.update_geometry(individual)
            save_model(geometry_updated.to_dict(), self.model_input_path)
            fom_dct = self.notebook_executor.calculate_figures_of_merit(self.notebook_configs,
                                                                        self.output_subdirectory_dir,
                                                                        individual,
                                                                        fom_dct_init)
        except (AttributeError, TypeError, IndexError, ArithmeticError):
            fom_dct = None

        if fom_dct is None:
            individual.fom = {objective_config.objective: float('nan') for objective_config in self.objective_configs}
        else:
            individual.fom = fom_dct
        return individual

    def save_the_best_individual(self, individuals, gen):
        """Abstract method initializing a population of candidate solutions

        """
        individuals_sorted = sorted(individuals, key=lambda individual: individual.score)
        individual_best = individuals_sorted[0]
        model_input_path_temp = self.model_input_path.replace('.json', "_%d.json" % gen)
        try:
            geometry_updated = self.model_translator.update_geometry(individual_best).to_dict()
            save_model(geometry_updated, model_input_path_temp)
        except (AttributeError, TypeError, IndexError, ArithmeticError):
            print(individual_best.to_dict())
            print(self.model_translator.geometry.to_dict())


def save_model(geometry_updated: dict, model_input_path) -> None:
    # decoded_chromosome: a chromosome decoded into a dictionary with keys corresponding to parameter names
    # (variable and block index) mapping to parameter values

    # write updated input to json
    # ToDo: save model as json to geometry
    with open(model_input_path, 'w') as file:
        json.dump(geometry_updated, file, sort_keys=True, indent=4)
