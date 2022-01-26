from functools import wraps

from esi.errors import TokenError


def fetch_token_for_owner(scopes):
    """returns valid token for owner.
    Needs to be attached on an Owner method !!

    Args:
    -scopes: Provide the required scopes.
    """

    def decorator(func):
        @wraps(func)
        def _wrapped_view(owner, *args, **kwargs):
            token, error = owner.token(scopes)
            if error:
                raise TokenError
            return func(owner, token, *args, **kwargs)

        return _wrapped_view

    return decorator
