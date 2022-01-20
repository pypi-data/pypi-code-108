from cnvrgv2.config import error_messages
from cnvrgv2.errors import CnvrgLoginError
from cnvrgv2.config import Config


def verify_login():
    token, domain, user = Config().get_credential_variables()
    if not (token and domain and user):
        raise CnvrgLoginError(error_messages.CREDENTIALS_MISSING)
