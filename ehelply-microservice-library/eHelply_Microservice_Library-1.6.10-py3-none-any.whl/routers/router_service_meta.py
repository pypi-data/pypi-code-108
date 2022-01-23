from fastapi import APIRouter, Cookie, Depends, Body, Query
from ehelply_bootstrapper.drivers.fast_api_utils.responses import *

from typing import List, Dict

import json
from pathlib import Path

from ehelply_bootstrapper.utils.state import State

router = APIRouter()


@router.get(
    '/meta',
    tags=["meta"],
)
async def get_meta():
    """
    Returns the service meta for this microservice
    :return:
    """
    return http_200_ok({
        "version": State.bootstrapper.service_meta.version,
        "name": State.bootstrapper.service_meta.name,
        "summary": State.bootstrapper.service_meta.summary,
        "authors": State.bootstrapper.service_meta.authors,
        "author_emails": State.bootstrapper.service_meta.author_emails
    })


@router.get(
    '/releases',
    tags=["releases"],
)
async def get_releases():
    """
    Returns the release history of this microservice
    :return:
    """
    releases_path: Path = State.bootstrapper.get_service_package_path().joinpath("releases.json")

    with open(str(releases_path)) as file:
        releases_data: list = json.load(file)

    return http_200_ok(releases_data)


@router.get(
    '/releases/{release}',
    tags=["releases"],
)
async def get_release(
        release: str
):
    """
    Returns information about a particular release

    If the release parameter is 'latest', it will be set to the current version of THIS running microservice

    :param release:
    :return:
    """
    if release == "latest":
        release = State.bootstrapper.service_meta.version

    releases_path: Path = State.bootstrapper.get_service_package_path().joinpath("releases.json")

    with open(str(releases_path)) as file:
        releases_data: list = json.load(file)

    for release_from_service in releases_data:
        if release_from_service['version'] == release:
            return http_200_ok(release_from_service)

    return http_404_not_found()


@router.get(
    '/releases/{release}/spec',
    tags=["releases"],
)
async def get_release(
        release: str
):
    """
    Returns the JSON spec of a microservice

    If the release parameter is 'latest', it will be set to the current version of THIS running microservice

    :param release:
    :return:
    """
    if release == "latest":
        release = State.bootstrapper.service_meta.version

    import glob

    docs_path: Path = State.bootstrapper.get_service_package_path().joinpath("docs")

    latest_name: str = ""
    for file_name in glob.glob(str(docs_path) + "/api-spec_{release}_*.json".format(release=release)):

        if Path(file_name).name > latest_name:
            latest_name = Path(file_name).name

    if len(latest_name) == 0:
        return http_404_not_found()

    try:
        with open(str(docs_path.joinpath(latest_name))) as file:
            spec = json.load(file)

        return spec

    except:
        return http_404_not_found()


@router.get(
    '/template',
    tags=["releases"],
)
async def get_service_template_details():
    """
    Returns details about the current service template this microservice is using such as the version
    :return:
    """
    package_path: Path = State.bootstrapper.get_service_package_path().joinpath("ehelply-package.json")

    with open(str(package_path)) as file:
        package_data: dict = json.load(file)

    return package_data
