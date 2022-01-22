"""Various utility functions to avoid boilerplate when performing common operations."""
import pathlib
import sys
import traceback
from contextlib import contextmanager
from typing import Generator, Union
from urllib.parse import ParseResult, urlparse

import grpc


@contextmanager
def syspath_prepend(path: Union[pathlib.Path, str]) -> Generator:
    """Temporarily prepend `path` to `sys.path` for the duration of the `with` block."""
    # NOTE. It is not thread-safe to use as is now.
    # In the future it might require an `RLock` to avoid concurrent access to `sys.path`.
    current = sys.path[:]
    # Use `insert` to put the value to the 0th position in `sys.path`. The given path will be the first one to check.
    sys.path.insert(0, str(path))
    try:
        yield
    finally:
        sys.path[:] = current


def get_grpc_channel(url: str) -> grpc.Channel:
    """Connect to a gRPC channel.

    For HTTPS it returns a secure channel and an insecure one for HTTP.
    """

    # TODO: (mike@levo.ai)
    # For whatever reason, Python or the grpc client library is no longer
    # picking up the system's trust store.  isrg_root_x1_pem is the contents
    # of...
    # https://letsencrypt.org/certs/isrgrootx1.pem
    # ...and I have verified that a file with the same contents is present in
    # /etc/ssl/certs on my system.
    #
    # Passing isrg_root_x1_pem to grpc.ssl_channel_credentials() as seen below
    # works around the TLS handshake issue we were debugging.  However, this
    # should be a SHORT TERM workaround.  We need to give some thought to how we
    # will consistently and reliably manage trust stores for any part of our
    # code that is acting as a TLS client and migrate the code below to our
    # chosen framework or convention.

    isrg_root_x1_pem = """\
-----BEGIN CERTIFICATE-----
MIIFFjCCAv6gAwIBAgIRAJErCErPDBinU/bWLiWnX1owDQYJKoZIhvcNAQELBQAw
TzELMAkGA1UEBhMCVVMxKTAnBgNVBAoTIEludGVybmV0IFNlY3VyaXR5IFJlc2Vh
cmNoIEdyb3VwMRUwEwYDVQQDEwxJU1JHIFJvb3QgWDEwHhcNMjAwOTA0MDAwMDAw
WhcNMjUwOTE1MTYwMDAwWjAyMQswCQYDVQQGEwJVUzEWMBQGA1UEChMNTGV0J3Mg
RW5jcnlwdDELMAkGA1UEAxMCUjMwggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEK
AoIBAQC7AhUozPaglNMPEuyNVZLD+ILxmaZ6QoinXSaqtSu5xUyxr45r+XXIo9cP
R5QUVTVXjJ6oojkZ9YI8QqlObvU7wy7bjcCwXPNZOOftz2nwWgsbvsCUJCWH+jdx
sxPnHKzhm+/b5DtFUkWWqcFTzjTIUu61ru2P3mBw4qVUq7ZtDpelQDRrK9O8Zutm
NHz6a4uPVymZ+DAXXbpyb/uBxa3Shlg9F8fnCbvxK/eG3MHacV3URuPMrSXBiLxg
Z3Vms/EY96Jc5lP/Ooi2R6X/ExjqmAl3P51T+c8B5fWmcBcUr2Ok/5mzk53cU6cG
/kiFHaFpriV1uxPMUgP17VGhi9sVAgMBAAGjggEIMIIBBDAOBgNVHQ8BAf8EBAMC
AYYwHQYDVR0lBBYwFAYIKwYBBQUHAwIGCCsGAQUFBwMBMBIGA1UdEwEB/wQIMAYB
Af8CAQAwHQYDVR0OBBYEFBQusxe3WFbLrlAJQOYfr52LFMLGMB8GA1UdIwQYMBaA
FHm0WeZ7tuXkAXOACIjIGlj26ZtuMDIGCCsGAQUFBwEBBCYwJDAiBggrBgEFBQcw
AoYWaHR0cDovL3gxLmkubGVuY3Iub3JnLzAnBgNVHR8EIDAeMBygGqAYhhZodHRw
Oi8veDEuYy5sZW5jci5vcmcvMCIGA1UdIAQbMBkwCAYGZ4EMAQIBMA0GCysGAQQB
gt8TAQEBMA0GCSqGSIb3DQEBCwUAA4ICAQCFyk5HPqP3hUSFvNVneLKYY611TR6W
PTNlclQtgaDqw+34IL9fzLdwALduO/ZelN7kIJ+m74uyA+eitRY8kc607TkC53wl
ikfmZW4/RvTZ8M6UK+5UzhK8jCdLuMGYL6KvzXGRSgi3yLgjewQtCPkIVz6D2QQz
CkcheAmCJ8MqyJu5zlzyZMjAvnnAT45tRAxekrsu94sQ4egdRCnbWSDtY7kh+BIm
lJNXoB1lBMEKIq4QDUOXoRgffuDghje1WrG9ML+Hbisq/yFOGwXD9RiX8F6sw6W4
avAuvDszue5L3sz85K+EC4Y/wFVDNvZo4TYXao6Z0f+lQKc0t8DQYzk1OXVu8rp2
yJMC6alLbBfODALZvYH7n7do1AZls4I9d1P4jnkDrQoxB3UqQ9hVl3LEKQ73xF1O
yK5GhDDX8oVfGKF5u+decIsH4YaTw7mP3GFxJSqv3+0lUFJoi5Lc5da149p90Ids
hCExroL1+7mryIkXPeFM5TgO9r0rvZaBFOvV2z0gp35Z0+L4WPlbuEjN/lxPFin+
HlUjr8gRsI3qfJOQFy/9rKIJR0Y/8Omwt/8oTWgy1mdeHmmjk7j1nYsvC9JSQ6Zv
MldlTTKB3zhThV1+XWYp6rjd5JW1zbVWEkLNxE7GJThEUG3szgBVGP7pSWTUTsqX
nLRbwHOoq7hHwg==
-----END CERTIFICATE-----""".encode(
        "ascii"
    )
    parsed = urlparse(url)
    address = get_grpc_address(parsed)
    if parsed.scheme == "https":
        return grpc.secure_channel(
            address, grpc.ssl_channel_credentials(root_certificates=isrg_root_x1_pem)
        )
    return grpc.insecure_channel(address)


def get_grpc_address(parsed: ParseResult) -> str:
    if parsed.port is not None:
        port = parsed.port
    else:
        port = 443 if parsed.scheme == "https" else 80
    return f"{parsed.hostname}:{port}"


def format_exception(error: Exception, include_traceback: bool = False) -> str:
    """Format exception as text."""
    error_type = type(error)
    if include_traceback:
        lines = traceback.format_exception(error_type, error, error.__traceback__)
    else:
        lines = traceback.format_exception_only(error_type, error)
    return "".join(lines)
