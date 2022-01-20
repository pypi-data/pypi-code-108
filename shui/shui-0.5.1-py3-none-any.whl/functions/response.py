"""Request with built-in retry"""
from requests import Session
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def get_with_retry(
    url, retries=3, backoff_factor=0.3, status_forcelist=(500, 502, 504)
):
    """Sends a GET request with retry options"""
    session = Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session.get(url)
