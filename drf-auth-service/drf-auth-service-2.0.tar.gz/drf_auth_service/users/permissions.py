from drf_auth_service.settings import settings

USER_PERMISSIONS = dict(
    user_confirm=[settings.PERMISSIONS.SERVICE_TOKEN_PERMISSION],
    resend_confirmation=[settings.PERMISSIONS.SECRET_SERVICE_TOKEN_PERMISSION],
    destroy=[settings.PERMISSIONS.SECRET_SERVICE_TOKEN_PERMISSION],
    block_user=[settings.PERMISSIONS.SECRET_SERVICE_TOKEN_PERMISSION],
    list=[settings.PERMISSIONS.SECRET_SERVICE_TOKEN_PERMISSION],
    unblock_user=[settings.PERMISSIONS.SECRET_SERVICE_TOKEN_PERMISSION],
    default=[settings.PERMISSIONS.SECRET_SERVICE_TOKEN_PERMISSION]
)
