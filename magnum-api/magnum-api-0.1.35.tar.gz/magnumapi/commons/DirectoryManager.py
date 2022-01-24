import os
import shutil
from distutils import dir_util
from pathlib import Path
from typing import List

from magnumapi.optimization.config.OptimizationNotebookConfig import OptimizationNotebookConfig


class DirectoryManager:
    """ A DirectoryManager class providing basic functionalities of checking file presence, creating directories, etc.

    """

    @staticmethod
    def check_if_file_exists(file_path: str) -> None:
        """Static method checking whether a file exists. If not, then a FileNotFoundError is raised.

        :param file_path: a path to a file whose presence is verified.
        """
        if not os.path.isfile(file_path):
            raise FileNotFoundError('The file %s does not exist!' % file_path)

    @staticmethod
    def create_directory_if_nonexistent(output_dir: Path) -> None:
        """ Static method checking whether a directory exists, if not then it is created

        :param output_dir: a path to an output directory
        """
        is_dir = Path(output_dir).is_dir()
        if not is_dir:
            os.mkdir(output_dir)

    @staticmethod
    def find_output_subdirectory_name(output_dir: str) -> int:
        """ Method finding an output subdirectory index by searching the maximum index present in an output directory
        and incrementing that index.

        :param output_dir: a path to a root output directory
        :return: a name of an output subdirectory corresponding to the incremented index
        """
        current_output_folder = 1
        int_folder_names = [int(name) for name in os.listdir(output_dir) if name.isnumeric()]
        if int_folder_names:
            current_output_folder = max(int_folder_names)

        return current_output_folder

    @classmethod
    def create_output_subdirectory(cls, output_dir: str, subdirectory_name: str) -> None:
        """ Static method creating an output subdirectory

        :param output_dir:
        :param subdirectory_name:
        """
        output_subdirectory_dir = Path(output_dir).joinpath(subdirectory_name)
        cls.create_directory_if_nonexistent(output_subdirectory_dir)

    @classmethod
    def copy_notebook_folders(cls,
                              input_folder: str,
                              notebook_configs: List[OptimizationNotebookConfig],
                              output_subdirectory_dir) -> None:
        """ Static method copying folders containing notebooks from the source directory to the output subdirectory

        :param input_folder: a root input folder
        :param notebook_configs: a list of notebook configs
        :param output_subdirectory_dir: a path to an output subdirectory
        """
        for notebook_config in notebook_configs:
            notebook_folder = notebook_config.notebook_folder
            input_notebook_folder_dir = Path(input_folder).joinpath(notebook_folder)
            output_notebook_subdirectory_dir = Path(output_subdirectory_dir).joinpath(notebook_folder)
            cls.create_directory_if_nonexistent(output_notebook_subdirectory_dir)
            cls.copy_directory_or_file_without_notebook_checkpoint(input_notebook_folder_dir,
                                                                   output_notebook_subdirectory_dir)

    @staticmethod
    def copy_directory_or_file_without_notebook_checkpoint(input_dir: Path, output_dir: Path) -> None:
        for dir_content in os.listdir(input_dir):
            if not dir_content.startswith('.'):
                if '.' in dir_content:
                    source = input_dir.joinpath(dir_content)
                    destination = output_dir.joinpath(dir_content)
                    shutil.copyfile(source, destination)
                else:
                    source = input_dir.joinpath(dir_content)
                    destination = output_dir.joinpath(dir_content)
                    dir_util.copy_tree(str(source), str(destination), preserve_symlinks=1)

    @classmethod
    def copy_folder_content(cls, input_folder_path: str, input_folder_name: str, output_subdirectory_dir: Path) -> None:
        """ Static method copying a model input from an input directory to an output subdirectory

        :param input_folder_path:
        :param input_folder_name:
        :param output_subdirectory_dir:
        """
        # ToDo: should be renamed to better denote the purpose
        ref_input_folder = Path(input_folder_path).joinpath(Path(input_folder_name))
        new_input_folder = Path(output_subdirectory_dir).joinpath(input_folder_name)

        cls.create_directory_if_nonexistent(new_input_folder)
        cls.copy_directory_or_file_without_notebook_checkpoint(ref_input_folder, new_input_folder)

    @classmethod
    def delete_directory_if_existent(cls, output_subdirectory_dir: Path) -> None:
        # todo: https://stackoverflow.com/questions/43765117/how-to-check-existence-of-a-folder-and-then-remove-it
        if os.path.exists(output_subdirectory_dir) and os.path.isdir(output_subdirectory_dir):
            print('deleting', output_subdirectory_dir)
            for root, dirs, files in os.walk(output_subdirectory_dir):
                for f in files:
                    os.unlink(os.path.join(root, f))
                for d in dirs:
                    shutil.rmtree(os.path.join(root, d))
