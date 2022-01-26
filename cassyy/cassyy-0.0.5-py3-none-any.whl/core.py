"""
Central Authentication Service (CAS) client
"""
import dataclasses
import logging
import urllib.parse
import urllib.request
import xml.etree.ElementTree
from typing import Dict, Optional, Union

logger = logging.getLogger(__name__)


def _fetch_url(url: str, timeout: float = 10.0) -> bytes:
    with urllib.request.urlopen(url, timeout=timeout) as f:
        return f.read()


class CASError(Exception):
    def __init__(self, error_code: str, *args) -> None:
        super().__init__(error_code, *args)
        self.error_code = error_code


class CASInvalidServiceError(CASError):
    def __init__(self, error_code: str, *args) -> None:
        super().__init__(error_code, *args)


class CASInvalidTicketError(CASError):
    def __init__(self, error_code: str, *args) -> None:
        super().__init__(error_code, *args)


@dataclasses.dataclass
class CASUser:
    userid: str
    attributes: Dict[str, str] = dataclasses.field(default_factory=dict)

    def asdict(self) -> Dict[str, Union[str, Dict[str, str]]]:
        return dataclasses.asdict(self)


class CASClient:
    CAS_NS = {'cas': 'http://www.yale.edu/tp/cas'}
    CAS_VALIDATE_ENCODING = 'utf-8'
    CAS_VALIDATE_TIMEOUT = 10.0

    def __init__(
            self,
            login_url: str,
            logout_url: str,
            validate_url: str,
    ) -> None:
        self.login_url = login_url
        self.logout_url = logout_url
        self.validate_url = validate_url

    @classmethod
    def from_base_url(
            cls,
            base_url: str,
            *,
            login_path: str = '/login',
            logout_path: str = '/logout',
            validate_path: str = '/p3/serviceValidate',
    ) -> 'CASClient':
        return cls(
            login_url=urllib.parse.urljoin(base_url, login_path),
            logout_url=urllib.parse.urljoin(base_url, logout_path),
            validate_url=urllib.parse.urljoin(base_url, validate_path),
        )

    def validate(
            self,
            service_url: str,
            ticket: str,
            *,
            timeout: Optional[float] = None,
            **kwargs
    ) -> CASUser:
        if timeout is None:
            timeout = self.CAS_VALIDATE_TIMEOUT
        target_validate = self.build_validate_url(service_url, ticket, **kwargs)
        logger.debug('Validating %s', target_validate)
        try:
            resp_data = _fetch_url(target_validate, timeout=timeout)
            resp_text = resp_data.decode(self.CAS_VALIDATE_ENCODING)
        except Exception as exc:
            raise CASError(repr(exc))
        else:
            logger.debug('Response:\n%s', resp_text)
            return self.parse_cas_response(resp_text)

    def build_login_url(
            self,
            service: str,
            *,
            callback_post: bool = False,
            **kwargs,
    ) -> str:
        params = {'service': service, **kwargs}
        if callback_post:
            params['method'] = 'POST'
        qs = urllib.parse.urlencode(params)
        return f'{self.login_url}?{qs}'

    def build_logout_url(self, service: Optional[str] = None, **kwargs) -> str:
        if service is None:
            if not kwargs:
                return self.logout_url
            params = kwargs
        else:
            params = {'service': service, **kwargs}
        qs = urllib.parse.urlencode(params)
        return f'{self.logout_url}?{qs}'

    def build_validate_url(self, service: str, ticket: str, **kwargs) -> str:
        params = {'service': service, 'ticket': ticket, **kwargs}
        qs = urllib.parse.urlencode(params)
        return f'{self.validate_url}?{qs}'

    def parse_cas_response(self, cas_response: str) -> CASUser:
        try:
            root = xml.etree.ElementTree.fromstring(cas_response)
        except Exception as exc:
            raise CASError('INVALID_RESPONSE', repr(exc)) from exc
        else:
            return self.parse_cas_xml(root)

    def parse_cas_xml(self, root: xml.etree.ElementTree.Element) -> CASUser:
        user_elem = root.find('cas:authenticationSuccess/cas:user',
                              self.CAS_NS)
        if user_elem is not None:
            attr_elem = root.find('cas:authenticationSuccess/cas:attributes',
                                  self.CAS_NS)
            return self.parse_cas_xml_user(user_elem, attr_elem)
        self.parse_cas_xml_error(root)

    def parse_cas_xml_user(
            self,
            user_elem: xml.etree.ElementTree.Element,
            attr_elem: Optional[xml.etree.ElementTree.Element],
    ) -> CASUser:
        cas_user = CASUser(userid=user_elem.text)
        if attr_elem is not None:
            tag_ns = '{' + self.CAS_NS['cas'] + '}'
            for e in attr_elem:
                attr_name = e.tag.replace(tag_ns, '', 1)
                cas_user.attributes[attr_name] = e.text
        return cas_user

    def parse_cas_xml_error(
            self,
            root: xml.etree.ElementTree.Element,
    ) -> None:
        error_code = 'Unknown'
        error_elem = root.find('cas:authenticationFailure', self.CAS_NS)
        if error_elem is not None:
            error_code = error_elem.attrib.get('code', error_code)
            error_text = error_elem.text
            if error_code == 'INVALID_TICKET':
                raise CASInvalidTicketError(error_code, error_text)
            elif error_code == 'INVALID_SERVICE':
                raise CASInvalidServiceError(error_code, error_text)
        raise CASError(error_code)

    def __repr__(self) -> str:
        return (
            'CASClient('
            f'login_url={self.login_url!r}, '
            f'logout_url={self.logout_url!r}, '
            f'validate_url={self.validate_url!r}'
            ')'
        )
