#import yaml
import copy

from ccorp.ruamel.yaml.include import YAML
import os
import glob
import zipfile
import pywanda
from .general_properties import (ROOT_EXPORT, ROOT_MODELS, WBIN)


def yaml_reader(file_path):
    """A YamlReader object that generates dictionaries from the Yaml fileformat.

        Keyword arguments:
        doc -- the document of the type Docx class
        file_path -- the path to the directory to read.

        source: https://stackoverflow.com/a/55975390/15619397
    """
    # Setup yaml configuration.

    yaml = YAML(typ='safe',
                pure=True)
    yaml.allow_duplicate_keys = True

    with open(file_path, 'r') as file:
        # The FullLoader parameter handles the conversion from YAML
        # scalar values to Python the dictionary formatz
        data_dictionary = yaml.load(file)
    # Change scenarios from list to dict
    if data_dictionary.get('scenarios') is not None:
        if type(data_dictionary['scenarios']) is list:
            temp_dict = {}
            for sub_list in data_dictionary['scenarios']:
                for sub_key in sub_list.keys():
                    temp_dict[sub_key] = sub_list[sub_key]
            data_dictionary['scenarios'] = temp_dict

    # Concatenate changes
    if data_dictionary.get('scenarios') is not None:
        for key in data_dictionary['scenarios']:
            change_list = data_dictionary['scenarios'][key]['changes']
            idx_array = []
            for idx_change, change in enumerate(change_list):
                if data_dictionary['scenarios'][key]['changes'][idx_change].get('changes') is not None:
                    idx_array.append(idx_change)
            data_dictionary['scenarios'][key]['changes']
            # Append list
            change_list_temp = copy.deepcopy(change_list)
            for idx in idx_array:
                change_list_temp.extend(change_list[idx]['changes'])
            for idx in idx_array[::-1]:
                change_list_temp.pop(idx)
            # Write to dict
            data_dictionary['scenarios'][key]['changes'] = change_list_temp
    return data_dictionary


def unzip_model(fn_file: str, export_dir: str = ROOT_EXPORT):
    """
    Unzip models to guarantee working Wanda-models

    ..........
    Attributes
    ----------
        fn_file: str
            Path to the model to be unzipped.
        export_dir: str
            Path to export the data to.
    """
    try:
        with zipfile.ZipFile("{}.zip".format(os.path.splitext(fn_file)[0])) as zipF:
            for names in zipF.namelist():
                zipF.extract(names, export_dir)

    except Warning as e:
        print(e)
        print("File {} not found!".format(fn_file))

def empty_directory(dir_path: str, file_name: str = None):
    """
    Empty the directory in the specfied path. If the file_name is not specified all files will be removed. Otherwise,
    all files that contain the file_name in their name will be removed.

    Parameters
    ----------
    dir_path: str
        Path to the directory to clear
    file_name: str, default None
        Files to search for in the directory.

    Returns
    -------

    """
    # Obtain all files.
    files = glob.glob(os.path.join(dir_path, '*'))
    # Remove only files that contain the name.
    if file_name is not None:
        remove_list = []
        for idx_file, file in enumerate(files):
            path, fn = os.path.split(file)
            if file_name.lower() not in fn.lower():
                remove_list.extend([idx_file])
        for idx_file in remove_list[::-1]:
            files.pop(idx_file)

    # Remove files in the file list.
    for file in files:
        os.remove(file)

def open_model(fn: str,
               unzip: bool = True,
               time_step: float = 1E-2,
               model_dir: str=ROOT_MODELS,
               export_dir: str= ROOT_EXPORT) -> pywanda.WandaModel:
    """
    Open a wanda model by either unzipping or directly opening. The method also sets the timestep of the simulation!!!
    Therefore, it is required to set the time step in the parameter files.

    Parameters
    ----------
    fn: str
        Filename of the wanda model
    unzip: bool, default=True
        Unzip the model
    model_dir: str, default=ROOT_MODELS
        Path to the model directory
    export_dir: str, default=ROOT_EXPORT
        Path to the export directory

    Returns
    -------
    model: Wanda model class

    """
    # Unzip wanda model.
    if unzip:
        unzip_model(fn_file=os.path.join(model_dir, fn),
                    export_dir=export_dir,
                    )
    # Open wanda model
    model = pywanda.WandaModel(os.path.join(export_dir, fn), WBIN)
    # Set model mode
    model.switch_to_transient_mode()
    # Set time step
    model.get_property('Time step').set_scalar(time_step)
    # Save model input
    model.save_model_input()

    return model