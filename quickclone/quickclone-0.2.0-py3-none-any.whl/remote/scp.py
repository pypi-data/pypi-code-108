from __future__ import annotations
import typing as t

from .locators import BaseLocator, UrlAuthority


class ScpLocator(object):
    """
    An object for representing SCP locators. You will encounter such locators
    when you are trying to clone git repositories from github or gitlab using
    SSH. These locators come in this format:
    `<username>:<password>@<host>:<path>`.
    
    Parameters
    ----------
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
    
    path: str = ""
        The path to the remote repository
        (not referring to where the local clone is located).
        Comes after the host and separated from it by ':'.
        Examples: RenoirTan/QuickClone
        (in https://github.com/RenoirTan/QuickClone)
    
    **kwargs: Any
        Miscellaneous data.
    """
    
    def __init__(
        self,
        host: str = "",
        username: str = "",
        password: str = "",
        path: str = "",
        **kwargs
    ) -> None:
        self.host = host
        self.username = username
        self.password = password
        self.path = path
        self.kwargs = kwargs
    
    def __str__(self) -> str:
        authority_part = authority_part = str(
            UrlAuthority(self.get_host(), self.get_username(), self.get_password(), "")
        )
        path_part = f":{self.get_path()}" if self.get_path() != "" else ""
        return authority_part + path_part
        
    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"host={repr(self.host)}, "
            f"username={repr(self.username)}, "
            f"password={repr(self.password)}, "
            f"path={repr(self.path)}"
        )
    
    def __iter__(self) -> t.Generator[t.Tuple[str, str], None, None]:
        yield "host", self.get_host()
        yield "username", self.get_username()
        yield "password", self.get_password()
        yield "path", self.get_path()
    
    def get_host(self) -> str:
        """Get the host name of the website hosting the remote repository."""
        return self.host
    
    def get_username(self) -> str:
        """Get the username used to access the remote repository."""
        return self.username
    
    def get_password(self) -> str:
        """Get the password used to access the remote repository."""
        return self.password
    
    def get_path(self) -> str:
        """Get the path of the remote repository (in the website)."""
        return self.path
    
    @classmethod
    def from_locator(cls, locator: BaseLocator) -> ScpLocator:
        """
        Create an SCP locator from a normal locator (used in typical RFC 3986
        URLs).
        
        Parameters
        ----------
        cls: Type[ScpLocator]
            The `ScpLocator` class type.
        
        locator: BaseLocator
            The locator to be converted into an SCP locator.
        
        Returns
        -------
        ScpLocator
        """
        return cls(
            locator.get_host(),
            locator.get_username(),
            locator.get_password(),
            locator.get_path(),
            **locator.kwargs
        )
