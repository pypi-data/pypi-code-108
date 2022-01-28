import os
from typing import Tuple, List
import logging
from tableschema import Schema
from tableschema.exceptions import LoadError

from tsfaker.exceptions import DifferentNumberInputOutput, TsfakerException


def process_input_output_arguments(input_descriptors: Tuple[str], output_files: Tuple[str]) -> Tuple[List, List]:
    """ Manage specific cases in input and output arguments

    :param input_descriptors:
    :param output_files:
    :return: (input_descriptors, output_files) after preprocessing
    """
    input_descriptors = list(input_descriptors)
    if is_single_directory(input_descriptors):
        input_directory = input_descriptors[0]
        input_descriptors = get_descriptors_files_path_in_directory(input_directory)

        if output_files == ('-',):
            output_files = [replace_json_to_csv_ext(input_file_path) for input_file_path in input_descriptors]

        if is_single_directory(output_files):
            output_directory = output_files[0]
            output_files = list()
            for input_file_path in input_descriptors:
                relative_path = os.path.relpath(input_file_path, start=input_directory)
                output_file_path = os.path.join(output_directory, replace_json_to_csv_ext(relative_path))
                output_files.append(output_file_path)

    if output_files == ('-',):
        output_files = ['-'] * len(input_descriptors)

    if len(input_descriptors) != len(output_files):
        message = 'The number of schema descriptors ({}) and output files paths ({}) should be identical. ' \
                  'If the target is a directory, it should already exists.' \
            .format(len(input_descriptors), len(output_files))
        raise DifferentNumberInputOutput(message)

    if not input_descriptors:
        logging.info("No input descriptor found. Run 'tsfaker --help' to get tsfaker command line usage.")

    return input_descriptors, output_files


def get_descriptors_files_path_in_directory(folder_path: str) -> List[str]:
    """ Walk through folder to list schema descriptors files' path

    :param folder_path:
    :return: schema descriptors files' path
    """
    descriptor_files_paths = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            if is_schema_file(file_path):
                descriptor_files_paths.append(file_path)

    return descriptor_files_paths


def is_schema_file(file_path):
    if not file_path.endswith('.json'):
        return False
    try:
        Schema(file_path)
    except LoadError:
        return False

    return True


def replace_json_to_csv_ext(file_path: str) -> str:
    if file_path.endswith('.json'):
        return file_path[:-5] + '.csv'
    else:
        raise TsfakerException("Input file path '{}' should end with extension '.json'".format(file_path))


def is_single_directory(files_or_dirs: List[str]) -> bool:
    return len(files_or_dirs) == 1 and isinstance(files_or_dirs[0], str) and os.path.isdir(files_or_dirs[0])
