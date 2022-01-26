from abc import ABC, abstractmethod
import os
from shutil import copyfile
from typing import List, Union

import papermill as pm
import scrapbook as sb
from papermill import PapermillExecutionError


from magnumapi.optimization.config.OptimizationNotebookConfig import OptimizationNotebookConfig
from magnumapi.optimization.design_variable.Individual import Individual


class Executor(ABC):
    """An abstract class for model executor used in optimization

    """

    def calculate_figures_of_merit(self,
                                   notebooks: List[OptimizationNotebookConfig],
                                   output_subdirectory_dir,
                                   individual: Individual,
                                   fom_dct_init: dict=None) -> Union[dict, None]:
        """Method calculating figures of merit with scripts or notebooks (papermill and scrapbook packages).

        :param individual: a list of 0s and 1s representing an individual to be executed
        :return: a dictionary with figures of merit if the computation was successful, otherwise an dictionary with NaNs
        """
        # Retrieve global parameters
        global_dvs = individual.get_global_dvs()
        global_design_variables = {global_dv.get_compact_variable_name(): global_dv.value for global_dv in global_dvs}
        fom_dct = {} if fom_dct_init is None else fom_dct_init

        for notebook_config in notebooks:
            notebook_folder = notebook_config.notebook_folder
            notebook_name = notebook_config.notebook_name
            notebook_dir = os.path.join(output_subdirectory_dir, notebook_folder)

            # copy artefacts
            for dest, source in notebook_config.input_artefacts.items():
                copyfile(os.path.join(output_subdirectory_dir, source),
                         os.path.join(notebook_dir, dest))

            # set parameters
            parameters_dct = Executor.merge_input_parameters(fom_dct, notebook_config, global_design_variables)

            # execute model
            fom_model = self.execute(notebook_dir, notebook_name, parameters_dct)

            # if the error key is present in an output dictionary, None is returned and loop is ended
            if fom_model is None:
                return None

            fom_dct = {**fom_dct, **fom_model}

        return fom_dct

    @staticmethod
    def merge_input_parameters(fom_dct: dict,
                               notebook_config: OptimizationNotebookConfig,
                               global_design_variables: dict) -> dict:
        """ Static method merging input parameters prior to an optimization routine execution.

        :param fom_dct: a dictionary with figures of merit calculated with scripts/notebooks
        :param notebook_config: a notebook config with input parameters dictionary
        :param global_design_variables: a dictionary with global design variables
        :return:
        """
        parameters_dct = {'full_output': False}
        for dest, source in notebook_config.input_parameters.items():
            if source in fom_dct.keys():
                parameters_dct[dest] = fom_dct[source]
            elif source in global_design_variables.keys():
                parameters_dct[dest] = global_design_variables[source]
        return parameters_dct

    @abstractmethod
    def execute(self, model_dir: str, model_name: str, parameters_dct: dict) -> Union[dict, None]:
        """Method executing a model and returning figures of merit.

        :param model_dir: model directory
        :param model_name: name of a model
        :param parameters_dct: a dictionary with model execution parameters and corresponding values

        :return: a dictionary with figures of merit if the computation was successful, otherwise an empty dictionary
        """
        raise NotImplementedError('This method is not implemented for this class')


class ScriptedNotebookExecutor(Executor):
    """ An implementation of ModelExecutor abstract class for scripts

    """

    def execute(self, model_dir: str, model_name: str, parameters_dct: dict) -> Union[dict, None]:
        """Method calculating figures of merit with scripts. Notebooks are converted to scripts.

        :param model_dir: model directory
        :param model_name: name of a model
        :param parameters_dct: a dictionary with model execution parameters and corresponding values

        :return: a dictionary with figures of merit if the computation was successful, otherwise a dictionary with -1
        error code is returned.
        """
        script = model_name.split('.')[0].lower() + '_script'
        cwd = os.getcwd()

        os.chdir(model_dir)
        run = getattr(__import__(script), 'run_' + script)
        print('Running %s script' % script)
        try:
            fom_model = run(**parameters_dct)
        except Exception as exception:
            print(exception)
            return None
        os.chdir(cwd)

        return fom_model


class NotebookExecutor(Executor):
    """ An implementation of ModelExecutor abstract class for notebooks

    """
    def execute(self, model_dir: str, model_name: str, parameters_dct: dict) -> Union[dict, None]:
        """Method calculating figures of merit with notebooks (papermill and scrapbook packages).

        :return: a dictionary with figures of merit if the computation was successful, otherwise a dictionary with -1
        error code is returned.
        """
        notebook_path = os.path.join(model_dir, model_name)
        notebook_name_split = model_name.split('.')
        out_notebook_name = '%s_out.%s' % tuple(notebook_name_split)

        out_notebook_path = os.path.join(model_dir, out_notebook_name)

        try:
            pm.execute_notebook(notebook_path, out_notebook_path, cwd=model_dir, parameters=parameters_dct)
        except PapermillExecutionError as e:
            # on error print the message
            print(e.exec_count)
            print(e.source)
            print(e.traceback[-1])
            return None
        except Exception as exception:
            raise Exception(exception)

        # fetch figure of merit
        return sb.read_notebook(out_notebook_path).scraps['model_results'].data


class ExecutorFactory:
    """ A factory class returning either a script or notebook executor

    """
    @staticmethod
    def build(is_script_executed: bool) -> "Executor":
        """

        :param is_script_executed: True if notebooks are executed as script, False otherwise
        :return: ScriptModelExecutor instance if True, otherwise NotebookModelExecutor
        """
        if is_script_executed:
            return ScriptedNotebookExecutor()
        else:
            return NotebookExecutor()
