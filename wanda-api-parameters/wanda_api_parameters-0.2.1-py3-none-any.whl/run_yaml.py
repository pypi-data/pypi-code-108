import os
from wanda_api_parameters.classobjects import WandaParameterScript
from wanda_api_parameters.parameters_api import (empty_directory)
import zipfile
import argparse
from distutils.util import strtobool
import sys

def parse_args():
    parser=argparse.ArgumentParser(description="Run wanda-api with a YAML-file.")
    # Base directory
    parser.add_argument(
        "--base-directory",
        type=str,
        default=None,
        help="(full) path to the base directory"
    )
    # YAML-file name
    parser.add_argument(
        "--option-file",
        type=str,
        help="(relative) path to the YAML option file"
    )
    # Model name
    parser.add_argument(
        "--model-file",
        type=str,
        help="(relative) path to the zip-file containing the model."
    )
    # Figure plot
    parser.add_argument(
        "--only-figures",
        type=strtobool,
        default=False,
        help="Boolean to only plot figures."
    )
    # Clear model folder
    parser.add_argument(
        "--clear-model-directory",
        type=strtobool,
        default=False,
        help="Clear the model directory."
    )
    # Number of workers for multiprocessing
    parser.add_argument(
        "--number-of-workers",
        type=int,
        default=1,
        help="Number of processes to run simultaneously."
    )
    args=parser.parse_args()
    return args


def clear_model_directory(file_path: str, file_name: str, only_figures: bool, model_name: str = "models"):
    """
    Clear the model directory of old-models.

    Parameters
    ----------
    file_path: str,
        The path to the base directory containing the scenario file and base-model
    file_name: str
        The file_name of the scenarios to clear. ]
    only_figures: bool
        A boolean that skips the deletion step if we're only processing the figures.
    model_name: str, default = Models
        Directory that contains the models.
    """
    # Remove processed model results if we're updating the models.
    if not only_figures:
        empty_directory(dir_path=os.path.join(file_path, model_name),
                        file_name=file_name)
        # Unzip wdi
        with zipfile.ZipFile(os.path.join(file_path, "{}.zip".format(file_name)), "r") as zip_ref:
            zip_ref.extractall(file_path)


def main(file_path: str,
         file_name: str,
         only_figures: bool = False,
         file_model: str = None,
         clear_folder: bool = False,
         nworkers: int = 1):
    """
    Main function to run the wanda model with a parameter script in YAML-file format.

    Parameters
    ----------
    file_path: str
        Complete path specification to the directory of the Wanda model and scenario file.
    file_name: str
        Name of the scenario file. If the file_model is not specified, the file_name should match the model name.
    only_figures: boolean, default = False
        Create figures with running the model (False) or without running the model (True)
    file_model:
        Name of the wanda model. Required if the scenario file does not match the model file.
    clear_folder: boolean, default = False
        Clear both the figures, and model folders completely.
    nworkers: int, default = 1
        Change the number of workers to perform mulitprocessing. Default the parameterscript performs the calculations
        in a serial fashion.

    Notes
    -----
    The current method is only implemented for a yaml-file format. A small adjustment is required to make this main
    script usefull for both XLS and YAML files.

    """
    if clear_folder:
        # Remove models
        clear_model_directory(
            file_path=file_path,
            file_name=file_name,
            only_figures=only_figures,
            model_name="models",
        )
        # Empty figure directory
        empty_directory(
            dir_path=os.path.join(file_path, "figures"),
        )
    # Define model file
    if file_model is None:
        file_model = os.path.join(file_path, "{}.wdi".format(file_name))
    else:
        file_model = os.path.join(file_path, "{}.wdi".format(file_model))
    # Create object.
    parameter_object = WandaParameterScript(
        wanda_model=file_model,
        yaml_file=os.path.join(file_path, "{}.yaml".format(file_name)),
        only_figures=only_figures
    )
    # Parse information
    parameter_object.parse_yaml_file()
    # Run scenarios
    parameter_object.run_scenarios(n_workers=nworkers)
    # ZIP results
    parameter_object.zip_models()

def run_yaml_file():
    # Parse the arguments.
    inputs = parse_args()
    # Replace input directory if necessary.
    if inputs.base_directory is None:
        inputs.base_directory = os.getcwd()
    # Open the main path.
    main(
        file_path=inputs.base_directory,
        file_name=inputs.option_file,
        file_model=inputs.model_file,
        only_figures=inputs.only_figures,
        nworkers=inputs.number_of_workers,
        clear_folder=inputs.clear_model_directory,
    )


if __name__ == '__main__':
    # Run main
    # Append additional arguments to sys.argv
    # sys.argv = sys.argv + [
    #     '--base-directory',
    #     r'c:\Users\meerkerk\OneDrive - Stichting Deltares\TemporaryProjects\11207243_Dunea_optimize\example_kelbij',
    #     '--option-file',
    #     'scenario_files_dunea_horizontal',
    #     '--model-file',
    #     'Basismodel_BAL1_en_2_v9_Vent_WindKetel_Horizontaal'
    # ]
    # Parse the arguments.
    inputs = parse_args()
    # Replace input directory if necessary.
    if inputs.base_directory is None:
        inputs.base_directory = os.getcwd()
    # Open the main path.
    main(
        file_path=inputs.base_directory,
        file_name=inputs.option_file,
        file_model=inputs.model_file,
        only_figures=inputs.only_figures,
        nworkers=inputs.number_of_workers,
        clear_folder=inputs.clear_model_directory,
    )
