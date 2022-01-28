from drf_auth_service.settings import settings

AUTHENTICATION_PERMISSIONS = dict(
    register=[settings.PERMISSIONS.SERVICE_TOKEN_PERMISSION],
    send_reset_password=[settings.PERMISSIONS.SERVICE_TOKEN_PERMISSION],
    reset_password_confirm=[settings.PERMISSIONS.SERVICE_TOKEN_PERMISSION],
    default=[settings.PERMISSIONS.SERVICE_TOKEN_PERMISSION]
)
