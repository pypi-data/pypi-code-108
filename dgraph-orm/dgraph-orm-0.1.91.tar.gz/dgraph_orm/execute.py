import typing as T
import os
import time
import httpx
from httpx import Response
from . import GQLException


class TokenExpiredException(Exception):
    pass


class ThrottleException(Exception):
    pass


class IOTimeoutException(Exception):
    pass


TIMEOUT = float(os.getenv("GQL_CLIENT_TIMEOUT", "25"))
print(f"{TIMEOUT=}")

client_sync = httpx.Client(timeout=TIMEOUT)
client = httpx.AsyncClient(timeout=TIMEOUT)


def check_for_errors(j: dict) -> None:
    if errors := j.get("errors"):
        print(f"{errors=}")
        if "Token is expired" in str(errors):
            raise TokenExpiredException(errors)
        if "Too Many Requests" in str(errors):
            raise ThrottleException(errors)
        if "i/o timeout" in str(errors):
            raise IOTimeoutException(errors)
        raise GQLException(errors)


def finish(
    *, response: Response, query_str: str, should_print: bool, start_time: float
) -> dict:
    try:
        j = response.json()
    except Exception as e:
        message = f".json() did not work for {response=}"
        print(message, "-", f"{e=}")
        raise GQLException(message)
    try:
        print(
            f"took: {(time.time() - start_time) * 1000}, "
            f'took internal: {int(j["extensions"]["tracing"]["duration"]) / (10 ** 6)}'
        )
    except Exception as e:
        print(f"ERRORED with {e=} IN FINISH, {j=}")
    if should_print:
        print(f"{query_str=}, {j=}")
    check_for_errors(j)
    if "data" not in j:
        raise GQLException(f"data not in j!, {j=}, {query_str=}")
    return j


"""
DEP
async def gql(
    url: str,
    query_str: str,
    variables: dict = None,
    headers: dict = None,
    should_print: bool = False,
    use_one_time: bool = False,
) -> dict:
    start = time.time()
    headers = headers or {}
    json = {"query": query_str, "variables": variables or {}}
    if use_one_time:
        async with httpx.AsyncClient(timeout=TIMEOUT) as onetime_client:
            response = await onetime_client.post(url=url, json=json, headers=headers)
    else:
        response = await client.post(url=url, json=json, headers=headers)
    return finish(
        response=response,
        query_str=query_str,
        should_print=should_print,
        start_time=start,
    )
"""
