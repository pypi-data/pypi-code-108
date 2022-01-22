from aiohttp.web import Application
from .mongotestcase import MongoTestCase
from ..db.mongo import Mongo, replace_id_with_object_id
from .. import runner
from .. import wstl
import logging
from typing import Union, Dict, List, Any, Optional, Type, Iterable
from testcontainers.mongodb import MongoDbContainer
import gridfs
from bson import ObjectId
from contextlib import ExitStack
from io import BytesIO
from yarl import URL
import os
from .expectedvalues import expected_values, ActionSpec, LinkSpec
from heaserver.service.docker import get_exposed_port, start_microservice_container, DockerImage
from array import array


def get_test_case_cls(href: Union[URL, str],
                      wstl_package: str,
                      coll: str,
                      fixtures: Dict[str, List[dict]],
                      content: Optional[Dict[str, Dict[str, bytes]]] = None,
                      content_type: Optional[str] = None,
                      put_content_status: Optional[int] = None,
                      body_post: Optional[Dict[str, Dict[str, Any]]] = None,
                      body_put: Optional[Dict[str, Dict[str, Any]]] = None,
                      expected_one: Optional[Dict[str, Any]] = None,
                      expected_one_wstl: Optional[Dict[str, Any]] = None,
                      expected_one_duplicate_form: Optional[Dict[str, Any]] = None,
                      expected_all: Optional[Dict[str, Any]] = None,
                      expected_all_wstl: Optional[Dict[str, Any]] = None,
                      expected_opener: Optional[Union[str, URL]] = None,
                      expected_opener_body: Optional[Dict[str, Any]] = None,
                      registry_docker_image: Optional[str] = None,
                      port: Optional[int] = None) -> Type[MongoTestCase]:
    """
    This function configures mocks. It returns a base test case class for testing a mongodb-based service with the
    provided fixtures. The test case class is a subclass of aiohttp.test_utils.AioHTTPTestCase, and the provided
    fixtures can be found in the following fields: _resource_path, _body_post, _body_put, _expected_all, and
    _expected_one.

    :param href: the resource being tested (required).
    :param wstl_package: the name of the package containing the wstl data package (required).
    :param coll: the MongoDB collection (required).
    :param fixtures: data to insert into the mongo database before running each test. Should be a dict of
    collection -> list of objects. Required.
    :param content: :param content: data to insert into GridFS (optional), as a collection string -> HEA Object id ->
    content as a bytes, bytearray, or array.array object.
    :param content_type: the MIME type of the content (optional).
    :param put_content_status: the expected status code for updating the content of the HEA object (optional). Normally
    should be 204 if the content is updatable and 405 if not. Default is None, which will cause associated tests to be
    skipped.
    :param body_post: JSON dict for data to be posted.
    :param body_put: JSON dict for data to be put. If None, the value of body_post will be used for PUTs.
    :param expected_one: The expected JSON dict for GET calls. If None, the value of expected_all will be used.
    :param expected_one_wstl: The expected JSON dict for GET calls that return the
    application/vnd.wstl+json mime type.
    :param expected_one_duplicate_form: The expected JSON dict for GET calls that return the
    object's duplicate form.
    :param expected_all: The expected JSON dict for GET-all calls.
    :param expected_all_wstl: The expected JSON dict for GET-all calls that return the
    application/vnd.wstl+json mime type.
    :param expected_opener: The expected URL of the resource that does the opening.
    :param expected_opener_body: The expected JSON dict for GET calls for an HEA desktop object's opener choices.
    :param registry_docker_image: an heaserver-registry docker image in REPOSITORY:TAG format, that will be launched
    after the MongoDB container is live.
    :param port: the port number to run aiohttp. If None, a random available port will be chosen.
    :return the base test case class.
    """

    class RealMongoTestCase(MongoTestCase):
        """
        Test case class for testing a mongodb-based service.
        """

        def __init__(self, methodName: str = 'runTest') -> None:
            """
            Initializes a test case.

            :param methodName: the name of the method to test.
            """
            super().__init__(methodName=methodName,
                             href=href,
                             coll=coll,
                             body_post=body_post,
                             body_put=body_put,
                             expected_all=expected_all,
                             expected_one=expected_one or expected_all,
                             expected_one_wstl=expected_one_wstl or expected_all_wstl,
                             expected_all_wstl=expected_all_wstl,
                             expected_one_duplicate_form=expected_one_duplicate_form,
                             expected_opener=expected_opener,
                             expected_opener_body=expected_opener_body,
                             wstl_package=wstl_package,
                             content=content,
                             content_type=content_type,
                             put_content_status=put_content_status,
                             port=port)

        def run(self, result=None):
            """
            Runs a test using a freshly created MongoDB Docker container. The container is destroyed upon concluding
            the test.

            :param result: a TestResult object into which the test's result is collected.
            :return: the TestResult object.
            """
            with ExitStack() as stack, self._caplog.at_level(logging.DEBUG):
                config_file = setup_test_environment(stack, fixtures, content, registry_docker_image=registry_docker_image)
                self.__config = runner.init(config_string=config_file)
                return super().run(result)

        async def get_application(self) -> Application:
            return runner.get_application(db=Mongo,
                                          wstl_builder_factory=wstl.builder_factory(wstl_package, href=href),
                                          config=self.__config,
                                          testing=True)

    return RealMongoTestCase


def get_test_case_cls_default(coll: str,
                              wstl_package: str,
                              fixtures: Dict[str, List[Dict[str, Any]]],
                              duplicate_action_name: str,
                              content: Optional[Dict[str, Dict[str, bytes]]] = None,
                              content_type: Optional[str] = None,
                              put_content_status: Optional[int] = None,
                              include_root=False,
                              href: Optional[Union[str, URL]] = None,
                              get_actions: Optional[List[ActionSpec]] = None,
                              get_all_actions: Optional[List[ActionSpec]] = None,
                              expected_opener: Optional[LinkSpec] = None,
                              registry_docker_image: Optional[str] = None,
                              port: Optional[int] = None) -> Type[MongoTestCase]:
    if href is None:
        href_ = str(URL(f'/{coll}/'))
    else:
        href_ = str(href)
        if not href_.endswith('/'):
            href_ = href_ + '/'
    return get_test_case_cls(href=href_, wstl_package=wstl_package, coll=coll, fixtures=fixtures,
                             content=content, content_type=content_type, put_content_status=put_content_status,
                             **expected_values(fixtures, coll, wstl.builder(package=wstl_package),
                                               duplicate_action_name, href_,
                                               include_root=include_root,
                                               get_actions=get_actions, get_all_actions=get_all_actions,
                                               opener_link=expected_opener),
                             registry_docker_image=registry_docker_image,
                             port=port
                             )


def setup_test_environment(stack: ExitStack,
                           fixtures: Dict[str, List[dict]],
                           content: Optional[Dict[str, Dict[str, bytes]]],
                           registry_docker_image: Optional[str] = None,
                           other_docker_images: Optional[Iterable[DockerImage]] = None) -> str:
    _logger = logging.getLogger(__name__)
    os.environ['MONGO_DB'] = 'hea'
    mongo_ = stack.enter_context(MongoDbContainer('mongo:4.2.2'))

    db = mongo_.get_connection_client().hea
    for k in fixtures or {}:
        db[k].insert_many(replace_id_with_object_id(f) for f in fixtures[k])
    content_ = content if content is not None else {}
    for k in content_:
        fs = gridfs.GridFSBucket(db, bucket_name=k)
        for id_, d in content_[k].items():
            if isinstance(d, (bytes, bytearray, array)):
                with BytesIO(d) as b:
                    fs.upload_from_stream_with_id(ObjectId(id_), id_, b)

    mongodb_connection_string = f'mongodb://test:test@{mongo_.get_container_host_ip()}:{get_exposed_port(mongo_, 27017)}/hea?authSource=admin'
    if registry_docker_image is None:
        config_file = f"""
                                        [MongoDB]
                                        ConnectionString = {mongodb_connection_string}
                                        """
    else:
        if other_docker_images is None:
            other_docker_images_: Iterable[DockerImage] = []
        else:
            other_docker_images_ = other_docker_images
        registry_url = start_microservice_container(DockerImage(image=registry_docker_image, port=8080, check_path='/components'), mongo_, stack)
        for image in other_docker_images_:
            start_microservice_container(image, mongo_, stack)
        config_file = f"""
                                        [DEFAULT]
                                        Registry={registry_url}

                                        [MongoDB]
                                        ConnectionString = {mongodb_connection_string}
                                            """
    _logger.debug('HEA config file: %s', config_file)
    return config_file
