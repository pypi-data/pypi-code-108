"""
This module implements a simple API for launching a swagger UI for trying out a HEA microservice's REST APIs.
"""

from testcontainers.mongodb import MongoDbContainer
from contextlib import ExitStack
from . import runner, wstl, db
from .db import mongo
from aiohttp_swagger3 import SwaggerDocs, SwaggerUiSettings
from aiohttp_swagger3.handlers import application_json
from aiohttp import web
from importlib.metadata import version
from typing import Dict, List, Tuple, Callable, Iterable, Optional
from types import ModuleType
from urllib.request import urlopen
import os
from tempfile import NamedTemporaryFile
from .docker import get_exposed_port
from heaserver.service.docker import DockerImage, start_microservice_container
from heaobject.root import HEAObjectDict
from copy import deepcopy


def run(project_slug: str,
        fixtures: Dict[str, List[HEAObjectDict]],
        module: ModuleType,
        routes: Iterable[Tuple[Callable, str, Callable]],
        registry_docker_image: Optional[str] = None,
        other_docker_images: Optional[List[DockerImage]] = None) -> None:
    """
    Launches a swagger UI for trying out the given HEA APIs. It downloads the HEA OpenAPI spec from gitlab.com,
    launches a MongoDB database in a Docker container, inserts the given HEA objects into it, and makes the given
    routes available to query in swagger.

    It prints the target service's configuration so that you can see the MongoDB connection string.

    :param project_slug: the Gitlab project slug of interest. Required.
    :param fixtures: a mapping of mongo collection -> list of HEA objects as dicts. Required.
    :param module: the microservice's service module.
    :param routes: a list of three-tuples containing the command, path and collable of each route of interest. The
    commands are one of: aiohttp.web.get, aiohttp.web.delete, aiohttp.web.post, aiohttp.web.put or aiohttp.web.view.
    :param registry_docker_image: an heaserver-registry docker image in REPOSITORY:TAG format, that will be launched
    after the MongoDB container is live.
    :param other_docker_images: optional list of HEA microservice docker images.
    :raises OSError: If an error occurred accessing the OpenAPI spec.
    """
    fixtures_ = deepcopy(fixtures)

    def download_openapi_spec():
        """
        Downloads HEA's OpenAPI spec file into a temporary file.
        :return: the path of the temp file.
        :raises OSError: if an error occurred downloading and writing the spec to a temporary file.
        """
        with NamedTemporaryFile(delete=False) as tmpfile:
            with urlopen(
                'https://gitlab.com/huntsman-cancer-institute/risr/hea/hea-openapi-specs/-/raw/master/openapi.yaml') as url:
                tmpfile.write(url.read())
            return tmpfile.name

    done = False
    openapi_spec_file = download_openapi_spec()
    try:
        os.environ['MONGO_DB'] = 'hea'
        with ExitStack() as stack:
            mongo_container = MongoDbContainer('mongo:4.2.2')
            mongo_ = stack.enter_context(mongo_container)
            mongodb_connection_string = f'mongodb://test:test@{mongo_.get_container_host_ip()}:{get_exposed_port(mongo_, 27017)}/hea?authSource=admin'
            if registry_docker_image is None:
                config_file = f"""
[MongoDB]
ConnectionString = {mongodb_connection_string}
"""
            elif registry_docker_image is not None:
                registry_url = start_microservice_container(
                    DockerImage(image=registry_docker_image, port=8080, check_path='/components'), mongo_, stack)
                config_file = f"""
[DEFAULT]
Registry={registry_url}

[MongoDB]
ConnectionString = {mongodb_connection_string}
                """
            for img in other_docker_images or []:
                url_ = start_microservice_container(img, mongo_, stack, registry_url)
                fixtures_.setdefault('components', []).append(
                    {'type': 'heaobject.registry.Component', 'base_url': url_, 'name': url_, "owner": "system|none",
                     'resources': img.resources})
            config = runner.init(config_string=config_file)
            _insert_fixtures_into_db(mongo_, fixtures_)
            app = runner.get_application(db.mongo.Mongo,
                                         wstl_builder_factory=wstl.builder_factory(module.__package__, href='/'),
                                         config=config)
            swagger = SwaggerDocs(app,
                                  swagger_ui_settings=SwaggerUiSettings(path="/docs"),
                                  title=project_slug,
                                  version=version(project_slug),
                                  components=openapi_spec_file)
            os.remove(openapi_spec_file)
            swagger.register_media_type_handler('application/vnd.collection+json', application_json)
            swagger.add_routes([r[0](r[1], r[2]) for r in routes])
            web.run_app(app)
        done = True
    finally:
        if not done:
            try:
                os.remove(openapi_spec_file)
            except OSError:
                pass


def _insert_fixtures_into_db(mongo_: MongoDbContainer, fixtures: Dict[str, List[HEAObjectDict]]) -> None:
    db_ = mongo_.get_connection_client().hea
    for k in fixtures or {}:
        db_[k].insert_many(mongo.replace_id_with_object_id(f) for f in fixtures[k])
