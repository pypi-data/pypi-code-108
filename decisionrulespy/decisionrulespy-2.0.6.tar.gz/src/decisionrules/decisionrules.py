import requests
from .exceptions import *
from .enums import *
from .custom_domain import *

_api_key: str
_geo_location: GeoLocations
_custom_domain: CustomDomain


def init(api_key, geo_location=GeoLocations.DEFAULT, custom_domain: CustomDomain = None):
    global _api_key
    _api_key = api_key
    global _geo_location
    _geo_location = geo_location
    global _custom_domain
    _custom_domain = custom_domain


async def solver(solver_type, rule_id, input_data, solver_strategy, version=None):
    endpoint = url_factory(solver_type, rule_id, version)

    header = header_factory(_api_key, solver_strategy)

    response = None

    try:
        response = requests.post(url=endpoint, json=request_parser(input_data), headers=header)

        validate_response(response.status_code)
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

    return response.json()


def url_factory(solver_type, rule_id, version):

    if _custom_domain is not None:
        url = f"{_custom_domain.custom_domain_protocol.value}://{_custom_domain.custom_domain_url}/{solver_type.value}/solve/"
    else:
        if _geo_location is not GeoLocations.DEFAULT:
            url = f"https://{_geo_location.value}.api.decisionrules.io/{solver_type.value}/solve/"
        else:
            url = f"https://api.decisionrules.io/{solver_type.value}/solve/"

    if version is not None:
        url += f"{rule_id}/{version}"
    else:
        url += rule_id

    return url


def validate_response(status_code):
    if status_code == 400:
        raise NoUserException
    elif status_code == 426:
        raise TooManyApiCallsException
    elif status_code == 401:
        raise NotPublishedException
    elif status_code == 500:
        raise InternalServerError


def header_factory(api_key, strategy):
    if strategy is not SolverStrategies.STANDARD:
        return {"Authorization": f"Bearer {api_key}"}
    else:
        return {"Authorization": f"Bearer {api_key}", "X-Strategy": strategy.value}


def request_parser(data):
    return {
        "data": data
    }
