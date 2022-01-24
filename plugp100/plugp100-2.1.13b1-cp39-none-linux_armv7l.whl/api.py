import base64
import dataclasses
import logging
from time import time
from typing import Any, Dict, Optional

import aiohttp
import jsons

from plugp100.core import helpers
from plugp100.core.encryption import Encryption
from plugp100.core.exceptions import TapoException
from plugp100.core.exceptions.TapoException import TapoException
from plugp100.core.http_client import AsyncHttp
from plugp100.core.key_pair import KeyPair
from plugp100.core.methods import GetDeviceInfoMethod, taporequest
from plugp100.core.methods import HandshakeMethod
from plugp100.core.methods import LoginDeviceMethod
from plugp100.core.methods import SecurePassthroughMethod
from plugp100.core.methods.get_energy_usage import GetEnergyUsageMethod
from plugp100.core.methods.set_device_info_method import SetDeviceInfoMethod
from plugp100.core.params import HandshakeParams
from plugp100.core.params import LoginDeviceParams
from plugp100.core.params.device_info_params import DeviceInfoParams, SwitchParams, LightParams
from plugp100.core.tp_link_cipher import TpLinkCipher

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class EnergyInfo:
    today_runtime: float = property(lambda self: self.info["today_runtime"])
    month_runtime: float = property(lambda self: self.info["month_runtime"])
    today_energy: float = property(lambda self: self.info["today_energy"])
    month_energy: float = property(lambda self: self.info["month_energy"])
    current_power: float = property(lambda self: self.info["current_power"])

    def __init__(self, info: Dict[str, Any]):
        self.info = info


@dataclasses.dataclass
class TapoDeviceState:
    device_id: str = property(lambda self: self.state["device_id"])
    mac: str = property(lambda self: self.state["mac"])
    nickname: str = property(lambda self: base64.b64decode(self.state["nickname"]).decode("UTF-8"))
    model: str = property(lambda self: self.state["model"])
    type: str = property(lambda self: self.state["type"])
    device_on: bool = property(lambda self: self.state["device_on"])
    brightness: Optional[int] = property(lambda self: self.state["brightness"] if "brightness" in self.state else None)
    hue: Optional[int] = property(lambda self: self.state["hue"] if "hue" in self.state else None)
    saturation: Optional[int] = property(lambda self: self.state["saturation"] if "saturation" in self.state else None)
    color_temp: Optional[int] = property(lambda self: self.state["color_temp"] if "color_temp" in self.state else None)
    overheated: bool = property(lambda self: self.state["overheated"])
    signal_level: int = property(lambda self: self.state["signal_level"])
    rssi: int = property(lambda self: self.state["rssi"])
    energy_info: EnergyInfo = property(lambda self: self._energy_info)

    def __init__(self, state: Dict[str, Any], energy_info: EnergyInfo):
        self.state = state
        self._energy_info = energy_info


class TapoApiClient:
    TERMINAL_UUID = "88-00-DE-AD-52-E1"

    def __init__(self, address: str, username: str, password: str, session: aiohttp.ClientSession = None):
        self.address = address
        self.username = username
        self.password = password
        self.url = f"http://{address}/app"
        logger.debug(f"Device url is: {self.url}")

        self.encryption = Encryption()
        self.key_pair: KeyPair
        self.cookie_token: str = ""
        self.token: str = ""

        self.http = AsyncHttp(aiohttp.ClientSession() if session is None else session)
        self.tp_link_cipher: TpLinkCipher = None

    async def login(self):
        await self._handshake()
        await self._login_request(self.username, self.password)

    async def get_state(self) -> TapoDeviceState:
        return TapoDeviceState(
            state=await self.get_state_as_dict(),
            energy_info=await self.get_energy_usage()
        )

    async def set_device_info(self, device_params: DeviceInfoParams, terminal_uuid: str = TERMINAL_UUID):
        await self._set_device_info(device_params.as_dict(), terminal_uuid)

    async def _set_device_info(self, device_params: Dict[str, Any], terminal_uuid: str = TERMINAL_UUID):
        logger.debug(f"Device info will change to: {device_params}")

        device_info_method = SetDeviceInfoMethod(device_params)
        device_info_method.set_request_time_milis(time())
        device_info_method.set_terminal_uuid(terminal_uuid)
        logger.debug(f"Device info method: {jsons.dumps(device_info_method)}")

        dim_encrypted = self.tp_link_cipher.encrypt(jsons.dumps(device_info_method))
        logger.debug(f"Device info method encrypted: {dim_encrypted}")

        secure_passthrough_method = SecurePassthroughMethod(dim_encrypted)
        logger.debug(f"Secure passthrough method: {secure_passthrough_method}")
        request_body = jsons.loads(jsons.dumps(secure_passthrough_method))
        logger.debug(f"Request body: {request_body}")

        response = await self.http.async_make_post_cookie(f"{self.url}?token={self.token}", request_body,
                                                          {'TP_SESSIONID': self.cookie_token})
        resp_dict = await response.json()
        logger.debug(f"Device responded with: {resp_dict}")

        self.__validate_response(resp_dict)

        decrypted_inner_response = jsons.loads(
            self.tp_link_cipher.decrypt(
                resp_dict['result']['response']
            ))
        logger.debug(f"Device inner response: {decrypted_inner_response}")
        self.__validate_response(decrypted_inner_response)

    async def on(self):
        return await self.set_device_info(SwitchParams(True))

    async def off(self):
        return await self.set_device_info(SwitchParams(False))

    async def set_brightness(self, brightness: int):
        return await self.set_device_info(LightParams(brightness=brightness))

    async def set_color_temperature(self, color_temperature: int):
        return await self.set_device_info(LightParams(color_temperature=color_temperature))

    async def set_hue_saturation(self, hue: int, saturation: int):
        return await self.set_device_info(LightParams(hue=hue, saturation=saturation))

    async def _handshake(self):
        logger.debug("Will perform handshaking...")

        logger.debug("Generating keypair")
        self.__generate_keypair()

        handshake_params = HandshakeParams(self.key_pair.get_public_key())
        logger.debug(f"Handshake params: {jsons.dumps(handshake_params)}")

        handshake_method = HandshakeMethod(handshake_params)
        logger.debug(f"Handshake method: {jsons.dumps(handshake_method)}")

        request_body = jsons.dump(handshake_method)
        logger.debug(f"Request body: {request_body}")

        response = await self.http.async_make_post(self.url, json=request_body)
        resp_dict = await response.json()
        logger.debug(f"Device responded with: {resp_dict}")
        self.__validate_response(resp_dict)
        self.cookie_token = response.cookies.get('TP_SESSIONID').value
        logger.debug(f"Got TP_SESSIONID token: ...{self.cookie_token[5:]}")

        logger.debug("Decoding handshake key...")
        self.tp_link_cipher = self.encryption.decode_handshake_key(resp_dict['result']['key'], self.key_pair)

    async def _login_request(self, username: str, password: str):
        logger.debug(f"Will login using username '{username[5:]}...'")
        digest_username = self.encryption.sha_digest_username(username)
        logger.debug(f"Username digest: ...{digest_username[:5]}")

        login_device_params = LoginDeviceParams(
            helpers.mime_encoder(password.encode("UTF-8")),
            helpers.mime_encoder(digest_username.encode("UTF-8"))
        )

        l_ldp = jsons.dumps(login_device_params).replace(helpers.mime_encoder(password.encode("UTF-8")),
                                                         "PASSWORD_REMOVED")
        logger.debug(f"Login device params: {l_ldp}")

        login_device_method = LoginDeviceMethod(login_device_params)
        login_device_method.set_request_time_milis(time())
        l_ldm = jsons.dumps(login_device_method).replace(helpers.mime_encoder(password.encode("UTF-8")),
                                                         "PASSWORD_REMOVED")
        logger.debug(f"Login device method: {l_ldm}")

        ldm_encrypted = self.tp_link_cipher.encrypt(jsons.dumps(login_device_method))
        logger.debug(f"Login device method encrypted: {ldm_encrypted}")

        secure_passthrough_method = SecurePassthroughMethod(ldm_encrypted)
        logger.debug(f"Secure passthrough method: {jsons.dumps(secure_passthrough_method)}")
        request_body = jsons.loads(jsons.dumps(secure_passthrough_method))
        logger.debug(f"Request body: {request_body}")

        response = await self.http.async_make_post_cookie(self.url, request_body,
                                                          {'TP_SESSIONID': self.cookie_token})
        resp_dict: dict = await response.json()
        logger.debug(f"Device responded with: {resp_dict}")

        self.__validate_response(resp_dict)

        decrypted_inner_response = jsons.loads(
            self.tp_link_cipher.decrypt(
                resp_dict['result']['response']
            )
        )

        logger.debug(f"Device inner response: {decrypted_inner_response}")

        self.token = decrypted_inner_response['result']['token']

    async def get_state_as_dict(self) -> Dict[str, Any]:
        device_info_method = GetDeviceInfoMethod(None)
        return await self._execute_method_request(device_info_method)

    async def get_energy_usage(self) -> Optional[EnergyInfo]:
        try:
            return EnergyInfo(
                await self._execute_method_request(GetEnergyUsageMethod(None))
            )
        except (Exception,):
            return None

    async def _execute_method_request(self, method: taporequest.TapoRequest) -> Dict[str, Any]:
        logger.debug(f"Method request: {jsons.dumps(method)}")
        dim_encrypted = self.tp_link_cipher.encrypt(jsons.dumps(method))
        logger.debug(f"Method request encrypted: {dim_encrypted}")

        secure_passthrough_method = SecurePassthroughMethod(dim_encrypted)
        logger.debug(f"Secure passthrough method: {secure_passthrough_method}")
        request_body = jsons.loads(jsons.dumps(secure_passthrough_method))
        logger.debug(f"Request body: {request_body}")

        response = await self.http.async_make_post_cookie(f"{self.url}?token={self.token}", request_body,
                                                          {'TP_SESSIONID': self.cookie_token})
        resp_dict: dict = await response.json()
        logger.debug(f"Device responded with: {resp_dict}")

        self.__validate_response(resp_dict)

        decrypted_inner_response = jsons.loads(
            self.tp_link_cipher.decrypt(
                resp_dict['result']['response']
            ))
        logger.debug(f"Device inner response: {decrypted_inner_response}")
        self.__validate_response(decrypted_inner_response)

        return decrypted_inner_response['result']

    def __generate_keypair(self):
        self.key_pair = self.encryption.generate_key_pair()

    def __validate_response(self, resp: dict):
        if 'error_code' not in resp:
            logger.warning("No error_code in the response!")
        else:
            if resp['error_code'] != 0:
                raise TapoException.from_error_code(resp['error_code'])
