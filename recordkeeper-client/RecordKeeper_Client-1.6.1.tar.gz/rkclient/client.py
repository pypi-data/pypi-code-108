import time
import logging
import datetime
from uuid import UUID, uuid1
from typing import Dict, Any, Optional, Tuple, Callable
from importlib.metadata import version
import urllib.request
import urllib.response
import urllib.parse
from urllib.error import URLError, HTTPError
import ssl

from rkclient.auth import RK_USER_AUTH_HEADER
from rkclient.entities import PEM, Artifact
from rkclient.serialization import PEMSerialization, _encode_as_base64

log = logging.getLogger("rkclient")
RK_VERSION = version('RecordKeeper_Client')


def add_pem_context(files: Dict[str, Any], pem: PEM):
    """
    Helper function to be used when adding RK context to request
    :param files: a dictionary which belongs to Python Requests object
    :return:
    """
    files['rk_context'] = pem.ID.hex


def get_pem_from_request(request) -> Optional[UUID]:
    """
    Helper function to be used when retrieving RK context
    :param request: Flask-request object
    :return:
    """
    rk_context = request.files.get('rk_context', None)
    if rk_context is None:
        return None
    pem_id: str = rk_context.stream.read().decode("UTF8")
    return UUID(hex=pem_id)


class RKClient:
    """
        All network functions return tuple [str, bool]
        If bool is False, str contains error description

        Errors are also logged to rkclient logger
    """

    def __init__(self, receiver_url: str,
                 emitter_id: Optional[UUID] = None,
                 timeout_sec: int = 5,
                 insecure: bool = True,
                 user_auth: str = ''):
        """

        :param receiver_url:
        :param emitter_id:
        :param timeout_sec:
        :param insecure: set it to True when operating with server that has test SSL certificates
        """
        self.receiver_url = receiver_url.rstrip('/')
        if emitter_id is None:
            emitter_id = uuid1()
        self.emitter_id = emitter_id
        self.timeout_sec = timeout_sec
        self.user_auth = user_auth
        log.info(f"ver {RK_VERSION}, connecting to: {self.receiver_url}")
        if self.user_auth:
            log.info(f"Authorizing with {RK_USER_AUTH_HEADER} header")
        self.insecure = insecure
        if self.insecure:
            log.warning("Disabled SSL certificate check")
        if "https://" not in self.receiver_url and "http://receiver:8083" not in self.receiver_url and \
                "localhost" not in self.receiver_url and "127.0.0.1" not in self.receiver_url:
            log.warning("If you're connecting to https server without specifying https in url, expect 405 errors")

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass

    @staticmethod
    def get_version() -> str:
        """
        :return: Version of RKClient
        """
        return RK_VERSION

    def prepare_pem(self,
                    pem_type: str,
                    predecessor_id: Optional[UUID] = None,
                    properties: Optional[Dict] = None,
                    tag_name: str = 'latest',
                    tag_namespace: Optional[UUID] = None) -> PEM:
        """
        In memory creation of PEM
        :param pem_type: user defined type of event
        :param predecessor_id: pass None if this event doesn't have a predecessor
        :param properties:
        :param tag_name:
        :param tag_namespace:
        :return: new PEM
        """
        uid = uuid1()
        now = datetime.datetime.utcfromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
        pem = PEM(uid, pem_type, predecessor_id, self.emitter_id, now)
        if properties is not None:
            pem.Properties = properties
        pem.Tag = tag_name
        if tag_namespace is None:
            pem.TagNamespace = self.emitter_id.hex
        else:
            pem.TagNamespace = tag_namespace.hex
        return pem

    def prepare_artifact(self,
                         artifact_type: str,
                         properties: Dict[str, str],
                         uid: Optional[UUID] = None) -> Artifact:
        """
        In memory creation of Artifact. It needs to be passed to PEM.add_uses/produces_artifact()
        :param artifact_type:
        :param properties:
        :param uid:
        :return: new Artifact
        """
        if uid is None:
            uid = uuid1()
        art = Artifact(uid, artifact_type, properties)
        return art

    def send_pem(self, pem: PEM) -> Tuple[str, bool]:
        """
        Sends PEM to Record Keeper.
        :return: check class description
        """
        def _send_pem():
            payload: str = PEMSerialization.to_json(pem)
            log.debug(f"sending PEM: {payload}")
            return self._post("/pem", payload)

        return _handle_request(_send_pem, "Sending PEM")

    def ping(self) -> Tuple[str, bool]:
        """
        :return: check class description
        """
        def _ping():
            return self._get("/ping")

        return _handle_request(_ping, "Pinging")

    def get_info(self) -> Tuple[str, bool]:
        """
        Returns json with 'postgres_enabled' and 'neo4j_enabled' bools, and 'version' with string semver
        :return: check class description
        TODO: return object instead of str
        """
        def _get_info():
            return self._get("/info", )

        return _handle_request(_get_info, "Getting info", True)

    def get_tag(self, namespace: UUID, tag_name: str) -> Tuple[str, bool]:
        """
        Returned tag is UUID in hex (do: UUID(hex=result))
        :return: check class description
        """
        def _get_tag():
            tag_base64 = _encode_as_base64(tag_name)
            return self._get(f"/tag/{namespace.hex}/{tag_base64}")

        return _handle_request(_get_tag, "Getting tag", True)

    def set_tag(self, namespace: UUID, tag_name: str, pem: PEM) -> Tuple[str, bool]:
        """
        Sets tag_name on pem.ID, within namespace
        :param tag_name: can contain space, / and other characters, but recommended charset: is A-Za-z0-9_-
        :param namespace:
        :param pem:
        :return: check class description
        """
        def _set_tag():
            tag_base64 = _encode_as_base64(tag_name)
            return self._post(f"/tag/{namespace.hex}/{tag_base64}/{pem.ID.hex}", tag_base64)

        return _handle_request(_set_tag, "Setting tag")

    def _get(self, url_postfix: str, query_params: Optional[Dict[str, Any]] = None) -> Tuple[str, bool]:
        url = self.receiver_url + url_postfix + self._encode_query_params(query_params)
        req = urllib.request.Request(url=url)
        if self.user_auth:
            req.add_header(RK_USER_AUTH_HEADER, self.user_auth)
        return self._make_request(req)

    def _post(self, url_postfix: str, payload: str, query_params: Optional[Dict[str, Any]] = None) -> Tuple[str, bool]:
        url = self.receiver_url + url_postfix + self._encode_query_params(query_params)
        req = urllib.request.Request(url=url, data=payload.encode())
        req.add_header('Content-Type', 'application/json')
        if self.user_auth:
            req.add_header(RK_USER_AUTH_HEADER, self.user_auth)
        return self._make_request(req)

    def _make_request(self, request):
        try:
            resp = urllib.request.urlopen(request, timeout=self.timeout_sec, context=self._get_ssl_context())
        except HTTPError as e:
            return f"error: {e} {e.read().decode()}", False
        except URLError as e:
            return f"connection error: {e}", False
        else:
            return resp.read().decode(), True

    def _get_ssl_context(self) -> ssl.SSLContext:
        ctx = ssl.create_default_context()
        if self.insecure:
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
        return ctx

    def _encode_query_params(self, query_params: Optional[Dict[str, Any]]) -> str:
        if query_params is None or len(query_params) == 0:
            return ''
        encoded_params = urllib.parse.urlencode(query_params)
        return '?' + encoded_params


def _handle_request(func: Callable, name: str, ret_text_on_ok: bool = False) -> Tuple[str, bool]:
    """
    Wraps the error, logging and exception handling.
    """
    text, ok = func()
    if not ok:
        msg = f"{name} failed: {text}"
        log.error(msg)
        return msg, False
    if ret_text_on_ok:
        return text, True
    else:
        return 'OK', True
