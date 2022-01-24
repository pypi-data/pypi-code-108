"""XMPP Connector to talk to bosch."""

import aioxmpp
from bosch_thermostat_client.const import (
    PUT,
    GET,
    USER_AGENT,
    CONTENT_TYPE,
    APP_JSON,
    ACCESS_KEY,
)
from .xmpp import XMPPBaseConnector

USERAGENT = "rrc2"


class EasycontrolConnector(XMPPBaseConnector):
    xmpp_host = "xmpp.rrcng.ticx.boschtt.net"
    _accesskey_prefix = "C42i9NNp_"
    _rrc_contact_prefix = "rrc2contact_"
    _rrc_gateway_prefix = "rrc2gateway_"
    no_verify = True

    def __init__(self, host, encryption, **kwargs):
        self._seqno = 0
        super().__init__(
            host=host,
            encryption=encryption,
            access_key=kwargs.get(ACCESS_KEY),
        )

    def _build_message(self, method, path, data=None):
        msg = aioxmpp.stanza.Message(
            to=self._to,
            type_=aioxmpp.MessageType.CHAT,
        )
        if method == GET:
            body = "\n".join(
                [
                    f"GET {path} HTTP/1.1",
                    f"{USER_AGENT}: {USERAGENT}",
                    f"Seq-No: {self._seqno}",
                    "\n",
                ]
            )
        elif method == PUT and data:
            body = "\r".join(
                [
                    f"PUT {path} HTTP/1.1",
                    f"{USER_AGENT}: {USERAGENT}",
                    f"{CONTENT_TYPE}: {APP_JSON}",
                    f"Content-Length: {len(data)}",
                    "",
                    data.decode("utf-8"),
                    "\r",
                ]
            )
        msg.body[None] = body
        self._seqno += 1
        return msg
