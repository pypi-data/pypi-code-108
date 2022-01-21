# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2022-01-10 11:31:34
@LastEditTime: 2022-01-13 18:12:21
@LastEditors: HuangJianYi
@Description: 抖店接口业务模型
"""

import json
import time
import requests
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.hashes import MD5, SHA256, Hash
from cryptography.hazmat.primitives.hmac import HMAC
from seven_cloudapp_frame.libs.customize.seven_helper import SevenHelper
from seven_cloudapp_frame.models.seven_model import *
from seven_framework.base_model import *


class ShakeShopBaseModel():
    """
    :description: 抖店接口业务模型
    """
    def __init__(self, context, app_key: str, app_secret: str, app_type, code=None, shop_id: str = None, proxy: str = None, test_mode=False, logging_error=None, logging_info=None):
        """
        :description:  初始化实例，自用型应用传入shop_id用于初始化access token，工具型应用传入code换取access token（如初始化时未传入，可以在访问抖店API之前调用init_token(code)进行token的初始化。
        :param context: 上下文
        :param app_key: app_key
        :param app_secret: app_secret
        :param app_secret: app_secret
        :param app_type: app_type(SELF或TOOL)
        :param code: code
        :param shop_id: 店铺ID
        :param proxy: 代理
        :param test_mode: 是否测试沙盒
        :param logging_error: logging_error
        :param logging_info: logging_info
        :return 
        :last_editors: HuangJianYi
        """
        self.context = context
        self.logging_link_error = logging_error
        self.logging_link_info = logging_info
        self._app_key = app_key
        self._app_secret = app_secret
        self._app_type = app_type
        if self._app_type == "SELF" and not shop_id:
            raise ShopIdError('shop_id is not assigned.')
        self._shop_id = shop_id
        self._proxy = proxy
        self._test_mode = test_mode
        if self._test_mode:
            self._gate_way = 'https://openapi-sandbox.jinritemai.com'
        else:
            self._gate_way = 'https://openapi-fxg.jinritemai.com'
        self._version = 2
        redis_token = SevenHelper.redis_init().get(f"shakeshop_access_token:{str(app_key)}_{self._test_mode}")
        if redis_token:
            redis_token = json.loads(redis_token)
        self._token = redis_token
        self._sign_method = 'hmac-sha256'
        if self._token:
            if self._token.get('expires_in') - int(time.time()) < 3000:
                self._refresh_token()
        else:
            if self._app_type == "SELF":
                self.init_token()
            elif self._app_type == "TOOL" and code:
                self.init_token(code)

    def _sign(self, method: str, param_json: str, timestamp: str) -> str:
        param_pattern = 'app_key{}method{}param_json{}timestamp{}v{}'.format(self._app_key, method, param_json, timestamp, self._version)
        sign_pattern = '{}{}{}'.format(self._app_secret, param_pattern, self._app_secret)
        return self._hash_hmac(sign_pattern)

    def _hash_hmac(self, pattern: str) -> str:
        try:
            hmac = HMAC(key=self._app_secret.encode('UTF-8'), algorithm=SHA256(), backend=default_backend())
            hmac.update(pattern.encode('UTF-8'))
            signature = hmac.finalize()
            return signature.hex()
        except Exception as e:
            if self.context:
                self.context.logging_link_error(traceback.format_exc())
            elif self.logging_link_error:
                self.logging_link_error(traceback.format_exc())
            return None

    def _access_token(self) -> str:
        """
        :description: 获取access_token
        :return 
        :last_editors: HuangJianYi
        """
        if not self._token:
            raise TokenError('no token info, call init_token() to initialize it.')
        try:
            if self._token.get('expires_in') - int(time.time()) < 3000:
                self._refresh_token()
            return self._token.get('access_token')
        except Exception as e:
            if self.context:
                self.context.logging_link_error(traceback.format_exc())
            elif self.logging_link_error:
                self.logging_link_error(traceback.format_exc())
            return None

    def init_token(self, code: str = '') -> bool:
        """
        :description: 初始化access_token
        :param code: 工具型应用从授权url回调中获取到的code，自用型应用无需传入。
        :return 
        :last_editors: HuangJianYi
        """
        request_redis_key = f"shakeshop_access_token:{str(self._app_key)}_{self._test_mode}"
        if SevenHelper.is_continue_request(request_redis_key, 2000) == True:
            return False
        if self._app_type == "TOOL" and not code:
            raise CodeError('code is not assigned.')
        path = '/token/create'
        grant_type = 'authorization_self' if self._app_type == "SELF" else 'authorization_code'
        params = {}
        params.update({'code': code if code else ''})
        params.update({'grant_type': grant_type})
        if self._app_type == "SELF":
            if self._test_mode:
                params.update({'test_shop': '1'})
            elif self._shop_id:
                params.update({'shop_id': self._shop_id})
            else:
                raise ShopIdError('shop_id is not assigned.')
        result = self._request(path=path, params=params, token_request=True)
        SevenHelper.redis_init().delete(request_redis_key)
        if result and result.get('err_no') == 0 and result.get('data'):
            self._token = result.get('data')
            self._token.update({'expires_in': int(time.time()) + result.get('data').get('expires_in')})
            SevenHelper.redis_init().set(f"shakeshop_access_token:{str(self._app_key )}_{self._test_mode}", json.dumps(self._token), ex=3600)
            return True
        return False

    def _get_refresh_token(self) -> str:
        """
        :description: 获取refresh_token
        :return 
        :last_editors: HuangJianYi
        """
        if not self._token:
            return None
        try:
            return self._token.get('refresh_token')
        except Exception as e:
            if self.context:
                self.context.logging_link_error(traceback.format_exc())
            elif self.logging_link_error:
                self.logging_link_error(traceback.format_exc())
            return None

    def _refresh_token(self) -> None:
        """
        :description: 刷新refresh_token
        :return 
        :last_editors: HuangJianYi
        """
        request_redis_key = f"shakeshop_access_token:{str(self._app_key)}_{self._test_mode}"
        if SevenHelper.is_continue_request(request_redis_key, 2000) == True:
            return False
        path = '/token/refresh'
        refresh_token = self._get_refresh_token()
        grant_type = 'refresh_token'
        params = {}
        params.update({'grant_type': grant_type})
        params.update({'refresh_token': refresh_token})
        result = self._request(path=path, params=params, token_request=True)
        SevenHelper.redis_init().delete(request_redis_key)
        if result and result.get('err_no') == 0 and result.get('data'):
            self._token = result.get('data')
            self._token.update({'expires_in': int(time.time()) + result.get('data').get('expires_in')})
            SevenHelper.redis_init().set(f"shakeshop_access_token:{str(self._app_key )}_{self._test_mode}", json.dumps(self._token), ex=3600)

    def _request(self, path: str, params: dict, token_request: bool = False, is_log: bool = False) -> json:
        """
        :description: 发起请求
        :param path: api地址
        :param params: 参数集合
        :param token_request: 是否token请求
        :param is_log: 是否记录日志
        :return 
        :last_editors: HuangJianYi
        """
        try:
            headers = {}
            headers.update({'Content-Type': 'application/json'})
            headers.update({'Accept': 'application/json'})
            headers.update({'User-Agent': 'newfire doudian python sdk(https://github.com/minibear2021/doudian)'})
            timestamp = SevenHelper.get_now_datetime()
            param_json = json.dumps(params, sort_keys=True, separators=(',', ':'))
            method = path[1:].replace('/', '.')
            sign = self._sign(method=method, param_json=param_json, timestamp=timestamp)
            if token_request:
                url = self._gate_way + '{}?app_key={}&method={}&param_json={}&timestamp={}&v={}&sign_method={}&sign={}'.format(path, self._app_key, method, param_json, timestamp, self._version, self._sign_method, sign)
            else:
                access_token = self._access_token()
                url = self._gate_way + '{}?app_key={}&method={}&access_token={}&param_json={}&timestamp={}&v={}&sign_method={}&sign={}'.format(path, self._app_key, method, access_token, param_json, timestamp, self._version, self._sign_method, sign)
            if is_log == True:
                if self.context:
                    self.context.logging_link_info(f'Request url:{url},Request headers:{headers},Request params:{param_json}')
                elif self.logging_link_info:
                    self.logging_link_info(f'Request url:{url},Request headers:{headers},Request params:{param_json}')

            response = requests.post(url=url, data=param_json, headers=headers, proxies=self._proxy)
            if is_log == True:
                if self.context:
                    self.context.logging_link_info(f'Response status code: {response.status_code},Response headers:{response.headers},Response content:' + response.content.decode('UTF-8'))
                elif self.logging_link_info:
                    self.logging_link_info(f'Response status code: {response.status_code},Response headers:{response.headers},Response content:' + response.content.decode('UTF-8'))
            if response.status_code != 200:
                return None
            return json.loads(response.content)
        except Exception as e:
            if self.context:
                self.context.logging_link_error(traceback.format_exc())
            elif self.logging_link_error:
                self.logging_link_error(traceback.format_exc())
            return None

    def request(self, path: str, params: dict, is_log: bool = False) -> json:
        """
        :description: 请求抖店API接口
        :param path: 调用的API接口地址，示例：'/material/uploadImageSync'
        :param params: 业务参数字典，示例：{'folder_id':'70031975314169695161250','url':'http://www.demo.com/demo.jpg','material_name':'demo.jpg'}
        :param is_log: 是否记录日志
        :return 
        :last_editors: HuangJianYi
        """
        return self._request(path=path, params=params, is_log=is_log)

    def callback(self, headers: dict, body: bytes, is_log: bool = False) -> json:
        """
        :description: 验证处理消息推送服务收到信息Md5解密模式
        :param headers: headers
        :param body: body
        :param is_log: 是否记录日志
        :return 
        :last_editors: HuangJianYi
        """
        data: str = body.decode('UTF-8')
        if is_log == True:
            if self.context:
                self.context.logging_link_info(f'Callback Header:{headers},Callback Body:{body}')
            elif self.logging_link_info:
                self.logging_link_info(f'Callback Header:{headers},Callback Body:{body}')
        if not data:
            return None
        if headers.get('app-id') != self._app_key:
            return None
        event_sign: str = headers.get('event-sign')
        if not event_sign:
            return None
        h = Hash(algorithm=MD5(), backend=default_backend())
        h.update('{}{}{}'.format(self._app_key, data, self._app_secret).encode('UTF-8'))
        if h.finalize().hex() != event_sign:
            return None
        return json.loads(data)

    def build_auth_url(self, service_id: str, state: str) -> str:
        """拼接授权URL，引导商家点击完成授权
        """
        if self._app_type == "TOOL":
            return 'https://fuwu.jinritemai.com/authorize?service_id={}&state={}'.format(service_id, state)
        else:
            return None


class TokenError(Exception):
    """access token无效
    """
    pass


class CodeError(Exception):
    """code无效
    """
    pass


class ShopIdError(Exception):
    """shop_id无效
    """
    pass
