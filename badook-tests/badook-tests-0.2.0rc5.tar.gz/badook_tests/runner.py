import unittest
import click
import sys
from collections import namedtuple


class BadookTestRunnerError(Exception):
    """Raised when there's a problem running a badook test"""

    def __init__(self, message):
        self.msg = message
        super().__init__(self.msg)


class BadookBaseTestResult(unittest.TextTestResult):
    """A base class to communicate the result of a test (a single test case) with the badook lab runtime"""

    result = namedtuple('results', ['passed', 'failed'])
    result.passed = []
    result.failed = []

    def startTest(self, test):

        # if there are no issues with the user's script (e.g. syntax error etc)
        if not isinstance(test, unittest.loader._FailedTest):
            # TODO: move this action to pyspark-runner when the test is finished. And send here just status success or not
            data = {'orgId': test.channel_id, 'projectId': test.context.project_name,
                    'runId': test.run_id, 'functionName': str(test._testMethodName), 'status': 'Running'}

            response = ManagementClient.register_start_test(test, data)

            # if error when requesting to start a test in service manager, abort the test
            if response['error']:
                msg = response['error']['message']
                raise BadookTestRunnerError(msg)

            super().startTest(test)
        else:
            test.__getattr__(test._testMethodName)()

    def addError(self, test, err):
        name = str(test._testMethodName) if hasattr(
            test, '_testMethodName') else ""

        data = {'orgId': test.channel_id if hasattr(test, 'channel_id') else "",
                'projectId': test.context.project_name if hasattr(test, 'context') else "",
                'runId': test.run_id if hasattr(test, 'run_id') else "",
                'functionName': str(test._testMethodName) if hasattr(test, '_testMethodName') else "",
                'status': 'Failure', 'failureMessage': str(err)}

        self.result.failed.append(name)

        # in case the run was aborted before a test was created
        response = {'error': True}
        try:
            # if test exists, update it's status in service management
            if test.context:
                response = test.context.api_client.send_json_post_request(
                    data, "runhistory/test")

                # if error when requesting to update a test in service manager - abort
                if response['error']:
                    msg = response['error']['message']
                    raise BadookTestRunnerError(msg)

        except Exception as e:
            BadookTestRunnerError(e)

        # If test exists:
        # this will display a failed test error message for the user.
        # passing err elements (list) except the traceback: err = (type, value, traceback)
        errNoTraceback = (err[0], err[1], None)
        super().addError(test, errNoTraceback)

    def addSuccess(self, test):
        name = str(test._testMethodName)
        response = ManagementClient.update_success(test, name)

        # if error when requesting to update a test in service manager - abort
        if response['error']:
            msg = response['error']['message']
            raise BadookTestRunnerError(msg)
        self.result.passed.append(name)
        super().addSuccess(test)


class ManagementClient(object):
    '''
    This is a utility class for accessing the management API.
    Its main use is to be mocked in tests. You can patch the ManagementClient methods as follows:

    @patch('badook_tests.runner.ManagementClient.[function name]', return_value=[returned value])
    '''

    @classmethod
    def register_start_test(cls, test, data):
        return test.context.api_client.send_json_post_request(data, "runhistory/test")

    @classmethod
    def update_success(self, test, name):
        data = {'orgId': test.channel_id, 'projectId': test.context.project_name,
                'runId': test.run_id, 'functionName': name, 'status': 'Success'}

        response = test.context.api_client.send_json_post_request(
            data, "runhistory/test")

        return response


class BadookRuntimeTestResult(BadookBaseTestResult):
    """A result class to communicate the result of a test (a single test case) with the badook lab runtime"""

    def startTest(self, test):

        try:
            super().startTest(test)
        except BadookTestRunnerError as berr:
            click.secho(
                f'\nUh Oh! Something bad happened while trying to run the test. Please contact Badook support.\n(Management Services - {berr.msg})', fg='red', bold=True)
            sys.exit(0)
        except Exception as err:
            click.secho(f'\n{err}', fg='red', bold=True)
            sys.exit(0)
