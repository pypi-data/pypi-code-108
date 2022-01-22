import jwt
import re
import inspect
import types
import functools
from .config import _JWTConfig
from fly import Fly
from fly.types import Request
from fly.exceptions import HTTPException, HTTP401Exception, HTTP500Exception
from fly.response import Response
from fly._parse import RequestParser

def _re_bearer(header_value):
    res = re.match(r'^Bearer (.+)$', header_value)
    if res is not None and len(res.groups()) == 1:
        return res[1]
    else:
        return None

_JWT_KEY_NAME="jwt_payload"
def require_jwt(
    **kwargs
):
    def _jwt(func):
        if not isinstance(func.__name__, str):
            raise TypeError("Invalid function name")

        def _fly_jwt(request: Request):
            _conf = _fly_jwt._jwt_config
            _auth = _conf.auth_handler
            _func = _conf.success_handler
            if _func is None:
                raise ValueError("Unknown success handler")
            if _auth is None:
                raise ValueError("not found authenticate handler")

            try:
                _jwt = FlyJWT(_conf)
                if request.get("header") is None:
                    raise HTTP401Exception(
                            "fly_jwt must have header key in dict of request"
                            )
                for item in request["header"]:
                    if item["name"] == "authorization":
                        encoded = _re_bearer(item["value"])
                        if encoded is None:
                            raise HTTP401Exception("There is no fly_jwt token in `Authorization: Bearer $token$`.")
                        try:
                            decoded = _jwt.decode(encoded)
                        except jwt.PyJWTError as e:
                            raise HTTP401Exception(f"JWT Decode Error: {str(e)}")
                        try:
                            res = _auth(decoded)
                            if res is None or not isinstance(res, bool):
                                raise TypeError("Return type must be bool type.")
                            if not res:
                                raise HTTP401Exception("Authentication failure")
                            else:
                                # Successful authentication !
                                request[_JWT_KEY_NAME] = decoded

                                _parser = RequestParser(_func)
                                print(request)
                                _parse_res = _parser.parse_func_args(request)
                                _args = _parse_res["args"]
                                _kwargs = _parse_res["kwargs"]
                                return _func(*_args, **_kwargs)
                        except HTTP401Exception as e:
                            raise HTTP401Exception(str(e))

                raise HTTP401Exception("Not found Authorization item in HTTP request header.")
            except HTTP401Exception as e:
                _fail = _conf.fail_handler
                if _fail is None:
                    raise HTTP401Exception(str(e))
                else:
                    args = list()
                    kwargs = dict()
                    _fullargspec = inspect.getfullargspec(_fail)
                    _args = _fullargspec.args
                    _kwargs = _fullargspec.varkw
                    if len(_args) == 1:
                        args.append(str(e))
                    elif len(_args) == 0 and _kwargs is not None:
                        kwargs["error"] = e
                    return _fail(*args, **kwargs)

        _conf = _JWTConfig(func, **kwargs)
        setattr(_fly_jwt, "_jwt_config", _conf)
        _fly_jwt.__name__ = func.__name__
        return _fly_jwt
    return _jwt

class FlyJWT:
    def __init__(self, conf):
        if not isinstance(conf, _JWTConfig):
            raise TypeError("FlyJWT must pass _JWTConfig instance.")

        self._conf = conf

    def decode(self, encoded, **kwargs):
        return jwt.decode(
            encoded,
            self._conf.private_key \
                    if self._conf._symmetric else \
                    self._conf.public_key,
            algorithms=self._conf.algorithm,
            **kwargs
        )

    def encode(self, payload):
        return jwt.encode(
            payload,
            self._conf.private_key,
            algorithm=self._conf.algorithm,
        )
