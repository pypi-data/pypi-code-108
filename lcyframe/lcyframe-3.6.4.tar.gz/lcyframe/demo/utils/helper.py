# coding=utf-8
import os
import logging
import random
import time
from datetime import datetime, date
import zlib, hmac, urllib
from bson import BSON, ObjectId
from functools import wraps
from lcyframe.libs import utils, funts, cprint, JWT, aes, Rsa, errors
import re


def get_excel_url(host, img, path=None):
    """excel"""
    if path is None:
        path = "/data/excel"

    if "http" in host and host.startswith("http"):
        pass
    else:
        host = "http://" + host

    p = host + path
    p = os.path.join(p, img)
    return p


def get_imge_url(host, img, path=None):
    """******"""
    if path is None:
        path = "/data"

    if "http" in host and host.startswith("http"):
        pass
    else:
        host = "http://" + host

    safe_params = os.path.join(path, img)
    p = os.path.join(host, urllib.parse.quote(safe_params, safe='/', encoding=None, errors=None))
    return p


def save_filedata(data, base_path, **kwargs):
    """保存文件"""
    if not data:
        return ""

    filename = gen_filename(data, **kwargs)
    save_path = gen_filepath(base_path, filename)

    if not os.path.exists(base_path):
        os.mkdir(base_path)

    if not os.path.exists(save_path):
        with open(save_path, "wb") as f:
            f.write(data["body"])

    return filename, save_path

def gen_filepath(base_path, filename=None):
    if not os.path.exists("%s" % base_path):
        os.makedirs("%s" % base_path)

    save_path = "%s/%s" % (base_path, filename)
    return save_path

def gen_filename(file_data, prefix="", suffix="", name_type="unique"):
    """
    生成文件名
    根据数据md5对文件去重
    :param body:
    :param name_type: unique名称按数据去重，date 按时间格式命名 random 随机命名
    :return:

    """
    metadata = get_fileinfo(file_data)

    if name_type == "unique":
        filename = metadata["unique_name"]
    elif name_type == "date":
        filename = "%s-%s" % (datetime.now().strftime("%Y%m%d%H%M%S"), str(utils.random_int(4)))
    elif name_type == "random":
        filename = str(utils.gen_random_sint(16))
    else:
        filename = metadata["name"]

    return "%s%s%s.%s" % (prefix, filename, suffix, metadata["format"])

def get_fileinfo(file_data=None, file_path=None):
    """
    读取文件基本信息
    :param file_data:
    :return:
    """
    if file_data:
        body = file_data["body"]
        unique_name = utils.md5(body)
        name, format = file_data["filename"].split(".")
        size = len(body)
    elif file_path and os.path.exists(file_path):
        with open(file_path, "r") as p:
            body = p.read()
            unique_name = utils.md5(body)
            name, format = file_data.split("/")[-1].split(".")
            size = len(body)
    else:
        raise

    return {
        "filename": file_data["filename"],
        "name": name,
        "format": format,
        "size": size,
        "unique_name": unique_name,
        "unique_filename": "%s.%s" % (unique_name, format)
    }

def app(permission_bit=0):
    """
    应用端访问： app web
    :param permission_bit: 
    :return: 
    """
    def wrap(method):
        @wraps(method)
        def has_role(self, *args, **kwargs):
            self.params = funts.get_params(self)
            if self.application.app_config["wsgi"]["logging_debug"] == "debug":
                logging.warning(self.params)

            if self.request.headers.get("uid", None):
                _check_admin(self)
            else:
                raise errors.MemberNotFound

            _check_token(self, permission_bit)

            return method(self, *args, **kwargs)

        return has_role

    return wrap

def admin(permission_bit=0):
    """
    管理后台验证: jtw
    支持多个客户端同时访问
    :param permission_bit:
    :return:
    """

    def wrap(method):
        @wraps(method)
        def has_role(self, *args, **kwargs):
            self.params = funts.get_params(self)
            if self.application.app_config["wsgi"]["logging_debug"] == "debug":
                logging.warning(self.params)

            # 用户后台
            if self.request.headers.get("uid", None):
                _check_admin(self)
            # 开发者接口方式访问
            elif self.request.headers.get("appkey", None):
                pass
            # 公司账户访问
            elif self.request.headers.get("commany", None):
                pass

            _check_token(self, permission_bit)

            return method(self, *args, **kwargs)

        return has_role

    return wrap


def api(permission_bit=1):
    """
    开放平台api访问装饰器
    通常用于开发者远程调用
    Aes加密
    :param permission_bit:
    :return:
    """

    def wrap(method):
        @wraps(method)
        def has_role(self, *args, **kwargs):
            self.params = funts.get_params(self)
            if self.application.app_config["wsgi"]["logging_debug"] == "debug":
                logging.warning(self.params)
                logging.warning(get_argument(self))

            self.uid = self.app_key = self.request.headers.get("appkey", None)
            self.token = self.request.headers.get("token", "")

            if not self.app_key or not self.token:
                raise errors.ErrorTokenInvalid

            if not ObjectId.is_valid(self.app_key):
                raise errors.ErrorTokenInvalid

            self.developer = self.model.DeveloperModel.get_developer(self.app_key)
            if not self.developer:
                raise errors.ErrorTokenInvalid

            self.developer_id = self.developer.get("_id", "")

            self.is_usdt = self.developer.get("is_usdt", False)

            # ******IP
            verifi_ip(self, self.developer["ip_list"])

            token_debug = self.application.token_config.get("debug", False)
            if not token_debug:
                if permission_bit != 0:
                    if not self.uid or not self.token:
                        raise errors.ErrorTokenInvalid

                    # ******
                    verifi_sign(self, self.token, self.developer["secret_key"])

            return method(self, *args, **kwargs)

        return has_role

    return wrap


def _check_admin(self):
    self.is_admin = True
    self.uid = self.app_key = self.request.headers.get("uid", 0)

    if type(self.uid) != int and self.uid.isdigit():
        self.uid = int(self.uid)

    self.member = self.model.AdminModel.get_admin(self.uid)
    if not self.member:
        raise errors.MemberNotFound

    self.gid = self.member["gid"]

def _check_token(self, permission_bit):
    self.token = self.request.headers.get("token", "")
    token_debug = self.application.token_config.get("debug", False)
    if not token_debug:
        if permission_bit != 0:
            if not self.uid or not self.token:
                raise errors.ErrorTokenInvalid

            jwt = JWT.JwtToken(self.uid, self.application.token_config["secret"],
                               self.application.token_config["expire"])

            # if self.application.token_config["secret"] in ["******"]:
            #     return

            try:
                if not jwt.is_validate(self.token):
                    raise errors.ErrorTokenInvalid

                if jwt.is_expire(self.token):
                    raise errors.ErrorTokenExpireInvalid

                payload = jwt.decode(self.token)
                if payload and payload["uid"] != self.uid:
                    raise errors.ErrorTokenInvalid
            except Exception as e:
                raise errors.ErrorTokenInvalid


def verifi_sign(self, token, secret_key):
    """
    验签
    :param self:
    :param token:
    :param secret_key:
    :return:
    """
    if not self.application.app_config["security"]["verifi_sign"]:
        return

    if secret_key in ["******"]:
        return

    argument = get_argument(self)

    # ******
    sign = encode_sign(secret_key, **{k: v[0] for k, v in self.request.body_arguments.items()})

    # ******
    new_sign = new_encode_sign(secret_key, **argument)

    new_sign2 = new_encode_sign2(secret_key, **argument)

    if token != sign and token != new_sign and token != new_sign2:
        raise errors.ErrorTokenInvalid


def verifi_ip(self, ip_list):
    """
    验证白名单
    :param self:
    :param ip_list:
    :return:
    """
    if not self.application.app_config["security"]["verifi_ip"]:
        return

    ip_list = [ip.encode("u8") for ip in ip_list]
    remote_ip = self.request.remote_ip.encode("u8")
    s = "*" in ip_list or remote_ip in ip_list
    if not s:
        raise errors.ErrorTranIpError


def encode_sign(secret_key, **kwargs):
    """
    验签 1.0
    :param secret_key:
    :param kwargs:
    :return:
    """
    mapping = {}
    for k, v in kwargs.items():
        mapping[k.lower()] = v

    keys = [k.lower() for k in mapping.keys()]
    keys.sort()
    s = "&".join(["%s=%s" % (k, mapping[k]) for k in keys])
    # TODO ******json******，******str='"sign"'******
    s = utils.to_json(s)
    s = aes.AES(secret_key).encode(s)
    s = hmac.HMAC(secret_key.encode("u8"), s).hexdigest()
    # s = utils.enbase64(s)
    return s


def new_encode_sign(secret_key, **kwargs):
    """
    验签 2.0
    :param secret_key:
    :param kwargs:
    :return:
    """
    mapping = {}
    for k, v in kwargs.items():
        mapping[k.lower()] = v

    keys = [k.lower() for k in mapping.keys()]
    keys.sort()
    s = "&".join(["%s=%s" % (k, mapping[k]) for k in keys])
    s = aes.AES(secret_key).encode(s)
    s = hmac.HMAC(secret_key.encode("u8"), s).hexdigest()
    # s = utils.enbase64(s)
    return s


def new_encode_sign2(secret_key, **kwargs):
    """
    验签 3.0
    :param secret_key:
    :param kwargs:
    :return:
    """
    mapping = {}
    for k, v in kwargs.items():
        mapping[k.lower()] = v

    keys = [k.lower() for k in mapping.keys()]
    keys.sort()
    s = "&".join(["%s=%s" % (k, str(mapping[k])) for k in keys])
    s = s + "&secret_key=" + secret_key

    token = utils.md5(s)
    return token


def get_token_sign_func(token_version):
    """
    token******
    :param token_version:
    :return:
    """
    mp = {
        "v1": new_encode_sign,
        "v2": new_encode_sign2
    }
    return mp[token_version]


def get_excel_path(root_path, file_name=None):
    if not file_name:
        file_name = "%s.xlsx" % (datetime.now().strftime("%Y%m%d%H%M%S") + str(random.randint(0, 99)))

    path = datetime.now().strftime("%Y%m%d")

    base_path = 'data/excel'
    if not os.path.exists("%s/%s/%s" % (root_path, base_path, path)):
        os.makedirs("%s/%s/%s" % (root_path, base_path, path))

    save_path = "%s/%s/%s/%s" % (root_path, base_path, path, file_name)

    file_name = '%s/%s' % (path, file_name)

    return save_path, file_name


def get_now_time_tuple(ts):
    d = utils.int_to_date_string(ts, fm="%d")
    m = utils.int_to_date_string(ts, fm="%m")
    y = utils.int_to_date_string(ts, fm="%Y")
    return y, m, d


def gen_sign_str(params):
    """
    ******
    :param params:
    :return:
    """
    keys = [k for k, v in params.items() if v != "" and k != "sign"]
    keys.sort()
    message = "&".join(["%s=%s" % (k, str(params[k])) for k in keys])

    return message


def pc_or_mobile(ua):
    """
    判断客户端PC还是手机端
    :param ua: ******User-Agent******
    :return:
    """
    factor = ua
    is_mobile = False
    _long_matches = r'googlebot-mobile|android|avantgo|blackberry|blazer|elaine|hiptop|ip(hone|od)|kindle|midp|mmp' \
                    r'|mobile|o2|opera mini|palm( os)?|pda|plucker|pocket|psp|smartphone|symbian|treo|up\.(browser|link)' \
                    r'|vodafone|wap|windows ce; (iemobile|ppc)|xiino|maemo|fennec'
    _long_matches = re.compile(_long_matches, re.IGNORECASE)
    _short_matches = r'1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\-)|ai(ko|rn)|al(av|ca|co)' \
                     r'|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)' \
                     r'|bl(ac|az)|br(e|v)w|bumb|bw\-(n|u)|c55\/|capi|ccwa|cdm\-|cell|chtm|cldc|cmd\-|co(mp|nd)|craw' \
                     r'|da(it|ll|ng)|dbte|dc\-s|devi|dica|dmob|do(c|p)o|ds(12|\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8' \
                     r'|ez([4-7]0|os|wa|ze)|fetc|fly(\-|_)|g1 u|g560|gene|gf\-5|g\-mo|go(\.w|od)|gr(ad|un)|haie|hcit' \
                     r'|hd\-(m|p|t)|hei\-|hi(pt|ta)|hp( i|ip)|hs\-c|ht(c(\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\-(20|go|ma)' \
                     r'|i230|iac( |\-|\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji' \
                     r'|kgt( |\/)|klon|kpt |kwc\-|kyo(c|k)|le(no|xi)|lg( g|\/(k|l|u)|50|54|e\-|e\/|\-[a-w])|libw|lynx' \
                     r'|m1\-w|m3ga|m50\/|ma(te|ui|xo)|mc(01|21|ca)|m\-cr|me(di|rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi' \
                     r'|de|do|t(\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)' \
                     r'|10)|ne((c|m)\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg' \
                     r'|pg(13|\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\-2|po(ck|rt|se)|prox|psio|pt\-g|qa\-a|qc(07|12|21' \
                     r'|32|60|\-[2-7]|i\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\-' \
                     r'|oo|p\-)|sdk\/|se(c(\-|0|1)|47|mc|nd|ri)|sgh\-|shar|sie(\-|m)|sk\-0|sl(45|id)|sm(al|ar|b3|it' \
                     r'|t5)|so(ft|ny)|sp(01|h\-|v\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\-|tdg\-|tel(i|m)' \
                     r'|tim\-|t\-mo|to(pl|sh)|ts(70|m\-|m3|m5)|tx\-9|up(\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)' \
                     r'|vk(40|5[0-3]|\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\-| )|webc|whit' \
                     r'|wi(g |nc|nw)|wmlb|wonu|x700|xda(\-|2|g)|yas\-|your|zeto|zte\-'

    _short_matches = re.compile(_short_matches, re.IGNORECASE)

    if _long_matches.search(factor) != None:
        is_mobile = True
    user_agent = factor[0:4]
    if _short_matches.search(user_agent) != None:
        is_mobile = True

    return is_mobile


def get_ua_client(ua):
    """
    判断客户端是否为IOS
    :param ua:
    :return:
    """
    try:

        from user_agents import parse
        user_agent = parse(ua)

        if user_agent.is_pc:
            return 3
        else:
            if user_agent.os.family == 'iOS':
                return 1
            else:
                return 2
    except:
        return 0

def tts():
    return time.time() * 1000

def get_argument(self):
    """
    ******
    :param self:
    :return:
    """
    argument = {}
    try:
        keys = self.params.keys()
        for key in keys:
            if key == "secret_key":
                continue
            argument[key] = self.get_argument(key)
    except:
        argument = {k: v[0] for k, v in self.request.body_arguments.items() or self.request.arguments.items()}

    return argument


