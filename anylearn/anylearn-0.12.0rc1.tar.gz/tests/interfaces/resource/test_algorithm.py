import responses
from requests.exceptions import RequestException

from anylearn.config import init_sdk
from anylearn.interfaces.resource.resource import ResourceState, ResourceVisibility
from anylearn.interfaces.resource.algorithm import Algorithm
from anylearn.utils.errors import AnyLearnException, AnyLearnMissingParamException
from tests.base_test_case import BaseTestCase

class TestAlgorithm(BaseTestCase):
    @responses.activate
    def test_list_algo_ok(self):
        responses.add(responses.GET, url=self._url("algorithm/list"),
                      json=[
                          {
                              'id': "ALGO001",
                              'name': "TestAlgo1",
                              'description': "test",
                              'state': ResourceState.READY,
                              'visibility': ResourceVisibility.PUBLIC,
                              'upload_time': "2020-01-01 00:00",
                              'tags': "tag1, tag2",
                              'follows_anylearn_norm': True,
                              'git_address': "http://anylearn.testing/anylearn/TestAlgo1.git",
                              'git_migrated': True,
                          },
                          {
                              'id': "ALGO002",
                              'name': "TestAlgo2",
                              'description': "test",
                              'state': ResourceState.READY,
                              'visibility': ResourceVisibility.PUBLIC,
                              'upload_time': "2020-01-02 00:00",
                              'tags': "tag3, tag4",
                              'follows_anylearn_norm': False,
                              'git_address': "http://anylearn.testing/anylearn/TestAlgo2.git",
                              'git_migrated': True,
                          },
                      ],
                      status=200)
        algos = Algorithm.get_list()
        self.assertIsInstance(algos, list)
        self.assertEqual(len(algos), 2)
        self.assertIsInstance(algos[0], Algorithm)
        self.assertIsInstance(algos[1], Algorithm)
        self.assertEqual(algos[0].id, "ALGO001")
        self.assertEqual(algos[1].id, "ALGO002")
        self.assertEqual(algos[0].tags, "tag1, tag2")
        self.assertEqual(algos[1].tags, "tag3, tag4")
        self.assertEqual(algos[0].follows_anylearn_norm, True)
        self.assertEqual(algos[1].follows_anylearn_norm, False)

    @responses.activate
    def test_list_algo_ko_unknown_response(self):
        responses.add(responses.GET, url=self._url("algorithm/list"),
                      json={'msg': "Unknown response"},
                      status=200)
        with self.assertRaises(AnyLearnException) as ctx:
            Algorithm.get_list()
        e = ctx.exception
        self.assertIsInstance(e, AnyLearnException)
        self.assertEqual(e.msg, "请求未能得到有效响应")

    @responses.activate
    def test_get_algo_detail_explicit_call_ok(self):
        responses.add(responses.GET, url=self._url("algorithm/query?id=ALGO001"),
                      match_querystring=True, json=[{
                          'id': "ALGO001",
                          'name': "TestAlgo1",
                          'description': "test",
                          'state': ResourceState.READY,
                          'visibility': ResourceVisibility.PUBLIC,
                          'upload_time': "2020-01-01 00:00",
                          'filename': "test.tar.gz",
                          'is_zipfile': 1,
                          'file': "USER001/algos/ALGO001/test.tar.gz",
                          'size': "250.41",
                          'creator_id': "USER001",
                          'node_id': "NODE001",
                          'owner': ["USER001"],
                          'tags': "tag1, tag2",
                          'train_params': '[{"test": "test"}]',
                          'evaluate_params': '[{"test": "test"}]',
                          'mirror_id': "MIRR001",
                          'follows_anylearn_norm': True,
                          'entrypoint_training': "python train.py",
                          'output_training': "output",
                          'entrypoint_evaluation': "python eval.py",
                          'output_evaluation': "output",
                          'git_address': "http://anylearn.testing/user001/TestAlgo1.git",
                          'git_migrated': True,
                      }],
                      status=200)
        algo = Algorithm(id="ALGO001")
        algo.get_detail()
        self.assertEqual(algo.filename, "test.tar.gz")
        self.assertTrue(algo.is_zipfile)
        self.assertEqual(algo.file_path, "USER001/algos/ALGO001/test.tar.gz")
        self.assertEqual(algo.size, "250.41")
        self.assertEqual(algo.creator_id, "USER001")
        self.assertEqual(algo.node_id, "NODE001")
        self.assertIsInstance(algo.owner, list)
        self.assertEqual(algo.owner[0], "USER001")
        self.assertEqual(algo.tags, "tag1, tag2")
        self.assertIsInstance(algo.train_params, list)
        self.assertIsInstance(algo.evaluate_params, list)
        self.assertEqual(str(algo.train_params), "[{'test': 'test'}]")
        self.assertEqual(str(algo.evaluate_params), "[{'test': 'test'}]")
        self.assertEqual(algo.mirror_id, "MIRR001")
        self.assertEqual(algo.follows_anylearn_norm, True)
        self.assertEqual(algo.entrypoint_training, "python train.py")
        self.assertEqual(algo.output_training, "output")
        self.assertEqual(algo.entrypoint_evaluation, "python eval.py")
        self.assertEqual(algo.output_evaluation, "output")

    @responses.activate
    def test_get_algo_detail_no_explicit_call_ok(self):
        responses.add(responses.GET, url=self._url("algorithm/query?id=ALGO001"),
                      match_querystring=True, json=[{
                          'id': "ALGO001",
                          'name': "TestAlgo1",
                          'description': "test",
                          'state': ResourceState.READY,
                          'visibility': ResourceVisibility.PUBLIC,
                          'upload_time': "2020-01-01 00:00",
                          'filename': "test.tar.gz",
                          'is_zipfile': 1,
                          'file': "USER001/algos/ALGO001/test.tar.gz",
                          'size': "250.41",
                          'creator_id': "USER001",
                          'node_id': "NODE001",
                          'owner': ["USER001"],
                          'tags': "tag1, tag2",
                          'train_params': '[{"test": "test"}]',
                          'evaluate_params': '[{"test": "test"}]',
                          'mirror_id': "MIRR001",
                          'follows_anylearn_norm': False,
                          'entrypoint_training': "python niart.py",
                          'output_training': "tuptuo",
                          'entrypoint_evaluation': "python lave.py",
                          'output_evaluation': "tuptuo",
                          'git_address': "http://anylearn.testing/user001/TestAlgo1.git",
                          'git_migrated': True,
                      }],
                      status=200)
        algo = Algorithm(id="ALGO001", load_detail=True)
        self.assertEqual(algo.name, "TestAlgo1")
        self.assertEqual(algo.filename, "test.tar.gz")
        self.assertTrue(algo.is_zipfile)
        self.assertEqual(algo.file_path, "USER001/algos/ALGO001/test.tar.gz")
        self.assertEqual(algo.size, "250.41")
        self.assertEqual(algo.creator_id, "USER001")
        self.assertEqual(algo.node_id, "NODE001")
        self.assertIsInstance(algo.owner, list)
        self.assertEqual(algo.owner[0], "USER001")
        self.assertEqual(algo.tags, "tag1, tag2")
        self.assertIsInstance(algo.train_params, list)
        self.assertIsInstance(algo.evaluate_params, list)
        self.assertEqual(str(algo.train_params), "[{'test': 'test'}]")
        self.assertEqual(str(algo.evaluate_params), "[{'test': 'test'}]")
        self.assertEqual(algo.mirror_id, "MIRR001")
        self.assertEqual(algo.follows_anylearn_norm, False)
        self.assertEqual(algo.entrypoint_training, "python niart.py")
        self.assertEqual(algo.output_training, "tuptuo")
        self.assertEqual(algo.entrypoint_evaluation, "python lave.py")
        self.assertEqual(algo.output_evaluation, "tuptuo")

    @responses.activate
    def test_get_algo_detail_ko_403(self):
        responses.add(responses.GET, url=self._url("algorithm/query?id=ALGO403"),
                      match_querystring=True, status=403)
        algo = Algorithm(id="ALGO403")
        with self.assertRaises(RequestException) as ctx:
            algo.get_detail()
        e = ctx.exception
        self.assertIsInstance(e, RequestException)
        self.assertEqual(e.response.status_code, 403)

    @responses.activate
    def test_get_algo_detail_ko_unknown_response(self):
        responses.add(responses.GET, url=self._url("algorithm/query?id=ALGO250"),
                      match_querystring=True, json={'msg': "Unknown response"},
                      status=200)
        algo = Algorithm(id="ALGO250")
        with self.assertRaises(AnyLearnException) as ctx:
            algo.get_detail()
        e = ctx.exception
        self.assertIsInstance(e, AnyLearnException)
        self.assertEqual(e.msg, "请求未能得到有效响应")

    @responses.activate
    def test_get_algo_detail_empty_list(self):
        responses.add(responses.GET, url=self._url("algorithm/query?id=ALGO250"),
                      match_querystring=True, json=[],
                      status=200)
        algo = Algorithm(id="ALGO250")
        with self.assertRaises(AnyLearnException) as ctx:
            algo.get_detail()
        e = ctx.exception
        self.assertIsInstance(e, AnyLearnException)
        self.assertEqual(e.msg, "请求未能得到有效响应")

    @responses.activate
    def test_create_algo_ok(self):
        responses.add(responses.POST, url=self._url("algorithm/add"),
                      json={'data': "ALGO001", 'message': "算法添加成功"},
                      status=200)
        algo = Algorithm(name="TestALGO001", filename="test.tar.gz",
                         train_params='[{"name": "test", "type": "int", "suggest": 1, "default": "0", "scope": "<0,1>"}]',
                         evaluate_params='[{"name": "test", "type": "int", "suggest": 1, "default": "0", "scope": "<0,1>"}]',
                         mirror_id="MIRR001")
        result = algo.save()
        self.assertTrue(result)
        self.assertEqual(algo.id, "ALGO001")

    def test_create_algo_ko_empty_name_filename_mirror_params(self):
        algo = Algorithm()
        with self.assertRaises(AnyLearnMissingParamException) as ctx:
            algo.save()
        e = ctx.exception
        self.assertIsInstance(e, AnyLearnMissingParamException)
        self.assertEqual(e.msg, "Algorithm缺少必要字段：['name', 'filename', 'mirror_id', 'train_params', 'evaluate_params']")

    # def test_create_algo_ko_empty_entrypoint_training_output_training(self):
    #     algo = Algorithm(name="TestALGO250", filename="test.tar.gz",
    #                      train_params='[{"name": "test", "type": "int", "suggest": 1, "default": "0", "scope": "<0,1>"}]',
    #                      evaluate_params='[{"name": "test", "type": "int", "suggest": 1, "default": "0", "scope": "<0,1>"}]',
    #                      mirror_id="MIRR001", follows_anylearn_norm=False)
    #     with self.assertRaises(AnyLearnMissingParamException) as ctx:
    #         algo.save()
    #     e = ctx.exception
    #     self.assertIsInstance(e, AnyLearnMissingParamException)
    #     self.assertEqual(e.msg, "Algorithm缺少必要字段：['entrypoint_training', 'output_training']")

    @responses.activate
    def test_create_algo_ko_unknown_response(self):
        responses.add(responses.POST, url=self._url("algorithm/add"),
                      json={'msg': "Unknown response"}, status=201)
        algo = Algorithm(name="TestAlgo", filename="ALGO250.tar.gz",
                         train_params='[{"test": "test"}]',
                         evaluate_params='[{"test": "test"}]',
                         mirror_id="MIRR001")
        with self.assertRaises(AnyLearnException) as ctx:
            algo.save()
        e = ctx.exception
        self.assertIsInstance(e, AnyLearnException)
        self.assertEqual(e.msg, "请求未能得到有效响应")

    @responses.activate
    def test_update_algo_ok(self):
        responses.add(responses.PUT, url=self._url("algorithm/update"),
                      json={'data': "ALGO001", 'message': "算法信息更新成功"},
                      status=200)
        algo = Algorithm(id="ALGO001", name="TestAlgo1", description="test m",
                          state=ResourceState.READY,
                          visibility=ResourceVisibility.PUBLIC,
                          upload_time="2020-01-01 00:00")
        result = algo.save()
        self.assertTrue(result)

    @responses.activate
    def test_update_algo_ko_empty_name(self):
        algo = Algorithm(id="ALGO250", name="")
        with self.assertRaises(AnyLearnMissingParamException) as ctx:
            algo.save()
        e = ctx.exception
        self.assertIsInstance(e, AnyLearnMissingParamException)
        self.assertEqual(e.msg, "Algorithm缺少必要字段：['name']")

    @responses.activate
    def test_update_algo_ko_unknown_response(self):
        responses.add(responses.PUT, url=self._url("algorithm/update"),
                      json={'msg': "Unknown response"},
                      status=200)
        algo = Algorithm(id="ALGO250", name="TestAlgo", description="test",
                          state=ResourceState.READY,
                          visibility=ResourceVisibility.PROTECTED,
                          upload_time="2020-01-01 02:50")
        with self.assertRaises(AnyLearnException) as ctx:
            algo.save()
        e = ctx.exception
        self.assertIsInstance(e, AnyLearnException)
        self.assertEqual(e.msg, "请求未能得到有效响应")

    @responses.activate
    def test_delete_algo_ok(self):
        responses.add(responses.DELETE,
                      url=self._url("algorithm/delete?id=ALGO001&force=0"),
                      match_querystring=True,
                      json={'data': "ALGO001", 'message': "算法删除成功"},
                      status=200)
        algo = Algorithm(id="ALGO001", name="TestAlgo1", description="test d",
                          state=ResourceState.READY,
                          visibility=ResourceVisibility.PUBLIC,
                          upload_time="2020-01-01 00:00")
        result = algo.delete()
        self.assertTrue(result)

    @responses.activate
    def test_delete_algo_ko_unknown_response(self):
        responses.add(responses.DELETE,
                      url=self._url("algorithm/delete?id=ALGO250&force=0"),
                      match_querystring=True,
                      json={'msg': "Unknown response"},
                      status=204)
        algo = Algorithm(id="ALGO250", name="TestAlgo", description="test",
                          state=ResourceState.READY,
                          visibility=ResourceVisibility.PROTECTED,
                          upload_time="2020-01-01 02:50")
        with self.assertRaises(AnyLearnException) as ctx:
            algo.delete()
        e = ctx.exception
        self.assertIsInstance(e, AnyLearnException)
        self.assertEqual(e.msg, "请求未能得到有效响应")

    def test_algo_params_parsing(self):
        json_params = '''
            [
                {"name": "test0", "type": "int", "suggest": 1, "scope": "<-Infinity,Infinity>"},
                {"name": "test1", "type": "int", "suggest": 1, "default": "1", "scope": "<0,1>"},
                {"name": "test2", "type": "int", "suggest": 1, "default": "2", "scope": "<0,2>"}
            ]
        '''
        algo = Algorithm(train_params=json_params, evaluate_params=json_params)
        
        self.assertIsInstance(algo.required_train_params, list)
        self.assertEqual(len(algo.required_train_params), 1)
        self.assertEqual(algo.required_train_params[0]['name'], 'test0')
        self.assertIsInstance(algo.default_train_params, dict)
        self.assertEqual(len(algo.default_train_params), 2)
        self.assertEqual(algo.default_train_params['test1'], '1')
        self.assertEqual(algo.default_train_params['test2'], '2')

        self.assertIsInstance(algo.required_evaluate_params, list)
        self.assertEqual(len(algo.required_evaluate_params), 1)
        self.assertEqual(algo.required_evaluate_params[0]['name'], 'test0')
        self.assertIsInstance(algo.default_evaluate_params, dict)
        self.assertEqual(len(algo.default_evaluate_params), 2)
        self.assertEqual(algo.default_evaluate_params['test1'], '1')
        self.assertEqual(algo.default_evaluate_params['test2'], '2')
