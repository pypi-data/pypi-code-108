import os
import shutil
import sys
import platform
import tempfile
import time
from pathlib import Path
from typing import Tuple
from zipfile import ZipFile
from termcolor import colored

import yaml

from biolib.biolib_api_client import AppVersionOnJob, Module, FilesMapping
from biolib.validators.validate_app_version import validate_app_version  # type: ignore
from biolib.validators.validate_argument import validate_argument  # type: ignore
from biolib.validators.validate_module import validate_module  # type: ignore
from biolib.biolib_errors import BioLibError
from biolib.biolib_logging import logger
from biolib.typing_utils import Dict, List


class BiolibValidationError(Exception):
    pass


def bl_colored(string, colour):
    # The colors does not seem to play nice with Windows PowerShell terminal
    if platform.system() == 'Windows':
        return string
    else:
        return colored(string, colour)


def validate_and_get_args(args):
    if args is None:
        args = []

    if isinstance(args, str):
        args = list(filter(lambda p: p != '', args.split(' ')))

    if not isinstance(args, list):
        raise Exception('The given input arguments must be list or str')

    return args


def get_files_dict_and_file_args(files, args):
    if files is None:
        files = []
        # TODO: Figure out how to make this slightly less error prone
        for idx, arg in enumerate(args):
            if not arg.startswith('/'):
                arg = f'{os.getcwd()}/{arg}'

            arg = Path(arg)
            if arg.is_file():
                files.append(arg)
                # Make sure that arg is only the filename
                args[idx] = arg.parts[-1]

    files_dict = {}
    for file_path in files:
        file = open(file_path, 'rb')
        path = '/' + file_path.parts[-1]

        files_dict[path] = file.read()
        file.close()

    return files_dict, args


def validate_and_get_app_path(provided_app_path):
    if provided_app_path.startswith('/'):
        app_path = Path(provided_app_path)
    else:
        app_path = Path(os.getcwd()) / provided_app_path

    if not app_path.exists():
        print(f'ERROR: Could not find path {app_path}')
        sys.exit(1)

    if not app_path.is_dir():
        print(f'ERROR: Path {app_path} is not a directory')
        sys.exit(1)

    return app_path


def get_yaml_data(app_path):
    try:
        yaml_file = open(f'{app_path}/.biolib/config.yml', 'r', encoding='utf-8')

    except Exception as error:  # pylint: disable=broad-except
        raise BioLibError(f'Could not open the biolib config file at {app_path}/.biolib/config.yml') from error

    try:
        yaml_data = yaml.safe_load(yaml_file)

    except Exception as error:  # pylint: disable=broad-except
        raise BioLibError(f'Could not parse {app_path}/.biolib/config.yml. Please make sure it is valid YAML') \
            from error

    return yaml_data


def validate_arguments(yaml_data):
    error_dict = {'arguments': {}}
    # Arguments are optional
    if 'arguments' in yaml_data:
        for argument in yaml_data['arguments']:
            argument_errors = validate_argument(argument)
            if argument_errors:
                error_dict['arguments'].update(argument_errors)

    # Just return empty dict if we have no errors
    if error_dict['arguments']:
        return error_dict
    else:
        return {}


def validate_and_get_biolib_yaml_version(yaml_data, error_dict):
    if not 'biolib_version' in yaml_data.keys():
        error_dict['config_yml']['biolib_version'] = ['Your config file is missing the biolib_version field.']
        print_errors(error_dict)
        sys.exit(1)
    else:
        biolib_version = yaml_data['biolib_version']

    if biolib_version not in (1, 2):
        error_dict['config_yml']['biolib_version'] = \
            [f'Biolib version can only be either 1 or 2 for now, your version is {biolib_version}.']
        print_errors(error_dict)
        sys.exit(1)

    return biolib_version


def validate_modules(yaml_data, biolib_yaml_version):
    error_dict = {'modules': {}}
    if 'modules' in yaml_data:
        for name, task_data in yaml_data['modules'].items():
            task_errors = validate_module(name, task_data, biolib_yaml_version)
            if task_errors:
                error_dict['modules'].update(task_errors)

    # Just return empty dict if we have no errors
    if error_dict['modules']:
        return error_dict
    else:
        return {}


def validate_yaml_config(yaml_data, source_files_zip_path):
    source_files_zip = ZipFile(source_files_zip_path)
    error_dict = {'config_yml': {}}

    biolib_yaml_version = validate_and_get_biolib_yaml_version(yaml_data, error_dict)
    error_dict['config_yml'].update(validate_app_version(yaml_data, biolib_yaml_version, source_files_zip))
    error_dict['config_yml'].update(validate_modules(yaml_data, biolib_yaml_version))
    error_dict['config_yml'].update(validate_arguments(yaml_data))

    if error_dict['config_yml']:
        print_errors(error_dict)
        raise BiolibValidationError('Could not validate .biolib/config.yml')


def print_errors(error_dict):
    print(bl_colored("\nThe following validation errors were found in the .biolib/config.yml file:", 'red'))
    print(yaml.safe_dump(error_dict, allow_unicode=True, default_flow_style=False))


def write_output_files(mapped_output_files=None):
    output_dir_path = 'biolib_results'

    if os.path.exists(output_dir_path):
        os.rename(output_dir_path, f'{output_dir_path}_old_{time.strftime("%Y%m%d%H%M%S")}')

    if mapped_output_files:
        logger.debug("Output Files:")

        for path, data in mapped_output_files.items():
            dirs, file = os.path.split(path)
            path_on_disk = f'{output_dir_path}{path}'

            if dirs:
                os.makedirs(f'{output_dir_path}{dirs}', exist_ok=True)
            if file:
                open(path_on_disk, 'wb').write(data)

            logger.debug(f"  - {path_on_disk}")

        logger.debug('\n')


def get_pretty_print_module_output_string(stdout=None, stderr=None, exitcode=None) -> str:
    stderr_string = f"\n{bl_colored('stderr:', 'red')}\n{stderr.decode()}" if stderr else ''
    return f'''{bl_colored('stdout:', 'green')}
{stdout.decode()}{stderr_string}
{bl_colored('exitcode:', 'green' if exitcode == 0 else 'red')} {exitcode}'''


def _get_files_mappings(file_commands: List[str]) -> List[FilesMapping]:
    files_mappings: List[FilesMapping] = []
    for file_command in file_commands:
        # TODO: figure out if splitting on space is good enough
        _, from_path, to_path = file_command.split(' ')
        files_mappings.append(FilesMapping(from_path=from_path, to_path=to_path))
    return files_mappings


def get_mocked_app_version_from_yaml(yaml_data: Dict, source_files_zip_path: str):
    modules: List[Module] = []
    for module_name in yaml_data['modules']:
        yaml_module = yaml_data['modules'][module_name]

        image_hostname, image_uri = yaml_module['image'].split('://')
        if image_hostname != 'local-docker':
            raise Exception(
                f'Found image {image_uri} with hostname {image_hostname}, please use "local-docker://"'
                f'Your application must use modules with local docker images to use run-dev'
            )

        modules.append(Module(
            command=yaml_module.get('command', ''),
            environment='biolib-ecr',
            image_uri=image_uri,
            input_files_mappings=_get_files_mappings(yaml_module['input_files']),
            large_file_systems=[],
            name=module_name,
            output_files_mappings=_get_files_mappings(yaml_module['output_files']),
            source_files_mappings=_get_files_mappings(yaml_module['source_files']),
            working_directory=yaml_module['working_directory'],
            estimated_image_size_bytes=None  # This should not be provided here
        ))

    return AppVersionOnJob(
        client_side_executable_zip=source_files_zip_path,
        consumes_stdin=True,
        is_runnable_by_user=True,
        modules=modules,
        public_id='app-version-mock-id',
        remote_hosts=[],
        settings=[],
        stdout_render_type='text',
        main_output_file=None
    )


def create_temporary_directory_with_source_files_zip(app_path: str) -> Tuple[tempfile.TemporaryDirectory, str]:
    original_working_directory = os.getcwd()
    temporary_directory = tempfile.TemporaryDirectory()
    os.chdir(app_path)
    try:
        zip_path_without_file_extension = os.path.join(temporary_directory.name, 'biolib-cli-tmp-source-files-zip')
        zip_path = f'{zip_path_without_file_extension}.zip'
        app_folder_name = Path(app_path).absolute().parts[-1]
        shutil.make_archive(
            base_name=zip_path_without_file_extension,
            format='zip',
            root_dir='..',
            base_dir=app_folder_name,
        )

        return temporary_directory, zip_path

    except Exception as error:
        temporary_directory.cleanup()
        raise Exception('Failed to create zip of application') from error

    finally:
        # change back to old working directory
        os.chdir(original_working_directory)
