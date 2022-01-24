import base64
import binascii
import warnings
from ssl import get_server_certificate, PEM_cert_to_DER_cert
from typing import Generator

import spnego
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.exceptions import UnsupportedAlgorithm
from httpx import Auth, Request, Response


class UnknownSignatureAlgorithmOID(Warning):
    pass


class HttpNtlmAuth(Auth):
    """ HTTP NTLM Authentication Handler for HTTPX. """

    def __init__(self, username, password, send_cbt=True):
        """Create an authentication handler for NTLM over HTTP.
        :param str username: Username in 'domain\\username' format
        :param str password: Password
        :param bool send_cbt: Will send the channel bindings over a HTTPS channel (Default: True)
        """
        self.username = username
        self.password = password
        self.send_cbt = send_cbt

    def auth_flow(self, request: Request) -> Generator[Request, Response, None]:

        def auth_from_header(header):
            """
            Given a WWW-Authenticate or Proxy-Authenticate header, returns the
            authentication type to use. We prefer NTLM over Negotiate if the server
            supports it.
            """
            header = header.lower() or ""
            if "ntlm" in header:
                return "NTLM"
            elif "negotiate" in header:
                return "Negotiate"
            return None

        request.headers["Connection"] = "Keep-Alive"
        response = yield request
        if response.status_code in (401, 407):
            yield from self._retry_using_ntlm(request, response)

    def _retry_using_ntlm(self, request: Request, response):

        def auth_from_header(header):
            """
            Given a WWW-Authenticate or Proxy-Authenticate header, returns the
            authentication type to use. We prefer NTLM over Negotiate if the server
            suppports it.
            """
            header = header.lower() or ""
            if "ntlm" in header:
                return "NTLM"
            elif "negotiate" in header:
                return "Negotiate"
            return None

        if response.status_code == 401:
            resp_header = "www-authenticate"
            req_header = "Authorization"
        elif response.status_code == 407:
            resp_header = "proxy-authenticate"
            req_header = "Proxy-authorization"
        auth_type = auth_from_header(response.headers.get(resp_header))
        if not auth_type:
            return
        # Get the certificate of the server if using HTTPS for CBT
        server_certificate_hash = self._get_server_cert(response)
        """Attempt to authenticate using HTTP NTLM challenge/response."""
        if req_header in request.headers:
            return
        # content_length = int(request.headers.get("Content-Length") or "0", base=10)
        # if hasattr(request.body, "seek"):
        #     if content_length > 0:
        #         request.body.seek(-content_length, 1)
        #     else:
        #         request.body.seek(0, 0)
        # request = request.copy()
        # ntlm returns the headers as a base64 encoded bytestring. Convert to
        # a string.
        client = spnego.client(self.username, self.password, protocol="ntlm")
        # Perform the first step of the NTLM authentication
        negotiate_message = base64.b64encode(client.step()).decode("ascii")

        request.headers[req_header] = f"{auth_type} {negotiate_message}"
        # A streaming response breaks authentication.
        # This can be fixed by not streaming this request, which is safe
        # because the returned response3 will still have stream=True set if
        # specified in args. In addition, we expect this request to give us a
        # challenge and not the real content, so the content will be short anyway.
        response2 = yield request

        # this is important for some web applications that store
        # authentication-related info in cookies (it took a long time to figure out)
        if response2.headers.get("set-cookie"):
            request.headers["Cookie"] = response2.headers.get("set-cookie")

        # get the challenge
        auth_header_value = response2.headers[resp_header]

        auth_strip = auth_type + " "

        ntlm_header_value = next(
            s
            for s in (val.lstrip() for val in auth_header_value.split(","))
            if s.startswith(auth_strip)
        ).strip()

        # Parse the challenge in the ntlm context
        # Parse the challenge in the ntlm context and perform
        # the second step of authentication
        val = base64.b64decode(ntlm_header_value[len(auth_strip):].encode())
        authenticate_message = base64.b64encode(client.step(val)).decode("ascii")

        auth = f"{auth_type} {authenticate_message}"
        request.headers[req_header] = auth
        yield request

    def _get_server_cert(self, response: Response):
        """
        Get the certificate at the request_url and return it as a hash. The
        certificate hash is then used with NTLMv2 authentication for Channel Binding
        Tokens support.
        :param response: The original 401 response from the server
        :return: The hash of the DER encoded certificate at the request_url or None if
        not an HTTPS endpoint
        """
        if self.send_cbt and response.url.scheme == "https":
            if response.url.port is None:
                port = "443"
            else:
                port = response.url.port
            cert = get_server_certificate((response.url.host, port))
            der_cert = PEM_cert_to_DER_cert(cert)
            certificate_hash = _get_certificate_hash(der_cert)
            return certificate_hash
        else:
            return None


def _get_certificate_hash(certificate_der):
    # https://tools.ietf.org/html/rfc5929#section-4.1
    cert = x509.load_der_x509_certificate(certificate_der, default_backend())

    try:
        hash_algorithm = cert.signature_hash_algorithm
    except UnsupportedAlgorithm as ex:
        warnings.warn(
            "Failed to get signature algorithm from certificate, "
            "unable to pass channel bindings: %s" % str(ex),
            UnknownSignatureAlgorithmOID,
        )
        return None

    # if the cert signature algorithm is either md5 or sha1 then use sha256
    # otherwise use the signature algorithm
    if hash_algorithm.name in ["md5", "sha1"]:
        digest = hashes.Hash(hashes.SHA256(), default_backend())
    else:
        digest = hashes.Hash(hash_algorithm, default_backend())

    digest.update(certificate_der)
    certificate_hash_bytes = digest.finalize()
    certificate_hash = binascii.hexlify(certificate_hash_bytes).decode().upper()

    return certificate_hash
