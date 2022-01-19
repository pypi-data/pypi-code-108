import hashlib
import time
import os

from aiohttp import client_exceptions, hdrs
from yarl import URL


class DigestAuth:
    """HTTP digest authentication helper.
    The work here is based off of
    https://github.com/requests/requests/blob/v2.18.4/requests/auth.py.
    """

    def __init__(self, username, password, session, previous=None):
        if previous is None:
            previous = {}

        self.username = username
        self.password = password
        self.last_nonce = previous.get('last_nonce', '')
        self.nonce_count = previous.get('nonce_count', 0)
        self.challenge = previous.get('challenge')
        self.args = {}
        self.digest_auth_tried = False
        self.session = session

    async def request(self, method, url, *, headers=None, **kwargs):
        if headers is None:
            headers = {}

        # Save the args so we can re-run the request
        self.args = {
            'method': method,
            'url': url,
            'headers': headers,
            'kwargs': kwargs
        }

        if self.challenge:
            headers[hdrs.AUTHORIZATION] = self._build_digest_header(
                method.upper(), url
            )

        response = await self.session.request(
            method, url, headers=headers, **kwargs
        )

        # Only try performing digest authentication if the response status is
        # from 400 to 500.
        if 400 <= response.status < 500 and self.digest_auth_tried is False:
            self.digest_auth_tried = True
            return await self._handle_401(response)

        return response

    def _build_digest_header(self, method, url):
        """
        :rtype: str
        """

        realm = self.challenge['realm']
        nonce = self.challenge['nonce']
        qop = self.challenge.get('qop')
        algorithm = self.challenge.get('algorithm', 'MD5').upper()
        opaque = self.challenge.get('opaque')

        if qop and not (qop == 'auth' or 'auth' in qop.split(',')):
            raise client_exceptions.ClientError(
                'Unsupported qop value: %s' % qop
            )

        # lambdas assume digest modules are imported at the top level
        if algorithm == 'MD5' or algorithm == 'MD5-SESS':
            hash_fn = hashlib.md5
        elif algorithm == 'SHA':
            hash_fn = hashlib.sha1
        else:
            return ''

        def H(x):
            return hash_fn(x.encode()).hexdigest()

        def KD(s, d):
            return H('%s:%s' % (s, d))

        path = URL(url).path_qs
        A1 = '%s:%s:%s' % (self.username, realm, self.password)
        A2 = '%s:%s' % (method, path)

        HA1 = H(A1)
        HA2 = H(A2)

        if nonce == self.last_nonce:
            self.nonce_count += 1
        else:
            self.nonce_count = 1

        self.last_nonce = nonce

        ncvalue = '%08x' % self.nonce_count

        # cnonce is just a random string generated by the client.
        cnonce_data = ''.join([
            str(self.nonce_count),
            nonce,
            time.ctime(),
            os.urandom(8).decode(errors='ignore'),
        ]).encode()
        cnonce = hashlib.sha1(cnonce_data).hexdigest()[:16]

        if algorithm == 'MD5-SESS':
            HA1 = H('%s:%s:%s' % (HA1, nonce, cnonce))

        # This assumes qop was validated to be 'auth' above. If 'auth-int'
        # support is added this will need to change.
        if qop:
            noncebit = ':'.join([
                nonce, ncvalue, cnonce, 'auth', HA2
            ])
            response_digest = KD(HA1, noncebit)
        else:
            response_digest = KD(HA1, '%s:%s' % (nonce, HA2))

        base = ', '.join([
            'username="%s"' % self.username,
            'realm="%s"' % realm,
            'nonce="%s"' % nonce,
            'uri="%s"' % path,
            'response="%s"' % response_digest,
            'algorithm="%s"' % algorithm,
        ])
        if opaque:
            base += ', opaque="%s"' % opaque
        if qop:
            base += ', qop="auth", nc=%s, cnonce="%s"' % (ncvalue, cnonce)

        return 'Digest %s' % base

    async def _handle_401(self, response):
        """
        Takes the given response and tries digest-auth, if needed.
        :rtype: ClientResponse
        """
        auth_header = response.headers.get('WWW-Authenticate', '')

        parts = auth_header.split(' ', 1)
        if 'digest' == parts[0].lower() and len(parts) > 1:
            self.challenge = parse_key_value_list(parts[1])

            return await self.request(
                self.args['method'],
                self.args['url'],
                headers=self.args['headers'],
                **self.args['kwargs']
            )

        return response


def parse_pair(pair):
    key, value = pair.split('=', 1)

    # If it has a trailing comma, remove it.
    if value[-1] == ',':
        value = value[:-1]

    # If it is quoted, then remove them.
    if value[0] == value[-1] == '"':
        value = value[1:-1]

    return str(key).strip(), str(value).strip()


def parse_key_value_list(header):
    return {
        key: value for key, value in
        [parse_pair(header_pair) for header_pair in header.split(',')]
    }
