import unittest

from cassyy import (
    CASClient,
    CASError,
    CASInvalidServiceError,
    CASInvalidTicketError,
)


class CASClientTestCase(unittest.TestCase):
    cas_login_url = 'https://cas.local/login'
    cas_logout_url = 'https://cas.local/logout'
    cas_validate_url = 'https://cas.local/p3/serviceValidate'
    test_service_url = 'https://foo.org'

    def setUp(self):
        self.client = CASClient(
            self.cas_login_url,
            self.cas_logout_url,
            self.cas_validate_url
        )

    def test_from_base_url(self):
        c = CASClient.from_base_url('https://cas.local/')
        self.assertEqual(c.login_url, 'https://cas.local/login')
        self.assertEqual(c.logout_url, 'https://cas.local/logout')
        self.assertEqual(c.validate_url, 'https://cas.local/p3/serviceValidate')

    def test_from_base_url_with_alt_paths(self):
        c = CASClient.from_base_url('https://cas.local/',
                                    login_path='foo',
                                    logout_path='bar/baz',
                                    validate_path='/qux')
        self.assertEqual(c.login_url, 'https://cas.local/foo')
        self.assertEqual(c.logout_url, 'https://cas.local/bar/baz')
        self.assertEqual(c.validate_url, 'https://cas.local/qux')

    def test_parse_userid(self):
        s = """
        <cas:serviceResponse xmlns:cas='http://www.yale.edu/tp/cas'>
            <cas:authenticationSuccess>
                <cas:user>jdoe</cas:user>
            </cas:authenticationSuccess>
        </cas:serviceResponse>
        """
        self.assertEqual('jdoe', self.client.parse_cas_response(s).userid)

    def test_parse_non_xml(self):
        s = "jdoe"
        with self.assertRaises(CASError) as cm:
            self.client.parse_cas_response(s)
        self.assertEqual('INVALID_RESPONSE', cm.exception.error_code)
        self.assertEqual("ParseError('syntax error: line 1, column 0')",
                         str(cm.exception.args[1]))

    def test_parse_invalid_ticket(self):
        s = """
        <cas:serviceResponse xmlns:cas='http://www.yale.edu/tp/cas'>
            <cas:authenticationFailure code="INVALID_TICKET">
                Ticket &#39;ST-foo&#39; not recognized
            </cas:authenticationFailure>
        </cas:serviceResponse>
        """
        with self.assertRaises(CASInvalidTicketError) as cm:
            self.client.parse_cas_response(s)
        self.assertEqual('INVALID_TICKET', cm.exception.error_code)

    def test_parse_invalid_service(self):
        s = """
        <cas:serviceResponse xmlns:cas='http://www.yale.edu/tp/cas'>
            <cas:authenticationFailure code="INVALID_SERVICE">
                Ticket &#39;ST-338345-KTQdtsv9b5WKtfVfrahU-cas3&#39; does not match supplied service. '
                The original service was &#39;https://foo.org&#39; and the supplied service was &#39;https://foo2.org&#39;.
            </cas:authenticationFailure>
        </cas:serviceResponse>
        """
        with self.assertRaises(CASInvalidServiceError) as cm:
            self.client.parse_cas_response(s)
        self.assertEqual('INVALID_SERVICE', cm.exception.error_code)

    def test_build_login_url(self):
        url = self.client.build_login_url(self.test_service_url)
        self.assertEqual(
            f'{self.cas_login_url}?service=https%3A%2F%2Ffoo.org',
            url
        )

    def test_build_login_url_with_postback(self):
        url = self.client.build_login_url(self.test_service_url, callback_post=True)
        self.assertEqual(
            f'{self.cas_login_url}?service=https%3A%2F%2Ffoo.org&method=POST',
            url
        )

    def test_build_validate_url(self):
        url = self.client.build_validate_url(self.test_service_url, 'tix')
        self.assertEqual(
            f'{self.cas_validate_url}?service=https%3A%2F%2Ffoo.org&ticket=tix',
            url
        )

    def test_build_logout_url(self):
        url = self.client.build_logout_url(self.test_service_url)
        self.assertEqual(
            f'{self.cas_logout_url}?service=https%3A%2F%2Ffoo.org',
            url
        )

    def test_parse_attributes(self):
        s = """
            <cas:serviceResponse xmlns:cas='http://www.yale.edu/tp/cas'>
                <cas:authenticationSuccess>
                    <cas:user>jdoe</cas:user>
                    <cas:attributes>
                        <cas:clientIpAddress>10.0.0.2</cas:clientIpAddress>
                        <cas:isFromNewLogin>true</cas:isFromNewLogin>
                        <cas:mail>jdoe@foo.org</cas:mail>
                        <cas:authenticationDate>2022-01-21T23:03:05.920747Z</cas:authenticationDate>
                        <cas:bypassMultifactorAuthentication>false</cas:bypassMultifactorAuthentication>
                        <cas:authnContextClass>mfa-example</cas:authnContextClass>
                        <cas:successfulAuthenticationHandlers>DuoSecurityAuthenticationHandler</cas:successfulAuthenticationHandlers>
                        <cas:userAgent>Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36</cas:userAgent>
                        <cas:cn>Jane Doe</cas:cn>
                        <cas:credentialType>DuoSecurityCredential</cas:credentialType>
                        <cas:authenticationMethod>DuoSecurityAuthenticationHandler</cas:authenticationMethod>
                        <cas:serverIpAddress>10.0.0.1</cas:serverIpAddress>
                        <cas:longTermAuthenticationRequestTokenUsed>false</cas:longTermAuthenticationRequestTokenUsed>
                        </cas:attributes>
                </cas:authenticationSuccess>
            </cas:serviceResponse>
        """
        cas_user = self.client.parse_cas_response(s)
        self.assertEqual('jdoe', cas_user.userid)
        self.assertEqual('jdoe@foo.org', cas_user.attributes['mail'])
        self.assertEqual('Jane Doe', cas_user.attributes['cn'])
        self.assertEqual('10.0.0.2', cas_user.attributes['clientIpAddress'])
