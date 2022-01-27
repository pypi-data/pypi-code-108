"""Declares :class:`BaseCache`."""
import functools
import typing


class BaseCache:
    """The base class for all cache implementations."""

    @property
    def opts(self):
        return self._opts

    @property
    def prefix(self) -> str:
        return self._opts.prefix

    @staticmethod
    def needs_connection(func):
        """Return a decorator that ensures that a connection
        is set up when the decorated function is invoked.
        """
        @functools.wraps(func)
        async def f(self, *args, **kwargs):
            if not self.is_connected():
                await self.connect()
            return await func(self, *args, **kwargs)
        return f

    def __init__(self, opts):
        self._opts = opts
        self._impl = None
        self.setup(opts)

    def abskey(self, key, version):
        """Returns the absolute key name."""
        return f'{self.opts.prefix}:{key}:{version}'

    async def connect(self):
        """Connect to the backend cache service."""
        raise NotImplementedError

    async def join(self):
        """Waits until the connection is closed."""
        raise NotImplementedError

    def close(self):
        """Closes the connection with the cache server."""
        raise NotImplementedError

    async def delete(self, name):
        """Delete a key from the cache."""
        raise NotImplementedError

    async def get(self,
        name: str,
        version: str = None,
        decoder: object = None
    ) -> typing.Union[bytes, str, None]:
        """Get a key from the cache."""
        raise NotImplementedError

    async def set(self,
        name: str,
        value: typing.Union[bytes, str],
        version: str = None,
        expires: int = None,
        overwrite: bool = True
    ) -> typing.Union[bool, bytes, str]:
        """Set a key in the cache."""
        raise NotImplementedError

    def setup(self, opts: dict):
        """Hook that is invoked during instance initialization."""
        pass

    def is_connected(self):
        """Return a boolean indicating if a connection is
        established with the cache service.
        """
        return self._impl is not None
