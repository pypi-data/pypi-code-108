import os
from pathlib import Path
import shutil
import stat
from typing import Union, List, Dict

import jinja2
import yaml


class Writer:
    """Static methods for generating files"""

    TEMPLATE_DIR: Path = Path(__file__).parent.parent / "resources/templates"

    @staticmethod
    def _write_to_file(filepath: Path, content: str) -> None:
        """Generate a file from output string."""
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, "w") as new_file:
                new_file.write(content)
        except IOError:
            raise IOError(f"Could not create file {filepath}")

    @staticmethod
    def generate_yaml(output_file: Path, data: Union[List, Dict]) -> None:
        """Generate YAML file from a List or Dict

        :param output_file: path to the output file
        :param data: List or a Dict with data for the YAML file
        """

        Writer._write_to_file(output_file, yaml.dump(data, explicit_start=True,
                                                     explicit_end=True))

    @staticmethod
    def generate_file_from_template(output_file: Path, template_name: str,
                                    data=None, ruby_variables=None) -> None:
        """Generate file from Jinja2 template

        :param output_file: path to the output file
        :param template_name: name of a Jinja2 template file in templates dir
        :param data: arbitrary number of named args for the template
        :param ruby_variables: additional variables to pass to the template
        """

        try:
            template_loader = jinja2.FileSystemLoader(searchpath=
                                                      str(Writer.TEMPLATE_DIR))
            template_env = jinja2.Environment(loader=template_loader,
                                              trim_blocks=True,
                                              lstrip_blocks=True)
            template = template_env.get_template(template_name)
        except jinja2.TemplateNotFound:
            raise RuntimeError(f"Could not find template {template_name}")

        output = template.render(data=data, ruby_variables=ruby_variables)
        Writer._write_to_file(output_file, output)

    @staticmethod
    def _on_rmtree_error(func, path, exc_info):
        """On error during rmtree, try to make the file writable"""
        os.chmod(path, stat.S_IWRITE)
        os.unlink(path)

    @staticmethod
    def clone_git_repository(repository: str, location: Path, cloned_dir: str) -> None:
        """Clone a git repository to the provided location and removes .git

        :param repository: repository location
        :param location: target directory
        :param cloned_dir: name of the cloned directory
        """

        try:
            os.makedirs(location, exist_ok=True)
            os.chdir(location)
            os.system(f"git clone -q {repository}")
        except RuntimeError:
            raise RuntimeError(f"Could not clone repository: {repository}")

        try:
            shutil.rmtree(location.joinpath(cloned_dir).joinpath(".git"),
                          onerror=Writer._on_rmtree_error)
        except OSError:
            pass

    @staticmethod
    def copy_file(source: Path, destination: Path):
        """Copies a file from the source path to the destination

        :param source: path to the source file
        :param destination: path to the destination file
        """

        try:
            os.makedirs(destination.parent, exist_ok=True)
            shutil.copyfile(source, destination)
        except OSError:
            raise RuntimeError(f"Could not copy file {source}")

    @staticmethod
    def copy_directory(source: Path, destination: Path):
        """Copy directory recursively form the source dir to the destination.

        :param source: path to source directory
        :param destination: path to the destination directory
        """

        try:
            os.makedirs(destination.parent, exist_ok=True)
            shutil.copytree(source, destination)
        except OSError:
            raise RuntimeError(f"Could not copy directory {source}")

    @staticmethod
    def remove_directory(directory: Path):
        """Remove the directory recursively

        :param directory: path to directory to remove
        """

        try:
            shutil.rmtree(directory)
        except OSError:
            raise RuntimeError(f"Could not remove directory {directory}")

    @staticmethod
    def remove_file(file: Path):
        """Remove a file

        :param file: path to a file to remove
        """

        try:
            os.remove(file)
        except OSError:
            raise RuntimeError(f"Could not remove file {file}")
