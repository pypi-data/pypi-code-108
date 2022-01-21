# coding=utf-8
import json
import logging
import time
import urllib
from tornado.gen import Return, coroutine
from tornado.httpclient import HTTPRequest, AsyncHTTPClient
from hashlib import md5


class MobSMS(object):
    """短信验证码"""

    def __init__(self, **kwargs):
        self.debug = kwargs.get("debug", False)
        self.SMS_APP_KEY = kwargs["app_key"]
        self.SMS_APP_SECRET = kwargs["app_secret"]
        self.SEND_URL = kwargs["send_url"]
        self.SMS_VERIFY_URL_CLIENT = kwargs["client_verify_url"]
        self.SMS_VERIFY_URL_SERVER = kwargs["server_verfiy_url"]
        self.SALT = kwargs["salt"]  # 防刷码

    def check_seq(self, **kwargs):
        if self.debug:
            return True

        if "seq" not in kwargs or "timestamp" not in kwargs:
            # 缺少seq
            return False

        now = time.time()
        seq = kwargs["seq"]
        timestamp = kwargs["timestamp"]

        if now - 300 < timestamp < now + 300:
            real_seq = self.gen_seq(**kwargs)
            if real_seq == seq:
                return True

        return False

    def gen_seq(self, **kwargs):
        kwargs.pop("seq", None)

        d = []
        for k in sorted(kwargs.keys()):
            v = kwargs[k]
            if isinstance(v, unicode):
                v = v.encode("u8")
            d.append("%s=%s" % (k, str(v)))
        s = self.SALT + "&".join(d)
        return md5(s).hexdigest()

    @coroutine
    def send_sms(self, zone, phone):
        body = {"appkey": self.SMS_APP_KEY, "zone": zone, "phone": phone}
        r = yield self.mob_send(self.SEND_URL, body)
        raise Return(r)

    @coroutine
    def verify_sms(self, zone, phone, code, is_client=True):
        if self.debug:
            raise Return(True)

        url = self.SMS_VERIFY_URL_CLIENT if is_client else self.SMS_VERIFY_URL_SERVER
        body = {"appkey": self.SMS_APP_KEY, "zone": zone, "phone": phone, 'code': code}
        r = yield self.mob_send(url, body)
        raise Return(r)

    @coroutine
    def mob_send(self, url, body):
        if self.debug:
            raise Return(True)
        request = HTTPRequest(url, method="POST", body=urllib.urlencode(body), validate_cert=False)
        httpClient = AsyncHTTPClient()
        response = yield httpClient.fetch(request)
        if json.loads(response.body).get("status") == 200:
            raise Return(True)
        else:
            print(response.body)
            raise Return(False)


if __name__ == "__main__":
    from tornado.ioloop import IOLoop

    # assert MobSMS.check_seq(seq=u"7170d06b94b6d585ee73a43bf714ecf6", avatar=u"adssfsdfdf", nickname=u"sdfsfsdfdsf",
    #                      sex=123, age="13", login_type="中文123", access_token=u"sdfsdfsdf",
    #                      openid=u"中文123", timestamp=123123213) == 0
    loop = IOLoop.instance()


    def down_callback(future):
        loop.add_callback(loop.stop)


    MobSMS.send_sms(86, 13681236816).add_done_callback(down_callback)
    loop.start()

