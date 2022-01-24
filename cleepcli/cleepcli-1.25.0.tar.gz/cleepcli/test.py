#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import time
from .console import EndlessConsole, Console, AdvancedConsole
import logging
from . import config
import importlib
import re
import datetime
import shutil

class Test():
    """
    Handle test processes
    """
    COVERAGE_PATH = '/opt/cleep/.coverage'

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.__endless_command_running = False
        self.__endless_command_return_code = 0
        self.__module_version = None
        self.__stderr = []
        if not os.path.exists(self.COVERAGE_PATH):
            os.makedirs(self.COVERAGE_PATH)

    def __coverage_to_dict(self, stdout):
        """
        Convert coverage results to dict

        Args:
            stdout (string): coverage results
        """
        out = {
            'files': [],
            'score': 0.0,
        }

        c = AdvancedConsole()
        results = c.find_in_string(stdout, r'((?:/.*?)+\.py)\s+(\d+)\s+\d+\s+(\d+)%|^(TOTAL)\s+\d+\s+\d+\s+(\d+)%$')
        for result in results:
            groups = list(filter(None, result[1]))
            if groups[0].startswith('TOTAL'):
                out['score'] = int(groups[1]) / 10
            else:
                out['files'].append({
                    'file': groups[0],
                    'statements': int(groups[1]),
                    'coverage': int(groups[2]),
                })

        return out

    def __reset_stds(self):
        self.__stderr.clear()

    def __quiet_console_callback(self, stdout, stderr):
        # self.logger.debug((stdout if stdout is not None else '') + (stderr if stderr is not None else ''))
        if stderr:
            self.__stderr.append(stderr)

    def __console_callback(self, stdout, stderr):
        self.logger.info((stdout if stdout is not None else '') + (stderr if stderr is not None else ''))
        if stderr:
            self.__stderr.append(stderr)

    def __console_end_callback(self, return_code, killed):
        self.__endless_command_running = False
        self.__endless_command_return_code = return_code

    def __get_module_version(self, module_name):
        if self.__module_version:
            return self.__module_version

        try:
            module_ = importlib.import_module('cleep.modules.%s' % (module_name))
            app_filename = getattr(module_, 'APP_FILENAME', module_name)
            del module_
            module_ = importlib.import_module('cleep.modules.%s.%s' % (module_name, app_filename))
            class_name = next((item for item in dir(module_) if item.lower() == app_filename.lower()), None)
            module_class_ = getattr(module_, class_name or '', None)
            self.__module_version = module_class_.MODULE_VERSION
            return self.__module_version
        except:
            self.logger.exception('Unable to get module version. Is module valid?')
            return None

    def __get_coverage_errors_and_failures(self, test_filepath):
        """
        Parse coverage output to find errors and failures count

        Args:
            test_filepath (string): test_filepath

        Returns:
            tuple: errors and failures count::

                (errors, failures)

        """
        exception = ''
        errors = 0
        failures = 0
        notest = False

        # coverage output is stored in stderr
        pattern = r'^FAILED \(((?:failures=(?P<failures>\d+))?|(?:, )?|(?:errors=(?P<errors>\d+))?)*\)$'
        matches = re.finditer(pattern, '\n'.join(self.__stderr), re.MULTILINE)
        for matchNum, match in enumerate(matches, start=1):
            indexes = match.groupdict()
            errors = indexes['errors'] if indexes['errors'] else 0
            failures = indexes['failures'] if indexes['failures'] else 0

        if not os.path.exists(test_filepath):
            notest = 'no test, '
            exception = ''
        else:
            notest = ''
            exception = 'run error, ' if errors == 0 and failures == 0 else ''

        return (errors, failures, exception, notest)

    def __get_coverage_file(self, module_name, module_version):
        """
        Return coverage file

        Args:
            module_name (string): module name
            module_version (string): module version

        Returns:
            string: coverage file
        """
        cov_file = os.path.join(self.COVERAGE_PATH, '%s.%s.cov' % (module_name, module_version))
        self.logger.debug('Coverage file = %s' % cov_file)
        return cov_file

    def __get_module_tests_path(self, module_name):
        """
        Return module tests path

        Args:
            module_name (string): module name

        Returns:
            string: module tests path
        """
        return '%s/%s/tests' % (config.MODULES_SRC, module_name)

    def __coverage_simple_command(self, path, coverage_command, coverage_options='', coverage_file=None, timeout=5.0):
        coverage_file = 'COVERAGE_FILE=%s ' % coverage_file if coverage_file else ''
        
        cmd = """
cd "%(path)s"
%(coverage_file)scoverage %(command)s %(options)s
        """ % {
            'coverage_file': coverage_file,
            'path': path,
            'command': coverage_command,
            'options': coverage_options,
        }
        c = Console()
        res = c.command(cmd, timeout=timeout)
        if res['error'] or res['killed']:
            self.logger.error('Error during command execution (killed: %s): %s' % (res['killed'], res['stderr']))
            return False

        return res

    def module_test(self, module_name, display_coverage=False, copy_to=None):
        """
        Execute module unit tests and display process output on stdout

        Args:
            module_name (string): module name
            display_coverage (bool): display coverage report (default False)

        Returns:
            bool: True if process succeed, False otherwise
        """
        # checking module path
        path = os.path.join(config.MODULES_SRC, module_name, 'tests')
        if not os.path.exists(path):
            self.logger.error('Specified module "%s" does not exist' % (module_name))
            return False

        # create module coverage path
        module_version = self.__get_module_version(module_name)
        if module_version is None:
            return False

        self.logger.info('Running unit tests...')
        coverage_file_path = self.__get_coverage_file(module_name, module_version)
        module_tests_path = self.__get_module_tests_path(module_name)
        cmd = """
cd "%s"
COVERAGE_FILE=%s coverage run --omit="*/lib/python*/*","test_*" --source="../backend" --concurrency=thread -m unittest discover
        """ % (module_tests_path, coverage_file_path)
        self.logger.debug('Test cmd: %s' % cmd)
        self.__endless_command_running = True
        self.__reset_stds()
        c = EndlessConsole(cmd, self.__console_callback, self.__console_end_callback)
        c.start()

        while self.__endless_command_running:
            time.sleep(0.25)

        # display coverage report
        if display_coverage:
            self.logger.debug('Display coverage')
            self.logger.info(self.module_test_coverage(module_name))

        # copy coverage file to standart location (in module tests directory) for coverage report tools
        if copy_to:
            shutil.copyfile(coverage_file_path, os.path.join(copy_to, '.coverage'))

        self.logger.debug('Return code: %s' % self.__endless_command_return_code)
        if self.__endless_command_return_code!=0:
            return False

        return True

    def module_test_coverage(self, module_name, missing=False, as_json=False):
        """
        Display module coverage

        Args:
            module_name (string): module name
            missing (bool): display missing statements (default False)
            as_json (bool): return results as json

        Returns:
            string or dict according to as_json option
        """
        # checking module path
        path = os.path.join(config.MODULES_SRC, module_name, 'tests')
        if not os.path.exists(path):
            raise Exception('Specified module "%s" does not exist' % (module_name))

        module_version = self.__get_module_version(module_name)
        if module_version is None:
            raise Exception('Module version not found')

        coverage_file = self.__get_coverage_file(module_name, module_version)
        if not os.path.exists(coverage_file):
            raise Exception('No coverage file found. Did tests run ?')

        res = self.__coverage_simple_command(
            self.__get_module_tests_path(module_name),
            'report',
            '-m -i' if missing else '-i',
            coverage_file,
        )
        if res == False:
            raise Exception('Error executing coverage report')

        stdout = '\n'.join(res['stdout'])
        if not as_json:
            return stdout
        return self.__coverage_to_dict(stdout)

    def __get_core_tests_path(self):
        """
        Return core tests path

        Returns:
            string: core tests path
        """
        return '%s/tests' % (config.CORE_SRC)

    def __list_core_files(self, core_path):
        """
        Return all python files on core with their associated tests

        Args:
            core_path (string): core path

        Returns:
            dict: list of files with test file path::

                {
                    python file (string): test file (string)
                }

        """
        files = []
        tests_path = self.__get_core_tests_path()

        self.logger.info('Searching core files...')
        for root, _, filenames in os.walk(core_path):
            for filename in filenames:
                filepath = os.path.join(root, filename)

                # drop useless files
                if not filename.endswith('.py'):
                    self.logger.debug('  Drop file "%s": not python file' % filepath)
                    continue
                if filename.startswith('__init__'):
                    self.logger.debug('  Drop file "%s": python init file' % filepath)
                    continue
                if filename.startswith('test_'):
                    self.logger.debug('  Drop file "%s": test file' % filepath)
                    continue
                if root.endswith('libs/tests'):
                    self.logger.debug('  Drop file "%s": test lib' % filepath)
                    continue

                # build paths
                core_relative_path = root.replace('%s' % core_path, '')
                core_relative_path = core_relative_path[1:] if core_relative_path.startswith('/') else core_relative_path
                test_filepath = os.path.join(tests_path, core_relative_path, 'test_%s' % filename)
                self.logger.debug('  Found "%s" [%s]' % (filepath, test_filepath))
                files.append((filepath, test_filepath))

        return files

    def core_test(self, display_coverage=False):
        """
        Execute core unit tests and display process output on stdout

        Args:
            display_coverage (bool): display coverage report (default False)

        Returns:
            bool: True if process succeed.
        """
        start = int(time.time())

        # clear previous results
        if self.__coverage_simple_command(self.__get_core_tests_path(), 'erase') == False:
            self.logger.error('Unable to clear previous tests results')
            return False

        # get files paths
        core_path = config.CORE_SRC
        files = self.__list_core_files(core_path)

        # execute tests
        self.logger.info('Running unit tests...')
        files_on_error = []
        files_on_success = []
        for filepath, test_filepath in files:
            self.logger.info('  Testing %s [%s]' % (filepath, test_filepath))
            cmd = """
cd "%(core_tests_path)s"
coverage run --omit="*/lib/python*/*","*test_*.py" --concurrency=thread --parallel-mode %(test_file)s
            """ % {
                'core_tests_path': self.__get_core_tests_path(),
                'test_file': test_filepath,
            }
            self.logger.trace('Test cmd: %s' % cmd)
            self.__endless_command_running = True
            self.__reset_stds()
            c = EndlessConsole(cmd, self.__quiet_console_callback, self.__console_end_callback)
            c.start()

            single_start = int(time.time())
            while self.__endless_command_running:
                time.sleep(0.25)

            single_duration = str(datetime.timedelta(seconds=(int(time.time()) - single_start)))
            self.logger.info('  Duration %s' % single_duration)

            if self.__endless_command_return_code!=0:
                self.logger.debug('Command output:\n%s' % '\n'.join(self.__stderr))
                errors, failures, exception, notest = self.__get_coverage_errors_and_failures(test_filepath)
                files_on_error.append({
                    'filepath': filepath,
                    'errors': errors,
                    'failures': failures,
                    'exception': exception,
                    'notest': notest,
                })
            else:
                files_on_success.append({
                    'filepath': filepath
                })

        # coverage
        if display_coverage:
            coverage = self.core_test_coverage()
            logging.info(coverage)

        # display tests report
        duration = str(datetime.timedelta(seconds=(int(time.time()) - start)))
        self.logger.info('-' * 50)
        self.logger.info('Tests report:')
        self.logger.info('  Duration: %s' % duration)
        self.logger.info('  %d files succeed' % len(files_on_success))
        self.logger.info('  %d files on error' % len(files_on_error))
        if len(files_on_error) != 0:
            for file_on_error in files_on_error:
                self.logger.info('    - %(filepath)s: %(notest)s%(exception)s%(errors)s errors, %(failures)s failures' % file_on_error)
        self.logger.info('-' * 50)

        return True if len(files_on_error) == 0 else False

    def core_test_coverage(self, as_json=False):
        """
        Get core test coverage last results

        Args:
            as_json (bool): return output as json

        Returns:
            string or dict according to as_json option
        """
        # combine results
        if self.__coverage_simple_command(self.__get_core_tests_path(), 'combine', timeout=120.0) == False:
            raise Exception('Error preparing coverage results')

        # combine results
        res = self.__coverage_simple_command(self.__get_core_tests_path(), 'report', '-i', timeout=120.0)
        if res == False:
            raise Exception('Error generating coverage results')

        stdout = '\n'.join(res['stdout'])
        if not as_json:
            return stdout
        return self.__coverage-to_dict(stdout)

