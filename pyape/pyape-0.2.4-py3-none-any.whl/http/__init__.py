import httpx 
from httpx import TimeoutException


class Req(object):
    """
    向 HTTP 服务器请求，基类
    """

    def __init__(self, r, url=None, timeout=3, connerrrmsg=None, logger=None):
        """
        初始化对象，每次请求都需要一个新对象
        :param r: regional
        :param url: 以 / 开头的地址，域名从配置中读取
        :param timeout: 访问超时（秒）
        :param connerrrmsg: 连接错误信息
        :param logger: logger 对象
        """
        self._r = r
        self._url = url
        self._timeout = timeout
        self._connerrmsg = connerrrmsg
        self._logger = logger

    def geturl(self):
        """
        子类必须覆盖此方法
        :return:
        """
        raise ValueError('必须覆盖 Req.geturl 方法，返回正确的 URL')

    def geterrormsg(self, msg=None, whole=False, code=500, error=True):
        if not msg:
            msg = 'action:' + self._url
        if not whole and not msg:
            msg = 'action: %s %s' % (self._url, msg)
        return {'error': error, 'message': msg, 'code': code}

    def debug(self, *args):
        if self._logger:
            self._logger.debug(*args)

    def info(self, *args):
        if self._logger:
            self._logger.info(*args)

    def error(self, *args):
        if self._logger:
            self._logger.error(*args)

    def _merge_info(self, info, rdata, data_key):
        """ 合并 info 和 rdata
        """
        # 若 info 提供了 code，使用它
        if info.get('code') is not None:
            rdata['code'] = info.get('code')
        # 若 code 不是 200，设定错误信息
        if rdata['code'] != 200:
            rdata['error'] = True
            if info.get('msg'):
                rdata['message'] = info.get('msg')
        if data_key:
            if info.get('data') is not None:
                # 如果info 提供了 data 键名，则仅使用 data 中的值
                rdata[data_key] = info.get('data')
            else:
                # 否则使用整个 info 作为 data
                rdata[data_key] = info

    def check_response(self, resp, data_key=None):
        """ 检测响应
        """
        rdata = {'error': False, 'code': 200}
        # print('Req.check_response status_code: %s, data:%s' %(resp.status_code, resp.content))
        self.info('Req.check_response status_code: %s, content:%s', resp.status_code, resp.content)
        if resp.status_code != 200:
            rdata['error'] = True
            rdata['code'] = resp.status_code
            if self._url:
                rdata['message'] = '%s %s %s' % (self._url, resp.status_code, resp.reason)
            else:
                rdata['message'] = '%s %s' % (resp.status_code, resp.reason)
            return rdata
        try:
            info = resp.json()
            # self.info('Req.check_response json: %s', info)
            if info:
                self._merge_info(info, rdata, data_key)
        except Exception as e:
            msg = 'Parse JSON error: ' + str(e)
            rdata['error'] = True
            rdata['code'] = 500
            rdata['message'] = msg
            self.error(msg)
            return rdata
        return rdata

    def do(self, data=None, data_key=None, method='get', json=False):
        try:
            url = self.geturl()
            self.info('Req.do: url: %s, method: %s, data: %s, data_key:%s', url, method, data, data_key)
            if url is None:
                return self.geterrormsg('没有找到 URL 配置，请检查！')
            if method == 'get':
                resp = httpx.get(url, params=data, timeout=self._timeout)
            else:
                # 仅 post 支持 json
                if json:
                    resp = httpx.post(url, json=data, timeout=self._timeout)
                else:
                    resp = httpx.post(url, data=data, timeout=self._timeout)
        except TimeoutException as e:
            self.error(str(e))
            return self.geterrormsg(str(e), True)
        except ConnectionError as e:
            self.error(str(e))
            return self.geterrormsg(self._connerrmsg or str(e), True)
        except Exception as e:
            self.error(str(e))
            return self.geterrormsg(str(e), False)
        return self.check_response(resp, data_key)
