"""
内容管理系统

注：requests-toolbelt 上传文件需要
"""

import os
import json
import time
import hashlib
import random
from pathlib import Path
from pprint import pprint as pp

from requests import Response
from requests_toolbelt import MultipartEncoder
from urllib.parse import urlparse
from PIL import Image

from spider_utils.client import BaseSpiderClient

from .utils import need_login
from .enums import AreaEnum, TypeEnum
from .exception import LoginError

# url = "https://username:password@www.baidu.com:80/index.html;parameters?name=tom#example"

from .requests import (
    ArtistSearchRequests,
    AlbumSearchRequests,
    SaveAlbumRequests,
    UserSubjectRequests,
    CreateShowerRequests,
    CheckRepeatRequests,
    QueryCompanySettlementRequests,
    QueryMatchListRequests,
    QueryMatchMQListRequests,
    QueryMatchSearchListRequests,
    QueryCheckMatchRequests,
    QueryTmeSettlementRequests,
    AccountListRequests,
    QuerySongRequests,
    QueryContractsRequests,
)

from .responses import (
    SigningAuthorizeResponses,
    IndexInfoResponses,
    ArtistListResponses,
    CompanyResponses,
    AlbumResponses,
    AlbumDetailsResponses,
    UserSubjectResponses,
    AudioDetectionResponses,
    QuerySongResponses,
    QueryContractsResponses,
    QueryCompanySettlementResponses,
    QueryMatchListResponses,
    QueryMatchMQListResponses,
    QueryMatchSearchListResponses,
    QueryTmeSettlementResponses,
    AccountListResponses,
)

headers = {
    "Accept": "*/*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Content-Type": "application/json;charset=UTF-8",
    # "DNT": "1",
    # "Host": "cms.sit.tmeoa.com",
    # "Origin": "http://cms.sit.tmeoa.com",
    # "Referer": "http://cms.sit.tmeoa.com/login",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36",
    # "title": "\\u817e\\u8baf\\u97f3\\u4e50\\u5a31\\u4e50"
}

URL_DICT = {
    'dev': {'web': 'http://cms.dev.tmeoa.com', 'api': 'http://cms.apidev.tmeoa.com', },
    'sit': {'web': 'http://cms.sit.tmeoa.com', 'api': 'http://cms.apisit.tmeoa.com', },
    'uat': {'web': 'http://cms.uat.tmeoa.com', 'api': 'http://cms.uat.tmeoa.com/api', },  # http://cms.apiuat.tmeoa.com
    'cms': {'web': 'http://icms.tmeoa.com', 'api': 'http://icms.tmeoa.com/api', },  # http://icms.api.tmeoa.com
}

# https://stackoverflow.com/questions/11832930/html-input-file-accept-attribute-file-type-csv
# 限制文件上传格式
ACCEPT_TYPE = {
    # 音频
    '.mp3': 'audio/mp3',
    '.flac': 'audio/flac',
    '.ogg': 'audio/ogg',
    '.wav': 'audio/wav',
    '.ape': 'audio/ape',
    '.wma': 'audio/wma',
    # 图片
    '.jpg': 'image/jpg',
    '.jpeg': 'image/jpeg',
    '.png': 'image/png',
    # 文件
    '.pdf': '.pdf',
    '.msg': '.msg',
    '.xls': '.xls',
    '.xlsx': '.xlsx',
    '.doc': '.doc',
    '.docx': '.docx',
    '.rar': '.rar',
    '.zip': '.zip',
    # 歌词
    '.txt': 'text/plain',
}


def _generate_kwargs(post=True):
    """
    从剪切板获取内容，生成需要用的参数
    """
    import pyperclip

    text = pyperclip.paste()
    # 参数列表
    kwargs_list = []
    kwargs_info = []
    for line in text.split('\n'):
        try:
            if post:
                参数名, 是否必选, 类型, 说明 = line.split('\t')
            else:
                参数名, 类型, 说明 = line.split('\t')
            # print(参数名, 是否必选, 类型, 说明)
            kwargs_list.append(参数名)
            kwargs_info.append(f"'{参数名}' : {参数名},  # {说明.strip()}")
        except Exception as e:
            print(line, e)
    print('-' * 70)
    print("='',".join(kwargs_list))
    print("\n".join(kwargs_info))
    print('=' * 70)


def get_appkey(url):
    """
    从 url 中获取 appkey

    """
    u = urlparse(url)
    data = [param[7:] for param in u.query.split('&') if param.startswith('appkey=')]
    if data:
        return data[0]


class TmeCms(BaseSpiderClient):

    def __init__(self, platform='uat', *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.platform = platform
        self.user_info = None
        self._token = None
        self._login_data = {}
        self.set_headers(headers)
        self.data = None

    def set_token(self, token):
        """
        设置登录授权
        """
        self.set_headers({'Authorization': f'Bearer {token}'})
        # 我们获取消息数量，检查是否已经登录成功
        self.get_count_message()
        self._token = token

    @property
    def base_url(self):
        return URL_DICT[self.platform]['api']

    def is_login(self):
        """
        检查是否已登录，我们还是只简单检查有没有 token
        """
        # self.get_count_message()
        return self._token is not None

    def load_token(self, filename):
        """
        通过载入 token 文件来达到登录状态。

        ..  seealso:: :meth:`.save_token`

        :param str|unicode filename: token 文件名。
        :return: 无返回值，也就是说其实不知道是否登录成功。
        """

        with open(filename, 'r', encoding='utf-8') as f:
            self.user_info = json.load(f)
            self._token = self.user_info['access_token']
            self.set_token(self.user_info['access_token'])
        self.is_login()

    @need_login
    def save_token(self, filename):
        """
        将通过登录获取到的 token 保存为文件，必须是已登录状态才能调用。

        ..  seealso:: :meth:`.load_token`

        :param str|unicode filename: 将 token 储存为文件。
        :return: 无返回值。
        """
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.user_info, f, ensure_ascii=False, indent=2)

    def get_response_data(self, resp):
        """
        解析接口返回的数据
        """
        self.data = None
        if resp.status_code != 200:
            raise ValueError(f'状态错误：{resp.text}')
        json_data = resp.json()
        if str(json_data['msg']).lower() != 'ok':
            raise ValueError(f'返回消息：{json_data["msg"]}')
        self.data = json_data['data']
        return self.data

    def sys_login(self, username, password):
        """
        系统登录，已经改为微信扫码登录
        """
        raise LoginError(f'已经改为微信登录，不支持账户密码登录!!!')
        url = f"{self.base_url}/user/sys-login"
        data = {"username": username, "password": hashlib.md5(password.encode('utf-8')).hexdigest()}
        r = self._session.post(url, json=data)
        self.user_info = self.get_response_data(r)
        self.set_token(self.user_info['access_token'])

    def _get_login(self):
        """
        获取微信登录需要的数据
        """
        redirect_uri = f"{URL_DICT[self.platform]['web']}/login/callback?"
        # print('redirect_uri:', redirect_uri)

        # 获取统一登录 URL
        url = f"{self.base_url}/user/login?redirecturi={redirect_uri}"  # /callback?
        # url = f"{self.base_url}/user/login"  # /callback?
        r = self._session.get(url)
        # print(r.json())
        login_url = self.get_response_data(r)

        if 'appkey=' not in login_url:
            raise LoginError(f'没有需要的 appkey 参数: {r.url}')

        u = urlparse(login_url)
        passport_url = f'{u.scheme}://{u.netloc}'
        # print(login_url)
        app_key = [param[7:] for param in u.query.split('&') if param.startswith('appkey=')][0]

        return login_url, redirect_uri, passport_url, app_key

    def auth_login(self, code):
        """
        认证后跳转
        """
        url = f"{self.base_url}/user/auth-login?code={code}"
        # print(url)
        r = self._session.get(url)
        # print(r.json())
        self.user_info = self.get_response_data(r)
        self.set_token(self.user_info['access_token'])

    def _get_qr_code_key(self, passport_url, app_key):
        """
        获取二维码的 Key
        """
        key_url = f'{passport_url}/scan/refreshQRCodeKey?t={random.random()}&app_key={app_key}'
        return self.get_response_data(self._session.get(key_url))

    def _get_qr_code(self):
        """
        获取二维码
        """
        login_url, redirect_uri, passport_url, app_key = self._get_login()

        qr_code_key = self._get_qr_code_key(passport_url, app_key)

        qr_code_url = f'{passport_url}/scan/qrcode?qrcode_key={qr_code_key}'

        # 保存登录数据，检查是否登录成功的时候使用
        self._login_data = {
            'login_url': login_url,
            'redirect_uri': redirect_uri,
            'passport_url': passport_url,
            'app_key': app_key,
            'qr_code_key': qr_code_key,
        }

        return self._session.get(qr_code_url)

    def _check_qr_code_login(self, passport_url, app_key, redirect_uri, qr_code_key):
        """
        检查二维码登录，如果成功保存登录数据
        """

        # 获取扫描检查的结果
        check_url = f'{passport_url}/scan/check?t={random.random()}&qrcode_key={qr_code_key}'
        scan_data = self.get_response_data(self._session.get(check_url))

        scan_status = scan_data['scanStatus']
        # print(scan_status)

        if scan_status == 11:
            print('扫码')
        elif scan_status == 12:
            print('扫码成功')
            auth_code = scan_data['auth_code']
            authorize_url = f'{passport_url}/authorize?code={auth_code}&appkey={app_key}&redirect_uri={redirect_uri}&qrcode_key={qr_code_key}'
            r = self._session.get(authorize_url)
            if 'code=' in r.url:
                self.auth_login(r.url.split('code=')[-1])
                return True
            else:
                raise LoginError(f'code错误: {r.url}')
        elif scan_status == 15:
            raise LoginError(f'二维码过期')

    def wx_login(self, time_out=30, save_token_file=None):
        """
        微信登录

        我们通过重写这部分，来支持网页登录
        """
        # 获取二维码，我们在获取二维码的时候也保存了需要用的登录参数到 self._login_data
        r = self._get_qr_code()

        Path('weixin_qrcode.jpg').write_bytes(r.content)

        # 显示二维码
        im = Image.open('weixin_qrcode.jpg')
        im.show()

        passport_url = self._login_data["passport_url"]
        app_key = self._login_data["app_key"]
        redirect_uri = self._login_data["redirect_uri"]
        qr_code_key = self._login_data["qr_code_key"]

        start = time.time()
        while True:  # 由于需要不断请求，让我们有时间来扫描二维码

            if self._check_qr_code_login(passport_url, app_key, redirect_uri, qr_code_key):
                break
            elif time.time() - start > time_out:
                raise LoginError(f'扫码登录超过 {time_out} 秒')

            time.sleep(2)

        if save_token_file is not None:
            self.save_token(save_token_file)

    def pin_login(self, username, password, save_token_file=None):
        """
        PIN 登录
        """
        login_url, redirect_uri, passport_url, app_key = self._get_login()

        data = {'username': username, 'password': password, 'login': '登  录', }

        authorize_url = f'{passport_url}/authorize?appkey={app_key}&redirect_uri={redirect_uri}'
        _headers = self.get_headers()
        _headers['Content-Type'] = 'application/x-www-form-urlencoded'
        r = self._session.post(authorize_url, data=data, headers=_headers)

        if 'code=' in r.url:
            self.auth_login(r.url.split('code=')[-1])
        else:
            raise LoginError(f'code错误: {r.url}')
        if save_token_file is not None:
            self.save_token(save_token_file)

    def get_account_list(self, account_list: AccountListRequests = None):
        """
        账号搜索
        """
        if account_list is None:
            account_list = AccountListRequests()

        url = f"{self.base_url}/accountmanage/list"
        r = self._session.post(url, data=account_list.json(exclude_none=True, ensure_ascii=False).encode('utf-8'))
        # return self.get_response_data(r)
        return AccountListResponses(**self.get_response_data(r))

    def get_index(self):
        """
        获取首页信息
        """
        url = f"{self.base_url}/index/index"
        r = self._session.get(url)
        return IndexInfoResponses(**self.get_response_data(r))

    def get_user_menu(self):
        """
        获取当前用户菜单
        """
        url = f"{self.base_url}/power/user-menu"
        r = self._session.post(url)
        return self.get_response_data(r)

    def get_count_message(self):
        """
        未读消息统计
        """
        url = f"{self.base_url}/message/count-message"
        r = self._session.post(url)
        return self.get_response_data(r)

    def get_company_list(self, supplier_url: str):
        """
        获取接口所属公司范围
        """
        url = f"{self.base_url}/system/company-list"
        r = self._session.post(url, json={'url': supplier_url})
        return CompanyResponses(**self.get_response_data(r))

    def get_signing_authorize(self):
        """
        获取签约授权信息
        """
        url = f"{self.base_url}/contract/signing-authorize"
        r = self._session.get(url)
        return SigningAuthorizeResponses(**self.get_response_data(r))

    def get_user_subject(self, user_subject: UserSubjectRequests = None):
        """
        获取用户签约主体列表
        """
        if user_subject is None:
            user_subject = UserSubjectRequests()

        url = f"{self.base_url}/subject/user-subject"
        r = self._session.post(url, data=user_subject.json(exclude_none=True, ensure_ascii=False).encode('utf-8'))
        return UserSubjectResponses(**self.get_response_data(r))

    def get_shower_list(self, artist_search: ArtistSearchRequests = None):
        """
        艺人查询
        """
        if artist_search is None:
            artist_search = CreateShowerRequests()

        url = f"{self.base_url}/work/shower-list"
        r = self._session.post(url, data=artist_search.json(ensure_ascii=False).encode('utf-8'))
        return ArtistListResponses(**self.get_response_data(r))

    def create_shower(self, shower: CreateShowerRequests = None):
        """
        艺人创建
        """
        if shower is None:
            shower = CreateShowerRequests()

        url = f"{self.base_url}/work/create-shower"
        r = self._session.post(url, data=shower.json(ensure_ascii=False).encode('utf-8'))
        return self.get_response_data(r)

    def get_album_list(self, album_search: AlbumSearchRequests = None):
        """
        专辑列表
        """
        if album_search is None:
            album_search = AlbumSearchRequests()

        url = f"{self.base_url}/work/album-list"
        r = self._session.post(url, data=album_search.json(ensure_ascii=False).encode('utf-8'))
        return AlbumResponses(**self.get_response_data(r))

    def get_album(self, album_id):
        """
        获取专辑详情
        """
        url = f"{self.base_url}/work/get-album"
        r = self._session.post(url, json={'id': album_id})
        # print(r.json())
        return AlbumDetailsResponses(**self.get_response_data(r))

    def save_album_draft(self, album_info: SaveAlbumRequests = None):
        """
        保存专辑草稿
        """
        if album_info is None:
            album_info = SaveAlbumRequests()

        url = f"{self.base_url}/work/save-album"
        r = self._session.post(url, data=album_info.json(ensure_ascii=False).encode('utf-8'))
        return self.get_response_data(r)

    # def get_file(self, att_id):
    #     """
    #     获取文件链接
    #     """
    #     url = f"{self.base_url}/upload/att"
    #     url = f"{self.base_url}/upload/show"
    #     r = self._session.get(url, params={'att_id': att_id})
    #     return self.get_response_data(r)

    def query_song(self, song_info: QuerySongRequests = None):
        """
        作品查询
        """
        if song_info is None:
            song_info = QuerySongRequests()

        url = f"{self.base_url}/query/works"
        r = self._session.post(url, data=song_info.json(ensure_ascii=False).encode('utf-8'))
        # return self.get_response_data(r)
        return QuerySongResponses(**self.get_response_data(r))

    def query_contracts(self, contracts_info: QueryContractsRequests = None):
        """
        合同查询
        """
        if contracts_info is None:
            contracts_info = QueryContractsRequests()

        url = f"{self.base_url}/query/contracts"
        r = self._session.post(url, data=contracts_info.json(ensure_ascii=False).encode('utf-8'))
        return QueryContractsResponses(**self.get_response_data(r))

    def get_contract_id_list(self, inter_no, equal=True):
        """
        获取合同ID列表

        """
        contracts = self.query_contracts(QueryContractsRequests(inter_no=inter_no))
        if equal:
            contract_id_list = [c.id for c in contracts.list if c.inter_no == inter_no]
        else:
            contract_id_list = [c.id for c in contracts.list]
        return contract_id_list

    def contracts_works_down(self, contract_id_list):
        """
        合同关联作品下载
        """
        url = f"{self.base_url}/contract/works-down"
        r = self._session.post(url, json={'contract_id_list': contract_id_list})
        return self.get_response_data(r)

    def query_company_settlement(self, settlement_info: QueryCompanySettlementRequests = None):
        """
        版权结算单查询

        /settlement-center/company-settlement 结算中心 / 供应商结算单列表
        """
        if settlement_info is None:
            settlement_info = QueryCompanySettlementRequests()

        url = f"{self.base_url}/account/sup-account-list"
        r = self._session.post(url, data=settlement_info.json(ensure_ascii=False).encode('utf-8'))
        # return self.get_response_data(r)
        return QueryCompanySettlementResponses(**self.get_response_data(r))

    def export_sup_account(self, settlement_id):
        """
        版权结算单导出

        结算中心 / 供应商结算单列表

        # 返回
        [{
          "id": "",
          "name": "",
          "url": "",
          "condition": "",
          "file_name": ""  # 有时候会没有
        }]
        """
        url = f"{self.base_url}/account/export-sup-account"
        r = self._session.post(url, json={'id': settlement_id})
        return self.get_response_data(r)

    def export_account(self, settlement_id):
        """
        结算单导出下载

        结算中心 / TME结算单列表 - 下载结算单

        # 返回
        "data": [{
            "id": "50",
            "url": ""
        }],
        """
        url = f"{self.base_url}/account/export-account"
        r = self._session.post(url, json={'id': settlement_id})
        return self.get_response_data(r)

    def query_match_list(self, match_info: QueryMatchListRequests = None):
        """
        手工单查询

        """
        if match_info is None:
            match_info = QueryMatchListRequests()

        url = f"{self.base_url}/account/match-list"
        r = self._session.post(url, data=match_info.json(ensure_ascii=False).encode('utf-8'))
        # return self.get_response_data(r)
        return QueryMatchListResponses(**self.get_response_data(r))

    def query_match_search_list(self, search_info: QueryMatchSearchListRequests = None):
        """
        手工单选择条件查询
        """
        if search_info is None:
            search_info = QueryMatchSearchListRequests()

        url = f"{self.base_url}/account/match-search"
        r = self._session.post(url, data=search_info.json(ensure_ascii=False).encode('utf-8'))
        # return self.get_response_data(r)
        return QueryMatchSearchListResponses(**self.get_response_data(r))

    def query_check_match_list(self, check_info: QueryCheckMatchRequests = None):
        """
        手工单生成版权结算单

        结算中心 / 手工生成结算单列表 - 选择条件 生成结算的任务
        """
        if check_info is None:
            check_info = QueryCheckMatchRequests()

        url = f"{self.base_url}/account/check-match"
        r = self._session.post(url, data=check_info.json(ensure_ascii=False).encode('utf-8'))
        return self.get_response_data(r)
        # return QueryMatchSearchListResponses(**self.get_response_data(r))

    def query_match_mq_list(self, mq_info: QueryMatchMQListRequests = None):
        """
        手工单任务查询(异步消息队列列表)
        """
        if mq_info is None:
            mq_info = QueryMatchMQListRequests()

        url = f"{self.base_url}/account/match-mq-list"
        r = self._session.post(url, data=mq_info.json(ensure_ascii=False).encode('utf-8'))
        # return self.get_response_data(r)
        return QueryMatchMQListResponses(**self.get_response_data(r))

    def query_tme_settlement(self, settlement_info: QueryTmeSettlementRequests = None):
        """
        结算单查询列表

        settlement-center/tme-settlement 结算中心 / TME结算单列表
        """
        if settlement_info is None:
            settlement_info = QueryTmeSettlementRequests()

        url = f"{self.base_url}/account/account-list"
        r = self._session.post(url, data=settlement_info.json(ensure_ascii=False).encode('utf-8'))
        # return self.get_response_data(r)
        return QueryTmeSettlementResponses(**self.get_response_data(r))

    def upload(self, upload_url, filename, accept_types=None):
        """
        作品录入文件上传
        """
        if accept_types is None:
            accept_types = ACCEPT_TYPE
        ext_name = os.path.splitext(filename)[-1]
        # print(ext_name)
        if ext_name in accept_types:
            file_type = accept_types[ext_name]
        else:
            raise TypeError(f"不支持的文件格式: {ext_name}")

        url = f"{self.base_url}/{upload_url}"
        # print(os.path.basename(filename))
        # from urllib.parse import quote, unquote
        m = MultipartEncoder(
            fields={
                'cosfile': (os.path.basename(filename), open(filename, 'rb'), file_type),
                'name': os.path.basename(filename),
                'type': file_type,
                'size': str(os.path.getsize(filename)),
            }
        )
        r = self._session.post(url, data=m, headers={'Content-Type': m.content_type})
        return self.get_response_data(r)

    def upload_work_file(self, filename):
        """
        作品录入文件上传
        """
        return self.upload('upload/work-file', filename)

    def upload_work_file_prod(self, filename):
        """
        作品文件上传
        """
        return self.upload('upload/work-file-prod', filename)

    def audio_detection(self, file_key):
        """
        音频检测上线平台
        """
        url = f"{self.base_url}/work/music-upload"
        r = self._session.post(url, json={'name': file_key})
        return AudioDetectionResponses(**self.get_response_data(r))

    def check_repeat(self, check: CheckRepeatRequests):
        """
        作品检测是否重复
        """
        url = f"{self.base_url}/work/check-repeat"
        r = self._session.post(url, data=check.json(ensure_ascii=False).encode('utf-8'))
        return self.get_response_data(r)
