import os

from biolib.app.utils import run_job
from biolib.biolib_api_client import JobState, Job
from biolib.biolib_api_client.app_types import App, AppVersion
from biolib.biolib_api_client.biolib_job_api import BiolibJobApi
from biolib.app.app_result import AppResult
from biolib.biolib_api_client.biolib_app_api import BiolibAppApi
from biolib.biolib_binary_format import ModuleInput
from biolib.biolib_errors import BioLibError
from biolib.biolib_logging import logger


class BioLibApp:

    def __init__(self, uri: str):
        app_response = BiolibAppApi.get_by_uri(uri)
        self._app: App = app_response['app']
        self._app_uri = app_response['app_uri']
        self._app_version: AppVersion = app_response['app_version']

        logger.info(f'Loaded project {self._app_uri}')

    def __str__(self) -> str:
        return self._app_uri

    @property
    def uuid(self) -> str:
        return self._app['public_id']

    @property
    def version(self) -> AppVersion:
        return self._app_version

    def cli(self, args=None, stdin=None, files=None):
        module_input_serialized = self._get_serialized_module_input(args, stdin, files)

        job: Job = BiolibJobApi.create(self._app_version['public_id'])
        BiolibJobApi.update_state(job['public_id'], JobState.IN_PROGRESS.value)

        try:
            module_output = run_job(job, module_input_serialized)
            try:
                BiolibJobApi.update_state(job_id=job['public_id'], state=JobState.COMPLETED.value)
            except Exception as error:  # pylint: disable=broad-except
                logger.warning(f'Could not update job state to completed:\n{error}')

            return AppResult(
                exitcode=module_output['exit_code'],
                stderr=module_output['stderr'],
                stdout=module_output['stdout'],
                files=module_output['files'],
                main_output_file=job['app_version']['main_output_file']
            )

        except BioLibError as exception:
            logger.error(f'Compute failed with: {exception.message}')
            try:
                BiolibJobApi.update_state(job_id=job['public_id'], state=JobState.FAILED.value)
            except Exception as error:  # pylint: disable=broad-except
                logger.warning(f'Could not update job state to failed:\n{error}')

            raise exception

    def __call__(self, *args, **kwargs):
        if not args and not kwargs:
            self.cli()

        else:
            raise BioLibError('''
Calling an app directly with app() is currently being reworked.
To use the previous functionality, please call app.cli() instead. 
Example: "app.cli('--help')"
''')

    @staticmethod
    def _get_serialized_module_input(args=None, stdin=None, files=None) -> bytes:
        if args is None:
            args = []

        if stdin is None:
            stdin = b''

        if isinstance(args, str):
            args = list(filter(lambda p: p != '', args.split(' ')))

        if not isinstance(args, list):
            raise Exception('The given input arguments must be list or str')

        if isinstance(stdin, str):
            stdin = stdin.encode('utf-8')

        if files is None:
            files = []
            for idx, arg in enumerate(args):
                if os.path.isfile(arg):
                    files.append(arg)
                    args[idx] = arg.split('/')[-1]

        cwd = os.getcwd()
        files_dict = {}

        for file in files:
            path = file
            if not file.startswith('/'):
                # make path absolute
                path = cwd + '/' + file

            arg_split = path.split('/')
            file = open(path, 'rb')
            path = '/' + arg_split[-1]

            files_dict[path] = file.read()
            file.close()

        module_input_serialized: bytes = ModuleInput().serialize(stdin=stdin, arguments=args, files=files_dict)
        return module_input_serialized
