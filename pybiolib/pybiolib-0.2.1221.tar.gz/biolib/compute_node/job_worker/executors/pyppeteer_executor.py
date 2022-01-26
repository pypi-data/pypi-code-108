import http.server
import json
import socketserver
import threading
import os
import asyncio
import subprocess
import base64
import sys
import logging

from biolib.typing_utils import Optional
from biolib import utils
from biolib.biolib_api_client import BiolibApiClient
from biolib.biolib_errors import BioLibError
from biolib.biolib_logging import logger, TRACE
from biolib.compute_node.job_worker.executors.base_executor import BaseExecutor
from biolib.compute_node.job_worker.executors.types import LocalExecutorOptions
from biolib.pyppeteer.pyppeteer import launch, command  # type: ignore
from biolib.pyppeteer.pyppeteer.launcher import resolveExecutablePath, __chromium_revision__  # type: ignore

# specifically limit logs from pyppeteer
logging.getLogger('biolib.pyppeteer.pyppeteer').setLevel(logging.ERROR)
logging.getLogger('biolib.pyppeteer.pyppeteer.connection').setLevel(logging.ERROR)


class RequestHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):  # pylint: disable=redefined-builtin
        if logger.level == TRACE:
            http.server.SimpleHTTPRequestHandler.log_message(self, format, *args)


class PyppeteerExecutor(BaseExecutor):
    _chrome_executable_path: Optional[str] = None
    _no_sandbox: bool = True

    def execute_module(self, module_input_serialized: bytes) -> bytes:
        with socketserver.TCPServer(('127.0.0.1', 0), RequestHandler) as httpd:
            port = httpd.server_address[1]
            thread = threading.Thread(target=httpd.serve_forever)
            original_working_directory = os.getcwd()
            # TODO: figure out how we can avoid changing the current directory
            biolib_js_dir = os.path.join(utils.BIOLIB_PACKAGE_ROOT_DIR, 'biolib-js')
            os.chdir(biolib_js_dir)
            try:
                thread.start()
                module_output_serialized: bytes = asyncio.get_event_loop().run_until_complete(self._call_pyppeteer(
                    port,
                    self._options,
                    module_input_serialized,
                ))
                return module_output_serialized
            finally:
                os.chdir(original_working_directory)
                httpd.shutdown()
                thread.join()

    async def _call_pyppeteer(self, port: int, options: LocalExecutorOptions, module_input_serialized: bytes):
        if not self._chrome_executable_path:
            mac_chrome_path = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
            if os.path.isfile(mac_chrome_path):
                self._chrome_executable_path = mac_chrome_path

        if not self._chrome_executable_path:
            linux_chrome_path = '/usr/lib/chromium-browser/chromium-browser'

            # special install for google colab
            if not os.path.isfile(linux_chrome_path) and 'google.colab' in sys.modules:
                subprocess.run('apt-get update', shell=True, check=True)
                subprocess.run('apt install chromium-chromedriver', shell=True, check=True)

            if os.path.isfile(linux_chrome_path):
                self._chrome_executable_path = linux_chrome_path

        resolved_path = resolveExecutablePath(None, __chromium_revision__)
        if not self._chrome_executable_path and resolved_path[1]:
            # if executable_path is not set explicit,
            # and resolveExecutablePath failed (== we got an error message back in resolved_path[1])
            logger.info('Installing dependencies...')
            os.environ['PYPPETEER_NO_PROGRESS_BAR'] = 'true'
            command.install()

        logger.info('Computing...')

        chrome_arguments = [
            '--disable-web-security',
        ]
        if self._no_sandbox:
            chrome_arguments.append('--no-sandbox')

        browser = await launch(args=chrome_arguments, executablePath=self._chrome_executable_path)

        # start new page
        page = await browser.newPage()

        await page.goto('http://localhost:' + str(port))

        def get_data():
            return base64.b64encode(module_input_serialized).decode('ascii')

        def set_progress_compute(value):
            logger.debug(f'Compute progress: {value}')

        def set_progress_initialization(value):
            logger.debug(f'Initialization progress: {value}')

        def add_log_message(value):
            logger.debug(f'Log message: {value}')

        await page.exposeFunction('getData', get_data)
        await page.exposeFunction('setProgressCompute', set_progress_compute)
        await page.exposeFunction('setProgressInitialization', set_progress_initialization)
        await page.exposeFunction('addLogMessage', add_log_message)

        api_client = BiolibApiClient.get()
        refresh_token_js_value = 'undefined' if not api_client.refresh_token else f'"{api_client.refresh_token}"'

        job = options['job'].copy()
        if 'custom_compute_node_url' in job:
            job.pop('custom_compute_node_url')

        job_json_string = json.dumps(job)

        output_serialized_js_bytes = await page.evaluate('''
        async function() {
          const refreshToken = ''' + refresh_token_js_value + ''';
          const baseUrl = \'''' + options['biolib_base_url'] + '''\';
          const job = ''' + job_json_string + ''';

          const { BioLibSingleton, AppClient } = window.BioLib;
          BioLibSingleton.setConfig({ baseUrl, refreshToken });
          AppClient.setApiClient(BioLibSingleton.get());

          const inputBase64 = await window.getData();
          const inputByteArray = Uint8Array.from(atob(inputBase64), c => c.charCodeAt(0));

          const jobUtils = {
              setProgressCompute: window.setProgressCompute,
              setProgressInitialization: window.setProgressInitialization,
              addLogMessage: window.addLogMessage,
          };

          try {
            const moduleOutput = await AppClient.runJob(job, inputByteArray, jobUtils);
            return moduleOutput.serialize();
          } catch(err) {
            return err.toString();
          }
        }
        ''')
        logger.debug('Closing browser')
        await browser.close()

        module_output_serialized = self._js_to_python_byte_array_converter(output_serialized_js_bytes)

        # TODO: check if module_output is correctly serialized
        if isinstance(module_output_serialized, bytes):
            return module_output_serialized
        else:
            raise BioLibError(module_output_serialized)

    def cleanup(self):
        pass

    @staticmethod
    def _js_to_python_byte_array_converter(js_encoded) -> bytes:
        try:
            return bytes(list([js_encoded[str(i)] for i in range(len(js_encoded))]))
        except Exception as error:
            logger.error('Failed to decode response from browser')
            logger.error(error)
            logger.error(js_encoded)
            raise BioLibError(js_encoded) from error
