import re
from dataclasses import dataclass
import datetime

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.x509 import ExtensionOID
from dataclass_dict_convert import dump_rfc3339, dataclass_dict_convert
from imecilabt_utils import URN, datetime_now
from stringcase import camelcase

from imecilabt.gpulab.util import gpulab_logging

logger = gpulab_logging.getLogger("cert_processor")


@dataclass_dict_convert(dict_letter_case=camelcase)
@dataclass(frozen=True)
class CertInfo:
    subject_user_urn: str
    subject_username: str
    not_valid_after: datetime.datetime
    not_valid_before: datetime.datetime


def process_cert(certfile: str) -> CertInfo:
    with open(certfile, 'r') as f:
        cert_content = f.read()  # encode because load_pem_x509_certificate needs bytes
    try:
        cert_begin_delim = '-----BEGIN CERTIFICATE-----'
        cert_end_delim = '-----END CERTIFICATE-----'
        cert_content = re.findall(r"{begin}.*?{end}".format(begin=cert_begin_delim, end=cert_end_delim),
                                   cert_content, re.DOTALL)[0]

        cert = x509.load_pem_x509_certificate(cert_content.encode('utf-8'), default_backend())
    except ValueError:
        logger.exception(f'Problem parsing PEM: {cert_content!r}')
        raise
    try:
        ext = cert.extensions.get_extension_for_oid(ExtensionOID.SUBJECT_ALTERNATIVE_NAME)
        urns = ext.value.get_values_for_type(x509.UniformResourceIdentifier)
    except ValueError:
        logger.exception(f'Problem processing certificate: {cert_content!r}')
        raise
    user_urn = str(urns[0])
    username = URN(urn=user_urn).name
    return CertInfo(
        subject_user_urn=user_urn,
        subject_username=username,
        not_valid_after=cert.not_valid_after.astimezone(datetime.timezone.utc),
        not_valid_before=cert.not_valid_before.astimezone(datetime.timezone.utc),
    )
