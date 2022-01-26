"""
register and verify
"""

from dataclasses import dataclass, field
from typing import Optional

from sanic import Blueprint
from sanic.log import logger
from sanic.response import json
from sanic_ext import openapi, validate
from signal_cli_dbus_rest_api.dataclasses import Error
from signal_cli_dbus_rest_api.lib.dbus import SignalCLIDBus

register_v1 = Blueprint("register_v1", url_prefix="/register")
verify_v1 = Blueprint("verify_v1", url_prefix="/register")


@dataclass
class RegisterV1PostParams:
    """
    RegisterV1PostParams
    """

    captcha: Optional[str]
    use_voice: Optional[bool] = False


@register_v1.middleware("request")
async def register_post_dummy_body(request):
    """
    Create empty dummy body for @validate
    if there is none in request
    """
    if not request.body:
        request.body = b"{}"


@register_v1.post("/<number:path>", version=1)
@openapi.tag("Devices")
@openapi.parameter("number", str, required=True, location="path")
@openapi.body({"application/json": RegisterV1PostParams})
@openapi.response(201, {"application/json": None}, description="Created")
@openapi.response(400, {"application/json": Error}, description="Bad Request")
@openapi.description("Register a phone number with the signal network.")
@validate(RegisterV1PostParams)
async def register_post(
    request, number, body: RegisterV1PostParams
):  # pylint: disable=unused-argument
    """
    Register a phone number.
    """
    opts = [number, body.use_voice]
    try:
        dbus = SignalCLIDBus()
        if body.captcha:
            method = dbus.pydbusconn.registerWithCaptcha
            opts.append(body.captcha)
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
        error = getattr(err, 'message', repr(err))
        logger.error(error)
        return json({"error": error}, 400)


@dataclass
class VerifyV1PostParams:
    """
    VerifyV1PostParams
    """

    pin: Optional[str] = field(default_factory=str)


@verify_v1.middleware("request")
async def verify_post_dummy_body(request):
    """
    Create empty dummy body for @validate
    if there is none in request
    """
    if not request.body:
        request.body = b"{}"


@verify_v1.post("/<number:path>/verify/<token:path>", version=1)
@openapi.tag("Devices")
@openapi.parameter("number", str, required=True, location="path")
@openapi.parameter("token", str, required=True, location="path")
@openapi.body({"application/json": VerifyV1PostParams})
@openapi.response(201, {"application/json": None}, description="Created")
@openapi.response(400, {"application/json": Error}, description="Bad Request")
@openapi.description("Verify a registered phone number with the signal network.")
@validate(VerifyV1PostParams)
async def verify_post(
    request, number, token, body: VerifyV1PostParams
):  # pylint: disable=unused-argument
    """
    Verify a registered phone number.
    """
    opts = [number, token]
    try:
        dbus = SignalCLIDBus()
        if body.pin:
            method = dbus.pydbusconn.verifyWithPin
            opts.append(body.pin)
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
        error = getattr(err, 'message', repr(err))
        logger.error(error)
        return json({"error": error}, 400)
