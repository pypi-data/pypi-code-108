# -*- coding: utf-8 -*-
"""Module containing the server profile class

The class :class:`ServerProfile` is the base for storing TLS server scan results.
A basic work flow for a server scan is as follows:

* The server profile is initialized and contains no data at the beginning.

* The scan is started, and the workers do their job. They are storing their
  results in the server profile. For example, first the supported TLS versions
  are determined together with the supported cipher suites. Next, the workers
  scan for the supported groups and the supported signature algorithms.

* At this point in time the server profile can be read by subsequent workers. E.g.,
  DH-parameters are only checked, if the server profile contains cipher suites
  using the DH key exchange. The DH-scanner worker will use the corresponding
  TLS versions, cipher suites and other parameters, knowing that they are all
  supported by the server. Then the worker will store its results in the server
  profile as well.

* After the scan is finished, the server profile can either be stored in a JSON/YAML
  file, or an extract from the server profile can be displayed on the screen (by a
  dedicated worker).

The server profile can also be used as a base for customized test cases: if a
scan has been executed against the target and the server profile has been serialized
to a file, then this server profile can be deserialized, and thus the test case can
use the data from it to evaluate if the feature to be tested is supported by the
target, and if so, the server profile values can be used to initiate connection to
the target with parameters known to be supported. This is exactly what the provided
workers do.

The YAML/JSON schema of a serialized server profile is described by the class
:class:`ServerProfileSchema` (and its nested schema classes). Look at the code
if you want to see the detailed structure.
"""
# import basic stuff
import abc
import logging
from typing import List, Tuple, Type, Any, Dict, Optional

# import own stuff
import tlsmate.cert as crt
import tlsmate.cert_chain as cert_chain
import tlsmate.mappings as mappings
import tlsmate.pdu as pdu
import tlsmate.structs as structs
import tlsmate.tls as tls
import tlsmate.utils as utils

# import other stuff
import yaml
from cryptography.hazmat.primitives.asymmetric import rsa, ed25519, ed448, dsa, ec
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from cryptography import x509
from marshmallow import fields, Schema, post_load, post_dump, pre_dump, INCLUDE
from marshmallow_oneofschema import OneOfSchema  # type: ignore

# #### Helper classes


class _YamlBlockStyle(str):
    """Class used to indicate that a string shall be serialized using the block style.
    """


def _literal_presenter(dumper, data):
    return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")


yaml.add_representer(_YamlBlockStyle, _literal_presenter)


class FieldsEnumString(fields.String):
    """Adapted marshmallow field for ExtendedEnums.

    An extended enum is serialized to a string field, containing the name of the enum.

    Example:
        ::

            In the schema class:
                field = FieldsEnumString(enum_class=tls.Version)

            In the data object:
                obj.field = tls.Version.TLS10

            Serialized:
                "field": "TLS10"

    Arguments:
        enum_class: The enum class used for deserialization.
    """

    default_error_messages = fields.String.default_error_messages
    default_error_messages.update({"not_in_enum": "String not defined in enum"})

    def __init__(self, enum_class: Type[tls.ExtendedEnum], **kwargs: Any) -> None:
        if enum_class is None:
            raise ValueError("FieldsEnumString: enum_class not given")

        # TODO: replace issubclass with isinstance?
        if not issubclass(enum_class, tls.ExtendedEnum):  # type: ignore
            raise ValueError("FieldsEnumString: class must be ExtendedEnum")

        self.enum_class = enum_class
        super().__init__(**kwargs)

    def _serialize(self, value, attr, obj, **kwargs):
        if not isinstance(value, self.enum_class):
            return None

        return super()._serialize(value.name, attr, obj, **kwargs)

    def _deserialize(self, value, attr, data, **kwargs):
        ret = self.enum_class.str2enum(value)
        if ret is None:
            raise self.make_error("not_in_enum")

        return ret


class FieldsBytes(fields.String):
    """Adapted marshmallow field for bytes.

    A bytes object will be serialized to a string where the bytes are separated by
    a colon.

    Example:
        ::

            b"Hallo" will be serialized to "48:61:6c:6c:6f"
    """

    default_error_messages = fields.String.default_error_messages
    default_error_messages.update({"not_in_enum": "String not defined in enum"})

    def _serialize(self, value, attr, obj, **kwargs):
        if not isinstance(value, (bytes, bytearray)):
            return None

        return pdu.string(value)

    def _deserialize(self, value, attr, data, **kwargs):
        return bytes.fromhex(
            "".join([c for c in value if c in "0123456789abcdefABCDEF"])
        )


class FieldsBlockString(fields.String):
    """Adapted marshmallow field strings which shall be displayed in block style (yaml).
    """

    def _serialize(self, value, attr, obj, **kwargs):
        return _YamlBlockStyle(value)


class ProfileSchema(Schema):
    """Wrapper class for easier deserialization to objects
    """

    _augments: List[Tuple[Type[Schema], Type[Schema]]] = []

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        # self.unknown = INCLUDE
        self.unknown = INCLUDE

    @post_load
    def deserialize(
        self, data: Dict[str, Any], reuse_object: Optional[bool] = None, **kwargs
    ) -> Any:
        """Instantiate an object and define the properties according to the given dict.

        Arguments:
            data (dict): dict representing the properties of the object we need to
                deserialize.

        Returns:
            Deserialized data, either a newly instantiated object (if given by the
            __profile_class__ class property), or the original dict.
        """

        cls = getattr(self, "__profile_class__", None)
        if cls is None:
            return data

        cls_data = self._get_schema_data(data)
        if reuse_object:
            obj = reuse_object
            # TODO: avoid calling __init__
            obj.__init__(data=cls_data)  # type: ignore

        else:
            obj = cls(data=cls_data)

        for base_cls, ext_cls in self._augments:
            if base_cls is self.__class__:
                cls_data = ext_cls._get_schema_data(data)  # type: ignore
                ext_data = ext_cls().load(cls_data)
                for key, val in ext_data.items():
                    setattr(obj, key, val)

        if data:
            fields = ", ".join(data.keys())
            raise ValueError(
                f"fields not defined in schema {self.__class__.__name__}: {fields}"
            )

        return obj

    @post_dump(pass_original=True)
    def serialize(
        self, data: Dict[str, Any], orig: Any, **kwargs: Any
    ) -> Dict[str, Any]:
        """Deserialize properties not covered by the schema as well.

        Arguments:
            data: the serialized data so far
            orig: the original object subject to serialization

        Returns:
            the final dict representing the serialized object
        """

        for base_cls, ext_cls in self._augments:
            if base_cls is self.__class__:
                data.update(ext_cls().dump(orig))
        return data

    @classmethod
    def _get_schema_data(cls, data):
        cls_data = {}
        for key in cls._declared_fields.keys():
            if key in data:
                cls_data[key] = data[key]
                del data[key]
        return cls_data

    @classmethod
    def augment(cls, ext_cls: Type["ProfileSchema"]) -> Type["ProfileSchema"]:
        """Decorator to register scheme extensions.

        cls is the class to be extended.

        Examlple:
            @SPServerProfile.augment
            class MyExtensions(ProfileSchema):
                client_simulation = fields.Nested(...)
                a_number = fields.Integer()

        This extends the schema class SPServerProfile by two more attributes.
        Note, that __profile_class__ must not be given in the extension class. The
        name of the extension class has no relevance.

        Arguments:
            ext_cls: the schema class containing the extensions

        Returns:
            the class used to extend the base_cls class
        """

        cls._augments.append((cls, ext_cls))
        return ext_cls


class ProfileEnumSchema(Schema):
    """Wrapper class for simpler (de)serialization of Enums.
    """

    id = fields.Integer()
    name = fields.String()

    @post_load
    def deserialize(self, data: Dict[str, Any], **kwargs: Any) -> Any:
        # TODO: enable type check
        return self.__profile_class__(data["id"])  # type: ignore

    @pre_dump
    def serialize(self, obj: tls.ExtendedEnum, **kwargs: Any) -> Dict[str, Any]:
        return {"id": obj.value, "name": obj.name}


class SPObject(metaclass=abc.ABCMeta):
    """Basic class for profile data, provides easy deserialization from dicts.

    Arguments:
        data(dict): a dictionary which is converted into object properties.
        obj: an object to initialize the instance from.
    """

    def __init__(self, data: Optional[Dict[str, Any]] = None, **kwargs: Any) -> None:
        if data is None:
            data = {}

        for key, val in {**data, **kwargs}.items():
            if val is not None:
                setattr(self, key, val)


# ### Classes used for the server profile


class SPScanInfo(SPObject):
    """Data class for scan infos.
    """


class SPScanInfoSchema(ProfileSchema):
    """Schema for scan infos.
    """

    __profile_class__ = SPScanInfo
    command = fields.String()
    proxy = fields.String()
    run_time = fields.Float()
    start_date = fields.DateTime()
    start_timestamp = fields.Float()
    stop_date = fields.DateTime()
    stop_timestamp = fields.Float()
    version = fields.String()


class SPCompressionEnumSchema(ProfileEnumSchema):
    """Schema for compression method (enum)
    """

    __profile_class__ = tls.CompressionMethod


class SPGrease(SPObject):
    """Data class for GREASE
    """


class SPGreaseSchema(ProfileSchema):
    """Schema for GREASE
    """

    __profile_class__ = SPGrease
    version_tolerance = FieldsEnumString(enum_class=tls.ScanState)
    cipher_suite_tolerance = FieldsEnumString(enum_class=tls.ScanState)
    extension_tolerance = FieldsEnumString(enum_class=tls.ScanState)
    group_tolerance = FieldsEnumString(enum_class=tls.ScanState)
    sig_algo_tolerance = FieldsEnumString(enum_class=tls.ScanState)
    psk_mode_tolerance = FieldsEnumString(enum_class=tls.ScanState)


class SPEphemeralKeyReuse(SPObject):
    """Data class for ephemeral key reuse
    """


class SPEphemeralKeyReuseSchema(ProfileSchema):
    """Schema for ephemeral key reuse
    """

    __profile_class__ = SPEphemeralKeyReuse
    tls12_dhe_reuse = FieldsEnumString(enum_class=tls.ScanState)
    tls12_ecdhe_reuse = FieldsEnumString(enum_class=tls.ScanState)
    tls13_dhe_reuse = FieldsEnumString(enum_class=tls.ScanState)
    tls13_ecdhe_reuse = FieldsEnumString(enum_class=tls.ScanState)


class SPFeatures(SPObject):
    """Data class for TLS features.
    """


class SPFeaturesSchema(ProfileSchema):
    """Schema for TLS features.
    """

    __profile_class__ = SPFeatures
    compression = fields.List(fields.Nested(SPCompressionEnumSchema))
    encrypt_then_mac = FieldsEnumString(enum_class=tls.ScanState)
    extended_master_secret = FieldsEnumString(enum_class=tls.ScanState)
    session_id = FieldsEnumString(enum_class=tls.ScanState)
    session_ticket = FieldsEnumString(enum_class=tls.ScanState)
    session_ticket_lifetime = fields.Integer()
    resumption_psk = FieldsEnumString(enum_class=tls.ScanState)
    early_data = FieldsEnumString(enum_class=tls.ScanState)
    psk_lifetime = fields.Integer()
    insecure_renegotiation = FieldsEnumString(enum_class=tls.ScanState)
    secure_renegotation = FieldsEnumString(enum_class=tls.ScanState)
    scsv_renegotiation = FieldsEnumString(enum_class=tls.ScanState)
    heartbeat = FieldsEnumString(enum_class=tls.HeartbeatState)
    grease = fields.Nested(SPGreaseSchema)
    ephemeral_key_reuse = fields.Nested(SPEphemeralKeyReuseSchema)
    ocsp_stapling = FieldsEnumString(enum_class=tls.ScanState)
    ocsp_multi_stapling = FieldsEnumString(enum_class=tls.ScanState)
    downgrade_attack_prevention = FieldsEnumString(enum_class=tls.ScanState)


class SPPublicKey(SPObject):
    """Data class for all types of public key
    """

    def __init__(self, pub_key: Any = None, **kwargs) -> None:
        super().__init__(**kwargs)
        if not pub_key:
            return

        if isinstance(pub_key, rsa.RSAPublicKey):
            self.key_size = pub_key.key_size
            self.key_type = tls.SignatureAlgorithm.RSA
            pub_numbers = pub_key.public_numbers()
            self.key_exponent = pub_numbers.e
            self.key = pub_numbers.n.to_bytes(int(pub_key.key_size / 8), "big")

        elif isinstance(pub_key, dsa.DSAPublicKey):
            self.key_size = pub_key.key_size
            self.key_type = tls.SignatureAlgorithm.DSA
            pub_numbers = pub_key.public_numbers()  # type: ignore
            self.key = pub_numbers.y.to_bytes(  # type: ignore
                int(pub_key.key_size / 8), "big"
            )

            self.key_p = utils.int_to_bytes(
                pub_numbers.parameter_numbers.p  # type:ignore
            )
            self.key_q = utils.int_to_bytes(
                pub_numbers.parameter_numbers.q  # type:ignore
            )
            self.key_g = utils.int_to_bytes(
                pub_numbers.parameter_numbers.g  # type:ignore
            )

        elif isinstance(pub_key, ec.EllipticCurvePublicKey):
            self.key_size = pub_key.key_size
            self.key_type = tls.SignatureAlgorithm.ECDSA
            group = mappings.curve_to_group.get(pub_key.curve.name)
            if group is None:
                raise ValueError("curve {pub_key.curve.name} unknown")
            self.curve = group
            self.key = pub_key.public_bytes(
                Encoding.X962, PublicFormat.UncompressedPoint
            )

        elif isinstance(pub_key, ed25519.Ed25519PublicKey):
            self.key_size = 256
            self.key_type = tls.SignatureAlgorithm.ED25519
            self.key = pub_key.public_bytes(Encoding.Raw, PublicFormat.Raw)

        elif isinstance(pub_key, ed448.Ed448PublicKey):
            self.key_size = 456
            self.key_type = tls.SignatureAlgorithm.ED448
            self.key = pub_key.public_bytes(Encoding.Raw, PublicFormat.Raw)


class SPPubKeyRsaSchema(ProfileSchema):
    """Schema for RSA public key.
    """

    __profile_class__ = SPPublicKey
    key_type = FieldsEnumString(enum_class=tls.SignatureAlgorithm)
    key = FieldsBytes()
    key_exponent = fields.Integer()
    key_size = fields.Integer()


class SPPubKeyDsaSchema(ProfileSchema):
    """Schema for DSA public key.
    """

    __profile_class__ = SPPublicKey
    key_type = FieldsEnumString(enum_class=tls.SignatureAlgorithm)
    key = FieldsBytes()
    key_p = FieldsBytes()
    key_q = FieldsBytes()
    key_g = FieldsBytes()


class SPPubKeyEcdsaSchema(ProfileSchema):
    """Schema for ECDSA public key.
    """

    __profile_class__ = SPPublicKey
    key_type = FieldsEnumString(enum_class=tls.SignatureAlgorithm)
    key = FieldsBytes()
    curve = FieldsEnumString(enum_class=tls.SupportedGroups)
    key_size = fields.Integer()


class SPPubKeyEdSchema(ProfileSchema):
    """Schema for ED25519 and ED448 public key
    """

    __profile_class__ = SPPublicKey
    key_type = FieldsEnumString(enum_class=tls.SignatureAlgorithm)
    key = FieldsBytes()


class SPPublicKeySchema(OneOfSchema):
    """Choice of public key types
    """

    type_field = "key_type"
    type_field_remove = False
    type_schemas = {
        "ECDSA": SPPubKeyEcdsaSchema,
        "RSA": SPPubKeyRsaSchema,
        "DSA": SPPubKeyDsaSchema,
        "ED25519": SPPubKeyEdSchema,
        "ED448": SPPubKeyEdSchema,
    }

    def get_obj_type(self, obj: Any) -> str:
        return obj.key_type.name


class SPCertGeneralName(SPObject):
    """Data class for general name
    """

    # TODO: replace Any by x509 class
    def __init__(self, name: Optional[Any] = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        if not name:
            return

        if isinstance(name, x509.RFC822Name):
            self.rfc822_name = name.value

        elif isinstance(name, x509.DNSName):
            self.dns_name = name.value

        elif isinstance(name, x509.DirectoryName):
            self.directory_name = name.value.rfc4514_string()

        elif isinstance(name, x509.UniformResourceIdentifier):
            self.uri = name.value

        elif isinstance(name, x509.IPAddress):
            self.ip_address = name.value

        else:
            logging.error(f"certificate extension: general name {name} not supported")


class SPCertGeneralNameSchema(ProfileSchema):
    """Schema for general name
    """

    __profile_class__ = SPCertGeneralName
    rfc822_name = fields.String()
    dns_name = fields.String()
    directory_name = fields.String()
    uri = fields.String()
    ip_address = fields.String()
    registered_id = fields.String()


# TODO: implement other name
#    other_name = fields.Nested(SpCertOtherNameSchema)


class SPCertNoticeReference(SPObject):
    """Data class for notice reference
    """

    # TODO: replace Any by x509 class
    def __init__(self, ref: Optional[Any] = None, **kwargs) -> None:
        super().__init__(**kwargs)
        if not ref:
            return

        self.organization = ref.organization
        self.notice_numbers = [number for number in ref.notice_numbers]


class SPCertNoticeReferenceSchema(ProfileSchema):
    """Schema for notice reference
    """

    __profile_class__ = SPCertNoticeReference
    organization = fields.String()
    notice_numbers = fields.List(fields.Integer())


class SPCertUserNotice(SPObject):
    """Data class for user notice
    """

    # TODO: replace Any by x509 class
    def __init__(self, notice: Optional[Any] = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        if not notice:
            return

        if isinstance(notice, x509.UserNotice):
            self.explicit_text = notice.explicit_text
            if notice.notice_reference is not None:
                self.notice_reference = SPCertNoticeReference(
                    ref=notice.notice_reference
                )

        else:
            self.text = notice


class SPCertUserNoticeSchema(ProfileSchema):
    """Schema for user notice
    """

    __profile_class__ = SPCertUserNotice
    explicit_text = fields.String()
    notice_reference = fields.Nested(SPCertNoticeReferenceSchema)
    text = fields.String()


class SPDistrPoint(SPObject):
    """Data class for distribution point
    """

    # TODO: replace Any by x509 class
    def __init__(self, point: Optional[Any] = None, **kwargs) -> None:
        super().__init__(**kwargs)
        if not point:
            return

        if point.full_name is not None:
            self.full_name = [SPCertGeneralName(name=name) for name in point.full_name]

        if point.relative_name is not None:
            logging.error(
                "Certificate extensions CrlDistrPoints: relative name "
                "not implemented"
            )

        if point.crl_issuer is not None:
            logging.error(
                "Certificate extensions CrlDistrPoints: crl_issuer not implemented"
            )

        if point.reasons is not None:
            logging.error(
                "Certificate extensions CrlDistrPoints: reasons not implemented"
            )


class SPDistrPointSchema(ProfileSchema):
    """Schema for distribution point
    """

    __profile_class__ = SPDistrPoint
    full_name = fields.List(fields.Nested(SPCertGeneralNameSchema))


class SPCertPolicyInfo(SPObject):
    """Data class for policy info
    """

    # TODO: replace Any by x509 class
    def __init__(self, policy: Optional[Any] = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        if not policy:
            return

        self.policy_name = policy.policy_identifier._name
        self.policy_oid = policy.policy_identifier.dotted_string
        if policy.policy_qualifiers is not None:
            self.policy_qualifiers = [
                SPCertUserNotice(notice=notice) for notice in policy.policy_qualifiers
            ]


class SPCertPolicyInfoSchema(ProfileSchema):
    """Schema for policy info
    """

    __profile_class__ = SPCertPolicyInfo
    policy_name = fields.String()
    policy_oid = fields.String()
    policy_qualifiers = fields.List(fields.Nested(SPCertUserNoticeSchema))


class SPCertAccessDescription(SPObject):
    """Data class for access description
    """

    # TODO: replace Any by x509 class
    def __init__(self, descr: Optional[Any] = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        if not descr:
            return

        self.access_method = descr.access_method._name
        self.access_location = descr.access_location.value


class SPCertAccessDescriptionSchema(ProfileSchema):
    """Schema for access description
    """

    __profile_class__ = SPCertAccessDescription
    access_method = fields.String()
    access_location = fields.String()


class SPCertSignedTimestamp(SPObject):
    """Data class for signed certificate timestamp
    """

    # TODO: replace Any by x509 class
    def __init__(self, timestamp: Optional[Any] = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        if not timestamp:
            return

        self.version = timestamp.version.name
        self.log_id = timestamp.log_id
        self.timestamp = timestamp.timestamp
        self.entry_type = timestamp.entry_type.name


class SPCertSignedTimestampSchema(ProfileSchema):
    """Schema for signed certificate timestamp
    """

    __profile_class__ = SPCertSignedTimestamp
    version = fields.String()
    log_id = FieldsBytes()
    timestamp = fields.DateTime()
    entry_type = fields.String()


class SPCertExtension(SPObject):
    """Data class for all extensions
    """

    def _ext_unrecognized_extension(self, value):
        self.bytes = value.value

    def _ext_key_usage(self, value):
        key_usage = []
        if value.digital_signature:
            key_usage.append(tls.CertKeyUsage.DIGITAL_SIGNATURE)

        if value.content_commitment:
            key_usage.append(tls.CertKeyUsage.CONTENT_COMMITMENT)

        if value.key_encipherment:
            key_usage.append(tls.CertKeyUsage.KEY_ENCIPHERMENT)

        if value.data_encipherment:
            key_usage.append(tls.CertKeyUsage.DATA_ENCIPHERMENT)

        if value.key_agreement:
            key_usage.append(tls.CertKeyUsage.KEY_AGREEMENT)
            if value.encipher_only:
                key_usage.append(tls.CertKeyUsage.ENCIPHER_ONLY)

            if value.decipher_only:
                key_usage.append(tls.CertKeyUsage.DECIPHER_ONLY)

        if value.key_cert_sign:
            key_usage.append(tls.CertKeyUsage.KEY_CERT_SIGN)

        if value.crl_sign:
            key_usage.append(tls.CertKeyUsage.CRL_SIGN)

        self.key_usage = key_usage

    def _ext_basic_constraints(self, value):
        self.ca = tls.ScanState(value.ca)
        if value.path_length is not None:
            self.path_length = value.path_length

    def _ext_extended_key_usage(self, value):
        self.extended_key_usage = [usage._name for usage in value]

    def _ext_subjec_key_id(self, value):
        self.digest = value.digest

    def _ext_ocsp_no_check(self, value):
        logging.error("Certificate extensions OcspNoCheck not implemented")

    def _ext_tls_features(self, value):
        self.tls_features = [tls.Extension(feature.value) for feature in value]

    def _ext_name_constraints(self, value):
        self.permitted_subtrees = [
            SPCertGeneralName(name=name) for name in value.permitted_subtrees
        ]
        self.excluded_subtrees = [
            SPCertGeneralName(name=name) for name in value.excluded_subtrees
        ]

    def _ext_authority_key_id(self, value):
        self.key_identifier = value.key_identifier
        if value.authority_cert_issuer is not None:
            self.authority_cert_issuer = [
                SPCertGeneralName(name=name) for name in value.authority_cert_issuer
            ]

        if value.authority_cert_serial_number is not None:
            self.authority_cert_serial_number = value.authority_cert_serial_number

    def _ext_subj_alt_name(self, value):
        self.subj_alt_names = [subj_alt_name.value for subj_alt_name in value]

    def _ext_issuer_alt_name(self, value):
        self.issuer_alt_name = [issuer_alt_name.value for issuer_alt_name in value]

    def _ext_precert_sign_cert_timestamps(self, value):
        self.signed_certificate_timestamps = [
            SPCertSignedTimestamp(timestamp=timestamp) for timestamp in value
        ]

    def _ext_precert_poison(self, value):
        logging.error("Certificate extensions PreCertPoison not implemented")

    def _ext_signed_cert_timestamps(self, value):
        logging.error("Certificate extensions SignedCertTimestamp not implemented")

    def _ext_delta_clr_indicator(self, value):
        logging.error("Certificate extensions DeltaClrIndicator not implemented")

    def _ext_authority_info_access(self, value):
        self.authority_info_access = [
            SPCertAccessDescription(descr=descr) for descr in value
        ]

    def _ext_subject_info_access(self, value):
        logging.error("Certificate extensions SubjectInfoAccess not implemented")

    def _ext_freshest_crl(self, value):
        logging.error("Certificate extensions FreshestCrl not implemented")

    def _ext_crl_distribution_points(self, value):
        self.distribution_points = [SPDistrPoint(point=point) for point in value]

    def _ext_inhibit_any_policy(self, value):
        logging.error("Certificate extensions InhibitAnyPolicy not implemented")

    def _ext_policy_constraints(self, value):
        if value.require_explicit_policy is not None:
            self.require_explicit_policy = value.require_explicit_policy

        if value.inhibit_policy_mapping is not None:
            self.inhibit_policy_mapping = value.inhibit_policy_mapping

    def _ext_crl_number(self, value):
        logging.error("Certificate extensions CrlNumber not implemented")

    def _ext_issuing_dist_point(self, value):
        logging.error("Certificate extensions IssuingDistPoint not implemented")

    def _ext_cert_policies(self, value):
        self.cert_policies = [SPCertPolicyInfo(policy=policy) for policy in value]

    def _ext_cert_issuer(self, value):
        raise NotImplementedError

    def _ext_crl_reason(self, value):
        logging.error("Certificate extensions CertIssuer not implemented")

    def _ext_invalidity_date(self, value):
        logging.error("Certificate extensions InvalidityDate not implemented")

    def _ext_ocsp_nonce(self, value):
        logging.error("Certificate extensions OcspNonce not implemented")

    _map_ext = {
        x509.extensions.KeyUsage: _ext_key_usage,
        x509.extensions.BasicConstraints: _ext_basic_constraints,
        x509.extensions.ExtendedKeyUsage: _ext_extended_key_usage,
        x509.extensions.OCSPNoCheck: _ext_ocsp_no_check,
        x509.extensions.TLSFeature: _ext_tls_features,
        x509.extensions.NameConstraints: _ext_name_constraints,
        x509.extensions.AuthorityKeyIdentifier: _ext_authority_key_id,
        x509.extensions.SubjectKeyIdentifier: _ext_subjec_key_id,
        x509.extensions.SubjectAlternativeName: _ext_subj_alt_name,
        x509.extensions.IssuerAlternativeName: _ext_issuer_alt_name,
        x509.extensions.PrecertificateSignedCertificateTimestamps: _ext_precert_sign_cert_timestamps,  # noqa: E501
        x509.extensions.PrecertPoison: _ext_precert_poison,
        x509.extensions.SignedCertificateTimestamps: _ext_signed_cert_timestamps,
        x509.extensions.DeltaCRLIndicator: _ext_delta_clr_indicator,
        x509.extensions.AuthorityInformationAccess: _ext_authority_info_access,
        x509.extensions.SubjectInformationAccess: _ext_subject_info_access,
        x509.extensions.FreshestCRL: _ext_freshest_crl,
        x509.extensions.CRLDistributionPoints: _ext_crl_distribution_points,
        x509.extensions.InhibitAnyPolicy: _ext_inhibit_any_policy,
        x509.extensions.PolicyConstraints: _ext_policy_constraints,
        x509.extensions.CRLNumber: _ext_crl_number,
        x509.extensions.IssuingDistributionPoint: _ext_issuing_dist_point,
        x509.extensions.UnrecognizedExtension: _ext_unrecognized_extension,
        x509.extensions.CertificatePolicies: _ext_cert_policies,
        x509.extensions.CertificateIssuer: _ext_cert_issuer,
        x509.extensions.CRLReason: _ext_crl_reason,
        x509.extensions.InvalidityDate: _ext_invalidity_date,
        x509.extensions.OCSPNonce: _ext_ocsp_nonce,
    }

    # TODO: replace Any by x509 class
    def __init__(self, ext: Optional[Any] = None, **kwargs) -> None:
        super().__init__(**kwargs)
        if not ext:
            return

        self.name = ext.value.__class__.__name__
        self.oid = ext.oid.dotted_string
        self.criticality = tls.ScanState(ext.critical)
        # TODO: resolve type issue
        func = self._map_ext.get(type(ext.value))  # type: ignore
        if func is not None:
            func(self, ext.value)


class SPCertExtUnrecognizedExtensionSchema(ProfileSchema):
    """Data class for unknown certificate extension
    """

    __profile_class__ = SPCertExtension
    name = fields.String()
    oid = fields.String()
    criticality = FieldsEnumString(enum_class=tls.ScanState)
    bytes = FieldsBytes()


class SPCertExtKeyUsageSchema(ProfileSchema):
    """Data class for certificate extension KeyUsage
    """

    __profile_class__ = SPCertExtension
    name = fields.String()
    oid = fields.String()
    criticality = FieldsEnumString(enum_class=tls.ScanState)
    key_usage = fields.List(FieldsEnumString(enum_class=tls.CertKeyUsage))


class SPCertExtBasicConstraintsSchema(ProfileSchema):
    """Data class for certificate extension BasicConstraints
    """

    __profile_class__ = SPCertExtension
    name = fields.String()
    oid = fields.String()
    criticality = FieldsEnumString(enum_class=tls.ScanState)
    ca = FieldsEnumString(enum_class=tls.ScanState)
    path_length = fields.Integer()


class SPCertExtExtendedKeyUsageSchema(ProfileSchema):
    """Data class for certificate extension ExtendedKeyUsage
    """

    __profile_class__ = SPCertExtension
    name = fields.String()
    oid = fields.String()
    criticality = FieldsEnumString(enum_class=tls.ScanState)
    extended_key_usage = fields.List(fields.String())


class SPCertExtOCSPNoCheckSchema(ProfileSchema):
    """Data class for certificate extension OCSPNoCheck
    """

    __profile_class__ = SPCertExtension
    name = fields.String()
    oid = fields.String()
    criticality = FieldsEnumString(enum_class=tls.ScanState)


class SPCertExtTLSFeatureSchema(ProfileSchema):
    """Data class for certificate extension TLSFeature
    """

    __profile_class__ = SPCertExtension
    name = fields.String()
    oid = fields.String()
    criticality = FieldsEnumString(enum_class=tls.ScanState)
    tls_features = fields.List(FieldsEnumString(enum_class=tls.Extension))


class SPCertExtNameConstraintsSchema(ProfileSchema):
    """Data class for certificate extension NameConstraints
    """

    __profile_class__ = SPCertExtension
    name = fields.String()
    oid = fields.String()
    criticality = FieldsEnumString(enum_class=tls.ScanState)
    permitted_subtrees = fields.List(fields.Nested(SPCertGeneralNameSchema))
    excluded_subtrees = fields.List(fields.Nested(SPCertGeneralNameSchema))


class SPCertExtAuthorityKeyIdentifierSchema(ProfileSchema):
    """Data class for certificate extension AuthorityKeyIdentifier
    """

    __profile_class__ = SPCertExtension
    name = fields.String()
    oid = fields.String()
    criticality = FieldsEnumString(enum_class=tls.ScanState)
    key_identifier = FieldsBytes()
    authority_cert_issuer = fields.List(fields.Nested(SPCertGeneralNameSchema))
    authority_cert_serial_number = fields.Integer()


class SPCertExtSubjectKeyIdentifierSchema(ProfileSchema):
    """Data class for certificate extension SubjectKeyIdentifier
    """

    __profile_class__ = SPCertExtension
    name = fields.String()
    oid = fields.String()
    criticality = FieldsEnumString(enum_class=tls.ScanState)
    digest = FieldsBytes()


class SPCertExtSubjectAlternativeNameSchema(ProfileSchema):
    """Data class for certificate extension SubjectAlternativeName
    """

    __profile_class__ = SPCertExtension
    name = fields.String()
    oid = fields.String()
    criticality = FieldsEnumString(enum_class=tls.ScanState)
    subj_alt_names = fields.List(fields.String())


class SPCertExtIssuerAlternativeNameSchema(ProfileSchema):
    """Data class for certificate extension IssuerAlternativeName
    """

    __profile_class__ = SPCertExtension
    name = fields.String()
    oid = fields.String()
    criticality = FieldsEnumString(enum_class=tls.ScanState)
    issuer_alt_name = fields.List(fields.String())


class SPCertExtPrecertSignedCertTimestampsSchema(ProfileSchema):
    """Data class for certificate extension ExtPrecertSignedCertTimestamps
    """

    __profile_class__ = SPCertExtension
    name = fields.String()
    oid = fields.String()
    criticality = FieldsEnumString(enum_class=tls.ScanState)
    signed_certificate_timestamps = fields.List(
        fields.Nested(SPCertSignedTimestampSchema)
    )


class SPCertExtPrecertPoisonSchema(ProfileSchema):
    """Data class for certificate extension PrecertPoison
    """

    __profile_class__ = SPCertExtension
    name = fields.String()
    oid = fields.String()
    criticality = FieldsEnumString(enum_class=tls.ScanState)


class SPCertExtSignedCertificateTimestampsSchema(ProfileSchema):
    """Data class for certificate extension SignedCertificateTimestamps
    """

    __profile_class__ = SPCertExtension
    name = fields.String()
    oid = fields.String()
    criticality = FieldsEnumString(enum_class=tls.ScanState)
    signed_certificate_timestamps = fields.List(
        fields.Nested(SPCertSignedTimestampSchema)
    )


class SPCertExtDeltaCRLIndicatorSchema(ProfileSchema):
    """Data class for certificate extension DeltaCRLIndicator
    """

    __profile_class__ = SPCertExtension
    name = fields.String()
    oid = fields.String()
    criticality = FieldsEnumString(enum_class=tls.ScanState)


class SPCertExtAuthorityInformationAccessSchema(ProfileSchema):
    """Data class for certificate extension AuthorityInformationAccess
    """

    __profile_class__ = SPCertExtension
    name = fields.String()
    oid = fields.String()
    criticality = FieldsEnumString(enum_class=tls.ScanState)
    authority_info_access = fields.List(fields.Nested(SPCertAccessDescriptionSchema))


class SPCertExtSubjectInformationAccessSchema(ProfileSchema):
    """Data class for certificate extension SubjectInformationAccess
    """

    __profile_class__ = SPCertExtension
    name = fields.String()
    oid = fields.String()
    criticality = FieldsEnumString(enum_class=tls.ScanState)


class SPCertExtFreshestCRLSchema(ProfileSchema):
    """Data class for certificate extension FreshestCRL
    """

    __profile_class__ = SPCertExtension
    name = fields.String()
    oid = fields.String()
    criticality = FieldsEnumString(enum_class=tls.ScanState)


class SPCertExtCRLDistributionPointsSchema(ProfileSchema):
    """Data class for certificate extension CRLDistributionPoints
    """

    __profile_class__ = SPCertExtension
    name = fields.String()
    oid = fields.String()
    criticality = FieldsEnumString(enum_class=tls.ScanState)
    distribution_points = fields.List(fields.Nested(SPDistrPointSchema))


class SPCertExtInhibitAnyPolicySchema(ProfileSchema):
    """Data class for certificate extension InhibitAnyPolicy
    """

    __profile_class__ = SPCertExtension
    name = fields.String()
    oid = fields.String()
    criticality = FieldsEnumString(enum_class=tls.ScanState)


class SPCertExtPolicyConstraintsSchema(ProfileSchema):
    """Data class for certificate extension PolicyConstraints
    """

    __profile_class__ = SPCertExtension
    name = fields.String()
    oid = fields.String()
    criticality = FieldsEnumString(enum_class=tls.ScanState)
    require_explicit_policy = fields.Integer()
    inhibit_policy_mapping = fields.Integer()


class SPCertExtCRLNumberSchema(ProfileSchema):
    """Data class for certificate extension CRLNumber
    """

    __profile_class__ = SPCertExtension
    name = fields.String()
    oid = fields.String()
    criticality = FieldsEnumString(enum_class=tls.ScanState)


class SPCertExtIssuingDistributionPointSchema(ProfileSchema):
    """Data class for certificate extension IssuingDistributionPoint
    """

    __profile_class__ = SPCertExtension
    name = fields.String()
    oid = fields.String()
    criticality = FieldsEnumString(enum_class=tls.ScanState)


class SPCertExtCertificatePoliciesSchema(ProfileSchema):
    """Data class for certificate extension CertificatePolicies
    """

    __profile_class__ = SPCertExtension
    name = fields.String()
    oid = fields.String()
    criticality = FieldsEnumString(enum_class=tls.ScanState)
    cert_policies = fields.List(fields.Nested(SPCertPolicyInfoSchema))


class SPCertExtCertificateIssuerSchema(ProfileSchema):
    """Data class for certificate extension CertificateIssuer
    """

    __profile_class__ = SPCertExtension
    name = fields.String()
    oid = fields.String()
    criticality = FieldsEnumString(enum_class=tls.ScanState)


class SPCertExtCRLReasonSchema(ProfileSchema):
    """Data class for certificate extension CRLReason
    """

    __profile_class__ = SPCertExtension
    name = fields.String()
    oid = fields.String()
    criticality = FieldsEnumString(enum_class=tls.ScanState)


class SPCertExtInvalidityDateSchema(ProfileSchema):
    """Data class for certificate extension InvalidityDate
    """

    __profile_class__ = SPCertExtension
    name = fields.String()
    oid = fields.String()
    criticality = FieldsEnumString(enum_class=tls.ScanState)


class SPCertExtOCSPNonceSchema(ProfileSchema):
    """Data class for certificate extension OCSPNonce
    """

    __profile_class__ = SPCertExtension
    name = fields.String()
    oid = fields.String()
    criticality = FieldsEnumString(enum_class=tls.ScanState)


class SPCertExtensionSchema(OneOfSchema):
    """Choice of certificate extensions
    """

    type_field = "name"
    type_field_remove = False
    type_schemas = {
        "KeyUsage": SPCertExtKeyUsageSchema,
        "UnrecognizedExtension": SPCertExtUnrecognizedExtensionSchema,
        "BasicConstraints": SPCertExtBasicConstraintsSchema,
        "ExtendedKeyUsage": SPCertExtExtendedKeyUsageSchema,
        "OCSPNoCheck": SPCertExtOCSPNoCheckSchema,
        "TLSFeature": SPCertExtTLSFeatureSchema,
        "NameConstraints": SPCertExtNameConstraintsSchema,
        "AuthorityKeyIdentifier": SPCertExtAuthorityKeyIdentifierSchema,
        "SubjectKeyIdentifier": SPCertExtSubjectKeyIdentifierSchema,
        "SubjectAlternativeName": SPCertExtSubjectAlternativeNameSchema,
        "IssuerAlternativeName": SPCertExtIssuerAlternativeNameSchema,
        "PrecertificateSignedCertificateTimestamps": SPCertExtPrecertSignedCertTimestampsSchema,  # noqa: E501
        "PrecertPoison": SPCertExtPrecertPoisonSchema,
        "SignedCertificateTimestamps": SPCertExtSignedCertificateTimestampsSchema,
        "DeltaCRLIndicator": SPCertExtDeltaCRLIndicatorSchema,
        "AuthorityInformationAccess": SPCertExtAuthorityInformationAccessSchema,
        "SubjectInformationAccess": SPCertExtSubjectInformationAccessSchema,
        "FreshestCRL": SPCertExtFreshestCRLSchema,
        "CRLDistributionPoints": SPCertExtCRLDistributionPointsSchema,
        "InhibitAnyPolicy": SPCertExtInhibitAnyPolicySchema,
        "PolicyConstraints": SPCertExtPolicyConstraintsSchema,
        "CRLNumber": SPCertExtCRLNumberSchema,
        "IssuingDistributionPoint": SPCertExtIssuingDistributionPointSchema,
        "CertificatePolicies": SPCertExtCertificatePoliciesSchema,
        "CertificateIssuer": SPCertExtCertificateIssuerSchema,
        "CRLReason": SPCertExtCRLReasonSchema,
        "InvalidityDate": SPCertExtInvalidityDateSchema,
        "OCSPNonce": SPCertExtOCSPNonceSchema,
    }

    # TODO: add type annotations
    def get_obj_type(self, obj):
        return obj.name


class SPCertificate(SPObject):
    """Data class for a certificate.
    """

    def __init__(self, cert: Optional[crt.Certificate] = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        if not cert:
            return

        self.pem = cert.pem.decode()
        self.subject = cert.subject_str
        self.issuer = cert.parsed.issuer.rfc4514_string()
        self.version = cert.parsed.version
        self.serial_number_int = cert.parsed.serial_number
        self.serial_number_bytes = utils.int_to_bytes(cert.parsed.serial_number)
        self.signature = cert.parsed.signature
        self.not_valid_before = cert.parsed.not_valid_before
        self.not_valid_after = cert.parsed.not_valid_after
        diff = cert.parsed.not_valid_after - cert.parsed.not_valid_before
        self.validity_period_days = diff.days
        self.self_signed = tls.ScanState(cert.self_signed)
        if cert.subject_matches is not None:
            self.subject_matches = tls.ScanState(cert.subject_matches)
        self.fingerprint_sha1 = cert.fingerprint_sha1
        self.fingerprint_sha256 = cert.fingerprint_sha256
        self.signature_algorithm = cert.signature_algorithm
        self.public_key = SPPublicKey(pub_key=cert.parsed.public_key())
        self.extensions = [SPCertExtension(ext=ext) for ext in cert.parsed.extensions]
        if cert.crl_status is not None:
            self.crl_revocation_status = cert.crl_status
        if cert.ocsp_status is not None:
            self.ocsp_revocation_status = cert.ocsp_status
        if cert.issues:
            self.issues = cert.issues
        self.ocsp_must_staple = cert.ocsp_must_staple
        self.ocsp_must_staple_multi = cert.ocsp_must_staple_multi
        self.extended_validation = cert.extended_validation
        self.from_trust_store = tls.ScanState(cert.from_trust_store)


class SPCertificateSchema(ProfileSchema):
    """Schema for a certificate.
    """

    __profile_class__ = SPCertificate
    pem = FieldsBlockString()
    subject = fields.String()
    issuer = fields.String()
    version = fields.String()
    serial_number_int = fields.Integer()
    serial_number_bytes = FieldsBytes()
    signature = FieldsBytes()
    not_valid_before = fields.DateTime()
    not_valid_after = fields.DateTime()
    validity_period_days = fields.Integer()
    self_signed = FieldsEnumString(enum_class=tls.ScanState)
    subject_matches = FieldsEnumString(enum_class=tls.ScanState)
    fingerprint_sha1 = FieldsBytes()
    fingerprint_sha256 = FieldsBytes()
    signature_algorithm = FieldsEnumString(enum_class=tls.SignatureScheme)
    public_key = fields.Nested(SPPublicKeySchema)
    crl_revocation_status = FieldsEnumString(enum_class=tls.CertCrlStatus)
    ocsp_revocation_status = FieldsEnumString(enum_class=tls.OcspStatus)
    ocsp_must_staple = FieldsEnumString(enum_class=tls.ScanState)
    ocsp_must_staple_multi = FieldsEnumString(enum_class=tls.ScanState)
    extensions = fields.List(fields.Nested(SPCertExtensionSchema))
    extended_validation = FieldsEnumString(enum_class=tls.ScanState)
    issues = fields.List(fields.String())
    from_trust_store = FieldsEnumString(enum_class=tls.ScanState)


class SPCertChain(SPObject):
    """Data class for a certificate chain.
    """

    def __init__(
        self, chain: Optional["cert_chain.CertChain"] = None, **kwargs: Any
    ) -> None:
        super().__init__(**kwargs)
        if not chain:
            return

        # TODO: resolve type issue
        self.id = chain.id  # type: ignore
        self.successful_validation = tls.ScanState(chain.successful_validation)
        self.cert_chain = [SPCertificate(cert=cert) for cert in chain.certificates]
        if chain.issues:
            self.issues = chain.issues

        self.root_cert_transmitted = tls.ScanState(chain.root_cert_transmitted)
        if chain.root_cert is not None:
            self.root_certificate = SPCertificate(cert=chain.root_cert)


class SPCertChainSchema(ProfileSchema):
    """Schema for a certificate chain.
    """

    __profile_class__ = SPCertChain
    id = fields.Integer()
    successful_validation = FieldsEnumString(enum_class=tls.ScanState)
    cert_chain = fields.List(fields.Nested(SPCertificateSchema))
    issues = fields.List(fields.String())
    root_cert_transmitted = FieldsEnumString(enum_class=tls.ScanState)
    root_certificate = fields.Nested(SPCertificateSchema)


class SPVersionEnumSchema(ProfileEnumSchema):
    """Schema for a TLS version (enum).
    """

    __profile_class__ = tls.Version


class SPSupportedGroupEnumSchema(ProfileEnumSchema):
    """Schema for a supported group (enum).
    """

    __profile_class__ = tls.SupportedGroups


class SPSupportedGroups(SPObject):
    """Data class for supported groups.
    """


class SPSupportedGroupsSchema(ProfileSchema):
    """Data class for supported groups.
    """

    __profile_class__ = SPSupportedGroups
    extension_supported = FieldsEnumString(enum_class=tls.ScanState)
    server_preference = FieldsEnumString(enum_class=tls.ScanState)
    groups_advertised = FieldsEnumString(enum_class=tls.ScanState)
    groups = fields.List(fields.Nested(SPSupportedGroupEnumSchema))


class SPSigAlgoEnumSchema(ProfileEnumSchema):
    """Schema for signature algorithms (enum).
    """

    __profile_class__ = tls.SignatureScheme


class SPSignatureAlgorithms(SPObject):
    """Data class for signature algorithms
    """

    def __init__(self, **kwargs: Any) -> None:
        # TODO: provide type of list
        self.algorithms = []  # type: ignore
        super().__init__(**kwargs)


class SPSignatureAlgorithmsSchema(ProfileSchema):
    """Schema for signature algorithms
    """

    __profile_class__ = SPSignatureAlgorithms
    algorithms = fields.List(fields.Nested(SPSigAlgoEnumSchema))
    info = fields.List(fields.String)


class SPCipherSuiteSchema(ProfileEnumSchema):
    """Schema for a cipher suite (enum).
    """

    __profile_class__ = tls.CipherSuite


class SPRecordProtocolSchema(ProfileEnumSchema):
    """Schema for a record protocol type.
    """

    __profile_class__ = tls.ContentType


class SPCiphers(SPObject):
    """Data class for ciphers
    """


class SPCiphersSchema(ProfileSchema):
    """Schema for ciphers
    """

    __profile_class__ = SPCiphers
    cipher_suites = fields.List(fields.Nested(SPCipherSuiteSchema))
    server_preference = FieldsEnumString(enum_class=tls.ScanState)
    chacha_poly_preference = FieldsEnumString(enum_class=tls.ScanState)


class SPCipherKindSchema(ProfileEnumSchema):
    """Schema for an SSL2 cipher kind (enum).
    """

    __profile_class__ = tls.SSLCipherKind


class SPDhGroup(SPObject):
    """Data class for DH groups
    """


class SPDhGroupSchema(ProfileSchema):
    """Schema for DH groups
    """

    __profile_class__ = SPDhGroup
    name = fields.String()
    size = fields.Integer()
    g_value = fields.Integer()
    p_value = FieldsBytes()


class SPNameResolution(SPObject):
    """Data class for name resolution infos
    """


class SPNameResolutionSchema(ProfileSchema):
    """Schema for name resolution infos
    """

    __profile_class__ = SPNameResolution
    domain_name = fields.String()
    ipv4_addresses = fields.List(fields.String())
    ipv6_addresses = fields.List(fields.String())


class SPServer(SPObject):
    """Data class for the servers' information
    """


class SPServerSchema(ProfileSchema):
    """Schema for the server's information
    """

    __profile_class__ = SPServer
    ip = fields.String()
    name_resolution = fields.Nested(SPNameResolutionSchema)
    port = fields.Integer()
    sni = fields.String()


class SPVersion(SPObject):
    """Data class for a dedicated TLS version.
    """


class SPVersionSchema(ProfileSchema):
    """Schema for a dedicated TLS version.
    """

    __profile_class__ = SPVersion
    cipher_kinds = fields.List(fields.Nested(SPCipherKindSchema))
    ciphers = fields.Nested(SPCiphersSchema)
    dh_group = fields.Nested(SPDhGroupSchema)
    supported_groups = fields.Nested(SPSupportedGroupsSchema)
    signature_algorithms = fields.Nested(SPSignatureAlgorithmsSchema)
    version = fields.Nested(SPVersionEnumSchema)
    support = FieldsEnumString(enum_class=tls.ScanState)


class SPCipherGroup(SPObject):
    """Data class for a cipher group (cipher suite, tls version, record protocol)
    """


class SPCipherGroupSchema(ProfileSchema):
    """Schema for a cipher group (cipher suite, TLS version, record protocol)
    """

    __profile_class__ = SPCipherGroup
    version = fields.Nested(SPVersionEnumSchema)
    cipher_suite = fields.Nested(SPCipherSuiteSchema)
    record_protocol = fields.Nested(SPRecordProtocolSchema)


class SPCbcPaddingOracle(SPObject):
    """Data class for CBC padding oracles
    """


class SPCbcPaddingOracleSchema(ProfileSchema):
    """Schema for CBC padding oracles
    """

    __profile_class__ = SPCbcPaddingOracle
    observable = FieldsEnumString(enum_class=tls.ScanState)
    strong = FieldsEnumString(enum_class=tls.ScanState)
    types = fields.List(FieldsEnumString(enum_class=tls.SPCbcPaddingOracle))
    cipher_group = fields.List(fields.Nested(SPCipherGroupSchema))


class SPCbcPaddingOracleInfo(SPObject):
    """Data class for CBC padding oracle info
    """


class SPCbcPaddingOracleInfoSchema(ProfileSchema):
    """Schema for CBC padding oracle info
    """

    __profile_class__ = SPCbcPaddingOracleInfo
    vulnerable = FieldsEnumString(enum_class=tls.ScanState)
    accuracy = FieldsEnumString(enum_class=tls.OracleScanAccuracy)
    oracles = fields.List(fields.Nested(SPCbcPaddingOracleSchema))


class SPVulnerabilities(SPObject):
    """Data class for vulnerabilities
    """


class SPVulnerabilitiesSchema(ProfileSchema):
    """Schema for vulnerabilities
    """

    __profile_class__ = SPVulnerabilities
    ccs_injection = FieldsEnumString(enum_class=tls.ScanState)
    heartbleed = FieldsEnumString(enum_class=tls.HeartbleedStatus)
    robot = FieldsEnumString(enum_class=tls.RobotVulnerability)
    poodle = FieldsEnumString(enum_class=tls.ScanState)
    tls_poodle = FieldsEnumString(enum_class=tls.ScanState)
    lucky_minus_20 = FieldsEnumString(enum_class=tls.ScanState)
    cbc_padding_oracle = fields.Nested(SPCbcPaddingOracleInfoSchema)
    beast = FieldsEnumString(enum_class=tls.ScanState)
    crime = FieldsEnumString(enum_class=tls.ScanState)
    sweet_32 = FieldsEnumString(enum_class=tls.ScanState)
    freak = FieldsEnumString(enum_class=tls.ScanState)
    logjam = FieldsEnumString(enum_class=tls.Logjam)


class SPMalfunctionIssue(SPObject):
    """Data class for a server issue
    """

    # TODO: replace Any
    def __init__(self, issue: Optional[Any] = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        if not issue:
            return

        self.name = issue.name
        self.description = issue.value


class SPMalfunctionIssueSchema(ProfileSchema):
    """Schema for malfunction issue
    """

    __profile_class__ = SPMalfunctionIssue
    name = fields.String()
    description = fields.String()


class SPMalfunctionMessageSchema(ProfileEnumSchema):
    """Schema for malfunction message
    """

    __profile_class__ = tls.HandshakeType


class SPMalfunctionExtensionSchema(ProfileEnumSchema):
    """Schema for malfunction extension
    """

    __profile_class__ = tls.Extension


class SPServerMalfunction(SPObject):
    """Data class for server malfunction
    """

    # TODO: replace Any
    def __init__(self, malfunction: Optional[Any] = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        if not malfunction:
            return

        self.issue = SPMalfunctionIssue(issue=malfunction.issue)
        if malfunction.message:
            self.message = malfunction.message

        if malfunction.extension:
            self.extension = malfunction.extension


class SPServerMalfunctionSchema(ProfileSchema):
    """Schema for server malfunction
    """

    __profile_class__ = SPServerMalfunction
    issue = fields.Nested(SPMalfunctionIssueSchema)
    message = fields.Nested(SPMalfunctionMessageSchema)
    extension = fields.Nested(SPMalfunctionExtensionSchema)


class ServerProfile(SPObject):
    """Data class for the server profile.

    Attributes:
        cert_chains (list :obj:`SPCertChain`): the list of certificate chains used
            by the server
        features (:obj:`SPFeatures`): the profile structure for the features supported
            by the server
        scan_info (:obj:`SPScanInfo`): object describing basic scan information
        server (:obj:`SPServer`): object describing the server's details
        versions (list of :obj:`SPVersion`): list versions supported by the server
        vulnerabilities (:obj:`SPVulnerabilities`): object containing infos regarding
            the vulnerabilities
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._hash: Dict[int, int] = {}

    def allocate_versions(self) -> None:
        """Ensure that the versions property and cert_chains properties are setup.
        """

        if not hasattr(self, "versions"):
            self.versions: List[SPVersion] = []

        if not hasattr(self, "cert_chains"):
            self.cert_chains: List[SPCertChain] = []

    def allocate_features(self) -> None:
        """Ensure that the features property is setup.
        """

        if not hasattr(self, "features"):
            self.features = SPFeatures()

    def allocate_vulnerabilities(self) -> None:
        """Ensure that the vulnerabilities property is setup.
        """

        if not hasattr(self, "vulnerabilities"):
            self.vulnerabilities = SPVulnerabilities()

    def append_unique_cert_chain(self, chain: "cert_chain.CertChain") -> None:
        """Append a certificate chain to the profile, if not yet present.

        Arguments:
            chain (:obj:`tlsmate.cert.CertChain`): the chain to be added

        Returns:
            int: the index of the chain, which may be created newly, or it might have
            been present already.
        """

        if chain.digest in self._hash:
            return self._hash[chain.digest]  # type: ignore

        idx = len(self._hash) + 1
        self._hash[chain.digest] = idx
        # TODO: resolve type issue
        chain.id = idx  # type: ignore
        self.cert_chains.append(SPCertChain(chain=chain))

    def get_versions(
        self, exclude: Optional[List[tls.Version]] = None
    ) -> List[tls.Version]:
        """Get all TLS versions from the profile.

        Returns:
            list(:obj:`tlsmate.tls.Version`): A list of all supported versions.
        """

        if not hasattr(self, "versions"):
            return []

        if exclude is None:
            exclude = []

        return [
            obj.version  # type: ignore
            for obj in self.versions
            if (
                obj.version not in exclude  # type: ignore
                and obj.support is tls.ScanState.TRUE  # type: ignore
            )
        ]

    def get_version_profile(self, version: tls.Version) -> Optional[SPVersion]:
        """Get the profile entry for a given version.

        Returns:
            :obj:`SPVersion`: the profile entry for the given version or None, if the
            version is not supported by the server.
        """

        for vers_obj in self.versions:
            if (
                vers_obj.version is version  # type: ignore
                and vers_obj.support is tls.ScanState.TRUE  # type: ignore
            ):
                return vers_obj

        return None

    def get_cipher_suites(
        self, version: tls.Version
    ) -> Optional[List[tls.CipherSuite]]:
        """Get all cipher suites for a given TLS version.

        Arguments:
            version (:obj:`tlsmate.tls.Version`): The version for which to get
                the cipher suites for.

        Returns:
            list(:obj:`tlsmate.tls.Ciphersuite`): The list of cipher suites or None,
            if the version is not supported by the server.
        """

        version_prof = self.get_version_profile(version)
        if version_prof is not None:
            if version is tls.Version.SSL20:
                return version_prof.cipher_kinds  # type: ignore

            else:
                return version_prof.ciphers.cipher_suites  # type: ignore

        return None

    def get_supported_groups(
        self, version: tls.Version
    ) -> Optional[List[tls.SupportedGroups]]:
        """Get all supported groups for a given TLS version.

        Arguments:
            version (:class:`tlsmate.tls.Version`): the TLS version to use

        Returns:
            list: a list of all supported groups supported by the server for the given
            TLS version, or None if no supported groups are available.
        """

        version_prof = self.get_version_profile(version)
        try:
            return version_prof.supported_groups.groups  # type: ignore

        except AttributeError:
            return None

    def get_signature_algorithms(
        self, version: tls.Version
    ) -> Optional[List[tls.SignatureScheme]]:
        """Get all signature algorithms for a given TLS version.

        Arguments:
            version (:class:`tlsmate.tls.Version`): the TLS version to use

        Returns:
            list: a list of all signature algorithms supported by the server for the
            given TLS version, or None if no signature algorithms are available.
        """

        version_prof = self.get_version_profile(version)
        if version_prof is not None and hasattr(version_prof, "signature_algorithms"):
            return version_prof.signature_algorithms.algorithms  # type: ignore

        return None

    def get_cert_sig_algos(
        self, key_types: Optional[List[tls.SignatureAlgorithm]] = None
    ) -> List[tls.SignatureScheme]:
        """Get all signature algorithms from the cert chains for the given key_types

        Arguments:
            key_types (list (:obj:`tlsmate.tls.SignatureAlgorithm`): the type of the
                public key required in the host certificate. Can be None to get
                all signature algorithms of all certs of all chains.

        Returns:
            list(:obj:`tlsmate.tls.SignatureScheme`): the list requested
        """
        sig_algos = []
        for chain in self.cert_chains:
            key_type = chain.cert_chain[0].public_key.key_type
            if key_types is None or key_type in key_types:
                for cert in chain.cert_chain:
                    if cert.signature_algorithm not in sig_algos:
                        sig_algos.append(cert.signature_algorithm)

                if hasattr(chain, "root_certificate"):
                    if chain.root_certificate.signature_algorithm not in sig_algos:
                        sig_algos.append(chain.root_certificate.signature_algorithm)

        return sig_algos

    def get_profile_values(
        self, filter_versions: List[tls.Version], full_hs: bool = False
    ) -> structs.ProfileValues:
        """Get a set of some common attributes for the given TLS version(s).

        Arguments:
            filter_versions (list of :class:`tlsmate.tls.Version`): the list of
                TLS versions to retrieve the data for
            full_hs (bool): an indication if only those cipher suites shall be returned
                for which a full handshake is supported. Defaults to False.

        Returns:
            :obj:`tlsmate.structs.ProfileValues`: a structure that provides a list of
            the versions, the cipher suites, the supported groups and the
            signature algorithms
        """

        versions: List[tls.Version] = []
        cipher_suites: List[tls.CipherSuite] = []
        sig_algos: List[tls.SignatureScheme] = []
        groups: List[tls.SupportedGroups] = []
        key_shares: List[tls.SupportedGroups] = []

        # We want to treat higer protocol versions first, so that the result
        # provides the most desirable preference
        for version in sorted(self.get_versions(), reverse=True):
            if version not in filter_versions:
                continue

            # So the versions are restored in order from low to high
            versions.insert(0, version)

            vers_cs = self.get_cipher_suites(version)
            cipher_suites.extend(
                [cs for cs in vers_cs if cs not in cipher_suites]  # type: ignore
            )

            vers_sig = self.get_signature_algorithms(version)
            if vers_sig is not None:
                sig_algos.extend([algo for algo in vers_sig if algo not in sig_algos])

            # Add the signature algorithms used in the certificate chains as well, if
            # not yet present.
            sig_algos.extend(
                [
                    algo
                    for algo in self.get_cert_sig_algos()  # type: ignore
                    if algo not in sig_algos
                ]
            )
            vers_group = self.get_supported_groups(version)
            if vers_group is not None:
                groups.extend([group for group in vers_group if group not in groups])

            if version is tls.Version.TLS13:
                key_shares = vers_group  # type: ignore

        if full_hs:
            cipher_suites = utils.filter_cipher_suites(cipher_suites, full_hs=True)

        return structs.ProfileValues(
            versions=versions,
            cipher_suites=cipher_suites,
            supported_groups=groups,
            signature_algorithms=sig_algos,
            key_shares=key_shares,
        )

    def make_serializable(self) -> Dict[str, Any]:
        """Convert the object into seralizable types

        Returns:
            dict: the serializable data provided as a dict.
        """

        return ServerProfileSchema().dump(self)

    def load(self, data: Any) -> None:
        ServerProfileSchema(profile=self).load(data)


class ServerProfileSchema(ProfileSchema):
    """Base schema for the server profile.
    """

    __profile_class__ = ServerProfile
    cert_chains = fields.List(fields.Nested(SPCertChainSchema))
    features = fields.Nested(SPFeaturesSchema)
    scan_info = fields.Nested(SPScanInfoSchema)
    server = fields.Nested(SPServerSchema)
    server_malfunctions = fields.List(fields.Nested(SPServerMalfunctionSchema))
    versions = fields.List(fields.Nested(SPVersionSchema))
    vulnerabilities = fields.Nested(SPVulnerabilitiesSchema)

    def __init__(self, profile: Optional[ServerProfile] = None, **kwargs: Any) -> None:
        self._profile = profile
        super().__init__(**kwargs)

    @post_load
    def deserialize(self, data: Any, **kwargs: Any) -> None:
        super().deserialize(data, reuse_object=self._profile, **kwargs)
