import os

from requests_auth_aws_sigv4 import AWSSigV4
from web3 import HTTPProvider
from web3.utils.request import _get_session


def make_post_request(endpoint_uri, data, *args, **kwargs):
    access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
    secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    region = os.getenv('AWS_REGION', 'ap-northeast-1')

    aws_auth = AWSSigV4(
        'managedblockchain',
        aws_access_key_id=access_key_id,
        aws_secret_access_key=secret_access_key,
        region=region
    )

    kwargs.setdefault('timeout', 10)
    session = _get_session(endpoint_uri)
    response = session.post(endpoint_uri, data=data, *args, **kwargs, auth=aws_auth)
    response.raise_for_status()

    return response.content


class AMBHTTPProvider(HTTPProvider):
    def make_request(self, method, params):
        self.logger.debug("Making request HTTP. URI: %s, Method: %s",
                          self.endpoint_uri, method)

        request_data = self.encode_rpc_request(method, params).decode()
        raw_response = make_post_request(
            self.endpoint_uri,
            request_data,
            **self.get_request_kwargs()
        )
        response = self.decode_rpc_response(raw_response)
        self.logger.debug("Getting response HTTP. URI: %s, "
                          "Method: %s, Response: %s",
                          self.endpoint_uri, method, response)
        return response
