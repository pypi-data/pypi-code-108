from requests.exceptions import RequestException
import responses

from anylearn.interfaces.user import User
from anylearn.utils.errors import AnyLearnException, AnyLearnMissingParamException
from tests.base_test_case import BaseTestCase


class TestUser(BaseTestCase):
    @responses.activate
    def test_create_user_ok(self):
        responses.add(responses.POST, url=self._url("user/registry"),
                      json={'data': "USER123", 'message': "用户添加成功"},
                      status=200)
        user = User(username="test_username",
                    password="123456", email="123@abc.com")
        res = user.save()
        self.assertTrue(res, True)

    def test_create_user_empty_username_password_email(self):
        user = User()
        with self.assertRaises(AnyLearnMissingParamException) as ctx:
            user.save()
        e = ctx.exception
        self.assertIsInstance(e, AnyLearnMissingParamException)
        self.assertEqual(e.msg, "User缺少必要字段：['username', 'password', 'email']")

    @responses.activate
    def test_create_user_unknown_response(self):
        responses.add(responses.POST, url=self._url("user/registry"),
                      json={'msg': "Unknown response"}, status=201)
        user = User(username="test_username",
                    password="123456", email="abc@123.com")
        with self.assertRaises(AnyLearnException) as ctx:
            user.save()
        e = ctx.exception
        self.assertIsInstance(e, AnyLearnException)
        self.assertEqual(e.msg, "请求未能得到有效响应")

    @responses.activate
    def test_get_user_detail_explicit_call_ok(self):
        responses.add(responses.GET, url=self._url("user?id=USER123"),
                      match_querystring=True,
                      json=[
                          {
                              "collected_algorithm": "[]",
                              "email": "123@abc.com",
                              "id": "USER123",
                              "namespace": "xln111",
                              "own_algorithms": [
                                  "ALGO1",
                                  "ALGO2",
                                  "ALGO3"
                              ],
                              "own_datasets": [
                                  "DSET1",
                                  "DSET2",
                                  "DSET3"
                              ],
                              "own_files": [
                                  "FILE1",
                                  "FILE2",
                                  "FILE3"
                              ],
                              "own_models": [
                                  "MODE1",
                                  "MODE2",
                                  "MODE3"
                              ],
                              "role": "admin,user",
                              "username": "xlearn"
                          }
                        ],
                    status=200)
        user = User(id="USER123")
        user.get_detail()
        self.assertIsInstance(user.own_datasets, list)
        if isinstance(user.own_datasets, list):
            self.assertEqual(len(user.own_datasets), 3)
        self.assertEqual(user.own_datasets[0], "DSET1")
        self.assertEqual(user.id, "USER123")
        self.assertEqual(user.role, "admin,user")
        self.assertEqual(user.email, "123@abc.com")
        self.assertEqual(user.username, "xlearn")

    @responses.activate
    def test_get_user_detail_no_explicit_call_ok(self):
        responses.add(responses.GET, url=self._url("user?id=USER123"),
                      match_querystring=True,
                      json=[
                          {
                              "collected_algorithm": "[]",
                              "email": "123@abc.com",
                              "id": "USER123",
                              "namespace": "xln111",
                              "own_algorithms": [
                                  "ALGO1",
                                  "ALGO2",
                                  "ALGO3"
                              ],
                              "own_datasets": [
                                  "DSET1",
                                  "DSET2",
                                  "DSET3"
                              ],
                              "own_files": [
                                  "FILE1",
                                  "FILE2",
                                  "FILE3"
                              ],
                              "own_models": [
                                  "MODE1",
                                  "MODE2",
                                  "MODE3"
                              ],
                              "role": "admin,user",
                              "username": "xlearn"
                          }
                        ],
                      status=200)
        user = User(id="USER123", load_detail=True)
        self.assertIsInstance(user.own_datasets, list)
        if isinstance(user.own_datasets, list):
            self.assertEqual(len(user.own_datasets), 3)
        self.assertEqual(user.id, "USER123")
        self.assertEqual(user.role, "admin,user")
        self.assertEqual(user.email, "123@abc.com")
        self.assertEqual(user.username, "xlearn")

    @responses.activate
    def test_get_user_detail_ko_403(self):
        responses.add(responses.GET, url=self._url("user?id=USER403"),
                      match_querystring=True, status=403)
        user = User(id="USER403")
        with self.assertRaises(RequestException) as ctx:
            user.get_detail()
        e = ctx.exception
        self.assertIsInstance(e, RequestException)
        self.assertEqual(e.response.status_code, 403)

    @responses.activate
    def test_get_user_detail_ko_unknown_response(self):
        responses.add(responses.GET, url=self._url("user?id=USER250"),
                      match_querystring=True, json={'msg': "Unknown response"},
                      status=200)
        user = User(id="USER250")
        with self.assertRaises(AnyLearnException) as ctx:
            user.get_detail()
        e = ctx.exception
        self.assertIsInstance(e, AnyLearnException)
        self.assertEqual(e.msg, "请求未能得到有效响应")

    @responses.activate
    def test_get_user_detail_empty_list(self):
        responses.add(responses.GET, url=self._url("user?id=USER250"),
                      match_querystring=True, json=[],
                      status=200)
        user = User(id="USER250")
        with self.assertRaises(AnyLearnException) as ctx:
            user.get_detail()
        e = ctx.exception
        self.assertIsInstance(e, AnyLearnException)
        self.assertEqual(e.msg, "请求未能得到有效响应")

    @responses.activate
    def test_change_password_ok(self):
        responses.add(responses.PUT, url=self._url("user/password"),
                      json={'data': "USER123", 'message': "密码修改成功"},
                      status=200)
        user = User(id="USER123")
        res = user.change_password("old_password", "new_password")
        self.assertEqual(res['data'], "USER123")

    def test_change_password_empty_id(self):
        user = User()
        with self.assertRaises(AnyLearnMissingParamException) as ctx:
            user.change_password("old_password", "new_password")
        e = ctx.exception
        self.assertIsInstance(e, AnyLearnMissingParamException)
        self.assertEqual(e.msg, "User缺少必要字段：['id']")

    @responses.activate
    def test_change_password_unknown_response(self):
        responses.add(responses.PUT, url=self._url("user/password"),
                      json={'msg': "Unknown response"}, status=201)
        user = User(id="USER123")
        with self.assertRaises(AnyLearnException) as ctx:
            user.change_password("old_password", "new_password")
        e = ctx.exception
        self.assertIsInstance(e, AnyLearnException)
        self.assertEqual(e.msg, "请求未能得到有效响应")

    @responses.activate
    def test_list_user_ok(self):
        responses.add(responses.GET, url=self._url("user/list"),
                      json=[
                          {
                              'id': "USER001",
                              'username': "TestUser1",
                              'email': "123@abc.com",
                              'role': "user",
                          },
                          {
                              'id': "USER002",
                              'username': "TestUser2",
                              'email': "456@abc.com",
                              'role': "user2",
                          },
                        ],
                      status=200)
        users = User.get_list()
        self.assertIsInstance(users, list)
        self.assertEqual(len(users), 2)
        self.assertIsInstance(users[0], User)
        self.assertIsInstance(users[1], User)
        self.assertEqual(users[0].id, "USER001")
        self.assertEqual(users[1].id, "USER002")

    @responses.activate
    def test_list_user_ko_unknown_response(self):
        responses.add(responses.GET, url=self._url("user/list"),
                      json={'msg': "Unknown response"},
                      status=200)
        with self.assertRaises(AnyLearnException) as ctx:
            User.get_list()
        e = ctx.exception
        self.assertIsInstance(e, AnyLearnException)
        self.assertEqual(e.msg, "请求未能得到有效响应")

    @responses.activate
    def test_user_collection_ok(self):
        responses.add(responses.GET, url=self._url("user/collection?collection=USER001,USER002"),
                      match_querystring=True,
                      json=[
                          {
                              'id': "USER001",
                              'role': "user1",
                              'email': "123@abc.com",
                              'username': "xlearn1"
                          },
                          {
                              'id': "USER002",
                              'role': "user2",
                              'email': "456@abc.com",
                              'username': "xlearn2"
                          }
                        ],
                      status=200)
        users = User.user_collection("USER001,USER002")
        self.assertIsInstance(users, list)
        self.assertEqual(len(users), 2)
        self.assertIsInstance(users[0], User)
        self.assertIsInstance(users[1], User)
        self.assertEqual(users[0].id, "USER001")
        self.assertEqual(users[1].id, "USER002")

    @responses.activate
    def test_user_collection_ko_403(self):
        responses.add(responses.GET, url=self._url("user/collection?collection=USER403"),
                      match_querystring=True, status=403)
        with self.assertRaises(RequestException) as ctx:
            User.user_collection("USER403")
        e = ctx.exception
        self.assertIsInstance(e, RequestException)
        self.assertEqual(e.response.status_code, 403)

    @responses.activate
    def test_user_collection_ko_unknown_response(self):
        responses.add(responses.GET, url=self._url("user/collection?collection=USER250"),
                      match_querystring=True, json={'msg': "Unknown response"},
                      status=200)
        with self.assertRaises(AnyLearnException) as ctx:
            User.user_collection("USER250")
        e = ctx.exception
        self.assertIsInstance(e, AnyLearnException)
        self.assertEqual(e.msg, "请求未能得到有效响应")

    @responses.activate
    def test_user_update_ok(self):
        responses.add(responses.PUT, url=self._url("user"),
                      json={'data': "USER123", 'message': "用户信息修改成功"},
                      status=200)
        user = User(id="USER123", username="test",
                    email="123@abc.com", role="user")
        res = user.save()
        self.assertTrue(res)

    @responses.activate
    def test_user_update_unknown_response(self):
        responses.add(responses.PUT, url=self._url("user"),
                      json={'msg': "Unknown response"}, status=201)
        user = User(id="USER201", username="test",
                    email="123@abc.com", role="user")
        with self.assertRaises(AnyLearnException) as ctx:
            user.save()
        e = ctx.exception
        self.assertIsInstance(e, AnyLearnException)
        self.assertEqual(e.msg, "请求未能得到有效响应")

    @responses.activate
    def test_user_delete_ok(self):
        responses.add(responses.DELETE, url=self._url("user"),
                      json={'data': "USER123", 'message': "用户删除成功"},
                      status=200)
        user = User(id="USER123")
        res = user.delete()
        self.assertTrue(res)

    def test_user_delete_empty_id(self):
        user = User()
        with self.assertRaises(AnyLearnMissingParamException) as ctx:
            user.delete()
        e = ctx.exception
        self.assertIsInstance(e, AnyLearnMissingParamException)
        self.assertEqual(e.msg, "User缺少必要字段：['id']")

    @responses.activate
    def test_user_delete_unknown_response(self):
        responses.add(responses.DELETE, url=self._url("user"),
                      json={'msg': "Unknown response"}, status=201)
        user = User(id="USER201")
        with self.assertRaises(AnyLearnException) as ctx:
            user.delete()
        e = ctx.exception
        self.assertIsInstance(e, AnyLearnException)
        self.assertEqual(e.msg, "请求未能得到有效响应")

    @responses.activate
    def test_user_check_ok(self):
        responses.add(responses.GET, url=self._url("user/check"),
                      json=True,
                      status=200)
        res = User.user_check(username="test")
        self.assertIsInstance(res,bool)
        self.assertEqual(res, True)

    def test_user_check_empty_username(self):
        with self.assertRaises(AnyLearnException) as ctx:
            User.user_check(username="")
        e = ctx.exception
        self.assertIsInstance(e, AnyLearnException)
        self.assertEqual(e.msg, "username值不能为空")

    @responses.activate
    def test_user_check_unknown_response(self):
        responses.add(responses.GET, url=self._url("user/check"),
                      json={'msg': "Unknown response"}, status=201)
        with self.assertRaises(AnyLearnException) as ctx:
            User.user_check(username="username201")
        e = ctx.exception
        self.assertIsInstance(e, AnyLearnException)
        self.assertEqual(e.msg, "请求未能得到有效响应")

    @responses.activate
    def test_update_role_resource_count_ok(self):
        responses.add(responses.PUT, url=self._url("user/role"),
                      json={'msg': "user角色最大GPU和显存数量已分别成功设置为2,26"},
                      status=200)
        res = User.update_role_resource_count(max_gpu=2, max_mem=26)
        self.assertEqual(res['msg'], "user角色最大GPU和显存数量已分别成功设置为2,26")

    @responses.activate
    def test_update_role_resource_count_unknown_response(self):
        responses.add(responses.PUT, url=self._url("user/role"),
                      json={'msg': "Unknown response"}, status=201)
        with self.assertRaises(AnyLearnException) as ctx:
            User.update_role_resource_count(max_gpu=2, max_mem=26)
        e = ctx.exception
        self.assertIsInstance(e, AnyLearnException)
        self.assertEqual(e.msg, "请求未能得到有效响应")

    @responses.activate
    def test_update_user_resource_count_ok(self):
        responses.add(responses.PATCH, url=self._url("user/user"),
                      json={'data': "USER123",
                            'msg': "用户最大GPU和显存数量已分别成功设置为3,18"},
                      status=200)
        res = User.update_user_resource_count(
            id="USER123", max_gpu=3, max_mem=18)
        self.assertEqual(res['data'], "USER123")

    @responses.activate
    def test_update_user_resource_count_unknown_response(self):
        responses.add(responses.PATCH, url=self._url("user/user"),
                      json={'msg': "Unknown response"}, status=201)
        with self.assertRaises(AnyLearnException) as ctx:
            User.update_user_resource_count(
                id="USER123", max_gpu=3, max_mem=18)
        e = ctx.exception
        self.assertIsInstance(e, AnyLearnException)
        self.assertEqual(e.msg, "请求未能得到有效响应")
