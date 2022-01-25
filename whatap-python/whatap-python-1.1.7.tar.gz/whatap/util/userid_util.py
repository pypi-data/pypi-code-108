from whatap.util.hash_util import HashUtil as hash_util
from whatap.util.hexa32 import Hexa32 as hexa32
from whatap.util.keygen import KeyGen
import whatap.util.bit_util as bit_util
from whatap.conf.configure import Configure as conf
import logging as logging_module
import sys,  traceback

logger = logging_module.getLogger(__name__)

def toDjangoHeaderName(src):

    return 'HTTP_' + src.upper().replace('-','_')

class UseridUtil(object):
    WHATAP_R = "WHATAP"

    @staticmethod
    def getUserId(req,  defValue):
        try:

            if conf.user_header_ticket:
                ticket = UseridUtil.getHeader(req, conf.user_header_ticket)
                if  ticket:
                    return hash_util.hashFromString(ticket), ticket
                return 0,""
            cookie = UseridUtil.getHeader(req, "Cookie")
            if cookie:
                if len(cookie) >= conf.trace_user_cookie_limit :
                    return defValue

                x1 = cookie.find(UseridUtil.WHATAP_R)
                if x1 >= 0:
                    x2 = cookie.find(';', x1)
                    if x2 > 0:
                        value = cookie[x1 + len(UseridUtil.WHATAP_R) + 1: x2]
                    else:
                        value = cookie[x1 + len(UseridUtil.WHATAP_R) + 1:]
                    return hexa32.toLong32(value), value
            userid=KeyGen.next()
            return userid, hexa32.toString32(userid)
        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            logger.debug("A502",10, str(exc_value))

    @staticmethod
    def setUserId(req, res, cookieValue):
        try:
            if not conf.user_header_ticket:
                cookie = UseridUtil.getHeaderEx(req, "Cookie")
                if not cookie:
                    UseridUtil.setCookie(res, UseridUtil.WHATAP_R, cookieValue, bit_util.INT_MAX_VALUE, "/", conf.trace_user_cookie_domain )
        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            logger.debug("A503", 10, str(exc_value))

    @staticmethod
    def DEPRECATED_getUserid(req, res, defValue):
        try:
            if conf.user_header_ticket_enabled:
                ticket = UseridUtil.getHeader(req, conf.user_header_ticket)
                if  ticket:
                    return hash_util.hash(ticket)
                return 0
            cookie = UseridUtil.getHeader(req, "Cookie")
            if cookie:
                if len(cookie) >= conf.trace_user_cookie_limit :
                    return defValue

                x1 = cookie.find(UseridUtil.WHATAP_R)
                if x1 >= 0:
                    x2 = cookie.find(';', x1)
                    if x2 > 0:
                        value = cookie[x1 + len(UseridUtil.WHATAP_R) + 1: x2]
                    else:
                        value = cookie[x1 + len(UseridUtil.WHATAP_R) + 1:]
                    return hexa32.toLong32(value)
            UseridUtil.setCookie(res, UseridUtil.WHATAP_R, hexa32.toString32(KeyGen.next()), bit_util.INT_MAX_VALUE, "/", conf.trace_user_cookie_domain )

        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            logger.debug("A502",10, str(exc_value))

        return defValue

    META_DICT = {'django': lambda x, name: x.get(toDjangoHeaderName(name))}

    @staticmethod
    def getHeader(args, name):
        for arg in args:
            if isinstance(arg, dict):
                if name in arg:
                    return arg[name]
                else:
                    for  fn in UseridUtil.META_DICT.values():
                        v = fn(arg, name)
                        if v:
                            return v

        return None

    GET_HEADER={'META': lambda x : x.META.get}
    @staticmethod
    def getHeaderEx(req, name):
        name = toDjangoHeaderName(name)

        for k, fn in UseridUtil.GET_HEADER.items():
            if hasattr(req, k):
                return fn(req)(name)

        return None

    SETCOOKIE_METHODS={
       "set_cookie": lambda res, key, value, max_age, path, domain : res.set_cookie(key, value, max_age = max_age, path=path, domain=domain )
    }
    @staticmethod
    def setCookie(res, key, value, max_age, path, domain):
        for mname, fn in UseridUtil.SETCOOKIE_METHODS.items():
            if hasattr(res, mname):
                fn(res, key, value, max_age, path, domain)
                break

    @staticmethod
    def getRemoteAddr(args):
        if conf.trace_http_client_ip_header_key:
            header_val = UseridUtil.getHeader(args, conf.trace_http_client_ip_header_key)
            if header_val:
                return header_val.split(',')[0].strip()

        return UseridUtil.getHeader(args, "REMOTE_ADDR")