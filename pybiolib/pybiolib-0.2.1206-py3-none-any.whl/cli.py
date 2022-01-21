import argparse
import logging
import os
import sys
import platform

from docker.errors import ImageNotFound  # type: ignore

from biolib import cli_utils, utils, biolib_errors, templates
from biolib.app import BioLibApp
from biolib.app.utils import run_job
from biolib.biolib_push import push_application
from biolib.biolib_api_client import Job
from biolib.biolib_binary_format import ModuleInput
from biolib.cli_utils import BiolibValidationError
from biolib.validators.validate_zip_file import validate_zip_file  # type: ignore
from biolib.biolib_docker_client import BiolibDockerClient
from biolib.biolib_logging import logger
from biolib.lfs import create_large_file_system, push_large_file_system, describe_large_file_system


class IllegalArgumentError(ValueError):
    pass


def file_path(path):
    if path.startswith('/'):
        full_path = path
    else:
        full_path = os.path.normpath(os.path.join(os.getcwd(), path))
    if not os.path.exists(full_path):
        raise IllegalArgumentError(f'The path {full_path} does not exist')
    return full_path


def port_number(port):
    if not port.isdigit():
        raise IllegalArgumentError(f'Port number {port} is not a number. Ports can only be numbers')

    if not (0 < int(port) < 65000):  # pylint: disable=superfluous-parens
        raise IllegalArgumentError('Port can only be between 0 and 65000')

    return port


def main():
    # set more restrictive default log level for CLI
    logger.configure(default_log_level=logging.WARNING)

    logger.debug(f'pybiolib version {utils.BIOLIB_PACKAGE_VERSION}')

    def _get_stdin():
        stdin = None
        if not sys.stdin.isatty() and not utils.IS_DEV:
            stdin = sys.stdin.read()
        return stdin

    if len(sys.argv) > 2 and sys.argv[1] == 'run':
        try:
            app = BioLibApp(uri=sys.argv[2])
        except biolib_errors.BioLibError as error:
            print(f'An error occurred:\n {error.message}', file=sys.stderr)
            sys.exit(1)

        app_args = sys.argv[3:]
        result = app.cli(args=app_args, stdin=_get_stdin(), files=None)
        result.save_files('biolib_results')

        # Write stdout and stderr if it has not been streamed (Markdown is not streamed)
        if app.version.get('stdout_render_type') == 'markdown':
            sys.stdout.buffer.write(result.stdout)
            sys.stderr.buffer.write(result.stderr)

        sys.exit(result.exitcode)

    elif len(sys.argv) > 2 and sys.argv[1] == 'run-dev':
        provided_app_path = sys.argv[2]
        app_path = cli_utils.validate_and_get_app_path(provided_app_path)
        logger.info(f'Running BioLib application in local directory {app_path}...')
        tmp_directory, source_files_zip_path = cli_utils.create_temporary_directory_with_source_files_zip(app_path)

        try:
            validate_zip_file(source_files_zip_path, app_path)
            yaml_data = cli_utils.get_yaml_data(app_path)
            cli_utils.validate_yaml_config(yaml_data, source_files_zip_path)
            app_version_mocked = cli_utils.get_mocked_app_version_from_yaml(yaml_data, source_files_zip_path)

            for module in app_version_mocked['modules']:
                try:
                    BiolibDockerClient.get_docker_client().images.get(module['image_uri'])
                except ImageNotFound:
                    raise Exception(
                        f"Could not find local docker image {module['image_uri']} specified in .biolib/config.yml"
                    ) from None

            app_args = sys.argv[3:]
            args = cli_utils.validate_and_get_args(app_args)
            files_dict, args = cli_utils.get_files_dict_and_file_args(files=None, args=args)

            module_input_serialized = ModuleInput().serialize(
                stdin=_get_stdin() or b'',
                files=files_dict,
                arguments=args,
            )

            module_output = run_job(
                module_input_serialized=module_input_serialized,
                job=Job(
                    app_version=app_version_mocked,
                    caller_job=None,
                    created_at='',
                    public_id=utils.RUN_DEV_JOB_ID,
                    remote_hosts_with_warning=[],
                    user_id=None,
                    federated_job_uuid=None,
                ),
            )

            cli_utils.write_output_files(module_output['files'])

            print(cli_utils.get_pretty_print_module_output_string(
                exitcode=module_output['exit_code'],
                stderr=module_output['stderr'],
                stdout=module_output['stdout'],
            ))

        except Exception as exception:
            # Exit on BiolibValidationError as we have already printed the validation errors
            if isinstance(exception, BiolibValidationError):
                logger.error('Validation check failed for config file at .biolib/config.yml')
                sys.exit(1)
            raise exception

        finally:
            try:
                tmp_directory.cleanup()
            except IOError:
                logger.error('Failed to clean up temporary source files zip directory')

    else:
        parser = argparse.ArgumentParser()
        parser.add_argument('--version', action='version', version=utils.BIOLIB_PACKAGE_VERSION)

        subparsers = parser.add_subparsers(help='command', dest='command')

        # Add subparser for run to help message makes sense
        # The actual code for running applications is above this
        _parser_run = subparsers.add_parser('run', help='Run an application on BioLib')

        # Add subparser for run to help message makes sense
        # The actual code for running local applications is above this
        _parser_run_dev = subparsers.add_parser('run-dev', help='Run an application from a local directory')

        # add subparser for push
        parser_push = subparsers.add_parser('push', help='Push an application to BioLib')
        parser_push.add_argument('app_uri')
        parser_push.add_argument('--path', default='.', required=False)
        parser_push.add_argument('--copy-images-from-version', required=False)

        # add subparser for init
        parser_push = subparsers.add_parser('init', help='Initialize a code project with a .biolib/config.yml file.')

        # add subparser for run-compute-node
        parser_start = subparsers.add_parser('start', help='Start a compute node')
        parser_start.add_argument('--port', default='5000', required=False, type=port_number)
        parser_start.add_argument('--host', default='127.0.0.1', required=False)

        # add subparser for lfs
        parser_lfs = subparsers.add_parser('lfs', help='Work with large file systems')
        subparsers_lfs = parser_lfs.add_subparsers(help='lfs command', dest='lfs_command')

        parser_lfs_create = subparsers_lfs.add_parser('create', help='Create a large filesystem')
        parser_lfs_create.add_argument('lfs_uri', type=str)

        parser_lfs_push = subparsers_lfs.add_parser('push', help='Push data to a large filesystem')
        parser_lfs_push.add_argument('lfs_uri', type=str)
        parser_lfs_push.add_argument('--path', type=str)

        parser_lfs_push = subparsers_lfs.add_parser('describe', help='Describe a large filesystem')
        parser_lfs_push.add_argument('lfs_uri', type=str)
        parser_lfs_push.add_argument('--json', action='store_true')

        args = parser.parse_args()

        if args.command == 'push':
            logger.configure(default_log_level=logging.INFO)
            push_application(args.app_uri, args.path, app_version_to_copy_images_from=args.copy_images_from_version)

        elif args.command == 'start':
            logger.configure(default_log_level=logging.INFO)
            if platform.system() == 'Windows':
                raise Exception('Starting a compute node is currently not supported on Windows')

            from biolib.compute_node.webserver import webserver  # pylint: disable=import-outside-toplevel
            webserver.start_webserver(host=args.host, port=args.port)

        elif args.command == 'init':
            cwd = os.getcwd()
            config_file_path = f'{cwd}/.biolib/config.yml'
            readme_path = f'{cwd}/README.md'

            if os.path.exists(config_file_path):
                print(f'The file "{config_file_path}" already exists', file=sys.stderr)
                sys.exit(1)
            else:
                os.makedirs(f'{cwd}/.biolib', exist_ok=True)
                with open(config_file_path, 'w') as config_file:
                    config_file.write(templates.example_app.CONFIG_YML)

            if not os.path.exists(readme_path):
                with open(readme_path, 'w') as readme_file:
                    project_name = input('Enter a name for your project: ')
                    readme_file.write(f'# {project_name}\n')

        elif args.command == 'lfs':
            if args.lfs_command == 'create':
                logger.configure(default_log_level=logging.INFO)
                create_large_file_system(lfs_uri=args.lfs_uri)
            elif args.lfs_command == 'push':
                logger.configure(default_log_level=logging.INFO)
                push_large_file_system(lfs_uri=args.lfs_uri, input_dir=args.path)
            elif args.lfs_command == 'describe':
                describe_large_file_system(lfs_uri=args.lfs_uri, output_as_json=args.json)

        else:
            print('Unrecognized command, please run biolib --help to see available options.')
            sys.exit(1)


# allow this script to be called without poetry in dev e.g. by an IDE debugger
if utils.IS_DEV and __name__ == '__main__':
    main()
