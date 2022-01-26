import os

from ansys.mapdl.core import LocalMapdlPool

from magnumapi.optimization.GeneticOptimization import GeneticOptimization
from magnumapi.optimization.config.ParallelOptimizationConfig import ParallelOptimizationConfig
from magnumapi.optimization.design_variable.DesignVariableFactory import init_genetic_design_variables_with_csv
from magnumapi.optimization.genetic.update_operators import UpdateOperatorFactory
from magnumapi.optimization.logger.Logger import Logger
from magnumapi.optimization.model.ModelRunner import ModelRunner
from magnumapi.tool_adapters.ansys.AnsysInputBuilder import AnsysInputBuilder
from magnumapi.tool_adapters.ansys.AnsysToolAdapter import AnsysToolAdapter


class ParallelGeneticOptimizationBuilder:
    @staticmethod
    def build(config: ParallelOptimizationConfig, output_subdirectory_dir):
        update_operator = UpdateOperatorFactory.build(config.update_operator_config)

        logger = Logger(os.path.join(output_subdirectory_dir, config.logger_rel_path))

        design_variables = init_genetic_design_variables_with_csv(os.path.join(output_subdirectory_dir,
                                                                               config.optimization_folder,
                                                                               config.design_variables_rel_path))
        model_runner = ModelRunner(config.model_runner_config, output_subdirectory_dir)

        return ParallelGeneticOptimization(n_pop=config.n_pop,
                                           n_gen=config.n_gen,
                                           update_operator=update_operator,
                                           logger=logger,
                                           model_runner=model_runner,
                                           design_variables=design_variables,
                                           config_ansys=config.ansys,
                                           output_subdirectory_dir=output_subdirectory_dir)


class ParallelGeneticOptimization(GeneticOptimization):

    def __init__(self,
                 n_pop,
                 n_gen,
                 update_operator,
                 logger,
                 model_runner,
                 design_variables,
                 config_ansys,
                 output_subdirectory_dir):
        super().__init__(n_pop=n_pop,
                         n_gen=n_gen,
                         update_operator=update_operator,
                         logger=logger,
                         model_runner=model_runner,
                         design_variables=design_variables)
        self.config_ansys = config_ansys
        self.output_subdirectory_dir = output_subdirectory_dir

    def initialize_optimization(self):
        root_dir = os.path.join(self.output_subdirectory_dir, self.config_ansys.root_dir)
        template_rel_dir = os.path.join(root_dir, 'template')

        for index in range(self.n_pop):
            for template_file, input_file in self.config_ansys.template_to_input_file.items():
                template_path = os.path.join(template_rel_dir, template_file)
                AnsysInputBuilder.update_input_template(template_path, index, root_dir, input_file)

    def optimize(self) -> None:
        """ Method executing the main optimization loop of the genetic algorithm

        """
        # enumerate generations
        for gen in range(self.n_gen):
            print('Generation:', gen)
            self.initialize_or_execute(gen)
            ###
            # execute ANSYS in parallel
            root_dir = os.path.join(self.output_subdirectory_dir, self.config_ansys.root_dir)
            AnsysToolAdapter.remove_ansys_output_files(root_dir, self.n_pop)

            indices = self.extract_calculated_indices()
            print('indices to process: ', indices)
            pool = LocalMapdlPool(self.config_ansys.n_parallel_runners,
                                  exec_file=self.config_ansys.exec_file,
                                  nproc=self.config_ansys.n_proc,
                                  run_location=self.config_ansys.run_dir)
            upload_files = list(self.config_ansys.template_to_input_file.values()) \
                           + self.config_ansys.additional_upload_files
            execute_ansys_in_parallel(pool, root_dir, self.config_ansys.master_input_file, upload_files, indices)
            pool.exit()
            # read figures of merit
            ansys_fom_dcts = AnsysToolAdapter.read_multiple_ansys_figures_of_merit(root_dir, self.n_pop)

            # merge list of figures of merit
            for index, individual in enumerate(self.individuals):
                individual.fom = {**individual.fom, **ansys_fom_dcts[index]}
            ###
            self.calculate_scores()
            self.display_scores()

            self.logger.append_individuals_to_logger(self.individuals)
            self.logger.save_logger()
            self.model_runner.save_the_best_individual(self.individuals, gen)

            self.individuals = self.update_operator.update_generation(self.individuals)

    def execute_individual_model(self, individual):
        fom_dct_init = {"index": len(self.individuals)}
        return self.model_runner.execute_model_with_error_handling(individual, len(self.individuals), fom_dct_init)

    def extract_calculated_indices(self):
        indices = []
        for index, individual in enumerate(self.individuals):
            if individual.is_fom_correct():
                indices.append(index)
        return indices


def execute_ansys_in_parallel(pool, root_dir, master_input_file, upload_files, indices):
    def mapping_function(mapdl, root_dir, master_input_file, upload_files, index):
        mapdl.clear()
        # upload input and macro files prior to model execution
        input_file = master_input_file % index

        for upload_file in upload_files:
            mapdl.upload(os.path.join(root_dir, upload_file % index), progress_bar=False)

        # run model
        mapdl.input(os.path.join(root_dir, input_file))

        # download output file
        output_file = 'vallone_%d.out' % index
        mapdl.download(output_file, os.path.join(root_dir, output_file))
        return mapdl.parameters.routine

    inputs = [(root_dir, master_input_file, upload_files, index) for index in indices]

    pool.map(mapping_function, inputs, progress_bar=True, wait=True)
