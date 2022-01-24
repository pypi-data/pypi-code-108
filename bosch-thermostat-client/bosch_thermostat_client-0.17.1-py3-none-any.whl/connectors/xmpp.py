"""XMPP Connector to talk to bosch."""
import logging
import json
import re


import asyncio
from contextlib import AsyncExitStack
import aioxmpp
from aioxmpp.version.xso import Query

from bosch_thermostat_client.exceptions import (
    DeviceException,
    MsgException,
    EncryptionException,
)
from bosch_thermostat_client.const import (
    GET,
    PUT,
    REQUEST_TIMEOUT,
    BODY_400,
    WRONG_ENCRYPTION,
    ACCESS_KEY,
)

_LOGGER = logging.getLogger(__name__)


class XMPPBaseConnector:
    no_verify = False

    def __init__(self, host, encryption, **kwargs):
        """
        :param host: aka serial number
        :param password:
        """
        self.serial_number = host
        self._encryption = encryption
        self._lock = asyncio.Lock()

        identifier = self.serial_number + "@" + self.xmpp_host
        self._from = self._rrc_contact_prefix + identifier
        self._to = self.jid(self._rrc_gateway_prefix + identifier)
        self._jid = self.jid(self._from)
        self.xmppclient = aioxmpp.PresenceManagedClient(
            self._jid,
            aioxmpp.make_security_layer(
                self._accesskey_prefix + kwargs.get(ACCESS_KEY),
                no_verify=self.no_verify,
            ),
        )
        self.message_dispatcher = self.xmppclient.summon(
            aioxmpp.dispatcher.SimpleMessageDispatcher
        )
        self._st = AsyncExitStack()
        self.listeners = set()
        self._xmppstream = None
        self.message_dispatcher.register_callback(
            aioxmpp.MessageType.NORMAL,
            None,
            self.main_listener,
        )
        self.message_dispatcher.register_callback(
            aioxmpp.MessageType.CHAT,
            None,
            self.main_listener,
        )

        async def handler(iq):
            result = Query()
            result.name = "com.bosch.tt.buderus.controlng"
            result.version = "3.6.0"
            result.os = ""
            return result

        self.xmppclient.stream.register_iq_request_handler(
            aioxmpp.IQType.GET,
            Query,
            handler,
        )

    @property
    def encryption_key(self):
        return self._encryption.key

    def jid(self, _from):
        return aioxmpp.JID.fromstr(_from)

    def _build_message(self, method, path, data=None):
        pass

    async def get(self, path):
        _LOGGER.debug("Sending GET request to %s by %s", path, id(self))
        data = await self._request(method=GET, path=path)
        _LOGGER.debug("Response to GET request %s: %s", path, json.dumps(data))
        if not data:
            raise DeviceException(f"Error requesting data from {path}")
        return data

    async def put(self, path, value):
        _LOGGER.debug("Sending PUT request to %s with value %s", path, value)
        data = await self._request(
            method=PUT,
            encrypted_msg=self._encryption.encrypt(json.dumps({"value": value})),
            path=path,
            timeout=10,
        )
        if data:
            return True

    async def start(self):
        if not self._xmppstream:
            self._xmppstream = await self._st.enter_async_context(
                self.xmppclient.connected()
            )

    async def close(self, force):
        await asyncio.wait_for(self._st.aclose(), 10)

    async def _request(self, method, path, encrypted_msg=None, timeout=REQUEST_TIMEOUT):
        data = None
        try:
            if not self._xmppstream:
                await self.start()
        except asyncio.TimeoutError:
            _LOGGER.error(
                "Can't connect to XMPP server!. Check your network connection or credentials!"
            )
            return None
        await self._lock.acquire()
        try:
            msg_to_send = self._build_message(
                method=method, path=path, data=encrypted_msg
            )
            future = asyncio.Future()

            def listener(recv_body, http_response):
                if future.done() or future.cancelled():
                    _LOGGER.debug(
                        "Future is already done. If it happens too often that it might be a bug. Report it."
                    )
                    return
                if method == PUT and http_response == "HTTP/1.0 204 No Content":
                    future.set_result(True)
                if recv_body == BODY_400:
                    future.set_exception(MsgException("400 HTTP Error"))
                elif recv_body is None and http_response == WRONG_ENCRYPTION:
                    future.set_exception(MsgException("Can't decrypt for %s" % path))
                elif method == GET and recv_body.get("id") in path:
                    try:
                        future.set_result(recv_body)
                    except (asyncio.InvalidStateError) as err:
                        _LOGGER.error(
                            "If you see this log please attach it to your issue/send it on Discord. Err message: %s. Recv body: %s, Path: %s",
                            err,
                            json.dumps(recv_body),
                            path,
                        )
                        self._xmppstream = None
                        pass

            try:
                self.listeners.add(listener)
                await self._xmppstream.send(msg_to_send)
                data = await asyncio.wait_for(future, timeout)
            except (asyncio.TimeoutError, MsgException):
                _LOGGER.info("Msg exception for %s", path)
            except (asyncio.InvalidStateError) as err:
                _LOGGER.error("Unknown error occured. Please check logs. %s", err)
            finally:
                self.listeners.remove(listener)
        finally:
            self._lock.release()
            return data

    def main_listener(self, msg):
        def notify_error(body, response):
            if len(self.listeners) == 1:
                for listener in self.listeners:
                    listener(body, response)
                    break

        if not msg.body:
            return
        try:
            body = msg.body.lookup([aioxmpp.structs.LanguageRange.fromstr("*")]).split(
                "\n"
            )
        except AttributeError:
            return
        http_response = body[0]
        if re.match(r"HTTP/1.[0-1] 20*", http_response):
            try:
                body = self._encryption.json_encrypt(body[-1:][0])
            except EncryptionException:
                notify_error(body=None, response=WRONG_ENCRYPTION)
            else:
                for listener in self.listeners:
                    listener(body, http_response)
            return
        if re.match(r"HTTP/1.[0-1] 40*", http_response):
            _LOGGER.info(f"400 HTTP Error - {body}")
            notify_error(body=BODY_400, response=http_response)
