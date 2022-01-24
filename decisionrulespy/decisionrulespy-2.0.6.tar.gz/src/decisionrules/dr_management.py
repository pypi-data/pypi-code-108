import requests

from .custom_domain import *
from .exceptions import *

_management_api: str
_custom_domain: CustomDomain

_header: dict


def init(management_api_key, custom_domain: CustomDomain = None):
    global _management_api
    _management_api = management_api_key
    global _custom_domain
    _custom_domain = custom_domain
    global _header
    _header = header_factory(_management_api)


def header_factory(api_key):
    return {"Authorization": f"Bearer {api_key}"}


def url_factory():
    if _custom_domain is not None:
        return f"{_custom_domain.custom_domain_protocol.value}://{_custom_domain.custom_domain_url}/api"
    else:
        return "https://api.decisionrules.io/api"


async def get_call(get_url):
    response = None

    try:
        response = requests.get(get_url, headers=_header)
        return response.json()
    except NoUserException:
        print(f"No valid user! STATUS: {response.status_code}")
        print(response.json())
    except TooManyApiCallsException:
        print(f"Too many api calls! STATUS: {response.status_code}")
        print(response.json())
    except NotPublishedException:
        print(f"Rule ain´t published yet! STATUS: {response.status_code}")
        print(response)
    except InternalServerError:
        print(f"Internal server error. STATUS: {response.status_code}")
        print(response)
    except GeneralException:
        print(f"General exception, something went wrong. STATUS: {response.status_code}")
        print(response)


async def get_rule_by_id(rule_id):
    url = f"{url_factory()}/rule/{rule_id}"

    return await get_call(url)


async def get_rule_by_id_and_version(rule_id, version):
    url = f"{url_factory()}/rule/{rule_id}/{version}"

    return await get_call(url)


async def get_space(space_id):
    url = f"{url_factory()}/space/{space_id}"

    return await get_call(url)


async def post_rule(space_id, data):
    url = f"{url_factory()}/rule/{space_id}"

    response = None

    try:
        response = requests.post(url, json=data, headers=_header)
        return response.json()
    except NoUserException:
        print(f"No valid user! STATUS: {response.status_code}")
        print(response.json())
    except TooManyApiCallsException:
        print(f"Too many api calls! STATUS: {response.status_code}")
        print(response.json())
    except NotPublishedException:
        print(f"Rule ain´t published yet! STATUS: {response.status_code}")
        print(response)
    except InternalServerError:
        print(f"Internal server error. STATUS: {response.status_code}")
        print(response)
    except GeneralException:
        print(f"General exception, something went wrong. STATUS: {response.status_code}")
        print(response)


async def put_rule(rule_id, version, data):
    url = f"{url_factory()}/rule/{rule_id}/{version}"

    response = None

    try:
        response = requests.put(url, json=data, headers=_header)
        return
    except NoUserException:
        print(f"No valid user! STATUS: {response.status_code}")
        print(response.json())
    except TooManyApiCallsException:
        print(f"Too many api calls! STATUS: {response.status_code}")
        print(response.json())
    except NotPublishedException:
        print(f"Rule ain´t published yet! STATUS: {response.status_code}")
        print(response)
    except InternalServerError:
        print(f"Internal server error. STATUS: {response.status_code}")
        print(response)
    except GeneralException:
        print(f"General exception, something went wrong. STATUS: {response.status_code}")
        print(response)


async def delete_rule(rule_id, version):
    url = f"{url_factory()}/rule/{rule_id}/{version}"

    response = None

    try:
        requests.delete(url, headers=_header)
        return
    except NoUserException:
        print(f"No valid user! STATUS: {response.status_code}")
        print(response.json())
    except TooManyApiCallsException:
        print(f"Too many api calls! STATUS: {response.status_code}")
        print(response.json())
    except NotPublishedException:
        print(f"Rule ain´t published yet! STATUS: {response.status_code}")
        print(response)
    except InternalServerError:
        print(f"Internal server error. STATUS: {response.status_code}")
        print(response)
    except GeneralException:
        print(f"General exception, something went wrong. STATUS: {response.status_code}")
        print(response)
