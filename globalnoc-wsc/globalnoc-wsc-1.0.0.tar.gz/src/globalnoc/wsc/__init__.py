import http.cookiejar
import logging

import requests
from lxml import etree as ET

namespaces = {
    'S': 'http://schemas.xmlsoap.org/soap/envelope/',
    'paos': 'urn:liberty:paos:2003-08',
    'ecp': 'urn:oasis:names:tc:SAML:2.0:profiles:SSO:ecp',
    'saml': 'urn:oasis:names:tc:SAML:2.0:assertion',
    'saml2p': 'urn:oasis:names:tc:SAML:2.0:protocol',
    'ds': 'http://www.w3.org/2000/09/xmldsig#',
}
# for ns in namespaces.keys():
#    ET.register_namespace(ns, namespaces[ns])


class NoNameService(Exception):
    pass


class NoURL(Exception):
    pass


class UndefinedURN(Exception):
    pass


class InvalidURN(Exception):
    pass


class RemoteMethodException(Exception):
    pass


class LoginFailure(Exception):
    pass


class ECP(requests.auth.AuthBase):
    def __init__(self, username, password, realm, debug=False):
        self.debug = debug
        self.username = username
        self.password = password
        self.realm = realm

    def handle_ecp(self, r, **kwargs):
        if r.headers.get('content-type', None) == 'application/vnd.paos+xml':
            logging.debug("Got PAOS Header. Redirecting through ECP login.")
            e = ET.fromstring(r.content)
            r.close()

            session = requests.Session()
            # XXX
            # Extract the relay state to use later
            (relaystate,) = ET.XPath(
                'S:Header/ecp:RelayState', namespaces=namespaces)(e)
            # Extract the response consumer URL to compare later
            responseconsumer = ET.XPath(
                'S:Header/paos:Request', namespaces=namespaces)(e)[0].get('responseConsumerURL')
            logging.debug("SP expects the response at: %s", responseconsumer)
            # Clean up the SP login request
            e.remove(ET.XPath('S:Header', namespaces=namespaces)(e)[0])

            # Log into the IdP  with the SP request
            logging.debug(
                "Logging into the IdP via %s as %s",
                self.realm, self.username
            )
            login_r = session.post(
                self.realm,
                auth=(self.username, self.password),
                data=ET.tostring(e),
                headers={'content-type': 'text/xml'}
            )
            if login_r.status_code != requests.codes.ok:
                raise RemoteMethodException(
                    "Received status code {0} from IdP".format(login_r.status_code))
            ee = ET.fromstring(login_r.content)

            # Make sure we got back the same response consumer URL and assertion consumer service URL
            idpACS = ET.XPath(
                'S:Header/ecp:Response', namespaces=namespaces)(ee)[0].get('AssertionConsumerServiceURL')
            logging.debug("IdP said to send the response to %s", idpACS)

            if responseconsumer != idpACS:
                raise LoginFailure("SP and IdP ACS mismatch")

            # Make sure we got a successful login
            if ET.XPath('S:Body/saml2p:Response/saml2p:Status/saml2p:StatusCode', namespaces=namespaces)(ee)[0].get('Value') != 'urn:oasis:names:tc:SAML:2.0:status:Success':
                raise LoginFailure("Login to IdP unsuccessful")

            logging.debug("IdP accepted login.")
            # Clean up login token
            (h,) = ET.XPath('S:Header', namespaces=namespaces)(ee)
            for el in h:
                h.remove(el)
            h.append(relaystate)

            # Pass login token to SP
            logging.debug("Sending login token to SP.")
            return_r = session.post(responseconsumer,
                                    data=ET.tostring(ee),
                                    headers={
                                        'Content-Type': 'application/vnd.paos+xml'},
                                    allow_redirects=False)
            if return_r.status_code not in [requests.codes.ok, requests.codes.found]:
                raise RemoteMethodException(
                    "Received status code {0} from SP".format(return_r.status_code))

            # Prepare the original request with the new login cookies
            prep = r.request.copy()
            if not hasattr(prep, '_cookies'):
                prep._cookies = requests.cookies.RequestsCookieJar()
            requests.cookies.extract_cookies_to_jar(
                prep._cookies, r.request, r.raw)
            prep._cookies.update(session.cookies)

            prep.prepare_cookies(prep._cookies)

            # Re-launch the original request
            logging.debug("Re-launching original request after logging in.")
            _r = r.connection.send(prep, **kwargs)

            # Add the login flow to the request history
            _r.history.append(r)
            _r.history.append(login_r)
            _r.history.append(return_r)

            _r.request = prep

            return _r
        logging.debug(
            "No PAOS header. Assuming already logged in, or no Shib required.")
        return r

    def __call__(self, r):
        # Update or add Accept header to indicate we want to do ECP
        if 'Accept' in r.headers:
            r.headers['Accept'] += ', application/vnd.paos+xml'
        else:
            r.headers['Accept'] = '*/*, application/vnd.paos+xml'
        # Signal that we support ECP
        r.headers['PAOS'] = 'ver="urn:liberty:paos:2003-08";"urn:oasis:names:tc:SAML:2.0:profiles:SSO:ecp"'
        r.register_hook('response', self.handle_ecp)
        return r

    def __eq__(self, other):
        return all([self.username == getattr(other, 'username', None),
                    self.password == getattr(other, 'password', None),
                    self.realm == getattr(other, 'realm', None)])

    def __ne__(self, other):
        return not self == other


class WSC(object):
    _debug = None
    _url = None
    _username = None
    _password = None
    _urn = None
    _ns = None
    _ns_etree = None
    _realm = None
    _raw = False
    _strict_content_type = True
    _session = None
    _timeout = None

    def __init__(self, ns='/etc/grnoc/name-service-cacher/name-service.xml', debug=False):
        logging.debug("Initialized WSC object")
        self._debug = debug
        self.ns = ns
        self.session = requests.Session()
        self.timeout = 60

    @property
    def ns(self):
        return self._ns

    @ns.setter
    def ns(self, ns):
        logging.debug("Setting NS cache: %s", ns)
        self._ns = ns

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, url):
        logging.debug("Setting URL: %s", url)
        self._url = url

    @property
    def username(self):
        return self._username

    @username.setter
    def username(self, username):
        logging.debug("Setting Username: %s", username)
        self._username = username

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, password):
        logging.debug("Setting Password")
        self._password = password

    @property
    def realm(self):
        return self._realm

    @realm.setter
    def realm(self, realm):
        logging.debug("Setting Realm: %s", realm)
        self._realm = realm

    @property
    def raw(self):
        return self._raw

    @realm.setter
    def raw(self, raw):
        logging.debug("Setting Raw: %s", raw)
        self._raw = raw

    @property
    def strict_content_type(self):
        return self._strict_content_type

    @realm.setter
    def strict_content_type(self, strict_content_type):
        logging.debug("Setting Strict Content Type: %s", strict_content_type)
        self._strict_content_type = strict_content_type

    @property
    def session(self):
        return self._session

    @session.setter
    def session(self, session):
        logging.debug("Setting Session: %s", session)
        self._session = session

    @property
    def timeout(self):
        return self._timeout

    @timeout.setter
    def timeout(self, timeout):
        logging.debug("Setting Timeout: %s", timeout)
        self._timeout = timeout

    @property
    def urn(self):
        return self._urn

    @urn.setter
    def urn(self, urn):
        self._ns_etree = ET.parse(self.ns)
        if not self._ns:
            raise NoNameService()
        if not urn.startswith('urn:publicid:IDN+grnoc.iu.edu:'):
            raise InvalidURN()
        (_, _, _, urn_cloud, urn_class, urn_version, urn_service) = urn.split(':')
        ns_cloud = [c for c in self._ns_etree.findall(
            "./cloud") if c.attrib.get('id') == urn_cloud]
        if len(ns_cloud) != 1:
            raise UndefinedURN("Looking for {0} found {1} matching clouds".format(
                urn_cloud, len(ns_cloud)))
        ns_cloud = ns_cloud[0]

        ns_class = [c for c in ns_cloud.findall(
            './class') if c.attrib.get('id') == urn_class]
        if len(ns_class) != 1:
            raise UndefinedURN("Looking for {0}:{1} found {2} matching classes".format(
                urn_cloud, urn_class, len(ns_class)))
        ns_class = ns_class[0]

        ns_version = [c for c in ns_class.findall(
            './version') if c.attrib.get('value') == urn_version]
        if len(ns_version) != 1:
            raise UndefinedURN("Looking for {0}:{1}:{2} found {3} matching versions".format(
                urn_cloud, urn_class, urn_version, len(ns_version)))
        ns_version = ns_version[0]

        ns_service = [c for c in ns_version.findall(
            './service') if c.attrib.get('id') == urn_service]
        if len(ns_service) != 1:
            raise UndefinedURN("Looking for {0}:{1}:{2}:{3} found {4} matching services".format(
                urn_cloud, urn_class, urn_version, urn_service, len(ns_service)))
        ns_service = ns_service[0]

        ns_locations = [c for c in ns_service.findall('./location')]
        if len(ns_locations) < 1:
            raise UndefinedURN("Looking for {0}:{1}:{2}:{3} found no matching locations".format(
                urn_cloud, urn_class, urn_version, urn_service))
        ns_locations.sort(key=lambda loc: loc.attrib.get('weight'))
        logging.debug("Setting and resolving URN: %s", urn)
        self.url = ns_locations[0].attrib.get('url')

        self._urn = urn

    def _remoteHandler(self, name):
        def handler(*args, **kwargs):
            if not self.url:
                raise NoURL()
            data = {'method': name}
            data.update(kwargs)
            if not self.realm:
                logging.debug(
                    "Realm not set. Launching as HTTP Basic without a fixed realm.")
                r = self.session.post(self.url, auth=(
                    self.username, self.password), data=data, timeout=self.timeout)
            elif "https://" in self.realm:
                logging.debug(
                    "Realm set and looks like Shibboleth ECP. Launching with ECP")
                r = self.session.post(self.url, auth=ECP(
                    self.username, self.password, self.realm, debug=self._debug), data=data, timeout=self.timeout)
            else:
                raise LoginFailure("Realm is not an IdP ECP Endpoint")
            if r.status_code != requests.codes.ok:
                raise RemoteMethodException(
                    "Received status code {0}".format(r.status_code))
            if self._raw:
                return r.content
            if self._strict_content_type and not '/json' in r.headers.get('content-type'):
                raise RemoteMethodException(
                    "Unknown content type {0}".format(r.headers.get('content-type')))
            try:
                return r.json()
            except:
                raise RemoteMethodException("JSON parse error")
        return handler

    def __getattr__(self, name):
        return self._remoteHandler(name)

    def _save(self, filename):
        jar = http.cookiejar.LWPCookieJar(filename)
        for cookie in self.session.cookies:
            jar.set_cookie(cookie)
        jar.save(ignore_discard=True)

    def _load(self, filename):
        jar = http.cookiejar.LWPCookieJar(filename)
        jar.load(ignore_discard=True)
        for cookie in jar:
            self.session.cookies.set_cookie(cookie)
