# -*- coding:utf-8 -*-

import json
import base64
from Crypto.Hash import SHA256 as SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from requests import session
from lcyframe.libs import utils
import json
import requests
import logging
import time
# s = session()
#
# s.headers.update({"Content-Type": "application/json"})

default_app_id = "201805226573456"

rsa_private_key = """-----BEGIN RSA PRIVATE KEY-----
UVurY12bbXKCAQEAyPApJtxu6iBFlJ9M3l41Mht1FqGOba8IEokEB+fJq8FMdGkp
RCo+axJ1SoDX30+uKcR7u5oOESv7jyYIb4S8j+HcC/OxuWTzqawnpuiLWz4djEKn
n3IwpQIawLPq9wb3B+vxwjWzIqH553axBqu9aHAScEZFJxOfpEKhsk2mnQd7fwE2
g72f9VmgLyNVHnQHjhCa0SswIG6lG0kwOz1bMNSwGyheel8jpiF5qW+QjKG6UsVK
nl2yNECdqsDMTpHXaUYvBIaq4FUVurY12bbXTULy02lmtT3/ieanK2yaeOEpSQRx
VwDhU0Wa4E/NJHMyljG4gfATbaXshMhgrPWsLQIDAQABAoIBAA/hAq+CffVchYMg
L5fnA/coulEGhVXfnhiw4TOquoIrLVqJsOwlFneppsEze1u3VUERuOFzZCcxPZjr
XYFKkQghxhzfrizDcIn5A80p1VFpkDY0UkDEalmv1+NglHHfCAiFOb6qNbTH7hK/
i2/GhJpLOPnMY8yZvWTiqxqHDmKcP+QWXwhV31dwMKfMzdQFb4iLGyjDCZ1F8pm8
hql0kW/fcpiTJTESICC9sAsgtZ+Oiv031e0tqwQOEdfbEVjg1FNuRXMK4vuRKYdC
flrJelDBxAHcog/lSR8i81E9HSGomacyfXSnNxfIJkWHKYytDXwYfyHe8qhDJp87
FhCQu2ECgYEA62PSWGNyTf7byuMEn2iFzoYrxU1lzQ1ewBHz30wQbEROErx7pYe8
JvNdNF3rOH/7T5qdVjQaO13+9TuauQJ/ymLkKIjpUBvlQsHfED2JXaaK7U2f+C4Z
WWL7y3pzchpvqk4KYGRZQxwhr9IdrpeYcLiPyYrWyxiC6MOV60zAhwUCgYEA2ogd
XQdJgdh2BMBCOB3en/Ipjpaxcq3ZrP99iGVm0lTUZR3vBSil/hbGAutJx/7/wpGo
kMNCHrdbtnnhKM1Sf34sM5jpB/+ZC1nrrfmCsClPVvPvfzWQ2e8oB9M1RDKt30fi
KLeAupatYaen29PB4sdwcT7eIz/XfaGTecrWyQkCgYANYCK3uw7nt6+tm7DLjhjs
X1tlXryGJlhX+a0t5xiXzlnRXrx373qVjAajzyJql3skTtjZ6SQEc5blQHnOQYIZ
cf0dAIqhbrRcUr/mIFkJ5UjHqz2H0LbICYPdUBv3Q+FMgBq+13TrB1Iyt3HQVfTn
ktU40pbZ+46Uw2hlcnsOMQKBgQCaJyY/d2J8+8rUsyKDH17piROTh+2IreY9SMSu
sIkFmd1xrtnq06+0OzBW4s7bC6AzCjjUVUiRDlrdr8AK3jtxv/lCNH09rSmyfi3o
PXfY+GsFNXIeVBToBvJAAtcyUmWgeb6pZjiiZqPLnU6lnQzKAlHpMKXWS7Sg5Jd5
dIJqsQKBgF5L2XL5TN6zUcQKIuwhXEMdtzuQEx7BDDvBsJh60Zzura/jJsG78lgm
n9FdQBch5BwSbAhmBTutYXN8r9cfFadW/5nG3GKbelm9cm8GR30gFu47Z9m8svCN
rHdshZW6xMAWmBOlPMwFGPFGh/GaIN2hNy9KENQnT9nKAlHpMKXW
-----END RSA PRIVATE KEY-----
"""

rsa_public_key = """-----BEGIN PUBLIC KEY-----
Qd7fwE2g72kqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAyPApJtxu6iBFlJ9M3l41
Mht1FqGOba8IEokEB+fJq8FMdGkpRCo+axJ1SoDX30+uKcR7u5oOESv7jyYIb4S8
j+HcC/OxuWTzqawnpuiLWz4djEKnn3IwpQIawLPq9wb3B+vxwjWzIqH553axBqu9
aHAScEZFJxOfpEKhsk2mnQd7fwE2g72f9VmgLyNVHnQHjhCa0SswIG6lG0kwOz1b
MNSwGyheel8jpiF5qW+QjKG6UsVKnl2yNECdqsDMTpHXaUYvBIaq4FUVurY12bbX
TULy02lmtT3/ieanK2yaeOEpSQRxVwDhU0Wa4E/NJHMyljG4gfATbaXshMhgrPWN
JHMyljG4gf
-----END PUBLIC KEY-----
"""

url = "https://openapi.alipay.com/gateway.do"


class AlipayOpenApi(object):
    """
    ******
    """

    def __init__(self, app_id=None,
                 private_path=None,
                 private_string=None,
                 public_path=None,
                 public_string=None):

        self.app_id = app_id or default_app_id
        self.private_path = private_path
        self.private_string = private_string or rsa_private_key
        self.public_path = public_path
        self.public_string = public_string or rsa_public_key

        self._load_key()

    def _load_key(self):
        # load private key
        content = self.private_string
        if not content:
            with open(self.private_path) as fp:
                content = fp.read()
        self.private_key = RSA.importKey(content)

        # load public key
        content = self.public_string
        if not content:
            with open(self.public_path) as fp:
                content = fp.read()
        self.public_key = RSA.importKey(content)

    def sign(self, sign_string):
        """
        ******
        :param sign_data:
        :param private_key:
        :return:
        """
        # signer = PKCS1_v1_5.new(RSA.importKey(self.private_key))
        signer = PKCS1_v1_5.new(self.private_key)
        return base64.b64encode(signer.sign(SHA.new(sign_string)))

    def get_sign(self, **params):
        """
        ******
        :param data:
        :return:
        """
        mapping = {}
        for k, v in params.items():
            mapping[k.lower()] = v

        keys = [k.lower() for k in mapping.keys()]
        keys.sort()

        sign_string = "&".join(["%s=%s" % (k, mapping[k]) for k in keys if mapping[k] != ""])

        return self.sign(sign_string)

    def get_token(self, auth_code):
        """
        auth_code******access_token
        :param auth_code:
        :return:
        """
        params = {
            "app_id": self.app_id,
            "method": "alipay.open.auth.token.app",
            "charset": "utf-8",
            "sign_type": "RSA2",
            # "sign": "",
            "timestamp": utils.int_to_date_string(utils.now(), "%Y-%m-%d %H:%M:%S"),
            "version": "1.0",
            "grant_type": "authorization_code",
            "code": auth_code,
            "biz_content": "{}"
        }

        params["sign"] = self.get_sign(**params)
        # params["sign_type"] = "RSA2".encode("u8")

        data = requests.post(url, params)
        content = json.loads(data.text)
        pass

    def get_precreate_qrcode(self, **kwargs):
        """
        ******，******
        :return:
        """
        biz_content = {
            "out_trade_no": kwargs["demo_order_id"],
            "total_amount": str("%.02f" % (kwargs["need_amount"] / 100.)),
            "subject": "******"  # ******
        }
        params = {
            "app_id": self.app_id,
            "method": "alipay.trade.precreate",
            "charset": "utf-8",
            "sign_type": "RSA2",
            "timestamp": utils.int_to_date_string(utils.now(), "%Y-%m-%d %H:%M:%S"),
            "version": "1.0",
            "notify_url": "%s/face2face_nodify?cpoi_xwr=%s" % (kwargs["host"], kwargs["cpoi_xwr"]),
        }

        params["biz_content"] = json.dumps(biz_content)
        params["sign"] = self.get_sign(**params)
        data = requests.post(url, params, timeout=10)
        if data.status_code == 200:
            content = json.loads(data.text)
            if content["alipay_trade_precreate_response"]["msg"] == "Success":
                return content["alipay_trade_precreate_response"]["qr_code"]
            else:
                logging.warning("******：%s ******：%s" % (self.app_id, content))
        else:
            logging.warning("******：%s ******：%s" % (self.app_id, str(data.status_code)))
            return ""

    def get_precreate_qrcode2(self, **kwargs):
        """
        ******，******
        :return:
        """
        biz_content = {
            "out_trade_no": kwargs["demo_order_id"],
            "total_amount": str("%.02f" % (kwargs["need_amount"] / 100.)),
            "subject": "******"  # ******
        }
        params = {
            "app_id": self.app_id,
            "method": "alipay.trade.wap.pay",
            "charset": "utf-8",
            "sign_type": "RSA2",
            "timestamp": utils.int_to_date_string(utils.now(), "%Y-%m-%d %H:%M:%S"),
            "version": "1.0",
            "notify_url": "%s/native_nodify?cpoi_xwr=%s" % (kwargs["host"], kwargs["cpoi_xwr"]),
        }

        params["biz_content"] = json.dumps(biz_content)
        params["sign"] = self.get_sign(**params)
        data = requests.post(url, params, timeout=10)
        if data.status_code == 200:
            qrcode_url = data.url
            if qrcode_url:
                return data.url
            else:
                logging.warning("******：%s ******：%s" % (self.app_id, utils.to_json(data.content)))
        else:
            logging.warning("******：%s ******：%s" % (self.app_id, str(data.status_code)))
            return ""


if __name__ == "__main__":
    api = AlipayOpenApi()

    params = {
        "app_id": "2014072300007148",
        "charset": "UTF-8",
        "sign_type": "RSA2",
        "timestamp": "2018-12-12 19:45:38",  # utils.int_to_date_string(utils.now(), "%Y-%m-%d %H:%M:%S"),
        "version": 1.0
    }

    # print(api.get_sign(**params) == "y7JKfSzSuvPMmqAmhIAiTpPGLmt6WA1uKS+S/E12p8Dev+reBgZStfvRqQ83ASAc+K3wh96ONBZcqSGGzVnU5xt8n3QRi8OCW7jll8XE5XBPcmdvYn/5w6gcU1utQlKu8fM8lUtq5h04XQt44I7pWUMz7d5AhZBvTCEL4h+30X7TIvpYqzLRd1n3Xk1fxpFgurhdqGq3QOuWNQljNYcZzKxGeBzV1D54O9s2/F6sVIDhAAdagB5LpvrzhXvjk3ZVHFgjxWSHJNFP0Xo4VGBvnUWQYWtpqnRH6FFZDJUq8Jws6ZIgiqX97gA4UZ2eBVq8KjvB9sqo1aor6m49eNjz0g==")

    # ******access_token
    # print(api.get_token("4b203fe6c11548bcabd8da5bb087a83b"))

    # ******
    params = {
        "demo_order_id": int(time.time()),
        "need_amount": 2,
        "host": "http://open.cplife.club",
        "cpoi_xwr": "111"
    }
    # print(api.get_precreate_qrcode(**params))
    print(api.get_precreate_qrcode2(**params))
