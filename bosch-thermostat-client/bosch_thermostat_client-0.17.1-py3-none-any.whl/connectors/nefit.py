"""XMPP Connector to talk to bosch."""
import logging

import aioxmpp
from bosch_thermostat_client.const import PUT, GET, USER_AGENT, CONTENT_TYPE, APP_JSON
from bosch_thermostat_client.const.nefit import NEFITEASY
from .xmpp import XMPPBaseConnector

_LOGGER = logging.getLogger(__name__)


class NefitConnector(XMPPBaseConnector):
    _accesskey_prefix = "Ct7ZR03b_"
    _rrc_contact_prefix = "rrccontact_"
    _rrc_gateway_prefix = "rrcgateway_"
    xmpp_host = "wa2-mz36-qrmzh6.bosch.de"

    def _build_message(self, method, path, data=None):
        msg = aioxmpp.stanza.Message(
            to=self._to,
            type_=aioxmpp.MessageType.CHAT,
        )
        if method == GET:
            body = "\r\r".join(
                [f"GET {path} HTTP/1.1", f"{USER_AGENT}: {NEFITEASY}", "\r\r"]
            )
        elif method == PUT and data:
            body = "\r\r".join(
                [
                    f"PUT {path} HTTP/1.1",
                    f"{USER_AGENT}: {NEFITEASY}",
                    f"{CONTENT_TYPE}: {APP_JSON}",
                    f"Content-Length: {len(data)}",
                    "",
                    data.decode("utf-8"),
                    "\r\r",
                ]
            )
        msg.body[None] = body
        return msg
