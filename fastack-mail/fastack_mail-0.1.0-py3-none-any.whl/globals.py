from fastack.globals import LocalProxy, state

from fastack_mail.backend import EmailBackend


def _get_email_backend() -> EmailBackend:
    backend = getattr(state, "email", None)
    if not isinstance(backend, EmailBackend):
        raise RuntimeError("fastack-mail is not installed")
    return backend


email: EmailBackend = LocalProxy(_get_email_backend)
