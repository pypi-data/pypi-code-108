from rest_framework.permissions import IsAuthenticated

from drf_auth_service.settings import settings

USER_PERMISSIONS = dict(set_password=[settings.PERMISSIONS.SERVICE_TOKEN_PERMISSION, IsAuthenticated])
