# coding=utf-8
import json
from time import time
from tornado import gen, ioloop
from tornado.httpclient import AsyncHTTPClient, HTTPError


JSON_HEADER = {'content-type': 'application/json'}

def get_async_client():
    return AsyncHTTPClient()


def parse_appkey(appkey):
    """解析appkey, 从中得到org和app, 注意, appkey的规则是 {org}#{app}"""
    return tuple(appkey.split('#'))


class Token:
    """表示一个登陆获取到的token对象"""

    def __init__(self, token, exipres_in):
        self.token = token
        self.exipres_in = exipres_in + int(time())

    def is_not_valid(self):
        """这个token是否还合法, 或者说, 是否已经失效了, 这里我们只需要
        检查当前的时间, 是否已经比或者这个token的时间过去了exipreis_in秒

        即  current_time_in_seconds < (expires_in + token_acquired_time)
        """
        return time() > self.exipres_in


class EasemobAuth(object):
    """环信登陆认证的基类"""

    @gen.coroutine
    def get_headers(self):
        token = yield self.get_token()
        headers = {'Authorization': 'Bearer ' + token,
                   'content-type': 'application/json'}

        raise gen.Return(headers)

    @gen.coroutine
    def get_token(self):
        """在这里我们先检查是否已经获取过token, 并且这个token有没有过期"""
        if (self.token is None) or (self.token.is_not_valid()):
            self.token = yield self.acquire_token()  # refresh the token
        raise gen.Return(self.token.token)

    @gen.coroutine
    def acquire_token(self):
        """真正的获取token的方法, 返回值是一个我们定义的Token对象
            这个留给子类去实现
        """
        pass


class AppClientAuth(EasemobAuth):
    """使用app的client_id和client_secret来获取app管理员token"""

    def __init__(self, org, app, client_id, client_secret, host):
        super(AppClientAuth, self).__init__()
        self.client_id = client_id
        self.client_secret = client_secret
        self.url = host + ("/%s/%s/token" % (org, app))
        self.token = None

    @gen.coroutine
    def acquire_token(self):
        """
        使用clieng_id / client_secret来获取token, 具体的REST API为

        POST /{org}/{app}/token {'grant_type':'client_credentials', 'client_id':'xxxx', 'client_secret':'xxxxx'}
        """
        payload = {'grant_type': 'client_credentials', 'client_id': self.client_id, 'client_secret': self.client_secret}
        response = yield get_async_client().fetch(self.url, method='POST', body=json.dumps(payload))
        if response.code == 200:
            result = json.loads(response.body)
            raise gen.Return(Token(result['access_token'], result['expires_in']))
        else:
            pass


class AppAdminAccountAuth(EasemobAuth):
    """使用app的管理员账号和密码来获取token"""

    def __init__(self, org, app, username, password, host):
        super(AppAdminAccountAuth, self).__init__()
        self.username = username
        self.password = password
        self.url = host + ("/%s/%s/token" % (org, app))
        self.token = None

    @gen.coroutine
    def acquire_token(self):
        """
        使用 username / password 来获取token, 具体的REST API为

        POST /{org}/{app}/token {'grant_type':'password', 'username':'xxxx', 'password':'xxxxx'}

        这里和上面使用client_id不同的是, grant_type的类型是password, 然后还需要提供username和password
        """
        payload = {'grant_type': 'password', 'username': self.username, 'password': self.password}
        response = yield get_async_client().fetch(self.url, method='POST', body=json.dumps(payload))
        if response.code == 200:
            result = json.loads(response.body)
            raise gen.Return(Token(result['access_token'], result['expires_in']))
        else:
            pass


class OrgAdminAccountAuth(EasemobAuth):
    """使用org的管理员账号和密码来获取token,
    和上面不同的是, 这里获取的是整个org的管理员账号,
    所以并没有appkey的概念

    并且, 因为没有appkey的概念, 所以, URL也不相同,
    这里使用的URL是 https://a1.easemob.com/management/token

    而app级别的token都是从 https://a1.easemob.com/{org}/{app}/token
    这个URL去获取的
    """

    def __init__(self, username, password, host):
        super(OrgAdminAccountAuth, self).__init__()
        self.username = username
        self.password = password
        self.url = host + "/management/token"
        self.token = None

    @gen.coroutine
    def acquire_token(self):
        """
        使用 username / password 来获取token, 具体的REST API为

        POST /management/token {'grant_type':'password', 'username':'xxxx', 'password':'xxxxx'}
        """
        payload = {'grant_type': 'password', 'username': self.username, 'password': self.password}
        response = yield get_async_client().fetch(self.url, method='POST', body=json.dumps(payload))
        if response.code == 200:
            result = json.loads(response.body)
            raise gen.Return(Token(result['access_token'], result['expires_in']))
        else:
            pass


class EMChatAsync(object):
    """环信"""

    def __init__(self, **kwargs):
        self.EASEMOB_HOST = kwargs.get("host", "https://a1.easemob.com")
        self.app_client_auth = None
        self.app = kwargs["app"]
        self.org = kwargs["org"]
        self.appkey = self.app + "#" + self.org
        self.org_admin_username = kwargs['username']
        self.org_admin_password = kwargs['password']
        self.client_id = kwargs['client_id']
        self.client_secret = kwargs['client_secret']
        self.app_admin_username = kwargs['username']
        self.app_admin_password = kwargs['password']
        self.PUSH_USER_ID = kwargs.get("push_user_id", "system")
        
    def get_org_admin_auth(self):
        """org_admin的认证方式"""
        return OrgAdminAccountAuth(self.org_admin_username, self.org_admin_password, self.EASEMOB_HOST)

    def get_app_admin_auth(self):
        """org_admin的认证方式"""
        return AppAdminAccountAuth(self.org, self.app, self.app_admin_username, self.app_admin_password, self.EASEMOB_HOST)

    @gen.coroutine
    def get_app_client_headers(self):
        """通过client id和secret来获取app管理员的token"""
        if self.app_client_auth is None:
            self.app_client_auth = AppClientAuth(self.org, self.app, self.client_id, self.client_secret, self.EASEMOB_HOST)

        headers = yield self.app_client_auth.get_headers()
        raise gen.Return(headers)

    @gen.coroutine
    def register_new_user(self, username, password):
        """注册新用户
        """
        data = {"username": username, "password": password}
        url = self.EASEMOB_HOST + ("/%s/%s/users" % (self.org, self.app))
        headers = yield self.get_app_client_headers()

        try:
            response = yield get_async_client().fetch(url,
                                                      method='POST',
                                                      body=json.dumps(data),
                                                      headers=headers)
            if response.code == 200:
                raise gen.Return(response.body)

        except HTTPError as e:
            if e.code == 400:
                # 新增用户、但是用户已经存在了, 不做处理
                if password == "password":
                    raise gen.Return(True)

                # 用户存在, 修改密码
                url = self.EASEMOB_HOST + ("/%s/%s/users/%s/password" % (self.org, self.app, username))
                response = yield get_async_client().fetch(url,
                                                      method='PUT',
                                                      body=json.dumps({"newpassword": password}),
                                                      headers=headers)
                if response.code == 200:
                    raise gen.Return(response.body)

            else:
                # 其他错误
                raise gen.Return(e.response.body)

    @gen.coroutine
    def delete_user(self, username):
        """删除用户
        """
        url = self.EASEMOB_HOST + ("/%s/%s/users/%s" % (self.org, self.app, username))

        headers = yield self.get_app_client_headers()
        response = yield get_async_client().fetch(url,
                                                  method='DELETE',
                                                  headers=headers)
        if response.code == 200:
            raise gen.Return(response.body)

    @gen.coroutine
    def send_file(self, filename):
        """发送文件
        """
        url = self.EASEMOB_HOST + ("/%s/%s/chatfiles" % (self.org, self.app))
        files = {'file': ('report.xls', open(filename, 'rb', encoding='utf-8'), 'image/jpeg', {'Expires': '0'})}

        headers = yield self.get_app_client_headers()
        response = yield get_async_client().fetch(url,
                                                  method='POST',
                                                  body=json.dumps(files),
                                                  headers=headers)
        if response.code == 200:
            raise gen.Return(response.body)

    @gen.coroutine
    def send_msg(self, msg, to_ids, from_user_id=None, ext={}):
        url = self.EASEMOB_HOST + ("/%s/%s/messages" % (self.org, self.app))
        if not isinstance(to_ids, list):
            to_ids = [to_ids]

        data = {"target_type": "users",
                "target": to_ids,
                "msg": {"type": "txt",
                        "msg": msg},
                "from": from_user_id or self.PUSH_USER_ID,
                "ext": ext if isinstance(ext, dict) else json.loads(ext)}

        headers = yield self.get_app_client_headers()
        response = yield get_async_client().fetch(url,
                                                  method='POST',
                                                  body=json.dumps(data),
                                                  headers=headers)
        if response.code == 200:
            raise gen.Return(response.body)

    @gen.coroutine
    def send_ninja_msg(self, msg, to_ids, from_user_id=None, ext={}, target_type="users"):
        url = self.EASEMOB_HOST + ("/%s/%s/messages" % (self.org, self.app))
        if not isinstance(to_ids, list):
            to_ids = [to_ids]

        data = {"target_type": target_type,
                "target": to_ids,
                "msg": {"type": "cmd",
                        "action": msg},
                "from": from_user_id or self.PUSH_USER_ID,
                "ext": ext if isinstance(ext, dict) else json.loads(ext)}
        headers = yield self.get_app_client_headers()
        response = yield get_async_client().fetch(url,
                                                  method='POST',
                                                  body=json.dumps(data),
                                                  headers=headers,
                                                  request_timeout=15)
        if response.code == 200:
            print(str(data).decode('string_escape'))
            raise gen.Return(response.body)


    @gen.coroutine
    def send_loc(self, to_ids, from_user_id=None, addr=None, lat=None, lng=None, ext={}):
        url = self.EASEMOB_HOST + ("/%s/%s/messages" % (self.org, self.app))
        if not isinstance(to_ids, list):
            to_ids = [to_ids]

        data = {"target_type": "users",
                "target": to_ids,
                "msg": {"type": "loc",
                        "addr": addr,
                        "lat": lat,
                        "lng": lng},
                "from": from_user_id or self.PUSH_USER_ID,
                "ext": ext if isinstance(ext, dict) else json.loads(ext)}

        headers = yield self.get_app_client_headers()
        response = yield get_async_client().fetch(url,
                                                  method='POST',
                                                  body=json.dumps(data),
                                                  headers=headers)
        if response.code == 200:
            raise gen.Return(response.body)

    @gen.coroutine
    def send_pic_msg(self, to_ids, from_user_id=None, img_url=None, filename=None, ext={}):
        url = self.EASEMOB_HOST + ("/%s/%s/messages" % (self.org, self.app))
        if not isinstance(to_ids, list):
            to_ids = [to_ids]

        data = {"target_type": "users",
                "target": to_ids,
                "msg": {"type": "img",
                        "url": img_url,
                        "filename": filename,
                        "secret": str(time() * 1000)},
                "from": from_user_id or self.PUSH_USER_ID,
                "ext": ext if isinstance(ext, dict) else json.loads(ext)}

        headers = yield self.get_app_client_headers()
        response = yield get_async_client().fetch(url,
                                                  method='POST',
                                                  body=json.dumps(data),
                                                  headers=headers)
        if response.code == 200:
            raise gen.Return(response.body)

    @gen.coroutine
    def send_audio_msg(self, to_ids, from_user_id=None, img_url=None, filename=None, length=None, ext={}):
        url = self.EASEMOB_HOST + ("/%s/%s/messages" % (self.org, self.app))
        if not isinstance(to_ids, list):
            to_ids = [to_ids]

        data = {"target_type": "users",
                "target": to_ids,
                "msg": {"type": "audio",
                        "url": img_url,
                        "filename": filename,
                        "length": length,
                        "secret": str(time() * 1000)},
                "from": from_user_id or self.PUSH_USER_ID,
                "ext": ext if isinstance(ext, dict) else json.loads(ext)}

        headers = yield self.get_app_client_headers()
        response = yield get_async_client().fetch(url,
                                                  method='POST',
                                                  body=json.dumps(data),
                                                  headers=headers)
        if response.code == 200:
            raise gen.Return(response.body)

    @gen.coroutine
    def send_video_msg(self, to_ids, from_user_id=None, img_url=None, filename=None, length=None, thumb=None, ext={}):
        url = self.EASEMOB_HOST + ("/%s/%s/messages" % (self.org, self.app))
        if not isinstance(to_ids, list):
            to_ids = [to_ids]

        data = {"target_type": "users",
                "target": to_ids,
                "msg": {"type": "video",
                        "url": img_url,
                        "filename": filename,
                        "length": length,
                        "file_length": 1024 * 1024,
                        "secret": str(time() * 1000),
                        "thumb": thumb,
                        "thumb_secret": str(time() * 1000)},
                "from": from_user_id or self.PUSH_USER_ID,
                "ext": ext if isinstance(ext, dict) else json.loads(ext)}

        headers = yield self.get_app_client_headers()
        response = yield get_async_client().fetch(url,
                                                  method='POST',
                                                  body=json.dumps(data),
                                                  headers=headers)
        if response.code == 200:
            raise gen.Return(response.body)

    @gen.coroutine
    def send_group_msg(self, msg, to_ids, from_user_id=None, ext={}):
        url = self.EASEMOB_HOST + ("/%s/%s/messages" % (self.org, self.app))
        if not isinstance(to_ids, list):
            to_ids = [to_ids]

        data = {"target_type": "chatgroups",
                "target": to_ids,
                "msg": {"type": "txt",
                        "msg": msg},
                "from": from_user_id or self.PUSH_USER_ID,
                "ext": ext if isinstance(ext, dict) else json.loads(ext)}

        headers = yield self.get_app_client_headers()
        response = yield get_async_client().fetch(url,
                                                  method='POST',
                                                  body=json.dumps(data),
                                                  headers=headers)
        if response.code == 200:
            raise gen.Return(response.body)


    @gen.coroutine
    def block_users(self, from_user_id, to_ids):

        url = self.EASEMOB_HOST + ("/%s/%s/users/%s/blocks/users" % (self.org, self.app, from_user_id))

        if not isinstance(to_ids, list):
            to_ids = [to_ids]

        data = {"usernames": to_ids}

        headers = yield self.get_app_client_headers()
        try:
            response = yield get_async_client().fetch(url,
                                                      method='POST',
                                                      body=json.dumps(data),
                                                      headers=headers)
            if response.code == 200:
                raise gen.Return(response.body)
        except HTTPError as e:
            print(e)
            raise gen.Return(False)

    @gen.coroutine
    def unblock_user(self, from_user_id, to_user_id):
        url = self.EASEMOB_HOST + ("/%s/%s/users/%s/blocks/users/%s" % (self.org, self.app, from_user_id, to_user_id))
        headers = yield self.get_app_client_headers()
        response = yield get_async_client().fetch(url,
                                                  method='DELETE',
                                                  headers=headers)
        if response.code == 200:
            raise gen.Return(response.body)


    @gen.coroutine
    def create_chat_group(self, kwargs):
        """创建群， 如果创建者没有在环信注册，则先注册用户"""
        url = self.EASEMOB_HOST + ("/%s/%s/chatgroups" % (self.org, self.app))
        headers = yield self.get_app_client_headers()

        try:
            response = yield get_async_client().fetch(url,
                                                      method='POST',
                                                      headers=headers,
                                                      body=json.dumps(kwargs))
            if response.code == 200:
                raise gen.Return(response.body)
        except HTTPError as e:
            print(e.code, e.response.body)



    @gen.coroutine
    def modify_chat_group(self, gid, kwargs):
        """修改群资料"""
        url = self.EASEMOB_HOST + ("/%s/%s/chatgroups/%d" % (self.org, self.app, gid))
        headers = yield self.get_app_client_headers()
        response = yield get_async_client().fetch(url,
                                                  method='PUT',
                                                  headers=headers,
                                                  body=json.dumps(kwargs))
        if response.code == 200:
            raise gen.Return(response.body)

    @gen.coroutine
    def delete_chat_group(self, gid):
        """解散群"""
        url = self.EASEMOB_HOST + ("/%s/%s/chatgroups/%s" % (self.org, self.app, gid))
        headers = yield self.get_app_client_headers()
        response = yield get_async_client().fetch(url,
                                                  method='DELETE',
                                                  headers=headers)
        if response.code == 200:
            raise gen.Return(response.body)

    @gen.coroutine
    def group_add_member(self, gid, user_id):
        """群添加成员"""
        url = self.EASEMOB_HOST + ("/%s/%s/chatgroups/%d/users/%s" % (self.org, self.app, gid, user_id))
        headers = yield self.get_app_client_headers()
        response = yield get_async_client().fetch(url,
                                                  method='POST',
                                                  headers=headers,
                                                  body="")

        if response.code == 200:
            raise gen.Return(response.body)
        else:
        #     yield self.register_new_user(user_id, md5(user_id + generate_access_token(user_id)).hexdigest())
            raise gen.Return(None)

    @gen.coroutine
    def group_delete_member(self, gid, user_id):
        """群减少成员"""

        url = self.EASEMOB_HOST + ("/%s/%s/chatgroups/%d/users/%s" % (self.org, self.app, gid, user_id))
        headers = yield self.get_app_client_headers()
        response = yield get_async_client().fetch(url,
                                                  method='DELETE',
                                                  headers=headers)
        if response.code == 200:
            raise gen.Return(response.body)


    @gen.coroutine
    def get_chatmessages(self, arg):
        url = self.EASEMOB_HOST + ("/%s/%s/chatmessages?%s" % (self.org, self.app, arg))
        try:
            headers = yield self.get_app_client_headers()
            response = yield get_async_client().fetch(url,
                                                      method='GET',
                                                      headers=headers)
            raise gen.Return(response.body)
        except HTTPError as e:
            raise gen.Return("faild")

    @gen.coroutine
    def check_online(self, user_id):

        url = self.EASEMOB_HOST + ("/%s/%s/users/%s/status" % (self.org, self.app, user_id))
        try:
            headers = yield self.get_app_client_headers()
            response = yield get_async_client().fetch(url,
                                                      method='GET',
                                                      headers=headers)
            raise gen.Return(json.loads(response.body)["data"][str(user_id)] == "online")
        except HTTPError as e:
            raise gen.Return(None)


    def d(self):
        import requests
        payload = {'grant_type': 'client_credentials', 'client_id': self.client_id, 'client_secret': self.client_secret}
        hu = self.EASEMOB_HOST + ("/%s/%s/token" % ("lcylln", "yyq"))
        h = requests.get(hu, payload)
        token = json.loads(h.content)["access_token"]
        headers = {'Authorization': 'Bearer ' + token,
                   'content-type': 'application/json'}
        url = self.EASEMOB_HOST + ("/%s/%s/users" % (self.org, self.app))
        s = requests.get(url, data=json.dumps({"username": "54887015", "password": "b733853dcefc0ad69f02e057608b3e3b"}), headers=headers)
        print(s)


# ss = EMChatAsync()
# ss.d()
