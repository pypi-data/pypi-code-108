from fastack import Fastack
from fastack.utils import import_attr

from fastack_mail.backend import EmailBackend


def setup(app: Fastack):
    params = {}
    prefix = "EMAIL_"
    email_backend_class_setting = prefix + "BACKEND"
    for setting in dir(app.state.settings):
        if not setting.startswith(prefix) or setting == email_backend_class_setting:
            continue

        value = app.get_setting(setting)
        setting = setting[len(prefix) :].lower()
        params[setting] = value

    klass = app.get_setting(email_backend_class_setting)
    try:
        email_backend_class = import_attr(klass)
    except Exception as e:
        raise RuntimeError(f"Unable to import email backend {klass}") from e

    email_backend: EmailBackend = email_backend_class(**params)
    app.state.email = email_backend
