"""XMPP Connector to talk to bosch."""
import aioxmpp
from bosch_thermostat_client.const import PUT, GET, USER_AGENT, CONTENT_TYPE, APP_JSON
from bosch_thermostat_client.const.ivt import TELEHEATER
from .xmpp import XMPPBaseConnector


class IVTXMPPConnector(XMPPBaseConnector):
    _accesskey_prefix = "C6u9jPue_"
    _rrc_contact_prefix = "contact_"
    _rrc_gateway_prefix = "gateway_"
    xmpp_host = "wa2-mz36-qrmzh6.bosch.de"

    def __init__(self, host, access_key, encryption, **kwargs):
        """IVTConnector constructor

        Args:
            host (str): serialnumber of target
            access_key (str): access key to bosch
            encryption (obj): Encryption object
        """
        self._seqno = 1
        super().__init__(host=host, access_key=access_key, encryption=encryption)

    def _build_message(self, method, path, data=None):
        if not path:
            return
        msg = aioxmpp.stanza.Message(
            to=self._to,
            type_=aioxmpp.MessageType.CHAT,
        )
        msg.autoset_id()
        if method == GET:
            body = "\r\r".join(
                [
                    f"GET {path} HTTP/1.1",
                    f"{USER_AGENT}: {TELEHEATER}",
                    f"Seq-No: {self._seqno}",
                    "\r\r",
                ]
            )
        elif method == PUT and data:
            body = "\r\r".join(
                [
                    f"PUT {path} HTTP/1.1",
                    f"{USER_AGENT}: {TELEHEATER}",
                    f"{CONTENT_TYPE}: {APP_JSON}",
                    f"Content-Length: {len(data)}",
                    f"Seq-No: {self._seqno}",
                    "",
                    data.decode("utf-8"),
                ]
            )
        else:
            return
        msg.body[None] = body
        self._seqno += 1
        return msg
