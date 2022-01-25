"""Utils module, common project methods."""
from django.conf import settings


def has_console_access(user):
    """Check if user has access to extra content."""
    if user.is_staff:
        return True

    if not getattr(settings, 'ALLOW_CONSOLE_ACCESS', False):
        return False

    return user.groups.filter(name='ecomm_console_client').exists()
