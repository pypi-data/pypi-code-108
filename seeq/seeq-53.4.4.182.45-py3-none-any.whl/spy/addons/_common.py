from packaging import version

from seeq.spy import _login
from seeq.spy._errors import *
from seeq.spy._session import Session


def verify_addons_support(session: Session):
    # We will have to keep this code till R53 is phased out, since there is a possibility of having versions R52 or
    # R53 with the external_tools endpoint.
    seeq_server_major, seeq_server_minor, seeq_server_patch = _login.get_server_version_tuple(session)
    seeq_server_version = f"{seeq_server_major}.{seeq_server_minor}.{seeq_server_patch}"
    if seeq_server_major == 52:
        if version.parse(seeq_server_version) < version.parse("52.1.5"):
            raise SPyValueError(f"Seeq R52 versions before R52.1.5 do not support spy.addons")
    elif seeq_server_major == 53:
        if version.parse(seeq_server_version) < version.parse("53.0.2"):
            raise SPyValueError(f"Seeq R53 versions before R53.0.2 do not support spy.addons")
