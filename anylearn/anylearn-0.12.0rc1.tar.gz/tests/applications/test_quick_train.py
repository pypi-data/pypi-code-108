from pathlib import Path
import responses
from unittest.mock import patch, create_autospec

from anylearn.applications.quickstart import quick_train, resume_unfinished_local_train_tasks
from anylearn.interfaces import Project, TrainTask, TrainTaskState
from anylearn.interfaces.resource import (
    Algorithm,
    Dataset,
    ResourceState,
    ResourceVisibility,
)
from anylearn.utils.errors import (
    AnyLearnException,
    AnyLearnNotSupportedException,
)
from tests.base_test_case import BaseTestCase


FAKE_ALGO_OK = Path(__file__).parent / "fake_algo_ok"
FAKE_ALGO_KO = Path(__file__).parent / "fake_algo_ko"
FAKE_DSET = Path(__file__).parent / "fake_dset"


class TestQuickTrain(BaseTestCase):
    @patch('anylearn.interfaces.resource.resource_uploader.ResourceUploader')
    @responses.activate
    def test_quick_train_ok(self, MockResourceUploader):
        @create_autospec
        def mock_upload_ok(resource_id, chunks):
            return True

        # Mock uploader with stubbed upload function
        uploader = MockResourceUploader()
        uploader.run = mock_upload_ok

        # Stub mirror list
        responses.add(responses.GET, url=self._url("mirror/list"),
                      json=[
                          {
                              'id': "MIRR001",
                              'name': "Test001",
                              'requirements': "test==0.0.1",
                          },
                          {
                              'id': "MIRR002",
                              'name': "QUICKSTART",
                              'requirements': "test==0.0.2",
                          },
                      ],
                      status=200)
        # Stub algo creation
        responses.add(responses.POST, url=self._url("algorithm/add"),
                      json={'data': "ALGO001", 'message': "算法添加成功"},
                      status=200)
        # Stub dset creation
        responses.add(responses.POST, url=self._url("dataset/add"),
                      json={'data': "DSET001", 'message': "数据集添加成功"},
                      status=200)
        # Stub project creation
        responses.add(responses.POST, url=self._url("project/add"),
                      json={'data': "PROJ001", 'message': "项目添加成功"},
                      status=200)
        # Stub algo upload finish
        responses.add(responses.POST, url=self._url("resource/upload_finish"),
                      json={
                          'msg': "上传已完成，稍后可查看上传结果"
                      },
                      status=200)
        # Stub dset upload finish
        responses.add(responses.POST, url=self._url("resource/upload_finish"),
                      json={
                          'msg': "上传已完成，稍后可查看上传结果"
                      },
                      status=200)
        # Stub algo query
        responses.add(responses.GET, url=self._url("algorithm/query?id=ALGO001"),
                      match_querystring=True, json=[{
                          'id': "ALGO001",
                          'name': "TestAlgo1",
                          'description': "test",
                          'state': ResourceState.READY,
                          'visibility': ResourceVisibility.PUBLIC,
                          'upload_time': "2020-01-01 00:00",
                          'filename': "buzhongyao",
                          'is_zipfile': 1,
                          'file': "USER001/algos/ALGO001/buzhongyao",
                          'size': 250.41,
                          'creator_id': "USER001",
                          'node_id': "NODE001",
                          'owner': ["USER001"],
                          'tags': "tag1, tag2",
                          'train_params': '[{"test": "test"}]',
                          'evaluate_params': '[{"test": "test"}]',
                          'mirror_id': "MIRR002",
                          'follows_anylearn_norm': False,
                          'entrypoint_training': "python train.py",
                          'output_training': "output",
                          'entrypoint_evaluation': "python eval.py",
                          'output_evaluation': "output",
                          'git_address': "http://anylearn.testing/anylearn/TestAlgo1.git",
                          'git_migrated': True,
                      }],
                      status=200)
        # Stub dset query
        responses.add(responses.GET, url=self._url("dataset/query?id=DSET001"),
                      match_querystring=True, json=[{
                          'id': "DSET001",
                          'name': "TestDset1",
                          'description': "test",
                          'state': ResourceState.READY,
                          'visibility': ResourceVisibility.PUBLIC,
                          'upload_time': "2020-01-01 00:00",
                          'filename': "buzhongyao",
                          'is_zipfile': 1,
                          'file': "USER001/datasets/DSET001/buzhongyao",
                          'size': 250.41,
                          'creator_id': "USER001",
                          'node_id': "NODE001",
                          'owner': ["USER001"],
                      }],
                      status=200)
        # Stub train task creation
        responses.add(responses.POST, url=self._url("train_task/add"),
                      json={'data': "TRAI001", 'message': "服务添加成功"},
                      status=200)
        # Stub train task query
        responses.add(responses.GET, url=self._url("train_task/query?id=TRAI001"),
                      match_querystring=True, json=[{
                          'id': "TRAI001",
                          'name': "TestTrainTask1",
                          'description': "test",
                          'state': TrainTaskState.RUNNING,
                          'visibility': 2,
                          'creator_id': "USER001",
                          'owner': ["USER001"],
                          'project_id': "PROJ001",
                          'algorithm_id': "ALGO001",
                          'algorithm_git_ref': 'master',
                          'args': "{\"arg1\":1, \"arg2\":\"test\"}",
                          'files': "DSET001",
                          'results_id': "FILE001",
                          'secret_key': "SECRET",
                          'create_time': "2021-03-01 23:59:59",
                          'finish_time': "",
                          'envs': "",
                          'resource_request': '[{"default": {"CPU": 1}}]',
                      }],
                      status=200)

        train_task, algo, dset, project = quick_train(
            algorithm_dir=FAKE_ALGO_OK,
            dataset_dir=FAKE_DSET,
            entrypoint="python main.py",
            output="output",
            resource_uploader=uploader,
            resource_polling=0.1,
            dataset_hyperparam_name="dataset",
            hyperparams={'test_param': "test"}
        )
        
        self.assertIsInstance(train_task, TrainTask)
        self.assertEqual(train_task.id, "TRAI001")
        self.assertTrue((FAKE_ALGO_OK / "anylearn_tools.py").exists())
        self.assertIsInstance(algo, Algorithm)
        self.assertEqual(algo.id, "ALGO001")
        self.assertIsInstance(dset, Dataset)
        self.assertEqual(dset.id, "DSET001")
        self.assertIsInstance(project, Project)
        self.assertEqual(project.id, "PROJ001")

    def test_quick_train_ko_algo_missing_requirements_txt(self):
        with self.assertRaises(AnyLearnException) as ctx:
            train_task = quick_train(algorithm_dir=FAKE_ALGO_KO,
                                     dataset_dir=FAKE_DSET,
                                     entrypoint="python main.py",
                                     output="output")
        e = ctx.exception
        self.assertIsInstance(e, AnyLearnException)
        self.assertEqual(e.msg, "Missing 'requirements.txt' in algorithm directory")

    @responses.activate
    def test_quick_train_ko_mirror_not_found(self):
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
        with self.assertRaises(AnyLearnNotSupportedException) as ctx:
            train_task = quick_train(algorithm_dir=FAKE_ALGO_OK,
                                     dataset_dir=FAKE_DSET,
                                     entrypoint="python main.py",
                                     output="output",
                                     mirror_name="QUICKSTART")
        e = ctx.exception
        self.assertIsInstance(e, AnyLearnNotSupportedException)
        self.assertEqual(e.msg, "Container for `QUICKSTART` is not supported by the connected backend.")

    @patch('anylearn.interfaces.resource.resource_uploader.ResourceUploader')
    @responses.activate
    def test_quick_train_ko_algo_on_error(self, MockResourceUploader):
        @create_autospec
        def mock_upload_ok(resource_id, chunks):
            return True

        # Mock uploader with stubbed upload function
        uploader = MockResourceUploader()
        uploader.run = mock_upload_ok

        # Stub mirror list
        responses.add(responses.GET, url=self._url("mirror/list"),
                      json=[
                          {
                              'id': "MIRR001",
                              'name': "Test001",
                              'requirements': "test==0.0.1",
                          },
                          {
                              'id': "MIRR002",
                              'name': "QUICKSTART",
                              'requirements': "test==0.0.2",
                          },
                      ],
                      status=200)
        # Stub algo creation
        responses.add(responses.POST, url=self._url("algorithm/add"),
                      json={'data': "ALGO250", 'message': "算法添加成功"},
                      status=200)
        # Stub dset creation
        responses.add(responses.POST, url=self._url("dataset/add"),
                      json={'data': "DSET001", 'message': "数据集添加成功"},
                      status=200)
        # Stub project creation
        responses.add(responses.POST, url=self._url("project/add"),
                      json={'data': "PROJ001", 'message': "项目添加成功"},
                      status=200)
        # Stub algo upload finish
        responses.add(responses.POST, url=self._url("resource/upload_finish"),
                      json={
                          'msg': "上传已完成，稍后可查看上传结果"
                      },
                      status=200)
        # Stub dset upload finish
        responses.add(responses.POST, url=self._url("resource/upload_finish"),
                      json={
                          'msg': "上传已完成，稍后可查看上传结果"
                      },
                      status=200)
        # Stub algo query
        responses.add(responses.GET, url=self._url("algorithm/query?id=ALGO250"),
                      match_querystring=True, json=[{
                          'id': "ALGO250",
                          'name': "TestAlgo1",
                          'description': "test",
                          'state': ResourceState.ERROR,
                          'visibility': ResourceVisibility.PUBLIC,
                          'upload_time': "2020-01-01 00:00",
                          'filename': "buzhongyao",
                          'is_zipfile': 1,
                          'file': "USER001/algos/ALGO250/buzhongyao",
                          'size': 250.41,
                          'creator_id': "USER001",
                          'node_id': "NODE001",
                          'owner': ["USER001"],
                          'tags': "tag1, tag2",
                          'train_params': '[{"test": "test"}]',
                          'evaluate_params': '[{"test": "test"}]',
                          'mirror_id': "MIRR002",
                          'follows_anylearn_norm': False,
                          'entrypoint_training': "python train.py",
                          'output_training': "output",
                          'entrypoint_evaluation': "python eval.py",
                          'output_evaluation': "output",
                          'git_address': "http://anylearn.testing/anylearn/TestAlgo1.git",
                          'git_migrated': True,
                      }],
                      status=200)
        # Stub dset query
        responses.add(responses.GET, url=self._url("dataset/query?id=DSET001"),
                      match_querystring=True, json=[{
                          'id': "DSET001",
                          'name': "TestDset1",
                          'description': "test",
                          'state': ResourceState.READY,
                          'visibility': ResourceVisibility.PUBLIC,
                          'upload_time': "2020-01-01 00:00",
                          'filename': "buzhongyao",
                          'is_zipfile': 1,
                          'file': "USER001/datasets/DSET001/buzhongyao",
                          'size': 250.41,
                          'creator_id': "USER001",
                          'node_id': "NODE001",
                          'owner': ["USER001"],
                      }],
                      status=200)

        with self.assertRaises(AnyLearnException) as ctx:
            train_task = quick_train(algorithm_dir=FAKE_ALGO_OK,
                                     dataset_dir=FAKE_DSET,
                                     entrypoint="python main.py",
                                     output="output",
                                     resource_uploader=uploader,
                                     resource_polling=0.1)
        e = ctx.exception
        self.assertIsInstance(e, AnyLearnException)
        self.assertEqual(e.msg, "An error occured when uploading algorithm")

    @patch('anylearn.interfaces.resource.resource_uploader.ResourceUploader')
    @responses.activate
    def test_quick_train_ko_dset_on_error(self, MockResourceUploader):
        @create_autospec
        def mock_upload_ok(resource_id, chunks):
            return True

        # Mock uploader with stubbed upload function
        uploader = MockResourceUploader()
        uploader.run = mock_upload_ok

        # Stub mirror list
        responses.add(responses.GET, url=self._url("mirror/list"),
                      json=[
                          {
                              'id': "MIRR001",
                              'name': "Test001",
                              'requirements': "test==0.0.1",
                          },
                          {
                              'id': "MIRR002",
                              'name': "QUICKSTART",
                              'requirements': "test==0.0.2",
                          },
                      ],
                      status=200)
        # Stub algo creation
        responses.add(responses.POST, url=self._url("algorithm/add"),
                      json={'data': "ALGO001", 'message': "算法添加成功"},
                      status=200)
        # Stub dset creation
        responses.add(responses.POST, url=self._url("dataset/add"),
                      json={'data': "DSET250", 'message': "数据集添加成功"},
                      status=200)
        # Stub project creation
        responses.add(responses.POST, url=self._url("project/add"),
                      json={'data': "PROJ001", 'message': "项目添加成功"},
                      status=200)
        # Stub algo upload finish
        responses.add(responses.POST, url=self._url("resource/upload_finish"),
                      json={
                          'msg': "上传已完成，稍后可查看上传结果"
                      },
                      status=200)
        # Stub dset upload finish
        responses.add(responses.POST, url=self._url("resource/upload_finish"),
                      json={
                          'msg': "上传已完成，稍后可查看上传结果"
                      },
                      status=200)
        # Stub algo query
        responses.add(responses.GET, url=self._url("algorithm/query?id=ALGO001"),
                      match_querystring=True, json=[{
                          'id': "ALGO001",
                          'name': "TestAlgo1",
                          'description': "test",
                          'state': ResourceState.READY,
                          'visibility': ResourceVisibility.PUBLIC,
                          'upload_time': "2020-01-01 00:00",
                          'filename': "buzhongyao",
                          'is_zipfile': 1,
                          'file': "USER001/algos/ALGO001/buzhongyao",
                          'size': 250.41,
                          'creator_id': "USER001",
                          'node_id': "NODE001",
                          'owner': ["USER001"],
                          'tags': "tag1, tag2",
                          'train_params': '[{"test": "test"}]',
                          'evaluate_params': '[{"test": "test"}]',
                          'mirror_id': "MIRR002",
                          'follows_anylearn_norm': False,
                          'entrypoint_training': "python train.py",
                          'output_training': "output",
                          'entrypoint_evaluation': "python eval.py",
                          'output_evaluation': "output",
                          'git_address': "http://anylearn.testing/anylearn/TestAlgo1.git",
                          'git_migrated': True,
                      }],
                      status=200)
        # Stub dset query
        responses.add(responses.GET, url=self._url("dataset/query?id=DSET250"),
                      match_querystring=True, json=[{
                          'id': "DSET250",
                          'name': "TestDset1",
                          'description': "test",
                          'state': ResourceState.ERROR,
                          'visibility': ResourceVisibility.PUBLIC,
                          'upload_time': "2020-01-01 00:00",
                          'filename': "buzhongyao",
                          'is_zipfile': 1,
                          'file': "USER001/datasets/DSET250/buzhongyao",
                          'size': 250.41,
                          'creator_id': "USER001",
                          'node_id': "NODE001",
                          'owner': ["USER001"],
                      }],
                      status=200)

        with self.assertRaises(AnyLearnException) as ctx:
            train_task = quick_train(algorithm_dir=FAKE_ALGO_OK,
                                     dataset_dir=FAKE_DSET,
                                     entrypoint="python main.py",
                                     output="output",
                                     resource_uploader=uploader,
                                     resource_polling=0.1)
        e = ctx.exception
        self.assertIsInstance(e, AnyLearnException)
        self.assertEqual(e.msg, "Error occured when uploading dataset")

    @responses.activate
    def test_update_local_train_task(self):
        responses.add(responses.GET, url=self._url("train_task/query?id=TRAI000"),
                match_querystring=True, json=[{
                    'id': "TRAI000",
                    'name': "TestTrainTask1",
                    'description': "test",
                    'state': TrainTaskState.FAIL,
                    'visibility': 2,
                    'creator_id': "USER001",
                    'owner': ["USER001"],
                    'project_id': "PROJ001",
                    'algorithm_id': "ALGO001",
                    'args': "{\"arg1\":1, \"arg2\":\"test\"}",
                    'files': "DSET001",
                    'results_id': "FILE001",
                    'secret_key': "SECRET",
                    'create_time': "2021-03-01 23:59:59",
                    'finish_time': "",
                    'envs': "",
                    'gpu_num': 1,
                }],
                status=200)

        responses.add(responses.GET, url=self._url("train_task/query?id=TRAI001"),
                match_querystring=True, json=[{
                    'id': "TRAI001",
                    'name': "TestTrainTask1",
                    'description': "test",
                    'state': TrainTaskState.ABORT,
                    'visibility': 2,
                    'creator_id': "USER001",
                    'owner': ["USER001"],
                    'project_id': "PROJ001",
                    'algorithm_id': "ALGO001",
                    'args': "{\"arg1\":1, \"arg2\":\"test\"}",
                    'files': "DSET001",
                    'results_id': "FILE001",
                    'secret_key': "SECRET",
                    'create_time': "2021-03-01 23:59:59",
                    'finish_time': "",
                    'envs': "",
                    'gpu_num': 1,
                }],
                status=200)

        responses.add(responses.GET, url=self._url("train_task/query?id=TRAI002"),
                match_querystring=True, json=[{
                    'id': "TRAI002",
                    'name': "TestTrainTask1",
                    'description': "test",
                    'state': TrainTaskState.SUCCESS,
                    'visibility': 2,
                    'creator_id': "USER001",
                    'owner': ["USER001"],
                    'project_id': "PROJ001",
                    'algorithm_id': "ALGO001",
                    'args': "{\"arg1\":1, \"arg2\":\"test\"}",
                    'files': "DSET001",
                    'results_id': "FILE001",
                    'secret_key': "SECRET",
                    'create_time': "2021-03-01 23:59:59",
                    'finish_time': "",
                    'envs': "",
                    'gpu_num': 1,
                }],
                status=200)
 
        task_list = resume_unfinished_local_train_tasks()
        if len(task_list):
            self.assertIsInstance(task_list[0], TrainTask)
            self.assertEqual((task_list[0]).id, "TRAI001")
            self.assertEqual(task_list[0].state, -3)
