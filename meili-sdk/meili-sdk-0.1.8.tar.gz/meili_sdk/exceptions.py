class MeiliException(Exception):
    """
    Base class for all exceptions risen in the project
    """

    def __init__(self, msg=None, *args: object) -> None:
        super().__init__(msg or "An exception occurred in Meili SDK", *args)


class MissingAttributesException(MeiliException):
    def __init__(self, cls, missing_attrs) -> None:
        if not isinstance(missing_attrs, (list, tuple, set)):
            missing_attrs = [missing_attrs]
        super().__init__(
            f"Cannot initialize {cls}. Missing attributes: {', '.join(missing_attrs)}"
        )


class APIError(MeiliException):
    """
    All exceptions from API should derive from this
    """

    def __init__(self, status_code=None, custom_message=None) -> None:
        msg = custom_message if custom_message else "Exception accessing API resources"
        if status_code:
            msg += f". Status code: {status_code}"
        super().__init__(msg)


class PermissionDenied(APIError):
    def __init__(
        self, status_code=403, custom_message="Permission denied for requested resource"
    ) -> None:
        super().__init__(status_code=status_code, custom_message=custom_message)


class BadRequest(APIError):
    def __init__(
        self, status_code=400, custom_message="Bad request", reason=None
    ) -> None:
        if reason:
            custom_message = f"{custom_message}. Reason: {reason}"
        super().__init__(status_code=status_code, custom_message=custom_message)


class ValidationError(MeiliException):
    pass


class WebsocketException(MeiliException):
    pass
