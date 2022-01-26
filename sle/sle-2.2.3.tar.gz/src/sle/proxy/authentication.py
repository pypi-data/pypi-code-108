import datetime as dt
import random
import struct
import hashlib

from pyasn1.codec.ber.encoder import encode as asn1_encode
from pyasn1.codec.der.encoder import encode as asn1_der_encode
from pyasn1.codec.der.decoder import decode as asn1_decode

from sle import logger
from sle.datatypes.security import HashInput, Isp1Credentials


class AuthenticationLayer:

    def __init__(
            self,
            proxy,
            local_identifier, peer_identifier,
            local_password=None, peer_password=None,
            auth_level='none'):
        self._proxy = proxy
        self._peer_identifier = peer_identifier
        self._peer_password = peer_password
        self._auth_level = auth_level

        self.local_credentials = None
        self.peer_credentials = None

        if local_password:
            self.local_credentials = self._make_credentials(
                local_identifier, local_password)
        if peer_password:
            self.peer_credentials = self._make_credentials(
                peer_identifier, peer_password)

    def sle_pdu_request(self, pdu, apply_authentication=False):
        if apply_authentication:
            if not self.local_credentials:
                logger.error(
                    "Local password not defined. Authentication failed.")
                return
            pdu['invokerCredentials']['used'] = self.local_credentials
        else:
            if 'invokerCredentials' in pdu:
                pdu['invokerCredentials']['unused'] = None
        self._proxy.encoding.sle_pdu_request(pdu)

    def sle_pdu_indication(self, pdu):
        key = pdu.getName()

        if 'responderIdentifier' in pdu[key]:
            responder_identifier = pdu[key]['responderIdentifier']
            if self._peer_identifier not in responder_identifier.prettyPrint():
                logger.warning(
                    'Authentication failed. Wrong responder identifier.')
                return

        if 'performerCredentials' in pdu[key]:
            performer_credentials = pdu[key]['performerCredentials']['used']
            if performer_credentials.isValue:
                if not self._check_return_credentials(
                        performer_credentials,
                        self._peer_identifier, self._peer_password):
                    logger.warning('Bind unsuccessful. Authentication failed.')
                    return

        self._proxy.service_layer.sle_pdu_indication(pdu)

    def _check_return_credentials(self, credentials, username, password):
        decoded_credentials = asn1_decode(
            credentials.asOctets(), asn1Spec=Isp1Credentials())[0]
        days, ms, us = struct.unpack(
            '!HIH', bytearray(decoded_credentials['time'].asNumbers()))
        time_delta = dt.timedelta(days=days, milliseconds=ms, microseconds=us)
        cred_time = time_delta + dt.datetime(1958, 1, 1)
        random_number = int(decoded_credentials['randomNumber'])
        generated_credentials = self._generate_encoded_credentials(
            cred_time, random_number, username, password)
        return generated_credentials == credentials.asOctets()

    def _make_credentials(self, username, password):
        """Makes credentials for the initiator"""
        now = dt.datetime.utcnow()
        random_number = random.randint(0, 2147483647)
        return self._generate_encoded_credentials(
            now, random_number, username, password)

    def _generate_encoded_credentials(
            self, current_time, random_number, username, password):
        """Generates encoded ISP1 credentials"""
        hash_input = HashInput()
        days = (current_time - dt.datetime(1958, 1, 1)).days
        millisecs = 1000 * (
            current_time - current_time.replace(
                hour=0, minute=0, second=0, microsecond=0)).total_seconds()
        microsecs = int(round(millisecs % 1 * 1000))
        millisecs = int(millisecs)
        credential_time = struct.pack('!HIH', days, millisecs, microsecs)

        hash_input['time'] = credential_time
        hash_input['randomNumber'] = random_number
        hash_input['userName'] = username
        hash_input['passWord'] = bytes.fromhex(password)
        der_encoded_hash_input = asn1_der_encode(hash_input)

        # TODO: check if SHA1 or SHA256 to be used
        the_protected = bytearray.fromhex(
            hashlib.sha1(der_encoded_hash_input).hexdigest())

        isp1_creds = Isp1Credentials()
        isp1_creds['time'] = credential_time
        isp1_creds['randomNumber'] = random_number
        isp1_creds['theProtected'] = the_protected

        return asn1_encode(isp1_creds)
