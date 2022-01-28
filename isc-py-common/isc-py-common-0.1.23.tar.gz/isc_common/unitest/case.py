import urllib
from django import test

from isc_common.http.RPCResponse import RPCResponseConstant


class TestCase(test.TestCase):
    def assertSuccessResponse(self, response):
        if response.container_data['response']['status'] == RPCResponseConstant.statusFailure:
            message = response.container_data['response']['data']['error']['message']

            stackTrace = response.container_data['response']['data']['error']['stackTrace']
            stackTrace = stackTrace.replace(', \'  ','')
            stackTrace = stackTrace.encode().decode('unicode-escape')

            raise self.failureException(f"\nmessage: {message}\nstackTrace:{stackTrace}")

    def assertFailureResponse(self, response, message=None, stackTrace=None):
        if response.container_data['response']['status'] == RPCResponseConstant.statusFailure:
            _message = response.container_data['response']['data']['error']['message']

            if message and message != _message:
                raise self.failureException(f"message: {message} != {_message}")

            _stackTrace = response.container_data['response']['data']['error']['stackTrace']
            if stackTrace and stackTrace != _stackTrace:
                raise self.failureException(f"stackTrace: {stackTrace} != {_stackTrace}")

        else:
            raise self.failureException(f"response not failure status.")
