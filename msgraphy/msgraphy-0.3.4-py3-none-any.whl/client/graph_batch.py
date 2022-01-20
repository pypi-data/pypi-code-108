import logging
import uuid
from typing import TypeVar
from urllib.parse import urlparse, parse_qs, urlencode, ParseResult, urlunparse

from msgraphy.client.graph_client import GraphClient, GraphResponse

logger = logging.getLogger(__name__)

T = TypeVar('T')


class StateError(Exception):
    def __init__(self, *args):
        super(StateError, self).__init__(*args)


class BatchRequestsGraphResponse(GraphResponse[T]):

    def __init__(self, client, id, response_type):
        self.client = client
        self.id = id
        self.response_type = response_type
        self.response = None

    def __ensure_response(self):
        if not self.response:
            self.client.flush()

    @property
    def ready(self) -> bool:
        return self.response is not None

    @property
    def ok(self) -> bool:
        self.__ensure_response()
        if "status" in self.response:
            return self.response['status'] < 400
        else:
            return self.response.ok

    @property
    def value(self) -> T:
        self.__ensure_response()
        data = self.response['body']
        if not self.ok:
            raise ValueError(f"Cannot call 'value' on failed call: {data}")
        return self.response_type(data)

    @property
    def text(self) -> str:
        self.__ensure_response()
        return self.response['body']

    @property
    def headers(self) -> dict:
        self.__ensure_response()
        return self.response.get("headers")


class BatchGraphClient(GraphClient):

    def __init__(self, client: GraphClient):
        self.__client = client
        self.__requests = []
        self.__responses = {}

    @property
    def single_client(self):
        return self.__client

    def make_request(self, url, method="get", headers=None, response_type: T = dict, json=None, body=None,
                     params=None, **kwargs) -> GraphResponse[T]:
        id = str(uuid.uuid4())

        request_args = {}

        if not headers:
            headers = {}

        if json:
            headers['Content-Type'] = 'application/json'
            request_args['body'] = json

        if body:
            request_args['body'] = body

        if params:
            pr = urlparse(url)
            query = parse_qs(pr.query)
            query = {**query, **params}
            query = urlencode(query, doseq=True)
            new_url = ParseResult(scheme=pr.scheme, netloc=pr.netloc, path=pr.path, params=pr.params,
                                  query=query, fragment=pr.fragment)
            url = urlunparse(new_url)

        method = method.upper()
        values = dict(id=id, method=method, url=url, headers=headers, **request_args)

        response = BatchRequestsGraphResponse(self, id, response_type=response_type)

        self.__requests.append(values)
        self.__responses[id] = response
        self.flush(threshold=20)

        return response

    def flush(self, threshold=0, batch_size=20):
        """
        Flush all requests until there remain less than threshold.
        With a threshold of 0 all requests are flushed
        """
        while len(self.__requests) >= threshold:
            batch = self.__requests[0:batch_size]
            if not batch:
                return

            self.__requests = self.__requests[batch_size:]
            response = self.__client.make_request("$batch", method="post", json=dict(requests=batch))
            for r in response.value["responses"]:
                self.__responses.pop(r['id']).response = r
                if r['status'] > 299:
                    logger.error(f"Batched request failed: {r}")
