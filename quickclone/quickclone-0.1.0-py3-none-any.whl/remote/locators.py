from __future__ import annotations
import typing as t

from .parser import parse_authority, parse_dirty_url, parse_full_url

__all__ = [
    "BaseLocator",
    "UniformResourceLocator",
    "DirtyLocator",
    "LocatorBuilder",
    "UrlAuthority"
]


LOCATOR_FIELDS: str = """
Fields
------
scheme: str
    The scheme used to access the remote repository.
    Comes before everything else in a URL and is suffixed by '://'.
    Examples: https, ssh

host: str
    The host where the remote repository is located.
    Examples: github.com, 1.1.1.1

username: str
    The username used to access the remote repository.
    Comes before the host and is separated from the latter by '@'.
    Examples: git (in git@github.com)

password: str
    Password of the user used to authenticate themselves.
    If present, must come after a username (separated by ':') and before
    a host name (separated by '@').
    RFC 3986 recommends that you don't ever use this because it's a huge
    security vulnerability.
    However, this is still used by github when you use HTTPS.

port: str
    The port used to connect to the server.
    If present, must come after the host name and must be an integer
    between 0 and 65535 (inclusive).

path: str
    The path to the remote repository
    (not referring to where the local clone is located).
    Comes after the host and separated from it by '/'.
    Examples: RenoirTan/QuickClone
    (in https://github.com/RenoirTan/QuickClone)

query: str
    The parameters in the URL.
    Comes after the path or host and the start of the query section is
    denoted by '?'.
    You can chain multiple key-value pairs using '&' as the separator.
    Examples: key=value (in https://example.com?key=value)

fragment: str
    The fragment identifying a secondary resource.
    The last part of the URL. The fragment section is denoted by '#'.
    Examples: History
    (in https://en.wikipedia.org/wiki/Python_(programming_language)#History)
"""


FIELDS = ["scheme", "host", "username", "password", "port", "path", "query", "fragment"]


class BaseLocator(object):
    """
    Base class for classes representing Uniform Resource Locators (URLs).
    This stores the parts of the URL like the domain name or path in the URL.
    
    Fields
    ------
    scheme: str
        The scheme used to access the remote repository.
        Comes before everything else in a URL and is suffixed by '://'.
        Examples: https, ssh

    host: str
        The host where the remote repository is located.
        Examples: github.com, 1.1.1.1

    username: str
        The username used to access the remote repository.
        Comes before the host and is separated from the latter by '@'.
        Examples: git (in git@github.com)

    password: str
        Password of the user used to authenticate themselves.
        If present, must come after a username (separated by ':') and before
        a host name (separated by '@').
        RFC 3986 recommends that you don't ever use this because it's a huge
        security vulnerability.
        However, this is still used by github when you use HTTPS.
    
    port: str
        The port used to connect to the server.
        If present, must come after the host name and must be an integer
        between 0 and 65535 (inclusive).

    path: str
        The path to the remote repository
        (not referring to where the local clone is located).
        Comes after the host and separated from it by '/'.
        Examples: RenoirTan/QuickClone
        (in https://github.com/RenoirTan/QuickClone)

    query: str
        The parameters in the URL.
        Comes after the path or host and the start of the query section is
        denoted by '?'.
        You can chain multiple key-value pairs using '&' as the separator.
        Examples: key=value (in https://example.com?key=value)

    fragment: str
        The fragment identifying a secondary resource.
        The last part of the URL. The fragment section is denoted by '#'.
        Examples: History
        (in https://en.wikipedia.org/wiki/Python_(programming_language)#History)
    """
    
    def __init__(
        self,
        scheme: str = "",
        host: str = "",
        username: str = "",
        password: str = "",
        path: str = "",
        port: str = "",
        query: str = "",
        fragment: str = "",
        **kwargs # Easy way to ignore excess keys
    ) -> None:
        """
        Initiate an object representing a URL.
        
        Parameters
        ----------
        self: BaseLocator
            The object to be initialised.
        
        scheme: str = ""
            The scheme used to access the remote repository.
            Comes before everything else in a URL and is suffixed by '://'.
            Examples: https, ssh

        host: str = ""
            The host where the remote repository is located.
            Examples: github.com, 1.1.1.1

        username: str = ""
            The username used to access the remote repository.
            Comes before the host and is separated from the latter by '@'.
            Examples: git (in git@github.com)

        password: str = ""
            Password of the user used to authenticate themselves.
            If present, must come after a username (separated by ':') and before
            a host name (separated by '@').
            RFC 3986 recommends that you don't ever use this because it's a huge
            security vulnerability.
            However, this is still used by github when you use HTTPS.
        
        port: str = ""
            The port used to connect to the server.
            If present, must come after the host name and must be an integer
            between 0 and 65535 (inclusive).

        path: str = ""
            The path to the remote repository
            (not referring to where the local clone is located).
            Comes after the host and separated from it by '/'.
            Examples: RenoirTan/QuickClone
            (in https://github.com/RenoirTan/QuickClone)

        query: str = ""
            The parameters in the URL.
            Comes after the path or host and the start of the query section is
            denoted by '?'.
            You can chain multiple key-value pairs using '&' as the separator.
            Examples: key=value (in https://example.com?key=value)

        fragment: str = ""
            The fragment identifying a secondary resource.
            The last part of the URL. The fragment section is denoted by '#'.
            Examples: History
            (in https://en.wikipedia.org/wiki/Python_(programming_language)#History)
        """
        self.scheme = scheme
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.path = path
        self.query = query
        self.fragment = fragment
    
    def __str__(self) -> str:
        scheme_part = f"{self.get_scheme()}://" if self.get_scheme() != "" else ""
        authority_part = str(UrlAuthority(
            self.get_host(),
            self.get_username(),
            self.get_password(),
            self.get_port()
        ))
        path_part = f"/{self.get_path()}" if self.get_path() != "" else ""
        query_part = f"?{self.get_query()}" if self.get_query() != "" else ""
        fragment_part = f"#{self.get_fragment()}" if self.get_fragment() != "" else ""
        return scheme_part + authority_part + path_part + query_part + fragment_part
        
    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"scheme={repr(self.scheme)}, "
            f"host={repr(self.host)}, "
            f"username={repr(self.username)}, "
            f"password={repr(self.password)}, "
            f"port={repr(self.port)}, "
            f"path={repr(self.path)}, "
            f"query={repr(self.query)}, "
            f"fragment={repr(self.fragment)})"
        )
    
    def __iter__(self) -> t.Generator[t.Tuple[str, str], None, None]:
        yield "scheme", self.get_scheme()
        yield "host", self.get_host()
        yield "username", self.get_username()
        yield "password", self.get_password()
        yield "port", self.get_port()
        yield "path", self.get_path()
        yield "query", self.get_query()
        yield "fragment", self.get_fragment()
    
    def get_scheme(self) -> str:
        """Get the scheme used to access the remote repository."""
        return self.scheme

    def get_host(self) -> str:
        """Get the host name of the website hosting the remote repository."""
        return self.host

    def get_username(self) -> str:
        """Get the username used to access the remote repository."""
        return self.username

    def get_password(self) -> str:
        """Get the password used to access the remote repository."""
        return self.password
    
    def get_port(self) -> str:
        """
        Get the port used to access the server hosting the remote repository.
        """
        return self.port

    def get_path(self) -> str:
        """Get the path of the remote repository (in the website)."""
        return self.path

    def get_query(self) -> str:
        """Get the parameters (as a single string)."""
        return self.query

    def get_fragment(self) -> str:
        """Get the fragment."""
        return self.fragment


class UniformResourceLocator(BaseLocator):
    """
    A full uniform resource locator (hopefully RFC 3986 compliant).
    
    Fields
    ------
    scheme: str
        The scheme used to access the remote repository.
        Comes before everything else in a URL and is suffixed by '://'.
        Examples: https, ssh

    host: str
        The host where the remote repository is located.
        Examples: github.com, 1.1.1.1

    username: str
        The username used to access the remote repository.
        Comes before the host and is separated from the latter by '@'.
        Examples: git (in git@github.com)

    password: str
        Password of the user used to authenticate themselves.
        If present, must come after a username (separated by ':') and before
        a host name (separated by '@').
        RFC 3986 recommends that you don't ever use this because it's a huge
        security vulnerability.
        However, this is still used by github when you use HTTPS.
    
    port: str
        The port used to connect to the server.
        If present, must come after the host name and must be an integer
        between 0 and 65535 (inclusive).

    path: str
        The path to the remote repository
        (not referring to where the local clone is located).
        Comes after the host and separated from it by '/'.
        Examples: RenoirTan/QuickClone
        (in https://github.com/RenoirTan/QuickClone)

    query: str
        The parameters in the URL.
        Comes after the path or host and the start of the query section is
        denoted by '?'.
        You can chain multiple key-value pairs using '&' as the separator.
        Examples: key=value (in https://example.com?key=value)

    fragment: str
        The fragment identifying a secondary resource.
        The last part of the URL. The fragment section is denoted by '#'.
        Examples: History
        (in https://en.wikipedia.org/wiki/Python_(programming_language)#History)
    """
    
    def __str__(self) -> str:
        for fault in self.find_faults():
            raise fault
        return super().__str__()
    
    def find_faults(self) -> t.Generator[BaseException, None, None]:
        """
        Find errors in this URL. This method returns a generator object, which
        allows you to iterate over this method.
        
        Yields
        ------
        BaseException
            All the errors that are encountered when reviewing the URL. If no
            errors are found, no exceptions will be yielded.
        """
        if self.get_username() == "" and self.get_password() != "":
            yield ValueError("Username not given but password given.")
        if self.get_scheme() == "":
            yield ValueError("No scheme specified.")
        if self.get_host() == "":
            yield ValueError("Empty host.")

    def validate(self) -> bool:
        """
        Validate this URL by making sure no errors are found in this URL.
        This uses the `find_faults` method to try and find errors.
        
        Returns
        -------
        bool
            `True` if this URL has no errors in it and `False` otherwise.
        """
        return sum(map(lambda _: 1, self.find_faults())) == 0
    
    @classmethod
    def process_url(cls, url: str) -> UniformResourceLocator:
        """
        Process a URL and turn it into `UniformResourceLocator` object. The
        URL must have at least a scheme and host.
        
        Parameters
        ----------
        cls: Type[UniformResourceLocator]
            The UniformResourceLocator class.
        
        url: str
            The URL to be parsed and decomposed into a UniformResourceLocator.
        
        Raises
        ------
        ValueError
            If an error was found in the URL. Only the first error encountered
            will be raised.
        
        Returns
        -------
        UniformResourceLocator
        """
        parsed = parse_full_url(url, none_str="to_str")
        if parsed == {}:
            raise ValueError(f"Invalid URL: {url}")
        url: UniformResourceLocator = UniformResourceLocator(**parsed)
        for fault in url.find_faults():
            raise fault
        return url
    
    @classmethod
    def from_user_and_defaults(
        cls,
        user_input: DirtyLocator,
        defaults: LocatorBuilder
    ) -> UniformResourceLocator:
        """
        Create a final URL from the user input and defaults drawn from user
        configurations or hard coded into QuickClone.
        
        Parameters
        ----------
        cls: Type[UniformResourceLocator]
            The UniformResourceLocator class.
        
        user_input: DirtyLocator
            The user-inputted URL.
        
        defaults: LocatorBuilder
            The defaults from configs.
        
        Raises
        ------
        ValueError
            If vital bits are missing.
        
        Returns
        -------
        UniformResourceLocator
        """
        parts = dict(defaults)
        for key, value in user_input:
            if value != "":
                parts[key] = value
        url = cls(**parts)
        for fault in url.find_faults():
            raise fault
        return url


class DirtyLocator(BaseLocator):
    """
    A locator object representing a user-inputted URL (with parts possibly
    missing).
    
    Fields
    ------
    scheme: str
        The scheme used to access the remote repository.
        Comes before everything else in a URL and is suffixed by '://'.
        Examples: https, ssh

    host: str
        The host where the remote repository is located.
        Examples: github.com, 1.1.1.1

    username: str
        The username used to access the remote repository.
        Comes before the host and is separated from the latter by '@'.
        Examples: git (in git@github.com)

    password: str
        Password of the user used to authenticate themselves.
        If present, must come after a username (separated by ':') and before
        a host name (separated by '@').
        RFC 3986 recommends that you don't ever use this because it's a huge
        security vulnerability.
        However, this is still used by github when you use HTTPS.
    
    port: str
        The port used to connect to the server.
        If present, must come after the host name and must be an integer
        between 0 and 65535 (inclusive).

    path: str
        The path to the remote repository
        (not referring to where the local clone is located).
        Comes after the host and separated from it by '/'.
        Examples: RenoirTan/QuickClone
        (in https://github.com/RenoirTan/QuickClone)

    query: str
        The parameters in the URL.
        Comes after the path or host and the start of the query section is
        denoted by '?'.
        You can chain multiple key-value pairs using '&' as the separator.
        Examples: key=value (in https://example.com?key=value)

    fragment: str
        The fragment identifying a secondary resource.
        The last part of the URL. The fragment section is denoted by '#'.
        Examples: History
        (in https://en.wikipedia.org/wiki/Python_(programming_language)#History)
    """
    
    @classmethod
    def process_dirty_url(cls, dirty_url: str) -> DirtyLocator:
        """
        Process a user-inputted URL (`dirty_url`).

        Parameters
        ----------
        cls: typing.Type[UrlAuthority]
            The UrlAuthority class.

        dirty_url: str
            The user-inputted URL.
        
        Raises
        ------
        ValueError
            If regex could not find matches using the `dirty_url`.

        Returns
        -------
        UrlAuthority
        """
        result = parse_dirty_url(dirty_url, none_str="to_str")
        if result == {}:
            raise ValueError(f"Could not match {dirty_url}")
        fields = {field: result[field] for field in FIELDS}
        return cls(**fields)


class LocatorBuilder(BaseLocator):
    """
    A builder which stores user/program specified defaults to generate valid
    URLs from user inputs.
    
    Fields
    ------
    scheme: str
        The scheme used to access the remote repository.
        Comes before everything else in a URL and is suffixed by '://'.
        Examples: https, ssh

    host: str
        The host where the remote repository is located.
        Examples: github.com, 1.1.1.1

    username: str
        The username used to access the remote repository.
        Comes before the host and is separated from the latter by '@'.
        Examples: git (in git@github.com)

    password: str
        Password of the user used to authenticate themselves.
        If present, must come after a username (separated by ':') and before
        a host name (separated by '@').
        RFC 3986 recommends that you don't ever use this because it's a huge
        security vulnerability.
        However, this is still used by github when you use HTTPS.
    
    port: str
        The port used to connect to the server.
        If present, must come after the host name and must be an integer
        between 0 and 65535 (inclusive).

    path: str
        The path to the remote repository
        (not referring to where the local clone is located).
        Comes after the host and separated from it by '/'.
        Examples: RenoirTan/QuickClone
        (in https://github.com/RenoirTan/QuickClone)

    query: str
        The parameters in the URL.
        Comes after the path or host and the start of the query section is
        denoted by '?'.
        You can chain multiple key-value pairs using '&' as the separator.
        Examples: key=value (in https://example.com?key=value)

    fragment: str
        The fragment identifying a secondary resource.
        The last part of the URL. The fragment section is denoted by '#'.
        Examples: History
        (in https://en.wikipedia.org/wiki/Python_(programming_language)#History)
    """

    DEFAULT_SCHEME: str = "https"
    """
    The default scheme used to access the remote repository. By default this is "https".
    """

    DEFAULT_HOST: str = "github.com"
    """
    The default host where the remote repository is located. By default this is "github.com".
    """

    def get_scheme(self) -> str:
        """Get the scheme used to access the remote repository."""
        return self.DEFAULT_SCHEME if self.scheme == "" else self.scheme

    def get_host(self) -> str:
        """Get the host name of the website hosting the remote repository."""
        return self.DEFAULT_HOST if self.host == "" else self.host


class UrlAuthority(object):
    """
    The authority component in a URL. This includes the host name, username
    password and port in the URL. Example: username:password@example.com:80

    Parameters
    ----------
    self: UrlAuthority
        The UrlAuthority object to be initialised.

    host: str
        The host name of the URL.

    username: str = ""
        The username in the URL.

    password: str = ""
        The password in the URL.
    
    port: str = ""
        The port in the URL. Must be a value between 0 and 65535 (inclusive).
    """

    def __init__(
        self,
        host: str,
        username: str = "",
        password: str = "",
        port: str = ""
    ) -> None:
        self.host = host
        self.username = username
        self.password = password
        self.port = port
    
    def __str__(self) -> str:
        userpass_part = self.username
        if self.password != "":
            userpass_part += f":{self.password}"
        if len(userpass_part) > 0:
            userpass_part += "@"
        port_part = f":{self.port}" if self.port != "" else ""
        return userpass_part + self.host + port_part

    @classmethod
    def process_authority(cls, authority: str) -> UrlAuthority:
        """
        Convert an authority (as a string) into a `UrlAuthority` object.

        Parameters
        ----------
        cls: typing.Type[UrlAuthority]
            The UrlAuthority class.

        authority: str
            The authority section in the URL.
        
        Raises
        ------
        ValueError
            If password provided without providing username.

        Returns
        -------
        UrlAuthority
        """
        result = parse_authority(authority, none_str="to_str")
        host = result["host"]
        username = result["username"]
        password = result["password"]
        port = result["port"]
        if username == "" and password != "":
            raise ValueError("Password provided without username.")
        return cls(host, username, password, port)
