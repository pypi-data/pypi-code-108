# -*- coding: utf-8 -*-
"""Module containing the TLS Extension classes
"""

# import basic stuff
import abc
import time
import logging
from typing import Tuple, Any, Optional, List, Union

# import own stuff
import tlsmate.client_state as client_state
import tlsmate.tls as tls
import tlsmate.structs as structs
import tlsmate.pdu as pdu

# import other stuff


class Extension(metaclass=abc.ABCMeta):
    """Abstract class for all extensions.
    """

    extension_id: tls.Extension
    """The extension id
    """

    @abc.abstractmethod
    def _serialize_ext_body(self, session: client_state.SessionState) -> bytes:
        """Serializes the content of an extension, i.e. excluding the header.

        Arguments:
            session: the session object that will be used to send this
                extensions.

        Returns:
            bytes: The serialized extensions body.
        """

        pass

    def serialize(self, session: client_state.SessionState) -> bytes:
        """Serializes an extensions, including the extensions header.

        Arguments:
            session: the session object that will be used to send this
                extensions.

        Returns:
            The serialized extension.
        """

        ext_body = self._serialize_ext_body(session)
        if self.extension_id is tls.Extension.UNKNOW_EXTENSION:
            ext_id = self.id  # type: ignore

        else:
            ext_id = self.extension_id.value

        ext = bytearray(pdu.pack_uint16(ext_id))
        ext.extend(pdu.pack_uint16(len(ext_body)))
        ext.extend(ext_body)
        return ext

    @staticmethod
    def deserialize(fragment: bytes, offset: int) -> Tuple["Extension", int]:
        """Deserializes an extension.

        Arguments:
            fragment: A PDU buffer as received from the network.
            offset: The offset within the fragment where the extension starts.

        Returns:
            The deserialized extension as an python object and the new offset
            into the fragment.
        """
        ext_id_int, offset = pdu.unpack_uint16(fragment, offset)
        ext_id = tls.Extension.val2enum(ext_id_int)
        ext_len, offset = pdu.unpack_uint16(fragment, offset)
        ext_body, offset = pdu.unpack_bytes(fragment, offset, ext_len)
        cls_name = deserialization_map.get(ext_id)
        if cls_name is None:
            return ExtUnknownExtension(id=ext_id_int, bytes=fragment[4:]), len(fragment)

        extension = cls_name()
        extension._deserialize_ext_body(ext_body)
        return extension, offset

    @abc.abstractmethod
    def _deserialize_ext_body(self, fragment):
        """Deserializes the body of an extension.

        Arguments:
            fragment (bytes): the body of the extension in binary format
        """


class ExtUnknownExtension(Extension):
    """Any extensions which is not known by tlsmate (yet).

    Arguments:
        id: the Id of the extensions as used in the PDU
        bytes: the content of the extension as a byte string
    """

    extension_id = tls.Extension.UNKNOW_EXTENSION

    def __init__(self, **kwargs: Any) -> None:
        self.id: Optional[int] = kwargs.get("id")
        self.bytes: Optional[bytes] = kwargs.get("bytes")

    def _serialize_ext_body(self, session):
        return self.bytes

    def _deserialize_ext_body(self, fragment):
        # deserialization implemented in base class.
        pass


class ExtServerNameIndication(Extension):
    """Represents the ServerNameIndication extension.

    Attributes:
        host_name: The name which identifies the host.
    """

    extension_id = tls.Extension.SERVER_NAME
    """:obj:`tlsmate.tls.Extension.SERVER_NAME`
    """

    def __init__(self, host_name: Optional[str] = None) -> None:
        self.host_name = host_name

    def _serialize_ext_body(self, session):
        # we only support exacly one list element: host_name
        ext = bytearray(pdu.pack_uint8(0))  # host_name
        ext.extend(pdu.pack_uint16(len(self.host_name)))
        ext.extend(pdu.pack_str(self.host_name))
        ext_body = bytearray(pdu.pack_uint16(len(ext)))
        ext_body.extend(ext)
        return ext_body

    def _deserialize_ext_body(self, fragment):
        if not len(fragment):
            return

        list_length, offset = pdu.unpack_uint16(fragment, 0)
        if offset + list_length != len(fragment):
            raise tls.ServerMalfunction(
                tls.ServerIssue.EXTENTION_LENGHT_ERROR, extension=self.extension_id
            )

        while offset < len(fragment):
            name_type, offset = pdu.unpack_uint8(fragment, offset)
            name_length, offset = pdu.unpack_uint16(fragment, offset)
            name, offset = pdu.unpack_bytes(fragment, offset, name_length)
            if name_type == 0:
                self.host_name = name.decode()

        if self.host_name is None:
            raise tls.ServerMalfunction(
                tls.ServerIssue.SNI_NO_HOSTNAME, extension=self.extension_id
            )


class ExtExtendedMasterSecret(Extension):
    """Represents the ExtendedMasterSecret extension.
    """

    extension_id = tls.Extension.EXTENDED_MASTER_SECRET
    """:obj:`tlsmate.tls.Extension.EXTENDED_MASTER_SECRET`
    """

    def _serialize_ext_body(self, session):
        return b""

    def _deserialize_ext_body(self, ext_body):
        if ext_body:
            raise tls.ServerMalfunction(
                tls.ServerIssue.EXTENTION_LENGHT_ERROR, extension=self.extension_id
            )


class ExtEncryptThenMac(Extension):
    """Represents the EncryptThenMac extension.
    """

    extension_id = tls.Extension.ENCRYPT_THEN_MAC
    """:obj:`tlsmate.tls.Extension.ENCRYPT_THEN_MAC`
    """

    def _serialize_ext_body(self, session):
        return b""

    def _deserialize_ext_body(self, ext_body):
        if ext_body:
            raise tls.ServerMalfunction(
                tls.ServerIssue.EXTENTION_LENGHT_ERROR, extension=self.extension_id
            )


class ExtRenegotiationInfo(Extension):
    """Represents the RenegotiationInfo extension.

    Attributes:
        renegotiated_connection: The opaque bytes.
    """

    extension_id = tls.Extension.RENEGOTIATION_INFO
    """:obj:`tlsmate.tls.Extension.RENEGOTIATION_INFO`
    """

    def __init__(self, renegotiated_connection: bytes = b"\0") -> None:
        self.renegotiated_connection = renegotiated_connection

    def _serialize_ext_body(self, session):
        ext_body = (
            pdu.pack_uint8(len(self.renegotiated_connection))
            + self.renegotiated_connection
        )
        return ext_body

    def _deserialize_ext_body(self, ext_body):
        length, offset = pdu.unpack_uint8(ext_body, 0)
        self.renegotiated_connection, offset = pdu.unpack_bytes(
            ext_body, offset, length
        )


class ExtEcPointFormats(Extension):
    """Represents the EcPointFormat extension.

    Attributes:
        ec_point_formats: The list of supported point formats.
    """

    extension_id = tls.Extension.EC_POINT_FORMATS
    """:obj:`tlsmate.tls.Extension.EC_POINT_FORMATS`
    """

    def __init__(
        self, ec_point_formats: Optional[List[Union[tls.EcPointFormat, int]]] = None
    ) -> None:
        self.ec_point_formats = (
            ec_point_formats if ec_point_formats else [tls.EcPointFormat.UNCOMPRESSED]
        )

    def _serialize_ext_body(self, session):
        format_list = bytearray()
        for point_format in self.ec_point_formats:
            if type(point_format) == int:
                format_list.extend(pdu.pack_uint8(point_format))

            else:
                format_list.extend(pdu.pack_uint8(point_format.value))

        ext_body = bytearray()
        ext_body.extend(pdu.pack_uint8(len(format_list)))
        ext_body.extend(format_list)
        return ext_body

    def _deserialize_ext_body(self, ext_body):
        self.ec_point_formats = []
        length, offset = pdu.unpack_uint8(ext_body, 0)
        if offset + length != len(ext_body):
            raise tls.ServerMalfunction(
                tls.ServerIssue.EXTENTION_LENGHT_ERROR, extension=self.extension_id
            )

        for i in range(length):
            point_format, offset = pdu.unpack_uint8(ext_body, offset)
            self.ec_point_formats.append(tls.EcPointFormat.val2enum(point_format))


class ExtSupportedGroups(Extension):
    """Represents the SupportedGroup extension.

    Attributes:
        supported_groups: The list of supported groups.
    """

    extension_id = tls.Extension.SUPPORTED_GROUPS
    """:obj:`tlsmate.tls.Extension.SUPPORTED_GROUPS`
    """

    def __init__(
        self, supported_groups: Optional[List[tls.SupportedGroups]] = None
    ) -> None:
        self.supported_groups = supported_groups if supported_groups else []

    def _serialize_ext_body(self, session):
        group_list = bytearray()
        for group in self.supported_groups:
            group_list.extend(pdu.pack_uint16(getattr(group, "value", group)))

        ext_body = bytearray()
        ext_body.extend(pdu.pack_uint16(len(group_list)))
        ext_body.extend(group_list)
        return ext_body

    def _deserialize_ext_body(self, ext_body):
        length, offset = pdu.unpack_uint16(ext_body, 0)
        end_of_list = offset + length
        while offset < end_of_list:
            group, offset = pdu.unpack_uint16(ext_body, offset)
            try:
                group = tls.SupportedGroups(group)

            except ValueError:
                pass

            self.supported_groups.append(group)


class ExtSignatureAlgorithms(Extension):
    """Represents the SignatureAlgorithms extension.

    Attributes:
        signature_algorithms: The of supported signature algorithms.
    """

    extension_id = tls.Extension.SIGNATURE_ALGORITHMS
    """:obj:`tlsmate.tls.Extension.SIGNATURE_ALGORITHMS`
    """

    def __init__(
        self,
        signature_algorithms: Optional[List[Union[tls.SignatureScheme, int]]] = None,
    ) -> None:
        self.signature_algorithms = signature_algorithms if signature_algorithms else []

    def _serialize_ext_body(self, session):
        algo_list = bytearray()
        for algo in self.signature_algorithms:
            if type(algo) is tuple:
                algo = 256 * algo[0] + algo[1]
            algo_list.extend(pdu.pack_uint16(getattr(algo, "value", algo)))

        ext_body = bytearray()
        ext_body.extend(pdu.pack_uint16(len(algo_list)))
        ext_body.extend(algo_list)
        return ext_body

    def _deserialize_ext_body(self, ext_body):
        length, offset = pdu.unpack_uint16(ext_body, 0)
        end_of_list = offset + length
        while offset < end_of_list:
            algo, offset = pdu.unpack_uint16(ext_body, offset)
            try:
                algo = tls.SignatureScheme(algo)

            except ValueError:
                pass

            self.signature_algorithms.append(algo)


class ExtHeartbeat(Extension):
    """Represents the Heartbeat extension.

    Attributes:
        heartbeat_mode: The mode for the heartbeat extension.
    """

    extension_id = tls.Extension.HEARTBEAT
    """:obj:`tlsmate.tls.Extension.HEARTBEAT`
    """

    def __init__(self, heartbeat_mode: Optional[tls.HeartbeatMode] = None) -> None:
        self.heartbeat_mode = heartbeat_mode

    def _serialize_ext_body(self, session):
        if type(self.heartbeat_mode) is int:
            val = self.heartbeat_mode
        else:
            val = self.heartbeat_mode.value

        return pdu.pack_uint8(val)

    def _deserialize_ext_body(self, ext_body):
        mode, offset = pdu.unpack_uint8(ext_body, 0)
        self.heartbeat_mode = tls.HeartbeatMode.val2enum(mode, alert_on_failure=True)


class ExtCertificateAuthorities(Extension):
    """Represents the CertificateAuthorities extension.

    Attributes:
        authorities: The list of authorities in original ASN.1 format.
    """

    extension_id = tls.Extension.CERTIFICATE_AUTHORITIES
    """:obj:`tlsmate.tls.Extension.CERTIFICATE_AUTHORITIES`
    """

    def __init__(self, authorities: Optional[List[bytes]] = None) -> None:
        self.authorities = authorities if authorities else []

    def _serialize_ext_body(self, session):
        raise NotImplementedError(f"serialization of extension {self} not implemented")

    def _deserialize_ext_body(self, ext_body):
        length, offset = pdu.unpack_uint16(ext_body, 0)
        end_of_list = offset + length
        while offset < end_of_list:
            length, offset = pdu.unpack_uint16(ext_body, offset)
            authority, offset = pdu.unpack_bytes(ext_body, offset, length)
            self.authorities.append(authority)


class ExtSessionTicket(Extension):
    """Represents the SessionTicket extension.

    Attributes:
        ticket: The ticket.
    """

    extension_id = tls.Extension.SESSION_TICKET
    """:obj:`tlsmate.tls.Extension.SESSION_TICKET`
    """

    def __init__(self, ticket: Optional[bytes] = None) -> None:
        self.ticket = ticket

    def _serialize_ext_body(self, session):
        ext_body = bytearray()
        if self.ticket is not None:
            ext_body.extend(self.ticket)

        return ext_body

    def _deserialize_ext_body(self, ext_body):
        pass


class ExtStatusRequest(Extension):
    """Represents the status_request extension.

    Attributes:
        status_type: The status type. Defaults to
            :obj:`tlsmate.tls.StatusType.OCSP`.
        responder_ids: The list of responder ids. Defaults to an empty list.
        extensions: The list of extensions. Defaults to an empty list.
    """

    extension_id = tls.Extension.STATUS_REQUEST
    """:obj:`tlsmate.tls.Extension.STATUS_REQUEST`
    """

    def __init__(
        self,
        status_type: tls.StatusType = tls.StatusType.OCSP,
        responder_ids: Optional[List[bytes]] = None,
        extensions: Optional[List[bytes]] = None,
    ) -> None:
        self.status_type = status_type
        if responder_ids is None:
            responder_ids = []

        self.reponder_ids = responder_ids
        if extensions is None:
            extensions = []

        self.extensions = extensions
        self.ocsp_response = None

    def _serialize_ext_body(self, session):
        ext_body = bytearray()
        ext_body.extend(
            pdu.pack_uint8(getattr(self.status_type, "value", self.status_type))
        )

        responders = bytearray()
        for responder in self.reponder_ids:
            responders.extend(pdu.pack_uint16(len(responder)))
            responders.extend(responder)

        ext_body.extend(pdu.pack_uint16(len(responders)))
        ext_body.extend(responders)

        extensions = bytearray()
        for extension in self.extensions:
            extensions.extend(pdu.pack_uint16(len(extension)))
            extensions.extend(extension)

        ext_body.extend(pdu.pack_uint16(len(extensions)))
        ext_body.extend(extensions)
        return ext_body

    def _deserialize_ext_body(self, ext_body):
        if not len(ext_body):
            self.status_type = tls.StatusType.NONE
            return

        status_type, offset = pdu.unpack_uint8(ext_body, 0)
        self.status_type = tls.StatusType.val2enum(status_type)
        length, offset = pdu.unpack_uint24(ext_body, offset)
        self.ocsp_response, offset = pdu.unpack_bytes(ext_body, offset, length)


class ExtStatusRequestV2(Extension):
    """Represents the status_requestv2 extension.

    Attributes:
        status_type (:obj:`tlsmate.tls.StatusType`): The status type. Defaults to
            :obj:`tlsmate.tls.StatusType.OCSP`.
        responder_ids (list of bytes): The list of responder ids. Defaults to an empty
            list.
        extensions (list of bytes): The list of extensions. Defaults to an empty
            list.
    """

    extension_id = tls.Extension.STATUS_REQUEST_V2
    """:obj:`tlsmate.tls.Extension.STATUS_REQUEST_V2`
    """

    def __init__(
        self,
        status_type: tls.StatusType = tls.StatusType.OCSP_MULTI,
        responder_ids: Optional[List[bytes]] = None,
        extensions: bytes = b"",
    ) -> None:
        self._requests: List[Tuple[tls.StatusType, Optional[List[bytes]], bytes]] = []
        self.add_request(status_type, responder_ids, extensions)

    def add_request(self, status_type, responder_ids=None, extensions=b""):
        if responder_ids is None:
            responder_ids = []

        self._requests.append((status_type, responder_ids, extensions))

    def _serialize_ext_body(self, session):

        ext_body = bytearray()
        for status_type, responder_ids, extensions in self._requests:
            request_item = bytearray(
                pdu.pack_uint8(getattr(status_type, "value", status_type))
            )
            status_request = bytearray()
            responders = bytearray()
            for responder in responder_ids:
                responders.extend(pdu.pack_uint16(len(responder)))
                responders.extend(responder)
            status_request.extend(pdu.pack_uint16(len(responders)))
            status_request.extend(responders)
            status_request.extend(pdu.pack_uint16(len(extensions)))
            status_request.extend(extensions)
            request_item.extend(pdu.pack_uint16(len(status_request)))
            request_item.extend(status_request)
            ext_body.extend(pdu.pack_uint16(len(request_item)))
            ext_body.extend(request_item)

        return ext_body

    def _deserialize_ext_body(self, ext_body):
        if not len(ext_body):
            self.status_type = tls.StatusType.NONE
            return

        status_type, offset = pdu.unpack_uint8(ext_body, 0)
        self.status_type = tls.StatusType.val2enum(status_type)
        length, offset = pdu.unpack_uint24(ext_body, offset)
        self.ocsp_response, offset = pdu.unpack_bytes(ext_body, offset, length)


class ExtSupportedVersions(Extension):
    """Represents the SupportedVersion extension.

    Attributes:
        versions: The list of TLS versions supported.
    """

    extension_id = tls.Extension.SUPPORTED_VERSIONS
    """:obj:`tlsmate.tls.Extension.SUPPORTED_VERSIONS`
    """

    def __init__(
        self, versions: Optional[List[Union[tls.Version, int]]] = None
    ) -> None:
        self.versions = versions

    def _serialize_ext_body(self, session):
        versions = bytearray()
        for version in self.versions:
            versions.extend(pdu.pack_uint16(getattr(version, "value", version)))

        ext_body = bytearray()
        ext_body.extend(pdu.pack_uint8(len(versions)))
        ext_body.extend(versions)
        return ext_body

    def _deserialize_ext_body(self, ext_body):
        self.versions = []
        offset = 0
        while offset < len(ext_body):
            version, offset = pdu.unpack_uint16(ext_body, offset)
            version = tls.Version.val2enum(version)
            self.versions.append(version)


class ExtCookie(Extension):
    """Represents the Cookie extension.

    Attributes:
        cookie: The opaque cookie value
    """

    extension_id = tls.Extension.COOKIE
    """:obj:`tlsmate.tls.Extension.COOKIE`
    """

    def __init__(self, cookie: bytes = b"") -> None:
        self.cookie = cookie

    def _serialize_ext_body(self, session):
        ext_body = bytearray()
        ext_body.extend(pdu.pack_uint16(len(self.cookie)))
        ext_body.extend(self.cookie)
        return ext_body

    def _deserialize_ext_body(self, ext_body):
        length, offset = pdu.unpack_uint16(ext_body, 0)
        self.cookie, offset = pdu.unpack_bytes(ext_body, offset, length)


class ExtKeyShare(Extension):
    """Represents the KeyShare extension.

    Given the list of supported groups, during serialization the shares are actually
    generated and the resulting public keys are included into the extension. The user
    must ensure that the key share uses the same sequence for the groups than
    provided in the SupportedGroup extension.

    Attributes:
        key_shares (list of :obj:`tlsmate.structs.KeyShareEntry`): the list of
            key shares, comprising the group and the public key for each element.
        groups (list of :obj:`tlsmate.tls.SupportedGroups`): The list of
            supported groups for which key shares shall be generated. This is an
            alternative to setup the extension. The public key will be determined
            when serializing the extension.
    """

    extension_id = tls.Extension.KEY_SHARE
    """:obj:`tlsmate.tls.Extension.KEY_SHARE`
    """

    def __init__(
        self,
        key_shares: Optional[List[structs.KeyShareEntry]] = None,
        groups: Optional[List[tls.SupportedGroups]] = None,
    ) -> None:
        if key_shares is None:
            key_shares = []

        if groups is None:
            groups = []

        if not key_shares and groups:
            key_shares = [
                structs.KeyShareEntry(group=group, key_exchange=None)
                for group in groups
            ]

        self.key_shares = key_shares

    def _serialize_ext_body(self, session):
        key_shares = bytearray()
        for ks in self.key_shares:
            key_shares.extend(pdu.pack_uint16(ks.group.value))
            share = session.create_key_share(ks.group)
            key_shares.extend(pdu.pack_uint16(len(share)))
            key_shares.extend(share)

        ext_body = bytearray()
        ext_body.extend(pdu.pack_uint16(len(key_shares)))
        ext_body.extend(key_shares)
        return ext_body

    def _deserialize_ext_body(self, ext_body):
        self.key_shares = []
        offset = 0
        while offset < len(ext_body):
            group, offset = pdu.unpack_uint16(ext_body, offset)
            group = tls.SupportedGroups.val2enum(group, alert_on_failure=True)
            if offset < len(ext_body):
                length, offset = pdu.unpack_uint16(ext_body, offset)
                share, offset = pdu.unpack_bytes(ext_body, offset, length)

            else:
                share = None

            self.key_shares.append(
                structs.KeyShareEntry(group=group, key_exchange=share)
            )


class ExtPreSharedKey(Extension):
    """Represents the PreSharedKey extension for TLS1.3

    Builds this extension based on the list of the given pre shared keys.

    Attributes:
        psks: The list of pre shared keys to offer to the server.
    """

    extension_id = tls.Extension.PRE_SHARED_KEY
    """:obj:`tlsmate.tls.Extension.PRE_SHARED_KEY`
    """

    def __init__(self, psks: Optional[List[structs.Psk]] = None) -> None:
        self.psks = psks
        self._bytes_after_ids = 0

    def _serialize_ext_body(self, session):
        identities = bytearray()
        binders = bytearray()
        for psk in self.psks:
            identities.extend(pdu.pack_uint16(len(psk.ticket)))
            identities.extend(psk.ticket)
            timestamp = session.recorder.inject(timestamp=time.time())
            ticket_age = int((timestamp - psk.timestamp) * 1000 + psk.age_add) % (
                2 ** 32
            )
            identities.extend(pdu.pack_uint32(ticket_age))
            binders.extend(pdu.pack_uint8(psk.hmac.mac_len))
            binders.extend(b"\0" * psk.hmac.mac_len)

        ext_body = bytearray()
        ext_body.extend(pdu.pack_uint16(len(identities)))
        ext_body.extend(identities)
        binders_len = len(binders)
        self._bytes_after_ids = binders_len + 2  # 2 bytes for length indicator
        ext_body.extend(pdu.pack_uint16(binders_len))
        ext_body.extend(binders)

        return ext_body

    def _deserialize_ext_body(self, ext_body):
        self.selected_id, offset = pdu.unpack_uint16(ext_body, 0)


class ExtPskKeyExchangeMode(Extension):
    """Represents the psk_key_exchange_mode extension.

    Attributes:
        modes: The list of the PSK key exchange modes to offer to the server.
    """

    extension_id = tls.Extension.PSK_KEY_EXCHANGE_MODES
    """:obj:`tlsmate.tls.Extension.PSK_KEY_EXCHANGE_MODES`
    """

    def __init__(self, modes: Optional[List[tls.PskKeyExchangeMode]] = None) -> None:
        self.modes = modes

    def _serialize_ext_body(self, session):
        ext_body = bytearray(pdu.pack_uint8(len(self.modes)))
        for mode in self.modes:
            ext_body.extend(pdu.pack_uint8(getattr(mode, "value", mode)))

        return ext_body

    def _deserialize_ext_body(self, ext_body):
        raise NotImplementedError


class ExtEarlyData(Extension):
    """Represents the EarlyData extension.

    Attributes:
        max_early_data_size: The maximum number of bytes used for the early data.
    """

    extension_id = tls.Extension.EARLY_DATA
    """:obj:`tlsmate.tls.Extension.EARLY_DATA`
    """

    def __init__(self, max_early_data_size: Optional[int] = None) -> None:
        self.max_early_data_size = max_early_data_size

    def _serialize_ext_body(self, session):
        if self.max_early_data_size is None:
            return b""

        else:
            return bytes(pdu.pack_uint32(self.max_early_data_size))

    def _deserialize_ext_body(self, ext_body):
        if ext_body:
            self.max_early_data_size, _ = pdu.unpack_uint32(ext_body, 0)


class ExtPostHandshakeAuth(Extension):
    """Represents the PostHandshakeAuth extension.
    """

    extension_id = tls.Extension.POST_HANDSHAKE_AUTH
    """:obj:`tlsmate.tls.Extension.POST_HANDSHAKE_AUTH`
    """

    def _serialize_ext_body(self, session):
        return b""

    def _deserialize_ext_body(self, ext_body):
        if ext_body:
            raise tls.ServerMalfunction(
                tls.ServerIssue.EXTENTION_LENGHT_ERROR, extension=self.extension_id
            )


# Map the extensions id to the corresponding class.
deserialization_map = {
    tls.Extension.SERVER_NAME: ExtServerNameIndication,
    # tls.Extension.MAX_FRAGMENT_LENGTH = 1
    # tls.Extension.CLIENT_CERTIFICATE_URL = 2
    # tls.Extension.TRUSTED_CA_KEYS = 3
    # tls.Extension.TRUNCATED_HMAC = 4
    tls.Extension.STATUS_REQUEST: ExtStatusRequest,
    # tls.Extension.USER_MAPPING = 6
    # tls.Extension.CLIENT_AUTHZ = 7
    # tls.Extension.SERVER_AUTHZ = 8
    # tls.Extension.CERT_TYPE = 9
    tls.Extension.SUPPORTED_GROUPS: ExtSupportedGroups,
    tls.Extension.EC_POINT_FORMATS: ExtEcPointFormats,
    # tls.Extension.SRP = 12
    tls.Extension.SIGNATURE_ALGORITHMS: ExtSignatureAlgorithms,
    # tls.Extension.USE_SRTP = 14
    tls.Extension.HEARTBEAT: ExtHeartbeat,
    # tls.Extension.APPLICATION_LAYER_PROTOCOL_NEGOTIATION = 16
    tls.Extension.STATUS_REQUEST_V2: ExtStatusRequestV2,
    # tls.Extension.SIGNED_CERTIFICATE_TIMESTAMP = 18
    # tls.Extension.CLIENT_CERTIFICATE_TYPE = 19
    # tls.Extension.SERVER_CERTIFICATE_TYPE = 20
    # tls.Extension.PADDING = 21
    tls.Extension.ENCRYPT_THEN_MAC: ExtEncryptThenMac,
    tls.Extension.EXTENDED_MASTER_SECRET: ExtExtendedMasterSecret,
    # tls.Extension.TOKEN_BINDING = 24
    # tls.Extension.CACHED_INFO = 25
    # tls.Extension.TLS_LTS = 26
    # tls.Extension.COMPRESS_CERTIFICATE = 27
    # tls.Extension.RECORD_SIZE_LIMIT = 28
    # tls.Extension.PWD_PROTECT = 29
    # tls.Extension.PWD_CLEAR = 30
    # tls.Extension.PASSWORD_SALT = 31
    # tls.Extension.TICKET_PINNING = 32
    # tls.Extension.TLS_CERT_WITH_EXTERN_PSK = 33
    # tls.Extension.DELEGATED_CREDENTIALS = 34
    tls.Extension.SESSION_TICKET: ExtSessionTicket,
    # tls.Extension.SUPPORTED_EKT_CIPHERS = 39
    tls.Extension.PRE_SHARED_KEY: ExtPreSharedKey,
    tls.Extension.EARLY_DATA: ExtEarlyData,
    tls.Extension.SUPPORTED_VERSIONS: ExtSupportedVersions,
    tls.Extension.COOKIE: ExtCookie,
    # tls.Extension.PSK_KEY_EXCHANGE_MODES = 45
    tls.Extension.CERTIFICATE_AUTHORITIES: ExtCertificateAuthorities,
    # tls.Extension.OID_FILTERS = 48
    tls.Extension.POST_HANDSHAKE_AUTH: ExtPostHandshakeAuth,
    # tls.Extension.SIGNATURE_ALGORITHMS_CERT = 50
    tls.Extension.KEY_SHARE: ExtKeyShare,
    # tls.Extension.TRANSPARENCY_INFO = 52
    # tls.Extension.CONNECTION_ID = 53
    # tls.Extension.EXTERNAL_ID_HASH = 55
    # tls.Extension.EXTERNAL_SESSION_ID = 56
    tls.Extension.RENEGOTIATION_INFO: ExtRenegotiationInfo,
}


def log_extensions(extensions: List[Extension]) -> None:
    """Log extensions

    Arguments:
        extensions: the list of extensions to iterate over
    """

    for extension in extensions:
        ext_id = extension.extension_id
        logging.debug(f"extension {ext_id.value} {ext_id}")


def get_extension(
    extensions: List[Extension], ext_id: tls.Extension
) -> Optional[Extension]:
    """Helper function to search for an extension

    Arguments:
        extensions: the list to search for the extension
        ext_id: the extension to to look for

    Returns:
        The extension if present, or None otherwise.
    """

    if extensions is not None:
        for extension in extensions:
            if extension.extension_id == ext_id:
                return extension

    return None


def deserialize_extensions(
    extensions: List[Extension], fragment: bytes, offset: int
) -> int:
    """Helper function to deserialize extensions

    Arguments:
        extensions: the list where to store the deserialized extensions
        fragment: the pdu buffer
        offset: the offset within the pdu buffer to the start of the extensions

    Returns:
        the offset on the byte following the extensions
    """

    if offset < len(fragment):
        # extensions present
        ext_len, offset = pdu.unpack_uint16(fragment, offset)
        ext_end = offset + ext_len
        while offset < ext_end:
            extension, offset = Extension.deserialize(fragment, offset)
            extensions.append(extension)

    return offset
