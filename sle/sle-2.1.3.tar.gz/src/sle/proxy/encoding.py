from pyasn1.codec.ber.encoder import encode as asn1_encode
from pyasn1.codec.der.decoder import decode as asn1_decode
import pyasn1.error

from sle import logger


class DataEncodingLayer:

    def __init__(self, proxy, provider_to_user_pdu):
        self._proxy = proxy
        self._provider_to_user_pdu = provider_to_user_pdu()

    def sle_pdu_request(self, pdu):
        encoded_pdu = asn1_encode(pdu)
        self._proxy.transport.sle_pdu_request(encoded_pdu)

    def sle_pdu_indication(self, encoded_pdu):
        try:
            pdu = asn1_decode(
                encoded_pdu, asn1Spec=self._provider_to_user_pdu)[0]
        except pyasn1.error.PyAsn1Error as e:
            logger.error("Unable to decode PDU:", e)
            return
        except TypeError:
            logger.error(
                "Unable to decode PDU due to type error. Skipping...")
            return
        self._proxy.authentication.sle_pdu_indication(pdu)
