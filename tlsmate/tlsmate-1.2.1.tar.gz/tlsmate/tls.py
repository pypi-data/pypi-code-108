# -*- coding: utf-8 -*-
"""Module defining constants for the TLS protocol
"""
# import basic stuff
import enum
from typing import List, TypeVar, Type, Optional, Union

# import own stuff

# import other stuff

_T = TypeVar("_T")


class ExtendedEnum(enum.Enum):
    """Class to extend the enum.Enum class by additional methods
    """

    @classmethod
    def val2enum(cls: Type[_T], value: int, alert_on_failure: bool = False) -> _T:
        """Class method to map a value to the corresponding enum.

        Args:
            value: The enum value which is used to map to an enum
            alert_on_failure: If set to True and the value is not a valid enum
                value, an :obj:`ServerMalfunction` exception will be raised.
                Defaults to False.

        Returns:
            The corresponding enum or None, if the mapping fails and
            `alert_on_failure` is set to False.

        Raises:
            ServerMalfunction: In case the given value is not a valid enum and
                `alert_on_failure` is True
        """

        # TODO: resolve type issue
        enum = cls._value2member_map_.get(value)  # type: ignore
        if (enum is None) and alert_on_failure:
            raise ServerMalfunction(ServerIssue.ILLEGAL_PARAMETER_VALUE)

        return enum

    @classmethod
    def str2enum(cls, name: str, alert_on_failure: bool = False) -> Optional[enum.Enum]:
        """Class method to map a string to the corresponding enum.

        Args:
            name (str): The name which must correspond to the name of the enum.
            alert_on_failure (bool, optional): If set to True and the name is
                not a valid enum value, an :obj:`ServerMalfunction` exception will be
                raised. Defaults to False.

        Returns:
            The corresponding enum or None, if the mapping fails and
            `alert_on_failure` is set to False.

        Raises:
            ServerMalfunction: In case the given name is not a valid enum and
                `alert_on_failure` is True
        """

        enum = cls._member_map_.get(name)  # type: ignore
        if (enum is None) and alert_on_failure:
            raise ValueError(f"Value {name} not defined for {cls}")

        return enum

    @classmethod
    def all(cls) -> List["ExtendedEnum"]:
        """Get all enum items

        Returns:
            list of all enum items defined for that enum
        """

        return list(cls.__members__.values())

    def __str__(self) -> str:
        """Use the name as a string representation

        Returns:
            str: the name of the enum item
        """

        return self.name


class ExtendedIntEnum(ExtendedEnum):
    """Class for comparable enums

    Note, that we us our own class, as we cannot overwrite the __str__ method of the
    enum.IntEnum call (__slots__!)
    """

    def __lt__(self, other):
        return self.value < getattr(other, "value", other)

    def __gt__(self, other):
        return self.value > getattr(other, "value", other)

    def __le__(self, other):
        return self.value <= getattr(other, "value", other)

    def __ge__(self, other):
        return self.value >= getattr(other, "value", other)


class Entity(ExtendedEnum):
    """Enum used to represent the entity of the TLS connection endpoint.
    """

    CLIENT = 0
    SERVER = 1


class Version(ExtendedIntEnum):
    """Enum for the TLS versions.

    The values defined correspond to the values used in PDUs.
    """

    SSL20 = 0x0200
    SSL30 = 0x0300
    TLS10 = 0x0301
    TLS11 = 0x0302
    TLS12 = 0x0303
    TLS13 = 0x0304

    @classmethod
    def tls_only(cls) -> List["Version"]:
        """Comfortable method to get all TLS versions 1.0 .. 1.3, excluding SSLv2/v3.
        """

        return [cls.TLS10, cls.TLS11, cls.TLS12, cls.TLS13]


class ContentType(ExtendedEnum):
    """Enum representing the TLS-Handshake protocols.

    The values defined correspond to the values used in PDUs as defined by IANA.
    """

    CHANGE_CIPHER_SPEC = 20
    ALERT = 21
    HANDSHAKE = 22
    APPLICATION_DATA = 23
    HEARTBEAT = 24
    SSL2 = 256


class CompressionMethod(ExtendedEnum):
    """Enum representing the TLS compression methods.

    The values defined correspond to the values used in PDUs as defined by IANA.
    """

    NULL = 0
    DEFLATE = 1


class Extension(ExtendedEnum):
    """Enum representing the TLS extensions.

    The values defined correspond to the values used in PDUs as defined by IANA.
    """

    SERVER_NAME = 0
    MAX_FRAGMENT_LENGTH = 1
    CLIENT_CERTIFICATE_URL = 2
    TRUSTED_CA_KEYS = 3
    TRUNCATED_HMAC = 4
    STATUS_REQUEST = 5
    USER_MAPPING = 6
    CLIENT_AUTHZ = 7
    SERVER_AUTHZ = 8
    CERT_TYPE = 9
    SUPPORTED_GROUPS = 10
    EC_POINT_FORMATS = 11
    SRP = 12
    SIGNATURE_ALGORITHMS = 13
    USE_SRTP = 14
    HEARTBEAT = 15
    APPLICATION_LAYER_PROTOCOL_NEGOTIATION = 16
    STATUS_REQUEST_V2 = 17
    SIGNED_CERTIFICATE_TIMESTAMP = 18
    CLIENT_CERTIFICATE_TYPE = 19
    SERVER_CERTIFICATE_TYPE = 20
    PADDING = 21
    ENCRYPT_THEN_MAC = 22
    EXTENDED_MASTER_SECRET = 23
    TOKEN_BINDING = 24
    CACHED_INFO = 25
    TLS_LTS = 26
    COMPRESS_CERTIFICATE = 27
    RECORD_SIZE_LIMIT = 28
    PWD_PROTECT = 29
    PWD_CLEAR = 30
    PASSWORD_SALT = 31
    TICKET_PINNING = 32
    TLS_CERT_WITH_EXTERN_PSK = 33
    DELEGATED_CREDENTIALS = 34
    SESSION_TICKET = 35
    SUPPORTED_EKT_CIPHERS = 39
    PRE_SHARED_KEY = 41
    EARLY_DATA = 42
    SUPPORTED_VERSIONS = 43
    COOKIE = 44
    PSK_KEY_EXCHANGE_MODES = 45
    CERTIFICATE_AUTHORITIES = 47
    OID_FILTERS = 48
    POST_HANDSHAKE_AUTH = 49
    SIGNATURE_ALGORITHMS_CERT = 50
    KEY_SHARE = 51
    TRANSPARENCY_INFO = 52
    CONNECTION_ID = 53
    EXTERNAL_ID_HASH = 55
    EXTERNAL_SESSION_ID = 56
    RENEGOTIATION_INFO = 65281
    UNKNOW_EXTENSION = 0x10000


class CipherSuite(ExtendedEnum):
    """Enum representing the TLS cipher suites (excluding SSL20).

    The values defined correspond to the values used in PDUs as defined by IANA,
    excluding cipher suites registered for drafts.
    """

    TLS_NULL_WITH_NULL_NULL = 0x0000
    TLS_RSA_WITH_NULL_MD5 = 0x0001
    TLS_RSA_WITH_NULL_SHA = 0x0002
    TLS_RSA_EXPORT_WITH_RC4_40_MD5 = 0x0003
    TLS_RSA_WITH_RC4_128_MD5 = 0x0004
    TLS_RSA_WITH_RC4_128_SHA = 0x0005
    TLS_RSA_EXPORT_WITH_RC2_CBC_40_MD5 = 0x0006
    TLS_RSA_WITH_IDEA_CBC_SHA = 0x0007
    TLS_RSA_EXPORT_WITH_DES40_CBC_SHA = 0x0008
    TLS_RSA_WITH_DES_CBC_SHA = 0x0009
    TLS_RSA_WITH_3DES_EDE_CBC_SHA = 0x000A
    TLS_DH_DSS_EXPORT_WITH_DES40_CBC_SHA = 0x000B
    TLS_DH_DSS_WITH_DES_CBC_SHA = 0x000C
    TLS_DH_DSS_WITH_3DES_EDE_CBC_SHA = 0x000D
    TLS_DH_RSA_EXPORT_WITH_DES40_CBC_SHA = 0x000E
    TLS_DH_RSA_WITH_DES_CBC_SHA = 0x000F
    TLS_DH_RSA_WITH_3DES_EDE_CBC_SHA = 0x0010
    TLS_DHE_DSS_EXPORT_WITH_DES40_CBC_SHA = 0x0011
    TLS_DHE_DSS_WITH_DES_CBC_SHA = 0x0012
    TLS_DHE_DSS_WITH_3DES_EDE_CBC_SHA = 0x0013
    TLS_DHE_RSA_EXPORT_WITH_DES40_CBC_SHA = 0x0014
    TLS_DHE_RSA_WITH_DES_CBC_SHA = 0x0015
    TLS_DHE_RSA_WITH_3DES_EDE_CBC_SHA = 0x0016
    TLS_DH_ANON_EXPORT_WITH_RC4_40_MD5 = 0x0017
    TLS_DH_ANON_WITH_RC4_128_MD5 = 0x0018
    TLS_DH_ANON_EXPORT_WITH_DES40_CBC_SHA = 0x0019
    TLS_DH_ANON_WITH_DES_CBC_SHA = 0x001A
    TLS_DH_ANON_WITH_3DES_EDE_CBC_SHA = 0x001B
    TLS_KRB5_WITH_DES_CBC_SHA = 0x001E
    TLS_KRB5_WITH_3DES_EDE_CBC_SHA = 0x001F
    TLS_KRB5_WITH_RC4_128_SHA = 0x0020
    TLS_KRB5_WITH_IDEA_CBC_SHA = 0x0021
    TLS_KRB5_WITH_DES_CBC_MD5 = 0x0022
    TLS_KRB5_WITH_3DES_EDE_CBC_MD5 = 0x0023
    TLS_KRB5_WITH_RC4_128_MD5 = 0x0024
    TLS_KRB5_WITH_IDEA_CBC_MD5 = 0x0025
    TLS_KRB5_EXPORT_WITH_DES_CBC_40_SHA = 0x0026
    TLS_KRB5_EXPORT_WITH_RC2_CBC_40_SHA = 0x0027
    TLS_KRB5_EXPORT_WITH_RC4_40_SHA = 0x0028
    TLS_KRB5_EXPORT_WITH_DES_CBC_40_MD5 = 0x0029
    TLS_KRB5_EXPORT_WITH_RC2_CBC_40_MD5 = 0x002A
    TLS_KRB5_EXPORT_WITH_RC4_40_MD5 = 0x002B
    TLS_PSK_WITH_NULL_SHA = 0x002C
    TLS_DHE_PSK_WITH_NULL_SHA = 0x002D
    TLS_RSA_PSK_WITH_NULL_SHA = 0x002E
    TLS_RSA_WITH_AES_128_CBC_SHA = 0x002F
    TLS_DH_DSS_WITH_AES_128_CBC_SHA = 0x0030
    TLS_DH_RSA_WITH_AES_128_CBC_SHA = 0x0031
    TLS_DHE_DSS_WITH_AES_128_CBC_SHA = 0x0032
    TLS_DHE_RSA_WITH_AES_128_CBC_SHA = 0x0033
    TLS_DH_ANON_WITH_AES_128_CBC_SHA = 0x0034
    TLS_RSA_WITH_AES_256_CBC_SHA = 0x0035
    TLS_DH_DSS_WITH_AES_256_CBC_SHA = 0x0036
    TLS_DH_RSA_WITH_AES_256_CBC_SHA = 0x0037
    TLS_DHE_DSS_WITH_AES_256_CBC_SHA = 0x0038
    TLS_DHE_RSA_WITH_AES_256_CBC_SHA = 0x0039
    TLS_DH_ANON_WITH_AES_256_CBC_SHA = 0x003A
    TLS_RSA_WITH_NULL_SHA256 = 0x003B
    TLS_RSA_WITH_AES_128_CBC_SHA256 = 0x003C
    TLS_RSA_WITH_AES_256_CBC_SHA256 = 0x003D
    TLS_DH_DSS_WITH_AES_128_CBC_SHA256 = 0x003E
    TLS_DH_RSA_WITH_AES_128_CBC_SHA256 = 0x003F
    TLS_DHE_DSS_WITH_AES_128_CBC_SHA256 = 0x0040
    TLS_RSA_WITH_CAMELLIA_128_CBC_SHA = 0x0041
    TLS_DH_DSS_WITH_CAMELLIA_128_CBC_SHA = 0x0042
    TLS_DH_RSA_WITH_CAMELLIA_128_CBC_SHA = 0x0043
    TLS_DHE_DSS_WITH_CAMELLIA_128_CBC_SHA = 0x0044
    TLS_DHE_RSA_WITH_CAMELLIA_128_CBC_SHA = 0x0045
    TLS_DH_ANON_WITH_CAMELLIA_128_CBC_SHA = 0x0046
    TLS_DHE_RSA_WITH_AES_128_CBC_SHA256 = 0x0067
    TLS_DH_DSS_WITH_AES_256_CBC_SHA256 = 0x0068
    TLS_DH_RSA_WITH_AES_256_CBC_SHA256 = 0x0069
    TLS_DHE_DSS_WITH_AES_256_CBC_SHA256 = 0x006A
    TLS_DHE_RSA_WITH_AES_256_CBC_SHA256 = 0x006B
    TLS_DH_ANON_WITH_AES_128_CBC_SHA256 = 0x006C
    TLS_DH_ANON_WITH_AES_256_CBC_SHA256 = 0x006D
    TLS_RSA_WITH_CAMELLIA_256_CBC_SHA = 0x0084
    TLS_DH_DSS_WITH_CAMELLIA_256_CBC_SHA = 0x0085
    TLS_DH_RSA_WITH_CAMELLIA_256_CBC_SHA = 0x0086
    TLS_DHE_DSS_WITH_CAMELLIA_256_CBC_SHA = 0x0087
    TLS_DHE_RSA_WITH_CAMELLIA_256_CBC_SHA = 0x0088
    TLS_DH_ANON_WITH_CAMELLIA_256_CBC_SHA = 0x0089
    TLS_PSK_WITH_RC4_128_SHA = 0x008A
    TLS_PSK_WITH_3DES_EDE_CBC_SHA = 0x008B
    TLS_PSK_WITH_AES_128_CBC_SHA = 0x008C
    TLS_PSK_WITH_AES_256_CBC_SHA = 0x008D
    TLS_DHE_PSK_WITH_RC4_128_SHA = 0x008E
    TLS_DHE_PSK_WITH_3DES_EDE_CBC_SHA = 0x008F
    TLS_DHE_PSK_WITH_AES_128_CBC_SHA = 0x0090
    TLS_DHE_PSK_WITH_AES_256_CBC_SHA = 0x0091
    TLS_RSA_PSK_WITH_RC4_128_SHA = 0x0092
    TLS_RSA_PSK_WITH_3DES_EDE_CBC_SHA = 0x0093
    TLS_RSA_PSK_WITH_AES_128_CBC_SHA = 0x0094
    TLS_RSA_PSK_WITH_AES_256_CBC_SHA = 0x0095
    TLS_RSA_WITH_SEED_CBC_SHA = 0x0096
    TLS_DH_DSS_WITH_SEED_CBC_SHA = 0x0097
    TLS_DH_RSA_WITH_SEED_CBC_SHA = 0x0098
    TLS_DHE_DSS_WITH_SEED_CBC_SHA = 0x0099
    TLS_DHE_RSA_WITH_SEED_CBC_SHA = 0x009A
    TLS_DH_ANON_WITH_SEED_CBC_SHA = 0x009B
    TLS_RSA_WITH_AES_128_GCM_SHA256 = 0x009C
    TLS_RSA_WITH_AES_256_GCM_SHA384 = 0x009D
    TLS_DHE_RSA_WITH_AES_128_GCM_SHA256 = 0x009E
    TLS_DHE_RSA_WITH_AES_256_GCM_SHA384 = 0x009F
    TLS_DH_RSA_WITH_AES_128_GCM_SHA256 = 0x00A0
    TLS_DH_RSA_WITH_AES_256_GCM_SHA384 = 0x00A1
    TLS_DHE_DSS_WITH_AES_128_GCM_SHA256 = 0x00A2
    TLS_DHE_DSS_WITH_AES_256_GCM_SHA384 = 0x00A3
    TLS_DH_DSS_WITH_AES_128_GCM_SHA256 = 0x00A4
    TLS_DH_DSS_WITH_AES_256_GCM_SHA384 = 0x00A5
    TLS_DH_ANON_WITH_AES_128_GCM_SHA256 = 0x00A6
    TLS_DH_ANON_WITH_AES_256_GCM_SHA384 = 0x00A7
    TLS_PSK_WITH_AES_128_GCM_SHA256 = 0x00A8
    TLS_PSK_WITH_AES_256_GCM_SHA384 = 0x00A9
    TLS_DHE_PSK_WITH_AES_128_GCM_SHA256 = 0x00AA
    TLS_DHE_PSK_WITH_AES_256_GCM_SHA384 = 0x00AB
    TLS_RSA_PSK_WITH_AES_128_GCM_SHA256 = 0x00AC
    TLS_RSA_PSK_WITH_AES_256_GCM_SHA384 = 0x00AD
    TLS_PSK_WITH_AES_128_CBC_SHA256 = 0x00AE
    TLS_PSK_WITH_AES_256_CBC_SHA384 = 0x00AF
    TLS_PSK_WITH_NULL_SHA256 = 0x00B0
    TLS_PSK_WITH_NULL_SHA384 = 0x00B1
    TLS_DHE_PSK_WITH_AES_128_CBC_SHA256 = 0x00B2
    TLS_DHE_PSK_WITH_AES_256_CBC_SHA384 = 0x00B3
    TLS_DHE_PSK_WITH_NULL_SHA256 = 0x00B4
    TLS_DHE_PSK_WITH_NULL_SHA384 = 0x00B5
    TLS_RSA_PSK_WITH_AES_128_CBC_SHA256 = 0x00B6
    TLS_RSA_PSK_WITH_AES_256_CBC_SHA384 = 0x00B7
    TLS_RSA_PSK_WITH_NULL_SHA256 = 0x00B8
    TLS_RSA_PSK_WITH_NULL_SHA384 = 0x00B9
    TLS_RSA_WITH_CAMELLIA_128_CBC_SHA256 = 0x00BA
    TLS_DH_DSS_WITH_CAMELLIA_128_CBC_SHA256 = 0x00BB
    TLS_DH_RSA_WITH_CAMELLIA_128_CBC_SHA256 = 0x00BC
    TLS_DHE_DSS_WITH_CAMELLIA_128_CBC_SHA256 = 0x00BD
    TLS_DHE_RSA_WITH_CAMELLIA_128_CBC_SHA256 = 0x00BE
    TLS_DH_ANON_WITH_CAMELLIA_128_CBC_SHA256 = 0x00BF
    TLS_RSA_WITH_CAMELLIA_256_CBC_SHA256 = 0x00C0
    TLS_DH_DSS_WITH_CAMELLIA_256_CBC_SHA256 = 0x00C1
    TLS_DH_RSA_WITH_CAMELLIA_256_CBC_SHA256 = 0x00C2
    TLS_DHE_DSS_WITH_CAMELLIA_256_CBC_SHA256 = 0x00C3
    TLS_DHE_RSA_WITH_CAMELLIA_256_CBC_SHA256 = 0x00C4
    TLS_DH_ANON_WITH_CAMELLIA_256_CBC_SHA256 = 0x00C5
    TLS_EMPTY_RENEGOTIATION_INFO_SCSV = 0x00FF
    TLS_AES_128_GCM_SHA256 = 0x1301
    TLS_AES_256_GCM_SHA384 = 0x1302
    TLS_CHACHA20_POLY1305_SHA256 = 0x1303
    TLS_AES_128_CCM_SHA256 = 0x1304
    TLS_AES_128_CCM_8_SHA256 = 0x1305
    TLS_FALLBACK_SCSV = 0x5600
    TLS_ECDH_ECDSA_WITH_NULL_SHA = 0xC001
    TLS_ECDH_ECDSA_WITH_RC4_128_SHA = 0xC002
    TLS_ECDH_ECDSA_WITH_3DES_EDE_CBC_SHA = 0xC003
    TLS_ECDH_ECDSA_WITH_AES_128_CBC_SHA = 0xC004
    TLS_ECDH_ECDSA_WITH_AES_256_CBC_SHA = 0xC005
    TLS_ECDHE_ECDSA_WITH_NULL_SHA = 0xC006
    TLS_ECDHE_ECDSA_WITH_RC4_128_SHA = 0xC007
    TLS_ECDHE_ECDSA_WITH_3DES_EDE_CBC_SHA = 0xC008
    TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA = 0xC009
    TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA = 0xC00A
    TLS_ECDH_RSA_WITH_NULL_SHA = 0xC00B
    TLS_ECDH_RSA_WITH_RC4_128_SHA = 0xC00C
    TLS_ECDH_RSA_WITH_3DES_EDE_CBC_SHA = 0xC00D
    TLS_ECDH_RSA_WITH_AES_128_CBC_SHA = 0xC00E
    TLS_ECDH_RSA_WITH_AES_256_CBC_SHA = 0xC00F
    TLS_ECDHE_RSA_WITH_NULL_SHA = 0xC010
    TLS_ECDHE_RSA_WITH_RC4_128_SHA = 0xC011
    TLS_ECDHE_RSA_WITH_3DES_EDE_CBC_SHA = 0xC012
    TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA = 0xC013
    TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA = 0xC014
    TLS_ECDH_ANON_WITH_NULL_SHA = 0xC015
    TLS_ECDH_ANON_WITH_RC4_128_SHA = 0xC016
    TLS_ECDH_ANON_WITH_3DES_EDE_CBC_SHA = 0xC017
    TLS_ECDH_ANON_WITH_AES_128_CBC_SHA = 0xC018
    TLS_ECDH_ANON_WITH_AES_256_CBC_SHA = 0xC019
    TLS_SRP_SHA_WITH_3DES_EDE_CBC_SHA = 0xC01A
    TLS_SRP_SHA_RSA_WITH_3DES_EDE_CBC_SHA = 0xC01B
    TLS_SRP_SHA_DSS_WITH_3DES_EDE_CBC_SHA = 0xC01C
    TLS_SRP_SHA_WITH_AES_128_CBC_SHA = 0xC01D
    TLS_SRP_SHA_RSA_WITH_AES_128_CBC_SHA = 0xC01E
    TLS_SRP_SHA_DSS_WITH_AES_128_CBC_SHA = 0xC01F
    TLS_SRP_SHA_WITH_AES_256_CBC_SHA = 0xC020
    TLS_SRP_SHA_RSA_WITH_AES_256_CBC_SHA = 0xC021
    TLS_SRP_SHA_DSS_WITH_AES_256_CBC_SHA = 0xC022
    TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA256 = 0xC023
    TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA384 = 0xC024
    TLS_ECDH_ECDSA_WITH_AES_128_CBC_SHA256 = 0xC025
    TLS_ECDH_ECDSA_WITH_AES_256_CBC_SHA384 = 0xC026
    TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA256 = 0xC027
    TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA384 = 0xC028
    TLS_ECDH_RSA_WITH_AES_128_CBC_SHA256 = 0xC029
    TLS_ECDH_RSA_WITH_AES_256_CBC_SHA384 = 0xC02A
    TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256 = 0xC02B
    TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384 = 0xC02C
    TLS_ECDH_ECDSA_WITH_AES_128_GCM_SHA256 = 0xC02D
    TLS_ECDH_ECDSA_WITH_AES_256_GCM_SHA384 = 0xC02E
    TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256 = 0xC02F
    TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384 = 0xC030
    TLS_ECDH_RSA_WITH_AES_128_GCM_SHA256 = 0xC031
    TLS_ECDH_RSA_WITH_AES_256_GCM_SHA384 = 0xC032
    TLS_ECDHE_PSK_WITH_RC4_128_SHA = 0xC033
    TLS_ECDHE_PSK_WITH_3DES_EDE_CBC_SHA = 0xC034
    TLS_ECDHE_PSK_WITH_AES_128_CBC_SHA = 0xC035
    TLS_ECDHE_PSK_WITH_AES_256_CBC_SHA = 0xC036
    TLS_ECDHE_PSK_WITH_AES_128_CBC_SHA256 = 0xC037
    TLS_ECDHE_PSK_WITH_AES_256_CBC_SHA384 = 0xC038
    TLS_ECDHE_PSK_WITH_NULL_SHA = 0xC039
    TLS_ECDHE_PSK_WITH_NULL_SHA256 = 0xC03A
    TLS_ECDHE_PSK_WITH_NULL_SHA384 = 0xC03B
    TLS_RSA_WITH_ARIA_128_CBC_SHA256 = 0xC03C
    TLS_RSA_WITH_ARIA_256_CBC_SHA384 = 0xC03D
    TLS_DH_DSS_WITH_ARIA_128_CBC_SHA256 = 0xC03E
    TLS_DH_DSS_WITH_ARIA_256_CBC_SHA384 = 0xC03F
    TLS_DH_RSA_WITH_ARIA_128_CBC_SHA256 = 0xC040
    TLS_DH_RSA_WITH_ARIA_256_CBC_SHA384 = 0xC041
    TLS_DHE_DSS_WITH_ARIA_128_CBC_SHA256 = 0xC042
    TLS_DHE_DSS_WITH_ARIA_256_CBC_SHA384 = 0xC043
    TLS_DHE_RSA_WITH_ARIA_128_CBC_SHA256 = 0xC044
    TLS_DHE_RSA_WITH_ARIA_256_CBC_SHA384 = 0xC045
    TLS_DH_ANON_WITH_ARIA_128_CBC_SHA256 = 0xC046
    TLS_DH_ANON_WITH_ARIA_256_CBC_SHA384 = 0xC047
    TLS_ECDHE_ECDSA_WITH_ARIA_128_CBC_SHA256 = 0xC048
    TLS_ECDHE_ECDSA_WITH_ARIA_256_CBC_SHA384 = 0xC049
    TLS_ECDH_ECDSA_WITH_ARIA_128_CBC_SHA256 = 0xC04A
    TLS_ECDH_ECDSA_WITH_ARIA_256_CBC_SHA384 = 0xC04B
    TLS_ECDHE_RSA_WITH_ARIA_128_CBC_SHA256 = 0xC04C
    TLS_ECDHE_RSA_WITH_ARIA_256_CBC_SHA384 = 0xC04D
    TLS_ECDH_RSA_WITH_ARIA_128_CBC_SHA256 = 0xC04E
    TLS_ECDH_RSA_WITH_ARIA_256_CBC_SHA384 = 0xC04F
    TLS_RSA_WITH_ARIA_128_GCM_SHA256 = 0xC050
    TLS_RSA_WITH_ARIA_256_GCM_SHA384 = 0xC051
    TLS_DHE_RSA_WITH_ARIA_128_GCM_SHA256 = 0xC052
    TLS_DHE_RSA_WITH_ARIA_256_GCM_SHA384 = 0xC053
    TLS_DH_RSA_WITH_ARIA_128_GCM_SHA256 = 0xC054
    TLS_DH_RSA_WITH_ARIA_256_GCM_SHA384 = 0xC055
    TLS_DHE_DSS_WITH_ARIA_128_GCM_SHA256 = 0xC056
    TLS_DHE_DSS_WITH_ARIA_256_GCM_SHA384 = 0xC057
    TLS_DH_DSS_WITH_ARIA_128_GCM_SHA256 = 0xC058
    TLS_DH_DSS_WITH_ARIA_256_GCM_SHA384 = 0xC059
    TLS_DH_ANON_WITH_ARIA_128_GCM_SHA256 = 0xC05A
    TLS_DH_ANON_WITH_ARIA_256_GCM_SHA384 = 0xC05B
    TLS_ECDHE_ECDSA_WITH_ARIA_128_GCM_SHA256 = 0xC05C
    TLS_ECDHE_ECDSA_WITH_ARIA_256_GCM_SHA384 = 0xC05D
    TLS_ECDH_ECDSA_WITH_ARIA_128_GCM_SHA256 = 0xC05E
    TLS_ECDH_ECDSA_WITH_ARIA_256_GCM_SHA384 = 0xC05F
    TLS_ECDHE_RSA_WITH_ARIA_128_GCM_SHA256 = 0xC060
    TLS_ECDHE_RSA_WITH_ARIA_256_GCM_SHA384 = 0xC061
    TLS_ECDH_RSA_WITH_ARIA_128_GCM_SHA256 = 0xC062
    TLS_ECDH_RSA_WITH_ARIA_256_GCM_SHA384 = 0xC063
    TLS_PSK_WITH_ARIA_128_CBC_SHA256 = 0xC064
    TLS_PSK_WITH_ARIA_256_CBC_SHA384 = 0xC065
    TLS_DHE_PSK_WITH_ARIA_128_CBC_SHA256 = 0xC066
    TLS_DHE_PSK_WITH_ARIA_256_CBC_SHA384 = 0xC067
    TLS_RSA_PSK_WITH_ARIA_128_CBC_SHA256 = 0xC068
    TLS_RSA_PSK_WITH_ARIA_256_CBC_SHA384 = 0xC069
    TLS_PSK_WITH_ARIA_128_GCM_SHA256 = 0xC06A
    TLS_PSK_WITH_ARIA_256_GCM_SHA384 = 0xC06B
    TLS_DHE_PSK_WITH_ARIA_128_GCM_SHA256 = 0xC06C
    TLS_DHE_PSK_WITH_ARIA_256_GCM_SHA384 = 0xC06D
    TLS_RSA_PSK_WITH_ARIA_128_GCM_SHA256 = 0xC06E
    TLS_RSA_PSK_WITH_ARIA_256_GCM_SHA384 = 0xC06F
    TLS_ECDHE_PSK_WITH_ARIA_128_CBC_SHA256 = 0xC070
    TLS_ECDHE_PSK_WITH_ARIA_256_CBC_SHA384 = 0xC071
    TLS_ECDHE_ECDSA_WITH_CAMELLIA_128_CBC_SHA256 = 0xC072
    TLS_ECDHE_ECDSA_WITH_CAMELLIA_256_CBC_SHA384 = 0xC073
    TLS_ECDH_ECDSA_WITH_CAMELLIA_128_CBC_SHA256 = 0xC074
    TLS_ECDH_ECDSA_WITH_CAMELLIA_256_CBC_SHA384 = 0xC075
    TLS_ECDHE_RSA_WITH_CAMELLIA_128_CBC_SHA256 = 0xC076
    TLS_ECDHE_RSA_WITH_CAMELLIA_256_CBC_SHA384 = 0xC077
    TLS_ECDH_RSA_WITH_CAMELLIA_128_CBC_SHA256 = 0xC078
    TLS_ECDH_RSA_WITH_CAMELLIA_256_CBC_SHA384 = 0xC079
    TLS_RSA_WITH_CAMELLIA_128_GCM_SHA256 = 0xC07A
    TLS_RSA_WITH_CAMELLIA_256_GCM_SHA384 = 0xC07B
    TLS_DHE_RSA_WITH_CAMELLIA_128_GCM_SHA256 = 0xC07C
    TLS_DHE_RSA_WITH_CAMELLIA_256_GCM_SHA384 = 0xC07D
    TLS_DH_RSA_WITH_CAMELLIA_128_GCM_SHA256 = 0xC07E
    TLS_DH_RSA_WITH_CAMELLIA_256_GCM_SHA384 = 0xC07F
    TLS_DHE_DSS_WITH_CAMELLIA_128_GCM_SHA256 = 0xC080
    TLS_DHE_DSS_WITH_CAMELLIA_256_GCM_SHA384 = 0xC081
    TLS_DH_DSS_WITH_CAMELLIA_128_GCM_SHA256 = 0xC082
    TLS_DH_DSS_WITH_CAMELLIA_256_GCM_SHA384 = 0xC083
    TLS_DH_ANON_WITH_CAMELLIA_128_GCM_SHA256 = 0xC084
    TLS_DH_ANON_WITH_CAMELLIA_256_GCM_SHA384 = 0xC085
    TLS_ECDHE_ECDSA_WITH_CAMELLIA_128_GCM_SHA256 = 0xC086
    TLS_ECDHE_ECDSA_WITH_CAMELLIA_256_GCM_SHA384 = 0xC087
    TLS_ECDH_ECDSA_WITH_CAMELLIA_128_GCM_SHA256 = 0xC088
    TLS_ECDH_ECDSA_WITH_CAMELLIA_256_GCM_SHA384 = 0xC089
    TLS_ECDHE_RSA_WITH_CAMELLIA_128_GCM_SHA256 = 0xC08A
    TLS_ECDHE_RSA_WITH_CAMELLIA_256_GCM_SHA384 = 0xC08B
    TLS_ECDH_RSA_WITH_CAMELLIA_128_GCM_SHA256 = 0xC08C
    TLS_ECDH_RSA_WITH_CAMELLIA_256_GCM_SHA384 = 0xC08D
    TLS_PSK_WITH_CAMELLIA_128_GCM_SHA256 = 0xC08E
    TLS_PSK_WITH_CAMELLIA_256_GCM_SHA384 = 0xC08F
    TLS_DHE_PSK_WITH_CAMELLIA_128_GCM_SHA256 = 0xC090
    TLS_DHE_PSK_WITH_CAMELLIA_256_GCM_SHA384 = 0xC091
    TLS_RSA_PSK_WITH_CAMELLIA_128_GCM_SHA256 = 0xC092
    TLS_RSA_PSK_WITH_CAMELLIA_256_GCM_SHA384 = 0xC093
    TLS_PSK_WITH_CAMELLIA_128_CBC_SHA256 = 0xC094
    TLS_PSK_WITH_CAMELLIA_256_CBC_SHA384 = 0xC095
    TLS_DHE_PSK_WITH_CAMELLIA_128_CBC_SHA256 = 0xC096
    TLS_DHE_PSK_WITH_CAMELLIA_256_CBC_SHA384 = 0xC097
    TLS_RSA_PSK_WITH_CAMELLIA_128_CBC_SHA256 = 0xC098
    TLS_RSA_PSK_WITH_CAMELLIA_256_CBC_SHA384 = 0xC099
    TLS_ECDHE_PSK_WITH_CAMELLIA_128_CBC_SHA256 = 0xC09A
    TLS_ECDHE_PSK_WITH_CAMELLIA_256_CBC_SHA384 = 0xC09B
    TLS_RSA_WITH_AES_128_CCM = 0xC09C
    TLS_RSA_WITH_AES_256_CCM = 0xC09D
    TLS_DHE_RSA_WITH_AES_128_CCM = 0xC09E
    TLS_DHE_RSA_WITH_AES_256_CCM = 0xC09F
    TLS_RSA_WITH_AES_128_CCM_8 = 0xC0A0
    TLS_RSA_WITH_AES_256_CCM_8 = 0xC0A1
    TLS_DHE_RSA_WITH_AES_128_CCM_8 = 0xC0A2
    TLS_DHE_RSA_WITH_AES_256_CCM_8 = 0xC0A3
    TLS_PSK_WITH_AES_128_CCM = 0xC0A4
    TLS_PSK_WITH_AES_256_CCM = 0xC0A5
    TLS_DHE_PSK_WITH_AES_128_CCM = 0xC0A6
    TLS_DHE_PSK_WITH_AES_256_CCM = 0xC0A7
    TLS_PSK_WITH_AES_128_CCM_8 = 0xC0A8
    TLS_PSK_WITH_AES_256_CCM_8 = 0xC0A9
    TLS_PSK_DHE_WITH_AES_128_CCM_8 = 0xC0AA
    TLS_PSK_DHE_WITH_AES_256_CCM_8 = 0xC0AB
    TLS_ECDHE_ECDSA_WITH_AES_128_CCM = 0xC0AC
    TLS_ECDHE_ECDSA_WITH_AES_256_CCM = 0xC0AD
    TLS_ECDHE_ECDSA_WITH_AES_128_CCM_8 = 0xC0AE
    TLS_ECDHE_ECDSA_WITH_AES_256_CCM_8 = 0xC0AF
    TLS_ECCPWD_WITH_AES_128_GCM_SHA256 = 0xC0B0
    TLS_ECCPWD_WITH_AES_256_GCM_SHA384 = 0xC0B1
    TLS_ECCPWD_WITH_AES_128_CCM_SHA256 = 0xC0B2
    TLS_ECCPWD_WITH_AES_256_CCM_SHA384 = 0xC0B3
    TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256 = 0xCCA8
    TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256 = 0xCCA9
    TLS_DHE_RSA_WITH_CHACHA20_POLY1305_SHA256 = 0xCCAA
    TLS_PSK_WITH_CHACHA20_POLY1305_SHA256 = 0xCCAB
    TLS_ECDHE_PSK_WITH_CHACHA20_POLY1305_SHA256 = 0xCCAC
    TLS_DHE_PSK_WITH_CHACHA20_POLY1305_SHA256 = 0xCCAD
    TLS_RSA_PSK_WITH_CHACHA20_POLY1305_SHA256 = 0xCCAE
    TLS_ECDHE_PSK_WITH_AES_128_GCM_SHA256 = 0xD001
    TLS_ECDHE_PSK_WITH_AES_256_GCM_SHA384 = 0xD002
    TLS_ECDHE_PSK_WITH_AES_128_CCM_8_SHA256 = 0xD003
    TLS_ECDHE_PSK_WITH_AES_128_CCM_SHA256 = 0xD005


class AlertDescription(ExtendedEnum):
    """Enum representing the alert descriptions.

    The values defined correspond to the values used in PDUs as defined by IANA.
    """

    CLOSE_NOTIFY = 0
    UNEXPECTED_MESSAGE = 10
    BAD_RECORD_MAC = 20
    DECRYPTION_FAILED = 21
    RECORD_OVERFLOW = 22
    DECOMPRESSION_FAILED = 30
    HANDSHAKE_FAILURE = 40
    NO_CERTIFICATE = 41
    BAD_CERTIFICATE = 42
    UNSUPPORTED_CERTIFICATE = 43
    CERTIFICATE_REVOKED = 44
    CERTIFICATE_EXPIRED = 45
    CERTIFICATE_UNKNOWN = 46
    ILLEGAL_PARAMETER = 47
    UNKNOWN_CA = 48
    ACCESS_DENIED = 49
    DECODE_ERROR = 50
    DECRYPT_ERROR = 51
    EXPORT_RESTRICTION = 60
    PROTOCOL_VERSION = 70
    INSUFFICIENT_SECURITY = 71
    INTERNAL_ERROR = 80
    INAPPROPRIATE_FALLBACK = 86
    USER_CANCELED = 90
    NO_RENEGOTIATION = 100
    MISSING_EXTENSION = 109
    UNSUPPORTED_EXTENSION = 110
    CERTIFICATE_UNOBTAINABLE = 111
    UNRECOGNIZED_NAME = 112
    BAD_CERTIFICATE_STATUS_RESPONSE = 113
    BAD_CERTIFICATE_HASH_VALUE = 114
    UNKNOWN_PSK_IDENTITY = 115
    CERTIFICATE_REQUIRED = 116
    NO_APPLICATION_PROTOCOL = 120


class AlertLevel(ExtendedEnum):
    """Enum representing the alert level.

    The values defined correspond to the values used in PDUs as defined by IANA.
    """

    WARNING = 1
    FATAL = 2


class HandshakeType(ExtendedEnum):
    """Enum representing the handshake message types.

    The values defined correspond to the values used in PDUs as defined by IANA.
    """

    HELLO_REQUEST = 0
    CLIENT_HELLO = 1
    SERVER_HELLO = 2
    NEW_SESSION_TICKET = 4
    END_OF_EARLY_DATA = 5
    ENCRYPTED_EXTENSIONS = 8
    CERTIFICATE = 11
    SERVER_KEY_EXCHANGE = 12
    CERTIFICATE_REQUEST = 13
    SERVER_HELLO_DONE = 14
    CERTIFICATE_VERIFY = 15
    CLIENT_KEY_EXCHANGE = 16
    FINISHED = 20
    CERTIFICATE_STATUS = 22
    KEY_UPDATE = 24
    COMPRESSED_CERTIFICATE = 25
    EKT_KEY = 26
    MESSAGE_HASH = 254
    # HelloRetryRequest is identical to a ServerHello, we assign a value > 256
    # to it for a clear separation
    HELLO_RETRY_REQUEST = 258


class CCSType(ExtendedEnum):
    """Enum representing the message types for the Change Cipher Spec protocol.

    The values defined correspond to the values used in PDUs as defined by IANA.
    """

    CHANGE_CIPHER_SPEC = 1


class HeartbeatType(ExtendedEnum):
    """Enum representing the message types for the Heartbeat protocol.

    The values defined correspond to the values used in PDUs as defined by IANA.
    """

    HEARTBEAT_REQUEST = 1
    HEARTBEAT_RESPONSE = 2


class SupportedGroups(ExtendedEnum):
    """Enum representing the supported groups.

    The values defined correspond to the values used in PDUs as defined by IANA.
    """

    SECT163K1 = 1
    SECT163R1 = 2
    SECT163R2 = 3
    SECT193R1 = 4
    SECT193R2 = 5
    SECT233K1 = 6
    SECT233R1 = 7
    SECT239K1 = 8
    SECT283K1 = 9
    SECT283R1 = 10
    SECT409K1 = 11
    SECT409R1 = 12
    SECT571K1 = 13
    SECT571R1 = 14
    SECP160K1 = 15
    SECP160R1 = 16
    SECP160R2 = 17
    SECP192K1 = 18
    SECP192R1 = 19
    SECP224K1 = 20
    SECP224R1 = 21
    SECP256K1 = 22
    SECP256R1 = 23
    SECP384R1 = 24
    SECP521R1 = 25
    BRAINPOOLP256R1 = 26
    BRAINPOOLP384R1 = 27
    BRAINPOOLP512R1 = 28
    X25519 = 29
    X448 = 30
    BRAINPOOLP256R1TLS13 = 31
    BRAINPOOLP384R1TLS13 = 32
    BRAINPOOLP512R1TLS13 = 33
    GC256A = 34
    GC256B = 35
    GC256C = 36
    GC256D = 37
    GC512A = 38
    GC512B = 39
    GC512C = 40
    CURVESM2 = 41
    FFDHE2048 = 256
    FFDHE3072 = 257
    FFDHE4096 = 258
    FFDHE6144 = 259
    FFDHE8192 = 260
    ARBITRARY_EXPLICIT_PRIME_CURVES = 65281
    ARBITRARY_EXPLICIT_CHAR2_CURVES = 65282

    @classmethod
    def all_tls13(cls) -> List["SupportedGroups"]:
        """Get all supported groups defined for TLS1.3 (RFC8446, 4.2.7)

        Returns:
            list (:obj:`SupportedGroups`): list of TLS1.3 supported groups
        """

        return [
            cls.SECP256R1,
            cls.SECP384R1,
            cls.SECP521R1,
            cls.X25519,
            cls.X448,
            cls.FFDHE2048,
            cls.FFDHE3072,
            cls.FFDHE4096,
            cls.FFDHE6144,
            cls.FFDHE8192,
        ]


class SignatureAlgorithm(ExtendedEnum):
    """Enum representing the signature algorithms.

    The values defined correspond to the values used in PDUs as defined by IANA.
    """

    ANONYMOUS = 0
    RSA = 1
    DSA = 2
    ECDSA = 3
    ED25519 = 7
    ED448 = 8


class HashPrimitive(ExtendedEnum):
    """Enum representing the hash primitives.

    The values defined correspond to the values used in PDUs as defined by IANA,
    e.g. for the signature algorithms. But we use this enum generally, i.e., as well
    for the hash primitive given in the cipher suite.
    """

    NULL = 0
    MD5 = 1
    SHA1 = 2
    SHA224 = 3
    SHA256 = 4
    SHA384 = 5
    SHA512 = 6
    INTRINSIC = 8


class SignatureScheme(ExtendedEnum):
    """Enum representing the signature schemes.

    The values defined correspond to the values used in PDUs as defined by IANA.
    """

    RSA_PKCS1_SHA1 = 0x0201
    ECDSA_SHA1 = 0x0203
    RSA_PKCS1_SHA256 = 0x0401
    ECDSA_SECP256R1_SHA256 = 0x0403
    RSA_PKCS1_SHA384 = 0x0501
    ECDSA_SECP384R1_SHA384 = 0x0503
    RSA_PKCS1_SHA512 = 0x0601
    ECDSA_SECP521R1_SHA512 = 0x0603
    ECCSI_SHA256 = 0x0704
    RSA_PSS_RSAE_SHA256 = 0x0804
    RSA_PSS_RSAE_SHA384 = 0x0805
    RSA_PSS_RSAE_SHA512 = 0x0806
    ED25519 = 0x0807
    ED448 = 0x0808
    RSA_PSS_PSS_SHA256 = 0x0809
    RSA_PSS_PSS_SHA384 = 0x080A
    RSA_PSS_PSS_SHA512 = 0x080B
    ECDSA_BRAINPOOLP256R1TLS13_SHA256 = 0x081A
    ECDSA_BRAINPOOLP384R1TLS13_SHA384 = 0x081B
    ECDSA_BRAINPOOLP512R1TLS13_SHA512 = 0x081C

    # ***************************************
    # legacy signature schemes needed as well
    # ***************************************
    RSA_PKCS1_MD5 = 0x0101
    RSA_PKCS1_SHA224 = 0x0301
    DSA_MD5 = 0x0102
    DSA_SHA1 = 0x0202
    DSA_SHA224 = 0x0302
    DSA_SHA256 = 0x0402
    DSA_SHA384 = 0x0502
    DSA_SHA512 = 0x0602
    ECDSA_SECP224R1_SHA224 = 0x0303


class EcPointFormat(ExtendedEnum):
    """Enum representing the Elliptic Curve Point Formats.

    The values defined correspond to the values used in PDUs as defined by IANA.
    """

    UNCOMPRESSED = 0
    ANSIX962_COMPRESSED_PRIME = 1
    ANSIX962_COMPRESSED_CHAR2 = 2


class EcCurveType(ExtendedEnum):
    """Enum representing the curve type as received in the ServerKeyExchange message.

    The values defined correspond to the values used in PDUs as defined by IANA.
    """

    EXPLICIT_PRIME = 1
    EXPLICIT_CHAR2 = 2
    NAMED_CURVE = 3


class KeyExchangeAlgorithm(ExtendedEnum):
    """Enum representing the key exchange mechanisms.
    """

    DHE_DSS = enum.auto()
    DHE_DSS_EXPORT = enum.auto()
    DHE_PSK = enum.auto()
    DHE_RSA = enum.auto()
    DHE_RSA_EXPORT = enum.auto()
    DH_ANON = enum.auto()
    DH_ANON_EXPORT = enum.auto()
    DH_DSS = enum.auto()
    DH_DSS_EXPORT = enum.auto()
    DH_RSA = enum.auto()
    DH_RSA_EXPORT = enum.auto()
    ECCPWD = enum.auto()
    ECDHE_ECDSA = enum.auto()
    ECDHE_PSK = enum.auto()
    ECDHE_RSA = enum.auto()
    ECDH_ANON = enum.auto()
    ECDH_ECDSA = enum.auto()
    ECDH_RSA = enum.auto()
    KRB5 = enum.auto()
    KRB5_EXPORT = enum.auto()
    NULL = enum.auto()
    PSK = enum.auto()
    PSK_DHE = enum.auto()
    RSA = enum.auto()
    RSA_EXPORT = enum.auto()
    RSA_PSK = enum.auto()
    SRP_SHA = enum.auto()
    SRP_SHA_DSS = enum.auto()
    SRP_SHA_RSA = enum.auto()
    TLS13_KEY_SHARE = enum.auto()


class KeyExchangeType(ExtendedEnum):
    """Enum representing the key exchange types.
    """

    NONE = enum.auto()
    RSA = enum.auto()
    DH = enum.auto()
    ECDH = enum.auto()


class KeyAuthentication(ExtendedEnum):
    """Enum representing the key authentication method.
    """

    NONE = enum.auto()
    RSA = enum.auto()
    DSS = enum.auto()
    ECDSA = enum.auto()


class CipherPrimitive(ExtendedEnum):
    """Enum representing the cipher primitive.
    """

    NULL = enum.auto()
    AES = enum.auto()
    CAMELLIA = enum.auto()
    IDEA = enum.auto()
    ARIA = enum.auto()
    RC4 = enum.auto()
    RC2 = enum.auto()
    SEED = enum.auto()
    DES = enum.auto()
    TRIPPLE_DES = enum.auto()
    CHACHA = enum.auto()


class SymmetricCipher(ExtendedEnum):
    """Enum representing the ciphers supported by tlsmate.

    "Supported" means, a handshake can be completed successfully, and a secured
    channel is established between both peers.
    """

    TRIPPLE_DES_EDE_CBC = enum.auto()
    AES_128 = enum.auto()
    AES_128_CBC = enum.auto()
    AES_128_CCM = enum.auto()
    AES_128_CCM_8 = enum.auto()
    AES_128_GCM = enum.auto()
    AES_256 = enum.auto()
    AES_256_CBC = enum.auto()
    AES_256_CCM = enum.auto()
    AES_256_CCM_8 = enum.auto()
    AES_256_GCM = enum.auto()
    ARIA_128_CBC = enum.auto()
    ARIA_128_GCM = enum.auto()
    ARIA_256_CBC = enum.auto()
    ARIA_256_GCM = enum.auto()
    CAMELLIA_128_CBC = enum.auto()
    CAMELLIA_128_GCM = enum.auto()
    CAMELLIA_256_CBC = enum.auto()
    CAMELLIA_256_GCM = enum.auto()
    CHACHA20_POLY1305 = enum.auto()
    DES40_CBC = enum.auto()
    DES_CBC = enum.auto()
    DES_CBC_40 = enum.auto()
    IDEA_CBC = enum.auto()
    NULL = enum.auto()
    RC2_CBC_40 = enum.auto()
    RC4_128 = enum.auto()
    RC4_40 = enum.auto()
    SEED_CBC = enum.auto()
    TLS13_AES_128_GCM = enum.auto()
    TLS13_AES_256_GCM = enum.auto()
    TLS13_AES_128_CCM = enum.auto()
    TLS13_AES_128_CCM_8 = enum.auto()


class CipherType(ExtendedEnum):
    """Enum representing the type of the cipher.
    """

    NULL = enum.auto()
    BLOCK = enum.auto()
    STREAM = enum.auto()
    AEAD = enum.auto()


class PskKeyExchangeMode(ExtendedEnum):
    """Values used in the extension psk_key_exchange_mode.
    """

    PSK_KE = 0
    PSK_DHE_KE = 1


class HeartbeatMode(ExtendedEnum):
    """Values for the heartbeat mode (extension)
    """

    PEER_ALLOWED_TO_SEND = 1
    PEER_NOT_ALLOWED_TO_SEND = 2


class ScanState(ExtendedEnum):
    """Enum representing a pseudo-boolean value in the server profile.

    In addition to True and False the two values are defined:

    * UNDETERMINED - used when tlsmate has not even tried to determine the
      value or if the value could not determined at all (for whatever reason).

    * NA - Used as an indication this the boolean value is not applicable, e.g.
      when the server does not support any CBC-cipher suite, support for the
      extension ENCRYPT_THEN_MAC is not applicable.
    """

    FALSE = 0
    TRUE = 1
    NA = 2
    UNDETERMINED = 3


class SSLMessagType(ExtendedEnum):
    """Enum representing the message types for SSL2.

    The values defined correspond to the values used in PDUs as defined by IANA.
    """

    SSL2_ERROR = 0
    SSL2_CLIENT_HELLO = 1
    SSL2_CLIENT_MASTER_KEY = 2
    SSL2_CLIENT_FINISHED = 3
    SSL2_SERVER_HELLO = 4
    SSL2_SERVER_VERIFY = 5
    SSL2_SERVER_FINISHED = 6
    SSL2_REQUEST_CERTIFICATE = 7
    SSL2_CLIENT_CERTIFICATE = 8


class SSLCipherKind(ExtendedEnum):
    """Enum representing cipher suite ("cipher kind" in SSL2 jargon).

    The values defined correspond to the values used in PDUs.

    Note:
        The cipher kind has a length of 3 bytes and is completely disjunct from the
        TLS cipher suites.
    """

    SSL_CK_RC4_128_WITH_MD5 = 0x010080
    SSL_CK_RC4_128_EXPORT40_WITH_MD5 = 0x020080
    SSL_CK_RC2_128_CBC_WITH_MD5 = 0x030080
    SSL_CK_RC2_128_CBC_EXPORT40_WITH_MD5 = 0x040080
    SSL_CK_IDEA_128_CBC_WITH_MD5 = 0x050080
    SSL_CK_DES_64_CBC_WITH_MD5 = 0x060040
    SSL_CK_DES_192_EDE3_CBC_WITH_MD5 = 0x0700C0


class SSLVersion(ExtendedEnum):
    """Enum representing the SSL2 version.

    The values defined correspond to the values used in PDUs.
    """

    SSL2 = 0x0002


class SSLError(ExtendedEnum):
    """Enum representing SSLv2 errors.
    """

    NO_CIPHER = 0x0001
    NO_CERTIFICATE = 0x0002
    BAD_CERTIFICATE = 0x0004
    UNSUPPORTED_CERTIFICATE_TYPE = 0x0006


class CertType(ExtendedEnum):
    """Enum representing certificate types.
    """

    RSA_SIGN = 1
    DSS_SIGN = 2
    RSA_FIXED_DH = 3
    DSS_FIXED_DH = 4
    RSA_EPHEMERAL_DH = 5
    DSS_EPHEMERAL_DH = 6
    FORTEZZA_DMS = 20
    ECDSA_SIGN = 64
    RSA_FIXED_ECDH = 65
    ECDSA_FIXED_ECDH = 66


class CertKeyUsage(ExtendedEnum):
    """Representing the various flags of the KeyUsage extension for certificates
    """

    DIGITAL_SIGNATURE = enum.auto()
    CONTENT_COMMITMENT = enum.auto()
    KEY_ENCIPHERMENT = enum.auto()
    DATA_ENCIPHERMENT = enum.auto()
    KEY_AGREEMENT = enum.auto()
    KEY_CERT_SIGN = enum.auto()
    CRL_SIGN = enum.auto()
    ENCIPHER_ONLY = enum.auto()
    DECIPHER_ONLY = enum.auto()


class CertCrlStatus(ExtendedEnum):
    """CRL Revocation Status
    """

    UNDETERMINED = enum.auto()
    NOT_REVOKED = enum.auto()
    REVOKED = enum.auto()
    CRL_DOWNLOAD_FAILED = enum.auto()
    WRONG_CRL_ISSUER = enum.auto()
    INVALID_TIMESTAMP = enum.auto()
    CRL_SIGNATURE_INVALID = enum.auto()


class OcspStatus(ExtendedEnum):
    """OCSP revocation status
    """

    NOT_APPLICABLE = enum.auto()
    NOT_SUPPORTED = enum.auto()
    UNDETERMINED = enum.auto()
    NOT_REVOKED = enum.auto()
    REVOKED = enum.auto()
    UNKNOWN = enum.auto()
    TIMEOUT = enum.auto()
    INVALID_RESPONSE = enum.auto()
    SIGNATURE_INVALID = enum.auto()
    INVALID_TIMESTAMP = enum.auto()
    NO_ISSUER = enum.auto()
    INVALID_ISSUER_CERT = enum.auto()


class Profile(ExtendedEnum):
    """Different types for client profile
    """

    LEGACY = enum.auto()
    INTEROPERABILITY = enum.auto()
    MODERN = enum.auto()
    TLS13 = enum.auto()


class HostType(ExtendedEnum):
    """Type of an IP-endpoint
    """

    HOST = enum.auto()
    IPV4 = enum.auto()
    IPV6 = enum.auto()


class RobotVulnerability(ExtendedEnum):
    """Status for the ROBOT vulnerability
    """

    NOT_APPLICABLE = enum.auto()
    UNDETERMINED = enum.auto()
    INCONSITENT_RESULTS = enum.auto()
    WEAK_ORACLE = enum.auto()
    STRONG_ORACLE = enum.auto()
    NOT_VULNERABLE = enum.auto()


class HeartbleedStatus(ExtendedEnum):
    """Status for heartbleed vulnerability
    """

    NOT_APPLICABLE = enum.auto()
    UNDETERMINED = enum.auto()
    VULNERABLE = enum.auto()
    NOT_VULNERABLE = enum.auto()
    TIMEOUT = enum.auto()
    CONNECTION_CLOSED = enum.auto()


class HeartbeatState(ExtendedEnum):
    """Status for heartbeart support
    """

    FALSE = 0
    TRUE = 1
    NA = 2
    UNDETERMINED = 3
    NOT_REPONDING = 4
    WRONG_RESPONSE = 5
    UNEXPECTED_MESSAGE = 6


class StatusType(ExtendedEnum):
    """Status type for TLS extension status_request
    """

    OCSP = 1
    OCSP_MULTI = 2
    NONE = 256


class SPCbcPaddingOracle(ExtendedEnum):
    """Different types of CBC padding oracles
    """

    LUCKY_MINUS_20 = enum.auto()
    PADDING_FILLS_RECORD = enum.auto()
    PADDING_EXCEEDS_RECORD = enum.auto()
    INVALID_PADDING = enum.auto()
    INVALID_MAC = enum.auto()


class OracleScanAccuracy(ExtendedEnum):
    """How accurate the scan for CBC padding oracles shall be
    """

    LOW = enum.auto()
    MEDIUM = enum.auto()
    HIGH = enum.auto()


class ServerIssue(ExtendedEnum):
    """Indication of a severe server violation
    """

    PSK_OUT_OF_RANGE = "selected PSK out of range (TLS1.3)"
    KEY_SHARE_NOT_PRESENT = "ServerHello, TLS13: extension KEY_SHARE not present"
    SECURE_RENEG_FAILED = "secure renegotiation check failed"
    VERIFY_DATA_INVALID = "received Finished: verify data does not match"
    CERT_REQ_NO_SIG_ALGO = (
        "certificate request without extension SignatureAlgorithms received"
    )
    EXTENTION_LENGHT_ERROR = "extension length incorrect"
    SNI_NO_HOSTNAME = "host_name not present"
    FFDH_GROUP_UNKNOWN = "FF-DH group unknown"
    MESSAGE_LENGTH_ERROR = "message length incorrect"
    INCOMPATIBLE_KEY_EXCHANGE = (
        "key exchange algorithm in ServerKeyExchange message incompatible with "
        "offered cipher suite"
    )
    PARAMETER_LENGTH_ERROR = "message length error when unpacking parameter"
    RECORD_TOO_SHORT = "decoded record shorter than MAC length"
    RECORD_MAC_INVALID = "MAC verification failed"
    RECORD_WRONG_PADDING_LENGTH = "wrong padding length"
    RECORD_WRONG_PADDING_BYTES = "wrong padding byte contents"
    ILLEGAL_PARAMETER_VALUE = "received parameter value is illegal"
    KEX_INVALID_SIGNATURE = "signature of server's key exchange parameters invalid"


class Logjam(ExtendedEnum):
    """The type of logjam weakness
    """

    NA = enum.auto()
    OK = enum.auto()
    UNDETERMINED = enum.auto()
    PRIME512 = enum.auto()
    PRIME1024_COMMON = enum.auto()
    PRIME1024_CUSTOMIZED = enum.auto()


##############
# Exceptions #
##############


class TlsmateException(Exception):
    """A class all exception for tlsmate are based on.
    """


class ServerMalfunction(TlsmateException):
    """Exception raised in case the server response contains unrecoverable errors.

    This exception basically indicates a specification violation by the server.

    Attributes:
        issue: the reason for the exception
        message: the message, if applicable
        extension: the extension, if applicable
    """

    def __init__(
        self,
        issue: ServerIssue,
        message: Optional[Union[HandshakeType, CCSType]] = None,
        extension: Optional[Extension] = None,
    ) -> None:
        super().__init__(issue.value)
        self.issue = issue
        self.message = message
        self.extension = extension


class TlsConnectionClosedError(TlsmateException):
    """Exception raised when the TLS connection is closed unexpectedly.

    Attributes:
        exc: the original exception
    """

    def __init__(self, exc: Optional[Exception] = None) -> None:
        self.exc = exc


class TlsMsgTimeoutError(TlsmateException):
    """Exception raised when a message is not received within a given timeout.
    """

    pass


class CurveNotSupportedError(TlsmateException):
    """Exception raised when a curve is negotiated which is not supported.

    Attributes:
        message: A human readable string providing the cause
        curve: The curve has been offered by the client, and selected by the
            server, but it is not supported for a full key exchange.
    """

    def __init__(self, message: str, curve: SupportedGroups) -> None:
        self.message = message
        self.curve = curve


class ScanError(TlsmateException):
    """Exception which might occur during a scan.

    The exception will be raised if an abnormal condition during a scan is
    detected.

    Attributes:
        message: A human readable string describing the cause.
    """

    def __init__(self, message: str) -> None:
        self.message = message


class OcspError(TlsmateException):
    """Exception for OCSP errors

    Attributes:
        issue: A human readable string describing the cause.
    """

    def __init__(self, issue: str) -> None:
        self.issue = issue


class UntrustedCertificate(TlsmateException):
    """Exception for unsuccessful certificate (chain) validation.

    Attributes:
        issue: A human readable string describing the cause.
    """

    def __init__(self, issue: str) -> None:
        self.issue = issue


class ServerParmsSignatureInvalid(TlsmateException):
    """More user friendly exception than cryptography.exception.InvalidSignature
    """
