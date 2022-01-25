import json
import os
from typing import KeysView, Dict, Any, Tuple
from urllib import parse


def prepare_identifier(
        payload: KeysView[str]
) -> str:
    """Convert keys object in dictionary to placeholder identifier
        example:
            we have object like this n = {"name": "andy", "age": 25}
            it will convert string like this {name: $name, age: $age}
            see it will not have quotes in string
    :param payload: dictionary keys
    :return: string key value without quotes
    """
    return json.dumps({
        k: f"${k}" for k in payload
    }).replace('"', "")


def make_identifier(
        param: Dict[str, Any],
) -> str:
    """Convert dictionary to parameter neo4j identifier
        example:
            we have object like this n = {"name": "andy", "age": 25}
            it will converted to format like this {name": "andy", age: 25}
            see it will remove quotes from name and age, cause name and age is identifier for neo4j
    :param param: dictionary
    :return: string object identifier
    """
    return "{" + "{}".format(", ".join([f'{k}: "{v}"' for k, v in param.items()])) + "}"


def parse_connection_uri(
        connection_uri: str
) -> Tuple[str, str, str]:
    """Parse connection uri to separate variable
    this function will fix connection uri and return new connection_uri, username and password
    :param connection_uri: string connection uri
    :return: tuple of string
    """
    connection_uri = parse.urlparse(connection_uri)
    username, password = connection_uri.username, connection_uri.password
    connection_uri = parse.urlunparse(
        connection_uri._replace(netloc="{}:{}".format(connection_uri.hostname, connection_uri.port))
    )
    return connection_uri, username, password


def get_cpu_count(

) -> int:
    """Get current cpu number in this machine
    :return: integer value
    """
    # Get the number of CPUs
    # in the system using
    # os.cpu_count() method
    cpu_count = os.cpu_count()
    return cpu_count
