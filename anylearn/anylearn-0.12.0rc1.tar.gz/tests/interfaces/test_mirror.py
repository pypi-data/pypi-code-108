import responses

from anylearn.interfaces.mirror import Mirror
from anylearn.utils.errors import AnyLearnException, AnyLearnMissingParamException
from tests.base_test_case import BaseTestCase

class TestMirror(BaseTestCase):
    @responses.activate
    def test_list_mirror_ok(self):
        responses.add(responses.GET, url=self._url("mirror/list"),
                      json=[
                          {
                              'id': "MIRR001",
                              'name': "Test001",
                              'requirements': "test==0.0.1",
                          },
                          {
                              'id': "MIRR002",
                              'name': "Test002",
                              'requirements': "test==0.0.2",
                          },
                      ],
                      status=200)
        mirrors = Mirror.get_list()
        self.assertIsInstance(mirrors, list)
        self.assertEqual(len(mirrors), 2)
        self.assertIsInstance(mirrors[0], Mirror)
        self.assertIsInstance(mirrors[1], Mirror)
        self.assertEqual(mirrors[0].id, "MIRR001")
        self.assertEqual(mirrors[1].id, "MIRR002")
        self.assertEqual(mirrors[0].name, "Test001")
        self.assertEqual(mirrors[1].name, "Test002")

    @responses.activate
    def test_list_mirror_ko_unknown_response(self):
        responses.add(responses.GET, url=self._url("mirror/list"),
                      json={'msg': "Unknown response"},
                      status=200)
        with self.assertRaises(AnyLearnException) as ctx:
            Mirror.get_list()
        e = ctx.exception
        self.assertIsInstance(e, AnyLearnException)
        self.assertEqual(e.msg, "请求未能得到有效响应")
