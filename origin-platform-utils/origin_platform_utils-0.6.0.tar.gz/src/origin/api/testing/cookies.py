from typing import Optional
from datetime import datetime
from wsgiref.headers import Headers
from http.cookies import SimpleCookie


class CookieTester(object):
    """
    Helper for testing cookies in HTTP responses.

    TODO Test this class.
    """
    def __init__(self, headers: Headers):
        """
        :param headers:
        """
        self.cookies = SimpleCookie('\r\n'.join(headers.get_all('Set-Cookie')))

    def assert_has_cookies(self, *names: str) -> 'CookieTester':
        """
        Assert that exactly the specified cookies were set.

        :param names:
        """
        assert tuple(self.cookies.keys()) == names

        return self

    def assert_cookie(
            self,
            name: str,
            value: Optional[str] = None,
            expires: Optional[datetime] = None,
            path: Optional[str] = None,
            comment: Optional[str] = None,
            domain: Optional[str] = None,
            max_age: Optional[str] = None,
            secure: Optional[bool] = None,
            http_only: Optional[bool] = None,
            version: Optional[str] = None,
            same_site: Optional[bool] = None,
    ) -> 'CookieTester':
        """
        Assert content of a cookie.

        :param name:
        :param value:
        :param expires:
        :param path:
        :param comment:
        :param domain:
        :param max_age:
        :param secure:
        :param http_only:
        :param version:
        :param same_site:
        :return:
        """
        if value is not None:
            assert self.cookies[name].value == value
        assert self.cookies[name]['expires'] == \
               (expires.strftime('%a, %d %b %Y %H:%M:%S GMT')
                if expires is not None else '')
        assert self.cookies[name]['path'] == \
               (path if path is not None else '')
        assert self.cookies[name]['comment'] == \
               (comment if comment is not None else '')
        assert self.cookies[name]['domain'] == \
               (domain if domain is not None else '')
        assert self.cookies[name]['max-age'] == \
               (max_age if max_age is not None else '')
        assert self.cookies[name]['secure'] == \
               (secure if secure else '')
        assert self.cookies[name]['httponly'] == \
               (http_only if http_only else '')
        assert self.cookies[name]['version'] == \
               (version if version is not None else '')
        assert self.cookies[name]['samesite'] == \
               ('Strict' if same_site else 'None')

        return self

    def get_value(self, name: str) -> Optional[str]:
        """
        Get value of a cookie.
        """
        return self.cookies[name].value
