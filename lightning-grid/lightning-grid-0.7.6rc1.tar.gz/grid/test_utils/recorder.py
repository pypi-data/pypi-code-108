"""Hook into the low level graphql Client transports and record HTTP request/responses

This allows us to generate a golden file unique to each test invocation against one
of the live dev environments. The query and response is recorded once, after which
future tests are able to just create a mock Client which reads the corresponding
golden files from disk and populates a mapping of request->response as it was
performed in a known good scenario.
"""

import logging
from pathlib import Path

GOLDEN_DIR = Path(__file__).parent.parent.parent / "tests" / "data" / "golden"


# noinspection PyMissingConstructor
class _FilterGQLSchemaQueries(logging.Filter):
    def __init__(self, param=None):
        self.param = param

    def filter(self, record):
        allow = self.param not in record.getMessage()
        record.msg = record.getMessage().replace("\\n", "").strip()
        record.args = ()
        return allow


class _FilterGQLMissingVariablesQuery(logging.Filter):
    def __init__(self, param=None):
        self.param = param

    def filter(self, record):
        msg = record.getMessage()
        if msg.startswith(">>>") and '", "variables": {' not in msg:
            record.msg = record.getMessage()[:-1] + ', "variables": {}}'
            record.args = ()
        return True


class _FilterRestHttpInfoRequest(logging.Filter):
    def __init__(self):  # skipcq: PYL-W0231
        pass

    def filter(self, record):
        msg = record.getMessage()
        if (msg.startswith(">>>") or msg.startswith("<<<")) and '_with_http_info' in msg:
            return False
        return True


_filter_request = _FilterGQLSchemaQueries('>>> {"query": "query IntrospectionQuery')
_filter_request_2 = _FilterGQLMissingVariablesQuery()
_filter_response = _FilterGQLSchemaQueries('<<< {"data":{"__schema":{"queryType"')
_filter_rest_http_request_response = _FilterRestHttpInfoRequest()


class QueryLogging:
    def __init__(self):
        logging.basicConfig(level='ERROR', format="%(name)s:%(message)s ")

        self._lg1 = logging.getLogger("gql.transport.requests")
        self._lg1.addFilter(_filter_response)
        self._lg1.addFilter(_filter_request_2)
        self._lg1.addFilter(_filter_request)

        self._lg2 = logging.getLogger("gql.transport.websockets")
        self._lg2.addFilter(_filter_response)
        self._lg2.addFilter(_filter_request_2)
        self._lg2.addFilter(_filter_request)

        self._lg3 = logging.getLogger("gql.transport.aiohttp")
        self._lg3.addFilter(_filter_response)
        self._lg3.addFilter(_filter_request_2)
        self._lg3.addFilter(_filter_request)

        self._lg4 = logging.getLogger("grid.sdk.rest.client")
        self._lg4.addFilter(_filter_rest_http_request_response)

        self._handler = None

    def __enter__(self):
        if self._handler is None:
            raise ValueError(f'output handler has not been set')
        self._lg1.addHandler(self._handler)
        self._lg2.addHandler(self._handler)
        self._lg3.addHandler(self._handler)
        self._lg4.addHandler(self._handler)
        self._activate()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._lg1.removeHandler(self._handler)
        self._lg2.removeHandler(self._handler)
        self._lg3.removeHandler(self._handler)
        self._lg4.removeHandler(self._handler)
        self._handler = None
        self._deactivate()

    def set_output_file_handler(self, filename: str) -> 'QueryLogging':
        self._handler = logging.FileHandler(filename, mode='w')
        return self

    def _activate(self):
        self._lg1.setLevel(logging.INFO)
        self._lg2.setLevel(logging.INFO)
        self._lg3.setLevel(logging.INFO)
        self._lg4.setLevel(logging.INFO)
        logging.basicConfig(level='INFO', format="%(name)s:%(message)s ")

    def _deactivate(self):
        self._lg1.setLevel(logging.ERROR)
        self._lg2.setLevel(logging.ERROR)
        self._lg3.setLevel(logging.ERROR)
        self._lg4.setLevel(logging.ERROR)
        logging.basicConfig(level='ERROR', format="%(name)s:%(message)s ")
