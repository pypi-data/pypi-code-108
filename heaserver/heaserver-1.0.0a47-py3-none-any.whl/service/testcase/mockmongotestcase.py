"""
Sets up a testing environment for testing HEA services, including mock modules and classes. To use this module, do the
following in order:
1) Import this module before importing anything else to insure that all mocks are are used in subsequently imported
modules.
2) Import the service to be tested.
3) Call the get_test_case_cls with the fixtures to use in the unit tests.
4) Create subclasses of the returned unit test class to implement actual test cases. The mixin module in this package
contains implementations of unit tests to run for testing GET, POST, PUT and DELETE. Add these mixins as superclasses
of your test cases.
"""

from ..db.mockmongo import MockMongo
from . import mongotestcase
from aiohttp import web
import configparser
import logging
from typing import Type, Dict, List, Any, Optional, Union
from heaserver.service import runner, wstl
from .expectedvalues import expected_values, ActionSpec, LinkSpec
from yarl import URL
from heaobject.root import HEAObjectDict
from heaobject.user import NONE_USER


def get_test_case_cls(href: Union[str, URL],
                      wstl_package: str,
                      coll: str,
                      fixtures: Dict[str, List[HEAObjectDict]],
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
                      sub: Optional[str] = NONE_USER) -> Type[mongotestcase.MongoTestCase]:
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
    """

    def mock_mongo(app: web.Application, config: configparser.ConfigParser):
        return MockMongo(app, config, fixtures, content)

    class MockMongoTestCase(mongotestcase.MongoTestCase):
        """
        Test case class for testing a mongodb-based service.
        """

        def __init__(self, methodName=None):
            """
            Initializes a test case.

            :param methodName: the name of the method to test.
            """
            super().__init__(methodName=methodName,
                             coll=coll,
                             href=href,
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
                             sub=sub)

        def run(self, result=None):
            with self._caplog.at_level(logging.DEBUG):
                return super().run(result)

        async def get_application(self):
            return runner.get_application(db=mock_mongo,
                                          wstl_builder_factory=wstl.builder_factory(wstl_package, href=href),
                                          testing=True)

    return MockMongoTestCase


def get_test_case_cls_default(coll: str,
                              wstl_package: str,
                              fixtures: Dict[str, List[HEAObjectDict]],
                              duplicate_action_name: str,
                              content: Optional[Dict[str, Dict[str, bytes]]] = None,
                              content_type: Optional[str] = None,
                              put_content_status: Optional[int] = None,
                              include_root=False,
                              href: Optional[Union[str, URL]] = None,
                              get_actions: Optional[List[ActionSpec]] = None,
                              get_all_actions: Optional[List[ActionSpec]] = None,
                              expected_opener: Optional[LinkSpec] = None,
                              sub: Optional[str] = NONE_USER) -> Type[mongotestcase.MongoTestCase]:
    if href is None:
        href_ = str(URL(f'/{coll}/'))
    else:
        href_ = str(href)
        if not href_.endswith('/'):
            href_ = href_ + '/'
    return get_test_case_cls(href=href_, wstl_package=wstl_package, coll=coll, fixtures=fixtures,
                             content=content, content_type=content_type, put_content_status=put_content_status, sub=sub,
                             **expected_values(fixtures, coll, wstl.builder(package=wstl_package),
                                               duplicate_action_name, href_,
                                               include_root=include_root, get_actions=get_actions,
                                               get_all_actions=get_all_actions,
                                               opener_link=expected_opener))
