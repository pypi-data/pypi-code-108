"""
Overridden implementations of globus clients to mitigate globus-sdk 2.x issues
Remove when upgrading to globus-sdk 3.x
"""
from globus_sdk import TransferClient as BaseTransferClient
from requests.adapters import HTTPAdapter
from requests.adapters import Retry


class TransferClient(BaseTransferClient):
    """
    Transfer client which retries select HTTP errors
    """

    def __init__(self, authorizer=None, **kwargs):
        super().__init__(authorizer=authorizer, **kwargs)
        # override the requests session object to have retries
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 502, 503, 504, 530],
            method_whitelist=["HEAD", "GET", "OPTIONS", "PUT", "DELETE", "POST", "TRACE"],
        )
        http_adapter = HTTPAdapter(max_retries=retry_strategy)
        self._session.mount("https://", http_adapter)
        self._session.mount("http://", http_adapter)
