"""
register and verify
"""

from typing import Optional
from dataclasses import dataclass, field
from sanic import Blueprint
from sanic.log import logger
from sanic.response import json
from sanic_ext import openapi, validate
from signal_cli_dbus_rest_api.lib.dbus import SignalCLIDBus
from signal_cli_dbus_rest_api.dataclasses import Error

register = Blueprint("register", url_prefix="/register")
verify = Blueprint("verify", url_prefix="/register")


@dataclass
class RegisterV1PostParams:
    """
    RegisterV1PostParams
    """
    captcha: Optional[str]
    use_voice: Optional[bool] = False


@register.post("/<number:path>", version=1)
@openapi.tag("Devices")
@openapi.parameter("number", str, required=True, location="path")
@openapi.body({"application/json": RegisterV1PostParams})
@openapi.response(201, {"application/json": None}, description="Created")
@openapi.response(400, {"application/json": Error}, description="Bad Request")
@openapi.description("Register a phone number with the signal network.")
@validate(json=RegisterV1PostParams)
async def register_post(request, number, body: RegisterV1PostParams):  # pylint: disable=unused-argument
    """
    Register a phone number.
    """
    use_voice = request.json.get("use_voice", False)
    captcha = request.json.get("captcha", "")
    opts = [number, use_voice]
    try:
        dbus = SignalCLIDBus()
        if captcha:
            method = dbus.pydbusconn.registerWithCaptcha
            opts.append(captcha)
        else:
            method = dbus.pydbusconn.register
        result = method(*opts)
        # successful verification just returns None
        if result:
            logger.info(result)
            return json({"error": result}, 400)
        return json(None, 200)
    # pylint: disable=broad-except
    except Exception as err:
        logger.error(err)
        return json({"error": err.__repr__()}, 400)


@dataclass
class VerifyV1PostParams:
    """
    VerifyV1PostParams
    """
    pin: Optional[str] = field(default_factory=str)


@verify.post("/<number:path>/verify/<token:path>", version=1)
@openapi.tag("Devices")
@openapi.parameter("number", str, required=True, location="path")
@openapi.parameter("token", str, required=True, location="path")
@openapi.body({"application/json": VerifyV1PostParams})
@openapi.response(201, {"application/json": None}, description="Created")
@openapi.response(400, {"application/json": Error}, description="Bad Request")
@openapi.description("Verify a registered phone number with the signal network.")
async def verify_post(request, number, token):  # pylint: disable=unused-argument
    """
    Verify a registered phone number.
    """
    pin = None
    if request.json:
        pin = request.json.get("pin")
    opts = [number, token]
    try:
        dbus = SignalCLIDBus()
        if pin:
            method = dbus.pydbusconn.verifyWithPin
            opts.append(pin)
        else:
            method = dbus.pydbusconn.verify
        result = method(*opts)
        # successful verification just returns None
        if result:
            logger.info(result)
            return json({"error": result}, 400)
        return json(None, 200)
    # pylint: disable=broad-except
    except Exception as err:
        logger.error(err)
        return json({"error": err.__repr__()}, 400)
