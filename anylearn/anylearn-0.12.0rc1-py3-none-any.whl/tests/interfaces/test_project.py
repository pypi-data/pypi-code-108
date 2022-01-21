import responses
from requests.exceptions import RequestException

from anylearn.interfaces.project import Project, ProjectVisibility
from anylearn.utils.errors import AnyLearnException, AnyLearnMissingParamException
from tests.base_test_case import BaseTestCase

class TestProject(BaseTestCase):
    @responses.activate
    def test_list_project_ok(self):
        responses.add(responses.GET, url=self._url("project/list"),
                      json=[
                          {
                              'id': "PROJ001",
                              'name': "TestPROJ1",
                              'description': "test",
                              'create_time': "2020-03-01 00:00",
                              'update_time': "2020-03-01 00:00",
                          },
                          {
                              'id': "PROJ002",
                              'name': "TestPROJ2",
                              'description': "test",
                              'create_time': "2020-03-02 00:00",
                              'update_time': "2020-03-02 00:00",
                          },
                      ],
                      status=200)
        projects = Project.get_list()
        self.assertIsInstance(projects, list)
        self.assertEqual(len(projects), 2)
        self.assertIsInstance(projects[0], Project)
        self.assertIsInstance(projects[1], Project)
        self.assertEqual(projects[0].id, "PROJ001")
        self.assertEqual(projects[1].id, "PROJ002")

    @responses.activate
    def test_list_project_ko_unknown_response(self):
        responses.add(responses.GET, url=self._url("project/list"),
                      json={'msg': "Unknown response"},
                      status=200)
        with self.assertRaises(AnyLearnException) as ctx:
            Project.get_list()
        e = ctx.exception
        self.assertIsInstance(e, AnyLearnException)
        self.assertEqual(e.msg, "请求未能得到有效响应")

    @responses.activate
    def test_get_project_detail_explicit_call_ok(self):
        responses.add(responses.GET, url=self._url("project/query?id=PROJ001"),
                      match_querystring=True, json=[{
                          'id': "PROJ001",
                          'name': "TestProj1",
                          'description': "test",
                          'visibility': ProjectVisibility.PUBLIC,
                          'create_time': "2020-03-01 00:00",
                          'update_time': "2020-03-01 00:00",
                          'creator_id': "USER001",
                          'owner': ["USER001"],
                          'datasets': ["DSET001", "DSET002"]
                      }],
                      status=200)
        project = Project(id="PROJ001")
        project.get_detail()
        self.assertEqual(project.name, "TestProj1")
        self.assertEqual(project.description, "test")
        self.assertEqual(project.visibility, ProjectVisibility.PUBLIC)
        self.assertEqual(project.create_time, "2020-03-01 00:00")
        self.assertEqual(project.update_time, "2020-03-01 00:00")
        self.assertEqual(project.creator_id, "USER001")
        self.assertIsInstance(project.owner, list)
        self.assertEqual(project.owner[0], "USER001")
        self.assertIsInstance(project.datasets, list)
        if isinstance(project.datasets, list):
            self.assertEqual(len(project.datasets), 2)
        self.assertEqual(project.datasets[0], "DSET001")
        self.assertEqual(project.datasets[1], "DSET002")

    @responses.activate
    def test_get_project_detail_no_explicit_call_ok(self):
        responses.add(responses.GET, url=self._url("project/query?id=PROJ002"),
                      match_querystring=True, json=[{
                          'id': "PROJ002",
                          'name': "TestProj2",
                          'description': "test",
                          'visibility': ProjectVisibility.PUBLIC,
                          'create_time': "2020-03-02 00:00",
                          'update_time': "2020-03-02 00:00",
                          'creator_id': "USER001",
                          'owner': ["USER001"],
                          'datasets': ["DSET001", "DSET002"]
                      }],
                      status=200)
        project = Project(id="PROJ002")
        project.get_detail()
        self.assertEqual(project.name, "TestProj2")
        self.assertEqual(project.description, "test")
        self.assertEqual(project.visibility, ProjectVisibility.PUBLIC)
        self.assertEqual(project.create_time, "2020-03-02 00:00")
        self.assertEqual(project.update_time, "2020-03-02 00:00")
        self.assertEqual(project.creator_id, "USER001")
        self.assertIsInstance(project.owner, list)
        self.assertEqual(project.owner[0], "USER001")
        self.assertIsInstance(project.datasets, list)
        if isinstance(project.datasets,list):
            self.assertEqual(len(project.datasets), 2)
        self.assertEqual(project.datasets[0], "DSET001")
        self.assertEqual(project.datasets[1], "DSET002")

    @responses.activate
    def test_get_project_detail_ko_403(self):
        responses.add(responses.GET, url=self._url("project/query?id=PROJ403"),
                      match_querystring=True, status=403)
        project = Project(id="PROJ403")
        with self.assertRaises(RequestException) as ctx:
            project.get_detail()
        e = ctx.exception
        self.assertIsInstance(e, RequestException)
        self.assertEqual(e.response.status_code, 403)

    @responses.activate
    def test_get_project_detail_ko_unknown_response(self):
        responses.add(responses.GET, url=self._url("project/query?id=DSET250"),
                      match_querystring=True, json={'msg': "Unknown response"},
                      status=200)
        project = Project(id="DSET250")
        with self.assertRaises(AnyLearnException) as ctx:
            project.get_detail()
        e = ctx.exception
        self.assertIsInstance(e, AnyLearnException)
        self.assertEqual(e.msg, "请求未能得到有效响应")

    @responses.activate
    def test_get_project_detail_empty_list(self):
        responses.add(responses.GET, url=self._url("project/query?id=DSET250"),
                      match_querystring=True, json=[],
                      status=200)
        project = Project(id="DSET250")
        with self.assertRaises(AnyLearnException) as ctx:
            project.get_detail()
        e = ctx.exception
        self.assertIsInstance(e, AnyLearnException)
        self.assertEqual(e.msg, "请求未能得到有效响应")

    @responses.activate
    def test_create_project_ok(self):
        responses.add(responses.POST, url=self._url("project/add"),
                      json={'data': "PROJ001", 'message': "项目添加成功"},
                      status=200)
        project = Project(name="TestProj001")
        result = project.save()
        self.assertTrue(result)
        self.assertEqual(project.id, "PROJ001")

    @responses.activate
    def test_create_project_ko_empty_name(self):
        project = Project()
        with self.assertRaises(AnyLearnMissingParamException) as ctx:
            project.save()
        e = ctx.exception
        self.assertIsInstance(e, AnyLearnMissingParamException)
        self.assertEqual(e.msg, "Project缺少必要字段：['name']")

    @responses.activate
    def test_create_project_ko_unknown_response(self):
        responses.add(responses.POST, url=self._url("project/add"),
                      json={'msg': "Unknown response"}, status=201)
        project = Project(name="TestProj250")
        with self.assertRaises(AnyLearnException) as ctx:
            project.save()
        e = ctx.exception
        self.assertIsInstance(e, AnyLearnException)
        self.assertEqual(e.msg, "请求未能得到有效响应")

    @responses.activate
    def test_update_project_ok(self):
        responses.add(responses.PUT, url=self._url("project/update"),
                      json={'data': "PROJ001", 'message': "项目信息更新成功"},
                      status=200)
        project = Project(id="PROJ001", name="TestProj1", description="test m")
        result = project.save()
        self.assertTrue(result)

    @responses.activate
    def test_update_project_ko_empty_name(self):
        project = Project(id="PROJ250", name="")
        with self.assertRaises(AnyLearnMissingParamException) as ctx:
            project.save()
        e = ctx.exception
        self.assertIsInstance(e, AnyLearnMissingParamException)
        self.assertEqual(e.msg, "Project缺少必要字段：['name']")

    @responses.activate
    def test_update_project_ko_unknown_response(self):
        responses.add(responses.PUT, url=self._url("project/update"),
                      json={'msg': "Unknown response"},
                      status=200)
        project = Project(id="DSET250", name="TestDset", description="test")
        with self.assertRaises(AnyLearnException) as ctx:
            project.save()
        e = ctx.exception
        self.assertIsInstance(e, AnyLearnException)
        self.assertEqual(e.msg, "请求未能得到有效响应")

    @responses.activate
    def test_delete_project_ok(self):
        responses.add(responses.DELETE,
                      url=self._url("project/delete?id=PROJ001&force=0"),
                      match_querystring=True,
                      json={'data': "PROJ001", 'message': "项目删除成功"},
                      status=200)
        project = Project(id="PROJ001")
        result = project.delete()
        self.assertTrue(result)

    @responses.activate
    def test_delete_project_ko_unknown_response(self):
        responses.add(responses.DELETE,
                      url=self._url("project/delete?id=DSET250&force=0"),
                      match_querystring=True,
                      json={'msg': "Unknown response"},
                      status=204)
        project = Project(id="DSET250")
        with self.assertRaises(AnyLearnException) as ctx:
            project.delete()
        e = ctx.exception
        self.assertIsInstance(e, AnyLearnException)
        self.assertEqual(e.msg, "请求未能得到有效响应")
